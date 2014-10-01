# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic
from IPython.display import Javascript

class JavascriptMagic(Magic):
    def line_javascript(self, code):
        """
        %javascript CODE - send code as JavaScript

        This line magic will execute the CODE on the line as
        JavaScript in the browser.

        Example:
            %javascript console.log("Print in the browser console")

        """
        jscode = Javascript(code)
        self.kernel.Display(jscode)

    def cell_javascript(self):
        """
        %%javascript - send contents of cell as JavaScript

        This cell magic will execute the contents of the cell as
        JavaScript in the browser.

        Example:
            %%javascript

            element.html("Hello this is <b>bold</b>!")

        """
        if self.code.strip():
            jscode = Javascript(self.code)
            self.kernel.Display(jscode)
            self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(JavascriptMagic)

