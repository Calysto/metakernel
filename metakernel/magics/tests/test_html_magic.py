
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)

def test_html_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%html

<b>bold</b>
""")
    text = get_log_text(kernel)
    assert "Display Data" in text, text

