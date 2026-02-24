"""
Markdown formatter for docx2md.

This module provides functions for formatting content as Markdown.
"""

from typing import Any, Dict, List, Optional, Union

from docx2md.utils.logging_utils import get_logger

logger = get_logger(__name__)


def format_heading(text: str, level: int = 1) -> str:
    """
    Format a heading in Markdown.
    
    Args:
        text: Heading text
        level: Heading level (1-6)
        
    Returns:
        Formatted heading
    """
    # Ensure level is between 1 and 6
    level = max(1, min(6, level))
    
    return f"{'#' * level} {text}"


def format_bold(text: str) -> str:
    """
    Format text as bold in Markdown.
    
    Args:
        text: Text to format
        
    Returns:
        Formatted text
    """
    return f"**{text}**"


def format_italic(text: str) -> str:
    """
    Format text as italic in Markdown.
    
    Args:
        text: Text to format
        
    Returns:
        Formatted text
    """
    return f"*{text}*"


def format_code(text: str, language: Optional[str] = None) -> str:
    """
    Format text as code in Markdown.
    
    Args:
        text: Code to format
        language: Programming language for syntax highlighting
        
    Returns:
        Formatted code block
    """
    if language:
        return f"```{language}\n{text}\n```"
    else:
        return f"```\n{text}\n```"


def format_inline_code(text: str) -> str:
    """
    Format text as inline code in Markdown.
    
    Args:
        text: Code to format
        
    Returns:
        Formatted inline code
    """
    return f"`{text}`"


def format_link(text: str, url: str) -> str:
    """
    Format a link in Markdown.
    
    Args:
        text: Link text
        url: Link URL
        
    Returns:
        Formatted link
    """
    return f"[{text}]({url})"


def format_image(alt_text: str, url: str, title: Optional[str] = None) -> str:
    """
    Format an image in Markdown.
    
    Args:
        alt_text: Alternative text
        url: Image URL
        title: Image title (optional)
        
    Returns:
        Formatted image
    """
    if title:
        return f"![{alt_text}]({url} \"{title}\")"
    else:
        return f"![{alt_text}]({url})"


def format_list_item(text: str, level: int = 0) -> str:
    """
    Format a list item in Markdown.
    
    Args:
        text: List item text
        level: Indentation level
        
    Returns:
        Formatted list item
    """
    indent = "  " * level
    return f"{indent}- {text}"


def format_numbered_list_item(text: str, number: int, level: int = 0) -> str:
    """
    Format a numbered list item in Markdown.
    
    Args:
        text: List item text
        number: Item number
        level: Indentation level
        
    Returns:
        Formatted numbered list item
    """
    indent = "  " * level
    return f"{indent}{number}. {text}"


def format_blockquote(text: str) -> str:
    """
    Format text as a blockquote in Markdown.
    
    Args:
        text: Text to format
        
    Returns:
        Formatted blockquote
    """
    # Add '> ' to the beginning of each line
    lines = text.split('\n')
    quoted_lines = [f"> {line}" for line in lines]
    return '\n'.join(quoted_lines)


def format_horizontal_rule() -> str:
    """
    Format a horizontal rule in Markdown.
    
    Returns:
        Formatted horizontal rule
    """
    return "---"


def format_table(headers: List[str], rows: List[List[str]], alignments: Optional[List[str]] = None) -> str:
    """
    Format a table in Markdown.
    
    Args:
        headers: List of header texts
        rows: List of rows, each a list of cell texts
        alignments: List of alignments ('left', 'center', 'right')
        
    Returns:
        Formatted table
    """
    if not headers or not rows:
        return ""
    
    # Determine column count
    col_count = len(headers)
    
    # Ensure all rows have the same number of columns
    normalized_rows = []
    for row in rows:
        if len(row) < col_count:
            # Pad with empty cells
            normalized_rows.append(row + [""] * (col_count - len(row)))
        else:
            # Truncate if too long
            normalized_rows.append(row[:col_count])
    
    # Create header row
    header_row = "| " + " | ".join(headers) + " |"
    
    # Create separator row with alignments
    if not alignments:
        alignments = ["left"] * col_count
    else:
        # Ensure alignments list has the right length
        alignments = alignments[:col_count] + ["left"] * (col_count - len(alignments))
    
    separator_cells = []
    for alignment in alignments:
        if alignment == "center":
            separator_cells.append(":---:")
        elif alignment == "right":
            separator_cells.append("---:")
        else:  # left or default
            separator_cells.append(":---")
    
    separator_row = "| " + " | ".join(separator_cells) + " |"
    
    # Create data rows
    data_rows = []
    for row in normalized_rows:
        data_rows.append("| " + " | ".join(row) + " |")
    
    # Combine all rows
    return "\n".join([header_row, separator_row] + data_rows)


def format_definition(term: str, definition: str) -> str:
    """
    Format a definition in Markdown.
    
    Args:
        term: Term to define
        definition: Definition text
        
    Returns:
        Formatted definition
    """
    return f"{term}\n: {definition}"


def format_footnote_reference(identifier: str) -> str:
    """
    Format a footnote reference in Markdown.
    
    Args:
        identifier: Footnote identifier
        
    Returns:
        Formatted footnote reference
    """
    return f"[^{identifier}]"


def format_footnote_definition(identifier: str, text: str) -> str:
    """
    Format a footnote definition in Markdown.
    
    Args:
        identifier: Footnote identifier
        text: Footnote text
        
    Returns:
        Formatted footnote definition
    """
    # Indent all lines after the first
    lines = text.split('\n')
    if len(lines) > 1:
        indented_lines = [lines[0]] + [f"    {line}" for line in lines[1:]]
        text = '\n'.join(indented_lines)
    
    return f"[^{identifier}]: {text}"


def format_math_inline(equation: str) -> str:
    """
    Format an inline math equation in Markdown.
    
    Args:
        equation: LaTeX equation
        
    Returns:
        Formatted inline math
    """
    return f"${equation}$"


def format_math_display(equation: str) -> str:
    """
    Format a display math equation in Markdown.
    
    Args:
        equation: LaTeX equation
        
    Returns:
        Formatted display math
    """
    return f"$$\n{equation}\n$$"