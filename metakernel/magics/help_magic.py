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
            strings += [s.format(self.kernel.help_suffix) for s in suffixes]
        if "help" in self.kernel.magic_prefixes:
            strings += [p.format(self.kernel.magic_prefixes["help"]) for p in prefixes]
        return sorted(strings)

    def line_help(self, text: str) -> str | None:
        """
        %help TEXT - get help on the given text

        This line magic shows the help for TEXT. Shows the help in the
        system pager that opens at bottom of screen.

        Example:
            %help dir

        """
        return self.get_text_help_on(text, 0, False)

    def cell_help(self, text: str) -> str | None:
        """
        %%help TEXT - get detailed help on the given text

        This line magic looks like a cell magic, but it really gets
        more detailed help on TEXT. Shows the help in the system
        pager that opens at bottom of screen.

        Example:
           %%help dir

        """
        return self.get_text_help_on(text, 1, False)

    def get_text_help_on(
        self, text: str, level: int, none_on_fail: bool = False, cursor_pos: int = -1
    ) -> str | None:
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

        if info["magic"]:
            minfo = info["magic"]
            errmsg = "No such {} magic '{}'".format(minfo["type"], minfo["name"])

            if minfo["type"] == "line":
                magic = self.kernel.line_magics.get(minfo["name"], None)
                if minfo["args"]:
                    info = self.kernel.parse_code(minfo["args"])
                elif magic:
                    assert isinstance(magic, Magic)
                    return magic.get_help(minfo["type"], minfo["name"], level)

            else:
                magic = self.kernel.cell_magics.get(minfo["name"], None)

                if minfo["code"]:
                    info = self.kernel.parse_code(minfo["code"])
                elif minfo["args"]:
                    info = self.kernel.parse_code(minfo["args"])
                elif magic:
                    assert isinstance(magic, Magic)
                    return magic.get_help(minfo["type"], minfo["name"], level)
                else:
                    return "No such {} magic named '{}', so can't really help with that".format(
                        minfo["type"], minfo["name"]
                    )
            if magic:
                assert isinstance(magic, Magic)
                the_help = magic.get_help_on(info, level)
                self.kernel.log.error("got")
                self.kernel.log.error(the_help)
                return the_help

            elif not info["magic"]["name"]:
                return self.kernel.get_usage()

            else:
                return errmsg

        else:
            return self.kernel.get_kernel_help_on(info, level, none_on_fail)

    def _prep_text(self, text: str) -> str:
        text = text.strip()

        magic = self.kernel.magic_prefixes["magic"]
        prefix = self.kernel.magic_prefixes["help"]
        suffix = self.kernel.help_suffix

        text = text.replace(f"{magic}{magic}help", "")
        text = text.replace(f"{magic}help", "")

        if prefix:
            while text.startswith(prefix):
                text = text[1:]

        if suffix:
            while text.endswith(suffix):
                text = text[:-1]

        return text


def register_magics(kernel) -> None:
    kernel.register_magics(HelpMagic)
