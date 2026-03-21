# Contributing to MetaKernel

## Prerequisites

- [Poetry](https://python-poetry.org/) — Python package manager (`pipx install "poetry>=2.3,<3"`)
- [just](https://github.com/casey/just) — command runner

## Setting up the development environment

Clone the repository and install all dependencies (including test, docs, and coverage groups):

```bash
git clone https://github.com/Calysto/metakernel
cd metakernel
just install
```

This runs `poetry install --with dev` and installs the pre-commit hooks. It creates a
virtual environment with `metakernel` in editable mode along with `metakernel_python`
and `metakernel_echo` (local path dependencies) and all development dependency groups.

## Available recipes

Run `just` to list all recipes. The most common ones are:

```bash
just install           # install for development
just test              # core test suite (no cluster needed)
just test-file <path>  # run a single test file or test function
just test-parallel     # full suite with ipcluster
just cover             # run with coverage
just run-notebooks     # execute example notebooks
just docs              # build MkDocs HTML docs
just help              # regenerate magics/README.md from docstrings
just typing            # run mypy type checks
just lint              # run ruff linter
just clean             # remove build artifacts
```

### Examples

```bash
just test-file tests/test_metakernel.py
just test-file tests/test_metakernel.py::test_magics
```

## Dependency groups

Dependencies are managed with [Poetry dependency groups](https://python-poetry.org/docs/managing-dependencies/#dependency-groups):

| Group | Purpose |
| ---------- | ---------------------------------------- |
| `test` | pytest, jupyter_kernel_test, metakernel_python (local) |
| `docs` | MkDocs and extensions |
| `coverage` | pytest-cov and coverage (includes test) |

To install only a specific group:

```bash
poetry install --with test
```

## Code style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting,
enforced via pre-commit hooks. The hooks are installed automatically by `just install`.

Lint manually with `just lint`.

## Running tests

The core test suite does not require a running ipcluster:

```bash
just test
```

For the full parallel test suite:

```bash
just test-parallel
```

This starts an ipcluster with 3 engines, runs all tests, and stops the cluster on exit.

## Example notebooks

The `examples/` directory contains demonstration notebooks for various MetaKernel-based kernels. All notebooks except `Calysto Processing.ipynb` and `SAS_metakernel_example.ipynb` are executed as part of CI.

To run them locally:

```bash
just run-notebooks
```

This script (`scripts/run_notebooks.sh`) starts an ipcluster with 5 engines (required by `Mandelbrot.ipynb` for parallel execution), runs each notebook via `jupyter nbconvert --execute`, and then stops the cluster. All required kernels and packages are installed via the `test-all` dependency group:

| Notebook | Kernel | Package |
| --- | --- | --- |
| `Jigsaw in IPython.ipynb` | `python3` | `jupyter` |
| `Mandelbrot.ipynb` | `calysto_scheme` | `calysto-scheme` |
| `MetaKernel Echo Demo.ipynb` | `metakernel_echo` | `./metakernel_echo` |
| `MetaKernel Python Demo.ipynb` | `metakernel_python` | `./metakernel_python` |
| `Processing Magic in IPython.ipynb` | `python3` | `jupyter` |
| `Tutor Magic in IPython.ipynb` | `python3` | `jupyter` |

> **Note:** `Mandelbrot.ipynb` uses `n=30` rows and distributes work across cluster engines. The engine count must divide evenly into 30 — the script uses 5 engines (6 rows each).

## Building docs

```bash
just docs
```

Output is written to `docs/_build/html/`.

## Submitting a pull request

1. Fork the repository and create a branch from `master`.
1. Make your changes with tests where appropriate.
1. Ensure `just test` and `just lint` pass.
1. Open a pull request against `master`.
