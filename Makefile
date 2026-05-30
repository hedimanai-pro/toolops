# Makefile — ToolOps Development Commands
# ======================================
#
# Name: Makefile
#
# Description: Standardized development tasks for ToolOps.
#              All commands use the project's configured tools.
#
# Last_updated: 2026-05-30
#
# Updated_by: Hedi Manai
# Github: https://github.com/hedimanai-pro
# LinkedIn: https://www.linkedin.com/in/hedimanai
#
# Note: This project is open source for knowledge sharing

.PHONY: help install install-dev test lint format typecheck coverage clean docker-up docker-down

PYTHON ?= python
PIP ?= pip

# Default target shows help
help:
	@echo "ToolOps Development Commands"
	@echo "============================"
	@echo ""
	@echo "  make install      Install the package locally"
	@echo "  make install-dev  Install local package and development tools"
	@echo "  make test         Run the full test suite with coverage"
	@echo "  make lint         Run Ruff and Black checks"
	@echo "  make format       Auto-format code with Black"
	@echo "  make typecheck    Run mypy in strict mode"
	@echo "  make coverage     Run tests and open HTML coverage report"
	@echo "  make clean        Remove build artifacts and cache files"
	@echo "  make docker-up    Start development environment (Docker)"
	@echo "  make docker-down  Stop development environment"
	@echo ""

# Installation targets
install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -r requirements.txt

# Test target — runs pytest with coverage, enforces 80% minimum
test:
	pytest tests/ -v \
		--cov=toolops \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=80

# Lint target — runs Ruff checks and Black format check
lint:
	ruff check toolops tests
	black --check --diff toolops tests

# Format target — auto-formats code with Black
format:
	black toolops tests

# Type-check target — runs mypy in strict mode on the package
typecheck:
	mypy --strict toolops

# Coverage target — generates HTML report and opens it
coverage:
	pytest tests/ -v \
		--cov=toolops \
		--cov-report=html \
		--cov-report=term-missing
	@echo "HTML coverage report: htmlcov/index.html"

# Clean target — removes build artifacts, caches, and temp files
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ \
		htmlcov/ .coverage .ruff_cache .tmp_test_cli/ \
		toolops/__pycache__ toolops/integrations/__pycache__ \
		tests/__pycache__ .benchmarks/

# Docker development environment
docker-up:
	docker-compose -f docker-compose.yml up -d --build

docker-down:
	docker-compose -f docker-compose.yml down
