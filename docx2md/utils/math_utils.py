"""
Math tokenizer utility for docx2md.

Splits markdown content into alternating text and math spans,
enabling context-aware processing of Unicode and equation patterns.
"""

import re
from typing import List, Tuple

# Matches $$...$$  (display) first, then $...$  (inline)
# Display must come first to avoid single-$ eating the start of $$
_MATH_PATTERN = re.compile(
    r'(\$\$[\s\S]*?\$\$'       # display math $$...$$
    r'|\$(?!\$).*?(?<!\$)\$)',  # inline math $...$  (not $$ at start/end)
    re.DOTALL,
)


def tokenize_math_spans(content: str) -> List[Tuple[str, str]]:
    """
    Split markdown content into ('text', ...) and ('math', ...) token pairs.

    Display math ($$...$$) and inline math ($...$) are identified and tagged
    as 'math'; everything else is 'text'.

    Args:
        content: Markdown string to tokenize

    Returns:
        List of (token_type, token_text) tuples where token_type is 'text' or 'math'
    """
    tokens: List[Tuple[str, str]] = []
    last_end = 0

    for match in _MATH_PATTERN.finditer(content):
        if match.start() > last_end:
            tokens.append(('text', content[last_end:match.start()]))
        tokens.append(('math', match.group(0)))
        last_end = match.end()

    if last_end < len(content):
        tokens.append(('text', content[last_end:]))

    return tokens


def reassemble(tokens: List[Tuple[str, str]]) -> str:
    """Reassemble tokenized spans back into a single string."""
    return ''.join(text for _, text in tokens)
