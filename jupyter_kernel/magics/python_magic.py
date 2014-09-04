# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

import sys
import os
from jupyter_kernel import Magic, option
try:
    import jedi
except ImportError:
    jedi = None
else:
    from jedi import Interpreter
    from jedi.api.helpers import completion_parts
    from jedi.parser.user_context import UserContext


class PythonMagic(Magic):
    env = {}

    def line_python(self, *args):
        """%python CODE - evaluate code as Python"""
        code = " ".join(args)
        self.retval = self.eval(code)

    def eval(self, code):
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

    def get_completions(self, text):
        '''Get Python completions'''
        # https://github.com/davidhalter/jedi/blob/master/jedi/utils.py
        if jedi is None:
            return []

        interpreter = Interpreter(text, [self.env])
        path = UserContext(text, (1, len(text))).get_path_until_cursor()
        path, dot, like = completion_parts(path)
        before = text[:len(text) - len(like)]
        completions = interpreter.completions()

        completions = [before + c.name_with_symbols for c in completions]
        return completions

    def get_help_on(self, expr, level=0):
        """Implement basic help for functions"""
        if not expr:
            return ''

        last = expr.split()[-1]
        default = 'No help available for "%s"' % last

        obj = self.env.get(last, None)
        if not obj is None:
            return getattr(obj, '__doc__', default)

        elif '.' in last:
            mod, _, name = last.partition('.')
            obj = self.env.get(mod, None)
            if obj:
                subobj = getattr(obj, name, None)
                if subobj:
                    return getattr(subobj, '__doc__', default)
        return default

def register_magics(kernel):
    kernel.register_magics(PythonMagic)

