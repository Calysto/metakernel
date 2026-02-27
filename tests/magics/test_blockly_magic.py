import os

import pytest

from tests.utils import EvalKernel, get_kernel, get_log_text, has_network


def test_blockly_default() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%blockly")
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_blockly_custom_height() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%blockly --height 600")
    text = get_log_text(kernel)
    assert "Display Data" in text, text


def test_blockly_page_from_local(tmp_path) -> None:
    html_file = tmp_path / "blockly_page.html"
    html_file.write_text("<html><body>Blockly</body></html>")
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(f"%blockly --page_from_local {html_file}")
    text = get_log_text(kernel)
    assert "Display Data" in text, text


@pytest.mark.skipif(not has_network(), reason="no network")
def test_blockly_page_from_origin() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(
        "%blockly --page_from_origin https://developers-dot-devsite-v2-prod.appspot.com/blockly/blockly-demo/blockly-demo"
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
    kernel.do_execute(
        f"%blockly --page_from_local {template_html} --template_data {tdata}"
    )
    text = get_log_text(kernel)
    assert "Display Data" in text, text
    assert os.path.isfile(tdata + ".html")


def test_blockly_help() -> None:
    kernel = get_kernel()
    helpstr = kernel.get_help_on("%blockly")
    assert "blockly" in helpstr.lower(), helpstr
