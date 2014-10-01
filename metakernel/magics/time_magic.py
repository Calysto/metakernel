# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic
import time

class TimeMagic(Magic):

    def cell_time(self):
        """
        %%time - show time to run cell

        Put this magic at the top of a cell and the amount of time
        taken to execute the code will be displayed before the output.

        Example:
            %%time
            [code for your language goes here!]

        This just reports real time taken to execute a program. This
        may fluctuate with number of users, system, load, etc.
        """
        self.start = time.time()

    def post_process(self, retval):
        if self.code.strip():
            result = "Time: %s seconds.\n" % (time.time() - self.start)
            self.kernel.Print(result)
        return retval


def register_magics(kernel):
    kernel.register_magics(TimeMagic)
