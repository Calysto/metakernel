# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option

class MatplotlibMagic(Magic):
    """
    Magic for using matplotlib with kernels other than ipython.
    """
    def line_matplotlib(self, backend):
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
        import IPython.display
        import metakernel.display
        import imp

        # Monkeypatch IPython.display.display:
        IPython.display.display = metakernel.display.display

        import matplotlib
        imp.reload(matplotlib)

        if backend == "notebook":
            backend = "nbagg"

        matplotlib.use(backend)

        import matplotlib.backends.backend_nbagg
        imp.reload(matplotlib.backends.backend_nbagg)

        import matplotlib.backends.backend_webagg_core
        imp.reload(matplotlib.backends.backend_webagg_core)

def register_magics(kernel):
    kernel.register_magics(MatplotlibMagic)
