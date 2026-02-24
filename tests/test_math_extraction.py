"""
Tests for docx2md.processors.math_extraction.

Covers placeholder insertion, splice logic, LaTeX cleanup,
empty-equation handling, and round-trip placeholder safety.
"""

import re
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET

import pytest

from docx2md.processors.math_extraction import MathExtractor, _fix_adjacent_inline
from docx2md.utils.docx_xml_utils import (
    NAMESPACES,
    create_text_run,
    register_omml_namespaces,
    rezip_docx,
    unzip_docx,
)


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------

@pytest.fixture
def extractor():
    return MathExtractor()


@pytest.fixture
def extractor_with_config():
    return MathExtractor(config={"processing": {"math_extraction": True}})


# -----------------------------------------------------------------------
# docx_xml_utils tests
# -----------------------------------------------------------------------

class TestDocxXmlUtils:
    """Tests for the XML utility functions."""

    def test_register_namespaces_does_not_raise(self):
        register_omml_namespaces()

    def test_create_text_run(self):
        ns_w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        run = create_text_run("hello", ns_w)
        assert run.tag == f"{ns_w}r"
        t_el = run.find(f"{ns_w}t")
        assert t_el is not None
        assert t_el.text == "hello"
        assert t_el.get("{http://www.w3.org/XML/1998/namespace}space") == "preserve"

    def test_unzip_rezip_roundtrip(self, tmp_path):
        """Unzip then rezip produces a valid zip file."""
        # Create a minimal docx-like zip
        original = tmp_path / "test.docx"
        with zipfile.ZipFile(original, "w") as zf:
            zf.writestr("word/document.xml", "<doc>hello</doc>")
            zf.writestr("[Content_Types].xml", "<Types/>")

        dest = tmp_path / "unpacked"
        unzip_docx(original, dest)

        assert (dest / "word" / "document.xml").exists()
        assert (dest / "[Content_Types].xml").exists()

        rezipped = tmp_path / "repacked.docx"
        rezip_docx(dest, rezipped)

        # Verify the rezipped file is a valid zip with the same entries
        with zipfile.ZipFile(rezipped, "r") as zf:
            names = zf.namelist()
            assert "[Content_Types].xml" in names
            assert "word/document.xml" in names
            assert zf.read("word/document.xml") == b"<doc>hello</doc>"


# -----------------------------------------------------------------------
# _clean_latex tests
# -----------------------------------------------------------------------

class TestCleanLatex:
    """Tests for MathExtractor._clean_latex."""

    def test_strip_trailing_backslash(self, extractor):
        assert extractor._clean_latex(r"x + y \ ") == "x + y"

    def test_strip_multiple_trailing_backslashes(self, extractor):
        assert extractor._clean_latex(r"a \\ ") == "a"

    def test_double_subscript_fix(self, extractor):
        result = extractor._clean_latex("x}_{1}_{2}")
        assert result == "x}{}_{1}{}_{2}"

    def test_double_superscript_fix(self, extractor):
        result = extractor._clean_latex("x}^{1}^{2}")
        assert result == "x}{}^{1}{}^{2}"

    def test_no_change_when_clean(self, extractor):
        assert extractor._clean_latex("x^{2} + y_{1}") == "x^{2} + y_{1}"

    def test_empty_string(self, extractor):
        assert extractor._clean_latex("") == ""

    def test_strip_equation_number_simple(self, extractor):
        result = extractor._clean_latex(r"x + y.\#(1.1.1)")
        assert result == "x + y"

    def test_strip_equation_number_comma(self, extractor):
        result = extractor._clean_latex(r"\end{pmatrix},\#(1.1.6)")
        assert result == r"\end{pmatrix}"

    def test_strip_equation_number_with_letter(self, extractor):
        result = extractor._clean_latex(r"T(v) = Mv.\#(1.1.13a)")
        assert result == "T(v) = Mv"

    def test_strip_equation_number_space_before(self, extractor):
        result = extractor._clean_latex(r"x = y\ \#(1.9.1)")
        assert result == "x = y"

    def test_strip_equation_number_deep(self, extractor):
        result = extractor._clean_latex(r"a + b.\#(1.8.454)")
        assert result == "a + b"

    def test_strip_equation_number_before_end_array(self, extractor):
        """#(N.N.N) at end of line but not end of string (multiline equation)."""
        result = extractor._clean_latex(
            "g_{k} \\in G.\\#(1.1.1)\n\\end{array}"
        )
        assert "#(" not in result
        assert "\\end{array}" in result

    def test_no_strip_hash_in_middle(self, extractor):
        """#(...) in the middle of an equation should NOT be stripped."""
        result = extractor._clean_latex(r"f(\#(x)) + y")
        # The pattern only matches at end-of-string, so middle is safe
        assert "#" in result

    def test_strip_equation_number_no_escape(self, extractor):
        """Bare #(1.1.5) without backslash-escape."""
        result = extractor._clean_latex("p^{n}.#(1.1.5)")
        assert result == "p^{n}"


