"""test_converter.py — converter.py 单元测试

测试原则：只测纯逻辑函数，不依赖文件系统或网络。
"""
import pytest

from converter import (
    BBCodeRenderer,
    J2MMConverter,
    MarkdownRenderer,
    _bbcode_to_markdown,
    _detect_article_type,
    _md_links_to_bbcode,
    _parse_date,
)

# ── _md_links_to_bbcode ──────────────────────────────

class TestMdLinksToBBCode:
    def test_basic(self):
        assert _md_links_to_bbcode("[文字](https://example.com)") == "[url=https://example.com]文字[/url]"

    def test_no_link(self):
        assert _md_links_to_bbcode("普通文字") == "普通文字"

    def test_multiple(self):
        result = _md_links_to_bbcode("[A](http://a.com) and [B](http://b.com)")
        assert "[url=http://a.com]A[/url]" in result
        assert "[url=http://b.com]B[/url]" in result

    def test_empty(self):
        assert _md_links_to_bbcode("") == ""


# ── _parse_date ──────────────────────────────────────

class TestParseDate:
    def test_iso_utc(self):
        result = _parse_date("2024-03-15T10:30:00Z")
        assert "2024" in result
        assert "18" in result  # UTC+8: 10+8=18

    def test_iso_with_offset(self):
        result = _parse_date("2024-03-15T10:30:00+00:00")
        assert "2024" in result

    def test_day_month_year(self):
        result = _parse_date("15 March 2024")
        assert "2024" in result
        assert "3" in result
        assert "15" in result

    def test_month_day_year(self):
        result = _parse_date("March 15, 2024")
        assert "2024" in result

    def test_empty(self):
        assert _parse_date("") == ""

    def test_invalid_returns_original(self):
        assert _parse_date("not-a-date") == "not-a-date"


# ── _bbcode_to_markdown ──────────────────────────────

class TestBBCodeToMarkdown:
    def test_bold(self):
        assert _bbcode_to_markdown("[b]粗体[/b]") == "**粗体**"

    def test_italic(self):
        assert _bbcode_to_markdown("[i]斜体[/i]") == "*斜体*"

    def test_url(self):
        result = _bbcode_to_markdown("[url=http://example.com]链接[/url]")
        assert "[链接](http://example.com)" in result

    def test_img(self):
        result = _bbcode_to_markdown("[img]http://example.com/a.png[/img]")
        assert "http://example.com/a.png" in result

    def test_list(self):
        result = _bbcode_to_markdown("[list][*]项目1[*]项目2[/list]")
        assert "- 项目1" in result
        assert "- 项目2" in result

    def test_strip_size_color(self):
        result = _bbcode_to_markdown("[size=5][color=red]文字[/color][/size]")
        assert "文字" in result
        assert "[size" not in result
        assert "[color" not in result


# ── _detect_article_type ─────────────────────────────

class TestDetectArticleType:
    @pytest.mark.parametrize("title,expected", [
        ("Minecraft Java Edition Snapshot 24w10a", "java_snapshot"),
        ("Minecraft Java Edition 1.21 Pre-Release 1", "java_prerelease"),
        ("Minecraft Java Edition 1.21 Release Candidate 1", "java_rc"),
        ("Minecraft Java Edition 1.21", "java_release"),
        ("Minecraft Beta & Preview 1.21.0.20", "bedrock_beta"),
        ("Minecraft Preview 1.21.0.20", "bedrock_beta"),
        ("Minecraft Bedrock Edition 1.21", "bedrock_release"),
        ("普通新闻标题", "normal"),
        ("", "normal"),
    ])
    def test_types(self, title, expected):
        assert _detect_article_type(title) == expected

    def test_prerelease_variants(self):
        assert _detect_article_type("1.21 Pre Release 1") == "java_prerelease"
        assert _detect_article_type("1.21 prerelease 1") == "java_prerelease"


# ── BBCodeRenderer ───────────────────────────────────

class TestBBCodeRenderer:
    def setup_method(self):
        self.r = BBCodeRenderer()

    def _block(self, btype, src, tr="", meta=None):
        return {"type": btype, "source_text": src, "translated_text": tr, "meta": meta or {}}

    def test_para_bilingual(self):
        result = self.r.render([self._block("p", "Hello", "你好")])
        assert "你好" in result
        assert "Hello" in result
        assert "[color=#bcbcbc]" in result

    def test_para_same_text(self):
        result = self.r.render([self._block("p", "Hello", "Hello")])
        assert result.count("Hello") == 1

    def test_para_no_translation(self):
        result = self.r.render([self._block("p", "Hello", "")])
        assert "Hello" in result

    def test_heading_h1(self):
        result = self.r.render([self._block("h1", "Title", "标题")])
        assert "[hr]" in result
        assert "[size=6]" in result
        assert "[b]" in result

    def test_heading_h3(self):
        result = self.r.render([self._block("h3", "Sub", "子标题")])
        assert "[size=5]" in result

    def test_code_block(self):
        result = self.r.render([self._block("pre", "code here")])
        assert "[code]code here[/code]" in result

    def test_img_with_src(self):
        result = self.r.render([self._block("img", "", "", meta={"src": "http://img.com/a.png", "alt": "图片"})])
        assert "[img]http://img.com/a.png[/img]" in result
        assert "[align=center]" in result

    def test_img_no_src(self):
        result = self.r.render([self._block("img", "", "", meta={"src": "", "alt": "描述"})])
        assert "[i]描述[/i]" in result

    def test_quote(self):
        result = self.r.render([self._block("blockquote", "原文", "译文")])
        assert "[quote]" in result
        assert "译文" in result

    def test_li_basic(self):
        blocks = [
            {"type": "li", "source_text": "Item 1", "translated_text": "项目1", "meta": {"indent_level": 0}},
            {"type": "li", "source_text": "Item 2", "translated_text": "项目2", "meta": {"indent_level": 0}},
        ]
        result = self.r.render(blocks)
        assert "[list]" in result
        assert "[*]项目1" in result
        assert "[*]项目2" in result
        assert "[/list]" in result

    def test_li_nested(self):
        blocks = [
            {"type": "li", "source_text": "Parent", "translated_text": "父", "meta": {"indent_level": 0}},
            {"type": "li", "source_text": "Child", "translated_text": "子", "meta": {"indent_level": 1}},
        ]
        result = self.r.render(blocks)
        assert result.count("[list]") == 2

    def test_empty_blocks(self):
        assert self.r.render([]) == ""


