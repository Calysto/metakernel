
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)
import os

def test_download_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%download --filename TEST.txt https://raw.githubusercontent.com/blink1073/metakernel/master/LICENSE.txt")
    text = get_log_text(kernel)
    assert "Downloaded 'TEST.txt'" in text, text
    assert os.path.isfile("TEST.txt"), "File does not exist: TEST.txt"

def teardown():
    try:
        os.remove("TEST.txt")
    except:
        pass
