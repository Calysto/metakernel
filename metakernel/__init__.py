from ._metakernel import MetaKernel
from . import pexpect
from . import replwrap
from .process_metakernel import ProcessMetaKernel
from .magic import Magic, option
from .parser import Parser

__all__ = ['Magic', 'MetaKernel', 'option']

__version__ = '0.5.1'

del magic, _metakernel, parser, process_metakernel
