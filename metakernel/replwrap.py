from __future__ import absolute_import
import os
import re
import signal
import sys
import pexpect
from pexpect import replwrap


IS_WINDOWS = sys.platform == 'win32'

PY3 = (sys.version_info[0] >= 3)

if PY3:
    def u(s):
        return s
else:
    def u(s):
        return s.decode('utf-8')


class REPLWrapper(replwrap.REPLWrapper):
    """Wrapper for a REPL.
    All prompts are interpreted as regexes.  If you have special
    characters in the prompt, use `re.escape` to escape the characters.
    :param cmd_or_spawn: This can either be an instance of
    :class:`pexpect.spawn` in which a REPL has already been started,
    or a str command to start a new REPL process.
    :param str prompt_regex:  Regular expression representing process prompt, eg ">>>" in Python.
    :param str continuation_prompt_regex: Regular expression repesenting process continuation prompt, e.g. "..." in Python.
    :param str prompt_change_cmd: Optional kernel command that sets continuation-of-line-prompts, eg PS1 and PS2, such as "..." in Python.
        to something more unique. If this is ``None``, the prompt will not be
        changed. This will be formatted with the new and continuation prompts
        as positional parameters, so you can use ``{}`` style formatting to
        insert them into the command.
    :param str new_prompt_regex: The more unique prompt to expect after the change.
    :param str extra_init_cmd: Commands to do extra initialisation, such as
      disabling pagers.
    :param str prompt_emit_cmd: Optional kernel command that emits the prompt
      when one is not emitted by default (typically happens on Windows only)
    :param bool echo: Whether the child should echo, or in the case
    of Windows, whether the child does echo.
    """
    def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
                 extra_init_cmd=None,
                 prompt_emit_cmd=None,
                 echo=False):
        self.prompt_emit_cmd = prompt_emit_cmd
        self.echo = echo
        # Signal handlers are inherited by forked processes, and we can't
        # easily  reset it from the subprocess. Since kernelapp ignores SIGINT
        # except in message handlers, we need to temporarily reset the SIGINT
        # handler here so that the subprocess and its children are
        # interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            replwrap.REPLWrapper.__init__(self, cmd_or_spawn, orig_prompt,
                                          prompt_change,
                                          extra_init_cmd=extra_init_cmd)
        finally:
            signal.signal(signal.SIGINT, sig)

    def run_command(self, command, timeout=-1, stream_handler=None):
        """Send a command to the REPL, wait for and return output.

        :param str command: The command to send. Trailing newlines are not needed.
          This should be a complete block of input that will trigger execution;
          if a continuation prompt is found after sending input, :exc:`ValueError`
          will be raised.
        :param int timeout: How long to wait for the next prompt. -1 means the
          default from the :class:`pexpect.spawn` object (default 30 seconds).
          None means to wait indefinitely.
        :param stream_handler: a callback method to receive each batch
        of incremental output. It takes one string parameter.
        """
        self.stream_handler = stream_handler
        value = replwrap.REPLWrapper.run_command(self, command, timeout)
        if stream_handler and value:
            stream_handler(value)
            value = ''
        return value

    def sendline(self, line):
        self.child.sendline(line)
        if self.echo:
            self.child.readline()

    def _expect_prompt(self, timeout=-1):
        if self.prompt_emit_cmd:
            self.sendline(self.prompt_emit_cmd)
        if timeout is None and self.stream_handler is not None:
            # "None" means we are executing code from a Jupyter cell by way of 
            # the run_command so do incremental output.
            while True:
                pos = self.child.expect_exact([self.prompt, self.continuation_prompt, '\r\n'],
                                              timeout=None)
                if pos == 2:
                    # End of line received
                    self.stream_handler(self.child.before + '\n')
                else:
                    if len(self.child.before) != 0:
                        # prompt received, but partial line precedes it
                        self.stream_handler(self.child.before)
                    break
        else:
            # Otherwise, use existing non-incremental code
            pos = replwrap.REPLWrapper._expect_prompt(self, timeout=timeout)

        # Prompt received, so return normally
        return pos


def python(command="python"):
    """Start a Python shell and return a :class:`REPLWrapper` object."""
    if IS_WINDOWS:
        raise OSError('Not supported on platform "%s"' % sys.platform)
    return REPLWrapper(command, u">>> ",
                       u"import sys; sys.ps1={0!r}; sys.ps2={1!r}")


def bash(command="bash"):
    """Start a bash shell and return a :class:`REPLWrapper` object."""
    # Note: the next few lines mirror functionality in the
    # bash() function of pexpect/replwrap.py.  Look at the
    # source code there for comments and context for
    # understanding the code here.
    bashrc = os.path.join(os.path.dirname(pexpect.__file__), 'bashrc.sh')
    child = pexpect.spawn("bash", ['--rcfile', bashrc], echo=False,
                          encoding='utf-8')
    ps1 = replwrap.PEXPECT_PROMPT[:5] + u'\[\]' + replwrap.PEXPECT_PROMPT[5:]
    ps2 = replwrap.PEXPECT_CONTINUATION_PROMPT[:5] + u'\[\]' + replwrap.PEXPECT_CONTINUATION_PROMPT[5:]
    prompt_change = u"PS1='{0}' PS2='{1}' PROMPT_COMMAND=''".format(ps1, ps2)

    # Using IREPLWrapper to get incremental output
    return REPLWrapper(child, u'\$', prompt_change,
                       extra_init_cmd="export PAGER=cat")


def cmd(command='cmd', prompt_regex=re.compile(r'[A-Z]:\\.*>')):
    """"Start a cmd shell and return a :class:`REPLWrapper` object."""
    if IS_WINDOWS:
        raise OSError('cmd only available on Windows')
    return REPLWrapper(command, prompt_regex, None, echo=True)
