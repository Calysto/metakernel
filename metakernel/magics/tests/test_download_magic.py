
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)
import os

def test_download_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%download --filename TEST.txt https://raw.githubusercontent.com/calysto/metakernel/master/LICENSE.txt")
    text = get_log_text(kernel)
    assert "Downloaded 'TEST.txt'" in text, text
    assert os.path.isfile("TEST.txt"), "File does not exist: TEST.txt"

    clear_log_text(kernel)

    kernel.do_execute("%download https://raw.githubusercontent.com/calysto/metakernel/master/LICENSE.txt")
    text = get_log_text(kernel)
    assert "Downloaded 'LICENSE.txt'" in text, text
    assert os.path.isfile("LICENSE.txt"), "File does not exist: LICENSE.txt"


def teardown():
    for fname in ['TEST.txt', 'LICENSE.txt']:
        try:
            os.remove(fname)
        except:
            pass
