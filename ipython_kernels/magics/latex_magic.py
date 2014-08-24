# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic
from IPython.display import Latex

class LatexMagic(Magic):
    name = "latex"
    help_lines = ["%%latex - display contents of cell as LaTeX",
                  " %latex TEXT - display text as LaTex"]

    def line(self, args):
        latex = Latex(args)
        self.kernel.Display(latex)

    def cell(self, args):
        latex = Latex(self.code)
        self.kernel.Display(latex)
        self.evaluate = False

def register_magics(magics):
    magics[LatexMagic.name] = LatexMagic
    
