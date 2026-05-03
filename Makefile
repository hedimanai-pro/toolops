.PHONY: install test lint format typecheck build clean

install:
	pip install -e ".[dev,all]"

test:
	pytest

lint:
	ruff check toolops tests
	black --check toolops tests

format:
	black toolops tests
	ruff check --fix toolops tests

typecheck:
	mypy toolops

build:
	python -m build

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache