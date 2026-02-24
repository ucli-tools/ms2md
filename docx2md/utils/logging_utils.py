"""
Logging utilities for docx2md.

This module provides functions for setting up and configuring logging.
"""

import logging
import sys
from typing import Optional

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create a logger for the package
_logger = logging.getLogger("docx2md")


def setup_logger(level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure the main logger for docx2md.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    if level:
        _logger.setLevel(getattr(logging, level.upper()))
    
    # Add a console handler if none exists
    if not _logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        _logger.addHandler(console_handler)
    
    return _logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Name of the module (optional)
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"docx2md.{name}")
    return _logger