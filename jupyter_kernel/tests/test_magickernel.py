from jupyter_kernel import MagicKernel
from IPython.kernel.zmq import session as ss
import zmq
import logging
from StringIO import StringIO


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
    kernel.reload_magics()
    for magic in ['cd', 'connect_info', 'download', 'html', 'install',
                  'javascript', 'latex', 'lsmagic', 'magic', 'plot',
                  'reload_magics', 'shell', 'time']:
        assert magic in kernel.line_magics

    for magic in ['file', 'html', 'javascript', 'latex', 'shell', 'time']:
        assert magic in kernel.cell_magics

    kernel.get_magic('%shell ls')
    log_text = get_log_text(kernel)
    assert 'test_magickernel.py' in log_text

    resp = kernel._get_help_on('%shell', 0)
    assert 'run the line as a shell command' in resp

    resp = kernel.do_execute('%cd?', False)
    assert 'change current directory of session' in resp[
        'payload'][0]['data']['text/plain']

    comp = kernel.do_complete('%connect_', len('%connect_'))
    assert comp['matches'] == ['connect_info']
