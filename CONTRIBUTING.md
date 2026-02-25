# Contributing to MetaKernel

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [just](https://github.com/casey/just) — command runner

## Setting up the development environment

Clone the repository and install all dependencies (including test, docs, and coverage groups):

```bash
git clone https://github.com/Calysto/metakernel
cd metakernel
just install
```

This runs `uv sync --all-groups` and installs the pre-commit hooks. It creates a
virtual environment with `metakernel` in editable mode along with `metakernel_python`
(local path dependency) and all development dependency groups.

## Available recipes

Run `just` to list all recipes. The most common ones are:

```bash
just install          # install for development
just test             # core test suite (no cluster needed)
just test-file <path> # run a single test file or test function
just test-parallel    # full suite with ipcluster
just cover            # run with coverage
just docs             # build Sphinx HTML docs
just help             # regenerate magics/README.md from docstrings
just typing           # run mypy type checks
just lint             # run ruff linter
just clean            # remove build artifacts
```

### Examples

```bash
just test-file tests/test_metakernel.py
just test-file tests/test_metakernel.py::test_magics
```

## Dependency groups

Dependencies are managed with uv [dependency groups](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-groups):

| Group | Purpose |
| ---------- | ---------------------------------------- |
| `test` | pytest, jupyter_kernel_test, metakernel_python (local) |
| `docs` | Sphinx and extensions |
| `coverage` | pytest-cov and coverage (includes test) |

To install only a specific group:

```bash
uv sync --group test
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
