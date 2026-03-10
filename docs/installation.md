# Installation

You can install metakernel through `pip`:

```bash
pip install metakernel --upgrade
```

## Installing a kernel

MetaKernel-based kernels expose an `install` subcommand that registers the kernel with Jupyter:

```bash
python -m my_kernel install --user
```

All flags are forwarded to `jupyter kernelspec install`. Common options:

`--user`

: Install into the current user's Jupyter data directory.

`--sys-prefix`

: Install into the active Python environment's prefix (useful with conda/venv).

`--prefix <path>`

: Install into an arbitrary prefix.

`--name <name>`

: Override the kernel directory name used by Jupyter.

`--display-name <name>`

: Set the display name shown in the JupyterLab kernel picker. This is written into the `display_name` field of the installed `kernel.json` and is useful when running multiple installations of the same kernel side-by-side (for example, one per environment):

````
```bash
python -m my_kernel install --user --name my-kernel-dev --display-name "My Kernel (dev)"
```
````