# -----------------------------------------------------------------------
# _is_wide_equation tests
# -----------------------------------------------------------------------

class TestIsWideEquation:
    """Tests for MathExtractor._is_wide_equation."""

    def test_short_equation_not_wide(self):
        assert not MathExtractor._is_wide_equation("x + y = z")

    def test_long_equation_is_wide(self):
        eq = "a + " * 100  # 400 chars
        assert MathExtractor._is_wide_equation(eq)

    def test_triple_matrix_is_wide(self):
        eq = (
            r"\begin{pmatrix} a \end{pmatrix}"
            r"\begin{pmatrix} b \end{pmatrix}"
            r"\begin{pmatrix} c \end{pmatrix}"
        )
        assert MathExtractor._is_wide_equation(eq)

    def test_double_matrix_not_wide(self):
        eq = (
            r"\begin{pmatrix} a \end{pmatrix}"
            r"\begin{pmatrix} b \end{pmatrix}"
        )
        assert not MathExtractor._is_wide_equation(eq)

    def test_bmatrix_counted(self):
        eq = (
            r"\begin{bmatrix} a \end{bmatrix}"
            r"\begin{bmatrix} b \end{bmatrix}"
            r"\begin{bmatrix} c \end{bmatrix}"
        )
        assert MathExtractor._is_wide_equation(eq)


# -----------------------------------------------------------------------
# _strip_delimiters tests
# -----------------------------------------------------------------------

class TestStripDelimiters:
    """Tests for MathExtractor._strip_delimiters."""

    def test_strip_dollar(self):
        assert MathExtractor._strip_delimiters("$x+y$") == "x+y"

    def test_strip_double_dollar(self):
        assert MathExtractor._strip_delimiters("$$x+y$$") == "x+y"

    def test_strip_paren(self):
        assert MathExtractor._strip_delimiters(r"\(x+y\)") == "x+y"

    def test_strip_bracket(self):
        assert MathExtractor._strip_delimiters(r"\[x+y\]") == "x+y"

    def test_no_delimiters(self):
        assert MathExtractor._strip_delimiters("x+y") == "x+y"

    def test_empty(self):
        assert MathExtractor._strip_delimiters("") == ""


# -----------------------------------------------------------------------
# _splice tests
# -----------------------------------------------------------------------

