
import os
import sys
from metakernel.tests.utils import (get_kernel, get_log_text,
                                    clear_log_text, EvalKernel)
PY3 = (sys.version_info[0] >= 3)

def test_set_get_int_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%set x 42")
    kernel.do_execute("%get x")
    text = get_log_text(kernel)
    assert "42" in text, text

def test_set_get_list_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%set variable [1., 2., 3., 4.]")
    kernel.do_execute("%get variable")
    text = get_log_text(kernel)
    assert "[1.0, 2.0, 3.0, 4.0]" in text, text

def test_set_get_range_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%set variable range(2)")
    kernel.do_execute("%get variable")
    text = get_log_text(kernel)
    if PY3:
        assert "range(0, 2)" in text, text
    else:
        assert "[0, 1]" in text, text
