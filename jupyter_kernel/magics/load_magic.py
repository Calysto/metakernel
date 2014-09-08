# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option

class LoadMagic(Magic):

    def line_load(self, filename):
        """%load FILENAME - load code from filename into next cell"""
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        text = open(filename).read()
        self.kernel.payload["source"] = "set_next_input"
        self.kernel.payload["text"] = text

def register_magics(kernel):
    kernel.register_magics(LoadMagic)

