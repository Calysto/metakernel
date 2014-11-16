
import subprocess
import os
import re
import threading
import shlex
try:
    import Queue
except ImportError:  # py3k
    import queue as Queue
import sys
import signal
import time
import atexit
import errno

try:
    import pty
    import termios
except ImportError:
    pty = None


class ExceptionPyExpect(Exception):
    pass


class EOF(ExceptionPyExpect):
    '''Raised when EOF is read from a child.
    This usually means the child has exited.'''


class TIMEOUT(ExceptionPyExpect):
    '''Raised when a read time exceeds the timeout. '''


class ExpectBase(object):

    def __init__(self, rchild, wchild=None, read_eol='\n', write_eol='\n',
                 timeout=1e6, encoding='utf-8'):
        """Expect-like interface to a child.

        rchild and wchild can be any one of:
        path to file (str)
        file object
        file descriptor (int)
        socket object
        serial object
        StringIO object
        Any object with read and (optionally) write methods
        """
        self._buf = ''
        self.timeout = timeout
        self.encoding = encoding

        if isinstance(rchild, str):
            if wchild == rchild:
                if encoding is None:
                    rchild = wchild = open(rchild, 'w+')
                else:
                    rchild = wchild = open(rchild, 'wb+')
            else:
                if encoding is None:
                    rchild = open(rchild, 'r')
                else:
                    rchild = open(rchild, 'rb')

        if hasattr(rchild, 'close'):
            atexit.regist(rchild.close)

        if isinstance(wchild, str):
            wchild = open(wchild, 'w')

        if wchild is None:
            wchild = rchild

        elif hasattr(wchild, 'close') and not wchild == rchild:
            atexit.register(wchild.close)

        # set serial timeout = 0
        try:
            rchild.timeout = 0
        except:
            pass

        self.rchild = rchild
        self.wchild = wchild

        self.read_eol = read_eol
        self.write_eol = write_eol

        self.before = ''
        self.after = ''

        self._read_queue = Queue.Queue()
        self._read_thread = threading.Thread(target=self._read_incoming)
        self._read_thread.setDaemon(True)
        self._read_thread.start()

    def read_nonblocking(self, size=-1, timeout=None):
        if timeout in (None, -1):
            timeout = self.timeout

        t0 = time.time()
        while 1:
            try:
                incoming = self._read_queue.get_nowait()
            except Queue.Empty:
                break
            else:
                if incoming is None:
                    raise EOF
                else:
                    self._buf += incoming

                if size >= 0 and len(self._buf) >= size:
                    break
                elif timeout > 0 and time.time() - t0 > timeout:
                    raise TIMEOUT
                elif size == -1 and timeout == -1:
                    break

        if size > 0:
            ret, self._buf = self._buf[:size], self._buf[size:]
        else:
            ret, self._buf = self._buf, ''
        return ret

    def _read_incoming(self):
        BUFSIZE = 1024

        while 1:
            buf = ''
            if isinstance(self.rchild, int):
                try:
                    buf = os.read(self.rchild, BUFSIZE)
                except OSError as e:
                    print(e)

            elif hasattr(self.rchild, 'getvalue'):
                current = self.rchild.tell()
                self.rchild.seek(0, os.SEEK_END)
                end = self.rchild.tell()
                self.rchild.seek(current)
                buf = self.rchild.read(min(end - current, BUFSIZE))

            else:
                try:
                    buf = self.rchild.read(BUFSIZE)
                except Exception as e:
                    print('Error', str(e))

            if not buf:
                buf = None
                self._read_queue.put(buf)
                return

            if self.encoding:
                buf = buf.decode(self.encoding, 'replace')

            self._read_queue.put(buf)
            time.sleep(0.001)

    def read(self, n, timeout=None):
        buf = self.read_nonblocking(n)
        t0 = time.time()
        if timeout in (None, -1):
            timeout = self.timeout

        while time.time() - t0 < timeout and len(buf) < n:
            buf += self.read_nonblocking(n - len(buf))

        return buf

    def next(self):
        self.expect([self.read_eol, EOF])
        if self.after == EOF:
            raise StopIteration
        else:
            return self.before

    def readlines(self, sizehint=None, eol=None, timeout=None):
        lines = []
        t0 = time.time()
        if timeout in (None, -1):
            timeout = self.timeout

        if eol is None:
            eol = self.read_eol

        while time.time() - t0 < self.timeout:
            line = self.expect([eol, EOF], timeout)
            if self.after == EOF:
                return lines
            else:
                lines.append(line)
            if sizehint and len(lines) == sizehint:
                break
        return lines

    def readline(self, eol=None, timeout=None):
        if eol is None:
            eol = self.read_eol
        return self.expect(eol, timeout=timeout)

    def write(self, msg):
        """Write a message to the process"""
        if self.encoding:
            msg = msg.encode(self.encoding)

        if isinstance(self.wchild, int):
            os.write(self.wchild, msg)
        else:
            self.wchild.write(msg)

    def flush(self):
        '''This does nothing. It is here to support the interface for a
        File-like object. '''
        pass

    def fileno(self):
        '''This returns the file descriptor for the rchild.
        '''
        if isinstance(self.rchild, int):
            return self.rchild
        elif hasattr(self.rchild, 'fileno'):
            return self.rchild.fileno()

    def isatty(self):
        '''This returns True if rchild is open and connected to a
        tty(-like) device, else False.
        '''
        if isinstance(self.fileno(), int):
            return os.isatty(self.fileno())

    def sendline(self, line, eol=None):
        if eol is None:
            eol = self.write_eol
        self.write(line + eol)

    def close(self):
        if hasattr(self.rchild, 'close'):
            self.rchild.close()
        if hasattr(self.wchild, 'close') and not self.rchild == self.wchild:
            self.wchild.close()

    def expect(self, patterns, timeout=None, escape=False):
        """Look for a pattern or list of patterns in a stream of data.

        Parameters
        ==========
        patterns : list of strs or regexs, or a single str or regex
            The search patterns.
        timeout : float, optional
            Timeout in seconds
        escape : bool, False
            If True, escape all special regex characters in the patterns
            (for an literal match).
        """

        if not isinstance(patterns, (list, tuple)):
            patterns = [patterns]
        patterns = [p for p in patterns if p]

        if TIMEOUT in patterns:
            allow_timeout = True
            patterns = [p for p in patterns if not p == TIMEOUT]
        else:
            allow_timeout = False

        if EOF in patterns:
            allow_eof = True
            patterns = [p for p in patterns if not p == EOF]
        else:
            allow_eof = False

        if escape:
            patterns = [re.escape(p) for p in patterns]

        if timeout in (None, -1):
            timeout = self.timeout

        t0 = time.time()

        try:
            buf = self.read_nonblocking(timeout=0)
        except EOF:
            if allow_eof:
                self.before = ''
                self.after = EOF
                return ''
            else:
                raise EOF

        while time.time() - t0 < timeout:
            if buf:
                for pattern in patterns:
                    if isinstance(pattern, str):
                        match = re.search(pattern, buf, re.UNICODE | re.MULTILINE)
                    else:
                        match = re.search(pattern, buf)
                    if match:
                        self.before = buf[:match.start()]
                        self.after = buf[match.start(): match.end()]
                        self._buf = buf[match.end():]
                        return self.before
            try:
                buf += self.read_nonblocking(timeout=0)
            except EOF:
                if allow_eof:
                    self.before, self._buf = buf, ''
                    self.after = EOF
                    return self.before
                else:
                    raise EOF

        if allow_timeout:
            self.before, self._buf = buf, ''
            self.after = TIMEOUT
            return self.before
        else:
            raise TIMEOUT

    def expect_exact(self, strings, timeout=None):
        """Look for a string or strings in a stream of data.

        Parameters
        ==========
        strings : list of strs, or a single str
            The search strings.
        timeout : float, optional
            Timeout in seconds
        """
        return self.expect(strings, timeout, escape=True)


