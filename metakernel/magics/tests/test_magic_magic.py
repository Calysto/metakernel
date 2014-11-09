
from metakernel.tests.utils import get_kernel, get_log_text


def test_magic_magic():
    kernel = get_kernel()
    kernel.do_execute('%magic', None)
    text = get_log_text(kernel)
    assert '! COMMAND ... - execute command in shell' in text
