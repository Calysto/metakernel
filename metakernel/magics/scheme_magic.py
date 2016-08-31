# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option

try:
    from calysto_scheme import scheme
except:
    scheme = None

class SchemeMagic(Magic):
    def __init__(self, kernel):
        super(SchemeMagic, self).__init__(kernel)
        self.retval = None

    def line_scheme(self, *args):
        """
        %scheme CODE - evaluate code as Scheme

        This line magic will evaluate the CODE (either expression or
        statement) as Scheme code.

        Examples:
            %scheme (define x 42)
            %scheme (import "math")
            %scheme (+ x + math.pi)

        """
        code = " ".join(args)
        self.retval = self.eval(code)

    def eval(self, code):
        if scheme:
            return scheme.execute_string_rm(code.strip())
        else:
            raise Exception("calysto_scheme is required")

    @option(
        "-e", "--eval_output", action="store_true", default=False,
        help="Use the retval value from the Scheme cell as code in the kernel language."
    )
    def cell_scheme(self, eval_output=False):
        """
        %%scheme - evaluate contents of cell as Scheme

        This cell magic will evaluate the cell (either expression or
        statement) as Scheme code.

        The -e or --eval_output flag signals that the retval value expression
        will be used as code for the cell to be evaluated by the host
        language.

        Examples:
            %%scheme
            (define x 42)

            %%scheme
            (import "math")
            (define retval (+ x math.pi))

            %%scheme -e
            (define retval "this = code")

            %%scheme -e
            "this = code"
        """
        if self.code.strip():
            if eval_output:
                self.code = self.eval(self.code)
                self.evaluate = True
            else:
                self.retval = self.eval(self.code)
                self.evaluate = False

    def post_process(self, retval):
        if retval is not None:
            return retval
        else:
            return self.retval

def register_magics(kernel):
    kernel.register_magics(SchemeMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic, register_cell_magic
    kernel = IPythonKernel()
    magic = SchemeMagic(kernel)

    @register_line_magic
    def scheme(line):
        magic.line_scheme(line)
        return magic.retval

    @register_cell_magic
    def scheme(line, cell):
        magic.code = cell
        magic.cell_scheme()
        return magic.retval
