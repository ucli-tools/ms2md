"""
Reusable XML utilities for working with .docx (OOXML) files.

Provides namespace registration, zip/unzip helpers, and element builders
needed by the math extraction pipeline.
"""

import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Union


# OOXML namespace URIs used in .docx packages
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
}


def register_omml_namespaces() -> None:
    """Register all OOXML namespaces so ElementTree preserves prefixes on write.

    Without this, ET uses ns0/ns1/... which breaks Word's XML parser.
    Must be called once before any ET.parse() or ET.write().
    """
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)


def unzip_docx(docx_path: Union[str, Path], dest_dir: Union[str, Path]) -> Path:
    """Extract a .docx file into *dest_dir* and return the directory path."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx_path, "r") as zf:
        zf.extractall(dest)
    return dest


def rezip_docx(source_dir: Union[str, Path], output_path: Union[str, Path]) -> Path:
    """Re-pack a directory into a .docx (ZIP) archive.

    Preserves the directory structure exactly as Word expects it.
    Returns the output path.
    """
    source = Path(source_dir)
    output = Path(output_path)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(source)
                zf.write(file_path, arcname)
    return output


def create_text_run(text: str, ns_w: str) -> ET.Element:
    """Create a ``<w:r><w:t>`` element containing *text*.

    Args:
        text: The string content for the run.
        ns_w: The full ``w`` namespace URI (e.g. ``{http://...}``).

    Returns:
        An ``<w:r>`` Element with a child ``<w:t>`` holding the text.
    """
    run = ET.SubElement(ET.Element("dummy"), f"{ns_w}r")
    t = ET.SubElement(run, f"{ns_w}t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    # Detach from dummy parent
    run = ET.Element(f"{ns_w}r")
    t = ET.SubElement(run, f"{ns_w}t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return run
