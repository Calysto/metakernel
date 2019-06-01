from metakernel import MetaKernel
try:
    from jupyter_client import session as ss
except ImportError:
    from IPython.kernel.zmq import session as ss
import zmq
import logging

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class EvalKernel(MetaKernel):
    implementation = 'Eval'
    implementation_version = '1.0'
    language = 'python'
    language_version = '0.1'
    banner = "Eval kernel - evaluates simple Python statements and expressions"

    def set_variable(self, name, value):
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

    def do_execute_meta(self, code):
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

    def initialize_debug(self, code):
        return "highlight: [%s, %s, %s, %s]" % (0, 0, 1, 0)


def has_network():
    import requests
    try:
        _ = requests.head('http://google.com', timeout=3)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False


def get_log():
    log = logging.getLogger('test')
    log.setLevel(logging.DEBUG)

    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    hdlr = logging.StreamHandler(StringIO())
    hdlr.setLevel(logging.DEBUG)
    log.addHandler(hdlr)

    return log


def get_kernel(kernel_class=MetaKernel):
    context = zmq.Context.instance()
    iopub_socket = context.socket(zmq.PUB)

    kernel = kernel_class(session=ss.Session(), iopub_socket=iopub_socket,
                          log=get_log())
    return kernel


def clear_log_text(obj):
    """Clear the log text from a kernel or a log object."""
    if isinstance(obj, MetaKernel):
        log = obj.log
    else:
        log = obj
    log.handlers[0].stream.truncate(0)
    log.handlers[0].stream.seek(0)


def get_log_text(obj):
    """Get the log text from a kernel or a log object."""
    if isinstance(obj, MetaKernel):
        log = obj.log
    else:
        log = obj
    return log.handlers[0].stream.getvalue()

