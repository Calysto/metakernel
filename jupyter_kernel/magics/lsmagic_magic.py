# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from IPython.core.magic import magic_escapes
from jupyter_kernel import Magic
import os

class LSMagicMagic(Magic):
    name = "lsmagic"
    help_lines = [" %lsmagic - list the current line and cell magics"]

    def line(self, args):
        mesc = magic_escapes['line']
        cesc = magic_escapes['cell']
        magics = self.kernel.magics
        # Hack to find out if magic supports line/cell (need more definite manner):
        line = [mesc + v.name for v in magics.values() if any([row.startswith(" %") for row in v.help_lines])]
        cell = [cesc + v.name for v in magics.values() if any([row.startswith("%%") for row in v.help_lines])]

        out = [
            'Available line magics:',
            '  '.join(sorted(line)),
            '',
            'Available cell magics:',
            '  '.join(sorted(cell)),
        ]
        self.kernel.Print('\n'.join(out))

def register_magics(magics):
    magics[LSMagicMagic.name] = LSMagicMagic


