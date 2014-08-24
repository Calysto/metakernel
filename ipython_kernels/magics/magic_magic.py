# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic

class MagicMagic(Magic):
    name = "magic"
    help_lines = [" %magic - show installed magics"]

    def line(self, args):
        retval = []
        for magic in self.kernel.magics:
            retval.extend(self.kernel.magics[magic].help_lines)
        self.kernel.Print("Line magics:")
        self.kernel.Print("    " + ("\n    ".join(sorted([line for line in retval if line.startswith(" ")]))))
        self.kernel.Print("")
        self.kernel.Print("Cell magics:")
        self.kernel.Print("    " + ("\n    ".join(sorted([line for line in retval if line.startswith("%")]))))
        self.kernel.Print("")
        self.kernel.Print("Shell shortcut:")
        self.kernel.Print("    ! COMMAND ... - execute command in shell")
        self.kernel.Print("")
        self.kernel.Print("Any cell magic can be made persistent for rest of session by using %%% prefix.")
        self.kernel.Print("")
        if self.kernel.help_patterns():
            self.kernel.Print("Help on items:")
            for (pattern, level, doc) in self.kernel.help_patterns():
                self.kernel.Print("    " + doc)
        self.kernel.Print("")

def register_magics(magics):
    magics[MagicMagic.name] = MagicMagic
    

