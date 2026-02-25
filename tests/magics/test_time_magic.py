import re

from tests.utils import EvalKernel, get_kernel, get_log_text


def test_time_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%time
x = 1
""")
    text = get_log_text(kernel)

    assert (
        re.match(".*Time: .* seconds.", text, re.MULTILINE | re.DOTALL) is not None
    ), text
