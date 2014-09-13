# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic


class RestartMagic(Magic):

    def line_restart(self):
        """
        %restart - restart session

        This line magic will restart the connection to the language
        kernel.

        Example:
            %restart

        Note that you will lose all computed values.
        """
        self.kernel.do_shutdown(True)


def register_magics(kernel):
    kernel.register_magics(RestartMagic)
