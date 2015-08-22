from __future__ import print_function

from metakernel import MetaKernel


class MetaKernelEcho(MetaKernel):
    implementation = 'MetaKernel Echo'
    implementation_version = '1.0'
    language = 'text'
    language_version = '0.1'
    banner = "MetaKernel Echo - as useful as a parrot"
    language_info = {
        'mimetype': 'text/plain',
        'name': 'text',
        # ------ If different from 'language':
        # 'codemirror_mode': {
        #    "version": 2,
        #    "name": "ipython"
        # }
        # 'pygments_lexer': 'language',
        # 'version'       : "x.y.z",
        'file_extension': '.txt',
        'help_links': MetaKernel.help_links,
    }

    def get_usage(self):
        return "This is the echo kernel."

    def do_execute_direct(self, code):
        return code.rstrip()

    def repr(self, data):
        return repr(data)

if __name__ == '__main__':
    try:
        from ipykernel.kernelapp import IPKernelApp
    except ImportError:
        from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MetaKernelEcho)
