
from IPython.display import *

ipdisplay = display
ipclear_output = clear_output

def display(*args, **kwargs):
    from . import get_metakernel
    kernel = get_metakernel()
    if kernel:
        kernel.Display(*args, **kwargs)
    else:
        ipdisplay(*args, **kwargs)

def clear_output(*args, **kwargs):
    from . import get_metakernel
    kernel = get_metakernel()
    if kernel:
        kernel.clear_output(*args, **kwargs)
    else:
        ipclear_output(*args, **kwargs)
