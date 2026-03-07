from __future__ import annotations

import optparse
import sys
from typing import Any
from unittest.mock import patch

import pytest

from metakernel import Magic, option
from metakernel.magic import (
    MagicOptionParser,
    _format_option,
    _indent,
    _parse_args,
    _split_args,
    _trim,
)
from tests.utils import get_kernel


class Dummy(Magic):
    @option("-s", "--size", action="store", help='Pixel size of plots, "width,height"')
    def line_dummy(self, foo, size=None) -> None:
        """
        %dummy [options] foo - Perform dummy operation on foo

        This is additional information on dummy.

        """
        self.foo = foo
        self.size = size

    def cell_spam(self):
        """
        %%spam - Cook some spam
        """
        pass

    def line_eggs(self, style):
        """
        %eggs STYLE - cook some eggs in the given style
        """
        pass


def test_get_magics() -> None:
    kernel = get_kernel()
    d = Dummy(kernel)
    line = d.get_magics("line")
    cell = d.get_magics("cell")

    assert "dummy" in line
    assert "spam" in cell
    assert "eggs" in line


def test_get_help() -> None:
    kernel = get_kernel()
    d = Dummy(kernel)

    dummy_help = d.get_help("line", "dummy", 0)
    assert dummy_help.startswith("%dummy")

    dummy_help = d.get_help("line", "dummy", 1)
    # will show this entire file, including this sentence
    assert "# will show this entire file, including this sentence" in dummy_help

    spam_help = d.get_help("cell", "spam", 0)
    assert spam_help.startswith("%%spam"), spam_help

    spam_help = d.get_help("cell", "spam", 1)
    assert "# will show this entire file, including this sentence" in spam_help


def test_option() -> None:
    kernel = get_kernel()
    d = Dummy(kernel)
    assert "Options:" in d.line_dummy.__doc__  # type:ignore[operator]
    assert "--size" in d.line_dummy.__doc__  # type:ignore[operator]

    ret = d.call_magic("line", "dummy", "", "hey -s400,200")
    assert ret == d
    assert d.foo == "hey", d.foo
    assert d.size == (400, 200)

    ret = d.call_magic("line", "dummy", "", "hey there")
    assert d.foo == "hey there"

    ret = d.call_magic("line", "dummy", "", "range(1, 10)")
    # arg eval no longer evals Python raw code:
    assert d.foo == "range(1, 10)"

    ret = d.call_magic("line", "dummy", "", "[1, 2, 3]")
    # arg eval does eval Python data structures:
    assert d.foo == [1, 2, 3]

    ret = d.call_magic("line", "dummy", "", "hey -l -s400,200")
    assert d.size == (400, 200)
    assert d.foo == "hey -l"

    ret = d.call_magic("line", "dummy", "", "hey -s -- -s400,200")
    assert d.size == (400, 200)
    assert d.foo == "hey -s"


# ---------------------------------------------------------------------------
# Helper magic subclasses used by the branch-coverage tests below
# ---------------------------------------------------------------------------


class NodocMagic(Magic):
    """Magic with a method that has no docstring."""

    def line_nodoc(self, x: str) -> None:
        pass  # intentionally no docstring


class RaisingMagic(Magic):
    def line_raise(self, x: str) -> None:
        """
        %raise x - always raises
        """
        raise RuntimeError("intentional error")


class VarargsMagic(Magic):
    def line_vararg(self, *args: Any) -> None:
        """
        %vararg - accept any number of positional args
        """
        self.captured = args


# ---------------------------------------------------------------------------
# MagicOptionParser.exit()
# ---------------------------------------------------------------------------


