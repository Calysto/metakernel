import sys
import time
import re
import signal
import os
import atexit

from . import pexpect

PY3 = (sys.version_info[0] >= 3)

if PY3:
    def u(s):
        return s
else:
    def u(s):
        return s.decode('utf-8')

PEXPECT_PROMPT = u('PEXPECT_PROMPT>')
PEXPECT_CONTINUATION_PROMPT = u('PEXPECT_PROMPT_')


class REPLWrapper(object):

    """Wrapper for a REPL.

    All prompts are interpreted as regexes.  If you have special
    characters in the prompt, use `re.escape` to escape the characters.

    :param cmd_or_spawn: This can either be an instance of
    :class:`pexpect.spawn` in which a REPL has already been started,
    or a str command to start a new REPL process.
    :param str orig_prompt: The prompt to expect at first.
    :param str prompt_change: A command to change the prompt to something more
      unique. If this is ``None``, the prompt will not be changed. This will
      be formatted with the new and continuation prompts as positional
      parameters, so you can use ``{}`` style formatting to insert them into
      the command.
    :param str new_prompt: The more unique prompt to expect after the change.
    :param str extra_init_cmd: Commands to do extra initialisation, such as
      disabling pagers.
    :param str prompt_cmd: Command to generate the prompt, if one is not
    printed by default after each command.
    :param bool echo: Whether the child should echo, or in the case
    of Windows, whether the child does echo.
    """

    def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
                 new_prompt=PEXPECT_PROMPT,
                 continuation_prompt=PEXPECT_CONTINUATION_PROMPT,
                 extra_init_cmd=None,
                 prompt_cmd=None,
                 echo=False):
        if isinstance(cmd_or_spawn, str):
            self.child = pexpect.spawnu(cmd_or_spawn, echo=echo)
        else:
            self.child = cmd_or_spawn

        if self.child.echo and not echo:
            # Existing spawn instance has echo enabled, disable it
            # to prevent our input from being repeated to output.
            self.child.setecho(False)
            self.child.waitnoecho()

        self.echo = echo
        self.prompt_cmd = prompt_cmd

        if prompt_change is None:
            self.prompt = orig_prompt
        else:
            self.set_prompt(orig_prompt,
                            prompt_change.format(new_prompt,
                                                 continuation_prompt))
            self.prompt = new_prompt
        self.continuation_prompt = continuation_prompt

        self._expect_prompt()

        if extra_init_cmd is not None:
            self.run_command(extra_init_cmd)

        atexit.register(self.child.terminate)

    def sendline(self, line):
        self.child.sendline(line)
        if self.echo:
            self.child.readline()

    def set_prompt(self, orig_prompt, prompt_change):
        self.child.expect(orig_prompt)
        self.sendline(prompt_change)

    def _expect_prompt(self, timeout=-1):
        if self.prompt_cmd:
            self.sendline(self.prompt_cmd)
        try:
            return self.child.expect([self.prompt, self.continuation_prompt],
                                     timeout=timeout)
        except KeyboardInterrupt:
            self.child.sendintr()
            if self.prompt_cmd:
                time.sleep(1.)
            try:
                self._expect_prompt(timeout=1)
            except pexpect.TIMEOUT:
                raise KeyboardInterrupt('REPL not responding to interrupt')
            raise KeyboardInterrupt

    def run_command(self, command, timeout=-1):
        """Send a command to the REPL, wait for and return output.

        :param str command: The command to send. Trailing newlines are
        not needed.
          This should be a complete block of input that will trigger execution;
          if a continuation prompt is found after sending input,
          :exc:`ValueError` will be raised.
        :param int timeout: How long to wait for the next prompt. -1 means the
          default from the :class:`pexpect.spawn` object (default 30 seconds).
          None means to wait indefinitely.
        """
        # Split up multiline commands and feed them in bit-by-bit
        cmdlines = command.splitlines()
        # splitlines ignores trailing newlines - add it back in manually
        if command.endswith('\n'):
            cmdlines.append('')
        if not cmdlines:
            raise ValueError("No command was given")

        self.sendline(cmdlines[0])
        for line in cmdlines[1:]:
            self._expect_prompt(timeout=1)
            self.sendline(line)

        # Command was fully submitted, now wait for the next prompt
        if self._expect_prompt(timeout=timeout) == 1:
            # We got the continuation prompt - command was incomplete
            self.child.kill(signal.SIGINT)
            self._expect_prompt(timeout=1)
            raise ValueError("Continuation prompt found -"
                             " input was incomplete:\n" + command)
        return self.child.before


def python(command="python"):
    """Start a Python shell and return a :class:`REPLWrapper` object."""
    if not pexpect.pty:
        raise OSError('Not supported on platform "%s"' % sys.platform)
    return REPLWrapper(command, u(">>> "),
                       u("import sys; sys.ps1={0!r}; sys.ps2={1!r}"))


def bash(command="bash", orig_prompt=re.compile('[$#]')):
    """Start a bash shell and return a :class:`REPLWrapper` object."""
    if os.name == 'nt':
        orig_prompt = u('__repl_ready__')
        prompt_cmd = u('echo __repl_ready__')
        prompt_change = None

    else:
        prompt_change = u("PS1='{0}' PS2='{1}' PROMPT_COMMAND=''")
        prompt_cmd = None

    extra_init_cmd = "export PAGER=cat"

    return REPLWrapper(command, orig_prompt, prompt_change,
                       prompt_cmd=prompt_cmd, extra_init_cmd=extra_init_cmd)


def cmd(command='cmd', orig_prompt=re.compile(r'[A-Z]:\\.*>')):
    """"Start a cmd shell and return a :class:`REPLWrapper` object."""
    if not os.name == 'nt':
        raise OSError('cmd only available on Windows')
    return REPLWrapper(command, orig_prompt, None, echo=True)
