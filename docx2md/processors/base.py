"""
Base processor class for MS2MD.

This module defines the base processor class that all specific processors
should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from pathlib import Path

from docx2md.utils.logging_utils import get_logger

logger = get_logger(__name__)


class BaseProcessor(ABC):
    """
    Base class for all content processors.
    
    This abstract class defines the interface that all processors must implement.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logger
    
    @abstractmethod
    def process(self, content: str) -> str:
        """
        Process the content.
        
        Args:
            content: Content to process
            
        Returns:
            Processed content
        """
        pass
    
    def process_file(
        self,
        input_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        Process a file.
        
        Args:
            input_file: Path to the input file
            output_file: Path to the output file (defaults to input_file if not provided)
            
        Returns:
            Dictionary with processing statistics
        """
        input_path = Path(input_file)
        output_path = Path(output_file) if output_file else input_path
        
        self.logger.info(f"Processing file: {input_path}")
        
        try:
            # Read input file
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Process content
            processed_content = self.process(content)
            
            # Write output file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(processed_content)
            
            self.logger.info(f"Processed file saved to: {output_path}")
            
            return {
                "success": True,
                "input_file": str(input_path),
                "output_file": str(output_path),
            }
        
        except Exception as e:
            self.logger.error(f"Error processing file {input_path}: {str(e)}")
            return {
                "success": False,
                "input_file": str(input_path),
                "output_file": str(output_path),
                "error": str(e),
            }