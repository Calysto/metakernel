from jupyter_kernel import MagicKernel
from IPython.kernel.zmq import session as ss
import zmq
import logging
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os


def get_kernel():
    log = logging.getLogger('test')
    log.setLevel(logging.DEBUG)

    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    hdlr = logging.StreamHandler(StringIO())
    hdlr.setLevel(logging.DEBUG)
    log.addHandler(hdlr)

    context = zmq.Context.instance()
    iopub_socket = context.socket(zmq.PUB)

    kernel = MagicKernel(session=ss.Session(), iopub_socket=iopub_socket,
                         log=log)
    return kernel


def get_log_text(kernel):
    return kernel.log.handlers[0].stream.getvalue()


def test_magics():
    kernel = get_kernel()
    for magic in ['cd', 'connect_info', 'download', 'html', 'install_magic',
                  'javascript', 'latex', 'lsmagic', 'magic', 'plot',
                  'reload_magics', 'shell']:
        msg = "magic '%s' is not in line_magics" % magic
        assert magic in kernel.line_magics, msg

    for magic in ['file', 'html', 'javascript', 'latex', 'shell', 'time']:
        assert magic in kernel.cell_magics

    with open('TEST.txt', 'wb'):
        pass
    kernel.get_magic('%shell ls')
    log_text = get_log_text(kernel)
    assert 'TEST.txt' in log_text
    os.remove('TEST.txt')


def test_help():
    kernel = get_kernel()
    resp = kernel.get_help_on('%shell', 0)
    assert 'run the line as a shell command' in resp

    resp = kernel.do_execute('%cd?', False)
    assert 'change current directory of session' in resp[
        'payload'][0]['data']['text/plain']


def test_complete():
    kernel = get_kernel()
    comp = kernel.do_complete('%connect_', len('%connect_'))
    assert comp['matches'] == ['%connect_info'], str(comp['matches'])

    comp = kernel.do_complete('%%fil', len('%%fil'))
    assert comp['matches'] == ['%%file'], str(comp['matches'])


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


def test_shell_magic():
    kernel = get_kernel()
    kernel.do_execute("!cat \"%s\"" % __file__, False)
    log_text = get_log_text(kernel)
    assert 'magickernel.py' in log_text


def test_inspect():
    kernel = get_kernel()
    kernel.do_inspect('%lsmagic', len('%lsmagic'))
    log_text = get_log_text(kernel)
    assert "list the current line and cell magics" in log_text


def test_path_complete():
    kernel = get_kernel()
    comp = kernel.do_complete('~/.ipytho', len('~/.ipytho'))
    assert comp['matches'] == ['~' + os.sep + '.ipython' + os.sep]

    files = [f for f in os.listdir(os.getcwd()) if not os.path.isdir(f)]
    comp = kernel.do_complete(files[0], len(files[0]) - 1)
    assert files[0] in comp['matches']


def test_history():
    kernel = get_kernel()
    kernel.do_execute('!ls', False)
    kernel.do_execute('%cd ~', False)
    kernel.do_shutdown(False)

    with open(kernel.hist_file, 'rb') as fid:
        text = fid.read().decode('utf-8', 'replace')

    assert '!ls' in text
    assert '%cd' in text

    kernel = get_kernel()
    kernel.do_history(None, None, None)
    print(kernel.hist_cache)
    assert '!ls' in ''.join(kernel.hist_cache)
    assert '%cd ~'


def test_plot_magic():
    kernel = get_kernel()
    kernel.do_execute('%plot qt -f svg -s400,200', None)
    assert kernel.plot_settings['size'] == '400,200'
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


def teardown():
    if os.path.exists("TEST.txt"):
        os.remove("TEST.txt")
