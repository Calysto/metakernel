
from metakernel.tests.utils import get_kernel, get_log_text


def test_shell_magic():
    kernel = get_kernel()

    text = '%shell di'
    comp = kernel.do_complete(text, len(text))

    assert 'dir' in comp['matches']

    helpstr = kernel.get_help_on('!dir')
    assert not 'Sorry, no help' in helpstr

    helpstr = kernel.get_help_on('%%shell dir', level=1)
    assert not 'Sorry, no help' in helpstr

    helpstr = kernel.get_help_on('!lkjalskdfj')
    assert 'Sorry, no help' in helpstr


def test_shell_magic2():
    kernel = get_kernel()
    kernel.do_execute("!cat \"%s\"" % __file__, False)
    log_text = get_log_text(kernel)
    assert 'metakernel.py' in log_text

    kernel.do_execute('!!\necho "hello"\necho "goodbye"', None)
    log_text = get_log_text(kernel)
    assert '"hello"' in log_text
    assert '"goodbye"' in log_text


def test_shell_magic3():
    kernel = get_kernel()
    kernel.do_execute('!lalkjds')
    text = get_log_text(kernel)
    assert ': command not found' in text, text
