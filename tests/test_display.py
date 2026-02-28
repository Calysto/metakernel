from unittest.mock import MagicMock, patch

import pytest

from metakernel import MetaKernel
from metakernel import display as display_module
from tests.utils import get_kernel


@pytest.fixture(autouse=True)
def reset_meta_kernel():
    """Restore MetaKernel.meta_kernel to its original value after each test."""
    original = MetaKernel.meta_kernel
    yield
    MetaKernel.meta_kernel = original


# --- display() ---


def test_display_with_kernel_calls_kernel_Display() -> None:
    kernel = get_kernel()
    MetaKernel.meta_kernel = kernel
    mock_display = MagicMock()
    kernel.Display = mock_display  # type: ignore[method-assign]

    display_module.display("hello")

    mock_display.assert_called_once_with("hello")


def test_display_with_kernel_passes_kwargs() -> None:
    kernel = get_kernel()
    MetaKernel.meta_kernel = kernel
    mock_display = MagicMock()
    kernel.Display = mock_display  # type: ignore[method-assign]

    display_module.display("hello", clear_output=True)

    mock_display.assert_called_once_with("hello", clear_output=True)


def test_display_without_kernel_calls_ipdisplay() -> None:
    MetaKernel.meta_kernel = None

    with patch("metakernel.display.ipdisplay") as mock_ipdisplay:
        display_module.display("hello")
        mock_ipdisplay.assert_called_once_with("hello")


def test_display_without_kernel_passes_kwargs() -> None:
    MetaKernel.meta_kernel = None

    with patch("metakernel.display.ipdisplay") as mock_ipdisplay:
        display_module.display("obj", metadata={"key": "val"})
        mock_ipdisplay.assert_called_once_with("obj", metadata={"key": "val"})


def test_display_without_kernel_multiple_args() -> None:
    MetaKernel.meta_kernel = None

    with patch("metakernel.display.ipdisplay") as mock_ipdisplay:
        display_module.display("a", "b", "c")
        mock_ipdisplay.assert_called_once_with("a", "b", "c")


# --- clear_output() ---


def test_clear_output_with_kernel_calls_kernel_clear_output() -> None:
    kernel = get_kernel()
    MetaKernel.meta_kernel = kernel
    mock_clear = MagicMock()
    kernel.clear_output = mock_clear  # type: ignore[method-assign]

    display_module.clear_output()

    mock_clear.assert_called_once_with()


def test_clear_output_with_kernel_passes_wait() -> None:
    kernel = get_kernel()
    MetaKernel.meta_kernel = kernel
    mock_clear = MagicMock()
    kernel.clear_output = mock_clear  # type: ignore[method-assign]

    display_module.clear_output(wait=True)

    mock_clear.assert_called_once_with(wait=True)


def test_clear_output_without_kernel_calls_ipclear_output() -> None:
    MetaKernel.meta_kernel = None

    with patch("metakernel.display.ipclear_output") as mock_clear:
        display_module.clear_output()
        mock_clear.assert_called_once_with()


def test_clear_output_without_kernel_passes_kwargs() -> None:
    MetaKernel.meta_kernel = None

    with patch("metakernel.display.ipclear_output") as mock_clear:
        display_module.clear_output(wait=True)
        mock_clear.assert_called_once_with(wait=True)