class TestSplice:
    """Tests for MathExtractor._splice."""

    def test_splice_inline(self, extractor):
        equations = [{"idx": 0, "kind": "inline", "placeholder": "@@MATH_INLINE_0000@@", "xml": ""}]
        eq_latex = {0: "x+y"}
        md = "The equation @@MATH_INLINE_0000@@ is simple."
        result = extractor._splice(md, eq_latex, equations)
        assert "$x+y$" in result
        assert "@@MATH" not in result

    def test_splice_display(self, extractor):
        equations = [{"idx": 0, "kind": "display", "placeholder": "@@MATH_DISPLAY_0000@@", "xml": ""}]
        eq_latex = {0: "E = mc^2"}
        md = "Famous equation:\n\n@@MATH_DISPLAY_0000@@\n\nNext paragraph."
        result = extractor._splice(md, eq_latex, equations)
        assert "$$\nE = mc^2\n$$" in result
        assert "@@MATH" not in result

    def test_splice_empty_equation_removed(self, extractor):
        equations = [{"idx": 0, "kind": "inline", "placeholder": "@@MATH_INLINE_0000@@", "xml": ""}]
        eq_latex = {0: ""}
        md = "Before @@MATH_INLINE_0000@@ after."
        result = extractor._splice(md, eq_latex, equations)
        assert "@@MATH" not in result
        assert "$$" not in result

    def test_splice_missing_equation_removed(self, extractor):
        equations = [{"idx": 5, "kind": "inline", "placeholder": "@@MATH_INLINE_0005@@", "xml": ""}]
        eq_latex = {}  # equation 5 not in latex dict
        md = "Before @@MATH_INLINE_0005@@ after."
        result = extractor._splice(md, eq_latex, equations)
        assert "@@MATH" not in result

    def test_splice_multiple_equations(self, extractor):
        equations = [
            {"idx": 0, "kind": "inline", "placeholder": "@@MATH_INLINE_0000@@", "xml": ""},
            {"idx": 1, "kind": "display", "placeholder": "@@MATH_DISPLAY_0001@@", "xml": ""},
            {"idx": 2, "kind": "inline", "placeholder": "@@MATH_INLINE_0002@@", "xml": ""},
        ]
        eq_latex = {0: "a", 1: "b = c", 2: "d"}
        md = "See @@MATH_INLINE_0000@@.\n\n@@MATH_DISPLAY_0001@@\n\nAlso @@MATH_INLINE_0002@@."
        result = extractor._splice(md, eq_latex, equations)
        assert "$a$" in result
        assert "$$\nb = c\n$$" in result
        assert "$d$" in result
        assert "@@MATH" not in result

    def test_splice_wide_display_gets_resizebox(self, extractor):
        """Wide display equations get wrapped in resizebox."""
        long_latex = "a + " * 100  # > 300 chars
        equations = [{"idx": 0, "kind": "display", "placeholder": "@@MATH_DISPLAY_0000@@", "xml": ""}]
        eq_latex = {0: long_latex.strip()}
        md = "Before\n\n@@MATH_DISPLAY_0000@@\n\nAfter"
        result = extractor._splice(md, eq_latex, equations)
        assert "\\resizebox{\\linewidth}" in result
        assert "\\displaystyle" in result
        assert "$$" not in result  # should NOT use $$ for wide equations

    def test_splice_normal_display_no_resizebox(self, extractor):
        """Normal-width display equations use standard $$."""
        equations = [{"idx": 0, "kind": "display", "placeholder": "@@MATH_DISPLAY_0000@@", "xml": ""}]
        eq_latex = {0: "x + y = z"}
        md = "Before\n\n@@MATH_DISPLAY_0000@@\n\nAfter"
        result = extractor._splice(md, eq_latex, equations)
        assert "$$" in result
        assert "resizebox" not in result

    def test_splice_collapses_excess_blank_lines(self, extractor):
        equations = [{"idx": 0, "kind": "display", "placeholder": "@@MATH_DISPLAY_0000@@", "xml": ""}]
        eq_latex = {0: "x"}
        md = "Before\n\n\n@@MATH_DISPLAY_0000@@\n\n\nAfter"
        result = extractor._splice(md, eq_latex, equations)
        # Should not have more than 3 consecutive newlines
        assert "\n\n\n\n" not in result


# -----------------------------------------------------------------------
# Adjacent inline math fix
# -----------------------------------------------------------------------

class TestAdjacentInlineFix:
    """Tests for the adjacent-inline-math regex fix."""

    def test_fix_adjacent_inline_callback(self):
        m = re.search(r'\$\$(?!\n)', "x$$ y")
        assert m is not None
        assert _fix_adjacent_inline(m) == "$ $"


# -----------------------------------------------------------------------
# Placeholder format tests
# -----------------------------------------------------------------------

