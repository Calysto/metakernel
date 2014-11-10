
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text)

def test_dot_magic():
    kernel = get_kernel()
    kernel.do_execute("""%%dot

graph A { a->b };
""")
    text = get_log_text(kernel)
    assert "Display Data" in text, text
    clear_log_text(kernel)

    kernel.do_execute("%dot graph A { a->b };")
    text = get_log_text(kernel)
    assert "Display Data" in text, text
    clear_log_text(kernel)
