# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic


class MagicMagic(Magic):

    def line_magic(self, line):
        """
        %magic - show installed magics

        This line magic shows all of the install magics, either from
        the system magic folder, or your own private magic folder.

        """
        line_magics = []
        cell_magics = []

        for (name, magic) in self.kernel.line_magics.items():
            line_magics.append(magic.get_help('line', name).split("\n")[0])
        for (name, magic) in self.kernel.cell_magics.items():
            cell_magics.append(magic.get_help('cell', name).split("\n")[0])

        prefixes = self.kernel.magic_prefixes
        line_magics = ("\n    ".join(sorted(line_magics)))
        line_magics = line_magics.replace('%', prefixes['magic'])
        cell_magics = ("\n    ".join(sorted(cell_magics)))
        cell_magics = cell_magics.replace('%', prefixes['magic'])

        self.kernel.Print("Line magics:")
        self.kernel.Print("    " + line_magics)
        self.kernel.Print("")
        self.kernel.Print("Cell magics:")
        self.kernel.Print("    " + cell_magics)
        self.kernel.Print("")
        self.kernel.Print("Shell shortcut:")
        self.kernel.Print("    %s COMMAND ... - execute command in shell" % prefixes['shell'])
        self.kernel.Print("")
        self.kernel.Print(
            "Any cell magic can be made persistent for rest of session by using {0}{0}{0} prefix.".format(prefixes['magic']))
        self.kernel.Print("")
        self.kernel.Print("Help on items:")
        for string in self.kernel.line_magics['help'].help_strings():
            self.kernel.Print("    " + string)
        self.kernel.Print("")

    def get_magic(self, info, get_args=False):

        if not info['magic']:
            return None

        minfo = info['magic']
        name = minfo['name']
        if minfo['type'] == 'sticky':
            sname = '%%' + name
            if sname in self.kernel.sticky_magics:
                del self.kernel.sticky_magics[sname]
                self.kernel.Print("%s removed from session magics.\n" % sname)
                # dummy magic to eat this line and continue:
                return Magic(self.kernel)
            else:
                self.kernel.sticky_magics[sname] = minfo['args']
                self.kernel.Print("%s added to session magics.\n" % name)

        cell_magics = self.kernel.cell_magics
        line_magics = self.kernel.line_magics
        if minfo['type'] in ['cell', 'sticky'] and name in cell_magics.keys():
            magic = cell_magics[name]
        elif minfo['type'] == 'line' and name in line_magics.keys():
            magic = line_magics[name]

        else:
            # FIXME: Raise an error
            return None
        if get_args:
            return magic.get_args(minfo['type'], minfo['name'],
                                  minfo['code'], minfo['args'])
        else:
            return magic.call_magic(minfo['type'], minfo['name'],
                                    minfo['code'], minfo['args'])


def register_magics(kernel):
    kernel.register_magics(MagicMagic)