class spawn(ExpectBase):

    def __init__(self, cmd, **kwargs):

        read_eol = kwargs.pop('read_eol', '\n')
        write_eol = kwargs.pop('write_eol', '\n')
        timeout = kwargs.pop('timeout', 1e6)

        self.delayafterclose = kwargs.pop('delayafterclose', 0.1)

        if isinstance(cmd, str):
            cmd = shlex.split(cmd)

        if pty is None:
            self.echo = False
            kwargs.update(dict(bufsize=0, stdin=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               stdout=subprocess.PIPE))

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'] = startupinfo
            kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP

        else:
            self.echo = True
            master, slave = pty.openpty()
            kwargs.update(dict(close_fds=True, bufsize=0, stdin=slave,
                               stderr=slave, stdout=slave))

            self.rchild, self.wchild = master, master

        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since some apps ignore SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that the child is interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            self.proc = subprocess.Popen(cmd, **kwargs)
        finally:
            signal.signal(signal.SIGINT, sig)

        if not pty:
            self.rchild = self.proc.stdout.fileno()
            self.wchild = self.proc.stdin.fileno()

        ExpectBase.__init__(self, self.rchild, self.wchild,
                            read_eol, write_eol, timeout)
        atexit.register(self.close)

    def close(self, force=True):
        '''This closes the connection with the child application. Note that
        calling close() more than once is valid. This emulates standard Python
        behavior with files. Set force to True if you want to make sure that
        the child is terminated (SIGKILL is sent if the child ignores SIGHUP
        and SIGINT). '''

        if not self.rchild == -1:
            self.flush()
            if self.terminate() is None and force:
                if self.kill() is None:
                    raise ExceptionPyExpect('Could not terminate the child.')
            self.rchild = -1

    def sendcontrol(self, char):

        """This sends a control character to the child such as Ctrl-C or
        Ctrl-D. For example, to send a Ctrl-G (ASCII 7)::

            child.sendcontrol('g')

        See also, sendintr() and sendeof().
        """

        char = char.lower()
        a = ord(char)
        if a >= 97 and a <= 122:
            a = a - ord('a') + 1
            return self.send(chr(a))
        d = {'@': 0, '`': 0,
                '[': 27, '{' :27,
                '\\': 28, '|': 28,
                ']': 29, '}': 29,
                '^': 30, '~': 30,
                '_': 31,
                '?': 127}
        if char not in d:
            return 0
        return self.send(chr(d[char]))

    def waitnoecho(self, timeout=-1):
        '''This waits until the terminal ECHO flag is set False. This returns
        True if the echo mode is off. This returns False if the ECHO flag was
        not set False before the timeout. This can be used to detect when the
        child is waiting for a password. Usually a child application will turn
        off echo mode when it is waiting for the user to enter a password. For
        example, instead of expecting the "password:" prompt you can wait for
        the child to set ECHO off::

            p = pyexpect.spawn('ssh user@example.com')
            p.waitnoecho()
            p.sendline(mypassword)

        If timeout==-1 then this method will use the value in self.timeout.
        If timeout==None then this method to block until ECHO flag is False.
        '''
        if timeout == -1:
            timeout = self.timeout
        if timeout is not None:
            end_time = time.time() + timeout
        while True:
            if not self.getecho():
                return True
            if timeout < 0 and timeout is not None:
                return False
            if timeout is not None:
                timeout = end_time - time.time()
            time.sleep(0.1)

    def getecho(self):
        '''This returns the terminal echo mode. This returns True if echo is
        on or False if echo is off. Child applications that are expecting you
        to enter a password often set ECHO False. See waitnoecho().

        Not supported on platforms where ``isatty()`` returns False.  '''
        if not self.isatty():
            return self.echo
        
        try:
            attr = termios.tcgetattr(self.rchild)
        except termios.error as err:
            errmsg = 'getecho() may not be called on this platform'
            if err.args[0] == errno.EINVAL:
                raise IOError(err.args[0], '%s: %s.' % (err.args[1], errmsg))
            raise

        self.echo = bool(attr[3] & termios.ECHO)
        return self.echo

    def setecho(self, state):
        '''This sets the terminal echo mode on or off. Note that anything the
        child sent before the echo will be lost, so you should be sure that
        your input buffer is empty before you call setecho().

        Not supported on platforms where ``isatty()`` returns False.
        '''
        if not self.isatty():
            self.echo = state

        errmsg = 'setecho() may not be called on this platform'

        try:
            attr = termios.tcgetattr(self.rchild)
        except termios.error as err:
            if err.args[0] == errno.EINVAL:
                raise IOError(err.args[0], '%s: %s.' % (err.args[1], errmsg))
            raise

        if state:
            attr[3] = attr[3] | termios.ECHO
        else:
            attr[3] = attr[3] & ~termios.ECHO

        try:
            # I tried TCSADRAIN and TCSAFLUSH, but these were inconsistent and
            # blocked on some platforms. TCSADRAIN would probably be ideal.
            termios.tcsetattr(self.rchild, termios.TCSANOW, attr)
        except IOError as err:
            if err.args[0] == errno.EINVAL:
                raise IOError(err.args[0], '%s: %s.' % (err.args[1], errmsg))
            raise

        self.echo = state

    def sendintr(self):
        self.kill(signal.SIGINT)

    def kill(self, sig=None):
        if pty:
            if sig is None:
                sig = signal.SIGKILL
            try:
                self.proc.send_signal(sig)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    return 1
                else:
                    raise e
            if sig in [signal.SIGTERM, signal.SIGKILL]:
                time.sleep(self.delayafterclose)

        else:
            if sig is None:
                sig = signal.SIGTERM
            if sig == signal.SIGINT:
                os.kill(self.proc.pid, signal.CTRL_C_EVENT)
            elif sig in [signal.CTRL_C_EVENT, signal.CTRL_BREAK_EVENT]:
                os.kill(self.proc.pid, sig)
            else:
                self.proc.terminate()
                time.sleep(self.delayafterclose)

        return self.proc.poll()

    def terminate(self):
        self.kill(signal.SIGTERM)


