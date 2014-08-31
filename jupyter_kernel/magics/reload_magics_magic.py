# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic

class ReloadMagicsMagic(Magic):

    def line_reload_magics(self):
        """%reload_magics - reload the magics from the installed files"""
        self.kernel.reload_magics()
        self.code += "%lsmagic\n" + self.code

def register_magics(kernel):
    kernel.register_magics(ReloadMagicsMagic)
