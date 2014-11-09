
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)

def test_edit_magic():
    kernel = get_kernel(EvalKernel)

    results = kernel.do_execute("%%edit %s" % __file__)
    text = results["payload"][0]["text"]
    assert text.startswith('%%file')
    assert 'def test_edit_magic' in text
