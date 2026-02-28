from typing import Any
from unittest.mock import MagicMock

import pytest

import metakernel.magics.kernel_magic as _km
from metakernel.magics.kernel_magic import register_ipython_magics
from metakernel_echo.metakernel_echo import MetaKernelEcho
from tests.utils import EvalKernel, clear_log_text, get_kernel, get_log_text


@pytest.fixture()
def ipython_magics(monkeypatch):
    """Yield (kernel_fn, kx_fn, mock_magic) with IPython registration stubbed out."""
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "IPython.core.magic.register_line_magic",
        lambda f: captured.update(kernel=f) or f,  # type:ignore[redundant-expr]
    )
    monkeypatch.setattr(
        "IPython.core.magic.register_cell_magic",
        lambda f: captured.update(kx=f) or f,  # type:ignore[redundant-expr]
    )

    mock_magic = MagicMock()
    monkeypatch.setattr(_km, "KernelMagic", lambda _kernel: mock_magic)

    register_ipython_magics()

    yield captured["kernel"], captured["kx"], mock_magic


def test_kernel_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%kx 42", False)
    results = get_log_text(kernel)
    assert "42" in results, results


def test_line_kernel_default_name() -> None:
    """line_kernel stores the sub-kernel under 'default' when no -k flag is given."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%kernel metakernel_echo.metakernel_echo MetaKernelEcho")

    mk = kernel.line_magics["kernel"]
    assert mk.kernel_name == "default"
    assert "default" in mk.kernels
    assert isinstance(mk.kernels["default"], MetaKernelEcho)
    # parent kernel is wired into the sub-kernel
    assert mk.kernels["default"].kernel is kernel  # type:ignore[attr-defined]


def test_line_kernel_named() -> None:
    """line_kernel stores the sub-kernel under the name given by -k."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(
        "%kernel metakernel_echo.metakernel_echo MetaKernelEcho -k linetest_named"
    )

    mk = kernel.line_magics["kernel"]
    assert mk.kernel_name == "linetest_named"
    assert "linetest_named" in mk.kernels
    assert isinstance(mk.kernels["linetest_named"], MetaKernelEcho)
    assert mk.kernels["linetest_named"].kernel is kernel  # type:ignore[attr-defined]


def test_line_kernel_invalid_module() -> None:
    """line_kernel logs an error when the module cannot be imported."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%kernel nonexistent_module_xyz SomeClass")

    assert "Error" in get_log_text(kernel)


def test_line_kernel_invalid_class() -> None:
    """line_kernel logs an error when the class does not exist in the module."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%kernel metakernel_echo.metakernel_echo NoSuchClass")

    assert "Error" in get_log_text(kernel)


def test_cell_kx_uses_current_kernel_name() -> None:
    """%%kx with no -k flag routes execution to the kernel set by the last %kernel call."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(
        "%kernel metakernel_echo.metakernel_echo MetaKernelEcho -k ctkx_default"
    )
    clear_log_text(kernel)

    kernel.do_execute("%%kx\nhello world")

    assert "hello world" in get_log_text(kernel)


def test_cell_kx_explicit_kernel_name() -> None:
    """%%kx -k NAME routes execution to the named sub-kernel."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(
        "%kernel metakernel_echo.metakernel_echo MetaKernelEcho -k ctkx_a"
    )
    kernel.do_execute(
        "%kernel metakernel_echo.metakernel_echo MetaKernelEcho -k ctkx_b"
    )
    clear_log_text(kernel)

    kernel.do_execute("%%kx -k ctkx_b\nrouted to b")

    assert "routed to b" in get_log_text(kernel)


# ---------------------------------------------------------------------------
# register_ipython_magics - inner `kernel` line-magic function
# ---------------------------------------------------------------------------


def test_ipython_kernel_two_parts_defaults_name(ipython_magics) -> None:
    """kernel(line) with exactly one space passes kernel_name='default' to line_kernel."""
    kernel_fn, _, mock_magic = ipython_magics

    kernel_fn("mymodule MyClass")

    mock_magic.line_kernel.assert_called_once_with("mymodule", "MyClass", "default")


def test_ipython_kernel_three_parts_uses_provided_name(ipython_magics) -> None:
    """kernel(line) with two spaces extracts the third token as kernel_name."""
    kernel_fn, _, mock_magic = ipython_magics

    kernel_fn("mymodule MyClass mykernel")

    mock_magic.line_kernel.assert_called_once_with("mymodule", "MyClass", "mykernel")


# ---------------------------------------------------------------------------
# register_ipython_magics - inner `kx` cell-magic function
# ---------------------------------------------------------------------------


def test_ipython_kx_nonempty_line_uses_line_as_name(ipython_magics) -> None:
    """kx(line, cell) uses line.strip() as the kernel name when non-empty."""
    _, kx_fn, mock_magic = ipython_magics

    kx_fn("mykernel", "some code")

    assert mock_magic.code == "some code"
    mock_magic.cell_kx.assert_called_once_with("mykernel")


def test_ipython_kx_empty_line_falls_back_to_default(ipython_magics) -> None:
    """kx(line, cell) uses 'default' as the kernel name when line is empty."""
    _, kx_fn, mock_magic = ipython_magics

    kx_fn("", "some code")

    assert mock_magic.code == "some code"
    mock_magic.cell_kx.assert_called_once_with("default")
