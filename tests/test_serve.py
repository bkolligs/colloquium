"""Tests for live-reload stability checks."""

from colloquium.serve import (
    _has_unclosed_fenced_code_block,
    _has_unclosed_html_comment,
)


class TestServeStabilityChecks:
    def test_closed_html_comment(self):
        text = "<!-- columns: 50/50 -->\n## Slide\n\nContent"
        assert not _has_unclosed_html_comment(text)

    def test_unclosed_html_comment(self):
        text = "<!-- footnote: editing in progress\n## Slide\n\nContent"
        assert _has_unclosed_html_comment(text)

    def test_arrow_in_content_does_not_block_rebuild(self):
        """A --> in content must NOT be treated as an unclosed comment."""
        text = "<!-- columns: 40/60 -->\n## Slide\n\nData --> Model --> Output"
        assert not _has_unclosed_html_comment(text)

    def test_stray_close_token_without_open(self):
        text = "A --> B\n\n## Slide"
        assert not _has_unclosed_html_comment(text)

    def test_no_comments_at_all(self):
        text = "## Just a slide\n\nSome content"
        assert not _has_unclosed_html_comment(text)

    def test_multiple_directives_with_arrows(self):
        text = (
            "<!-- columns: 40/60 -->\n"
            "<!-- class: highlight -->\n"
            "## Slide\n\n"
            "A --> B --> C\n\n"
            "|||\n\n"
            "![image](img.png)"
        )
        assert not _has_unclosed_html_comment(text)

    def test_unclosed_comment_after_closed_ones(self):
        text = "<!-- columns: 40/60 -->\n## Slide\n\n<!-- editing"
        assert _has_unclosed_html_comment(text)

    def test_balanced_backtick_fences(self):
        text = "```conversation\nmessages: []\n```\n\n## Slide"
        assert not _has_unclosed_fenced_code_block(text)

    def test_unclosed_backtick_fences(self):
        text = "```conversation\nmessages: []\n\n## Slide"
        assert _has_unclosed_fenced_code_block(text)

    def test_balanced_tilde_fences(self):
        text = "~~~python\nprint('hi')\n~~~\n\n## Slide"
        assert not _has_unclosed_fenced_code_block(text)

    def test_unclosed_tilde_fences(self):
        text = "~~~python\nprint('hi')\n\n## Slide"
        assert _has_unclosed_fenced_code_block(text)
