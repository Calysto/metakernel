import errno
import sys
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
        if isinstance(s, str):
            return s.decode('utf-8')
        return s

PEXPECT_PROMPT = u('PEXPECT_PROMPT>')
PEXPECT_STDIN_PROMPT = u('PEXPECT_PROMPT+')
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
    :param str stdin_prompt_regex: The regex for a stdin prompt from the 
        child process.  The prompt itself will be sent to the `stdin_handler`,
        so any sentinel value inserted will have to be removed by the caller.
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
                 stdin_prompt_regex=PEXPECT_STDIN_PROMPT,
                 extra_init_cmd=None,
                 prompt_emit_cmd=None,
                 echo=False):
        if isinstance(cmd_or_spawn, str):
            self.child = pexpect.spawnu(cmd_or_spawn, echo=echo,
                                        codec_errors="ignore",
                                        encoding="utf-8")
        else:
            self.child = cmd_or_spawn

        if self.child.echo and not echo:
            # Existing spawn instance has echo enabled, disable it
            # to prevent our input from being repeated to output.
            self.child.setecho(False)
            self.child.waitnoecho()

        # Convert all arguments to unicode.
        prompt_regex = u(prompt_regex)
        prompt_change_cmd = u(prompt_change_cmd)
        continuation_prompt_regex = u(continuation_prompt_regex)
        stdin_prompt_regex = u(stdin_prompt_regex)
        prompt_emit_cmd = u(prompt_emit_cmd)

        self.echo = echo
        self.prompt_emit_cmd = prompt_emit_cmd

        if prompt_change_cmd is None:
            self.prompt_regex = u(prompt_regex)
        else:
            self.set_prompt(prompt_regex,
                            prompt_change_cmd.format(new_prompt_regex,
                                                     continuation_prompt_regex))
            self.prompt_regex = new_prompt_regex
        self.continuation_prompt_regex = continuation_prompt_regex
        self.stdin_prompt_regex = stdin_prompt_regex

        self._stream_handler = None
        self._stdin_handler = None
        self._expect_prompt()

        if extra_init_cmd is not None:
            self.run_command(extra_init_cmd)

        atexit.register(self.terminate)

    def sendline(self, line):
        self.child.sendline(u(line))
        if self.echo:
            self.child.readline()

    def set_prompt(self, prompt_regex, prompt_change_cmd):
        self.child.expect(prompt_regex)
        self.sendline(prompt_change_cmd)

    def _expect_prompt(self, timeout=None):
        """Expect a prompt from the child.
        """
        stream_handler = self._stream_handler
        stdin_handler = self._stdin_handler
        expects = [self.prompt_regex, self.continuation_prompt_regex,
                   self.stdin_prompt_regex]
        if stream_handler:
            expects += [u(self.child.crlf)]
        if self.prompt_emit_cmd:
            self.sendline(self.prompt_emit_cmd)
        while True:
            pos = self.child.expect(expects, timeout=timeout)
            if pos == 2 and stdin_handler:
                resp = stdin_handler(self.child.before + self.child.after)
                self.sendline(resp)
            elif pos == 3:  # End of line received
                stream_handler(self.child.before)
            else:
                if len(self.child.before) != 0 and stream_handler:
                    # prompt received, but partial line precedes it
                    stream_handler(self.child.before)
                break
        return pos

    def run_command(self, command, timeout=None, stream_handler=None,
                    stdin_handler=None):
        """Send a command to the REPL, wait for and return output.
        :param str command: The command to send. Trailing newlines are not needed.
          This should be a complete block of input that will trigger execution;
          if a continuation prompt is found after sending input, :exc:`ValueError`
          will be raised.
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

        res = []
        self._stream_handler = stream_handler
        self._stdin_handler = stdin_handler
        self.sendline(cmdlines[0])
        for line in cmdlines[1:]:
            self._expect_prompt(timeout=timeout)
            res.append(self.child.before)
            self.sendline(line)

        # Command was fully submitted, now wait for the next prompt
        if self._expect_prompt(timeout=timeout) == 1:
            # We got the continuation prompt - command was incomplete
            self.interrupt()
            raise ValueError("Continuation prompt found - input was incomplete:\n" + command)
        return u''.join(res + [self.child.before])

    def interrupt(self):
        """Interrupt the process and wait for a prompt.

        Returns
        -------
        The value up to the prompt.
        """
        if pexpect.pty:
            self.child.sendintr()
        else:
            self.child.kill(signal.SIGINT)
        while 1:
            try:
                self._expect_prompt(timeout=-1)
                break
            except KeyboardInterrupt:
                pass
        return self.child.before

    def terminate(self):
        if pexpect.pty:
            self.child.close()
            return self.child.terminate()
        try:
            self.child.kill(signal.SIGTERM)
        except Exception as e:
            if e.errno != errno.EACCES:
                raise


def python(command="python"):
    """Start a Python shell and return a :class:`REPLWrapper` object."""
    if not pexpect.pty:
        raise OSError('Not supported on platform "%s"' % sys.platform)
    return REPLWrapper(command, u(">>> "),
                       u("import sys; sys.ps1={0!r}; sys.ps2={1!r}"))


def bash(command="bash", prompt_regex=re.compile('[$#]')):
    """Start a bash shell and return a :class:`REPLWrapper` object."""

    # If the user runs 'env', the value of PS1 will be in the output. To avoid
    # replwrap seeing that as the next prompt, we'll embed the marker characters
    # for invisible characters in the prompt; these show up when inspecting the
    # environment variable, but not when bash displays the prompt.
    ps1 = PEXPECT_PROMPT[:5] + u'\[\]' + PEXPECT_PROMPT[5:]
    ps2 = PEXPECT_CONTINUATION_PROMPT[:5] + u'\[\]' + PEXPECT_CONTINUATION_PROMPT[5:]
    prompt_change_cmd = u"PS1='{0}' PS2='{1}' PROMPT_COMMAND=''".format(ps1, ps2)

    if os.name == 'nt':
        prompt_regex = u('__repl_ready__')
        prompt_emit_cmd = u('echo __repl_ready__')
        prompt_change_cmd = None
    else:
        prompt_emit_cmd = None

    extra_init_cmd = "export PAGER=cat"

    # Make sure the bash shell has a valid ending character.
    bashrc = os.path.join(os.path.dirname(pexpect.PEXPECT_DIR), 'bashrc.sh')
    child = pexpect.spawn(command, ['--rcfile', bashrc], echo=False,
                          encoding='utf-8')

    return REPLWrapper(child, prompt_regex, prompt_change_cmd,
                       prompt_emit_cmd=prompt_emit_cmd,
                       extra_init_cmd=extra_init_cmd)


def cmd(command='cmd', prompt_regex=re.compile(r'[A-Z]:\\.*>')):
    """"Start a cmd shell and return a :class:`REPLWrapper` object."""
    if not os.name == 'nt':
        raise OSError('cmd only available on Windows')
    return REPLWrapper(command, prompt_regex, None, echo=True)
