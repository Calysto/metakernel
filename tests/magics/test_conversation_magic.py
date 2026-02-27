from unittest.mock import patch

from tests.utils import EvalKernel, get_kernel, get_log_text


def test_conversation_line_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%conversation mysite")
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
    kernel.do_execute("%%conversation mysite\n")
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
