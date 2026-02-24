# Contributing to docx2md

Thank you for your interest in contributing to docx2md! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Contributing to docx2md](#contributing-to-docx2md)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [Getting Started](#getting-started)
  - [Development Environment](#development-environment)
  - [Coding Standards](#coding-standards)
  - [Pull Request Process](#pull-request-process)
  - [Testing](#testing)
  - [Documentation](#documentation)
  - [Issue Reporting](#issue-reporting)
  - [Thank You!](#thank-you)

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to adhere to the following principles:

- Be respectful and considerate of differing viewpoints and experiences
- Use inclusive language and avoid offensive comments or personal attacks
- Focus on what is best for the community and the project
- Show empathy towards other community members

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your feature or bug fix
5. Make your changes
6. Run tests to ensure your changes don't break existing functionality
7. Submit a pull request

## Development Environment

We recommend using [uv](https://pypi.org/project/uv/) for managing dependencies and virtual environments:

```bash
# Clone the repository
git clone https://github.com/ucli-tools/docx2md.git
cd docx2md

# Set up a virtual environment
uv venv

# Install development dependencies
uv pip install -r requirements.txt -r requirements-dev.txt

# Install the package in development mode
uv pip install -e .
```

## Coding Standards

We follow standard Python best practices:

- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [mypy](http://mypy-lang.org/) for type checking
- Write docstrings in [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

You can check your code with:

```bash
# Format code
black docx2md tests

# Sort imports
isort docx2md tests

# Run linters
flake8 docx2md tests
mypy docx2md
```

## Pull Request Process

1. Ensure your code follows the coding standards
2. Update documentation if necessary
3. Add or update tests as appropriate
4. Make sure all tests pass
5. Update the README.md with details of changes if applicable
6. The pull request will be merged once it receives approval from maintainers

## Testing

We use [pytest](https://docs.pytest.org/) for testing. All new features should include tests, and bug fixes should include tests that verify the fix.

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=docx2md

# Run a specific test
pytest tests/test_specific_file.py::test_specific_function
```

## Documentation

- Keep docstrings up to date
- Update the README.md for user-facing changes
- Add examples for new features

## Issue Reporting

When reporting issues, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment information (OS, Python version, etc.)
- Any relevant logs or error messages

For feature requests, please describe the feature and its use case clearly.

## Thank You!

Your contributions help make docx2md better for everyone. We appreciate your time and effort!
