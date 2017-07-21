**MetaKernel Echo** is a Jupyter kernel using MetaKernel magics, shell, help, and parallel processing tools. This code provides an example MetaKernel kernel.

## Install

First, you need to install the metakernel_echo library and dependencies:

```shell
pip install metakernel_echo --upgrade
```

Then, you need to install the metakernel echo kernel spec:

```shell
python metakernel_echo install
```

## Running

You can then run the metakernel_echo kernel as a console, notebook, etc.:

```shell
jupyter console --kernel=metakernel_echo
```

## Dependencies

1. IPython 3
1. MetaKernel (installed with pip)
