# docx2md Makefile
# Install with: make build
# Reinstall with: make rebuild
# Uninstall with: make delete

.PHONY: help build rebuild delete setup test test-cov lint format clean local-run local-run-fish

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

build: ## Install docx2md (uv tool install → ~/.local/bin)
	@echo "Installing docx2md..."
	uv tool install --from . docx2md --force
	@echo ""
	@echo "Installed. Verify with: docx2md --version"

rebuild: delete build ## Reinstall docx2md (uninstall + install)

delete: ## Uninstall docx2md
	@echo "Uninstalling docx2md..."
	uv tool uninstall docx2md || true
	@echo "Uninstall complete."

setup: ## Set up development environment
	@echo "Setting up development environment..."
	uv venv
	uv pip install -r requirements.txt -r requirements-dev.txt
	uv pip install -e .
	@echo "Setup complete."

test: ## Run tests
	.venv/bin/python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	.venv/bin/python -m pytest tests/ --cov=docx2md --cov-report=term --cov-report=html

lint: ## Run linters (flake8, mypy)
	.venv/bin/flake8 docx2md tests
	.venv/bin/mypy docx2md

format: ## Format code (black, isort)
	.venv/bin/black docx2md tests
	.venv/bin/isort docx2md tests

clean: ## Remove build artifacts and cache files
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

local-run: ## Batch convert ./files/input → ./files/output
	.venv/bin/python -m docx2md batch ./files/input ./files/output

local-run-fish: ## Batch convert (fish shell)
	fish -c ".venv/bin/python -m docx2md batch ./files/input ./files/output"
