# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic, option
import os

class EditMagic(Magic):

    def line_edit(self, filename):
        """
        %edit FILENAME - load code from filename into next cell for editing

        This line magic will open the file in the next cell, and allow
        you edit it.

        This is a shortcut for %load, and appending a "%%file" as first line.

        Example:
            %edit myprogram.ss

        """
        orig_filename = filename
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        text = open(filename).read()
        self.kernel.payload.append({"source": "set_next_input",
                                    "text": "%%file " + orig_filename + "\n" + text})

def register_magics(kernel):
    kernel.register_magics(EditMagic)

