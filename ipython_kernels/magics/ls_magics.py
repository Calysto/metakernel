# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from IPython.core.magic import magic_escapes
from ipython_kernels import Magic
import os


class LSMagic(Magic):
    name = "lsmagic"
    help_lines = [" %lsmagic - list the current line and cell magics"]

    def line(self, args):
        mesc = magic_escapes['line']
        cesc = magic_escapes['cell']
        magics = self.kernel.magics
        line = [v.name for v in magics.values() if hasattr(v, 'line')]
        cell = [v.name for v in magics.values() if hasattr(v, 'cell')]

        out = ['Available line magics:',
               mesc + ('  '+mesc).join(sorted(line)),
               '',
               'Available cell magics:',
               cesc + ('  '+cesc).join(sorted(cell)),
               ]
        self.kernel.Print('\n'.join(out))


def register_magics(magics):
    magics[LSMagic.name] = LSMagic


