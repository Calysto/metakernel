# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic

class ReloadMagicsMagic(Magic):
    name = "reload_magics"
    help_lines = [" %reload_magics - reload the magics from the installed files"]

    def post_process(self, retval):
        self.kernel.reload_magics()
        result = "Magics reloaded: %s\n" % ", ".join(self.kernel.magics.keys())
        self.kernel.Print(result)
        return retval

def register_magics(magics):
    magics[ReloadMagicsMagic.name] = ReloadMagicsMagic
    
