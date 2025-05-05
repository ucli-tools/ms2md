#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script for batch converting Word documents to Markdown.

This script demonstrates how to use the MS2MD library to convert
multiple Word documents to Markdown in a single operation.
"""

import os
import sys
from pathlib import Path

from ms2md.converter import batch_convert


def main():
    """
    Main entry point for the script.
    """
    # Check command-line arguments
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input_directory> <output_directory>")
        return 1
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Validate input directory
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure the conversion
    config = {
        "equations": {
            "inline_delimiters": ["$", "$"],
            "display_delimiters": ["$$", "$$"],
            "use_pandoc_mathml": True,
        },
        "images": {
            "extract_path": "./images",
            "optimize": True,
            "max_width": 800,
            "max_height": 600,
        },
        "tables": {
            "format": "pipe",
            "header_style": "bold",
        },
        "processing": {
            "fix_delimiters": True,
            "extract_images": True,
            "process_tables": True,
        },
    }
    
    print(f"Converting Word documents from '{input_dir}' to '{output_dir}'...")
    
    # Perform the batch conversion
    result = batch_convert(
        input_dir,
        output_dir,
        config=config,
        recursive=True,
        parallel=True,
    )
    
    # Print results
    print("\nConversion complete!")
    print(f"Files processed: {result['files_processed']}")
    print(f"Files succeeded: {result['files_succeeded']}")
    print(f"Files failed: {result['files_failed']}")
    
    # Print details of each conversion
    if result["files_succeeded"] > 0:
        print("\nSuccessful conversions:")
        for item in result["results"]:
            if "error" not in item:
                print(f"  {item['input_file']} -> {item['output_file']}")
                print(f"    Equations: {item.get('equations_count', 0)}")
                print(f"    Images: {item.get('images_count', 0)}")
                print(f"    Tables: {item.get('tables_count', 0)}")
    
    if result["files_failed"] > 0:
        print("\nFailed conversions:")
        for item in result["results"]:
            if "error" in item:
                print(f"  {item['input_file']}: {item['error']}")
    
    return 0 if result["files_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())