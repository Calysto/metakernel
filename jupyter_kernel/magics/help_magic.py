# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import re


class HelpMagic(Magic):

    def help_strings():
        suffixes = [
            "item{0}{0} - get detailed help on item",
            "item{0} - get help on item",
        ]
        prefixes = [
            "{0}{0}item - get detailed help on item",
            "{0}item - get help on item",
        ]
        strings = []
        if 'help' in self.kernel.suffixes:
            strings += [s.format(self.kernel.suffixes['help'])
                        for s in suffixes]
        if 'help' in self.kernel.prefixes:
            strings += [p.format(self.kernel.prefixes['help'])
                        for p in prefixes]
        return strings

    def line_help(self, text):
        """%help TEXT - get help on the given text"""
        text = text.replace('%help', '').lstrip()
        return self.get_help_on(text, 0)

    def cell_help(self, text):
        """%%help TEXT - get detailed help on the given text"""
        text = text.replace('%%help', '').lstrip()
        return self.get_help_on(text, 1)

    def get_help_on(self, info, level, none_on_fail=False):

        if info['magic'] and info['magic']['name'] == 'help':
            code = info['rest'].rstrip()

            magic_prefix = self.kernel.magic_prefixes['magic']
            if code.endswith(magic_prefix + 'help'):
                return self.get_help('line', 'help', level)

            if magic_prefix + 'help' in code:
                while code.startswith(self.kernel.magic_prefixes['magic']):
                    code = code[1:]
                if code.startswith('help'):
                    code = code[len('help'):]

            info = self.kernel.parse_code(code.lstrip())

        if info['magic']:

            if info['magic']['name'] == 'help':
                return self.get_help('line', 'help', level)

            minfo = info['magic']
            errmsg = "No such %s magic '%s'" % (minfo['type'], minfo['name'])

            if minfo['type'] == 'line':
                magic = self.kernel.line_magics.get(minfo['name'], None)
            else:
                magic = self.kernel.cell_magics.get(minfo['name'], None)

            if not info['rest']:
                if magic:
                    return magic.get_help(minfo['type'], minfo['name'], level)
                elif not info['magic']['name']:
                    return self.kernel.get_usage()
                else:
                    return errmsg
            else:
                if magic:
                    return magic.get_help_on(info, level)
                else:
                    return errmsg
        else:
            return self.kernel.get_kernel_help_on(info, level, none_on_fail)


def register_magics(kernel):
    kernel.register_magics(HelpMagic)
