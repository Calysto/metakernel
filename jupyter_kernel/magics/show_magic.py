# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option
import os

class ShowMagic(Magic):

    def cell_show(self):
        """
        %%show - load cell contents into system pager

        This cell magic will put the contents the cell into
        the system pager.

        Example:
            %%show

            This information will appear in the pager.
        """
        self.kernel.payload = [{"data": {"text/plain": self.code},
                                "start_line_number": 0,
                                "source": "page"}]
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(ShowMagic)

