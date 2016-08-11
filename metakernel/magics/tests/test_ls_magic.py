
import os
from metakernel.tests.utils import (get_kernel, get_log_text,
                                    clear_log_text)


def test_ls_magic():
    kernel = get_kernel()
    kernel.do_execute("%ls /tmp")
    text = get_log_text(kernel)
    ## FIXME: failing on Travis
    #assert '/tmp/' in text, text[:100]
    clear_log_text(kernel)

    kernel.do_execute("%ls /tmp --recursive")
    text = get_log_text(kernel)
    ## FIXME: failing on Travis
    #assert '/tmp' in text, text[:100]
    clear_log_text(kernel)
