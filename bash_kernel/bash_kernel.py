from __future__ import print_function

from metakernel import MetaMagicKernel, MetaKernelAdapter

class BashKernel(MetaMagicKernel):
    def get_usage(self):
        return "This is the bash kernel."

    def do_execute_direct(self, code):
        if not code.strip():
            return
        self.log.debug('execute: %s' % code)
        shell_magic = self.line_magics['shell']
        resp, error = shell_magic.eval(code.strip())
        if error:
            self.Error(error)
        self.log.debug('execute done')
        return resp.strip()

    def get_completions(self, info):
        shell_magic = self.line_magics['shell']
        return shell_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        code = info['code'].strip()
        if not code or len(code.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        shell_magic = self.line_magics['shell']
        return shell_magic.get_help_on(info, level, none_on_fail)

    def repr(self, data):
        return data

class BashKernelAdapter(MetaKernelAdapter):
    implementation = 'Bash'
    implementation_version = '1.0'
    language = 'bash'
    language_version = '0.1'
    banner = "Bash kernel - interact with a bash prompt"
    meta_class = BashKernel

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=BashKernelAdapter)
