# metakernel development tasks

# Default: list available recipes
default:
    @just --list

# Install all package for development
install: clean
    uv sync --extra parallel --extra activity --group test

# Remove build artifacts and cached bytecode
clean:
    rm -rf build dist
    find . \( -name "*.pyc" -o -name "*.py,cover" \) -delete

# Run the core test suite
test:
    uv run --group test pytest

# Run a specific test file or test (e.g. just test-file metakernel/tests/test_metakernel.py)
test-file FILE:
    uv run --group test pytest {{FILE}}

# Run the full test suite with parallel cluster
test-parallel: clean
    ipcluster start -n=3 &
    uv run --group test pytest -W default || uv run --group test pytest -W default --lf
    ipcluster stop
    uv run --group test python metakernel_python/test_metakernel_python.py

# Run tests with coverage
cover: clean
    ipcluster start -n=3 &
    uv run --group cover pytest --cov=metakernel || uv run --group cover pytest --lf --cov=metakernel
    ipcluster stop
    uv run --group cover python metakernel_python/test_metakernel_python.py
    uv run --group cover coverage annotate

# Build Sphinx HTML documentation
docs: clean
    uv run --group docs make -C docs html SPHINXOPTS="-W"

# Run type checking
typing:
    uv run --group typing mypy metakernel

# Regenerate magics/README.md from magic docstrings
help:
    uv run python docs/generate_help.py

# Launch metakernel_python kernel interactively (for manual testing)
try-python:
    uv run --with ./metakernel_python --with ipython ipython console --kernel=metakernel_python

# Launch metakernel_echo kernel interactively (for manual testing)
try-echo:
    uv run --with ./metakernel_echo --with ipython ipython console --kernel=metakernel_echo
