# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option


class PlotMagic(Magic):

    @option(
        '-s', '--size', action='store',
        help='Pixel size of plots, "width,height"'
    )
    @option(
        '-f', '--format', action='store',
        help='Plot format (png, svg or jpg).'
    )
    @option(
        '-b', '--backend', action='store', default='inline',
        help='Backend selection'
    )
    @option(
        '-r', '--resolution', action='store',
        help='Resolution in pixels per inch'
    )
    @option(
        '-w', '--width', action='store',
        help='Plot width in pixels'
    )
    @option(
        '-h', '--height', action='store',
        help='Plot height in pixels'
    )
    def line_plot(self, *args, **kwargs):
        """
        %plot [options] backend - configure plotting for the session.

        This line magic will configure the plot settings for this
        language.

        Examples:
            %plot qt --format=png
            %plot inline -w 640

        Note: not all languages may support the %plot magic, and not all
        options may be supported.
        """
        if args and not args[0].startswith('-'):
            kwargs['backend'] = args[0]
        if 'size' in kwargs and kwargs['size'] is not None:
            width, height = kwargs['size']
            kwargs['width'] = int(width)
            kwargs['height'] = int(height)
        # Remove empty options so ".setdefault" will work.
        for key in ['resolution', 'format', 'size', 'width', 'height']:
            if key in kwargs and kwargs[key] is None:
                del kwargs[key]
        self.kernel.plot_settings = kwargs
        self.kernel.handle_plot_settings()


def register_magics(kernel):
    kernel.register_magics(PlotMagic)
