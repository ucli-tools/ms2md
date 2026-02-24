# Test Fixtures

This directory contains test fixtures for the docx2md test suite.

## Adding Test Files

To add test files:

1. Create a `.docx` file with the content you want to test
2. Add a corresponding `.md` file with the expected output
3. Update the test cases to use these files

## Current Fixtures

- `simple.docx` - A simple Word document with basic formatting
- `math_heavy.docx` - A Word document with complex mathematical content
- `tables.docx` - A Word document with various table formats
- `images.docx` - A Word document with embedded images

Note: The actual `.docx` files are not included in the repository to keep it lightweight.
You can generate them using Microsoft Word or LibreOffice and add them to this directory
when running tests locally.