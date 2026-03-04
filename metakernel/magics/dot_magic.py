# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

from typing import Any

from IPython.display import HTML

from metakernel import Magic


class DotMagic(Magic):
    def line_dot(self, code: str) -> None:
        """
        %dot CODE - render code as Graphviz image

        This line magic will render the Graphiz CODE, and render
        it as an image.

        Example:
            %dot graph A { a->b };

        """
        try:
            import pydot
        except ImportError:
            raise Exception("You need to install pydot") from None
        graph_result: Any = pydot.graph_from_dot_data(str(code))
        if isinstance(graph_result, list):
            graph_result = graph_result[0]
        svg = graph_result.create_svg()
        if hasattr(svg, "decode"):
            svg = svg.decode("utf-8")
        html = HTML(svg)  # type: ignore[no-untyped-call]
        self.kernel.Display(html)

    def cell_dot(self) -> None:
        """
        %%dot - render contents of cell as Graphviz image

        This cell magic will send the cell to the browser as
        HTML.

        Example:
            %%dot

            graph A { a->b };
        """
        try:
            import pydot
        except ImportError:
            raise Exception("You need to install pydot") from None
        graph_result: Any = pydot.graph_from_dot_data(str(self.code))
        if isinstance(graph_result, list):
            graph_result = graph_result[0]
        svg = graph_result.create_svg()
        if hasattr(svg, "decode"):
            svg = svg.decode("utf-8")
        html = HTML(svg)  # type: ignore[no-untyped-call]
        self.kernel.Display(html)
        self.evaluate = False


def register_magics(kernel: Any) -> None:
    kernel.register_magics(DotMagic)


def register_ipython_magics() -> None:
    from IPython.core.magic import register_cell_magic

    from metakernel import IPythonKernel

    kernel = IPythonKernel()
    magic = DotMagic(kernel)

    @register_cell_magic  # type: ignore[untyped-decorator]
    def dot(line: str, cell: str) -> None:
        """
        %%dot - evaluate cell contents as a dot diagram.
        """
        magic.code = cell
        magic.cell_dot()
