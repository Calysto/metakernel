
import os
from metakernel.tests.utils import get_kernel, get_log_text, clear_log_text


def test_cd_magic():
    kernel = get_kernel()
    kernel.do_execute("%cd ~")
    assert os.getcwd() == os.path.expanduser('~'), os.getcwd()
    clear_log_text(kernel)
    kernel.do_execute('%cd')
    assert os.getcwd() in get_log_text(kernel)
