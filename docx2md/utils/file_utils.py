"""
File utilities for docx2md.

This module provides functions for file operations and path handling.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Set, Union

from docx2md.utils.logging_utils import get_logger

logger = get_logger(__name__)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_relative_path(file_path: Union[str, Path], base_path: Union[str, Path]) -> Path:
    """
    Get the relative path from a base path.
    
    Args:
        file_path: File path to convert to relative
        base_path: Base path to make the path relative to
        
    Returns:
        Relative path
    """
    return Path(file_path).relative_to(Path(base_path))


def find_files(
    directory: Union[str, Path],
    extensions: Optional[List[str]] = None,
    recursive: bool = False,
) -> List[Path]:
    """
    Find files with specific extensions in a directory.
    
    Args:
        directory: Directory to search in
        extensions: List of file extensions to include (e.g., ['.docx', '.doc'])
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    directory_path = Path(directory)
    
    if not directory_path.exists() or not directory_path.is_dir():
        logger.warning(f"Directory not found: {directory_path}")
        return []
    
    # Normalize extensions to lowercase with leading dot
    if extensions:
        normalized_extensions = {
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in extensions
        }
    else:
        normalized_extensions = None
    
    result = []
    
    if recursive:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = Path(root) / file
                if normalized_extensions is None or file_path.suffix.lower() in normalized_extensions:
                    result.append(file_path)
    else:
        for file_path in directory_path.iterdir():
            if file_path.is_file() and (normalized_extensions is None or file_path.suffix.lower() in normalized_extensions):
                result.append(file_path)
    
    return sorted(result)


def copy_file(
    source: Union[str, Path],
    destination: Union[str, Path],
    overwrite: bool = False,
) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing files
        
    Returns:
        True if successful, False otherwise
    """
    source_path = Path(source)
    destination_path = Path(destination)
    
    if not source_path.exists() or not source_path.is_file():
        logger.error(f"Source file not found: {source_path}")
        return False
    
    if destination_path.exists() and not overwrite:
        logger.warning(f"Destination file already exists: {destination_path}")
        return False
    
    try:
        # Create destination directory if it doesn't exist
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        return True
    except Exception as e:
        logger.error(f"Failed to copy file {source_path} to {destination_path}: {str(e)}")
        return False


def read_file(file_path: Union[str, Path]) -> Optional[str]:
    """
    Read the contents of a text file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File contents as a string, or None if the file couldn't be read
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        return None


def write_file(file_path: Union[str, Path], content: str) -> bool:
    """
    Write content to a text file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write to file {file_path}: {str(e)}")
        return False