# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic


class HelpMagic(Magic):

    def line_help(self, text):
        """%help TEXT - get help on the given text"""
        text = text.replace('%help', '').lstrip()
        return self.kernel.get_help_on(text, 0)

    def cell_help(self, text):
        """%%help TEXT - get detailed help on the given text"""
        text = text.replace('%%help', '').lstrip()
        return self.kernel.get_help_on(text, 1)

    def get_help_on(self, info, level):
        if info['magic'] and info['magic']['name'] == 'help':
            text = info['magic']['cmd'] + ' ' + info['magic']['args'] + '\n' + info['magic']['code']
        elif info['magic']:
            text = info['magic']['prefix'] + info['magic']['name'] + ' ' + info['rest']
        else:
            text = info['code']
        return self.kernel.get_help_on(text.rstrip())

    def help_patterns(self):
        return [
            ("^(.*)\?\?$", 1,
             "item?? - get detailed help on item"),  # "code??", level, explain
            ("^(.*)\?$", 0,
             "item? - get help on item"),   # "code?"
            ("^\?\?(.*)$", 1,
             "??item - get detailed help on item"),  # "??code"
            ("^\?(.*)$", 0,
             "?item - get help on item"),   # "?code"
        ]


def register_magics(kernel):
    kernel.register_magics(HelpMagic)
