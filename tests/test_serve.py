"""Tests for live-reload stability checks."""

from colloquium.serve import (
    _has_balanced_fenced_code_blocks,
    _has_balanced_html_comments,
)


class TestServeStabilityChecks:
    def test_balanced_html_comments(self):
        text = "<!-- columns: 50/50 -->\n## Slide\n\nContent"
        assert _has_balanced_html_comments(text)

    def test_unbalanced_html_comments(self):
        text = "<!-- footnote: editing in progress\n## Slide\n\nContent"
        assert not _has_balanced_html_comments(text)

    def test_html_comment_tokens_in_code_fence_do_not_break_balance(self):
        text = "```md\n<!-- footnote: literal example -->\n```\n\n## Slide"
        assert _has_balanced_html_comments(text)

    def test_balanced_backtick_fences(self):
        text = "```conversation\nmessages: []\n```\n\n## Slide"
        assert _has_balanced_fenced_code_blocks(text)

    def test_unbalanced_backtick_fences(self):
        text = "```conversation\nmessages: []\n\n## Slide"
        assert not _has_balanced_fenced_code_blocks(text)

    def test_balanced_tilde_fences(self):
        text = "~~~python\nprint('hi')\n~~~\n\n## Slide"
        assert _has_balanced_fenced_code_blocks(text)

    def test_unbalanced_tilde_fences(self):
        text = "~~~python\nprint('hi')\n\n## Slide"
        assert not _has_balanced_fenced_code_blocks(text)
