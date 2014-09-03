from __future__ import print_function

from jupyter_kernel import MagicKernel


class BashKernel(MagicKernel):
    implementation = 'Bash'
    implementation_version = '1.0'
    language = 'bash'
    language_version = '0.1'
    banner = "Bash kernel - interact with a bash prompt"

    def get_usage(self):
        return "This is the bash kernel."

    def do_execute_direct(self, code):
        shell_magic = self.line_magics['shell']
        resp, error = shell_magic.eval(code.strip())
        if error:
            self.Error(error)
        if resp:
            self.Print(resp)

    def add_complete(self, matches, token):
        shell_magic = self.line_magics['shell']
        matches.extend(shell_magic.get_completions(token))

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=BashKernel)
