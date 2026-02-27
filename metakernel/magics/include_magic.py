# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import shlex

from metakernel import Magic


class IncludeMagic(Magic):
    def line_include(self, filenames) -> None:
        """
        %include FILENAME ... - include code from filename into this code

        This line magic will get the contents of a file and include it
        in this cell evaluation.

        You can have multiple %include's at the beginning of a cell,
        and they will be included in order.

        Examples:
            %include myprog.py
            %include myprog1.py myprog2.py
        """
        text = ""
        # posix=False keeps backslashes intact (needed for Windows paths);
        # strip outer quote characters that shlex leaves in non-posix mode.
        try:
            parts = shlex.split(filenames, posix=False)
        except ValueError:
            parts = filenames.split()
        filenames = [
            p[1:-1] if len(p) >= 2 and p[0] == p[-1] and p[0] in ("'", '"') else p
            for p in parts
        ]
        prefix = self.kernel.magic_prefixes["magic"]
        for filename in filenames:
            if filename.startswith("~"):
                filename = os.path.expanduser(filename)
            filename = os.path.abspath(filename)
            with open(filename) as f:
                text += f.read() + "\n"
        if self.code.lstrip().startswith(prefix):
            lines = self.code.lstrip().split("\n")
            new_lines = []
            need_to_insert = True
            for line in lines:
                if need_to_insert and not line.startswith(prefix):
                    new_lines.append(text)
                    need_to_insert = False
                new_lines.append(line)
            if need_to_insert:
                new_lines.append(text)
            self.code = "\n".join(new_lines)
        else:
            self.code = text + self.code


def register_magics(kernel) -> None:
    kernel.register_magics(IncludeMagic)
