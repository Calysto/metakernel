# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option

class PythonMagic(Magic):
    env = {}

    def line_python(self, *args):
        """%python CODE - evaluate code as Python"""
        code = " ".join(args)
        self.retval = self.eval(code)

    def eval(self, code):
        print(code.strip())
        try:
            return eval(code.strip(), self.env)
        except:
            try:
                exec(code.strip(), self.env)
            except Exception as exc:
                return "Error: " + str(exc)
        if "retval" in self.env:
            return self.env["retval"]

    @option(
        "-e", "--eval_output", action="store_true", default=False,
        help="Use the retval value from the Python cell as code in the kernel language."
    )
    def cell_python(self, eval_output=False):
        """%%python - evaluate contents of cell as Python"""
        if self.code.strip():
            if eval_output:
                self.eval(self.code)
                self.code = str(self.env["retval"]) if "retval" in self.env else ""
                self.retval = None
                self.evaluate = True
            else:
                self.retval = self.eval(self.code)
                self.evaluate = False

    def post_process(self, retval):
        if retval:
            return retval
        else:
            return self.retval

def register_magics(kernel):
    kernel.register_magics(PythonMagic)

