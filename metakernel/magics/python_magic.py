# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option, ExceptionWrapper
import pydoc
import sys
import ast
import jedi
from jedi import Interpreter
from jedi.api.helpers import get_on_completion_name
from parso import split_lines


def exec_then_eval(code, env):
    import traceback
    try:
        block = ast.parse(code, mode="exec")
        last = block.body.pop()
        if type(last) != ast.Expr:
            block.body.append(last)
            retval = exec(compile(block, "python cell", mode="exec"), env)
        else:
            exec(compile(block, "python cell", mode="exec"), env)
            retval = eval(compile(ast.Expression(last.value),
                                  "python cell", mode="eval"), env)
        if "retval" in env and env["retval"] is not None:
            return env['retval']
        else:
            return retval

    except Exception as exc:
        ex_type, ex, tb = sys.exc_info()
        line1 = ["Traceback (most recent call last):"]
        line2 = ["%s: %s" % (ex.__class__.__name__, str(ex))]
        tb_format = line1 + [line.rstrip() for line in traceback.format_tb(tb)[1:]] + line2
        return ExceptionWrapper(ex_type.__name__, repr(exc.args), tb_format)

class PythonMagic(Magic):

    def __init__(self, kernel):
        super(PythonMagic, self).__init__(kernel)
        self.env = globals()['__builtins__'].copy()
        self.retval = None

    def line_python(self, *args):
        """
        %python CODE - evaluate code as Python

        This line magic will evaluate the CODE (either expression or
        statement) as Python code.

        Note that the version of Python is that of the notebook server.

        Examples:
            %python x = 42
            %python import math
            %python x + math.pi

        """
        code = " ".join(args)
        self.retval = self.eval(code)
        self.env["retval"] = None

    def eval(self, code):
        import IPython.display
        import metakernel.display
        # monkey patch IPython.display.display
        # to redirect notebook display calls to kernel display
        IPython.display.display = metakernel.display.display

        if "__builtins__" not in self.env:
            ## __builtins__ get generated after an eval:
            eval("1", self.env)
            ## make 'kernel' and 'input' available:
            self.env["__builtins__"]["kernel"] = self.kernel
            self.env["__builtins__"]["input"] = self.kernel.raw_input
            self.env["input"] = self.kernel.raw_input
        return exec_then_eval(code.strip(), self.env)

    @option(
        "-e", "--eval_output", action="store_true", default=False,
        help="Use the retval value from the Python cell as code in the kernel language."
    )
    def cell_python(self, eval_output=False):
        """
        %%python - evaluate contents of cell as Python

        This cell magic will evaluate the cell (either expression or
        statement) as Python code.

        Unlike IPython's Python, this does not return the last expression.
        To do that, you need to assign the last expression to the special
        variable "retval".

        The -e or --eval_output flag signals that the retval value expression
        will be used as code for the cell to be evaluated by the host
        language.

        Note that the version of Python is that of the notebook server.

        Examples:
            %%python
            x = 42

            %%python
            import math
            retval = x + math.pi

            %%python -e
            retval = "'(this is code in the kernel language)"

            %%python -e
            "'(this is code in the kernel language)"

        """
        if self.code.strip():
            if eval_output:
                retval = self.eval(self.code)
                self.code = str(self.env["retval"]) if ("retval" in self.env and
                                                        self.env["retval"] != None) else retval
                self.retval = None
                self.env["retval"] = None
                self.evaluate = True
            else:
                self.retval = self.eval(self.code)
                self.env["retval"] = None
                self.evaluate = False

    def post_process(self, retval):
        if retval is not None:
            return retval
        else:
            return self.retval

    def get_completions(self, info):
        '''Get Python completions'''
        # https://github.com/davidhalter/jedi/blob/master/jedi/utils.py
        if jedi is None:
            return []

        text = info['code']
        position = (info['line_num'], info['column'])
        interpreter = Interpreter(text, [self.env])

        lines = split_lines(text)
        name = get_on_completion_name(
            interpreter._module_node,
            lines,
            position
        )
        before = text[:len(text) - len(name)]

        try:
            completions = interpreter.complete()
        except AttributeError:
            completions = interpreter.completions()

        completions = [before + c.name_with_symbols for c in completions]

        self.kernel.log.error(completions)

        return [c[info['start']:] for c in completions]

    def get_help_on(self, info, level=0, none_on_fail=False):
        """Implement basic help for functions"""
        if not info['code']:
            return None if none_on_fail else ''

        last = info['obj']

        default = None if none_on_fail else ('No help available for "%s"' % last)

        parts = last.split('.')

        obj = self.env.get(parts[0], None)

        if not obj:
            return default

        for p in parts[1:]:

            obj = getattr(obj, p, None)

            if not obj:
                return default

        strhelp = pydoc.render_doc(obj, "Help on %s")
        if level == 0:
            return getattr(obj, '__doc__', strhelp)
        else:
            return strhelp

def register_magics(kernel):
    kernel.register_magics(PythonMagic)
