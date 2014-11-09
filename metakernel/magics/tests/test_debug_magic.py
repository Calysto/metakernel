
import os
from metakernel.tests.utils import get_kernel, EvalKernel


def test_debug_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%debug
print('ok')
""")

    
