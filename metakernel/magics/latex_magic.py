# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic
from IPython.display import Latex

class LatexMagic(Magic):

    def line_latex(self, text):
        """
        %latex TEXT - display text as LaTeX

        This line magic will display the TEXT on the line as LaTeX.

        Example:
            %latex x_1 = \dfrac{a}{b}

        """
        latex = Latex(text)
        self.kernel.Display(latex)

    def cell_latex(self):
        """
        %%latex - display contents of cell as LaTeX

        This cell magic will display the TEXT in the cell as LaTeX.

        Example:
            %%latex 
            x_1 = \dfrac{a}{b}

            x_2 = a^{n - 1}
        """
        latex = Latex(self.code)
        self.kernel.Display(latex)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(LatexMagic)
