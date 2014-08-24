# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic
import os

class CDMagic(Magic):
    name = "cd"
    help_lines = [" %cd PATH - change current directory of session"]

    def line(self, args):
        try:
            os.chdir(args)
            retval = os.path.abspath(args)
        except Exception as e:
            self.kernel.Error(e.message)
            retval = None
        if retval:
            self.kernel.Print(retval)

def register_magics(magics):
    magics[CDMagic.name] = CDMagic
    