class TestMagicOptionParser:
    def test_exit_with_msg_writes_stderr(self) -> None:
        parser = MagicOptionParser()
        with patch.object(sys, "stderr") as mock_stderr:
            with pytest.raises(Exception, match="oops"):
                parser.exit(1, "oops")
        mock_stderr.write.assert_called_once_with("oops")

    def test_exit_without_msg_skips_stderr(self) -> None:
        parser = MagicOptionParser()
        with patch.object(sys, "stderr") as mock_stderr:
            with pytest.raises(Exception, match="None"):
                parser.exit(0)
        mock_stderr.write.assert_not_called()


# ---------------------------------------------------------------------------
# Magic.get_args()
# ---------------------------------------------------------------------------


class TestGetArgs:
    def test_sticky_mtype_resolved_to_cell(self) -> None:
        kernel = get_kernel()
        d = Dummy(kernel)
        result = d.get_args("sticky", "spam", "", "")
        # "sticky" → "cell"; cell_spam exists; returns (args, kwargs, old_args)
        assert isinstance(result, tuple) and len(result) == 3

    def test_parse_args_exception_returns_self(self) -> None:
        kernel = get_kernel()
        d = Dummy(kernel)
        with patch("metakernel.magic._parse_args", side_effect=Exception("bad")):
            result = d.get_args("line", "dummy", "", "something")
        assert result is d

    def test_varargs_suppresses_extra_arg_merging(self) -> None:
        kernel = get_kernel()
        d = VarargsMagic(kernel)
        args, _kwargs, _old_args = d.get_args("line", "vararg", "", "a b c")
        # varargs present → no merging; all three args kept separate
        assert args == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# Magic.call_magic() - uncovered branches
# ---------------------------------------------------------------------------


class TestCallMagicBranches:
    def test_sticky_mtype_resolved_to_cell(self) -> None:
        kernel = get_kernel()
        d = Dummy(kernel)
        ret = d.call_magic("sticky", "spam", "", "")
        assert ret is d

    def test_parse_args_exception_returns_self(self) -> None:
        kernel = get_kernel()
        d = Dummy(kernel)
        with patch("metakernel.magic._parse_args", side_effect=Exception("bad")):
            ret = d.call_magic("line", "dummy", "", "something")
        assert ret is d

    def test_typeerror_fallback_calls_func_with_old_args(self) -> None:
        kernel = get_kernel()
        d = Dummy(kernel)
        # Empty args → func() is missing required 'foo' → TypeError →
        # func(old_args) called with old_args="" → succeeds
        ret = d.call_magic("line", "dummy", "", "")
        assert ret is d
        assert d.foo == ""

    def test_outer_exception_returns_new_magic_instance(self) -> None:
        kernel = get_kernel()
        d = RaisingMagic(kernel)
        ret = d.call_magic("line", "raise", "", "x")
        assert isinstance(ret, Magic)
        assert ret is not d


# ---------------------------------------------------------------------------
# Magic.get_help() - uncovered branches
# ---------------------------------------------------------------------------


class TestGetHelpBranches:
    def test_level0_no_docstring_returns_no_help_message(self) -> None:
        kernel = get_kernel()
        d = NodocMagic(kernel)
        result = d.get_help("line", "nodoc", 0)
        assert "No help available" in result

    def test_level1_file_not_exists_returns_no_help_message(self) -> None:
        kernel = get_kernel()
        d = Dummy(kernel)
        with patch("os.path.exists", return_value=False):
            result = d.get_help("line", "dummy", 1)
        assert "No help available" in result

    def test_no_such_magic_returns_no_such_magic_message(self) -> None:
        kernel = get_kernel()
        d = Dummy(kernel)
        result = d.get_help("line", "nonexistent", 0)
        assert "No such magic" in result


# ---------------------------------------------------------------------------
# option() decorator - uncovered branches
# ---------------------------------------------------------------------------


