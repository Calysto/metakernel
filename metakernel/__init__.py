from .metakernel import MetaKernel
import .pyexpect
from .process_metakernel import ProcessMetaKernel
from .magic import Magic, option
from .parser import Parser

__all__ = ['Magic', 'MetaKernel', 'option']

__version__ = '0.3'

del magic, metakernel, parser, process_metakernel, pyexpect
