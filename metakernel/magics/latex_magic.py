# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from IPython.display import Latex

from metakernel import Magic, MetaKernel


class LatexMagic(Magic):
    def line_latex(self, text: str) -> None:
        r"""
        %latex TEXT - display text as LaTeX

        This line magic will display the TEXT on the line as LaTeX.

        Example:
            %latex $x_1 = \dfrac{a}{b}$

        """
        latex = Latex(text)  # type: ignore[no-untyped-call]
        self.kernel.Display(latex)

    def cell_latex(self) -> None:
        r"""
        %%latex - display contents of cell as LaTeX

        This cell magic will display the TEXT in the cell as LaTeX.

        Example:
            %%latex
            $x_1 = \dfrac{a}{b}$

            $x_2 = a^{n - 1}$
        """
        latex = Latex(self.code)  # type: ignore[no-untyped-call]
        self.kernel.Display(latex)
        self.evaluate = False


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(LatexMagic)
