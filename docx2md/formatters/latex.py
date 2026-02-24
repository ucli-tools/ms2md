"""
LaTeX formatter for docx2md.

This module provides functions for formatting LaTeX content within Markdown.
"""

from typing import Any, Dict, List, Optional, Union

from docx2md.utils.logging_utils import get_logger

logger = get_logger(__name__)


def format_math_environment(equation: str, environment: str = "equation") -> str:
    """
    Format a LaTeX math environment.
    
    Args:
        equation: LaTeX equation content
        environment: LaTeX environment name
        
    Returns:
        Formatted LaTeX environment
    """
    return f"\\begin{{{environment}}}\n{equation}\n\\end{{{environment}}}"


def format_aligned_equations(equations: List[str], numbered: bool = False) -> str:
    """
    Format aligned equations in LaTeX.
    
    Args:
        equations: List of equation lines
        numbered: Whether to number the equations
        
    Returns:
        Formatted aligned equations
    """
    env = "align" if numbered else "align*"
    
    # Join equations with line breaks and alignment markers
    aligned_content = []
    for eq in equations:
        if "&" not in eq:
            # Add alignment marker if not present
            parts = eq.split("=", 1)
            if len(parts) > 1:
                aligned_content.append(f"{parts[0]} &= {parts[1]} \\\\")
            else:
                aligned_content.append(f"{eq} \\\\")
        else:
            # Already has alignment marker
            if not eq.endswith("\\\\"):
                aligned_content.append(f"{eq} \\\\")
            else:
                aligned_content.append(eq)
    
    # Remove trailing \\ from the last line
    if aligned_content and aligned_content[-1].endswith("\\\\"):
        aligned_content[-1] = aligned_content[-1][:-2]
    
    content = "\n".join(aligned_content)
    
    return f"\\begin{{{env}}}\n{content}\n\\end{{{env}}}"


def format_matrix(matrix: List[List[str]], environment: str = "pmatrix") -> str:
    """
    Format a matrix in LaTeX.
    
    Args:
        matrix: 2D list representing the matrix
        environment: Matrix environment (pmatrix, bmatrix, vmatrix, etc.)
        
    Returns:
        Formatted LaTeX matrix
    """
    # Convert each row to LaTeX format
    rows = []
    for row in matrix:
        rows.append(" & ".join(row) + " \\\\")
    
    # Join rows with newlines
    content = "\n".join(rows)
    
    return f"\\begin{{{environment}}}\n{content}\n\\end{{{environment}}}"


def format_fraction(numerator: str, denominator: str) -> str:
    """
    Format a fraction in LaTeX.
    
    Args:
        numerator: Numerator expression
        denominator: Denominator expression
        
    Returns:
        Formatted LaTeX fraction
    """
    return f"\\frac{{{numerator}}}{{{denominator}}}"


def format_sqrt(expression: str, n: Optional[int] = None) -> str:
    """
    Format a square root in LaTeX.
    
    Args:
        expression: Expression under the root
        n: Optional root index (for nth roots)
        
    Returns:
        Formatted LaTeX square root
    """
    if n is not None:
        return f"\\sqrt[{n}]{{{expression}}}"
    else:
        return f"\\sqrt{{{expression}}}"


def format_sum(expression: str, lower: Optional[str] = None, upper: Optional[str] = None) -> str:
    """
    Format a summation in LaTeX.
    
    Args:
        expression: Expression to sum
        lower: Lower bound
        upper: Upper bound
        
    Returns:
        Formatted LaTeX summation
    """
    if lower is not None and upper is not None:
        return f"\\sum_{{{lower}}}^{{{upper}}} {expression}"
    elif lower is not None:
        return f"\\sum_{{{lower}}} {expression}"
    elif upper is not None:
        return f"\\sum^{{{upper}}} {expression}"
    else:
        return f"\\sum {expression}"


