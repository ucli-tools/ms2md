# MS2MD Makefile
# Provides commands for development, testing, and installation

.PHONY: setup test lint format clean build install install-dev install-user install-system uninstall all help

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
	@echo "Installing dependencies (including python-docx 1.0.0 for math module support)..."
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
	@echo "Choose an installation method:"
	@echo "1. For development mode (current directory): make install-dev"
	@echo "2. For user installation (recommended): make install-user"
	@echo "3. For system-wide installation: make install-system"

# Install in development mode
install-dev:
	@echo "Installing package in development mode..."
	uv pip install -e . || pip install -e .
	@echo "Installation complete. Run 'ms2md --version' to verify."
	@echo "Note: You may need to restart your terminal for the command to be available."

# Install for current user
install-user:
	@echo "Installing package for current user..."
	pip install --user .
	@echo "Installation complete. Run 'ms2md --version' to verify."
	@echo "Note: Make sure ~/.local/bin is in your PATH."
	@echo "You may need to restart your terminal for the command to be available."

# Install system-wide
install-system:
	@echo "Installing package system-wide..."
	@echo "This may require sudo privileges."
	sudo pip install .
	@echo "Installation complete. Run 'ms2md --version' to verify."

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

# Test batch locally in ./input and print in /output
local-run:
	uv venv
	uv pip install -e .
	@echo "Running batch conversion..."
	@bash -c "source .venv/bin/activate && python3 -m ms2md batch ./files/input ./files/output && deactivate"
	@echo "Batch conversion complete."

# Test batch locally with fish shell
local-run-fish:
	uv venv
	uv pip install -e .
	@echo "Running batch conversion with fish shell..."
	@fish -c "source .venv/bin/activate.fish && python3 -m ms2md batch ./files/input ./files/output && deactivate"
	@echo "Batch conversion complete."