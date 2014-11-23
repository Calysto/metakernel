# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic, option
import os
import errno

class FileMagic(Magic):

    @option(
        '-a', '--append', action='store_true', default=False,
        help='append onto an existing file'
    )
    def cell_file(self, filename, append=False):
        """
        %%file [--append|-a] FILENAME - write contents of cell to file

        This cell magic will create or append the cell contents into/onto
        a file.

        Example:
            %%file -a log.txt
            This will append this line onto the file "log.txt"

        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        # Create the path of the file if dirs don't exist:
        path = os.path.dirname(os.path.abspath(filename))
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
        # Create or append to file:
        if not append:
            message = "Created file '%s'." % filename
            if os.path.isfile(self.code):
                message = "Overwrote file '%s'." % filename
        else:
            message = "Appended on file '%s'." % filename
        try:
            if append:
                fp = open(filename, "a")
            else:
                fp = open(filename, "w")
            fp.write(self.code)
            fp.close()
            self.kernel.Print(message)
        except Exception as e:
            self.kernel.Error(str(e))
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(FileMagic)
