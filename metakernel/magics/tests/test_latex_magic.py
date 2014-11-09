
from metakernel.tests.utils import (get_kernel, get_log_text,
                                    clear_log_text)


def test_latex_magic():
    kernel = get_kernel()
    kernel.do_execute("%latex x_1 = \dfrace{a}{b}")
    text = get_log_text(kernel)
    assert "Display Data" in text

    clear_log_text(kernel)

    kernel.do_execute("""%%latex
            x_1 = \dfrac{a}{b}

            x_2 = a^{n - 1}""")
    text = get_log_text(kernel)
    assert "Display Data" in text
