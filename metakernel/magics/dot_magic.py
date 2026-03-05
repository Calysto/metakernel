# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from IPython.display import HTML

from metakernel import Magic, MetaKernel


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
        graph = pydot.graph_from_dot_data(str(code))
        if not graph:
            return
        svg = graph[0].create_svg()  # type: ignore[attr-defined, unused-ignore]
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
        graph = pydot.graph_from_dot_data(str(self.code))
        if not graph:
            return
        svg = graph[0].create_svg()  # type: ignore[attr-defined, unused-ignore]
        if hasattr(svg, "decode"):
            svg = svg.decode("utf-8")
        html = HTML(svg)  # type: ignore[no-untyped-call]
        self.kernel.Display(html)
        self.evaluate = False


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(DotMagic)


def register_ipython_magics() -> None:
    from metakernel import IPythonKernel
    from metakernel.magic import register_cell_magic

    kernel = IPythonKernel()
    magic = DotMagic(kernel)

    @register_cell_magic
    def dot(line: str, cell: str) -> None:
        """
        %%dot - evaluate cell contents as a dot diagram.
        """
        magic.code = cell
        magic.cell_dot()
