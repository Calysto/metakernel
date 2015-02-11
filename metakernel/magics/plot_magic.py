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
    @option(
        '-b', '--backend', action='store', default='inline',
        help='Backend selection'
    )
    @option(
        '-r', '--resolution', action='store', default=96,
        help='Resolution in pixels per inch'
    )
    def line_plot(self, *args, **kwargs):
        """
        %plot [options] backend - configure plotting for the session.

        This line magic will configure the plot settings for this
        language.

        Examples:
            %plot qt --format=png
            %plot inline -s 640,480

        Note: not all languages may support the %plot magic, and not all
        options may be supported.
        """
        if args:
            kwargs['backend'] = args[0]
        self.kernel.plot_settings.update(**kwargs)
        self.kernel.handle_plot_settings()


def register_magics(kernel):
    kernel.register_magics(PlotMagic)
