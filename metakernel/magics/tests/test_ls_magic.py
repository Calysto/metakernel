
import time
import os
from metakernel.tests.utils import (get_kernel, get_log_text,
                                    clear_log_text)


def test_ls_magic():
    kernel = get_kernel()
    kernel.do_execute("%ls /tmp")
    time.sleep(2)
    text = get_log_text(kernel)
    assert '/tmp/' in text, text[:100]
    clear_log_text(kernel)

    kernel.do_execute("%ls /tmp --recursive")
    time.sleep(2)
    text = get_log_text(kernel)
    assert '/tmp' in text, text[:100]
    clear_log_text(kernel)
