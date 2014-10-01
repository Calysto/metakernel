# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import os

class ShowMagic(Magic):

    @option(
        '-o', '--output', action='store_true', default=False,
        help='rather than showing the contents, show the results'
    )
    def cell_show(self, output=False):
        """
        %%show [-o]- show cell contents or results in system pager

        This cell magic will put the contents or results of the cell
        into the system pager.

        Examples:
            %%show
            This information will appear in the pager.

            %%show --output
            retval = 54 * 54
        """
        self.show_output = output
        if not output: # show contents
            self.kernel.payload = [{"data": {"text/plain": self.code},
                                    "start_line_number": 0,
                                    "source": "page"}]
            self.evaluate = False
        else:
            self.evaluate = True

    def post_process(self, results):
        if self.show_output:
            self.kernel.payload = [{"data": {"text/plain": self.kernel.repr(results)},
                                    "start_line_number": 0,
                                    "source": "page"}]
        return None

def register_magics(kernel):
    kernel.register_magics(ShowMagic)

