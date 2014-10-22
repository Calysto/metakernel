# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic
import subprocess
import os
import atexit
import threading
import time
try:
    import Queue
except ImportError:
    import queue as Queue


class ShellMagic(Magic):

    def __init__(self, kernel):
        super(ShellMagic, self).__init__(kernel)
        self.proc = None
        self.start_process()

    def line_shell(self, *args):
        """
        %shell COMMAND - run the line as a shell command

        This line command will run the COMMAND in the bash shell.

        Examples:
            %shell ls -al
            %shell cd

         Note: this is a persistent connection to a shell.
         The working directory is synchronized to that of the notebook
         before and after each call.

        You can also use "!" instead of "%shell".

        """
        # get in sync with the cwd
        self.eval('cd %s' % os.getcwd())

        command = " ".join(args)
        resp, error = self.eval(command)

        if self.cmd == 'cmd':
            cwd, _ = self.eval('cd')
        else:
            cwd, _ = self.eval('pwd')

        if os.path.exists(cwd):
            os.chdir(cwd)

        if error:
            self.kernel.Error(error)

        if resp:
            self.kernel.Print(resp)

    def eval(self, cmd):
        cmd = cmd.strip().replace('\n', self.separator)
        cmd += self.separator
        cmd += 'echo "__eval_complete__"\n'

        os.write(self.wfid, cmd.encode('utf-8'))

        buf = ''

        try:
            while not '__eval_complete__' in buf:
                buf += os.read(self.rfid, 1024).decode('utf-8', 'replace')
        except KeyboardInterrupt:
            self.start_process()
            return '', 'Interrupted, restarting shell'
        buf = buf[:buf.index('__eval_complete__')]

        if buf.endswith('"'):
            buf = buf[:-1]

        resp = buf.rstrip()

        try:
            error = self._error_queue.get_nowait()
        except Queue.Empty:
            error = ''

        return resp, error

    def _read_errors(self):
        buf = os.read(self.efid, 1024).decode('utf-8', 'replace')
        self._error_queue.put(buf)
        time.sleep(0.01)

    def start_process(self):
        if not self.proc is None:
            self.proc.terminate()

        try:
            subprocess.check_output('bash --version', shell=True)
        except OSError as e:
            if os.name == 'nt':
                self.cmd = 'cmd'
                self.separator = ' & '
            else:
                raise OSError(e)
        else:
            self.cmd = 'bash'
            self.separator = ';'

        self.rfid, wpipe = os.pipe()
        rpipe, self.wfid = os.pipe()
        self.efid, epipe = os.pipe()

        kwargs = dict(bufsize=0, stdin=rpipe,
                      stderr=epipe, stdout=wpipe)

        self.proc = subprocess.Popen(self.cmd, **kwargs)

        atexit.register(self.proc.terminate)

        self._error_thread = threading.Thread(target=self._read_errors)
        self._error_queue = Queue.Queue()
        self._error_thread.setDaemon(True)
        self._error_thread.start()

    def cell_shell(self):
        """
        %%shell - run the contents of the cell as shell commands

        This shell command will run the cell contents in the bash shell.

        Example:
            %%shell
               cd ..
               ls -al

       Note: this is a persistent connection to a shell.
         The working directory is synchronized to that of the notebook
         before and after each call.

        You can also use "!!" instead of "%%shell".
        """
        self.line_shell(self.code)
        self.evaluate = False

    def get_completions(self, info):
        if self.cmd == 'cmd':
            return []
        cmd = 'compgen -cdfa "%s"' % info['magic']['args']
        completion_text, error = self.eval(cmd)
        return completion_text.split()

    def get_help_on(self, info, level=0):
        expr = info['rest'].rstrip()
        if self.cmd == 'cmd':
            resp, error = self.eval('help %s' % expr)
        elif level == 0:
            resp, error = self.eval('%s --help' % expr)
        else:
            resp, error = self.eval('man %s' % expr)
        if resp:
            return resp
        else:
            return "Sorry, no help is available on '%s'." % expr

    def __del__(self):
        self.proc.terminate()


def register_magics(kernel):
    kernel.register_magics(ShellMagic)
