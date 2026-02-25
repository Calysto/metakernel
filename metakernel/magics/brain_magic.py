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


def register_magics(kernel) -> None:
    kernel.register_magics(BrainMagic)


def register_ipython_magics() -> None:
    from IPython.core.magic import register_cell_magic

    from metakernel import IPythonKernel

    kernel = IPythonKernel()
    magic = BrainMagic(kernel)

    @register_cell_magic
    def brain(line, cell):
        from IPython import get_ipython  # type:ignore[attr-defined]

        ipkernel = get_ipython()
        magic.code = cell
        magic.cell_brain()
        ipkernel.kernel.do_execute(magic.code, silent=True)
