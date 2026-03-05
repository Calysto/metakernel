from metakernel import Magic, MetaKernel, get_ipython


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


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(BrainMagic)


def register_ipython_magics() -> None:
    from metakernel import IPythonKernel
    from metakernel.magic import register_cell_magic

    kernel = IPythonKernel()
    magic = BrainMagic(kernel)

    @register_cell_magic
    def brain(line: str, cell: str) -> None:
        ipkernel = get_ipython()
        if ipkernel is None:
            return
        magic.code = cell
        magic.cell_brain()
        ipkernel.kernel.do_execute(magic.code, silent=True)  # type: ignore[attr-defined]
