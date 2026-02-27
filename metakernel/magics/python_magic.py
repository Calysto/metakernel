# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import ast
import pydoc
import sys
from typing import Any

import jedi  # type:ignore[import-untyped]
from jedi import Interpreter
from jedi.api.helpers import get_on_completion_name  # type:ignore[import-untyped]
from parso import split_lines  # type:ignore[attr-defined]

from metakernel import ExceptionWrapper, Magic, MetaKernel, option


def exec_then_eval(code: str, env: dict[str, Any]) -> Any:
    import traceback

    try:
        block = ast.parse(code, mode="exec")
        last = block.body.pop()
        if not isinstance(last, ast.Expr):
            block.body.append(last)
            exec(compile(block, "python cell", mode="exec"), env)
            retval = None
        else:
            exec(compile(block, "python cell", mode="exec"), env)
            retval = eval(
                compile(ast.Expression(last.value), "python cell", mode="eval"), env
            )
        if "retval" in env and env["retval"] is not None:
            return env["retval"]
        else:
            return retval

    except Exception as exc:
        ex_type, ex, tb = sys.exc_info()
        line1 = ["Traceback (most recent call last):"]
        ex_name = ex_type.__name__ if ex_type is not None else "Exception"
        line2 = [f"{ex_name}: {ex!s}"]
        tb_format = (
            line1 + [line.rstrip() for line in traceback.format_tb(tb)[1:]] + line2
        )
        return ExceptionWrapper(ex_name, repr(exc.args), tb_format)


class PythonMagic(Magic):
    def __init__(self, kernel: MetaKernel) -> None:
        super().__init__(kernel)
        self.env = globals()["__builtins__"].copy()
        self.retval: Any = None

    def line_python(self, *args: Any) -> None:
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

    def eval(self, code: str) -> Any:
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
        "-e",
        "--eval_output",
        action="store_true",
        default=False,
        help="Use the retval value from the Python cell as code in the kernel language.",
    )
    def cell_python(self, eval_output: bool = False) -> None:
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
                self.code = (
                    str(self.env["retval"])
                    if ("retval" in self.env and self.env["retval"] is not None)
                    else str(retval)
                )
                self.retval = None
                self.env["retval"] = None
                self.evaluate = True
            else:
                self.retval = self.eval(self.code)
                self.env["retval"] = None
                self.evaluate = False

    def post_process(self, retval: Any) -> Any:
        if retval is not None:
            return retval
        else:
            return self.retval

    def get_completions(self, info: dict[str, Any]) -> list[str]:
        """Get Python completions"""
        # https://github.com/davidhalter/jedi/blob/master/jedi/utils.py
        if jedi is None:
            return []

        text = info["code"]
        position = (info["line_num"], info["column"])
        interpreter = Interpreter(text, [self.env])

        lines = split_lines(text)
        name = get_on_completion_name(interpreter._module_node, lines, position)
        before = text[: len(text) - len(name)]

        try:
            completions = interpreter.complete()
        except AttributeError:
            completions = interpreter.completions()

        completions = [before + c.name_with_symbols for c in completions]

        self.kernel.log.error(completions)

        return [c[info["start"] :] for c in completions]

    def get_help_on(
        self, info: dict[str, Any], level: int = 0, none_on_fail: bool = False
    ) -> str | None:
        """Implement basic help for functions"""
        if not info["code"]:
            return None if none_on_fail else ""

        last = info["obj"]

        default = None if none_on_fail else (f'No help available for "{last}"')

        parts = last.split(".")

        obj = self.env.get(parts[0], None)

        if not obj:
            return default

        for p in parts[1:]:
            obj = getattr(obj, p, None)

            if not obj:
                return default

        strhelp = pydoc.render_doc(obj, "Help on %s")
        if level == 0:
            return getattr(obj, "__doc__", strhelp)
        else:
            return strhelp


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(PythonMagic)
