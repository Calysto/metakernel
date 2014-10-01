# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option


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
        """
        %plot [options] backend - configure plotting for the session.

        This line magic will configure the plot settings for this
        language.

        Examples:
            %plot --format=png matplotlib
            %plot -s 640,480 matplotlib

        Note: not all languages may support the %plot magic.
        """
        self.kernel.update_plot_settings(backend.lower(), size, format)
        self.kernel.handle_plot_settings()

def register_magics(kernel):
    kernel.register_magics(PlotMagic)
