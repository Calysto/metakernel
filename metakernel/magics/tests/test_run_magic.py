
from metakernel.tests.utils import (get_kernel, EvalKernel, 
                                    get_log_text, clear_log_text)

def test_run_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%%run %s" % __file__.replace(".pyc", ".py"))
    kernel.do_execute("TEST")
    text = get_log_text(kernel)
    assert '42' in text, "Didn't run this file"

    clear_log_text(kernel)
    kernel.do_execute("%%run --language python %s" % __file__.replace(".pyc", ".py"))
    kernel.do_execute("TEST")
    text = get_log_text(kernel)
    assert '42' in text, "Didn't run this file"

TEST = 42
