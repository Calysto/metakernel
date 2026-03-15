# Creating a New Magic

This guide explains how to write a custom magic for any MetaKernel-based kernel — whether you are a kernel author bundling magics with your kernel, or an end-user who wants to add a magic to an existing kernel.

## Magic file conventions

Each magic lives in its own file named `{name}_magic.py`. The file must:

1. Define a class that inherits from `metakernel.Magic`.
1. Implement one or both of:
   - `line_{name}(self, ...)` — invoked by `%name arg1 arg2`
   - `cell_{name}(self, ...)` — invoked by `%%name arg1\ncell body`
1. Expose a module-level `register_magics(kernel)` function so that MetaKernel can load it automatically.

## A minimal example

```python
# greet_magic.py

from metakernel import Magic, MetaKernel


class GreetMagic(Magic):

    def line_greet(self, name="world"):
        """
        %greet [name]

        Print a friendly greeting.

        Example::

            %greet Alice
        """
        self.kernel.Print(f"Hello, {name}!")


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(GreetMagic)
```

Save this file and use it as described in the next section.

## Installing a magic

There are two ways to make a magic available in your kernel.

### User-local installation (any kernel)

Drop the magic file into `~/.ipython/metakernel/magics/`. MetaKernel creates this directory automatically and searches it on every startup.

```bash
cp greet_magic.py ~/.ipython/metakernel/magics/
```

Then, in a running notebook cell, reload the magic registry:

```
%reload_magics
```

The new magic is now available for the rest of the session without restarting the kernel. On future kernel starts it will be loaded automatically.

### Downloading from a URL

Use the built-in `%install_magic` line magic to fetch a magic file directly from a URL and install it into your local magic directory:

```
%install_magic https://example.com/path/to/greet_magic.py
```

`%install_magic` downloads the file and then runs `%reload_magics` for you automatically.

### Bundling with a kernel package

Place the magic file inside a `magics/` subpackage alongside your kernel module. MetaKernel discovers these at startup via `reload_magics()`:

```
my_kernel/
├── __init__.py
└── magics/
    └── greet_magic.py
```

No extra registration step is required — the `register_magics(kernel)` function in each file is called automatically.

## Debugging magic loading

If a magic is not appearing as expected, use `%lsmagic -v` to see which directories MetaKernel searched and whether any files failed to load:

```
%lsmagic -v
```

The output includes:

- **Magic search paths** — the directories that were scanned for `*_magic.py` files. For a bundled kernel magic, the first entry should be the `magics/` subdirectory of your kernel package. If your magic file is not in one of these directories, it will never be found.
- **Load errors** — any exceptions raised while importing a magic file or calling its `register_magics` function. The error message points directly to the file and the cause.

If your magic is missing after a regular (non-editable) install, verify that the `magics/` directory is included in your package. With hatchling add it explicitly if needed:

```toml
[tool.hatch.build.targets.wheel]
packages = ["my_kernel"]
```

After fixing the file placement, restart the kernel and run `%lsmagic -v` again to confirm the path appears and no errors are reported.

## Writing a cell magic

A cell magic receives the rest of the cell as a body via `self.code`. Set `self.evaluate = False` if you do not want the kernel to evaluate the cell body as normal code after the magic runs.

```python
# repeat_magic.py

from metakernel import Magic, MetaKernel


class RepeatMagic(Magic):

    def cell_repeat(self, times=2):
        """
        %%repeat [times]

        Print the cell body *times* times.

        Example::

            %%repeat 3
            Hello!
        """
        for _ in range(int(times)):
            self.kernel.Print(self.code)
        self.evaluate = False   # don't pass the body to the kernel


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(RepeatMagic)
```

## Adding options with `@option`

Use the `option` decorator (backed by `optparse`) to add named flags to a magic. The decorator appends option documentation to the magic's docstring automatically.

```python
# shout_magic.py

from metakernel import Magic, MetaKernel, option


class ShoutMagic(Magic):

    @option(
        "-u", "--upper",
        action="store_true",
        default=False,
        help="Convert output to upper case.",
    )
    def line_shout(self, message="hello", upper=False):
        """
        %shout [-u] message

        Print a message, optionally in upper case.

        Example::

            %shout -u hello world
        """
        if upper:
            message = message.upper()
        self.kernel.Print(message)


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(ShoutMagic)
```

Options can also be used on cell magics — see `tutor_magic.py` in the MetaKernel source for a complete example.

## Kernel output helpers

Inside a magic method, use the following helpers on `self.kernel`:

`self.kernel.Print(text)`

: Send plain text to the notebook output area.

`self.kernel.Error(text)`

: Send error text (displayed in red by most frontends).

`self.kernel.Display(obj)`

: Display any rich IPython displayable (e.g. `IPython.display.HTML`, `IFrame`, images).

`self.kernel.set_variable(name, value)`

: Inject a variable into the kernel's namespace so the user can access it after the magic runs.

`self.kernel.get_variable(name)`

: Read a variable from the kernel's namespace.

`self.kernel.schedule_display_output(callback)`

: Schedule a zero-argument callable to run on the kernel's main IO loop. Use this when you need to send output from a background thread (for example, in response to an event from a connected application). ZMQ sockets are not thread-safe, so calling `Print` or `Display` directly from a background thread is unsafe — `schedule_display_output` routes the call through Tornado's thread-safe `add_callback`:

````
```python
import threading

def line_watch(self, interval="5"):
    """
    %watch [interval]

    Start a background thread that prints a status message every *interval* seconds.
    """
    def _monitor():
        import time
        while True:
            time.sleep(float(interval))
            self.kernel.schedule_display_output(
                lambda: self.kernel.Print("still running…")
            )

    threading.Thread(target=_monitor, daemon=True).start()
```
````

`self.code`

: The raw cell body (cell magics only); available after `call_magic` sets it, or directly inside `cell_*` methods.

`self.evaluate`

: Boolean (default `True`). Set to `False` inside a cell magic to prevent the kernel from evaluating `self.code` as normal code.

## Docstrings and help

The docstring of a magic method is displayed when the user runs:

```
%greet?
%%greet?
```

It is also executed as a doctest by pytest (`--doctest-modules`), so keep examples valid. A good docstring follows this structure:

```
%magic_name [args]

One-line summary.

Longer explanation if needed.

Example::

    %magic_name value
```

## IPython / Jupyter notebook compatibility

If you want your magic to work in plain IPython (not just in MetaKernel-based kernels), add a `register_ipython_magics()` function to the file:

```python
def register_ipython_magics() -> None:
    from metakernel import IPythonKernel
    from metakernel.magic import register_line_magic

    kernel = IPythonKernel()
    magic = GreetMagic(kernel)

    @register_line_magic
    def greet(line: str) -> None:
        magic.line_greet(line or "world")
```

MetaKernel calls `register_ipython_magics()` automatically when loading magics into an IPython session. For cell magics, use `register_cell_magic` instead.

See `tutor_magic.py` for a complete working example of both functions.
