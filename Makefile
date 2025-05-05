# MS2MD Makefile
# Provides commands for development, testing, and installation

.PHONY: setup test lint format clean build install uninstall all help

# Default target
all: setup lint test

# Help message
help:
	@echo "MS2MD Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  setup       - Set up development environment with uv"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linters (flake8, mypy)"
	@echo "  format      - Format code with black and isort"
	@echo "  clean       - Remove build artifacts and cache files"
	@echo "  build       - Build package"
	@echo "  install     - Install package in development mode"
	@echo "  uninstall   - Uninstall package"
	@echo "  all         - Run setup, lint, and test"
	@echo "  help        - Show this help message"

# Set up development environment
setup:
	@echo "Setting up development environment..."
	uv venv || python -m venv .venv
	uv pip install -r requirements.txt -r requirements-dev.txt || pip install -r requirements.txt -r requirements-dev.txt
	uv pip install -e . || pip install -e .
	@echo "Setup complete."

# Run tests
test:
	@echo "Running tests..."
	pytest
	@echo "Tests complete."

# Run with coverage
coverage:
	@echo "Running tests with coverage..."
	pytest --cov=ms2md --cov-report=term --cov-report=html
	@echo "Coverage report generated."

# Run linters
lint:
	@echo "Running linters..."
	flake8 ms2md tests
	mypy ms2md
	@echo "Linting complete."

# Format code
format:
	@echo "Formatting code..."
	black ms2md tests
	isort ms2md tests
	@echo "Formatting complete."

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .tox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaning complete."

# Build package
build: clean
	@echo "Building package..."
	python -m build
	@echo "Build complete."

# Install package
install:
	@echo "Installing package..."
	uv pip install -e . || pip install -e .
	@echo "Installation complete."

# Uninstall package
uninstall:
	@echo "Uninstalling package..."
	uv pip uninstall -y ms2md || pip uninstall -y ms2md
	@echo "Uninstallation complete."

# Create example files
examples:
	@echo "Creating example files..."
	mkdir -p examples
	@echo "Examples created."