# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option

class RunMagic(Magic):

    def line_run(self, filename):
        """%run FILENAME - run code in filename by kernel"""
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        self.kernel.do_execute_file(filename)

def register_magics(kernel):
    kernel.register_magics(RunMagic)

