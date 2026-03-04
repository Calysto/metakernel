# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

from typing import Any

from IPython.display import HTML

from metakernel import Magic


class ProcessingMagic(Magic):
    canvas_id = 0

    def cell_processing(self, dummy: str | None = None) -> None:
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
        if repr_code.startswith("u"):
            repr_code = repr_code[1:]

        env = {"code": repr_code, "id": self.canvas_id}
        code = """
<canvas id="canvas_{id}"></canvas>
<script>
require([window.location.protocol + "//calysto.github.io/javascripts/processing/processing.js"], function () {{
    var processingCode = {code};
    var cc = Processing.compile(processingCode);
    var processingInstance = new Processing("canvas_{id}", cc);
}});
</script>
""".format(**env)
        html = HTML(code)  # type: ignore[no-untyped-call]
        self.kernel.Display(html)
        self.evaluate = False


def register_magics(kernel: Any) -> None:
    kernel.register_magics(ProcessingMagic)


def register_ipython_magics() -> None:
    from IPython.core.magic import register_cell_magic

    from metakernel import IPythonKernel

    kernel = IPythonKernel()
    magic = ProcessingMagic(kernel)

    @register_cell_magic  # type: ignore[untyped-decorator]
    def processing(line: str, cell: str) -> None:
        """ """
        magic.code = cell
        magic.cell_processing()
