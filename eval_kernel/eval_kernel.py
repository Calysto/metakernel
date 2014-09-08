from __future__ import print_function

from jupyter_kernel import MagicKernel


class EvalKernel(MagicKernel):
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
        return python_magic.eval(code.strip(), self.env)

    def get_completions(self, info):
        python_magic = self.line_magics['python']
        return python_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        python_magic = self.line_magics['python']
        return python_magic.get_help_on(info, level, none_on_fail)

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=EvalKernel)
