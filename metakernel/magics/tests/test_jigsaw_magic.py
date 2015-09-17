
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)
import os

def test_jigsaw_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%jigsaw Processing")
    text = get_log_text(kernel)
    assert os.path.isfile("Processing.html"), "File does not exist: Processing.html"

def teardown():
    for fname in ['Processing.html']:
        try:
            os.remove(fname)
        except:
            pass
