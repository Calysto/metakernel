# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import os

class IncludeMagic(Magic):

    def line_include(self, filename):
        """
        %include FILENAME - include code from filename into this code

        This line magic will get the contents of a file and include it
        in this cell evaluation.

        Example:
            %include myprog.py
        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        text = open(filename).read()
        self.code = text  + self.code

    def cell_include(self, filename):
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

