"""
Tests for the equations processor module.
"""

import os
import tempfile
import unittest
from pathlib import Path

import pytest

from ms2md.processors.equations import fix_delimiters, validate_equations


class TestEquations(unittest.TestCase):
    """Test cases for the equations processor module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_fix_delimiters(self):
        """Test fixing equation delimiters."""
        # Create a test file with Pandoc-style delimiters
        input_file = self.test_dir / "input.md"
        with open(input_file, "w") as f:
            f.write("""
# Test Document

This is an inline equation: \\(E = mc^2\\)

This is a display equation:

\\[
F = ma
\\]

Another inline equation: \\(a^2 + b^2 = c^2\\)
""")
        
        output_file = self.test_dir / "output.md"
        
        # Fix delimiters with default settings
        result = fix_delimiters(input_file, output_file)
        
        # Check that the output file exists
        self.assertTrue(output_file.exists())
        
        # Read the output file
        with open(output_file, "r") as f:
            content = f.read()
        
        # Check that delimiters were fixed
        self.assertIn("This is an inline equation: $E = mc^2$", content)
        self.assertIn("$$\nF = ma\n$$", content)
        self.assertIn("Another inline equation: $a^2 + b^2 = c^2$", content)
        
        # Check the result statistics
        self.assertEqual(result["inline_original"], 2)
        self.assertEqual(result["display_original"], 1)
        self.assertEqual(result["inline_fixed"], 2)
        self.assertEqual(result["display_fixed"], 1)
    
    def test_fix_delimiters_custom(self):
        """Test fixing equation delimiters with custom delimiters."""
        # Create a test file with Pandoc-style delimiters
        input_file = self.test_dir / "input.md"
        with open(input_file, "w") as f:
            f.write("""
# Test Document

This is an inline equation: \\(E = mc^2\\)

This is a display equation:

\\[
F = ma
\\]
""")
        
        output_file = self.test_dir / "output.md"
        
        # Fix delimiters with custom settings
        result = fix_delimiters(
            input_file, output_file,
            inline_delimiters=("\\(", "\\)"),
            display_delimiters=("\\begin{equation}", "\\end{equation}")
        )
        
        # Read the output file
        with open(output_file, "r") as f:
            content = f.read()
        
        # Check that delimiters were fixed according to custom settings
        self.assertIn("This is an inline equation: \\(E = mc^2\\)", content)
        self.assertIn("\\begin{equation}\nF = ma\n\\end{equation}", content)
    
    def test_validate_equations_valid(self):
        """Test validating equations with valid equations."""
        # Create a test file with valid equations
        input_file = self.test_dir / "valid.md"
        with open(input_file, "w") as f:
            f.write("""
# Test Document

This is an inline equation: $E = mc^2$

This is a display equation:

$$
F = ma
$$

Another inline equation: $a^2 + b^2 = c^2$

An equation with environments:

$$
\\begin{aligned}
x &= y + z \\\\
y &= 2
\\end{aligned}
$$
""")
        
        # Validate equations
        result = validate_equations(input_file)
        
        # Check the result
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["inline_count"], 2)
        self.assertEqual(result["display_count"], 2)
        self.assertEqual(result["invalid_count"], 0)
        self.assertEqual(len(result["issues"]), 0)
    
    def test_validate_equations_invalid(self):
        """Test validating equations with invalid equations."""
        # Create a test file with invalid equations
        input_file = self.test_dir / "invalid.md"
        with open(input_file, "w") as f:
            f.write("""
# Test Document

This is an invalid inline equation: $E = mc^2 + {$

This is an invalid display equation:

$$
\\begin{aligned}
x &= y + z \\\\
y &= 2
\\end{aligned
$$
""")
        
        # Validate equations
        result = validate_equations(input_file)
        
        # Check the result
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["inline_count"], 1)
        self.assertEqual(result["display_count"], 1)
        self.assertGreater(result["invalid_count"], 0)
        self.assertGreater(len(result["issues"]), 0)


if __name__ == "__main__":
    unittest.main()