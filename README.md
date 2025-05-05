# MS2MD: MS Word to Markdown+LaTeX Converter

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A powerful tool for converting Microsoft Word documents with complex mathematical content to Markdown with LaTeX equations.

## Table of Contents

- [MS2MD: MS Word to Markdown+LaTeX Converter](#ms2md-ms-word-to-markdownlatex-converter)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Using uv (Development Mode)](#using-uv-development-mode)
    - [User Installation (Recommended)](#user-installation-recommended)
    - [System-wide Installation](#system-wide-installation)
  - [Usage](#usage)
    - [Basic Conversion](#basic-conversion)
    - [Batch Conversion](#batch-conversion)
    - [Fixing LaTeX Delimiters](#fixing-latex-delimiters)
    - [Validating Output](#validating-output)
    - [Use Cases](#use-cases)
  - [Examples](#examples)
  - [Advanced Usage](#advanced-usage)
    - [Custom Configuration](#custom-configuration)
    - [Processing Pipeline Customization](#processing-pipeline-customization)
  - [Tests and Development Tools](#tests-and-development-tools)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Logging](#logging)
  - [Contributing](#contributing)
  - [License](#license)

## Overview

MS2MD is designed to convert Microsoft Word documents containing complex mathematical equations, tables, and figures into clean Markdown with LaTeX. It's particularly useful for technical books, academic papers, and scientific documentation.

This tool bridges the gap between Word documents and the Markdown+LaTeX workflow, enabling you to leverage tools like [mdtexpdf](https://github.com/ucli-tools/mdtexpdf) for generating beautiful PDFs.

## Features

- **Equation Conversion**: Accurately converts Word equations to LaTeX
- **Image Extraction**: Properly extracts and references images
- **Table Handling**: Converts Word tables to Markdown tables
- **Batch Processing**: Process multiple files at once
- **LaTeX Delimiter Fixing**: Standardizes equation delimiters
- **Cross-Reference Handling**: Maintains document references
- **Modular Architecture**: Extensible for custom processing needs
- **Robust CLI**: Git-like command structure for ease of use

## Prerequisites

- Python 3.8 or higher
- Pandoc (for Word document conversion)
- Microsoft Word documents with equations created using the built-in equation editor

## Installation

### Using uv (Development Mode)

```bash
# Clone the repository
git clone https://github.com/ucli-tools/ms2md.git
cd ms2md

# Set up a virtual environment and install dependencies
uv venv
uv pip install -e .
```

### User Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/ucli-tools/ms2md.git
cd ms2md

# Install for the current user
make install-user
# Or directly: pip install --user .
```

### System-wide Installation

```bash
# Clone the repository
git clone https://github.com/ucli-tools/ms2md.git
cd ms2md

# Install system-wide (may require sudo)
make install-system
# Or directly: sudo pip install .
```

> **Note**: After installation, make sure the installation directory is in your PATH. You may need to restart your terminal for the `ms2md` command to be available.

## Usage

### Basic Conversion

Convert a single Word document to Markdown:

```bash
ms2md convert document.docx
```

Specify an output file:

```bash
ms2md convert document.docx output.md
```

### Batch Conversion

Convert all Word documents in a directory:

```bash
ms2md batch input_directory/ output_directory/
```

### Fixing LaTeX Delimiters

Standardize LaTeX delimiters in a Markdown file:

```bash
ms2md fix-delimiters document.md
```

### Validating Output

Check if a Markdown file has valid LaTeX equations:

```bash
ms2md validate document.md
```

### Use Cases

For detailed usage scenarios and workflows, see [Use Cases](docs/usecase.md).

## Examples

The `examples/` directory contains sample Word documents and their converted Markdown outputs:

- `simple.docx` - Basic document with minimal equations
- `math_heavy.docx` - Document with complex mathematical content
- `batch_convert.py` - Example script for batch processing

## Advanced Usage

### Custom Configuration

Create a configuration file to customize the conversion process:

```yaml
# config.yaml
equations:
  inline_delimiters: ["$", "$"]
  display_delimiters: ["$$", "$$"]
  
images:
  extract_path: "./images"
  
tables:
  format: "pipe"  # Options: pipe, grid, simple
```

Use the configuration file:

```bash
ms2md convert --config config.yaml document.docx
```

### Processing Pipeline Customization

You can extend the processing pipeline by creating custom processors:

```python
from ms2md.processors.base import BaseProcessor

class MyCustomProcessor(BaseProcessor):
    def process(self, content):
        # Custom processing logic
        return modified_content
```

## Tests and Development Tools

The repository includes a comprehensive test suite and development tools:

```
# Set up development environment
make setup

# Run tests
make test

# Format code
make format

# Run linters
make lint
```

## Troubleshooting

### Common Issues

- **Equations not converting properly**: Ensure equations in Word are created with the built-in equation editor
- **Images missing**: Check if the extraction path exists and has write permissions
- **Pandoc errors**: Verify Pandoc is installed and in your PATH

### Logging

Enable detailed logging for troubleshooting:

```bash
ms2md convert --log-level debug document.docx
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.