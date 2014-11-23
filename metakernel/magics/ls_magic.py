# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from IPython.display import FileLinks
from metakernel import Magic, option
import os

class LSMagic(Magic):
    def line_ls(self, path):
        """
        %ls PATH - list files and directories under PATH

        This line magic is used to list the directory contents.

        Examples:
            %ls .
            %ls ..
        """
        path = os.path.expanduser(path)
        retval = FileLinks(path)
        if retval:
            self.kernel.Display(retval)


def register_magics(kernel):
   kernel.register_magics(LSMagic)
