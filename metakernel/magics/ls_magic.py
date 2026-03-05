# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

import os
from typing import Any

from IPython.display import FileLinks

from metakernel import Magic, MetaKernel, option


class LSMagic(Magic):
    @option(
        "-r",
        "--recursive",
        action="store_true",
        default=False,
        help="recursively descend into subdirectories",
    )
    def line_ls(self, path: str = ".", recursive: bool = False) -> None:
        """
        %ls PATH - list files and directories under PATH

        This line magic is used to list the directory contents.

        Examples:
            %ls .
            %ls ..
        """
        path = os.path.expanduser(path)
        self.retval = FileLinks(path, recursive=recursive)  # type: ignore[no-untyped-call]

    def post_process(self, retval: Any) -> Any:
        return self.retval


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(LSMagic)
