# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from IPython.display import FileLinks
from metakernel import Magic, option
import os

class LSMagic(Magic):
    @option(
        "-r", "--recursive", action="store_true", default=False,
        help='recursively descend into subdirectories'
    )
    def line_ls(self, path=".", recursive=False):
        """
        %ls PATH - list files and directories under PATH

        This line magic is used to list the directory contents.

        Examples:
            %ls .
            %ls ..
        """
        path = os.path.expanduser(path)
        self.retval = FileLinks(path, recursive=recursive)

    def post_process(self, retval):
        return self.retval


def register_magics(kernel):
   kernel.register_magics(LSMagic)
