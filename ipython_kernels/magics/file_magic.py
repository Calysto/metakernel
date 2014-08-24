# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic
import os

class FileMagic(Magic):
    name = "file"
    help_lines = ["%%file FILENAME - write contents of cell to file"]

    def cell(self, args):
        message = "Created file '%s'." % args
        if os.path.isfile(args):
            message = "Overwrote file '%s'." % args
        try:
            fp = open(args, "w")
            fp.write(self.code)
            fp.close()
            self.kernel.Print(message)
        except Exception as e:
            self.kernel.Error(e.message)
        self.evaluate = False

def register_magics(magics):
    magics[FileMagic.name] = FileMagic
    
