import asyncio
import importlib.util
import shutil
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from metakernel.magics.dot_magic import register_ipython_magics
from tests.utils import EvalKernel, get_kernel, get_log_text

NO_PYDOT = importlib.util.find_spec("pydot") is None
NO_DOT = shutil.which("dot") is None or NO_PYDOT


@pytest.mark.skipif(NO_DOT, reason="Requires dot from graphviz")
def test_dot_magic_cell() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute("""%%dot

graph A { a->b };
""")
    )

    text = get_log_text(kernel)
    assert "Display Data" in text, text


@pytest.mark.skipif(NO_DOT, reason="Requires dot from graphviz")
def test_dot_magic_line() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%dot graph A { a->b };"))

    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_line_dot_raises_without_pydot(monkeypatch) -> None:
    """%dot raises a friendly error when pydot is not installed."""
    kernel = get_kernel()
    magic = kernel.line_magics["dot"]
    monkeypatch.setitem(sys.modules, "pydot", None)
    with pytest.raises(Exception, match="You need to install pydot"):
        magic.line_dot("graph A { a->b };")


def test_cell_dot_raises_without_pydot(monkeypatch) -> None:
    """%%dot raises a friendly error when pydot is not installed."""
    kernel = get_kernel()
    magic = kernel.cell_magics["dot"]
    magic.code = "graph A { a->b };"
    monkeypatch.setitem(sys.modules, "pydot", None)
    with pytest.raises(Exception, match="You need to install pydot"):
        magic.cell_dot()


@pytest.mark.skipif(NO_PYDOT, reason="Requires pydot")
def test_line_dot_noop_for_empty_graph() -> None:
    """%dot does nothing when pydot fails to parse any graph."""
    kernel = get_kernel()
    magic = kernel.line_magics["dot"]
    with patch("pydot.graph_from_dot_data", return_value=[]) as mock_parse:
        with patch.object(kernel, "Display") as mock_display:
            magic.line_dot("not valid dot")
    mock_parse.assert_called_once()
    mock_display.assert_not_called()


@pytest.mark.skipif(NO_PYDOT, reason="Requires pydot")
def test_cell_dot_noop_for_empty_graph() -> None:
    """%%dot does nothing when pydot fails to parse any graph."""
    kernel = get_kernel()
    magic = kernel.cell_magics["dot"]
    magic.code = "not valid dot"
    with patch("pydot.graph_from_dot_data", return_value=[]):
        with patch.object(kernel, "Display") as mock_display:
            magic.cell_dot()
    mock_display.assert_not_called()


@pytest.mark.skipif(NO_PYDOT, reason="Requires pydot")
def test_line_dot_handles_str_svg() -> None:
    """%dot handles a create_svg() result that is already str (no .decode)."""
    kernel = get_kernel()
    magic = kernel.line_magics["dot"]
    fake_graph = MagicMock()
    fake_graph.create_svg.return_value = "<svg>already str</svg>"
    with patch("pydot.graph_from_dot_data", return_value=[fake_graph]):
        with patch.object(kernel, "Display") as mock_display:
            magic.line_dot("graph A { a->b };")
    html_obj = mock_display.call_args[0][0]
    assert "already str" in html_obj.data


@pytest.mark.skipif(NO_PYDOT, reason="Requires pydot")
def test_cell_dot_handles_str_svg() -> None:
    """%%dot handles a create_svg() result that is already str (no .decode)."""
    kernel = get_kernel()
    magic = kernel.cell_magics["dot"]
    magic.code = "graph A { a->b };"
    fake_graph = MagicMock()
    fake_graph.create_svg.return_value = "<svg>already str</svg>"
    with patch("pydot.graph_from_dot_data", return_value=[fake_graph]):
        with patch.object(kernel, "Display") as mock_display:
            magic.cell_dot()
    html_obj = mock_display.call_args[0][0]
    assert "already str" in html_obj.data
    assert not magic.evaluate


@pytest.mark.skipif(NO_PYDOT, reason="Requires pydot")
def test_register_ipython_magics() -> None:
    """The registered `dot` cell-magic transforms the cell into a dot render call."""
    captured: dict[str, Any] = {}
    with patch(
        "IPython.core.magic.register_cell_magic",
        lambda f: captured.update(dot=f) or f,  # type:ignore[redundant-expr]
    ):
        register_ipython_magics()

    fake_graph = MagicMock()
    fake_graph.create_svg.return_value = "<svg>ipython</svg>"
    with patch("pydot.graph_from_dot_data", return_value=[fake_graph]):
        with patch("IPython.display.display") as mock_display:
            captured["dot"]("", "graph A { a->b };")
    assert mock_display.called
