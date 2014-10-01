# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic
from IPython.display import HTML

class HTMLMagic(Magic):

    def line_html(self, code):
        """
        %html CODE - display code as HTML

        This line magic will send the CODE to the browser as
        HTML.

        Example:
            %html <u>This is underlined!</u>

        """
        html = HTML(code)
        self.kernel.Display(html)

    def cell_html(self):
        """
        %%html - display contents of cell as HTML

        This cell magic will send the cell to the browser as
        HTML.

        Example:
            %%html 
    
            <script src="..."></script>

            <div>Contents of div tag</div>
        """
        html = HTML(self.code)
        self.kernel.Display(html)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(HTMLMagic)
