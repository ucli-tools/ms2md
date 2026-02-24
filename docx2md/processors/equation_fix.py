"""
Equation fix processor for MS2MD.

Fixes garbled LaTeX equations produced by pandoc's OMML→LaTeX conversion.
Common patterns from Microsoft Word's equation editor (OMML) that pandoc
converts incorrectly.

All fixes are applied only inside math delimiters ($...$ and $$...$$).
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from docx2md.processors.base import BaseProcessor
from docx2md.utils.logging_utils import get_logger
from docx2md.utils.math_utils import tokenize_math_spans

logger = get_logger(__name__)


class EquationFixProcessor(BaseProcessor):
    """
    Fixes garbled OMML→LaTeX equation patterns from pandoc.

    Args:
        config: Configuration dict (uses config["equation_fix"] section)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        cfg = (config or {}).get('equation_fix', {})
        self.enabled = cfg.get('enabled', True)

    def process(self, content: str) -> str:
        if not self.enabled:
            return content

        tokens = tokenize_math_spans(content)
        result = []
        for kind, text in tokens:
            if kind == 'math':
                text = _fix_equation(text)
            result.append(text)
        return ''.join(result)


# ---------------------------------------------------------------------------
# Individual fix functions applied in order (most specific first)
# ---------------------------------------------------------------------------

# Pattern 1: \sum_{}^{}var = val^{upper}  →  \sum_{var=val}^{upper}
# Handles pandoc splitting i=1 out of the subscript: \sum_{}^{}i = 1^{n}
_P1 = re.compile(
    r'\\sum_\{\}\^\{\}([a-zA-Z]\s*=\s*[\w]+)\^\{([^}]+)\}'
)

# Pattern 2: \op_{word}^{}  →  \op_{\text{word}}
# Handles multi-letter word subscripts (≥2 chars) with empty superscript from OMML.
# Single-letter subscripts are variables (n, k, i, ...) handled by P3 instead.
_P2 = re.compile(
    r'\\(sum|prod|int|oint|iint|iiint|bigcup|bigcap|bigoplus|bigotimes|bigvee|bigwedge)'
    r'_\{([a-zA-Z]{2,})\}\^\{\}'
)

# Pattern 3: any \cmd_{...}^{}  →  \cmd_{...}   (empty superscript removal)
# Must run AFTER P1 and P2 to avoid stripping needed patterns
_P3 = re.compile(r'(\\[a-zA-Z]+(?:_\{[^}]*\})?)\^\{\}')

# Pattern 4: \hslash  →  \hbar  (not in all distributions)
_P4 = re.compile(r'\\hslash')

# Pattern 5: \mathbb{c} and other lowercase blackboard bold (undefined in msbm)
# Map to \mathbf{c} as a reasonable fallback
_P5 = re.compile(r'\\mathbb\{([a-z])\}')


def _fix_equation(eq: str) -> str:
    """Apply all equation fixes to a single math token (including delimiters)."""

    # P1: \sum_{}^{}i = 1^{n} → \sum_{i=1}^{n}
    def _p1_replace(m: re.Match) -> str:
        sub = m.group(1).replace(' ', '')
        sup = m.group(2)
        return f'\\sum_{{{sub}}}^{{{sup}}}'

    eq = _P1.sub(_p1_replace, eq)

    # P2: \sum_{row}^{} → \sum_{\text{row}}
    def _p2_replace(m: re.Match) -> str:
        op = m.group(1)
        word = m.group(2)
        return f'\\{op}_{{\\text{{{word}}}}}'

    eq = _P2.sub(_p2_replace, eq)

    # P3: remove remaining empty superscripts ^{}
    eq = _P3.sub(r'\1', eq)

    # P4: \hslash → \hbar
    eq = _P4.sub(r'\\hbar', eq)

    # P5: \mathbb{c} → \mathbf{c} (lowercase blackboard bold is undefined)
    eq = _P5.sub(r'\\mathbf{\1}', eq)

    return eq
