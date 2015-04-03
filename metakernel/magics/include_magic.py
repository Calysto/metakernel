# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import os

class IncludeMagic(Magic):

    def line_include(self, filenames):
        """
        %include FILENAME ... - include code from filename into this code

        This line magic will get the contents of a file and include it
        in this cell evaluation.

        Example:
            %include myprog.py
        """
        text = ""
        filenames = filenames.split()
        for filename in filenames:
            if filename.startswith("~"):
                filename = os.path.expanduser(filename)
            filename = os.path.abspath(filename)
            text += open(filename).read()
        if self.code.startswith("%"):
            lines = self.code.split("\n")
            new_lines = []
            need_to_insert = True
            for line in lines:
                if need_to_insert and not line.startswith("%"):
                    new_lines.append(text)
                    need_to_insert = False
                new_lines.append(line)
            if need_to_insert:
                new_lines.append(text)
            self.code = "\n".join(new_lines)
        else:
            self.code = text  + self.code

    def cell_include(self, filename, *args):
        """
        %%include FILENAME - include code from filename into this code

        This line magic will get the contents of a file and include it
        in this cell evaluation.

        Example:
            %%include myprog.py
            print("Done!")
        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        text = open(filename).read()
        self.code = text  + self.code

def register_magics(kernel):
    kernel.register_magics(IncludeMagic)

