# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import inspect
import ast
import os

class MacroMagic(Magic):
    macros = {"renumber-cells": """%%javascript

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
        super(MacroMagic, self).__init__(*args, **kwargs)
        self._load_macros()

    @option(
        '-d', '--delete', action='store_true', default=False,
        help='delete a named macro'
    )
    @option(
        '-l', '--list', action='store_true', default=False,
        help='list macros'
    )
    @option(
        '-s', '--show', action='store_true', default=False,
        help='show macro'
    )
    def line_macro(self, name, delete=False, list=False, show=False):
        """
        %macro NAME - execute a macro
        %macro -l [all|learned|system] - list macros
        %macro [-s] [-d] NAME - show or delete a macro

        This line macro will execute, show, list, or delete the 
        named macro.

        Examples:
            %macro renumber-cells

            %%macro test
            print "Ok!"

            %macro -l all

            %macro -d test
        """
        if list:
            self._list_macros(name)
        elif show:
            retval = "%%%%macro %s\n" % name
            if name in self.macros:
                retval += self.macros[name]
            elif name in self.learned:
                retval += self.learned[name]
            self.kernel.Print(retval)
        elif name in self.learned:
            if delete:
                del self.learned[name]
                self._save_macros()
            else:
                self.code = self.code.strip()
                if self.code: 
                    self.code += "\n"
                self.code += self.learned[name]
        elif name in self.macros:
            if delete:
                raise Exception("Can't delete system macro")
            else:
                self.code = self.code.strip()
                if self.code: 
                    self.code += "\n"
                self.code += self.macros[name]
        elif name == "":
            self._list_macros()
        else:
            self._list_macros(retval="No such macro: '%s'\n\n" % name,
                              error=True)
        self.evaluate = True

    def _list_macros(self, name="all", retval="", error=False):
        retval += "Available macros:\n"
        if name in ["all", "system"]:
            retval += "    System:\n"
            for macro in sorted(self.macros.keys()):
                retval += "        %s\n" % macro
        if name in ["all", "learned"]:
            retval += "    Learned:\n"
            for macro in sorted(self.learned.keys()):
                retval += "        %s\n" % macro
        if error:
            self.kernel.Error(retval)
        else:
            self.kernel.Print(retval)

    def _load_macros(self):
        self.learned = {}
        local_macros_dir = self.kernel.get_local_magics_dir()
        # Search all of the places there could be macros:
        files = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "macros.json"),
                 os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(self.__class__))), "macros.json"),
                 os.path.join(local_macros_dir, "macros.json")]
        for macro_file in files:
            try:
                data = ast.literal_eval(open(macro_file).read()) 
            except:
                continue
            self.learned.update(data)

    def _save_macros(self):
        local_macros_dir = self.kernel.get_local_magics_dir()
        filename = os.path.join(local_macros_dir, "macros.json")
        open(filename, "w").write(str(self.learned))

    def cell_macro(self, name):
        """
        %%macro NAME - learn a new macro

        This cell macro will learn the macro in the
        cell. The cell contents are just commands (macros
        or code in the kernel language).

        Example:
            %%macro test
            print "Ok!"

            %macro test
            Ok!
        """
        self.learned[name] = self.code
        self._save_macros()
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(MacroMagic)

