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

        env = {"code": repr(self.code)[1:],
               "id": self.canvas_id}
        code = """
<canvas id="canvas_%(id)s"></canvas>
<script>
require(["http://cs.brynmawr.edu/gxk2013/examples/tools/alphaChannels/processing.js"], function () {
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
