# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic
from IPython.display import HTML



class ProcessingMagic(Magic):
    canvas_id = 0

    def cell_processing(self, dummy=None):
        """
        %%processing - run the cell in the language Processing

        This cell magic will execute the contents of the cell as a
        Processing program. This uses the Java-based Processing
        language.
        
        Example:

            %%processing
            setup() {
            }
            draw() {
            }
        """
        self.canvas_id += 1
        """%%processing - run contents of cell as a Processing script"""

        repr_code = repr(self.code)
        if repr_code.startswith('u'):
            repr_code = repr_code[1:]

        env = {"code": repr_code,
               "id": self.canvas_id}
        code = """
<canvas id="canvas_%(id)s"></canvas>
<script>
require([window.location.protocol + "//calysto.github.io/javascripts/processing/processing.js"], function () {
    var processingCode = %(code)s;
    var cc = Processing.compile(processingCode);
    var processingInstance = new Processing("canvas_%(id)s", cc);
});
</script>
""" % env
        html = HTML(code)
        self.kernel.Display(html)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(ProcessingMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_cell_magic
    kernel = IPythonKernel()
    magic = ProcessingMagic(kernel)

    @register_cell_magic
    def processing(line, cell):
        """
        """
        magic.code = cell
        magic.cell_processing()
