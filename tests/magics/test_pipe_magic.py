import asyncio
from typing import Any

import pytest

import metakernel.magics.pipe_magic as _pm
from metakernel.magics.pipe_magic import register_ipython_magics
from tests.utils import EvalKernel, clear_log_text, get_kernel, get_log_text


@pytest.fixture()
def ipython_pipe_magic(monkeypatch):
    """Yield the registered `pipe` cell-magic function with IPython stubbed out."""
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "IPython.core.magic.register_cell_magic",
        lambda f: captured.update(pipe=f) or f,  # type:ignore[redundant-expr]
    )

    register_ipython_magics()

    yield captured["pipe"]


def test_pipe_magic() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute("""

def upper(text):
    return text.upper()

def lower(text):
    return text.lower()

def pl_word(word):
    if len(word) > 3:
        return word[1:] + word[0] + "ay"
    else:
        return word

def piglatin(text):
    return " ".join([pl_word(word) for word in text.split(" ")])

""")
    )
    asyncio.run(
        kernel.do_execute("""%%pipe upper
this is a test
 """)
    )
    text = get_log_text(kernel)
    assert "THIS IS A TEST" in text, "text: " + text

    asyncio.run(
        kernel.do_execute("""%%pipe upper | piglatin
this is a test
 """)
    )
    text = get_log_text(kernel)
    assert "HISTay IS A ESTTay" in text, "text: " + text

    asyncio.run(
        kernel.do_execute("""%%pipe piglatin | upper
this is a test
 """)
    )
    text = get_log_text(kernel)
    assert "HISTAY IS A ESTTAY" in text, "text: " + text

    asyncio.run(
        kernel.do_execute("""%%pipe piglatin | upper | lower
this is a test
 """)
    )
    text = get_log_text(kernel)
    assert "histay is a esttay" in text, "text: " + text
    clear_log_text(kernel)


def test_register_ipython_magics_noop_without_ipython(
    ipython_pipe_magic, monkeypatch
) -> None:
    """The registered `pipe` function is a no-op when get_ipython() returns None."""
    monkeypatch.setattr(_pm, "get_ipython", lambda: None)
    assert ipython_pipe_magic("upper", "hello") is None


def test_register_ipython_magics_pipes_through_functions(
    ipython_pipe_magic, monkeypatch
) -> None:
    """The registered `pipe` function evaluates and pipes through user_global functions."""

    class FakeIPython:
        ns_table = {"user_global": {"upper": str.upper, "reverse": lambda s: s[::-1]}}

    monkeypatch.setattr(_pm, "get_ipython", lambda: FakeIPython())

    assert ipython_pipe_magic("upper | reverse", "hello") == "OLLEH"