PY3 = (sys.version_info[0] >= 3)

if PY3:
    def u(s):
        return s
else:
    def u(s):
        return s.decode('utf-8')

PYEXPECT_PROMPT = u('[PYEXPECT_PROMPT>')
PYEXPECT_CONTINUATION_PROMPT = u('[PYEXPECT_PROMPT+')


class REPLWrapper(object):

    """Wrapper for a REPL.

    :param cmd_or_spawn: This can either be an instance of :class:`pyexpect.spawn`
      in which a REPL has already been started, or a str command to start a new
      REPL process.
    :param str orig_prompt: The prompt to expect at first.
    :param str prompt_change: A command to change the prompt to something more
      unique. If this is ``None``, the prompt will not be changed. This will
      be formatted with the new and continuation prompts as positional
      parameters, so you can use ``{}`` style formatting to insert them into
      the command.
    :param str new_prompt: The more unique prompt to expect after the change.
    :param str prompt_cmd: Command to generate the prompt.
    :param str extra_init_cmd: Commands to do extra initialisation, such as
      disabling pagers.
    """

    def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
                 new_prompt=PYEXPECT_PROMPT,
                 continuation_prompt=PYEXPECT_CONTINUATION_PROMPT,
                 prompt_cmd=None,
                 echo=False,
                 extra_init_cmd=None):
        if isinstance(cmd_or_spawn, str):
            self.child = spawn(cmd_or_spawn)
        else:
            self.child = cmd_or_spawn

        self.prompt_cmd = prompt_cmd

        if not echo and self.child.isatty() and self.child.getecho():
            # Existing spawn instance has echo enabled, disable it
            # to prevent our input from being repeated to output.
            self.child.setecho(False)
            self.child.waitnoecho()

        self.echo = echo

        if prompt_change is None:
            self.prompt = orig_prompt
        elif not prompt_cmd:
            pc = prompt_change.format(new_prompt, continuation_prompt)
            self.set_prompt(orig_prompt, pc)
            new_prompt = re.escape(new_prompt)
            self.prompt = new_prompt

        self.continuation_prompt = re.escape(continuation_prompt)

        self._expect_prompt()

        if extra_init_cmd is not None:    
            self.run_command(extra_init_cmd)

    def set_prompt(self, orig_prompt, prompt_change):
        self.child.expect(orig_prompt)
        self.child.sendline(prompt_change)

    def _expect_prompt(self, timeout=-1):
        if self.prompt_cmd:
            self.child.sendline(self.prompt_cmd)

        return self.child.expect([self.prompt, self.continuation_prompt],
                                 timeout=timeout)

    def run_command(self, command, timeout=-1):
        """Send a command to the REPL, wait for and return output.

        :param str command: The command to send. Trailing newlines are not needed.
          This should be a complete block of input that will trigger execution;
          if a continuation prompt is found after sending input, :exc:`ValueError`
          will be raised.
        :param int timeout: How long to wait for the next prompt. -1 means the
          default from the :class:`pyexpect.spawn` object (default 30 seconds).
          None means to wait indefinitely.
        """
        # Split up multiline commands and feed them in bit-by-bit
        cmdlines = command.splitlines()
        # splitlines ignores trailing newlines - add it back in manually
        if command.endswith('\n'):
            cmdlines.append('')
        if not cmdlines:
            raise ValueError("No command was given")

        self.child.sendline(cmdlines[0])
        if self.echo:
            self.child.expect(cmdlines[0])
        for line in cmdlines[1:]:
            self._expect_prompt(timeout=1)
            self.child.sendline(line)
            if self.echo:
                self.child.expect(line)

        # Command was fully submitted, now wait for the next prompt
        if self._expect_prompt(timeout=timeout) == 1:
            # We got the continuation prompt - command was incomplete
            self.child.kill(signal.SIGINT)
            self._expect_prompt(timeout=1)
            msg = "Continuation prompt found - input was incomplete:\n"
            raise ValueError(msg + command)
        return self.child.before


