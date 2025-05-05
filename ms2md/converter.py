"""
Core conversion functionality for MS2MD.

This module provides the main functions for converting Word documents to
Markdown+LaTeX, including the processing pipeline and batch conversion.
"""

import os
import glob
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import docx
import pypandoc

from ms2md.processors.docx import extract_docx_content
from ms2md.processors.equations import fix_delimiters, process_equations
from ms2md.processors.images import extract_and_process_images
from ms2md.processors.tables import process_tables
from ms2md.utils.logging_utils import get_logger

logger = get_logger(__name__)


def convert_docx_to_markdown(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convert a Word document to Markdown+LaTeX.
    
    Args:
        input_file: Path to the Word document (.docx) to convert
        output_file: Path for the output Markdown file
        config: Configuration dictionary (optional)
        
    Returns:
        Dict containing statistics about the conversion
    """
    if config is None:
        config = {}
    
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    # Ensure input file exists and is a .docx file
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if input_path.suffix.lower() != ".docx":
        raise ValueError(f"Input file must be a .docx file: {input_path}")
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Converting {input_path} to {output_path}")
    
    # Step 1: Extract content from the Word document
    doc_content = extract_docx_content(input_path)
    
    # Step 2: Use Pandoc to convert to Markdown
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", encoding="utf-8") as temp_md:
        # Get extra Pandoc arguments from config
        extra_args = config.get("pandoc", {}).get("extra_args", ["--wrap=none"])
        
        # Add MathML conversion if enabled
        if config.get("equations", {}).get("use_pandoc_mathml", True):
            extra_args.append("--mathml")
        
        # Set up image extraction if enabled
        images_dir = config.get("images", {}).get("extract_path", "./images")
        if config.get("processing", {}).get("extract_images", True):
            images_dir = os.path.join(os.path.dirname(output_path), images_dir)
            os.makedirs(images_dir, exist_ok=True)
            extra_args.append(f"--extract-media={images_dir}")
        
        # Convert using Pandoc
        markdown_content = pypandoc.convert_file(
            str(input_path),
            "markdown",
            format="docx",
            extra_args=extra_args,
        )
        
        # Write to temporary file
        temp_md.write(markdown_content)
        temp_md.flush()
        
        # Step 3: Process the Markdown content
        stats = {}
        
        # Process equations if enabled
        if config.get("processing", {}).get("fix_delimiters", True):
            inline_delimiters = tuple(config.get("equations", {}).get("inline_delimiters", ["$", "$"]))
            display_delimiters = tuple(config.get("equations", {}).get("display_delimiters", ["$$", "$$"]))
            
            eq_stats = fix_delimiters(
                temp_md.name,
                temp_md.name,
                inline_delimiters=inline_delimiters,
                display_delimiters=display_delimiters,
            )
            stats.update(eq_stats)
        
        # Process tables if enabled
        if config.get("processing", {}).get("process_tables", True):
            table_format = config.get("tables", {}).get("format", "pipe")
            header_style = config.get("tables", {}).get("header_style", "bold")
            
            table_stats = process_tables(
                temp_md.name,
                temp_md.name,
                table_format=table_format,
                header_style=header_style,
            )
            stats.update(table_stats)
        
        # Process images if enabled
        if config.get("processing", {}).get("extract_images", True):
            optimize = config.get("images", {}).get("optimize", True)
            max_width = config.get("images", {}).get("max_width", 800)
            max_height = config.get("images", {}).get("max_height", 600)
            
            image_stats = extract_and_process_images(
                temp_md.name,
                temp_md.name,
                images_dir=images_dir,
                optimize=optimize,
                max_width=max_width,
                max_height=max_height,
            )
            stats.update(image_stats)
        
        # Read the final processed content
        temp_md.seek(0)
        final_content = temp_md.read()
    
    # Write the final content to the output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    logger.info(f"Conversion completed: {input_path} -> {output_path}")
    
    return {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "equations_count": stats.get("inline_fixed", 0) + stats.get("display_fixed", 0),
        "images_count": stats.get("images_processed", 0),
        "tables_count": stats.get("tables_processed", 0),
        **stats,
    }


def batch_convert(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    config: Optional[Dict[str, Any]] = None,
    recursive: bool = False,
    parallel: bool = True,
) -> Dict[str, Any]:
    """
    Convert multiple Word documents to Markdown+LaTeX.
    
    Args:
        input_dir: Directory containing Word documents (.docx) to convert
        output_dir: Directory for output Markdown files
        config: Configuration dictionary (optional)
        recursive: Whether to recursively process subdirectories
        parallel: Whether to process files in parallel
        
    Returns:
        Dict containing statistics about the batch conversion
    """
    if config is None:
        config = {}
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure input directory exists
    if not input_path.exists() or not input_path.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_path}")
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .docx files
    pattern = "**/*.docx" if recursive else "*.docx"
    docx_files = list(input_path.glob(pattern))
    
    if not docx_files:
        logger.warning(f"No .docx files found in {input_path}")
        return {
            "files_processed": 0,
            "files_succeeded": 0,
            "files_failed": 0,
            "results": [],
        }
    
    logger.info(f"Found {len(docx_files)} .docx files to process")
    
    # Prepare conversion tasks
    conversion_tasks = []
    for docx_file in docx_files:
        # Determine relative path from input directory
        rel_path = docx_file.relative_to(input_path)
        
        # Construct output file path with .md extension
        output_file = output_path / rel_path.with_suffix(".md")
        
        # Create parent directories if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        conversion_tasks.append((docx_file, output_file))
    
    results = []
    failed_count = 0
    
    # Process files in parallel or sequentially
    if parallel and len(conversion_tasks) > 1:
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(
                    convert_docx_to_markdown, input_file, output_file, config
                ): (input_file, output_file)
                for input_file, output_file in conversion_tasks
            }
            
            for future in as_completed(futures):
                input_file, output_file = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Converted {input_file} -> {output_file}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to convert {input_file}: {str(e)}")
                    results.append({
                        "input_file": str(input_file),
                        "output_file": str(output_file),
                        "error": str(e),
                        "success": False,
                    })
    else:
        for input_file, output_file in conversion_tasks:
            try:
                result = convert_docx_to_markdown(input_file, output_file, config)
                results.append(result)
                logger.info(f"Converted {input_file} -> {output_file}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to convert {input_file}: {str(e)}")
                results.append({
                    "input_file": str(input_file),
                    "output_file": str(output_file),
                    "error": str(e),
                    "success": False,
                })
    
    return {
        "files_processed": len(conversion_tasks),
        "files_succeeded": len(conversion_tasks) - failed_count,
        "files_failed": failed_count,
        "results": results,
    }