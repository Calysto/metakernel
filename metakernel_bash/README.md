**MetaKernel Bash** is a Jupyter kernel using MetaKernel magics, shell, help, and parallel processing tools. This code provides the core of the Bash magics for MetaKernel.

## Install

First, you need to install the metakernel_bash library and dependencies:

```shell
pip install metakernel_bash --upgrade
```

Then, you need to install the metakernel bash kernel spec:

```shell
python -m metakernel_bash install
```

## Running

You can then run the metakernel_bash kernel as a console, notebook, etc.:

```shell
jupyter console --kernel=metakernel_bash
```

## Dependencies

1. IPython 3
1. MetaKernel (installed with pip)
