import importlib.util

import pytest

from tests.utils import get_kernel

has_calysto = importlib.util.find_spec("calysto_scheme") is not None

pytestmark = pytest.mark.skipif(
    not has_calysto, reason="calysto_scheme is not installed"
)


def test_scheme_line_magic_expression() -> None:
    kernel = get_kernel()
    kernel.do_execute("%scheme (+ 1 2)", None)
    magic = kernel.line_magics["scheme"]
    assert magic.retval == 3


def test_scheme_line_magic_define() -> None:
    kernel = get_kernel()
    kernel.do_execute("%scheme (define x 42)", None)
    magic = kernel.line_magics["scheme"]
    # define statements return a void Symbol in calysto_scheme, not None
    from calysto_scheme import scheme as cs

    assert magic.retval == cs.void_value


def test_scheme_cell_magic() -> None:
    kernel = get_kernel()
    kernel.do_execute("%%scheme\n(+ 10 32)", None)
    magic = kernel.cell_magics["scheme"]
    assert magic.retval == 42
    assert not magic.evaluate


def test_scheme_cell_magic_multiline() -> None:
    kernel = get_kernel()
    kernel.do_execute("%%scheme\n(define x 10)\n(+ x 5)", None)
    magic = kernel.cell_magics["scheme"]
    assert magic.retval == 15


def test_scheme_cell_magic_eval_output() -> None:
    kernel = get_kernel()
    # -e flag: Scheme result is used as code for the host kernel
    kernel.do_execute('%%scheme -e\n"1 + 2"', None)
    magic = kernel.cell_magics["scheme"]
    assert magic.evaluate


def test_scheme_cell_magic_empty() -> None:
    kernel = get_kernel()
    kernel.do_execute("%%scheme\n  ", None)
    magic = kernel.cell_magics["scheme"]
    # Whitespace-only cell: nothing is evaluated, retval stays None
    assert magic.retval is None


def test_scheme_help() -> None:
    kernel = get_kernel()
    helpstr = kernel.get_help_on("%scheme")
    assert "Scheme" in helpstr or "scheme" in helpstr, helpstr


def test_scheme_no_calysto(monkeypatch) -> None:
    import sys

    kernel = get_kernel()
    magic = kernel.line_magics["scheme"]
    # The magic loader registers the module as "scheme_magic" in sys.modules
    sm = sys.modules["scheme_magic"]
    monkeypatch.setattr(sm, "scheme", None)
    with pytest.raises(Exception, match="calysto_scheme is required"):
        magic.eval("(+ 1 2)")
