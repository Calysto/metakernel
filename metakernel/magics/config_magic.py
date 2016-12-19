# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic, option


class ConfigMagic(Magic):

    @option(
        '-t', '--timeout', action='store', default=-1
        help='"Timeout for execution calls, in seconds.  Use -1 for no timeout"'
    )
    def cell_config(self, timeout=-1):
        """
        %%config -t TIMEOUT - change timeout duration

        This line magic is used to change the configuration of the kernel
        itself.

        The timeout pa

        Example:
            %%config -t 10
        """
        config = dict(timeout=int(timeout))
        self.kernel.config = config


def register_magics(kernel):
    kernel.register_magics(ConfigMagic)
