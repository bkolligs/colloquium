#!/usr/bin/env python3
"""Build a minimal project site for GitHub Pages."""

from __future__ import annotations

import html
import shutil
from dataclasses import dataclass
from pathlib import Path

from markdown_it import MarkdownIt

from colloquium import __version__
from colloquium.build import build_file
from colloquium.parse import parse_file


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "dist" / "site"
REPO_URL = "https://github.com/natolambert/colloquium"
PAGES_URL = "https://natolambert.github.io/colloquium/"
PICO_CSS_URL = "https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"


@dataclass
class Example:
    slug: str
    title: str
    deck_path: Path
    deck_filename: str
    readme_path: Path | None
    summary: str
    docs_html: str


def _make_md() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True})
    md.enable("table")
    return md


def _extract_summary(readme_text: str) -> str:
    for line in readme_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        return stripped
    return "Rendered example deck with copy-paste patterns."


def _load_examples() -> list[Example]:
    md = _make_md()
    examples: list[Example] = []

    for example_dir in sorted(p for p in EXAMPLES_DIR.iterdir() if p.is_dir()):
        deck_candidates = sorted(
            p for p in example_dir.glob("*.md") if p.name.lower() != "readme.md"
        )
        if not deck_candidates:
            continue
        deck_path = deck_candidates[0]
        deck = parse_file(str(deck_path))
        readme_path = example_dir / "README.md"
        readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
        docs_html = md.render(readme_text) if readme_text else ""
        summary = _extract_summary(readme_text) if readme_text else (
            deck.author.strip() or "Minimal example deck for a specific Colloquium pattern."
        )
        examples.append(
            Example(
                slug=example_dir.name,
                title=deck.title or example_dir.name.replace("-", " ").title(),
                deck_path=deck_path,
                deck_filename=f"{deck_path.stem}.html",
                readme_path=readme_path if readme_path.exists() else None,
                summary=summary,
                docs_html=docs_html,
            )
        )
    return examples


def _site_css() -> str:
    return """
main { max-width: 1100px; margin: 0 auto; }
nav ul { align-items: center; }
article.example-card h3,
article.feature-card h3 { margin-bottom: 0.35rem; }
article.example-card p,
article.feature-card p { margin-bottom: 0.75rem; }
.button-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.75rem; }
.hero-copy { max-width: 44rem; }
.plain-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.example-page { display: grid; gap: 1rem; grid-template-columns: minmax(280px, 380px) minmax(0, 1fr); }
.preview-panel { padding: 0; overflow: hidden; min-height: 78vh; }
.preview-panel iframe { width: 100%; min-height: 78vh; border: 0; }
.doc-body h1:first-child, .doc-body h2:first-child { margin-top: 0; }
.footer-note { color: var(--pico-muted-color); font-size: 0.95rem; }
@media (max-width: 900px) {
  .example-page { grid-template-columns: 1fr; }
  .preview-panel iframe { min-height: 68vh; }
}
"""


