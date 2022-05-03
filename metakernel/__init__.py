"""A Jupyter kernel base class in Python which includes core magic functions (including help, command and file path completion, parallel and distributed processing, downloads, and much more)."""
from ._metakernel import (
    ExceptionWrapper, MetaKernel, IPythonKernel, register_ipython_magics, get_metakernel,
    MetaKernelApp)
from . import pexpect
from .replwrap import REPLWrapper, u
from .process_metakernel import ProcessMetaKernel
from .magic import Magic, option
from .parser import Parser

__all__ = ['Magic', 'MetaKernel', 'option']

__version__ = '0.29.0'
