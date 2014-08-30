from .magickernel import MagicKernel
from .magic import Magic, argument

__all__ = ['Magic', 'MagicKernel, argument']
JUPYTER_INSTANCE = None

def get_jupyter():
    return JUPYTER_INSTANCE

del magic, magickernel
