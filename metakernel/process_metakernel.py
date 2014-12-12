from __future__ import absolute_import
from . import MetaKernel
from .pexpect import EOF
from .replwrap import REPLWrapper, u
from subprocess import check_output
import os
import re

__version__ = '0.0'

version_pat = re.compile(r'version (\d+(\.\d+)+)')


class ProcessMetaKernel(MetaKernel):
    implementation = 'process_kernel'
    implementation_version = __version__
    language = 'process'
    language_info = {
        # 'mimetype': 'text/x-python',
        # 'language': 'python',
        # ------ If different from 'language':
        # 'codemirror_mode': 'language',
        # 'pygments_lexer': 'language',
        # 'file_extension': 'py',
    }

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = "Process"

    @property
    def banner(self):
        return self._banner

    def __init__(self, **kwargs):
        MetaKernel.__init__(self, **kwargs)
        self.wrapper = None
        self.repr = str
        self._start()

    def _start(self):
        if not self.wrapper is None:
            self.wrapper.child.terminate()
        self.wrapper = self.makeWrapper()

    def do_execute_direct(self, code):

        self.payload = []

        if not code.strip():
            self.kernel_resp = {'status': 'ok',
                            'execution_count': self.execution_count,
                            'payload': [], 'user_expressions': {}}
            return

        interrupted = False
        try:
            output = self.wrapper.run_command(code.rstrip(), timeout=None)
        except KeyboardInterrupt as e:
            interrupted = True
            output = self.wrapper.child.before
            if 'REPL not responding to interrupt' in str(e):
                output += '\n%s' % e
        except EOF:
            output = self.wrapper.child.before + 'Restarting'
            self._start()

        if interrupted:
            self.kernel_resp = {'status': 'abort',
                            'execution_count': self.execution_count}

        exitcode, trace = self.check_exitcode()

        if exitcode:
            self.kernel_resp = {'status': 'error',
                            'execution_count': self.execution_count,
                            'ename': '', 'evalue': str(exitcode),
                            'traceback': trace}
        else:
            self.kernel_resp = {'status': 'ok',
                            'execution_count': self.execution_count,
                            'payload': [], 'user_expressions': {}}

        return output

    def check_exitcode(self):
        """
        Return (1, ["trace"]) if error.
        """
        return (0, None)

    def makeWrapper(self):
        """
        In this method the REPLWrapper is created and returned.
        REPLWrapper takes the name of the executable, and arguments
        describing the executable prompt:

        return REPLWrapper('bash', orig_prompt, prompt_change,
                           prompt_cmd=prompt_cmd,
                           extra_init_cmd=extra_init_cmd)

        The parameters are:

        :param orig_prompt: What the original prompt is (or is forced
        to be by prompt_cmd).

        :param prompt_cmd: Used when the prompt is not printed by default
        (happens on Windows) to print something that we can search for.

        :param prompt_change: Used to set the PS1/PS2 equivalents to
        something that is easier to tell apart from everything else,
        make sure it is a string with {0} and {1} in it for the
        PS1/PS2 fill-ins.

        See `metakernel.replwrap.REPLWrapper` for more details.

        """
        raise NotImplementedError


class DynamicKernel(ProcessMetaKernel):
    def __init__(self, 
                 executable,
                 language,
                 mimetype="text/plain",
                 implementation="metakernel",
                 file_extension='txt',
                 orig_prompt=None,
                 prompt_change=None,
                 prompt_cmd=None,
                 extra_init_cmd=None):
        self.executable = executable
        self.orig_prompt = orig_prompt
        self.prompt_change = prompt_change
        self.prompt_cmd = prompt_cmd
        self.extra_init_cmd = extra_init_cmd
        self.implementation = implementation
        self.language = language
        self.language_info['mimetype'] = mimetype
        self.language_info['language'] = language
        self.language_info['file_extension'] = file_extension
        super(DynamicKernel, self).__init__()

    def makeWrapper(self):
        return REPLWrapper(self.executable, 
                           u(self.orig_prompt), 
                           self.prompt_change,
                           prompt_cmd=self.prompt_cmd,
                           extra_init_cmd=self.extra_init_cmd)

    """
    DynamicKernel(executable="bash",
                  orig_prompt=re.compile('[$#]'),
                  prompt_change=u("PS1='{0}' PS2='{1}' PROMPT_COMMAND=''"),
                  prompt_cmd=None,
                  extra_init_cmd="export PAGER=cat",
                  implementation="bash_kernel",
                  language="bash",
                  mimetype="text/x-bash",
                  file_extension="sh")
    """

class BashKernel(ProcessMetaKernel):
    # Identifiers:
    implementation = 'bash_kernel'
    language = 'bash'
    language_info = {
        'mimetype': 'text/x-bash',
        'language': 'bash',
        # ------ If different from 'language':
        # 'codemirror_mode': 'language',
        # 'pygments_lexer': 'language',
        'file_extension': 'sh',
    }

    _banner = None
    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['bash', '--version']).decode('utf-8')
        return self._banner

    def makeWrapper(self):
        """Start a bash shell and return a :class:`REPLWrapper` object.

        Note that this is equivalent :function:`metakernel.pyexpect.bash`,
        but is used here as an example of how to be cross-platform.
        """
        if os.name == 'nt':
            prompt_regex = u('__repl_ready__')
            prompt_emit_cmd = u('echo __repl_ready__')
            prompt_change_cmd = None

        else:
            prompt_change_cmd = u("PS1='{0}' PS2='{1}' PROMPT_COMMAND=''")
            prompt_emit_cmd = None
            prompt_regex = re.compile('[$#]')

        extra_init_cmd = "export PAGER=cat"

        return REPLWrapper('bash', prompt_regex, prompt_change_cmd,
                           prompt_emit_cmd=prompt_emit_cmd,
                           extra_init_cmd=extra_init_cmd)

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=BashKernel)
