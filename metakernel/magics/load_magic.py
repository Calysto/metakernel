# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import os

class LoadMagic(Magic):

    def line_load(self, filename):
        """
        %load FILENAME - load code from filename into next cell

        This line magic will get the contents of a file and load it
        into the next cell.

        Example:
            %load myprog.py
        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        text = open(filename).read()
        self.kernel.payload.append({"source": "set_next_input",
                                    "text": text})

def register_magics(kernel):
    kernel.register_magics(LoadMagic)

