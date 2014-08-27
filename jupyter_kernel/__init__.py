from .magickernel import MagicKernel
from .magic import Magic

JUPYTER_INSTANCE = None

def get_jupyter():
    return JUPYTER_INSTANCE

__all__ = ['Magic', 'MagicKernel']

del magic, magickernel
