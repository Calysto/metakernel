# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from metakernel import Magic, pexpect
from metakernel.replwrap import cmd, bash
import os


class ShellMagic(Magic):

    def __init__(self, kernel):
        super(ShellMagic, self).__init__(kernel)
        self.repl = None
        self.cmd = None
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
        resp = self.eval(command)

        if self.cmd == 'cmd':
            cwd = self.eval('cd')
        else:
            cwd = self.eval('pwd')

        if os.path.exists(cwd):
            os.chdir(cwd)

        if resp:
            self.kernel.Print(resp)

    def eval(self, cmd):
        return self.repl.run_command(cmd)

    def start_process(self):
        if not self.repl is None:
            self.repl.child.terminate()

        if not self.cmd:
            try:
                pexpect.which('bash')
            except Exception as e:  # pragma: no cover

                if os.name == 'nt':
                    self.cmd = 'cmd'
                else:
                    raise(e)
            else:
                self.cmd = 'bash'

        if self.cmd == 'cmd':
            self.repl = cmd()
        else:
            self.repl = bash()

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
        command = 'compgen -cdfa "%s"' % info['code']
        completion_text = self.eval(command)
        return completion_text.split()

    def get_help_on(self, info, level=0):
        expr = info['code'].rstrip()
        if self.cmd == 'cmd':
            resp = self.eval('help %s' % expr)
        elif level == 0:
            resp = self.eval('%s --help' % expr)
        else:
            resp = self.eval('man %s' % expr)
        if resp and not ': command not found' in resp:
            return resp
        else:
            return "Sorry, no help is available on '%s'." % expr


def register_magics(kernel):
    kernel.register_magics(ShellMagic)
