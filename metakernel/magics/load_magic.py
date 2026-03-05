# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

import os

from metakernel import Magic, MetaKernel


class LoadMagic(Magic):
    def line_load(self, filename: str) -> None:
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
        with open(filename) as f:
            self.kernel.payload.append({"source": "set_next_input", "text": f.read()})


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(LoadMagic)
