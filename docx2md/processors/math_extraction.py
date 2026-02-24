"""
Placeholder-based math extraction for docx2md.

Replaces the single-pandoc-call approach with a 3-phase pipeline:

1. **Extract** — Parse .docx XML, pull out all ``<m:oMathPara>`` (display)
   and ``<m:oMath>`` (inline) elements, replace each with a unique text
   placeholder, and re-zip into a sanitised .docx.
2. **Convert** — Run pandoc on the math-free .docx (structure only) **and**
   batch-convert the extracted equations via a separate pandoc call.
3. **Splice** — Replace placeholders in the markdown with properly
   delimited LaTeX (``$...$`` for inline, ``$$...$$`` for display).

This eliminates pandoc's intermittent dropping of ``$`` delimiters around
OMML-converted equations.
"""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from xml.etree import ElementTree as ET

import pypandoc

from docx2md.utils.docx_xml_utils import (
    NAMESPACES,
    create_text_run,
    register_omml_namespaces,
    rezip_docx,
    unzip_docx,
)
from docx2md.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Namespace URIs wrapped in braces for ElementTree tag construction
_NS_W = "{" + NAMESPACES["w"] + "}"
_NS_M = "{" + NAMESPACES["m"] + "}"


class MathExtractor:
    """Extract math from .docx XML, convert via pandoc, splice back."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_and_convert(
        self,
        docx_path: Union[str, Path],
        media_dir: Union[str, Path],
        extra_args: List[str],
    ) -> Tuple[str, Dict[str, Any]]:
        """Top-level orchestrator.

        Args:
            docx_path: Path to the original .docx file.
            media_dir: Directory for extracted media (images).
            extra_args: Extra arguments to pass to pandoc.

        Returns:
            (markdown_text, stats_dict)
        """
        docx_path = Path(docx_path)
        media_dir = Path(media_dir)

        with tempfile.TemporaryDirectory(prefix="docx2md_math_") as tmp_dir:
            tmp = Path(tmp_dir)

            # Phase 1: extract math, create sanitised docx
            sanitized_docx, equations = self._extract_math_from_docx(
                docx_path, tmp
            )

            logger.info(
                "Extracted %d equations (%d display, %d inline)",
                len(equations),
                sum(1 for e in equations if e["kind"] == "display"),
                sum(1 for e in equations if e["kind"] == "inline"),
            )

            # Phase 2a: pandoc on math-free docx (structure + text)
            markdown = self._run_pandoc(sanitized_docx, media_dir, extra_args)

            # Phase 2b: batch-convert equations to LaTeX
            if equations:
                eq_latex = self._batch_convert_equations(equations, tmp)
            else:
                eq_latex = {}

            # Phase 3: splice equations back into markdown
            markdown = self._splice(markdown, eq_latex, equations)

        stats = {
            "math_equations_extracted": len(equations),
            "math_display_count": sum(
                1 for e in equations if e["kind"] == "display"
            ),
            "math_inline_count": sum(
                1 for e in equations if e["kind"] == "inline"
            ),
        }
        return markdown, stats

    # ------------------------------------------------------------------
    # Phase 1: XML extraction
    # ------------------------------------------------------------------

    def _extract_math_from_docx(
        self, docx_path: Path, tmp_dir: Path
    ) -> Tuple[Path, List[Dict[str, Any]]]:
        """Parse document.xml, replace math elements with placeholders.

        Returns:
            (path_to_sanitized_docx, list_of_equation_dicts)

        Each equation dict has keys: ``idx``, ``kind`` (inline|display),
        ``xml`` (serialised element bytes), ``placeholder``.
        """
        register_omml_namespaces()

        unpack_dir = tmp_dir / "unpack"
        unzip_docx(docx_path, unpack_dir)

        doc_xml_path = unpack_dir / "word" / "document.xml"
        tree = ET.parse(doc_xml_path)
        root = tree.getroot()

        # Build child→parent map (ElementTree has no parent pointers)
        parent_map: Dict[ET.Element, ET.Element] = {}
        for parent in root.iter():
            for child in parent:
                parent_map[child] = parent

        equations: List[Dict[str, Any]] = []
        idx = 0

        # Process display equations FIRST (oMathPara contains inner oMath)
        for math_para in list(root.iter(f"{_NS_M}oMathPara")):
            placeholder = f"@@MATH_DISPLAY_{idx:04d}@@"
            xml_bytes = ET.tostring(math_para, encoding="unicode")

            equations.append({
                "idx": idx,
                "kind": "display",
                "xml": xml_bytes,
                "placeholder": placeholder,
            })

            parent = parent_map.get(math_para)
            if parent is not None:
                pos = list(parent).index(math_para)
                parent.remove(math_para)
                run = create_text_run(placeholder, _NS_W)
                parent.insert(pos, run)
                # Update parent map for new element
                parent_map[run] = parent

            idx += 1

        # Process remaining inline oMath (those NOT inside an oMathPara)
        for math_el in list(root.iter(f"{_NS_M}oMath")):
            # Skip if this oMath is inside an oMathPara (already handled)
            ancestor = parent_map.get(math_el)
            inside_para = False
            while ancestor is not None:
                if ancestor.tag == f"{_NS_M}oMathPara":
                    inside_para = True
                    break
                ancestor = parent_map.get(ancestor)
            if inside_para:
                continue

            placeholder = f"@@MATH_INLINE_{idx:04d}@@"
            xml_bytes = ET.tostring(math_el, encoding="unicode")

            equations.append({
                "idx": idx,
                "kind": "inline",
                "xml": xml_bytes,
                "placeholder": placeholder,
            })

            parent = parent_map.get(math_el)
            if parent is not None:
                pos = list(parent).index(math_el)
                parent.remove(math_el)
                run = create_text_run(placeholder, _NS_W)
                parent.insert(pos, run)
                parent_map[run] = parent

            idx += 1

        # Write modified XML back
        tree.write(doc_xml_path, xml_declaration=True, encoding="UTF-8")

        # Re-zip
        sanitized_path = tmp_dir / "sanitized.docx"
        rezip_docx(unpack_dir, sanitized_path)

        return sanitized_path, equations

    # ------------------------------------------------------------------
    # Phase 2a: pandoc on structure-only docx
    # ------------------------------------------------------------------

    def _run_pandoc(
        self, docx_path: Path, media_dir: Path, extra_args: List[str]
    ) -> str:
        """Run pandoc on the math-free docx to get structural markdown."""
        return pypandoc.convert_file(
            str(docx_path),
            "markdown",
            format="docx",
            extra_args=extra_args,
        )

    # ------------------------------------------------------------------
    # Phase 2b: batch equation conversion
    # ------------------------------------------------------------------

    def _batch_convert_equations(
        self, equations: List[Dict[str, Any]], tmp_dir: Path
    ) -> Dict[int, str]:
        """Create a batch .docx with one equation per paragraph, convert all at once.

        Returns:
            dict mapping equation idx → LaTeX string
        """
        register_omml_namespaces()

        # Build a minimal document.xml with marker + equation pairs
        ns_w = NAMESPACES["w"]
        ns_m = NAMESPACES["m"]

        doc_ns = {
            "xmlns:w": ns_w,
            "xmlns:m": ns_m,
            "xmlns:r": NAMESPACES["r"],
        }

        # Create document element
        body_xml = self._build_batch_document(equations, ns_w)

        # Create minimal .docx structure
        batch_dir = tmp_dir / "batch_docx"
        batch_dir.mkdir()

        word_dir = batch_dir / "word"
        word_dir.mkdir()

        # Write document.xml
        (word_dir / "document.xml").write_text(body_xml, encoding="utf-8")

        # Write minimal [Content_Types].xml
        (batch_dir / "[Content_Types].xml").write_text(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>',
            encoding="utf-8",
        )

        # Write _rels/.rels
        rels_dir = batch_dir / "_rels"
        rels_dir.mkdir()
        (rels_dir / ".rels").write_text(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            '</Relationships>',
            encoding="utf-8",
        )

        batch_docx = tmp_dir / "batch.docx"
        rezip_docx(batch_dir, batch_docx)

        # Convert with pandoc
        raw_md = pypandoc.convert_file(
            str(batch_docx),
            "markdown",
            format="docx",
            extra_args=["--wrap=none"],
        )

        # Parse output: markers like @@EQ_0042@@ followed by equation LaTeX
        return self._parse_batch_output(raw_md, equations)

    def _build_batch_document(
        self, equations: List[Dict[str, Any]], ns_w: str
    ) -> str:
        """Build a minimal Word document XML containing marker paragraphs
        and equation paragraphs."""
        parts = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
            "<w:body>",
        ]

        for eq in equations:
            marker = f"@@EQ_{eq['idx']:04d}@@"
            # Marker paragraph
            parts.append(
                f"<w:p><w:r><w:t xml:space=\"preserve\">{marker}</w:t></w:r></w:p>"
            )
            # Equation paragraph — inject raw XML
            parts.append(f"<w:p>{eq['xml']}</w:p>")

        parts.append("</w:body></w:document>")
        return "\n".join(parts)

    def _parse_batch_output(
        self, raw_md: str, equations: List[Dict[str, Any]]
    ) -> Dict[int, str]:
        """Parse pandoc's markdown output from the batch document.

        Expects alternating marker lines (@@EQ_NNNN@@) and equation content.
        """
        result: Dict[int, str] = {}
        lines = raw_md.split("\n")
        marker_re = re.compile(r"@@EQ_(\d{4})@@")

        i = 0
        while i < len(lines):
            m = marker_re.search(lines[i])
            if m:
                eq_idx = int(m.group(1))
                # Collect lines until next marker or end
                content_lines = []
                i += 1
                while i < len(lines):
                    if marker_re.search(lines[i]):
                        break
                    content_lines.append(lines[i])
                    i += 1

                # Strip leading/trailing blank lines
                while content_lines and not content_lines[0].strip():
                    content_lines.pop(0)
                while content_lines and not content_lines[-1].strip():
                    content_lines.pop()

                latex = "\n".join(content_lines).strip()
                # Strip any delimiters pandoc may have added
                latex = self._strip_delimiters(latex)
                latex = self._clean_latex(latex)
                result[eq_idx] = latex
            else:
                i += 1

        return result

    @staticmethod
    def _strip_delimiters(latex: str) -> str:
        """Remove any ``$``, ``$$``, ``\\(...\\)``, ``\\[...\\]`` wrapping."""
        s = latex.strip()
        # Display: $$...$$ or \[...\]
        if s.startswith("$$") and s.endswith("$$"):
            s = s[2:-2].strip()
        elif s.startswith("\\[") and s.endswith("\\]"):
            s = s[2:-2].strip()
        # Inline: $...$ or \(...\)
        elif s.startswith("$") and s.endswith("$") and not s.startswith("$$"):
            s = s[1:-1].strip()
        elif s.startswith("\\(") and s.endswith("\\)"):
            s = s[2:-2].strip()
        return s

    # ------------------------------------------------------------------
    # Phase 3: splice
    # ------------------------------------------------------------------

    def _splice(
        self,
        markdown: str,
        eq_latex: Dict[int, str],
        equations: List[Dict[str, Any]],
    ) -> str:
        """Replace placeholders in *markdown* with delimited LaTeX."""
        for eq in equations:
            idx = eq["idx"]
            placeholder = eq["placeholder"]
            latex = eq_latex.get(idx, "")

            if not latex:
                # Remove placeholder if equation came back empty
                markdown = markdown.replace(placeholder, "")
                continue

            if eq["kind"] == "display":
                if self._is_wide_equation(latex):
                    # Wrap in resizebox so it scales to fit the page
                    replacement = (
                        "\n\n```{=latex}\n"
                        "\\resizebox{\\linewidth}{!}{$\\displaystyle\n"
                        f"{latex}\n"
                        "$}\n```\n\n"
                    )
                else:
                    replacement = f"\n\n$$\n{latex}\n$$\n\n"
            else:
                replacement = f"${latex}$"

            markdown = markdown.replace(placeholder, replacement)

        # Fix adjacent inline math: $...$$ → $...$ $ (add space)
        markdown = re.sub(r'\$\$(?!\n)', _fix_adjacent_inline, markdown)

        # Collapse excessive blank lines introduced by display splicing
        markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)

        return markdown

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_wide_equation(latex: str) -> bool:
        """Return True if a display equation is likely to overflow the page.

        Heuristics:
        - Longest line exceeds the character threshold, OR
        - Contains multiple matrix environments (pmatrix, bmatrix, etc.)
        """
        longest = max((len(line) for line in latex.split("\n")), default=0)
        if longest > MathExtractor._WIDE_EQ_THRESHOLD:
            return True
        # Multiple matrices on one line (e.g. matrix product chains)
        matrix_count = len(re.findall(
            r"\\begin\{[pbBvV]?matrix\}", latex
        ))
        if matrix_count >= 3:
            return True
        return False

    # Regex for equation numbers like #(1.1.46) or #(1.1.13a)
    # Uses re.MULTILINE so $ matches end-of-line (not just end-of-string),
    # catching numbers before \end{array} on the next line.
    _RE_EQ_NUMBER = re.compile(
        r'[,.\s\\]*'           # optional leading punctuation/space/backslash
        r'\\?#\('              # literal #( possibly with backslash escape
        r'[0-9]+(?:\.[0-9]+)*' # dotted number like 1.1.46
        r'[a-z]?'              # optional letter suffix like 13a
        r'\)\s*$'              # closing paren at end of line
        , re.MULTILINE
    )

    # Threshold (chars) above which a display equation gets \resizebox wrapping
    _WIDE_EQ_THRESHOLD = 300

    @staticmethod
    def _clean_latex(content: str) -> str:
        """Post-process a single LaTeX equation string.

        - Strip trailing ``\\ `` (backslash-space), convergence loop
        - Strip trailing equation numbers like ``#(1.1.46)``
        - Fix double subscripts: ``}_{`` → ``{}_{``
        - Fix double superscripts: ``}^{`` → ``{}^{``
        """
        # Strip trailing backslash-space (pandoc artifact)
        limit = 20
        while limit > 0 and content.rstrip().endswith("\\"):
            content = content.rstrip().rstrip("\\").rstrip()
            limit -= 1

        # Strip trailing equation numbers: ,#(1.1.46) or .\#(1.9.3) etc.
        content = MathExtractor._RE_EQ_NUMBER.sub("", content)

        # Double subscript/superscript fix
        content = content.replace("}_{", "}{}_{")
        content = content.replace("}^{", "}{}^{")

        return content.strip()


def _fix_adjacent_inline(match: re.Match) -> str:
    """Callback for adjacent-inline-math regex.

    Only fires when ``$$`` appears NOT followed by a newline (which would
    indicate a display-math opener).  Inserts a space: ``$ $``.
    """
    return "$ $"
