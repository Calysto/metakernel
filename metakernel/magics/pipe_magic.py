# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option

class PipeMagic(Magic):
    def __init__(self, *args, **kwargs):
        super(PipeMagic, self).__init__(*args, **kwargs)

    def cell_pipe(self, pipe_str):
        """
        %%pipe FUNCTION1 | FUNCTION2 ...

        The pipe cell will "pipe" the contents of a cell
        through a series of function calls. All of the
        functions must be defined in the language, and
        the kernel must support the `do_function_direct`
        method.

        Example:
            %%pipe f1 | f2 | f3
            CELL CONTENTS

            is the same as issuing:

            f3(f2(f1("CELL CONTENTS")))
        """
        functions = [function.strip() for function in pipe_str.split("|")]
        self.retval = self.code
        for function in functions:
            self.retval = self.kernel.do_function_direct(function, self.retval)
        self.evaluate = False

    def post_process(self, retval):
        return self.retval

def register_magics(kernel):
    kernel.register_magics(PipeMagic)

def register_ipython_magics():
    from IPython.core.magic import register_cell_magic
    from IPython import get_ipython

    @register_cell_magic
    def pipe(line, cell):
        """
        """
        ip = get_ipython()
        functions = [function.strip() for function in line.split("|")]
        retval = cell
        for function in functions:
            f = eval(function, ip.ns_table["user_global"])
            retval = f(retval)
        return retval
