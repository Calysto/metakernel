
from metakernel.tests.utils import get_kernel, get_log_text, EvalKernel
import os
import time

def test_kernel_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%kx 42", False)
    results = get_log_text(kernel)
    assert "42" in results, results
    
