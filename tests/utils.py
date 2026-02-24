from __future__ import annotations

from metakernel import MetaKernel
try:
    from jupyter_client import session as ss
except ImportError:
    from IPython.kernel.zmq import session as ss  # type: ignore[no-redef]
import zmq
import logging
from logging import Logger, StreamHandler

try:
    from StringIO import StringIO  # type: ignore[import]
except ImportError:
    from io import StringIO


class EvalKernel(MetaKernel):
    implementation = 'Eval'
    implementation_version = '1.0'
    language = 'python'
    language_version = '0.1'
    banner = "Eval kernel - evaluates simple Python statements and expressions"

    def set_variable(self, name, value) -> None:
        """
        Set a variable in the kernel language.
        """
        python_magic = self.line_magics['python']
        python_magic.env[name] = value

    def get_variable(self, name):
        """
        Get a variable from the kernel language.
        """
        python_magic = self.line_magics['python']
        return python_magic.env[name]

    def do_execute_direct(self, code):
        python_magic = self.line_magics['python']
        return python_magic.eval(code.strip())

    def do_execute_meta(self, code) -> str | None:
        if code == "reset":
            return "RESET"
        elif code == "stop":
            return "STOP"
        elif code == "step":
            return "STEP"
        elif code.startswith("inspect "):
            return "INSPECT"
        else:
            raise Exception("Unknown meta command: '%s'" % code)

    def initialize_debug(self, code) -> str:
        return "highlight: [%s, %s, %s, %s]" % (0, 0, 1, 0)


def has_network() -> bool:
    import requests  # type: ignore[import-untyped]
    try:
        _ = requests.head('http://google.com', timeout=3)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False


from metakernel._metakernel import MetaKernel
def get_log() -> Logger:
    log = logging.getLogger('test')
    log.setLevel(logging.DEBUG)

    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    hdlr = StreamHandler(StringIO())
    hdlr.setLevel(logging.DEBUG)
    log.addHandler(hdlr)

    return log


def get_kernel(kernel_class=MetaKernel) -> MetaKernel:
    context = zmq.Context.instance()
    iopub_socket = context.socket(zmq.PUB)

    kernel = kernel_class(session=ss.Session(), iopub_socket=iopub_socket,
                          log=get_log())
    return kernel


def clear_log_text(obj) -> None:
    """Clear the log text from a kernel or a log object."""
    if isinstance(obj, MetaKernel):
        log = obj.log
    else:
        log = obj
    handler = log.handlers[0]
    assert isinstance(handler, StreamHandler)
    handler.stream.truncate(0)
    handler.stream.seek(0)


def get_log_text(obj):
    """Get the log text from a kernel or a log object."""
    if isinstance(obj, MetaKernel):
        log = obj.log
    else:
        log = obj
    handler = log.handlers[0]
    assert isinstance(handler, StreamHandler)
    return handler.stream.getvalue()
