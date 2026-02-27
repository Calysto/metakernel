"""A Jupyter kernel base class in Python which includes core magic functions (including help, command and file path completion, parallel and distributed processing, downloads, and much more)."""

from . import pexpect
from ._metakernel import (
    ExceptionWrapper,
    IPythonKernel,
    MetaKernel,
    MetaKernelApp,
    get_metakernel,
    register_ipython_magics,
)
from .magic import Magic, option
from .parser import Parser

__all__ = [
    "ExceptionWrapper",
    "IPythonKernel",
    "Magic",
    "MetaKernel",
    "MetaKernelApp",
    "Parser",
    "get_metakernel",
    "option",
    "pexpect",
    "register_ipython_magics",
]

try:
    from .process_metakernel import ProcessMetaKernel
    from .replwrap import REPLWrapper

    __all__ += ["ProcessMetaKernel", "REPLWrapper"]
except ImportError:
    pass

__version__ = "0.30.4"
