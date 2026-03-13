# Creating a New Kernel

This guide walks through building a new Jupyter kernel using MetaKernel as the base class. MetaKernel handles magic dispatch, tab completion, help, history, and display so you can focus on the language-specific execution layer.

See the [metakernel_echo](https://github.com/calysto/metakernel/tree/main/metakernel_echo) and [metakernel_python](https://github.com/calysto/metakernel/tree/main/metakernel_python) directories in this repository as minimal reference implementations.

## Project layout

A typical MetaKernel-based project looks like this:

```
my_kernel/
├── pyproject.toml
├── my_kernel/
│   ├── __init__.py      # kernel class
│   ├── __main__.py      # entry-point for -m invocation
│   └── magics/          # optional: kernel-specific magics
│       └── my_magic.py
└── data_kernelspec/
    └── share/
        └── jupyter/
            └── kernels/
                └── my_kernel/
                    └── kernel.json
```

## Implementing the kernel class

Subclass `MetaKernel` and implement `do_execute_direct`. Set the required class attributes so that Jupyter knows how to display the kernel:

```python
# my_kernel/__init__.py

from metakernel import MetaKernel

__version__ = "0.1.0"


class MyKernel(MetaKernel):
    implementation = "My Kernel"
    implementation_version = "1.0"
    language = "my_language"
    language_version = "0.1"
    banner = "My Kernel – evaluates My Language expressions"
    language_info = {
        "mimetype": "text/plain",
        "name": "my_language",
        "file_extension": ".my",
        "help_links": MetaKernel.help_links,
    }

    def get_usage(self):
        return "This is My Kernel."

    def do_execute_direct(self, code):
        """Evaluate *code* and return the result as a string."""
        # Replace this with your language's evaluation logic.
        return code.rstrip()
```

For kernels that wrap a subprocess REPL, subclass `ProcessMetaKernel` instead and use `REPLWrapper` to drive the child process.

## Adding an entry-point module

Jupyter launches kernels via `python -m my_kernel -f <connection_file>`, so add a `__main__.py`:

```python
# my_kernel/__main__.py

from my_kernel import MyKernel

MyKernel.run_as_main()
```

## Kernel spec (kernel.json)

Create `data_kernelspec/share/jupyter/kernels/my_kernel/kernel.json`:

```json
{
    "argv": ["python", "-m", "my_kernel", "-f", "{connection_file}"],
    "display_name": "My Kernel",
    "language": "my_language",
    "name": "my_kernel"
}
```

Optional keys include `"codemirror_mode"`, `"env"`, and `"interrupt_mode"`. See the [Jupyter kernel specification](https://jupyter-client.readthedocs.io/en/stable/kernels.html) for the full list.

## Rich display output

MetaKernel provides two complementary display paths depending on whether your kernel produces Python objects or raw MIME data.

### Python objects

Call `self.Display(obj)` from within `do_execute_direct` (or from a magic). MetaKernel passes the object through IPython's display formatter, which invokes `_repr_html_`, `_repr_svg_`, `_repr_png_`, and similar methods automatically:

```python
def do_execute_direct(self, code):
    from IPython.display import HTML
    return HTML("<b>result</b>")
```

You can also return the object directly from `do_execute_direct` and MetaKernel will format and publish it as an `execute_result`.

### Raw MIME bundles (non-Python kernels)

If your kernel generates display data natively — for example a C++ kernel that produces SVG or HTML — use `self.DisplayData(data)` to send a raw MIME bundle directly without going through IPython's formatter:

```python
def do_execute_direct(self, code):
    # Call your language runtime and get MIME data back
    mime_bundle = evaluate(code)  # e.g. {'text/html': '<b>result</b>', 'text/plain': 'result'}
    self.DisplayData(mime_bundle)
```

`DisplayData` accepts an optional `metadata` dict keyed by MIME type:

```python
self.DisplayData(
    {"image/svg+xml": svg_string, "text/plain": "[SVG image]"},
    metadata={"image/svg+xml": {"isolated": True}},
)
```

You can also return a MIME bundle dict directly from `do_execute_direct`. MetaKernel detects dicts whose keys are all MIME types and publishes them as `execute_result` without formatting:

```python
def do_execute_direct(self, code):
    return {"text/html": "<b>result</b>", "text/plain": "result"}
```

As a convenience, `self.Display()` also accepts a raw MIME bundle dict and routes it to `DisplayData` automatically, so you can pass MIME data through the same call site as Python objects.

## Adding custom magics

Place magic files in a `magics/` subpackage alongside your kernel module. Each file should be named `{name}_magic.py` and define a class that inherits from `Magic`. Line magics are methods named `line_{name}` and cell magics are `cell_{name}`:

```python
# my_kernel/magics/greet_magic.py

from metakernel import Magic


class GreetMagic(Magic):

    def line_greet(self, name="world"):
        """
        %greet [name]

        Print a greeting.

        Example::

            %greet Alice
        """
        self.kernel.Print(f"Hello, {name}!")


def register_magics(kernel):
    kernel.register_magics(GreetMagic)
```

MetaKernel auto-discovers magics in `magics/` at startup via `reload_magics()`. Users can also install additional magics in `~/.local/share/jupyter/kernels/metakernel/magics/`.

## pyproject.toml

A minimal `pyproject.toml` using [hatchling](https://hatch.pypa.io/) (the same build backend used by the reference kernels in this repository):

```toml
[build-system]
requires = ["hatchling >= 1.10.0", "jupyter_client"]
build-backend = "hatchling.build"

[project]
name = "my_kernel"
version = "0.1.0"
dependencies = ["metakernel"]

[tool.hatch.build.targets.wheel.shared-data]
"data_kernelspec/share" = "share"
```

The `shared-data` table installs the kernelspec into the wheel's data directory so that `pip install` registers the kernel automatically.

For full packaging guidelines, including how to handle logos, kernel spec installation during development, and publishing to PyPI, see the official [Jupyter kernel packaging documentation](https://jupyter-client.readthedocs.io/en/stable/kernels.html#packaging).

## Testing

Use the `EvalKernel` fixture from `tests/utils.py` as a reference for writing unit tests. Instantiate your kernel with a ZMQ socket and logger in the same style, then call `do_execute_direct` and inspect the result.

The MetaKernel test suite uses `pytest` with `--doctest-modules`, so any doctests in your magic docstrings are executed automatically.

### Testing with jupyter_kernel_test

[jupyter_kernel_test](https://github.com/jupyter/jupyter_kernel_test) is the standard library for validating that a kernel correctly implements the [Jupyter messaging protocol](https://jupyter-client.readthedocs.io/en/stable/messaging.html). It runs the kernel as a real subprocess and exercises it over ZMQ, so it catches integration issues that unit tests miss.

**Install:**

```bash
pip install jupyter_kernel_test
```

Add it to your development dependencies in `pyproject.toml`:

```toml
[project.optional-dependencies]
test = ["pytest", "jupyter_kernel_test"]
```

**Writing tests:**

Subclass `jupyter_kernel_test.KernelTests` and set class attributes to describe your kernel's expected behaviour. Only `kernel_name` is required; everything else is optional but enables additional protocol checks:

```python
# test_my_kernel.py

import unittest
import jupyter_kernel_test as jkt


class MyKernelTests(jkt.KernelTests):
    # REQUIRED: matches the directory name under
    # share/jupyter/kernels/ (i.e. what you pass to
    # `jupyter console --kernel <kernel_name>`)
    kernel_name = "my_kernel"

    # OPTIONAL checks below

    # checked against language_info.name in kernel_info_reply
    language_name = "my_language"

    # checked against language_info.file_extension
    file_extension = ".my"

    # code that writes exactly "hello, world" to stdout
    code_hello_world = "print('hello, world')"

    # code that writes anything to stderr
    code_stderr = "import sys; print('error', file=sys.stderr)"

    # tab-completion samples: `text` is the partial input,
    # `matches` is a set of strings that must appear in the reply
    completion_samples = [
        {"text": "pri", "matches": {"print"}},
    ]

    # used by console clients to decide whether to execute on <Enter>
    complete_code_samples = ["1 + 1"]
    incomplete_code_samples = ["def f(x):"]

    # (code, expected string repr of the result) pairs
    code_execute_result = [
        {"code": "1 + 1", "result": "2"},
    ]

    # code that raises an error and sends a traceback
    code_generate_error = "raise ValueError('oops')"

    # object name that the kernel can provide inspection help for
    code_inspect_sample = "print"


if __name__ == "__main__":
    unittest.main()
```

`KernelTests` inherits from `unittest.TestCase`, so the suite runs under either `pytest` or plain `python -m unittest`.

**What gets tested:**

`KernelTests` automatically runs a suite of protocol-level checks based on the attributes you provide:

- `kernel_info_reply` fields (`language_name`, `file_extension`)
- `execute_reply` status for valid and error-generating code
- stdout / stderr routing (`code_hello_world`, `code_stderr`)
- `execute_result` content (`code_execute_result`)
- tab completion replies (`completion_samples`)
- code-completeness replies (`complete_code_samples`, `incomplete_code_samples`)
- inspection replies (`code_inspect_sample`)

The `metakernel_python` kernel in this repository uses this approach; see `metakernel_python/test_metakernel_python.py` for a complete working example.

## Debugging

To see the full kernel log output while interacting with your kernel, launch it through `jupyter console` with debug logging enabled. If you don't have it installed, run `pip install jupyter-console` first.

```bash
jupyter console --log-level=debug --kernel=octave
```

Replace `octave` with the name of your kernel (the directory name under `share/jupyter/kernels/`). Debug output includes the raw ZMQ messages exchanged between the client and kernel, which is useful for diagnosing protocol-level issues.

## Troubleshooting

### Kernel hangs at startup on Windows (encoding mismatch)

If your kernel uses `ProcessMetaKernel` / `REPLWrapper` and hangs indefinitely at startup on Windows — with `pexpect` timing out while waiting for the initial prompt — the cause is often an encoding mismatch. `REPLWrapper` defaults to `encoding="utf-8"`, but many Windows programs (including gnuplot) write their startup output in the system code page (e.g. `cp1252`). When pexpect can't decode the bytes it receives it never matches the prompt pattern, so the kernel never finishes initialising.

Pass the correct encoding when constructing `REPLWrapper`:

```python
from metakernel.replwrap import REPLWrapper

repl = REPLWrapper("gnuplot", r"gnuplot>", None, encoding="cp1252")
```

To find the encoding your program uses, run it in a terminal and check what Python reports:

```python
import locale
print(locale.getpreferredencoding())
```

Or start with `encoding="cp1252"` on Western-European Windows locales and `encoding="utf-8"` everywhere else.
