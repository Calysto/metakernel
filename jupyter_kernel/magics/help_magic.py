# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import re


class HelpMagic(Magic):

    help_strings = [
        "item?? - get detailed help on item",   # "code??", level, explain
        "item? - get help on item",   # "code?"
        "??item - get detailed help on item",  # "??code"
        "?item - get help on item",   # "?code"
    ]

    def line_help(self, text):
        """%help TEXT - get help on the given text"""
        text = text.replace('%help', '').lstrip()
        return self.get_help_on(text, 0)

    def cell_help(self, text):
        """%%help TEXT - get detailed help on the given text"""
        text = text.replace('%%help', '').lstrip()
        return self.get_help_on(text, 1)

    def get_help_on(self, info, level):

        if info['magic'] and info['magic']['name'] == 'help':
            code = info['code']
            if '?' in info['code']:
                code = code.replace('?', '')
            elif re.match('%+help', code):
                code = re.sub('%+help', '', code).lstrip()
            info = self.kernel.parse_code(code)

        if info['magic']:

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
            return self.kernel.get_kernel_help_on(info, level)


def register_magics(kernel):
    kernel.register_magics(HelpMagic)
