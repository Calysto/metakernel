from __future__ import annotations

import inspect
import optparse
import os
import shlex
import sys
import traceback
from ast import literal_eval as safe_eval
from typing import TYPE_CHECKING, Any, Callable, NoReturn, TypeVar

if TYPE_CHECKING:
    from . import MetaKernel

_F = TypeVar("_F", bound=Callable[..., Any])

_maxsize = sys.maxsize


class MagicOptionParser(optparse.OptionParser):
    def error(self, msg: str) -> NoReturn:
        raise Exception(f'Magic Parse error: "{msg}"')

    def exit(self, status: int = 0, msg: Any = None) -> NoReturn:
        if msg:
            sys.stderr.write(msg)
        raise Exception(msg)

    ## FIXME: override help to also stop processing
    ## currently --help gives syntax error


class Magic:
    """
    Base class to define magics for MetaKernel based kernels.

    Users can redefine the default magics provided by Metakernel
    by creating a module with the exact same name as the
    Metakernel magic.

    For example, you can override %matplotlib in your kernel by
    writing a new magic inside magics/matplotlib_magic.py
    """

    def __init__(self, kernel: MetaKernel) -> None:
        self.kernel = kernel
        self.evaluate = True
        self.code = ""

    def get_args(self, mtype: str, name: str, code: str, args: Any) -> Any:
        self.code = code
        old_args = args
        mtype = mtype.replace("sticky", "cell")

        func = getattr(self, mtype + "_" + name)
        try:
            args, kwargs = _parse_args(func, args, usage=self.get_help(mtype, name))
        except Exception as e:
            self.kernel.Error(str(e))
            return self
        arg_spec = inspect.getfullargspec(func)
        fargs = arg_spec.args
        if fargs[0] == "self":
            fargs = fargs[1:]

        fargs = [f for f in fargs if f not in kwargs.keys()]
        if len(args) > len(fargs) and not arg_spec.varargs:
            extra = " ".join(str(s) for s in (args[len(fargs) - 1 :]))
            args = args[: len(fargs) - 1] + [extra]

        return (args, kwargs, old_args)

    def call_magic(self, mtype: str, name: str, code: str, args: Any) -> Magic:
        self.code = code
        old_args = args
        mtype = mtype.replace("sticky", "cell")

        func = getattr(self, mtype + "_" + name)
        try:
            args, kwargs = _parse_args(func, args, usage=self.get_help(mtype, name))
        except Exception as e:
            self.kernel.Error(str(e))
            return self

        arg_spec = inspect.getfullargspec(func)
        fargs = arg_spec.args
        if fargs[0] == "self":
            fargs = fargs[1:]

        fargs = [f for f in fargs if f not in kwargs.keys()]
        if len(args) > len(fargs) and not arg_spec.varargs:
            extra = " ".join(str(s) for s in (args[len(fargs) - 1 :]))
            args = args[: len(fargs) - 1] + [extra]

        try:
            try:
                func(*args, **kwargs)
            except TypeError:
                func(old_args)
        except Exception as exc:
            msg = f"Error in calling magic '{name}' on {mtype}:\n    {exc!s}\n    args: {args}\n    kwargs: {kwargs}"
            self.kernel.Error(msg)
            self.kernel.Error(traceback.format_exc())
            self.kernel.Error(self.get_help(mtype, name))
            # return dummy magic to end processing:
            return Magic(self.kernel)
        return self

    def get_help(self, mtype: str, name: str, level: int = 0) -> str:
        if hasattr(self, mtype + "_" + name):
            func = getattr(self, mtype + "_" + name)
            if level == 0:
                if func.__doc__:
                    return _trim(func.__doc__)  # type: ignore[return-value]
                else:
                    return f"No help available for magic '{name}' for {mtype}s."
            else:
                filename = inspect.getfile(func)
                if filename and os.path.exists(filename):
                    with open(filename) as f:
                        return f.read()
                else:
                    return f"No help available for magic '{name}' for {mtype}s."
        else:
            return f"No such magic '{name}' for {mtype}s."

    def get_help_on(self, info: dict[str, Any], level: int = 0) -> str | None:
        return "Sorry, no help is available on '{}'.".format(info["code"])

    def get_completions(self, info: dict[str, Any]) -> list[str]:
        """
        Get completions based on info dict from magic.
        """
        return []

    def get_magics(self, mtype: str) -> list[str]:
        magics = []
        for name in dir(self):
            if name.startswith(mtype + "_"):
                magics.append(name.replace(mtype + "_", ""))
        return magics

    def get_code(self) -> str:
        return self.code

    def post_process(self, retval: Any) -> Any:
        return retval


