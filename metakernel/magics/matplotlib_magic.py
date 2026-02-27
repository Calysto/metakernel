# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, MetaKernel


class MatplotlibMagic(Magic):
    """
    Magic for using matplotlib with kernels other than ipython.
    """

    def line_matplotlib(self, backend: str) -> None:
        """
        %matplotlib BACKEND - set the matplotlib backend to BACKEND

        This line magic will set (and reload) the items associated
        with the matplotlib backend.

        Also, monkeypatches the IPython.display.display
        to work with metakernel-based kernels.

        Example:
            %matplotlib notebook

            import matplotlib.pyplot as plt
            plt.plot([3, 8, 2, 5, 1])
            plt.show()
        """
        import importlib

        import IPython.display

        import metakernel.display

        # Monkeypatch IPython.display.display:
        IPython.display.display = metakernel.display.display

        import matplotlib

        importlib.reload(matplotlib)

        if backend == "notebook":
            backend = "nbagg"

        matplotlib.use(backend)

        import matplotlib.backends.backend_nbagg

        importlib.reload(matplotlib.backends.backend_nbagg)

        import matplotlib.backends.backend_webagg_core

        importlib.reload(matplotlib.backends.backend_webagg_core)


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(MatplotlibMagic)
