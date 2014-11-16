from __future__ import absolute_import
from .metakernel import MetaKernel
from .process_metakernel import ProcessMetaKernel
from .magic import Magic, option
from .parser import Parser

__all__ = ['Magic', 'MetaKernel', 'option']

__version__ = '0.3'

del magic, metakernel, parser, process_metakernel, pyexpect
