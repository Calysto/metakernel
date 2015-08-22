from __future__ import print_function

from metakernel import MetaKernel


class MetaKernelBash(MetaKernel):
    implementation = 'MetaKernel Bash'
    implementation_version = '1.0'
    language = 'bash'
    language_version = '0.1'
    banner = "MetaKernel Bash - interact with bash"
    language_info = {
        'mimetype': 'text/x-bash',
        'name': 'bash',
        # ------ If different from 'language':
        # 'codemirror_mode': {
        #    "version": 2,
        #    "name": "ipython"
        # }
        # 'pygments_lexer': 'language',
        # 'version'       : "x.y.z",
        'file_extension': '.sh',
        'help_links': MetaKernel.help_links,
    }

    def get_usage(self):
        return "This is the bash kernel."

    def do_execute_direct(self, code):
        if not code.strip():
            return
        self.log.debug('execute: %s' % code)
        shell_magic = self.line_magics['shell']
        resp = shell_magic.eval(code.strip())
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

if __name__ == '__main__':
    try:
        from ipykernel.kernelapp import IPKernelApp
    except ImportError:
        from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MetaKernelBash)
