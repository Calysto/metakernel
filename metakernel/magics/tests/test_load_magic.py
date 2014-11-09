
from metakernel.tests.utils import get_kernel


def test_load_magic():
    kernel = get_kernel()
    ret = kernel.do_execute("%%load %s" % __file__)
    assert 'def test_load_magic' in ret['payload'][0]['text']
