import sys
from jupyter_kernel import MagicKernel
from IPython.kernel.zmq import session as ss
import zmq


def get_kernel():
    context = zmq.Context.instance()
    iopub_socket = context.socket(zmq.PUB)
    kernel = MagicKernel(session=ss.Session(), iopub_socket=iopub_socket)
    return kernel


def test_magics():
    kernel = get_kernel()
    kernel.reload_magics()
    for magic in ['cd', 'connect_info', 'download', 'html', 'install', 'javascript',
                             'latex', 'lsmagic', 'magic', 'plot', 'reload_magics', 'shell',
                             'time']:
        assert magic in kernel.line_magics

    for magic in ['file', 'html', 'javascript', 'latex', 'shell', 'time']:
        assert magic in kernel.cell_magics

    kernel.get_magic('%shell ls')

    resp = kernel._get_help_on('%shell', 0)
    assert 'run the line as a shell command' in resp

    resp = kernel.do_execute('%cd?', False)
    assert 'change current directory of session' in resp['payload'][0]['data']['text/plain']

    comp = kernel.do_complete('%connect_', len('%connect_'))
    assert comp['matches'] == ['connect_info']
