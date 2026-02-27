# Note: This justfile is meant for MetaKernel developer use only.
# Run `just` to list all available recipes.

# Default: list all recipes
default:
    @just --list

# Install for development
install:
    uv sync
    uv tool run pre-commit install

# Clean build artifacts
clean:
    rm -rf build dist
    find . -name "*.pyc" -delete
    find . -name "*.py,cover" -delete

# Run core test suite (no cluster needed)
test *args="":
    uv run pytest {{args}}

# Run full test suite with ipcluster
test-parallel *args="":
    uv run --with ipyparallel ipcluster start -n=3 &
    uv run pytest {{args}}
    uv run --with ipyparallel ipcluster stop

# Run tests with coverage
cover:
    uv run --with ipyparallel ipcluster start -n=3 &
    uv run --group coverage pytest -x --cov=metakernel
    uv run coverage annotate
    uv run --with ipyparallel ipcluster stop

# Build Sphinx HTML docs
docs:
    uv run --group docs sphinx-build -W -d docs/_build/doctrees docs docs/_build/html

# Regenerate magics/README.md from magic docstrings
help:
    uv run python docs/generate_help.py

# Run type checking
typing:
    uv run --group typing mypy . --install-types --non-interactive

# Run linter
lint:
    just pre-commit ruff-format
    just pre-commit ruff-check

# Run pre-commit hook
pre-commit *args="":
    uv tool run pre-commit run --all-files {{args}}