class TestPlaceholderFormat:
    """Verify placeholder patterns won't collide with natural content."""

    def test_inline_placeholder_format(self):
        ph = "@@MATH_INLINE_0042@@"
        assert re.match(r"@@MATH_INLINE_\d{4}@@", ph)

    def test_display_placeholder_format(self):
        ph = "@@MATH_DISPLAY_0042@@"
        assert re.match(r"@@MATH_DISPLAY_\d{4}@@", ph)

    def test_no_collision_with_email(self):
        """@@ patterns should not appear in normal prose or email addresses."""
        text = "Contact user@example.com for details."
        assert "@@MATH" not in text


# -----------------------------------------------------------------------
# _parse_batch_output tests
# -----------------------------------------------------------------------

class TestParseBatchOutput:
    """Tests for parsing pandoc batch output."""

    def test_parse_single_equation(self, extractor):
        equations = [{"idx": 0, "kind": "inline", "xml": "", "placeholder": "@@MATH_INLINE_0000@@"}]
        raw_md = "@@EQ_0000@@\n\n$x + y$\n"
        result = extractor._parse_batch_output(raw_md, equations)
        assert 0 in result
        assert result[0] == "x + y"

    def test_parse_multiple_equations(self, extractor):
        equations = [
            {"idx": 0, "kind": "inline", "xml": "", "placeholder": "@@MATH_INLINE_0000@@"},
            {"idx": 1, "kind": "display", "xml": "", "placeholder": "@@MATH_DISPLAY_0001@@"},
        ]
        raw_md = "@@EQ_0000@@\n\n$a$\n\n@@EQ_0001@@\n\n$$b + c$$\n"
        result = extractor._parse_batch_output(raw_md, equations)
        assert result[0] == "a"
        assert result[1] == "b + c"

    def test_parse_empty_equation(self, extractor):
        equations = [{"idx": 0, "kind": "inline", "xml": "", "placeholder": "@@MATH_INLINE_0000@@"}]
        raw_md = "@@EQ_0000@@\n\n\n"
        result = extractor._parse_batch_output(raw_md, equations)
        assert result.get(0, "") == ""

    def test_parse_multiline_equation(self, extractor):
        equations = [{"idx": 0, "kind": "display", "xml": "", "placeholder": "@@MATH_DISPLAY_0000@@"}]
        raw_md = "@@EQ_0000@@\n\n$$a +\nb +\nc$$\n"
        result = extractor._parse_batch_output(raw_md, equations)
        assert "a +" in result[0]
        assert "c" in result[0]


# -----------------------------------------------------------------------
# _extract_math_from_docx tests (with minimal docx)
# -----------------------------------------------------------------------

