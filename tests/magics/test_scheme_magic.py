import asyncio
import importlib
import importlib.util
import sys
from typing import Any
from unittest.mock import patch

import pytest

from metakernel.magics.scheme_magic import register_ipython_magics
from tests.utils import get_kernel

has_calysto = importlib.util.find_spec("calysto_scheme") is not None

pytestmark = pytest.mark.skipif(
    not has_calysto, reason="calysto_scheme is not installed"
)


def test_scheme_line_magic_expression() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%scheme (+ 1 2)", None))
    magic = kernel.line_magics["scheme"]
    assert magic.retval == 3


def test_scheme_line_magic_define() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%scheme (define x 42)", None))
    magic = kernel.line_magics["scheme"]
    # define statements return a void Symbol in calysto_scheme, not None
    from calysto_scheme import scheme as cs  # type: ignore[import-untyped]

    assert magic.retval == cs.void_value


def test_scheme_cell_magic() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%scheme\n(+ 10 32)", None))
    magic = kernel.cell_magics["scheme"]
    assert magic.retval == 42
    assert not magic.evaluate


def test_scheme_cell_magic_multiline() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%scheme\n(define x 10)\n(+ x 5)", None))
    magic = kernel.cell_magics["scheme"]
    assert magic.retval == 15


def test_scheme_cell_magic_eval_output() -> None:
    kernel = get_kernel()
    # -e flag: Scheme result is used as code for the host kernel
    asyncio.run(kernel.do_execute('%%scheme -e\n"1 + 2"', None))
    magic = kernel.cell_magics["scheme"]
    assert magic.evaluate


def test_scheme_cell_magic_empty() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%scheme\n  ", None))
    magic = kernel.cell_magics["scheme"]
    # Whitespace-only cell: nothing is evaluated, retval stays None
    assert magic.retval is None


def test_scheme_help() -> None:
    kernel = get_kernel()
    helpstr = kernel.get_help_on("%scheme")
    assert "Scheme" in helpstr or "scheme" in helpstr, helpstr


def test_scheme_no_calysto(monkeypatch) -> None:
    kernel = get_kernel()
    magic = kernel.line_magics["scheme"]
    # The magic loader registers the module as "scheme_magic" in sys.modules
    sm = sys.modules["scheme_magic"]
    monkeypatch.setattr(sm, "scheme", None)
    with pytest.raises(Exception, match="calysto_scheme is required"):
        magic.eval("(+ 1 2)")


def test_post_process_returns_retval_when_not_none() -> None:
    """post_process prefers a non-None retval over self.retval."""
    kernel = get_kernel()
    magic = kernel.cell_magics["scheme"]
    magic.retval = "self-retval"
    assert magic.post_process("other-retval") == "other-retval"


def test_post_process_returns_self_retval_when_none() -> None:
    """post_process falls back to self.retval when retval is None."""
    kernel = get_kernel()
    magic = kernel.cell_magics["scheme"]
    magic.retval = "self-retval"
    assert magic.post_process(None) == "self-retval"


def test_module_import_error_sets_scheme_none() -> None:
    """When calysto_scheme can't be imported, the module falls back to scheme=None."""
    get_kernel()  # ensures the magics loader has imported "scheme_magic"
    sm = sys.modules["scheme_magic"]
    with patch.dict(sys.modules, {"calysto_scheme": None}):
        importlib.reload(sm)
    try:
        assert sm.scheme is None
    finally:
        importlib.reload(sm)


def test_register_ipython_magics_line() -> None:
    """The registered line `scheme` function evaluates code and returns retval."""
    captured: dict[str, Any] = {}
    with (
        patch(
            "IPython.core.magic.register_line_magic",
            lambda f: captured.update(line=f) or f,  # type:ignore[redundant-expr]
        ),
        patch(
            "IPython.core.magic.register_cell_magic",
            lambda f: captured.update(cell=f) or f,  # type:ignore[redundant-expr]
        ),
    ):
        register_ipython_magics()

    assert captured["line"]("(+ 1 2)") == 3


def test_register_ipython_magics_cell() -> None:
    """The registered cell `scheme` function evaluates the cell and returns retval."""
    captured: dict[str, Any] = {}
    with (
        patch(
            "IPython.core.magic.register_line_magic",
            lambda f: captured.update(line=f) or f,  # type:ignore[redundant-expr]
        ),
        patch(
            "IPython.core.magic.register_cell_magic",
            lambda f: captured.update(cell=f) or f,  # type:ignore[redundant-expr]
        ),
    ):
        register_ipython_magics()

    assert captured["cell"]("", "(+ 10 32)") == 42
