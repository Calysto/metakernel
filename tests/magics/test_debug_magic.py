
import os
from tests.utils import get_kernel, EvalKernel


def test_debug_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%debug
print('ok')
""")

    
