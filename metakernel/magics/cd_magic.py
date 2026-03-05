# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


import os

from metakernel import Magic, MetaKernel


class CDMagic(Magic):
    def line_cd(self, path: str = ".") -> None:
        """
        %cd PATH - change current directory of session

        This line magic is used to change the directory of the
        notebook or console.

        Note that this is not the same directory as used by
        the %shell magics.

        Example:
            %cd ..
        """
        path = os.path.expanduser(path)
        try:
            os.chdir(path)
            retval = os.path.abspath(path)
        except Exception as e:
            self.kernel.Error(str(e))
            retval = None
        if retval:
            self.kernel.Print(retval)


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(CDMagic)
