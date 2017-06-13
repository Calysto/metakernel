# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from distutils.version import LooseVersion
from metakernel import Magic, option, ExceptionWrapper
import pydoc
import traceback
import sys
try:
    import jedi
    from jedi import Interpreter
    if jedi.__version__ >= LooseVersion('0.10.0'):
        from jedi.api.helpers import get_on_completion_name
        from jedi import common
    else:
        from jedi.api.helpers import completion_parts
        from jedi.parser.user_context import UserContext
except ImportError:
    jedi = None

PY3 = sys.version_info[0] == 3

def exec_code(code, env, mode):
    import traceback
    try:
        ccode = compile(code, "python cell", mode)
    except Exception as exc:
        ex_type, ex, tb = sys.exc_info()
        tb_format = ["%s: %s" % (ex.__class__.__name__, str(ex))]
        return ExceptionWrapper(ex_type.__name__, repr(exc.args), tb_format)
    try:
        if mode == "exec":
            exec(ccode, env)
        elif mode == "eval":
            return eval(ccode, env)
    except Exception as exc:
        ex_type, ex, tb = sys.exc_info()
        line1 = ["Traceback (most recent call last):"]
        line2 = ["%s: %s" % (ex.__class__.__name__, str(ex))]
        tb_format = line1 + [line.rstrip() for line in traceback.format_tb(tb)[1:]] + line2
        return ExceptionWrapper(ex_type.__name__, repr(exc.args), tb_format)
    if "retval" in env:
        return env["retval"]

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

    def eval(self, code):
        if "__builtins__" not in self.env:
            ## __builtins__ get generated after an eval:
            eval("1", self.env)
            ## make 'kernel' and 'input' available:
            self.env["__builtins__"]["kernel"] = self.kernel
            if PY3:
                self.env["__builtins__"]["input"] = self.kernel.raw_input
                self.env["input"] = self.kernel.raw_input
            else:
                def input(*args, **kwargs):
                    return eval(self.kernel.raw_input(*args, **kwargs))
                self.env["__builtins__"]["input"] = input
                self.env["input"] = input
                self.env["__builtins__"]["raw_input"] = self.kernel.raw_input = self.kernel.raw_input
                self.env["raw_input"] = self.kernel.raw_input = self.kernel.raw_input
        try:
            ccode = compile(code.strip(), "python cell", "eval") # is it an expression?
        except:
            return exec_code(code.strip(), self.env, "exec") # no, it is statement
        return exec_code(code.strip(), self.env, "eval")     # yes, it is expression

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
                self.eval(self.code)
                self.code = str(self.env["retval"]) if ("retval" in self.env and
                                                        self.env["retval"] != None) else ""
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

        if jedi.__version__ >= LooseVersion('0.10.0'):
            lines = common.splitlines(text)
            name = get_on_completion_name(
                interpreter._get_module_node(),
                lines,
                position
            )
            before = text[:len(text) - len(name)]
        else:
            path = UserContext(text, position).get_path_until_cursor()
            path, dot, like = completion_parts(path)
            before = text[:len(text) - len(like)]

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
