from __future__ import absolute_import
from metakernel import MetaKernel
from metakernel.pyexpect import REPLWrapper, EOF, u

import os
import re

__version__ = '0.0'

version_pat = re.compile(r'version (\d+(\.\d+)+)')


class ProcessMetaKernel(MetaKernel):
    implementation = 'process_kernel'
    implementation_version = __version__
    language = 'process'

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
        self._start()

    def _start(self):
        if not self.wrapper is None:
            self.wrapper.child.terminate()
        self.wrapper = self.makeWrapper()

    def do_execute_direct(self, code):

        if not code.strip():
            self.payload = {'status': 'ok',
                            'execution_count': self.execution_count,
                            'payload': [], 'user_expressions': {}}
            return

        interrupted = False
        try:
            output = self.wrapper.run_command(code.rstrip(), timeout=None)
        except KeyboardInterrupt:
            self.wrapper.child.sendintr()
            interrupted = True
            self.wrapper._expect_prompt()
            output = self.wrapper.child.before
        except EOF:
            output = self.wrapper.child.before + 'Restarting'
            self._start()

        if interrupted:
            self.payload = {'status': 'abort',
                            'execution_count': self.execution_count}

        exitcode, trace = self.check_exitcode()

        if exitcode:
            self.payload = {'status': 'error',
                            'execution_count': self.execution_count,
                            'ename': '', 'evalue': str(exitcode),
                            'traceback': trace}
        else:
            self.payload = {'status': 'ok',
                            'execution_count': self.execution_count,
                            'payload': [], 'user_expressions': {}}

        return output

    def check_exitcode(self):
        """
        Return (1, ["trace"]) if error.
        """
        return (0, None)

    def makeWrapper(self):
        raise NotImplementedError


class BashKernel(ProcessMetaKernel):
    # Identifiers:
    implementation = 'bash_kernel'
    language = 'bash'
    _banner = "Bash Kernel"

    def makeWrapper(self):
        """Start a bash shell and return a :class:`REPLWrapper` object.

        Note that this is equivalent :function:`metakernel.pyexpect.bash`,
        but is used here as an example of how to be cross-platform.
        """
        if os.name == 'nt':
            command = 'bash'
            orig_prompt = '__repl_ready__'
            prompt_cmd = 'echo __repl_ready__'
            prompt_change = None

        else:
            command = 'bash -i'
            prompt_change = u("PS1='{0}' PS2='{1}' PROMPT_COMMAND=''")
            prompt_cmd = None
            orig_prompt = re.compile('[$#]')

        extra_init_cmd = "export PAGER=cat"

        return REPLWrapper(command, orig_prompt, prompt_change,
                           prompt_cmd=prompt_cmd,
                           extra_init_cmd=extra_init_cmd)

    def check_exitcode(self):
        return (int(self.wrapper.run_command('echo $?').rstrip()), [])
