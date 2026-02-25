from tests.utils import EvalKernel, get_kernel, get_log_text


def test_html_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%html

<b>bold</b>
""")
    text = get_log_text(kernel)
    assert "Display Data" in text, text
