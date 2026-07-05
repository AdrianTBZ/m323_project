"""Tests for the M323 Markdown → HTML converter."""

import pytest
from converter import (
    parse_inline, apply_rule, INLINE_RULES,
    parse_line, group_lists, take_while,
    render_line, build_html, convert,
)


class TestApplyRule:
    def test_applies_substitution(self):
        rule = (r"\*\*([^*]+)\*\*", r"<strong>\1</strong>")
        assert apply_rule("**hi**", rule) == "<strong>hi</strong>"

    def test_no_match_unchanged(self):
        rule = (r"\*\*([^*]+)\*\*", r"<strong>\1</strong>")
        assert apply_rule("plain", rule) == "plain"


class TestParseInline:
    def test_bold(self):
        assert parse_inline("**bold**") == "<strong>bold</strong>"

    def test_italic(self):
        assert parse_inline("*italic*") == "<em>italic</em>"

    def test_link(self):
        assert parse_inline("[TBZ](https://tbz.ch)") == '<a href="https://tbz.ch">TBZ</a>'

    def test_image(self):
        assert parse_inline("![alt](img.png)") == '<img alt="alt" src="img.png">'

    def test_image_before_link(self):
        result = parse_inline("![pic](a.jpg) and [link](b.html)")
        assert "<img" in result and "<a" in result

    def test_no_change(self):
        assert parse_inline("plain") == "plain"

    def test_bold_and_italic(self):
        result = parse_inline("**bold** and *italic*")
        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result


class TestParseLine:
    def test_h1(self):
        assert parse_line("# Title") == ("heading", 1, "Title")

    def test_h3(self):
        assert parse_line("### Sub") == ("heading", 3, "Sub")

    def test_h6(self):
        assert parse_line("###### Deep") == ("heading", 6, "Deep")

    def test_paragraph(self):
        assert parse_line("Hello") == ("paragraph", "Hello")

    def test_ul_dash(self):
        assert parse_line("- item") == ("ul_item", "item")

    def test_ul_star(self):
        assert parse_line("* item") == ("ul_item", "item")

    def test_ol(self):
        assert parse_line("1. first") == ("ol_item", "first")

    def test_blank(self):
        assert parse_line("") == ("blank",)


class TestTakeWhile:
    def test_takes_matching(self):
        tokens = (("ul_item", "a"), ("ul_item", "b"), ("paragraph", "p"))
        run, rest = take_while(tokens, "ul_item")
        assert len(run) == 2
        assert rest == (("paragraph", "p"),)

    def test_no_match(self):
        tokens = (("paragraph", "p"),)
        run, rest = take_while(tokens, "ul_item")
        assert run == ()
        assert rest == tokens


class TestGroupLists:
    def test_merges_ul(self):
        tokens = (("ul_item", "a"), ("ul_item", "b"))
        result = group_lists(tokens)
        assert result == (("ul", ("a", "b")),)

    def test_merges_ol(self):
        tokens = (("ol_item", "one"), ("ol_item", "two"))
        result = group_lists(tokens)
        assert result == (("ol", ("one", "two")),)

    def test_preserves_non_list(self):
        tokens = (("heading", 1, "H"), ("paragraph", "p"))
        assert group_lists(tokens) == tokens

    def test_list_between_paragraphs(self):
        tokens = (
            ("paragraph", "before"),
            ("ul_item", "x"),
            ("ul_item", "y"),
            ("paragraph", "after"),
        )
        result = group_lists(tokens)
        assert result == (
            ("paragraph", "before"),
            ("ul", ("x", "y")),
            ("paragraph", "after"),
        )

    def test_empty(self):
        assert group_lists(()) == ()


class TestRenderToken:
    def test_heading(self):
        assert render_line(("heading", 2, "Hi")) == "<h2>Hi</h2>"

    def test_paragraph(self):
        assert render_line(("paragraph", "text")) == "<p>text</p>"

    def test_ul(self):
        html = render_line(("ul", ("a", "b")))
        assert "<ul>" in html and "<li>a</li>" in html

    def test_ol(self):
        html = render_line(("ol", ("one",)))
        assert "<ol>" in html and "<li>one</li>" in html

    def test_blank_is_empty(self):
        assert render_line(("blank",)) == ""

    def test_inline_in_heading(self):
        assert render_line(("heading", 1, "**bold**")) == "<h1><strong>bold</strong></h1>"


class TestBuildHtml:
    def test_doctype(self):
        assert "<!DOCTYPE html>" in build_html("<p>hi</p>")

    def test_body_content(self):
        assert "<p>hi</p>" in build_html("<p>hi</p>")

    def test_css_inlined(self):
        html = build_html("<p>hi</p>", css="body { color: red; }")
        assert "<style>" in html and "color: red" in html

    def test_no_css_no_style(self):
        assert "<style>" not in build_html("<p>hi</p>")


class TestConvert:
    def test_heading(self):
        assert "<h1>Hello</h1>" in convert("# Hello")

    def test_paragraph(self):
        assert "<p>text</p>" in convert("text")

    def test_ul(self):
        html = convert("- a\n- b")
        assert "<ul>" in html and "<li>a</li>" in html

    def test_ol(self):
        html = convert("1. first\n2. second")
        assert "<ol>" in html and "<li>first</li>" in html

    def test_bold(self):
        assert "<strong>bold</strong>" in convert("**bold**")

    def test_italic(self):
        assert "<em>italic</em>" in convert("*italic*")

    def test_link(self):
        assert '<a href="https://tbz.ch">TBZ</a>' in convert("[TBZ](https://tbz.ch)")

    def test_image(self):
        assert '<img alt="logo" src="logo.png">' in convert("![logo](logo.png)")

    def test_full_document(self):
        md = "# Page\n\nHello **world**.\n\n- item1\n- item2\n"
        html = convert(md)
        assert "<h1>Page</h1>" in html
        assert "<strong>world</strong>" in html
        assert "<ul>" in html

    def test_css_inlined(self):
        assert "color: blue" in convert("# H", css="h1 { color: blue; }")