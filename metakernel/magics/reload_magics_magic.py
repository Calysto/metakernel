# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic

class ReloadMagicsMagic(Magic):

    def line_reload_magics(self):
        """
        %reload_magics - reload the magics from the installed files

        Example:
            %reload_magics

        This line magic will reload the magics installed in the
        system, and in your private magic folder.

        You only need to do this if you edit a magic file. It runs
        automatically if you install a new magic.
        """
        self.kernel.reload_magics()
        self.code = "%lsmagic\n" + self.code

def register_magics(kernel):
    kernel.register_magics(ReloadMagicsMagic)
