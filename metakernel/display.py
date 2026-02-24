
from IPython.display import display as ipdisplay, clear_output as ipclear_output
from IPython.display import *  # noqa: F401,F403


def display(*args, **kwargs) -> None:
    from . import get_metakernel
    kernel = get_metakernel()
    if kernel:
        kernel.Display(*args, **kwargs)
    else:
        ipdisplay(*args, **kwargs)

def clear_output(*args, **kwargs) -> None:
    from . import get_metakernel
    kernel = get_metakernel()
    if kernel:
        kernel.clear_output(*args, **kwargs)
    else:
        ipclear_output(*args, **kwargs)