# ── MarkdownRenderer ─────────────────────────────────

class TestMarkdownRenderer:
    def setup_method(self):
        self.r = MarkdownRenderer()

    def _block(self, btype, src, tr="", meta=None):
        return {"type": btype, "source_text": src, "translated_text": tr, "meta": meta or {}}

    def test_para_bilingual(self):
        result = self.r.render([self._block("p", "Hello", "你好")])
        assert "你好" in result
        assert "Hello" in result

    def test_para_same(self):
        result = self.r.render([self._block("p", "Hello", "Hello")])
        assert result.count("Hello") == 1

    def test_heading_h1(self):
        result = self.r.render([self._block("h1", "Title", "标题")])
        assert "# 标题" in result
        assert "---" in result

    def test_heading_h2(self):
        result = self.r.render([self._block("h2", "Sub", "子标题")])
        assert "## 子标题" in result

    def test_heading_h3(self):
        result = self.r.render([self._block("h3", "Sub", "子标题")])
        assert "### 子标题" in result
        assert "---" not in result

    def test_code_block(self):
        result = self.r.render([self._block("pre", "code here")])
        assert "```" in result
        assert "code here" in result

    def test_img(self):
        result = self.r.render([self._block("img", "", "", meta={"src": "http://img.com/a.png", "alt": "图片"})])
        assert "![图片](http://img.com/a.png)" in result

    def test_img_no_src(self):
        result = self.r.render([self._block("img", "", "", meta={"src": "", "alt": "描述"})])
        assert "*描述*" in result

    def test_quote(self):
        result = self.r.render([self._block("blockquote", "原文", "译文")])
        assert "> 译文" in result

    def test_li(self):
        blocks = [
            {"type": "li", "source_text": "Item", "translated_text": "项目", "meta": {"indent_level": 0}},
        ]
        result = self.r.render(blocks)
        assert "- 项目" in result

    def test_li_indent(self):
        blocks = [
            {"type": "li", "source_text": "Child", "translated_text": "子", "meta": {"indent_level": 2}},
        ]
        result = self.r.render(blocks)
        assert "        - 子" in result  # 2 * 4 spaces


# ── J2MMConverter ────────────────────────────────────

class TestJ2MMConverter:
    def setup_method(self):
        self.conv = J2MMConverter()

    def _make_data(self, title="Test Title", translated_title="测试标题", blocks=None):
        return {
            "title": title,
            "translated_title": translated_title,
            "release_date": "2024-03-15T10:00:00Z",
            "author": "jiubook",
            "url": "https://github.com/jiubook/",
            "description": "测试描述",
            "blocks": blocks or [],
        }

    def test_bbcode_has_title(self):
        result = self.conv.convert_to_bbcode(self._make_data())
        assert "测试标题" in result
        assert "Test Title" in result

    def test_bbcode_has_meta(self):
        result = self.conv.convert_to_bbcode(self._make_data())
        assert "jiubook" in result
        assert "github.com/jiubook" in result

    def test_bbcode_has_hr(self):
        result = self.conv.convert_to_bbcode(self._make_data())
        assert "[hr]" in result

    def test_markdown_has_title(self):
        result = self.conv.convert_to_markdown(self._make_data())
        assert "# 测试标题" in result

    def test_markdown_has_separator(self):
        result = self.conv.convert_to_markdown(self._make_data())
        assert "---" in result

    def test_bbcode_with_blocks(self):
        blocks = [{"type": "p", "source_text": "Hello", "translated_text": "你好", "meta": {}}]
        result = self.conv.convert_to_bbcode(self._make_data(blocks=blocks))
        assert "你好" in result

    def test_markdown_with_blocks(self):
        blocks = [{"type": "p", "source_text": "Hello", "translated_text": "你好", "meta": {}}]
        result = self.conv.convert_to_markdown(self._make_data(blocks=blocks))
        assert "你好" in result

    def test_same_title_no_duplicate(self):
        data = self._make_data(title="同一标题", translated_title="同一标题")
        result = self.conv.convert_to_bbcode(data)
        assert result.count("同一标题") == 1

    def test_no_translated_title(self):
        data = self._make_data(translated_title="")
        result = self.conv.convert_to_bbcode(data)
        assert "Test Title" in result

    def test_snapshot_type_detection(self):
        data = self._make_data(title="Minecraft Java Edition Snapshot 24w10a")
        result = self.conv.convert_to_bbcode(data)
        assert result  # 不崩溃即可

    def test_get_modules_empty_config(self):
        conv = J2MMConverter(modules_config=None)
        assert conv._get_modules("start") == []
        assert conv._get_modules("end") == []
        assert conv._get_modules("custom") == []