def format_integral(expression: str, lower: Optional[str] = None, upper: Optional[str] = None, variable: Optional[str] = None) -> str:
    """
    Format an integral in LaTeX.
    
    Args:
        expression: Expression to integrate
        lower: Lower bound
        upper: Upper bound
        variable: Integration variable
        
    Returns:
        Formatted LaTeX integral
    """
    integral = "\\int"
    
    if lower is not None and upper is not None:
        integral = f"\\int_{{{lower}}}^{{{upper}}}"
    elif lower is not None:
        integral = f"\\int_{{{lower}}}"
    elif upper is not None:
        integral = f"\\int^{{{upper}}}"
    
    if variable is not None:
        return f"{integral} {expression} \\, d{variable}"
    else:
        return f"{integral} {expression}"


def format_limit(expression: str, variable: str, value: str) -> str:
    """
    Format a limit in LaTeX.
    
    Args:
        expression: Expression to take the limit of
        variable: Limit variable
        value: Limit value
        
    Returns:
        Formatted LaTeX limit
    """
    return f"\\lim_{{{variable} \\to {value}}} {expression}"


def format_derivative(expression: str, variable: str, order: int = 1) -> str:
    """
    Format a derivative in LaTeX.
    
    Args:
        expression: Expression to differentiate
        variable: Differentiation variable
        order: Order of differentiation
        
    Returns:
        Formatted LaTeX derivative
    """
    if order == 1:
        return f"\\frac{{d}}{{d{variable}}} {expression}"
    else:
        return f"\\frac{{d^{order}}}{{d{variable}^{order}}} {expression}"


def format_partial_derivative(expression: str, variable: str, order: int = 1) -> str:
    """
    Format a partial derivative in LaTeX.
    
    Args:
        expression: Expression to differentiate
        variable: Differentiation variable
        order: Order of differentiation
        
    Returns:
        Formatted LaTeX partial derivative
    """
    if order == 1:
        return f"\\frac{{\\partial}}{{\\partial {variable}}} {expression}"
    else:
        return f"\\frac{{\\partial^{order}}}{{\\partial {variable}^{order}}} {expression}"


def format_cases(cases: List[Tuple[str, str]]) -> str:
    """
    Format a piecewise function with cases in LaTeX.
    
    Args:
        cases: List of (expression, condition) tuples
        
    Returns:
        Formatted LaTeX cases
    """
    case_lines = []
    for expr, cond in cases:
        if cond:
            case_lines.append(f"{expr} & \\text{{{cond}}} \\\\")
        else:
            case_lines.append(f"{expr} & \\\\")
    
    content = "\n".join(case_lines)
    
    return f"\\begin{{cases}}\n{content}\n\\end{{cases}}"


def format_theorem(content: str, name: Optional[str] = None, numbered: bool = True) -> str:
    """
    Format a theorem in LaTeX.
    
    Args:
        content: Theorem content
        name: Optional theorem name
        numbered: Whether to number the theorem
        
    Returns:
        Formatted LaTeX theorem
    """
    env = "theorem" if numbered else "theorem*"
    
    if name:
        return f"\\begin{{{env}}}[{name}]\n{content}\n\\end{{{env}}}"
    else:
        return f"\\begin{{{env}}}\n{content}\n\\end{{{env}}}"


def format_proof(content: str) -> str:
    """
    Format a proof in LaTeX.
    
    Args:
        content: Proof content
        
    Returns:
        Formatted LaTeX proof
    """
    return f"\\begin{{proof}}\n{content}\n\\end{{proof}}"


def format_chemical_equation(equation: str) -> str:
    """
    Format a chemical equation in LaTeX using the mhchem package.
    
    Args:
        equation: Chemical equation content
        
    Returns:
        Formatted LaTeX chemical equation
    """
    return f"\\ce{{{equation}}}"


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in text.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    # Characters that need to be escaped in LaTeX
    special_chars = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
        '\\': '\\textbackslash{}',
    }
    
    # Escape each special character
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    
    return text