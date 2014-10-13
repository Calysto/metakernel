from .metakernel import MetaKernel, MetaKernelAdapter, MetaMagicKernel, ZmqKernel
from .magic import Magic, option

# FIXME: Is this export magic good Python style?
__all__ = ['Magic', 'MetaKernel', 'MetaKernelAdapter', 'MetaMagicKernel', 'ZmqKernel', 'option']

__version__ = '0.3'

del magic, metakernel
