from __future__ import print_function

from metakernel import MetaKernel
import sys

class MetaKernelPython(MetaKernel):
    implementation = 'MetaKernel Python'
    implementation_version = '1.0'
    language = 'python'
    language_version = '0.1'
    banner = "MetaKernel Python - evaluates Python statements and expressions"
    language_info = {
        'mimetype': 'text/x-python',
        'name': 'python',
        # ------ If different from 'language':
        # 'codemirror_mode': {
        #    "version": 2,
        #    "name": "ipython"
        # }
        # 'pygments_lexer': 'language',
        # 'version'       : "x.y.z",
        'file_extension': '.py',
        'help_links': MetaKernel.help_links,
    }
    kernel_json = {
        "argv": [
            sys.executable, "-m", "metakernel_python", "-f", "{connection_file}"],
        "display_name": "MetaKernel Python",
        "language": "python",
        "name": "metakernel_python"
    }

    def get_usage(self):
        return ("This is MetaKernel Python. It implements a Python " +
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

    def get_completions(self, info):
        python_magic = self.line_magics['python']
        return python_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        python_magic = self.line_magics['python']
        return python_magic.get_help_on(info, level, none_on_fail)


if __name__ == '__main__':
    MetaKernelPython.run_as_main()
