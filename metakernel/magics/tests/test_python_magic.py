
from metakernel.tests.utils import get_kernel, get_log_text


def test_python_magic():
    kernel = get_kernel()

    text = '%python imp'
    comp = kernel.do_complete(text, len(text))

    assert 'import' in comp['matches']

    helpstr = kernel.get_help_on('%python bin')
    assert 'bin(number)' in helpstr


def test_python_magic2():
    kernel = get_kernel()
    kernel.do_execute('%python retval = 1', None)
    assert '1' in get_log_text(kernel)

    kernel.do_execute('''%%python
        def test(a):
            return a + 1
        retval = test(2)''', None)
    assert '3' in get_log_text(kernel)
