# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import os

class CDMagic(Magic):

    def line_cd(self, args):
        """%cd PATH - change current directory of session"""
        try:
            os.chdir(args)
            retval = os.path.abspath(args)
        except Exception as e:
            self.kernel.Error(e.message)
            retval = None
        if retval:
            self.kernel.Print(retval)


def register_magics(kernel):
   kernel.register_magics(CDMagic)
