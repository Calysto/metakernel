import asyncio
import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from metakernel.magics.blockly_magic import register_ipython_magics
from tests.utils import EvalKernel, get_kernel, get_log_text, has_network


def test_blockly_default() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%blockly"))
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_blockly_custom_height() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%blockly --height 600"))
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_blockly_page_from_local(tmp_path) -> None:
    html_file = tmp_path / "blockly_page.html"
    html_file.write_text("<html><body>Blockly</body></html>")
    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute(f"%blockly --page_from_local {html_file}"))
    text = get_log_text(kernel)
    assert "Display Data" in text, text


@pytest.mark.skipif(not has_network(), reason="no network")
def test_blockly_page_from_origin() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute(
            "%blockly --page_from_origin https://developers-dot-devsite-v2-prod.appspot.com/blockly/blockly-demo/blockly-demo"
        )
    )
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_blockly_template_data_no_source() -> None:
    kernel = get_kernel(EvalKernel)
    magic = kernel.line_magics["blockly"]
    with pytest.raises(ValueError, match="No -l or -o is provided"):
        magic.line_blockly(template_data="some_data")


def test_blockly_template_data_from_local(tmp_path) -> None:
    template_html = tmp_path / "template.html"
    template_html.write_text(
        "<html>MY_BLOCKLY_TOOLBOX MY_BLOCKLY_WORKSPACE MY_BLOCKLY_BLOCKS_JS</html>"
    )
    tdata = str(tmp_path / "tdata")
    (tmp_path / "tdata-toolbox.xml").write_text("<xml>toolbox</xml>")
    (tmp_path / "tdata-workspace.xml").write_text("<xml>workspace</xml>")
    (tmp_path / "tdata-blocks.js").write_text("var blocks = {};")
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute(
            f"%blockly --page_from_local {template_html} --template_data {tdata}"
        )
    )
    text = get_log_text(kernel)
    assert "Display Data" in text, text
    assert os.path.isfile(tdata + ".html")


def test_blockly_help() -> None:
    kernel = get_kernel()
    helpstr = kernel.get_help_on("%blockly")
    assert "blockly" in helpstr.lower(), helpstr


def test_blockly_none_height_defaults_to_350() -> None:
    """Passing height=None falls back to the default of 350."""
    kernel = get_kernel(EvalKernel)
    magic = kernel.line_magics["blockly"]
    with patch.object(kernel, "Display") as mock_display:
        magic.line_blockly(height=None)
    iframe = mock_display.call_args_list[-1][0][0]
    assert iframe.height == 350


def test_blockly_template_data_from_origin(tmp_path) -> None:
    """template_data combined with page_from_origin downloads the template via urllib."""
    tdata = str(tmp_path / "tdata")
    (tmp_path / "tdata-toolbox.xml").write_text("<xml>toolbox</xml>")
    (tmp_path / "tdata-workspace.xml").write_text("<xml>workspace</xml>")
    (tmp_path / "tdata-blocks.js").write_text("var blocks = {};")

    kernel = get_kernel(EvalKernel)
    magic = kernel.line_magics["blockly"]

    fake_response = MagicMock()
    fake_response.read.return_value = (
        b"<html>MY_BLOCKLY_TOOLBOX MY_BLOCKLY_WORKSPACE MY_BLOCKLY_BLOCKS_JS</html>"
    )
    with patch("urllib.request.urlopen", return_value=fake_response) as mock_urlopen:
        magic.line_blockly(
            page_from_origin="http://example.com/template.html",
            template_data=tdata,
        )
    mock_urlopen.assert_called_once_with("http://example.com/template.html")
    assert os.path.isfile(tdata + ".html")


def test_register_ipython_magics() -> None:
    """The registered `blockly` line-magic forwards to kernel.call_magic."""
    captured: dict[str, Any] = {}
    with patch(
        "IPython.core.magic.register_line_magic",
        lambda f: captured.update(blockly=f) or f,  # type:ignore[redundant-expr]
    ):
        register_ipython_magics()

    with patch("metakernel.IPythonKernel.call_magic") as mock_call_magic:
        captured["blockly"]("--height 600")
    mock_call_magic.assert_called_once_with("%blockly --height 600")
