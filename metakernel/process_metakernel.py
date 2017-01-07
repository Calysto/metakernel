from __future__ import absolute_import
from . import MetaKernel
from pexpect import EOF
from .replwrap import REPLWrapper, bash
from subprocess import check_output
import re

__version__ = '0.0'

version_pat = re.compile(r'version (\d+(\.\d+)+)')

if PY3:
    string_types = (str,)
else:
    string_types = basestring

class TextOutput(object):
    """Wrapper for text output whose repr is the text itself.

    This avoids `repr(output)` adding quotation marks around already-rendered text.
    """
    def __init__(self, output):
        self.output = output

    def __repr__(self):
        return self.output


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

    def __init__(self, *args, **kwargs):
        MetaKernel.__init__(self, *args, **kwargs)
        self.wrapper = None
        self._start()
    
    def repr(self, item):
        """Return text representation
        
        Don't wrap str in repr to avoid adding quotes to reprs from subprocesses.
        """
        if isinstance(item, string_types):
            # return the string itself because repr would wrap it in quotes
            return item
        else:
            # use regular repr on non-string objects
            return repr(item)

    def _start(self):
        if self.wrapper is not None:
            self.wrapper.child.terminate()
        self.wrapper = self.makeWrapper()

    def do_execute_direct(self, code, silent=False):
        """Execute the code in the subprocess.
        """
        self.payload = []

        if not code.strip():
            self.kernel_resp = {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
            return

        interrupted = False
        output = ''
        stream_handler = self.Print if not silent else None
        try:
            output = self.wrapper.run_command(code.rstrip(), timeout=None,
                                     stream_handler=stream_handler,
                                     stdin_handler=self.raw_input)
        except KeyboardInterrupt as e:
            interrupted = True
            output = self.wrapper.child.before
            if 'REPL not responding to interrupt' in str(e):
                output += '\n%s' % e
        except EOF:
            output = self.wrapper.child.before + 'Restarting'
            self._start()

        if interrupted:
            self.kernel_resp = {
                'status': 'abort',
                'execution_count': self.execution_count,
            }

        exitcode, trace = self.check_exitcode()

        if exitcode:
            self.kernel_resp = {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': '', 'evalue': str(exitcode),
                'traceback': trace,
            }
        else:
            self.kernel_resp = {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }

        if silent and output:
            return TextOutput(output)

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
                 extra_init_cmd=None,
                 stdin_prompt_regex=None):
        self.executable = executable
        self.orig_prompt = orig_prompt
        self.prompt_change = prompt_change
        self.prompt_cmd = prompt_cmd
        self.extra_init_cmd = extra_init_cmd
        self.stdin_prompt_regex = stdin_prompt_regex
        self.implementation = implementation
        self.language = language
        self.language_info['mimetype'] = mimetype
        self.language_info['language'] = language
        self.language_info['file_extension'] = file_extension
        super(DynamicKernel, self).__init__()

    def makeWrapper(self):
        return REPLWrapper(self.executable,
                           self.orig_prompt,
                           self.prompt_change,
                           prompt_cmd=self.prompt_cmd,
                           stdin_prompt_regex=self.stdin_prompt_regex,
                           extra_init_cmd=self.extra_init_cmd)

    """
    DynamicKernel(executable="bash",
                  orig_prompt=re.compile('[$#]'),
                  prompt_change=u"PS1='{0}' PS2='{1}' PROMPT_COMMAND=''",
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
        return bash()

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=BashKernel)
