# Note: This justfile is meant for MetaKernel developer use only.
# Run `just` to list all available recipes.

# Default: list all recipes
default:
    @just --list

# Install for development
install:
    poetry install --with dev
    poetry run pre-commit install

# Clean build artifacts
clean:
    rm -rf build dist
    find . -name "*.pyc" -delete
    find . -name "*.py,cover" -delete

# Run core test suite (no cluster needed)
test *args="":
    poetry install --with test
    poetry run python -m metakernel_python install --sys-prefix
    poetry run pytest {{args}}

# Run full test suite with ipcluster and all optional magic dependencies
test-all *args="":
    #!/usr/bin/env bash
    set -euo pipefail
    poetry install --with test-all
    poetry run python -m metakernel_python install --sys-prefix
    bash scripts/start_cluster.sh 3
    poetry run pytest {{args}}
    poetry run ipcluster stop || true

# Alias for test-all
test-parallel *args="":
    just test-all {{args}}

# Run tests with coverage
cover *args="":
    #!/usr/bin/env bash
    set -euo pipefail
    poetry install --with coverage
    poetry run python -m metakernel_python install --sys-prefix
    bash scripts/start_cluster.sh 3
    poetry run pytest --cov=metakernel {{args}}
    poetry run coverage annotate
    poetry run coverage xml
    poetry run coverage report --show-missing
    poetry run ipcluster stop || true

# Build MkDocs HTML docs
docs:
    poetry install --with docs
    poetry run mkdocs build

# Serve MkDocs docs locally
docs-serve:
    poetry install --with docs
    poetry run mkdocs serve

# Regenerate magics/README.md from magic docstrings
help:
    poetry install --with test
    poetry run python docs/generate_help.py

# Run type checking
typing:
    poetry install --with typing
    poetry run mypy . --install-types --non-interactive

# Run linter
lint:
    just pre-commit ruff-format
    just pre-commit ruff-check
    just pre-commit validate-pyproject
    just pre-commit poetry-check

# Run example notebooks (excludes Calysto Processing and SAS)
run-notebooks:
    poetry install --with test-all
    bash scripts/run_notebooks.sh

# Run pre-commit hook
pre-commit *args="":
    poetry install --with dev
    poetry run pre-commit run --all-files {{args}}
