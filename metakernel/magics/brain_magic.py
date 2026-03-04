from __future__ import annotations

from typing import Any

from metakernel import Magic


class BrainMagic(Magic):
    def cell_brain(self) -> None:
        """
        %%brain - run a cell as brain control code
        for a calysto.simulation.

        Requires calysto.

        Examples:
           %%brain
           robot.forward(1)
        """
        text = self.code
        pre_code = """
from calysto.simulation import *
robot = get_robot()
def brain():
"""
        post_code = """robot.brain = brain"""
        new_code = "    ".join(line + "\n" for line in text.split("\n"))
        self.code = pre_code + new_code + post_code


def register_magics(kernel: Any) -> None:
    kernel.register_magics(BrainMagic)


def register_ipython_magics() -> None:
    from IPython.core.magic import register_cell_magic

    from metakernel import IPythonKernel

    kernel = IPythonKernel()
    magic = BrainMagic(kernel)

    @register_cell_magic  # type: ignore[untyped-decorator]
    def brain(line: str, cell: str) -> None:
        from IPython import get_ipython  # type:ignore[attr-defined]

        ipkernel = get_ipython()  # type: ignore[no-untyped-call]
        magic.code = cell
        magic.cell_brain()
        ipkernel.kernel.do_execute(magic.code, silent=True)
