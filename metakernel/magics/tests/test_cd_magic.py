
import os
from metakernel.tests.utils import get_kernel


def test_cd_magic():
    kernel = get_kernel()
    kernel.do_execute("%cd ~")
    assert os.getcwd() == os.path.expanduser('~'), os.getcwd()
