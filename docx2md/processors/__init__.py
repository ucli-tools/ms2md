"""
Processor modules for docx2md.

These modules handle specific aspects of the conversion process,
such as equations, images, tables, and references.
"""

from docx2md.processors.cleanup import WordCleanupProcessor
from docx2md.processors.equation_fix import EquationFixProcessor
from docx2md.processors.figures import FigureProcessor
from docx2md.processors.unicode_fix import UnicodeFixProcessor

__all__ = [
    "WordCleanupProcessor",
    "EquationFixProcessor",
    "FigureProcessor",
    "UnicodeFixProcessor",
]