from tests.utils import EvalKernel, get_kernel, get_log_text


def test_javascript_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%javascript

console.log("Hello from Javascript");
""")
    text = get_log_text(kernel)
    assert "Display Data" in text, text
