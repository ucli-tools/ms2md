"""
Tests for the converter module.
"""

import os
import tempfile
import unittest
from pathlib import Path

import pytest

from docx2md.converter import convert_docx_to_markdown, batch_convert


class TestConverter(unittest.TestCase):
    """Test cases for the converter module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_convert_docx_to_markdown_missing_file(self):
        """Test conversion with a missing input file."""
        input_file = self.test_dir / "nonexistent.docx"
        output_file = self.test_dir / "output.md"
        
        with pytest.raises(FileNotFoundError):
            convert_docx_to_markdown(input_file, output_file)
    
    def test_convert_docx_to_markdown_invalid_extension(self):
        """Test conversion with an invalid file extension."""
        # Create a text file with .txt extension
        input_file = self.test_dir / "test.txt"
        with open(input_file, "w") as f:
            f.write("This is not a DOCX file")
        
        output_file = self.test_dir / "output.md"
        
        with pytest.raises(ValueError):
            convert_docx_to_markdown(input_file, output_file)
    
    @pytest.mark.skip(reason="Requires actual DOCX file")
    def test_convert_docx_to_markdown_basic(self):
        """Test basic conversion with a simple DOCX file."""
        # This test requires an actual DOCX file
        # In a real test suite, we would include test fixtures
        input_file = Path("tests/fixtures/simple.docx")
        output_file = self.test_dir / "output.md"
        
        result = convert_docx_to_markdown(input_file, output_file)
        
        # Check that the output file exists
        self.assertTrue(output_file.exists())
        
        # Check that the result contains expected keys
        self.assertIn("input_file", result)
        self.assertIn("output_file", result)
        self.assertIn("equations_count", result)
        self.assertIn("images_count", result)
        self.assertIn("tables_count", result)
    
    @pytest.mark.skip(reason="Requires actual DOCX files")
    def test_batch_convert(self):
        """Test batch conversion of multiple DOCX files."""
        # This test requires actual DOCX files
        # In a real test suite, we would include test fixtures
        input_dir = Path("tests/fixtures")
        output_dir = self.test_dir / "output"
        
        result = batch_convert(input_dir, output_dir)
        
        # Check that the output directory exists
        self.assertTrue(output_dir.exists())
        
        # Check that the result contains expected keys
        self.assertIn("files_processed", result)
        self.assertIn("files_succeeded", result)
        self.assertIn("files_failed", result)
        self.assertIn("results", result)


if __name__ == "__main__":
    unittest.main()