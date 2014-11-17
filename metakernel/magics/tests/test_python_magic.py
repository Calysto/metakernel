
from metakernel.tests.utils import get_kernel, get_log_text, clear_log_text


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


def test_python_magic3():
    kernel = get_kernel()
    kernel.do_execute('%%python -e\n1 + 2', None)
    magic = kernel.get_magic('%%python')
    assert magic.retval is None

    kernel = get_kernel()
    kernel.do_execute('%%python\n1 + 2', None)
    magic = kernel.get_magic('%%python')
    assert magic.retval == 3


def test_python_magic4():
    kernel = get_kernel()
    kernel.do_execute('?%python', None)
    assert '%python CODE' in get_log_text(kernel)

    clear_log_text(kernel)

    ret = kernel.do_execute('?%python a', None)
    assert ret['payload'][0]['data']['text/plain'] == 'No help available for "a"'
    ret = kernel.do_execute('?%%python a.b', None)
    assert ret['payload'][0]['data']['text/plain'] == 'No help available for "a.b"'

    ret = kernel.do_execute('??%%python oct', None)
    assert ret['payload'][0]['data']['text/plain'].startswith('oct(number)')


def test_python_magic5():
    kernel = get_kernel()
    kernel.do_execute("%python print('hello')")

    assert 'hello' in get_log_text(kernel)

