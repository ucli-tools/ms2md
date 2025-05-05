#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix LaTeX delimiters in Markdown files.

This script provides a standalone utility for fixing LaTeX equation delimiters
in Markdown files, converting from Pandoc's default \(...\) and \[...\] to
standard $...$ and $$...$$ delimiters.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def fix_delimiters(
    input_file: str,
    output_file: Optional[str] = None,
    inline_delimiters: Tuple[str, str] = ("$", "$"),
    display_delimiters: Tuple[str, str] = ("$$", "$$"),
) -> bool:
    """
    Fix LaTeX equation delimiters in a Markdown file.
    
    Args:
        input_file: Path to the input Markdown file
        output_file: Path to the output Markdown file (defaults to input_file)
        inline_delimiters: Tuple of (start, end) delimiters for inline equations
        display_delimiters: Tuple of (start, end) delimiters for display equations
        
    Returns:
        True if successful, False otherwise
    """
    # Use input file as output if not specified
    if not output_file:
        output_file = input_file
    
    try:
        # Read the input file
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Count original occurrences
        inline_original_count = len(re.findall(r'\\\((.*?)\\\)', content, re.DOTALL))
        display_original_count = len(re.findall(r'\\\[(.*?)\\\]', content, re.DOTALL))
        
        # Fix inline equations
        pattern_inline = r'\\\((.*?)\\\)'
        replacement_inline = f'{inline_delimiters[0]}\\1{inline_delimiters[1]}'
        content = re.sub(pattern_inline, replacement_inline, content, flags=re.DOTALL)
        
        # Fix display equations
        pattern_display = r'\\\[(.*?)\\\]'
        replacement_display = f'{display_delimiters[0]}\\1{display_delimiters[1]}'
        content = re.sub(pattern_display, replacement_display, content, flags=re.DOTALL)
        
        # Count fixed occurrences
        inline_fixed_count = len(re.findall(re.escape(inline_delimiters[0]) + r'(.*?)' + re.escape(inline_delimiters[1]), content, re.DOTALL))
        display_fixed_count = len(re.findall(re.escape(display_delimiters[0]) + r'(.*?)' + re.escape(display_delimiters[1]), content, re.DOTALL))
        
        # Write the output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Fixed {inline_original_count} inline and {display_original_count} display equations")
        print(f"Output written to {output_file}")
        
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False


def process_directory(
    directory: str,
    recursive: bool = False,
    inline_delimiters: Tuple[str, str] = ("$", "$"),
    display_delimiters: Tuple[str, str] = ("$$", "$$"),
) -> Tuple[int, int]:
    """
    Process all Markdown files in a directory.
    
    Args:
        directory: Directory path
        recursive: Whether to process subdirectories
        inline_delimiters: Tuple of (start, end) delimiters for inline equations
        display_delimiters: Tuple of (start, end) delimiters for display equations
        
    Returns:
        Tuple of (success_count, failure_count)
    """
    success_count = 0
    failure_count = 0
    
    # Get all Markdown files
    md_files = []
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))
    else:
        md_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".md")]
    
    # Process each file
    for md_file in md_files:
        print(f"Processing {md_file}...")
        if fix_delimiters(md_file, None, inline_delimiters, display_delimiters):
            success_count += 1
        else:
            failure_count += 1
    
    return success_count, failure_count


def main() -> int:
    """
    Main entry point for the script.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description="Fix LaTeX equation delimiters in Markdown files"
    )
    
    # Input arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f", "--file", help="Input Markdown file"
    )
    input_group.add_argument(
        "-d", "--directory", help="Directory containing Markdown files"
    )
    
    # Output arguments
    parser.add_argument(
        "-o", "--output", help="Output file (only used with --file)"
    )
    
    # Delimiter arguments
    parser.add_argument(
        "--inline-delimiters", default="$,$",
        help="Inline math delimiters (start,end), default: $,$"
    )
    parser.add_argument(
        "--display-delimiters", default="$$,$$",
        help="Display math delimiters (start,end), default: $$,$$"
    )
    
    # Other arguments
    parser.add_argument(
        "-r", "--recursive", action="store_true",
        help="Recursively process subdirectories (only used with --directory)"
    )
    
    args = parser.parse_args()
    
    # Parse delimiter options
    inline_start, inline_end = args.inline_delimiters.split(",")
    display_start, display_end = args.display_delimiters.split(",")
    
    # Process file or directory
    if args.file:
        if fix_delimiters(
            args.file, args.output,
            (inline_start, inline_end),
            (display_start, display_end)
        ):
            return 0
        else:
            return 1
    else:  # args.directory
        success_count, failure_count = process_directory(
            args.directory, args.recursive,
            (inline_start, inline_end),
            (display_start, display_end)
        )
        
        print(f"Processed {success_count + failure_count} files: {success_count} succeeded, {failure_count} failed")
        
        return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())