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
    for magic in ['cd', 'connect_info', 'download', 'html', 'install',
                  'javascript', 'latex', 'lsmagic', 'magic', 'plot',
                  'reload_magics', 'shell', 'time']:
        assert magic in kernel.line_magics

    for magic in ['file', 'html', 'javascript', 'latex', 'shell', 'time']:
        assert magic in kernel.cell_magics

    kernel.get_magic('%shell ls')
    log_text = get_log_text(kernel)
    assert 'magickernel.py' in log_text

    resp = kernel.get_help_on('%shell', 0)
    assert 'run the line as a shell command' in resp

    resp = kernel.do_execute('%cd?', False)
    assert 'change current directory of session' in resp[
        'payload'][0]['data']['text/plain']

    comp = kernel.do_complete('%connect_', len('%connect_'))
    assert comp['matches'] == ['connect_info']


def test_file_magic():
    kernel = get_kernel()
    resp = kernel.do_execute("""%%file TEST.txt
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

    resp = kernel.do_execute("""%%file -a TEST.txt

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


def teardown():
    if os.path.exists("TEST.txt"):
        os.remove("TEST.txt")

