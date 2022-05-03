"""A Echo kernel for Jupyter"""
from metakernel import MetaKernel
import sys

__version__ = "0.1.0"

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
    kernel_json = {
        'argv': [
            sys.executable, '-m', 'metakernel_echo', '-f', '{connection_file}'],
        'display_name': 'MetaKernel Echo',
        'language': 'echo',
        'name': 'metakernel_echo'
    }

    def get_usage(self):
        return "This is the echo kernel."

    def do_execute_direct(self, code):
        return code.rstrip()

    def repr(self, data):
        return repr(data)


if __name__ == '__main__':
    MetaKernelEcho.run_as_main()
