# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
from IPython.display import Javascript

class JavascriptMagic(Magic):
    def line_javascript(self, args):
        """%javascript CODE - send code as JavaScript"""
        jscode = Javascript(args)
        self.kernel.Display(jscode)

    def cell_javascript(self, args):
        """%%javascript - send contents of cell as JavaScript"""
        if self.code.strip():
            jscode = Javascript(self.code)
            self.kernel.Display(jscode)
            self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(JavascriptMagic)

