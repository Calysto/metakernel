# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic
from IPython.display import HTML

class DotMagic(Magic):

    def line_dot(self, code):
        """
        %dot CODE - render code as Graphviz image

        This line magic will render the Graphiz CODE, and render 
        it as an image.

        Example:
            %dot graph A { a->b };

        """
        try:
            import pydot
        except:
            raise Exception("You need to install pydot")
        graph = pydot.graph_from_dot_data(str(code))
        svg = graph.create_svg()
        if hasattr(svg, "decode"):
            svg = svg.decode("utf-8")
        html = HTML(svg)
        self.kernel.Display(html)

    def cell_dot(self):
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
        except:
            raise Exception("You need to install pydot")
        graph = pydot.graph_from_dot_data(str(self.code))
        svg = graph.create_svg()
        if hasattr(svg, "decode"):
            svg = svg.decode("utf-8")
        html = HTML(svg)
        self.kernel.Display(html)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(DotMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_cell_magic
    kernel = IPythonKernel()
    magic = DotMagic(kernel)

    @register_cell_magic
    def dot(line, cell):
        """
        %%dot - evaluate cell contents as a dot diagram.
        """
        magic.code = cell
        magic.cell_dot()