def bash(command="bash -i", orig_prompt=re.compile('[$#]')):
    """Start a bash shell and return a :class:`REPLWrapper` object."""
    if os.name == 'nt':
        command = command.replace('-i', '')
        orig_prompt = '__repl_ready__'
        prompt_cmd = 'echo "__repl_""ready__"'
        prompt_change = None

    else:
        prompt_change = u("PS1='{0}' PS2='{1}' PROMPT_COMMAND=''")
        prompt_cmd = None

    extra_init_cmd = "export PAGER=cat"

    return REPLWrapper(command, orig_prompt, prompt_change,
                       prompt_cmd=prompt_cmd, extra_init_cmd=extra_init_cmd)


def cmd(command='cmd', prompt=re.compile(r'[A-Z]:\\.*>')):
    """"Start a cmd shell and return a :class:`REPLWrapper` object."""
    if not os.name == 'nt':
        raise OSError('cmd only available on Windows')
    return REPLWrapper(command, prompt, None, echo=True)


def python(command="python"):
    """Start a Python shell and return a :class:`REPLWrapper` object."""
    if os.name == 'nt':
        raise OSError('Cannot spawn a Python process on Windows')
    prompt_change = u("import sys; sys.ps1={0!r}; sys.ps2={1!r}")
    return REPLWrapper(command, u(">>> "), prompt_change)
