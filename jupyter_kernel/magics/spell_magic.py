# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option
import inspect
import ast
import os

class SpellMagic(Magic):
    spells = {"renumber-cells": """%%javascript

        var cells = IPython.notebook.get_cells();
        // We only keep the code cells.
        cells = cells.filter(function(c)
            {
                return c instanceof IPython.CodeCell; 
            })
        // We set the input prompt of all code cells.
        for (var i = 0; i < cells.length; i++) {
            cells[i].set_input_prompt(i + 1);
        }
"""}

    def __init__(self, *args, **kwargs):
        super(SpellMagic, self).__init__(*args, **kwargs)
        self._load_spells()

    @option(
        '-d', '--delete', action='store_true', default=False,
        help='delete a named spell'
    )
    @option(
        '-l', '--list', action='store_true', default=False,
        help='list spells'
    )
    def line_spell(self, name, delete=False, list=False):
        """
        %spell [-l] [-d] [INCANTATION] - call a spell to perform it's magic

        This line magic will execute the spell.

        Example:
            %spell renumber-cells
        """
        if list:
            retval = "Available spells:\n"
            if name in ["all", "system"]:
                retval += "    System:\n"
                for spell in sorted(self.spells.keys()):
                    retval += "        %s\n" % spell
            if name in ["all", "learned"]:
                retval += "    Learned:\n"
                for spell in sorted(self.learned.keys()):
                    retval += "        %s\n" % spell
            self.kernel.Print(retval)
        elif name in self.spells:
            if delete:
                raise Exception("Can't delete system spell")
            else:
                self.code = self.code.strip()
                if self.code: 
                    self.code += "\n"
                self.code += self.spells[name]
        elif name in self.learned:
            if delete:
                del self.learned[name]
                self._save_spells()
            else:
                self.code = self.code.strip()
                if self.code: 
                    self.code += "\n"
                self.code += self.learned[name]
        else:
            raise Exception("No such spell: '%s'" % name)
        self.evaluate = True

    def _load_spells(self):
        self.learned = {}
        local_magics_dir = self.kernel.get_local_magics_dir()
        # Search all of the places there could be spells:
        files = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "spells.json"),
                 os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(self.__class__))), "spells.json"),
                 os.path.join(local_magics_dir, "spells.json")]
        for spell_file in files:
            try:
                data = ast.literal_eval(open(spell_file).read()) 
            except:
                continue
            self.learned.update(data)

    def _save_spells(self):
        local_magics_dir = self.kernel.get_local_magics_dir()
        filename = os.path.join(local_magics_dir, "spells.json")
        open(filename, "w").write(str(self.learned))

    def cell_spell(self, name):
        """
        %%spell INCANTATION - teach a spell

        This cell magic will teach the spell.

        Example:
            %%spell COMMAND

            CODE
        """
        self.learned[name] = self.code
        self._save_spells()
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(SpellMagic)


