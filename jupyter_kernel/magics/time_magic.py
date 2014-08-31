# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import time

class TimeMagic(Magic):

    def cell_time(self):
        """%%time - show time to run cell"""
        self.start = time.time()

    def line_time(self, comand):
        """%time COMMAND - show time to run line"""
        self.start = time.time()

    def post_process(self, retval):
        if self.code.strip():
            result = "Time: %s seconds.\n" % (time.time() - self.start)
            self.kernel.Print(result)
        return retval


def register_magics(kernel):
    kernel.register_magics(TimeMagic)
