from ._metakernel import MetaKernel, IPythonKernel, register_ipython_magics, get_metakernel
from . import pexpect
from .replwrap import REPLWrapper, u
from .process_metakernel import ProcessMetaKernel
from .magic import Magic, option
from .parser import Parser

__all__ = ['Magic', 'MetaKernel', 'option']

__version__ = '0.11.2'

del magic, _metakernel, parser, process_metakernel
