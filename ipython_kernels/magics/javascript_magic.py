# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic
from IPython.display import Javascript

class JavascriptMagic(Magic):
    name = "javascript"
    help_lines = [" %javascript CODE - send code as JavaScript",
                  "%%javascript - send contents of cell as JavaScript"]

    def line(self, args):
        jscode = Javascript(args)
        self.kernel.Display(jscode)

    def cell(self, args):
        if self.code.strip():
            jscode = Javascript(self.code)
            self.kernel.Display(jscode)
            self.evaluate = False

def register_magics(magics):
    magics[JavascriptMagic.name] = JavascriptMagic
    
