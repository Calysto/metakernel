# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from IPython.core.magic import magic_escapes
from jupyter_kernel import Magic
import os

class LSMagicMagic(Magic):

    def line_lsmagic(self, *args, **kwargs):
        """%lsmagic - list the current line and cell magics"""
        mesc = magic_escapes['line']
        cesc = magic_escapes['cell']

        line_magics = self.kernel.line_magics.keys()
        cell_magics = self.kernel.cell_magics.keys()

        out = [
            'Available line magics:',
            '  '.join(sorted(line_magics)),
            '',
            'Available cell magics:',
            '  '.join(sorted(cell_magics)),
        ]
        self.kernel.Print('\n'.join(out))

def register_magics(kernel):
    kernel.register_magics(LSMagicMagic)
