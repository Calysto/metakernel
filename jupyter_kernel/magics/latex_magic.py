# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
from IPython.display import Latex

class LatexMagic(Magic):

    def line_latex(self, args):
        """%latex TEXT - display text as LaTeX"""
        latex = Latex(args)
        self.kernel.Display(latex)

    def cell_latex(self, args):
        """%%latex - display contents of cell as LaTeX"""
        latex = Latex(self.code)
        self.kernel.Display(latex)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(LatexMagic)
