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

    def __init__(self, cmd_or_spawn, prompt_regex, prompt_change_cmd,
                 new_prompt_regex=PEXPECT_PROMPT,
                 continuation_prompt_regex=PEXPECT_CONTINUATION_PROMPT,
                 extra_init_cmd=None,
                 prompt_emit_cmd=None,
                 echo=False):
        if isinstance(cmd_or_spawn, str):
            self.child = pexpect.spawnu(cmd_or_spawn, echo=echo,
                                        errors="ignore")
        else:
            self.child = cmd_or_spawn

        if self.child.echo and not echo:
            # Existing spawn instance has echo enabled, disable it
            # to prevent our input from being repeated to output.
            self.child.setecho(False)
            self.child.waitnoecho()

        self.echo = echo
        self.prompt_emit_cmd = prompt_emit_cmd

        if prompt_change_cmd is None:
            self.prompt_regex = prompt_regex
        else:
            self.set_prompt(prompt_regex,
                            prompt_change_cmd.format(new_prompt_regex,
                                                     continuation_prompt_regex))
            self.prompt_regex = new_prompt_regex
        self.continuation_prompt_regex = continuation_prompt_regex

        self._expect_prompt()

        if extra_init_cmd is not None:
            self.run_command(extra_init_cmd)

        atexit.register(self.child.terminate)

    def sendline(self, line):
        self.child.sendline(line)
        if self.echo:
            self.child.readline()

    def set_prompt(self, prompt_regex, prompt_change_cmd):
        self.child.expect(prompt_regex)
        self.sendline(prompt_change_cmd)

    def _expect_prompt(self, timeout=-1):
        if self.prompt_emit_cmd:
            self.sendline(self.prompt_emit_cmd)

        try:
            return self.child.expect([self.prompt_regex, self.continuation_prompt_regex],
                                     timeout=timeout)
        except KeyboardInterrupt:
            self.child.sendintr()
            if self.prompt_emit_cmd:
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
            self._expect_prompt(timeout=-1)
            self.sendline(line)

        # Command was fully submitted, now wait for the next prompt
        if self._expect_prompt(timeout=timeout) == 1:
            # We got the continuation prompt - command was incomplete
            self.child.kill(signal.SIGINT)
            self._expect_prompt(timeout=-1)
            raise ValueError("Continuation prompt found -"
                             " input was incomplete:\n" + command)
        return self.child.before


def python(command="python"):
    """Start a Python shell and return a :class:`REPLWrapper` object."""
    if not pexpect.pty:
        raise OSError('Not supported on platform "%s"' % sys.platform)
    return REPLWrapper(command, u(">>> "),
                       u("import sys; sys.ps1={0!r}; sys.ps2={1!r}"))


def bash(command="bash", prompt_regex=re.compile('[$#]')):
    """Start a bash shell and return a :class:`REPLWrapper` object."""
    if os.name == 'nt':
        prompt_regex = u('__repl_ready__')
        prompt_emit_cmd = u('echo __repl_ready__')
        prompt_change_cmd = None

    else:
        prompt_change_cmd = u("PS1='{0}' PS2='{1}' PROMPT_COMMAND=''")
        prompt_emit_cmd = None

    extra_init_cmd = "export PAGER=cat"

    return REPLWrapper(command, prompt_regex, prompt_change_cmd,
                       prompt_emit_cmd=prompt_emit_cmd,
                       extra_init_cmd=extra_init_cmd)


def cmd(command='cmd', prompt_regex=re.compile(r'[A-Z]:\\.*>')):
    """"Start a cmd shell and return a :class:`REPLWrapper` object."""
    if not os.name == 'nt':
        raise OSError('cmd only available on Windows')
    return REPLWrapper(command, prompt_regex, None, echo=True)
