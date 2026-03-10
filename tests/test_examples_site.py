from pathlib import Path

from docs.build import build_examples_site


def test_build_examples_site(tmp_path: Path):
    output_dir = tmp_path / "site"
    result = build_examples_site(output_dir, repo_stars=123)

    assert result == output_dir
    assert (output_dir / "index.html").exists()
    assert (output_dir / ".nojekyll").exists()

    expected_examples = {
        "hello": ("hello.html", "hello.pdf"),
        "footnotes": ("footnotes.html", "footnotes.pdf"),
        "rows-and-columns": ("rows-and-columns.html", "rows-and-columns.pdf"),
        "title-slides": ("title-slides.html", "title-slides.pdf"),
    }

    for slug, (deck_file, pdf_file) in expected_examples.items():
        example_dir = output_dir / "examples" / slug
        assert (example_dir / deck_file).exists()
        # PDF may not exist if no headless browser is available (CI without Chrome)
        # but when it does exist, the home page should link to it
        if (example_dir / pdf_file).exists():
            index_html = (output_dir / "index.html").read_text()
            assert pdf_file in index_html
