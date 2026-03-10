"""Built-with element — renders a compact GitHub badge."""

from __future__ import annotations

import functools
import html as html_module
import json
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

import yaml

PATTERN = re.compile(
    r'<pre><code class="language-builtwith">(.*?)</code></pre>',
    re.DOTALL,
)

DEFAULT_REPO = "natolambert/colloquium"
DEFAULT_LABEL = "Built with"

_GITHUB_ICON = """
<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
  <path d="M8 0C3.58 0 0 3.58 0 8a8.01 8.01 0 0 0 5.47 7.59c.4.07.55-.17.55-.38
  0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52
  -.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.5-1.07-1.78-.2-3.64
  -.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.52 7.52 0
  0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87
  3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0
  0 16 8c0-4.42-3.58-8-8-8Z"></path>
</svg>
""".strip()


def reset() -> None:
    """No-op to match the element registry contract."""


@functools.lru_cache(maxsize=16)
def _fetch_repo_stars(repo: str) -> int | None:
    """Best-effort GitHub star lookup with a short timeout."""
    request = Request(
        f"https://api.github.com/repos/{repo}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "colloquium-builtwith",
        },
    )
    try:
        with urlopen(request, timeout=1.5) as response:
            payload = json.load(response)
    except (OSError, URLError, ValueError):
        return None
    stars = payload.get("stargazers_count")
    try:
        return int(stars)
    except (TypeError, ValueError):
        return None


def _format_stars(stars: int) -> str:
    """Compact GitHub star counts for a small badge."""
    if stars >= 1_000_000:
        value = f"{stars / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{value}M stars"
    if stars >= 1_000:
        value = f"{stars / 1_000:.1f}".rstrip("0").rstrip(".")
        return f"{value}k stars"
    return f"{stars} stars"


def _resolve_star_count(value, repo: str) -> int | None:
    """Return an integer star count, fetch automatically, or suppress."""
    if value in {None, "", "auto", True}:
        return _fetch_repo_stars(repo)
    if value in {False, "false", "none", "off"}:
        return None
    try:
        stars = int(value)
    except (TypeError, ValueError):
        return None
    return stars if stars >= 0 else None


def process(yaml_str: str) -> str:
    """Convert YAML to a compact built-with badge."""
    raw = html_module.unescape(yaml_str.strip())
    if raw:
        try:
            spec = yaml.safe_load(raw)
        except yaml.YAMLError:
            return '<p style="color:red">Invalid builtwith YAML</p>'
        if spec is None:
            spec = {}
        if not isinstance(spec, dict):
            return '<p style="color:red">Builtwith spec must be a YAML mapping</p>'
    else:
        spec = {}

    repo = str(spec.get("repo", DEFAULT_REPO)).strip() or DEFAULT_REPO
    url = str(spec.get("url", f"https://github.com/{repo}")).strip() or f"https://github.com/{repo}"
    label = str(spec.get("label", DEFAULT_LABEL)).strip()
    stars = _resolve_star_count(spec.get("stars", "auto"), repo)
    icon = spec.get("icon", True) not in {False, "false", "none", "off"}

    escaped_repo = html_module.escape(repo)
    escaped_label = html_module.escape(label)
    escaped_url = html_module.escape(url, quote=True)

    parts = [
        f'<a class="colloquium-builtwith" href="{escaped_url}" target="_blank" rel="noopener noreferrer">'
    ]
    if icon:
        parts.append(f'<span class="colloquium-builtwith-icon">{_GITHUB_ICON}</span>')
    parts.append('<span class="colloquium-builtwith-text">')
    if label:
        parts.append(f'<span class="colloquium-builtwith-label">{escaped_label}</span>')
    parts.append(f'<span class="colloquium-builtwith-repo">{escaped_repo}</span>')
    parts.append("</span>")
    if stars is not None:
        parts.append(
            f'<span class="colloquium-builtwith-stars">{html_module.escape(_format_stars(stars))}</span>'
        )
    parts.append("</a>")
    return "".join(parts)
