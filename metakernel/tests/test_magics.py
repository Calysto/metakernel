import os
from metakernel.tests.utils import get_kernel, get_log_text


def test_shell_magic():
    kernel = get_kernel()
    kernel.do_execute("!cat \"%s\"" % __file__, False)
    log_text = get_log_text(kernel)
    assert 'metakernel.py' in log_text

    kernel.do_execute('!!\necho "hello"\necho "goodbye"', None)
    log_text = get_log_text(kernel)
    assert '"hello"' in log_text
    assert '"goodbye"' in log_text

    resp = kernel.do_complete('! di', len('! di'))
    assert 'dir' in resp['matches']


def test_plot_magic():
    kernel = get_kernel()
    kernel.do_execute('%plot qt -f svg -s400,200', None)
    assert kernel.plot_settings['size'] == (400, 200)
    assert kernel.plot_settings['format'] == 'svg'
    assert kernel.plot_settings['backend'] == 'qt'


def test_python_magic():
    kernel = get_kernel()
    kernel.do_execute('%python retval = 1', None)
    assert '1' in get_log_text(kernel)

    kernel.do_execute('''%%python
        def test(a):
            return a + 1
        retval = test(2)''', None)
    assert '3' in get_log_text(kernel)


def test_magic_magic():
    kernel = get_kernel()
    kernel.do_execute('%magic', None)
    text = get_log_text(kernel)
    assert '! COMMAND ... - execute command in shell' in text


def test_help_magic():
    kernel = get_kernel()
    kernel.do_execute('?%magic', None)
    text = get_log_text(kernel)
    assert '%magic - show installed magics' in text, repr(text)


def test_file_magic():
    kernel = get_kernel()
    kernel.do_execute("""%%file TEST.txt
LINE1
LINE2
LINE3""", False)
    assert os.path.exists("TEST.txt")
    with open("TEST.txt") as fp:
        lines = fp.readlines()
        assert len(lines) == 3
        assert lines[0] == "LINE1\n"
        assert lines[1] == "LINE2\n"
        assert lines[2] == "LINE3"

    kernel.do_execute("""%%file -a TEST.txt

LINE4
LINE5
LINE6""", False)
    assert os.path.exists("TEST.txt")
    with open("TEST.txt") as fp:
        lines = fp.readlines()
        assert len(lines) == 6
        assert lines[3] == "LINE4\n"
        assert lines[4] == "LINE5\n"
        assert lines[5] == "LINE6"
