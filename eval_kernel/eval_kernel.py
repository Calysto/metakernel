from __future__ import print_function

from jupyter_kernel import MagicKernel


class EvalKernel(MagicKernel):
    implementation = 'Eval'
    implementation_version = '1.0'
    language = 'python'
    language_version = '0.1'
    banner = "Eval kernel - evaluates simple Python statements and expressions"
    env = {}

    def get_usage(self):
        return "This is a usage statement."

    def set_variable(self, name, value):
        """
        Set a variable in the kernel language.
        """
        self.env[name] = value

    def get_variable(self, name):
        """
        Get a variable from the kernel language.
        """
        return self.env.get(name, None)

    def do_execute_direct(self, code):
        python_magic = self.line_magics['python']
        return python_magic.eval(code.strip())

    def get_completions(self, info):
        python_magic = self.line_magics['python']
        return python_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0):
        python_magic = self.line_magics['python']
        return python_magic.get_help_on(info, level)

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=EvalKernel)