def _page_shell(
    title: str,
    body: str,
    *,
    home_href: str,
    docs_href: str,
    examples_href: str,
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{PICO_CSS_URL}">
  <style>{_site_css()}</style>
</head>
<body>
  <main class="container">
    <nav>
      <ul>
        <li><strong>Colloquium</strong></li>
      </ul>
      <ul>
        <li><a href="{home_href}">Home</a></li>
        <li><a href="{docs_href}">Docs</a></li>
        <li><a href="{examples_href}">Examples</a></li>
        <li><a href="{REPO_URL}">GitHub</a></li>
      </ul>
    </nav>
    {body}
  </main>
</body>
</html>
"""


def _render_home_page(examples: list[Example]) -> str:
    hello = next((example for example in examples if example.slug == "hello"), examples[0])
    cards = "\n".join(
        f"""
        <article class="example-card">
          <h3>{html.escape(example.title)}</h3>
          <p>{html.escape(example.summary)}</p>
          <div class="button-row">
            <a href="examples/{html.escape(example.slug)}/" role="button" class="secondary">Docs & preview</a>
            <a href="examples/{html.escape(example.slug)}/{html.escape(example.deck_filename)}">Full deck</a>
          </div>
        </article>
        """
        for example in examples
    )
    body = f"""
    <header>
      <h1>Colloquium</h1>
      <p class="hero-copy">A markdown-first slide tool for research talks. The site is intentionally small: start with the hello deck, use the docs page for the core commands and primitives, and then browse the focused examples.</p>
      <div class="button-row">
        <a href="examples/{html.escape(hello.slug)}/" role="button">Start with hello</a>
        <a href="docs/" role="button" class="secondary">Open docs</a>
        <a href="examples/">All examples</a>
      </div>
    </header>

    <section>
      <h2>Hello example</h2>
      <article class="feature-card">
        <h3>{html.escape(hello.title)}</h3>
        <p>{html.escape(hello.summary)}</p>
        <div class="button-row">
          <a href="examples/{html.escape(hello.slug)}/" role="button" class="secondary">Docs & preview</a>
          <a href="examples/{html.escape(hello.slug)}/{html.escape(hello.deck_filename)}">Full deck</a>
        </div>
      </article>
    </section>

    <section>
      <h2>Focused examples</h2>
      <div class="plain-grid">
        {cards}
      </div>
    </section>

    <p class="footer-note">Built from Colloquium {html.escape(__version__)}.</p>
    """
    return _page_shell(
        "Colloquium",
        body,
        home_href="./",
        docs_href="docs/",
        examples_href="examples/",
    )


def _render_docs_page() -> str:
    docs_md = """
# Docs

Colloquium is intentionally small. Most of the authoring surface is shown in the example decks.

## Install

```bash
uv tool install colloquium
# or inside a project
uv pip install colloquium
```

For unreleased main:

```bash
uv tool install --from git+https://github.com/natolambert/colloquium colloquium
```

## Core commands

```bash
uv run colloquium build slides.md
uv run colloquium serve slides.md
uv run colloquium export slides.md
```

## Core primitives

- Markdown slides separated by `---`
- Frontmatter for title, author, fonts, footer, bibliography, and theme options
- Slide directives in HTML comments such as `columns`, `rows`, `layout`, `class`, `cite-right`, `footnote-right`, `img-valign`
- Math with KaTeX: inline `$...$` and display `$$...$$`
- Code fences with syntax highlighting
- Citations from `[@key]` with BibTeX-backed references
- `conversation` blocks for chat examples
- `box` blocks for callouts
- `rows` / `row-columns` / `columns` for layout composition

## Where to look next

- [Hello example](../examples/hello/)
- [Title slides](../examples/title-slides/)
- [Rows and columns](../examples/rows-and-columns/)
- [Footnotes](../examples/footnotes/)

For the full source-oriented reference, use the repository README:

- [README on GitHub](https://github.com/natolambert/colloquium/blob/main/README.md)
"""
    docs_html = _make_md().render(docs_md)
    body = f"""
    <header>
      <h1>Docs</h1>
      <p>A compact reference for the core commands and authoring primitives.</p>
    </header>
    <section class="doc-body">
      {docs_html}
    </section>
    """
    return _page_shell(
        "Colloquium docs",
        body,
        home_href="../",
        docs_href="./",
        examples_href="../examples/",
    )


def _render_examples_index(examples: list[Example]) -> str:
    cards = "\n".join(
        f"""
        <article class="example-card">
          <h3>{html.escape(example.title)}</h3>
          <p>{html.escape(example.summary)}</p>
          <div class="button-row">
            <a href="{html.escape(example.slug)}/" role="button" class="secondary">Docs & preview</a>
            <a href="{html.escape(example.slug)}/{html.escape(example.deck_filename)}">Full deck</a>
          </div>
        </article>
        """
        for example in examples
    )
    body = f"""
    <header>
      <h1>Examples</h1>
      <p>Rendered decks with just enough surrounding docs to copy patterns into your own talks.</p>
    </header>
    <section class="plain-grid">
      {cards}
    </section>
    """
    return _page_shell(
        "Colloquium examples",
        body,
        home_href="../",
        docs_href="../docs/",
        examples_href="./",
    )


def _render_example_page(example: Example) -> str:
    docs_html = example.docs_html or (
        f"<p class='doc-body'>Open the rendered deck for <strong>{html.escape(example.title)}</strong>.</p>"
    )
    source_rel = example.deck_path.relative_to(REPO_ROOT).as_posix()
    body = f"""
    <p><a href="../">← Back to examples</a></p>
    <section class="example-page">
      <article>
        <h1>{html.escape(example.title)}</h1>
        <div class="button-row">
          <a href="{html.escape(example.deck_filename)}" role="button" class="secondary">Open deck</a>
          <a href="{REPO_URL}/blob/main/{source_rel}">View source</a>
        </div>
        <div class="doc-body">{docs_html}</div>
      </article>
      <article class="preview-panel">
        <iframe src="{html.escape(example.deck_filename)}" title="{html.escape(example.title)} preview"></iframe>
      </article>
    </section>
    """
    return _page_shell(
        f"{example.title} · Colloquium",
        body,
        home_href="../../",
        docs_href="../../docs/",
        examples_href="../",
    )


def _copy_example_assets(example_dir: Path, output_dir: Path) -> None:
    for path in example_dir.iterdir():
        if path.is_dir():
            shutil.copytree(path, output_dir / path.name, dirs_exist_ok=True)
            continue
        if path.suffix.lower() in {".html", ".pdf", ".pptx"}:
            continue
        if path.name.lower() in {"readme.md"}:
            continue
        shutil.copy2(path, output_dir / path.name)


def build_examples_site(output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    examples = _load_examples()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")

    for example in examples:
        example_dir = output_dir / "examples" / example.slug
        example_dir.mkdir(parents=True, exist_ok=True)
        build_file(str(example.deck_path), str(example_dir / example.deck_filename))
        _copy_example_assets(example.deck_path.parent, example_dir)
        (example_dir / "index.html").write_text(
            _render_example_page(example),
            encoding="utf-8",
        )

    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "index.html").write_text(_render_docs_page(), encoding="utf-8")

    examples_dir = output_dir / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)
    (examples_dir / "index.html").write_text(
        _render_examples_index(examples),
        encoding="utf-8",
    )

    (output_dir / "index.html").write_text(_render_home_page(examples), encoding="utf-8")
    return output_dir


def main() -> None:
    path = build_examples_site()
    print(f"Built examples site: {path}")


if __name__ == "__main__":
    main()
