"""
MS2MD: Convert Microsoft Word documents with complex math to Markdown+LaTeX.

This package provides tools to convert Microsoft Word documents containing
mathematical equations, tables, and figures into clean Markdown with LaTeX.
"""

__version__ = "0.1.0"
__author__ = "ThreeFold"
__license__ = "Apache-2.0"

from docx2md.converter import convert_docx_to_markdown

__all__ = ["convert_docx_to_markdown"]