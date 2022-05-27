import errno
import sys
import re
import signal
import os
import time
import atexit

from . import pexpect


def u(s):
    return s
basestring = str

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
    :param str continuation_prompt_regex: Regular expression representing process continuation prompt, e.g. "..." in Python.
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
    :param bool force_prompt_on_continuation: Whether to force a prompt when
    we need to interrupt a continuation prompt.
    :param bool echo: Whether the child should echo, or in the case
    of Windows, whether the child does echo.
    """

    def __init__(self, cmd_or_spawn, prompt_regex, prompt_change_cmd,
                 new_prompt_regex=PEXPECT_PROMPT,
                 continuation_prompt_regex=PEXPECT_CONTINUATION_PROMPT,
                 stdin_prompt_regex=PEXPECT_STDIN_PROMPT,
                 extra_init_cmd=None,
                 prompt_emit_cmd=None,
                 force_prompt_on_continuation=False,
                 echo=False):
        if isinstance(cmd_or_spawn, basestring):
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
        self._force_prompt_on_continuation = force_prompt_on_continuation

        if prompt_change_cmd is None:
            self.prompt_regex = u(prompt_regex)
            self.prompt_change_cmd = None
        else:
            self.set_prompt(prompt_regex,
                            prompt_change_cmd.format(new_prompt_regex,
                                                     continuation_prompt_regex))
            self.prompt_regex = new_prompt_regex
        self.continuation_prompt_regex = continuation_prompt_regex
        self.stdin_prompt_regex = stdin_prompt_regex

        self._stream_handler = None
        self._stdin_handler = None
        self._line_handler = None

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
        self.prompt_change_cmd = prompt_change_cmd

    def _expect_prompt(self, timeout=None):
        """Expect a prompt from the child.
        """
        expects = [self.prompt_regex, self.continuation_prompt_regex,
                   self.stdin_prompt_regex]
        if self.prompt_emit_cmd:
            self.sendline(self.prompt_emit_cmd)

        if self._stream_handler:
            return self._expect_prompt_stream(expects, timeout)

        if self._line_handler:
            expects += [u(self.child.crlf)]

        while True:
            pos = self.child.expect(expects, timeout=timeout)
            # got a full prompt or continuation prompt.
            if pos in [0, 1]:
                return pos
            # got a stdin prompt
            if pos == 2:
                if not self._stdin_handler:
                    raise ValueError('Stdin Requested but not stdin handler available')

                resp = self._stdin_handler(self.child.after)
                self.sendline(resp)
            # got a newline
            else:
                self._line_handler(self.child.before.rstrip())

    def _expect_prompt_stream(self, expects, timeout=None):
        """Expect a prompt with streaming output.
        """
        stream_handler = self._stream_handler
        stdin_handler = self._stdin_handler

        t0 = time.time()
        if timeout == -1:
            timeout = 30
        elif timeout is None:
            timeout = 1e6
        stream_timeout = 0.1

        unhandled_cr = False

        # Wait for a prompt, handling carriage returns.
        while True:
            if time.time() - t0 > timeout:
                raise pexpect.TIMEOUT('Timed out')

            try:
                # Wait for a prompt.
                pos = self.child.expect(expects, timeout=stream_timeout)
            except pexpect.TIMEOUT:
                # Process any carriage returns in the stream.
                while 1:
                    try:
                        self.child.expect([u('\r')], timeout=0)
                        if unhandled_cr:
                            stream_handler('\r')
                        stream_handler(self.child.before)
                        unhandled_cr = True
                    except pexpect.TIMEOUT:
                        break
                continue

            # prompt or stdin request received, handle line.
            line = self.child.before

            # Handle cr state.
            if unhandled_cr:
                line = '\r' + line
            unhandled_cr = False

            # Handle stdin request.
            if pos == 2:
                if not stdin_handler:
                    raise ValueError('Stdin Requested but no stdin handler available')
                resp = stdin_handler(line + self.child.after)
                self.sendline(resp)
                continue

            # prompt received, but partial line precedes it
            if len(line) != 0:
                stream_handler(line)

            # exit on prompt received.
            break
        return pos

    def run_command(self, command, timeout=None, stream_handler=None,
                    line_handler=None, stdin_handler=None):
        """Send a command to the REPL, wait for and return output.
        :param str command: The command to send. Trailing newlines are not needed.
          This should be a complete block of input that will trigger execution;
          if a continuation prompt is found after sending input, :exc:`ValueError`
          will be raised.
        :param int timeout: How long to wait for the next prompt. -1 means the
          default from the :class:`pexpect.spawn` object (default 30 seconds).
          None means to wait indefinitely.
        :param func stream_handler - A function that accepts a string to print as a streaming output
        :param func line_handler - A function that accepts a string to print as a line output
        :param stdin_handler - A function that prompts the user for input and
        returns a response.
        """
        # Split up multiline commands and feed them in bit-by-bit
        cmdlines = command.splitlines()
        # splitlines ignores trailing newlines - add it back in manually
        if command.endswith('\n'):
            cmdlines.append('')
        if not cmdlines:
            raise ValueError("No command was given")

        res = []
        self._line_handler = line_handler
        self._stream_handler = stream_handler
        self._stdin_handler = stdin_handler

        self.sendline(cmdlines[0])
        for line in cmdlines[1:]:
            if not self.prompt_emit_cmd:
                self._expect_prompt(timeout=timeout)
                res.append(self.child.before)
            self.sendline(line)

        # Command was fully submitted, now wait for the next prompt
        if self._expect_prompt(timeout=timeout) == 1:
            # We got the continuation prompt - command was incomplete
            self.interrupt(continuation=True)
            raise ValueError("Continuation prompt found - input was incomplete:\n" + command)

        if self._stream_handler or self._line_handler:
            return u''
        return u''.join(res + [self.child.before])

    def interrupt(self, continuation=False):
        """Interrupt the process and wait for a prompt.

        Returns
        -------
        The value up to the prompt.
        """
        if pexpect.pty:
            self.child.sendintr()
        else:
            self.child.kill(signal.SIGINT)
        if continuation and self._force_prompt_on_continuation:
            self.sendline(self.prompt_change_cmd or '')
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
    ps1 = PEXPECT_PROMPT[:5] + r'\[\]' + PEXPECT_PROMPT[5:]
    ps2 = PEXPECT_CONTINUATION_PROMPT[:5] + r'\[\]' + PEXPECT_CONTINUATION_PROMPT[5:]
    prompt_change_cmd = u"PS1='{0}' PS2='{1}' PROMPT_COMMAND=''".format(ps1, ps2)

    if os.name == 'nt':
        prompt_regex = u('__repl_ready__')
        prompt_emit_cmd = u('echo __repl_ready__')
        prompt_change_cmd = None
    else:
        prompt_emit_cmd = None

    extra_init_cmd = "export TERM=dumb PAGER=cat"

    # Make sure the bash shell has a valid ending character.
    bashrc = os.path.join(os.path.dirname(pexpect.PEXPECT_DIR), 'bashrc.sh')
    child = pexpect.spawn(command, ['--rcfile', bashrc], echo=False,
                          encoding='utf-8')

    return REPLWrapper(child, prompt_regex, prompt_change_cmd,
                       prompt_emit_cmd=prompt_emit_cmd,
                       extra_init_cmd=extra_init_cmd)


def powershell(command='powershell', prompt_regex='>'):
    """"Start a powershell and return a :class:`REPLWrapper` object."""
    return REPLWrapper(command, prompt_regex, 'Function prompt {{ "{0}" }}', echo=True)