class TestExtractMathFromDocx:
    """Tests for XML-level math extraction using a synthetic .docx."""

    def _make_minimal_docx(self, tmp_path: Path, body_xml: str) -> Path:
        """Create a minimal .docx with given body XML content."""
        register_omml_namespaces()

        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document '
            'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f"<w:body>{body_xml}</w:body>"
            "</w:document>"
        )

        docx_dir = tmp_path / "docx_contents"
        word_dir = docx_dir / "word"
        word_dir.mkdir(parents=True)
        rels_dir = docx_dir / "_rels"
        rels_dir.mkdir()

        (word_dir / "document.xml").write_text(doc_xml, encoding="utf-8")
        (docx_dir / "[Content_Types].xml").write_text(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
            encoding="utf-8",
        )
        (rels_dir / ".rels").write_text(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>",
            encoding="utf-8",
        )

        docx_path = tmp_path / "test.docx"
        rezip_docx(docx_dir, docx_path)
        return docx_path

    def test_extract_inline_math(self, tmp_path, extractor):
        """Inline oMath is replaced with @@MATH_INLINE_NNNN@@ placeholder."""
        body = (
            "<w:p>"
            '<w:r><w:t xml:space="preserve">Text </w:t></w:r>'
            '<m:oMath><m:r><m:t>x</m:t></m:r></m:oMath>'
            '<w:r><w:t xml:space="preserve"> more</w:t></w:r>'
            "</w:p>"
        )
        docx_path = self._make_minimal_docx(tmp_path, body)
        work_dir = tmp_path / "work"
        work_dir.mkdir()

        sanitized, equations = extractor._extract_math_from_docx(docx_path, work_dir)

        assert len(equations) == 1
        assert equations[0]["kind"] == "inline"
        assert equations[0]["placeholder"] == "@@MATH_INLINE_0000@@"

        # Verify placeholder is in the output docx
        unpack = tmp_path / "verify"
        unzip_docx(sanitized, unpack)
        doc_text = (unpack / "word" / "document.xml").read_text()
        assert "@@MATH_INLINE_0000@@" in doc_text
        assert "<m:oMath" not in doc_text

    def test_extract_display_math(self, tmp_path, extractor):
        """Display oMathPara is replaced with @@MATH_DISPLAY_NNNN@@ placeholder."""
        body = (
            "<w:p>"
            "<m:oMathPara><m:oMath><m:r><m:t>E=mc^2</m:t></m:r></m:oMath></m:oMathPara>"
            "</w:p>"
        )
        docx_path = self._make_minimal_docx(tmp_path, body)
        work_dir = tmp_path / "work"
        work_dir.mkdir()

        sanitized, equations = extractor._extract_math_from_docx(docx_path, work_dir)

        assert len(equations) == 1
        assert equations[0]["kind"] == "display"
        assert equations[0]["placeholder"] == "@@MATH_DISPLAY_0000@@"

    def test_display_before_inline_ordering(self, tmp_path, extractor):
        """Display equations (oMathPara) are extracted before standalone inline (oMath)."""
        body = (
            "<w:p>"
            "<m:oMathPara><m:oMath><m:r><m:t>display</m:t></m:r></m:oMath></m:oMathPara>"
            "</w:p>"
            "<w:p>"
            '<m:oMath><m:r><m:t>inline</m:t></m:r></m:oMath>'
            "</w:p>"
        )
        docx_path = self._make_minimal_docx(tmp_path, body)
        work_dir = tmp_path / "work"
        work_dir.mkdir()

        _, equations = extractor._extract_math_from_docx(docx_path, work_dir)

        assert len(equations) == 2
        assert equations[0]["kind"] == "display"
        assert equations[1]["kind"] == "inline"

    def test_no_math_returns_empty(self, tmp_path, extractor):
        """Document with no math returns empty equation list."""
        body = '<w:p><w:r><w:t>Just text</w:t></w:r></w:p>'
        docx_path = self._make_minimal_docx(tmp_path, body)
        work_dir = tmp_path / "work"
        work_dir.mkdir()

        _, equations = extractor._extract_math_from_docx(docx_path, work_dir)
        assert equations == []

    def test_inner_omath_not_double_extracted(self, tmp_path, extractor):
        """oMath inside oMathPara should NOT be extracted separately."""
        body = (
            "<w:p>"
            "<m:oMathPara>"
            "<m:oMath><m:r><m:t>inner</m:t></m:r></m:oMath>"
            "</m:oMathPara>"
            "</w:p>"
        )
        docx_path = self._make_minimal_docx(tmp_path, body)
        work_dir = tmp_path / "work"
        work_dir.mkdir()

        _, equations = extractor._extract_math_from_docx(docx_path, work_dir)

        # Only 1 equation (the display), not 2
        assert len(equations) == 1
        assert equations[0]["kind"] == "display"


# -----------------------------------------------------------------------
# Config integration
# -----------------------------------------------------------------------

class TestConfigIntegration:
    """Test that config flags are respected."""

    def test_default_config_has_math_extraction(self):
        from docx2md.config import DEFAULT_CONFIG
        assert "math_extraction" in DEFAULT_CONFIG["processing"]
        assert DEFAULT_CONFIG["processing"]["math_extraction"] is True

    def test_math_extractor_exported_from_processors(self):
        from docx2md.processors import MathExtractor
        assert MathExtractor is not None

    def test_frontmatter_defaults_no_equation_numbers(self):
        """equation_numbers not in defaults — user enables via config/YAML."""
        from docx2md.processors.frontmatter import _DEFAULT_MDTEXPDF
        assert "equation_numbers" not in _DEFAULT_MDTEXPDF
