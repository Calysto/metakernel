# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import os

class FileMagic(Magic):

    def cell_file(self, filename):
        """%%file FILENAME - write contents of cell to file"""
        message = "Created file '%s'." % filename
        if os.path.isfile(self.code):
            message = "Overwrote file '%s'." % filename
        try:
            fp = open(filename, "w")
            fp.write(self.code)
            fp.close()
            self.kernel.Print(message)
        except Exception as e:
            self.kernel.Error(e.message)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(FileMagic)
