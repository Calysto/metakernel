
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)

def test_dot_magic_cell():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%dot

graph A { a->b };
""")

    text = get_log_text(kernel)
    assert "Display Data" in text, text

def test_dot_magic_line():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%dot graph A { a->b };")

    text = get_log_text(kernel)
    assert "Display Data" in text, text
