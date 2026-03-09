"""Dev server with file watching and auto-rebuild."""

from __future__ import annotations

import http.server
import os
import re
import socketserver
import threading
import time
from pathlib import Path


_COMMENT_OPEN_RE = re.compile(r"<!--")
_COMMENT_CLOSE_RE = re.compile(r"-->")
_FENCE_LINE_RE = re.compile(r"^(?:```|~~~)", re.MULTILINE)


def _has_unclosed_html_comment(text: str) -> bool:
    """Return True if the text ends inside an unclosed <!-- block.

    Only checks whether the *last* ``<!--`` has a matching ``-->``.
    Stray ``-->`` in content (e.g. arrow notation) is harmless.
    """
    last_open = -1
    for m in _COMMENT_OPEN_RE.finditer(text):
        last_open = m.start()
    if last_open == -1:
        return False
    return _COMMENT_CLOSE_RE.search(text, last_open + 4) is None


def _has_unclosed_fenced_code_block(text: str) -> bool:
    """Return True if the text ends inside an unclosed fenced code block."""
    backticks = 0
    tildes = 0
    for match in _FENCE_LINE_RE.finditer(text):
        token = match.group(0)
        if token.startswith("```"):
            backticks += 1
        else:
            tildes += 1
    return backticks % 2 != 0 or tildes % 2 != 0


def _source_is_stable_for_rebuild(input_path: str) -> bool:
    """Return True when the source is in a stable enough state to rebuild."""
    try:
        text = Path(input_path).read_text(encoding="utf-8")
    except OSError:
        return False
    if not text.strip():
        return False
    return not _has_unclosed_html_comment(text) and not _has_unclosed_fenced_code_block(text)


# After this many seconds of "unstable", build anyway to avoid getting
# permanently stuck.
_MAX_STABLE_WAIT = 3.0


def _watch_and_rebuild(input_path: str, output_path: str, stop_event: threading.Event):
    """Poll for file changes and rebuild on modification."""
    from colloquium.build import build_file

    last_mtime = 0.0
    pending_mtime = 0.0
    pending_since = 0.0
    debounce_seconds = 0.35
    waiting_for_stable_source = False
    unstable_since = 0.0

    while not stop_event.is_set():
        try:
            mtime = os.stat(input_path).st_mtime
            if mtime > max(last_mtime, pending_mtime):
                pending_mtime = mtime
                pending_since = time.monotonic()

            if pending_mtime and time.monotonic() - pending_since >= debounce_seconds:
                stable = _source_is_stable_for_rebuild(input_path)
                timed_out = (
                    unstable_since > 0
                    and time.monotonic() - unstable_since >= _MAX_STABLE_WAIT
                )

                if not stable and not timed_out:
                    if not waiting_for_stable_source:
                        print("  Waiting for stable source before rebuild...")
                        waiting_for_stable_source = True
                        unstable_since = time.monotonic()
                else:
                    if timed_out and not stable:
                        print("  Stability wait timed out, rebuilding anyway.")
                    if last_mtime > 0:
                        print(f"  Rebuilding {input_path}...")
                    build_file(input_path, output_path)
                    last_mtime = pending_mtime
                    pending_mtime = 0.0
                    pending_since = 0.0
                    waiting_for_stable_source = False
                    unstable_since = 0.0
        except OSError:
            pass
        except Exception as e:
            print(f"  Build error: {e}")
            pending_mtime = 0.0
            pending_since = 0.0
            waiting_for_stable_source = False
            unstable_since = 0.0

        stop_event.wait(timeout=0.15)


def serve(input_path: str, port: int = 8080, output_dir: str | None = None):
    """Serve a presentation with live rebuilding on file changes."""
    from colloquium.build import build_file

    input_path = str(Path(input_path).resolve())
    stem = Path(input_path).stem

    if output_dir:
        serve_dir = str(Path(output_dir).resolve())
    else:
        serve_dir = str(Path(input_path).parent)

    output_path = os.path.join(serve_dir, f"{stem}.html")

    # Initial build
    print(f"Building {input_path}...")
    build_file(input_path, output_path)
    print(f"  Output: {output_path}")

    # Start file watcher in background
    stop_event = threading.Event()
    watcher = threading.Thread(
        target=_watch_and_rebuild,
        args=(input_path, output_path, stop_event),
        daemon=True,
    )
    watcher.start()

    # Serve from the output directory
    os.chdir(serve_dir)

    handler = http.server.SimpleHTTPRequestHandler

    # Suppress request logging
    class QuietHandler(handler):
        def log_message(self, format, *args):
            pass

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    try:
        with ReusableTCPServer(("", port), QuietHandler) as httpd:
            url = f"http://localhost:{port}/{stem}.html"
            print(f"  Serving at {url}")
            print(f"  Watching for changes... (Ctrl+C to stop)")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down.")
    finally:
        stop_event.set()
        watcher.join(timeout=2)
