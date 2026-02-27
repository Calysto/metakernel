from typing import Any

from IPython.display import clear_output as ipclear_output
from IPython.display import display as ipdisplay


def display(*args: Any, **kwargs: Any) -> None:
    from . import get_metakernel

    kernel = get_metakernel()
    if kernel:
        kernel.Display(*args, **kwargs)
    else:
        ipdisplay(*args, **kwargs)  # type:ignore[no-untyped-call]


def clear_output(*args: Any, **kwargs: Any) -> None:
    from . import get_metakernel

    kernel = get_metakernel()
    if kernel:
        kernel.clear_output(*args, **kwargs)
    else:
        ipclear_output(*args, **kwargs)  # type:ignore[no-untyped-call]
