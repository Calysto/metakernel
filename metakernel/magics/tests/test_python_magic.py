
from metakernel.tests.utils import get_kernel


def test_python_magic():
    kernel = get_kernel()

    text = '%python imp'
    comp = kernel.do_complete(text, len(text))

    assert 'import' in comp['matches']

    helpstr = kernel.get_help_on('%python bin')
    assert 'bin(number)' in helpstr
