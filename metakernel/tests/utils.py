from metakernel import MetaKernel
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

    def get_usage(self):
        return ("This is the Eval kernel. It implements a simple Python " +
                "interpreter.")

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
        return python_magic.env.get(name, None)

    def do_execute_direct(self, code):
        python_magic = self.line_magics['python']
        return python_magic.eval(code.strip())

    def do_execute_file(self, filename):
        code = "".join(open(filename).readlines())
        return self.do_execute_direct(code)

    def do_function_direct(self, function_name, arg):
        """
        Call a function in the kernel language with args (as a single item).
        """
        python_magic = self.line_magics['python']
        return python_magic.eval("%s(%s)" % (function_name, arg))

    def get_completions(self, info):
        python_magic = self.line_magics['python']
        return python_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        python_magic = self.line_magics['python']
        return python_magic.get_help_on(info, level, none_on_fail)


def get_kernel(kernel_class=MetaKernel):
    log = logging.getLogger('test')
    log.setLevel(logging.DEBUG)

    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    hdlr = logging.StreamHandler(StringIO())
    hdlr.setLevel(logging.DEBUG)
    log.addHandler(hdlr)

    context = zmq.Context.instance()
    iopub_socket = context.socket(zmq.PUB)

    kernel = kernel_class(session=ss.Session(), iopub_socket=iopub_socket,
                          log=log)
    return kernel


def clear_log_text(kernel):
    kernel.log.handlers[0].stream.truncate(0)
    kernel.log.handlers[0].stream.seek(0)


def get_log_text(kernel):
    return kernel.log.handlers[0].stream.getvalue()

