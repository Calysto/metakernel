# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic


class HelpMagic(Magic):

    def help_strings(self):
        suffixes = [
            "item{0}{0} - get detailed, technical information on item",
            "item{0}  - get help on item",
        ]
        prefixes = [
            "{0}{0}item - get detailed, technical information on item",
            "{0}item  - get help on item",
        ]
        strings = []
        if self.kernel.help_suffix:
            strings += [s.format(self.kernel.help_suffix['help'])
                        for s in suffixes]
        if 'help' in self.kernel.magic_prefixes:
            strings += [p.format(self.kernel.magic_prefixes['help'])
                        for p in prefixes]
        return sorted(strings)

    def line_help(self, text):
        """
        %help TEXT - get help on the given text

        This line magic shows the help for TEXT. Shows the help in the
        system pager that opens at bottom of screen.

        Example:
            %help dir

        """
        return self.get_help_on(text, 0, False)

    def cell_help(self, text):
        """
        %%help TEXT - get detailed help on the given text

        This line magic looks like a cell magic, but it really gets
        more detailed help on TEXT. Shows the help in the system
        pager that opens at bottom of screen.

        Example:
           %%help dir

        """
        return self.get_help_on(text, 1, False)

    def get_help_on(self, text, level, none_on_fail=False, cursor_pos=-1):
        """
        Examples
        ========

        All of the following give help on np.ones using the %python magic:

        %help %python np.ones
        %python np.ones?

        To get help on a magic itself, we would write one of the following:

        %python?
        %help %python
        ?%python
        """
        text = self._prep_text(text)
        if not text:
            return self.kernel.get_usage()

        info = self.kernel.parse_code(text, cursor_end=cursor_pos)

        if info['magic']:

            minfo = info['magic']
            errmsg = "No such %s magic '%s'" % (minfo['type'], minfo['name'])

            if minfo['type'] == 'line':
                magic = self.kernel.line_magics.get(minfo['name'], None)
                if minfo['args']:
                    info = self.kernel.parse_code(minfo['args'])
                elif magic:
                    return magic.get_help(minfo['type'], minfo['name'],
                                          level)

            else:
                magic = self.kernel.cell_magics.get(minfo['name'], None)

                if minfo['code']:
                    info = self.kernel.parse_code(minfo['code'])
                elif minfo['args']:
                    info = self.kernel.parse_code(minfo['args'])
                elif magic:
                    return magic.get_help(minfo['type'], minfo['name'],
                                          level)
                else:
                    return ("No such %s magic named '%s', so can't really help with that" % 
                            (minfo["type"], minfo["name"]))

            if magic:
                return magic.get_help_on(info)

            elif not info['magic']['name']:
                return self.kernel.get_usage()

            else:
                return errmsg

        else:
            return self.kernel.get_kernel_help_on(info, level, none_on_fail)

    def _prep_text(self, text):
        text = text.strip()

        magic = self.kernel.magic_prefixes['magic']
        prefix = self.kernel.magic_prefixes['help']
        suffix = self.kernel.help_suffix

        text = text.replace('{0}{0}help'.format(magic), '')
        text = text.replace('{0}help'.format(magic), '')

        if text.startswith('{0}{0}'.format(prefix)):
            text = text[2:]
        elif text.startswith('{0}'.format(prefix)):
            text = text[1:]

        if suffix:
            if text.endswith('{0}{0}'.format(suffix)):
                text = text[:-2]
            elif text.endswith('{0}'.format(suffix)):
                text = text[:-1]

        return text


def register_magics(kernel):
    kernel.register_magics(HelpMagic)
