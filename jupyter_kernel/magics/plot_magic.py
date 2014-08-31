# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option


class PlotMagic(Magic):

    @option(
        '-s', '--size', action='store',
        help='Pixel size of plots, "width,height"'
    )
    @option(
        '-f', '--format', action='store', default='png',
        help='Plot format (png, svg or jpg).'
    )
    def line_plot(self, backend, size=None, format=None):
        """%plot [options] backend - configure plotting for the session.
        """
        self.kernel.update_plot_settings(backend.lower(), size, format)
        self.kernel.handle_plot_settings()

def register_magics(kernel):
    kernel.register_magics(PlotMagic)
