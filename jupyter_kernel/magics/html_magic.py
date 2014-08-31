# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
from IPython.display import HTML

class HTMLMagic(Magic):

    def line_html(self, code, *args, **kwargs):
        """%html CODE - display code as HTML"""
        html = HTML(code)
        self.kernel.Display(html)

    def cell_html(self, *args, **kwargs):
        """%%html - display contents of cell as HTML"""
        html = HTML(self.code)
        self.kernel.Display(html)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(HTMLMagic)
