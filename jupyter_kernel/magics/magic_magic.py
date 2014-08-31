# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic

class MagicMagic(Magic):

    def line_magic(self, *args, **kwargs):
        """%magic - show installed magics"""
        line_magics = []
        cell_magics = []

        for (name, magic) in self.kernel.line_magics.items():
            line_magics.append(magic.get_help('line', name))
        for (name, magic) in self.kernel.cell_magics.items():
            cell_magics.append(magic.get_help('cell', name))

        self.kernel.Print("Line magics:")
        self.kernel.Print("    " + ("\n    ".join(sorted(line_magics))))
        self.kernel.Print("")
        self.kernel.Print("Cell magics:")
        self.kernel.Print("    " + ("\n    ".join(sorted(cell_magics))))
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

def register_magics(kernel):
    kernel.register_magics(MagicMagic)
