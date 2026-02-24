# Contributing to metakernel

## Prerequisites

- [uv](https://github.com/astral-sh/uv) — Python environment management
- [just](https://github.com/casey/just) — task runner
- [ipcluster](https://ipyparallel.readthedocs.io/) — optional, required for parallel magic tests

## Setup

```bash
git clone https://github.com/metakernel-project/metakernel.git
cd metakernel

# If you use direnv:
direnv allow

# Otherwise, create and activate the venv manually:
uv venv --seed --python 3.9
source .venv/bin/activate

# Install all packages for development:
just install
```

## Common tasks

| Command | Description |
|---------|-------------|
| `just install` | Install all packages for development |
| `just test` | Run core test suite (no cluster needed) |
| `just test-file <path>` | Run a specific test file or test |
| `just test-parallel` | Full suite with ipcluster (parallel magic tests) |
| `just cover` | Run tests with coverage |
| `just docs` | Build Sphinx HTML docs |
| `just help` | Regenerate `magics/README.md` from docstrings |
| `just try-python` | Launch metakernel_python interactively |
| `just try-echo` | Launch metakernel_echo interactively |
| `just clean` | Remove build artifacts and cached bytecode |

Run `just` (or `just --list`) to see all available recipes.

### Running a single test

```bash
just test-file metakernel/tests/test_metakernel.py
just test-file metakernel/tests/test_metakernel.py::test_magics
```

## Adding a magic

Each magic lives in `metakernel/magics/{name}_magic.py`. Define a class that subclasses `Magic` and add methods named `line_{name}` and/or `cell_{name}`. The method docstring becomes the user-visible help text. See existing magics in that directory for examples.

MetaKernel auto-discovers magics at startup via `reload_magics()`. User-local magics can be placed in `~/.local/share/jupyter/kernels/metakernel/magics/`.

## Creating a new kernel

Subclass `MetaKernel` (or `ProcessMetaKernel` for subprocess-based kernels) and implement `do_execute_direct`. Set `implementation`, `language`, `language_version`, `banner`, and `language_info` class attributes. See `metakernel_python/` and `metakernel_echo/` for reference implementations.
