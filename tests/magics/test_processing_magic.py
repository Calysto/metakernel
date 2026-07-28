import asyncio
from typing import Any
from unittest.mock import patch

from metakernel.magics.processing_magic import ProcessingMagic, register_ipython_magics
from tests.utils import EvalKernel, get_kernel, get_log_text


def test_processing_magic() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute("""%%processing

setup() {
}

draw() {
}
""")
    )
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_cell_processing_strips_leading_u_prefix() -> None:
    """A repr() beginning with 'u' (Python 2 unicode literal style) is stripped."""

    class FakeCode:
        def __repr__(self) -> str:
            return "u'draw() {}'"

    kernel = get_kernel(EvalKernel)
    magic = kernel.cell_magics["processing"]
    magic.code = FakeCode()
    with patch.object(kernel, "Display") as mock_display:
        magic.cell_processing()
    html_obj = mock_display.call_args[0][0]
    assert "u'draw" not in html_obj.data
    assert "'draw() {}'" in html_obj.data


def test_register_ipython_magics() -> None:
    """The registered `processing` cell-magic sets code and renders the canvas."""
    captured: dict[str, Any] = {}
    with patch(
        "IPython.core.magic.register_cell_magic",
        lambda f: captured.update(processing=f) or f,  # type:ignore[redundant-expr]
    ):
        register_ipython_magics()

    with patch.object(ProcessingMagic, "cell_processing") as mock_cell_processing:
        captured["processing"]("", "draw() {}")
    mock_cell_processing.assert_called_once()