def option(*args: Any, **kwargs: Any) -> Callable[[_F], _F]:
    """Return decorator that adds a magic option to a function."""

    def decorator(func: _F) -> _F:
        help_text = ""
        if not getattr(func, "has_options", False):
            func.has_options = True  # type:ignore[attr-defined]
            func.options = []  # type:ignore[attr-defined]
            help_text += "Options:\n-------\n"
        try:
            option = optparse.Option(*args, **kwargs)
        except optparse.OptionError:
            help_text += args[0] + "\n"
        else:
            help_text += _format_option(option) + "\n"
            func.options.append(option)  # type:ignore[attr-defined]
        if func.__doc__:
            func.__doc__ += _indent(func.__doc__, help_text)
        else:
            func.__doc__ = help_text
        return func

    return decorator


def _parse_args(
    func: Any, args: Any, usage: Any = None
) -> tuple[list[Any], dict[str, Any]]:
    """Parse the arguments given to a magic function"""
    if isinstance(args, list):
        args = " ".join(args)

    args = _split_args(args)

    kwargs = dict()
    if getattr(func, "has_options", False):
        parser = MagicOptionParser(usage=usage, conflict_handler="resolve")
        parser.add_options(func.options)

        left = []
        value = None
        if "--" in args:
            left = args[: args.index("--")]
            value, args = parser.parse_args(args[args.index("--") + 1 :])
        else:
            while args:
                try:
                    value, args = parser.parse_args(args)
                except Exception:
                    left.append(args.pop(0))
                else:
                    break
        args = left + args
        if value:
            kwargs = value.__dict__

    new_args = []
    for arg in args:
        try:
            new_args.append(safe_eval(arg))
        except Exception:
            new_args.append(arg)

    for key, value in kwargs.items():
        try:
            kwargs[key] = safe_eval(value)
        except Exception:
            pass

    return new_args, kwargs


def _split_args(args: Any) -> list[Any]:
    try:
        # do not use posix mode, to avoid eating quote characters
        args = shlex.split(args, posix=False)
    except Exception:
        # parse error; let's pass args along rather than crashing
        args = args.split()

    new_args = []
    temp = ""
    for arg in args:
        if arg.startswith("-"):
            new_args.append(arg)

        elif temp:
            arg = temp + " " + arg
            try:
                safe_eval(arg)
            except Exception:
                temp = arg
            else:
                new_args.append(arg)
                temp = ""

        elif arg.startswith(("(", "[", "{")) or "(" in arg:
            try:
                safe_eval(arg)
            except Exception:
                temp = arg
            else:
                new_args.append(arg)

        else:
            new_args.append(arg)

    if temp:
        new_args.append(temp)

    return new_args


def _format_option(option: Any) -> str:
    output = ""
    if option._short_opts:
        output = option._short_opts[0] + " "
    output += option.get_opt_string() + " "
    output += " " * (15 - len(output))
    output += option.help + " "
    if not option.default == ("NO", "DEFAULT"):
        output += f"[default: {option.default}]"
    return str(output)


def _trim(docstring: str, return_lines: bool = False) -> str | list[str]:
    """
    Trim of unnecessary leading indentations.
    """
    # from: http://legacy.python.org/dev/peps/pep-0257/
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    indent = _min_indent(lines)
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < _maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    if return_lines:
        return trimmed
    else:
        # Return a single string:
        return "\n".join(trimmed)


def _min_indent(lines: list[str]) -> int:
    """
    Determine minimum indentation (first line doesn't count):
    """
    indent = _maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    return indent


def _indent(docstring: str, text: str) -> str:
    """
    Returns text indented at appropriate indententation level.
    """
    if not docstring:
        return text
    lines = docstring.expandtabs().splitlines()
    indent = _min_indent(lines)
    if indent < _maxsize:
        newlines = _trim(text, return_lines=True)
        return "\n" + ("\n".join([(" " * indent) + line for line in newlines]))
    else:
        return "\n" + text
