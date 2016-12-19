
from metakernel.tests.utils import get_kernel


def test_config_magic():
    kernel = get_kernel()
    kernel.do_execute("%%config -t 10")
    kernel.do_execute("%%config --timeout -1")
