import asyncio
from typing import Any
from unittest.mock import patch

import pytest

from metakernel.magics.conversation_magic import register_ipython_magics
from tests.utils import EvalKernel, get_kernel, get_log_text


@pytest.fixture()
def ipython_conversation_magics(monkeypatch):
    """Yield (line_fn, cell_fn) for `conversation` with IPython stubbed out."""
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "IPython.core.magic.register_line_magic",
        lambda f: captured.update(line=f) or f,  # type:ignore[redundant-expr]
    )
    monkeypatch.setattr(
        "IPython.core.magic.register_cell_magic",
        lambda f: captured.update(cell=f) or f,  # type:ignore[redundant-expr]
    )

    register_ipython_magics()

    yield captured["line"], captured["cell"]


def test_conversation_line_magic() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%conversation mysite"))
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_conversation_line_magic_embeds_id() -> None:
    kernel = get_kernel(EvalKernel)
    magic = kernel.line_magics["conversation"]
    with patch.object(kernel, "Display") as mock_display:
        magic.line_conversation("mysite")
    html_obj = mock_display.call_args[0][0]
    assert "mysite.disqus.com" in html_obj.data


def test_conversation_line_magic_sets_evaluate_false() -> None:
    kernel = get_kernel(EvalKernel)
    magic = kernel.line_magics["conversation"]
    magic.line_conversation("mysite")
    assert not magic.evaluate


def test_conversation_cell_magic() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%%conversation mysite\n"))
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_conversation_cell_magic_embeds_id() -> None:
    kernel = get_kernel(EvalKernel)
    magic = kernel.cell_magics["conversation"]
    with patch.object(kernel, "Display") as mock_display:
        magic.cell_conversation("anothersite")
    html_obj = mock_display.call_args[0][0]
    assert "anothersite.disqus.com" in html_obj.data


def test_conversation_help() -> None:
    kernel = get_kernel()
    helpstr = kernel.get_help_on("%conversation")
    assert "conversation" in helpstr.lower(), helpstr


def test_register_ipython_magics_line(ipython_conversation_magics) -> None:
    """The registered line `conversation` function embeds the id and disables evaluate."""
    line_fn, _ = ipython_conversation_magics
    line_fn("mysite")


def test_register_ipython_magics_cell(ipython_conversation_magics) -> None:
    """The registered cell `conversation` function sets code and embeds the id."""
    _, cell_fn = ipython_conversation_magics
    cell_fn("mysite", "some cell text")