class TestOptionDecorator:
    def test_second_option_application_skips_header(self) -> None:
        def myfunc(self: Any, x: str) -> None:
            """
            %myfunc x - test
            """

        first = option("--foo", action="store_true", help="foo")(myfunc)
        second = option("--bar", action="store_true", help="bar")(first)
        assert second.__doc__ is not None
        # "Options:" header appears only once even with two decorators
        assert second.__doc__.count("Options:") == 1

    def test_option_error_appends_raw_arg_string(self) -> None:
        def myfunc(self: Any, x: str) -> None:
            """
            %myfunc x - test
            """

        # "not-a-flag" doesn't start with "-" → optparse.OptionError
        decorated = option("not-a-flag")(myfunc)
        assert decorated.__doc__ is not None
        assert "not-a-flag" in decorated.__doc__

    def test_no_docstring_sets_help_text_as_doc(self) -> None:
        def myfunc(self: Any, x: str) -> None:
            pass  # no docstring

        decorated = option("--verbose", action="store_true", help="verbose")(myfunc)
        assert decorated.__doc__ is not None
        assert "Options:" in decorated.__doc__


# ---------------------------------------------------------------------------
# _parse_args() - uncovered branches
# ---------------------------------------------------------------------------


class TestParseArgsFunction:
    def test_list_args_joined_before_splitting(self) -> None:
        def myfunc(self: Any, x: str, y: str) -> None:
            pass

        args, kwargs = _parse_args(myfunc, ["hello", "world"])
        assert args == ["hello", "world"]
        assert kwargs == {}

    def test_no_options_skips_parser(self) -> None:
        def myfunc(self: Any, x: str) -> None:
            pass

        args, kwargs = _parse_args(myfunc, "hello")
        assert args == ["hello"]
        assert kwargs == {}

    def test_empty_args_with_options_yields_empty_kwargs(self) -> None:
        def myfunc(self: Any, x: str) -> None:
            pass

        myfunc.has_options = True  # type: ignore[attr-defined]
        myfunc.options = [optparse.Option("--size", action="store", help="size")]  # type: ignore[attr-defined]
        _args, kwargs = _parse_args(myfunc, "")
        # Empty input → while loop never runs → value stays None → kwargs = {}
        assert kwargs == {}


# ---------------------------------------------------------------------------
# _split_args() - shlex exception fallback
# ---------------------------------------------------------------------------


class TestSplitArgsFunction:
    def test_shlex_exception_falls_back_to_split(self) -> None:
        with patch("metakernel.magic.shlex") as mock_shlex:
            mock_shlex.split.side_effect = ValueError("simulated parse error")
            result = _split_args("hello world")
        assert "hello" in result
        assert "world" in result


# ---------------------------------------------------------------------------
# _format_option() - uncovered branches
# ---------------------------------------------------------------------------


class TestFormatOption:
    def test_long_only_option_no_short_prefix(self) -> None:
        opt = optparse.Option("--verbose", action="store_true", help="enable verbose")
        result = _format_option(opt)
        assert result.startswith("--verbose")

    def test_explicit_default_shown_in_output(self) -> None:
        opt = optparse.Option("--size", action="store", default=10, help="size")
        result = _format_option(opt)
        assert "[default: 10]" in result


# ---------------------------------------------------------------------------
# _trim() - uncovered branches
# ---------------------------------------------------------------------------


class TestTrimFunction:
    def test_empty_string_returns_empty(self) -> None:
        assert _trim("") == ""

    def test_return_lines_true_returns_list(self) -> None:
        result = _trim("  hello\n  world", return_lines=True)
        assert isinstance(result, list)
        assert "hello" in result


# ---------------------------------------------------------------------------
# _indent() - uncovered branches
# ---------------------------------------------------------------------------


class TestIndentFunction:
    def test_empty_docstring_returns_text_directly(self) -> None:
        result = _indent("", "some text")
        assert result == "some text"

    def test_single_line_docstring_uses_newline_prefix(self) -> None:
        # Single-line docstring → _min_indent returns sys.maxsize (no lines[1:])
        # → indent >= _maxsize → return "\n" + text
        result = _indent("single line", "some text")
        assert result == "\nsome text"
