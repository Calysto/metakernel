import asyncio
import importlib.util

import pytest

from tests.utils import EvalKernel, get_kernel

NO_MATPLOTLIB = importlib.util.find_spec("matplotlib") is None

pytestmark = pytest.mark.skipif(NO_MATPLOTLIB, reason="Requires matplotlib")


@pytest.fixture(autouse=True)
def restore_ipython_display():
    """Restore IPython.display.display after each test."""
    import IPython.display

    original = IPython.display.display
    yield
    IPython.display.display = original


def test_matplotlib_magic_sets_backend() -> None:
    """%matplotlib sets the matplotlib backend."""
    import matplotlib

    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%matplotlib agg", False))

    assert matplotlib.get_backend().lower() == "agg"


def test_matplotlib_magic_notebook_alias() -> None:
    """'notebook' is an alias for the 'nbagg' backend."""
    import matplotlib

    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%matplotlib notebook", False))

    assert matplotlib.get_backend().lower() == "nbagg"


def test_matplotlib_magic_inline_alias() -> None:
    """'inline' is an alias for the 'agg' backend (issue #227)."""
    import matplotlib

    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%matplotlib inline", False))

    assert matplotlib.get_backend().lower() == "agg"


def test_matplotlib_magic_patches_ipython_display() -> None:
    """%matplotlib monkeypatches IPython.display.display with metakernel's."""
    import IPython.display

    import metakernel.display

    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%matplotlib agg", False))

    assert IPython.display.display is metakernel.display.display
