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
        'language': 'text',
        # ------ If different from 'language':
        # 'codemirror_mode': 'language',
        # 'pygments_lexer': 'language',
        'file_extension': '.txt',
    }

    def get_usage(self):
        return "This is the echo kernel."

    def do_execute_direct(self, code):
        return code.rstrip()

    def repr(self, data):
        return repr(data)

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MetaKernelEcho)
