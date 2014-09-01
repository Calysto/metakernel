from .magickernel import MagicKernel
from .magic import Magic, option

__all__ = ['Magic', 'MagicKernel', 'option']

__version__ = '0.3dev'

JUPYTER_INSTANCE = None

def get_jupyter():
    return JUPYTER_INSTANCE

del magic, magickernel
