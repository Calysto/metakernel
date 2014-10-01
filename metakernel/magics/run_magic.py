# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import os

class RunMagic(Magic):

    def line_run(self, filename):
        """
        %run FILENAME - run code in filename by kernel

        This magic will take the code in FILENAME and run it. The
        exact details of how the code runs are deterimined by your
        language.

        Example:
            %run filename.ss

        Note: not all languages may support %run.
        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        self.kernel.do_execute_file(filename)

def register_magics(kernel):
    kernel.register_magics(RunMagic)

