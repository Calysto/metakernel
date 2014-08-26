# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import subprocess

class ShellMagic(Magic):

    def line_shell(self, args):
        """%shell COMMAND - run the line as a shell command"""
        try:
            process = subprocess.Popen(args, shell=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            retval, error = process.communicate()
            if error:
                self.kernel.Error(error)
        except Exception as e:
            self.kernel.Error(e.message)
            retval = None
        if retval:
            self.kernel.Print(retval)

    def cell_shell(self, args):
        """%%shell - run the contents of the cell as shell commands"""
        self.line_shell(self.code)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(ShellMagic)
