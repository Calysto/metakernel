# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic
import time

class TimeMagic(Magic):
    name = "time"
    help_lines = [" %time COMMAND - show time to run line",
                  "%%time - show time to run cell"]

    def cell(self, args):
        self.start = time.time()

    def line(self, args):
        self.start = time.time()

    def post_process(self, retval):
        if self.code.strip():
            result = "Time: %s seconds.\n" % (time.time() - self.start)
            self.kernel.Print(result)
        return retval

def register_magics(magics):
    magics[TimeMagic.name] = TimeMagic
    
