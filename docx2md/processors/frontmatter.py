"""
YAML frontmatter generator for MS2MD.

Generates mdtexpdf-compatible YAML frontmatter from document metadata
and prepends it to the markdown content.

Metadata sources (priority order):
  1. python-docx core properties (title, author, subject)
  2. Body text scan: **Bold Title**, *Italic subtitle*, Name -- <email>
  3. Config defaults (config["yaml_frontmatter"]["mdtexpdf"])
  4. Input filename stem as last-resort title
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from docx2md.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Matches a bold-only first paragraph: **Title text**
_BOLD_TITLE = re.compile(r'^\*\*([^*\n]+)\*\*\s*$', re.MULTILINE)

# Matches an italic-only paragraph: *Subtitle text*
_ITALIC_SUBTITLE = re.compile(r'^\*([^*\n]+)\*\s*$', re.MULTILINE)

# Matches "Name -- <email>" or "Name -- email@..." author line
_AUTHOR_LINE = re.compile(
    r'^([A-Z][^\n<]*?)\s+--\s+<?([a-zA-Z0-9._%+\-]+@[^\s>]+)>?\s*$',
    re.MULTILINE,
)

# Title block at start of document: optional bold title + optional italic subtitle +
# optional author line, each separated by a blank line
_TITLE_BLOCK = re.compile(
    r'^\*\*[^*\n]+\*\*\s*\n\n'          # bold title + blank line
    r'(?:\*[^*\n]+\*\s*\n\n)?'           # optional italic subtitle + blank line
    r'(?:[A-Z][^\n<]*?--[^\n]+\n\n)?',   # optional author line + blank line
    re.MULTILINE,
)

_DEFAULT_MDTEXPDF: Dict[str, Any] = {
    'format': 'article',
    'toc': True,
    'toc-depth': 2,
    'no_numbers': True,
    'header_footer_policy': 'all',
    'pageof': True,
}


def generate_yaml_frontmatter(
    doc_properties: Dict[str, Any],
    config: Dict[str, Any],
    input_path: Path,
    content: str,
) -> Tuple[str, str]:
    """
    Generate a YAML frontmatter block and optionally strip the title block from body.

    Args:
        doc_properties: Metadata extracted by python-docx (title, author, subject, ...)
        config:         Full docx2md config dict
        input_path:     Path to the original .docx file (used for title fallback)
        content:        Current markdown content (may be scanned for title/author)

    Returns:
        Tuple of (frontmatter_string, updated_content) where frontmatter_string is
        the YAML block (including --- delimiters) and updated_content has the
        title block removed if strip_body_title_block is True.
    """
    fm_cfg = config.get('yaml_frontmatter', {})

    if not fm_cfg.get('enabled', True):
        return '', content

    # Guard: don't double-prepend if content already starts with YAML
    if content.lstrip().startswith('---'):
        logger.debug('Content already has YAML frontmatter, skipping generation')
        return '', content

    # ---- Collect metadata ----
    title = doc_properties.get('title', '').strip()
    author = doc_properties.get('author', '').strip()
    subtitle = doc_properties.get('subject', '').strip()
    email = ''

    # Scan body text if allowed and properties are incomplete
    if fm_cfg.get('extract_from_body', True):
        title, subtitle, author, email = _extract_from_body(
            content, title, subtitle, author
        )

    # Last resort: derive title from filename
    if not title:
        title = input_path.stem.replace('_', ' ').replace('-', ' ').title()

    # Fall back to config default_author
    if not author:
        author = fm_cfg.get('default_author', '')

    # ---- Build frontmatter dict ----
    fm: Dict[str, Any] = {}
    if title:
        fm['title'] = title
    if subtitle:
        fm['subtitle'] = subtitle
    if author:
        fm['author'] = author
    if email:
        fm['email'] = email

    # Merge mdtexpdf defaults with any config overrides
    mdtexpdf_opts = dict(_DEFAULT_MDTEXPDF)
    mdtexpdf_opts.update(fm_cfg.get('mdtexpdf', {}))
    fm.update(mdtexpdf_opts)

    # ---- Strip title block from body ----
    updated_content = content
    if fm_cfg.get('strip_body_title_block', True):
        updated_content = _strip_title_block(content)

    # ---- Serialize to YAML ----
    yaml_str = yaml.dump(
        fm,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    frontmatter = f'---\n{yaml_str}---\n\n'

    logger.debug(f'Generated frontmatter for: {title!r} by {author!r}')
    return frontmatter, updated_content


def _extract_from_body(
    content: str,
    title: str,
    subtitle: str,
    author: str,
) -> Tuple[str, str, str, str]:
    """
    Scan the first paragraphs of the body for title/subtitle/author patterns.
    Only fills in values that are still empty.
    """
    email = ''

    # Look for bold title paragraph
    if not title:
        m = _BOLD_TITLE.search(content[:500])
        if m:
            title = m.group(1).strip()

    # Look for italic subtitle paragraph
    if not subtitle:
        m = _ITALIC_SUBTITLE.search(content[:800])
        if m:
            subtitle = m.group(1).strip()

    # Look for "Name -- <email>" author line
    if not author:
        m = _AUTHOR_LINE.search(content[:1000])
        if m:
            author = m.group(1).strip()
            email = m.group(2).strip()

    return title, subtitle, author, email


def _strip_title_block(content: str) -> str:
    """
    Remove the leading title/subtitle/author paragraphs from the body
    (they have been moved into the YAML frontmatter).
    """
    return _TITLE_BLOCK.sub('', content, count=1)
