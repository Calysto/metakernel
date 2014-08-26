# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
from IPython.display import HTML

class HTMLMagic(Magic):

    def line_html(self, args):
        """%html CODE - display code as HTML"""
        html = HTML(args)
        self.kernel.Display(html)

    def cell_html(self, args):
        """%%html - display contents of cell as HTML"""
        html = HTML(self.code)
        self.kernel.Display(html)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(HTMLMagic)
