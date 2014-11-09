
from metakernel.tests.utils import get_kernel, get_log_text, EvalKernel
import re

def test_time_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%time
x = 1
""")
    text = get_log_text(kernel)

    assert re.match(".*Time: .* seconds.", text, re.MULTILINE | re.DOTALL) != None, text
  

