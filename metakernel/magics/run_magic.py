# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import os

class RunMagic(Magic):

    @option(
        '-l', '--language', action='store', default=None,
        help='use the provided language name as kernel'
    )
    def line_run(self, filename, language=None):
        """
        %run [--language LANG] FILENAME - run code in filename by
           kernel

        This magic will take the code in FILENAME and run it. The
        exact details of how the code runs are deterimined by your
        language.

        The --language LANG option will prefix the file contents with
        "%%LANG". You may also put information in the cell which will
        appear before the contents of the file.

        Examples:
            %run filename.ss
            %run -l python filename.py

            %kx calysto_scheme.kernel CalystoScheme
            %run --language kx filename.ss
            %run --language "kx default" filename.ss

        Note: not all languages may support %run.
        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        if language is None:
            self.kernel.do_execute_file(filename)
        else:
            code = "".join(open(filename).readlines())
            self.code = "%%" + language + "\n" + self.code + code

def register_magics(kernel):
    kernel.register_magics(RunMagic)

