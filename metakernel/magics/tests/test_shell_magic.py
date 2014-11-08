
from metakernel.tests.utils import get_kernel


def test_python_magic():
    kernel = get_kernel()

    text = '%shell di'
    comp = kernel.do_complete(text, len(text))

    assert 'dir' in comp['matches']

    helpstr = kernel.get_help_on('!dir')
    assert not 'Sorry, no help' in helpstr

    helpstr = kernel.get_help_on('!dir', level=1)
    assert not 'Sorry, no help' in helpstr
