"""
References processing module for docx2md.

This module provides functions for handling cross-references and citations
in Markdown files.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from docx2md.processors.base import BaseProcessor
from docx2md.utils.file_utils import read_file, write_file
from docx2md.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ReferenceProcessor(BaseProcessor):
    """
    Processor for cross-references and citations in Markdown.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the reference processor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
    
    def process(self, content: str) -> str:
        """
        Process references in the content.
        
        Args:
            content: Markdown content with references
            
        Returns:
            Processed content with standardized references
        """
        # Process cross-references
        content = self._process_cross_references(content)
        
        # Process citations
        content = self._process_citations(content)
        
        return content
    
    def _process_cross_references(self, content: str) -> str:
        """
        Process cross-references in the content.
        
        Args:
            content: Markdown content
            
        Returns:
            Content with processed cross-references
        """
        # Find all headings and assign IDs
        headings = {}
        heading_pattern = r'^(#{1,6})\s+(.+?)(?:\s+\{#([a-zA-Z0-9_-]+)\})?\s*$'
        
        def process_heading(match):
            level = len(match.group(1))
            text = match.group(2).strip()
            existing_id = match.group(3)
            
            # Use existing ID or generate one
            heading_id = existing_id or self._generate_id(text)
            
            # Store heading
            headings[heading_id] = {
                "level": level,
                "text": text,
                "id": heading_id,
            }
            
            # Return heading with ID
            return f"{'#' * level} {text} {{#{heading_id}}}"
        
        # Process headings
        content = re.sub(heading_pattern, process_heading, content, flags=re.MULTILINE)
        
        # Find and replace cross-references
        ref_pattern = r'\[\[([^\]]+)\]\]'
        
        def replace_reference(match):
            ref_text = match.group(1).strip()
            
            # Check if it's a direct ID reference
            if ref_text in headings:
                heading = headings[ref_text]
                return f"[{heading['text']}](#{heading['id']})"
            
            # Check if it's a text reference
            for heading_id, heading in headings.items():
                if heading["text"].lower() == ref_text.lower():
                    return f"[{heading['text']}](#{heading_id})"
            
            # Not found, leave as is
            return match.group(0)
        
        # Replace references
        content = re.sub(ref_pattern, replace_reference, content)
        
        return content
    
    def _process_citations(self, content: str) -> str:
        """
        Process citations in the content.
        
        Args:
            content: Markdown content
            
        Returns:
            Content with processed citations
        """
        # This is a placeholder for citation processing
        # A more robust implementation would handle various citation formats
        return content
    
    def _generate_id(self, text: str) -> str:
        """
        Generate an ID from text.
        
        Args:
            text: Text to generate ID from
            
        Returns:
            Generated ID
        """
        # Convert to lowercase
        id_text = text.lower()
        
        # Replace non-alphanumeric characters with hyphens
        id_text = re.sub(r'[^a-z0-9]+', '-', id_text)
        
        # Remove leading and trailing hyphens
        id_text = id_text.strip('-')
        
        return id_text


def process_references(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Process references in a Markdown file.
    
    Args:
        input_file: Path to the input Markdown file
        output_file: Path to the output Markdown file
        config: Configuration dictionary
        
    Returns:
        Dictionary with statistics about the processing
    """
    processor = ReferenceProcessor(config)
    return processor.process_file(input_file, output_file)


def extract_references(content: str) -> Dict[str, Any]:
    """
    Extract references from Markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        Dictionary with extracted references
    """
    # Extract headings
    headings = []
    heading_pattern = r'^(#{1,6})\s+(.+?)(?:\s+\{#([a-zA-Z0-9_-]+)\})?\s*$'
    
    for match in re.finditer(heading_pattern, content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        heading_id = match.group(3) or _generate_id(text)
        
        headings.append({
            "level": level,
            "text": text,
            "id": heading_id,
            "position": match.start(),
        })
    
    # Extract cross-references
    references = []
    ref_pattern = r'\[\[([^\]]+)\]\]'
    
    for match in re.finditer(ref_pattern, content):
        ref_text = match.group(1).strip()
        
        references.append({
            "text": ref_text,
            "position": match.start(),
        })
    
    # Extract citations
    citations = []
    cite_pattern = r'\[@([^\]]+)\]'
    
    for match in re.finditer(cite_pattern, content):
        cite_key = match.group(1).strip()
        
        citations.append({
            "key": cite_key,
            "position": match.start(),
        })
    
    return {
        "headings": headings,
        "references": references,
        "citations": citations,
    }


def _generate_id(text: str) -> str:
    """
    Generate an ID from text.
    
    Args:
        text: Text to generate ID from
        
    Returns:
        Generated ID
    """
    # Convert to lowercase
    id_text = text.lower()
    
    # Replace non-alphanumeric characters with hyphens
    id_text = re.sub(r'[^a-z0-9]+', '-', id_text)
    
    # Remove leading and trailing hyphens
    id_text = id_text.strip('-')
    
    return id_text