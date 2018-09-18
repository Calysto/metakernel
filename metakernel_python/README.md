**MetaKernel Python** is a Jupyter kernel using MetaKernel magics, shell, help, and parallel processing tools. This code provides the core of the Python magics for MetaKernel.

## Install

First, you need to install the metakernel_python library and dependencies:

```shell
pip install metakernel_python --upgrade
```

Then, you need to install the metakernel kernel spec:

```shell
python -m metakernel_python install
```

## Running

You can then run the metakernel_python kernel as a console, notebook, etc.:

```shell
jupyter console --kernel=metakernel_python
```

## Dependencies

1. IPython 3
2. MetaKernel (installed with pip)
