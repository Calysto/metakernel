import os
import re
import sys
import tempfile
import unittest.mock
from typing import Any

import pytest
import zmq
from traitlets.config import LoggingConfigurable

from metakernel import ExceptionWrapper, MetaKernel
from tests.utils import (
    EvalKernel,
    clear_log_text,
    get_kernel,
    get_log,
    get_log_text,
    ss,
)


def test_magics() -> None:
    kernel = get_kernel()
    for magic in [
        "cd",
        "connect_info",
        "download",
        "html",
        "install_magic",
        "javascript",
        "latex",
        "lsmagic",
        "magic",
        "plot",
        "reload_magics",
        "shell",
    ]:
        msg = "magic '%s' is not in line_magics" % magic
        assert magic in kernel.line_magics, msg

    for magic in ["file", "html", "javascript", "latex", "shell", "time"]:
        assert magic in kernel.cell_magics

    with tempfile.NamedTemporaryFile() as ntf:
        kernel.get_magic("%%shell ls %s" % ntf.name)
        log_text = get_log_text(kernel)
        # Windows may give 8.3 short paths (RUNNER~1) vs long paths in shell output
        assert os.path.basename(ntf.name) in log_text


def test_help() -> None:
    kernel = get_kernel()
    resp = kernel.get_help_on("%shell", 0)
    assert "run the line as a shell command" in resp

    resp = kernel.do_execute("%cd?", False)
    assert (
        "change current directory of session"
        in resp["payload"][0]["data"]["text/plain"]
    )

    resp = kernel.get_help_on("what", 0)
    assert resp == "Sorry, no help is available on 'what'.", (
        "response was actually %s" % resp
    )


def test_complete() -> None:
    kernel = get_kernel()
    comp = kernel.do_complete("%connect_", len("%connect_"))
    assert comp["matches"] == ["%connect_info"], str(comp["matches"])

    comp = kernel.do_complete("%%fil", len("%%fil"))
    assert comp["matches"] == ["%%file"], str(comp["matches"])

    comp = kernel.do_complete("%%", len("%%"))
    assert "%%file" in comp["matches"]
    assert "%%html" in comp["matches"]


def test_inspect() -> None:
    kernel = get_kernel()
    kernel.do_inspect("%lsmagic", len("%lsmagic"))
    log_text = get_log_text(kernel)
    assert "list the current line and cell magics" in log_text

    kernel.do_inspect("%lsmagic ", len("%lsmagic") + 1)


@pytest.mark.skipif(
    sys.platform == "win32", reason="path completion format differs on Windows"
)
def test_path_complete() -> None:
    kernel = get_kernel()
    comp = kernel.do_complete("~/.ipytho", len("~/.ipytho"))
    assert comp["matches"] == ["ipython/"]

    paths = [
        p for p in os.listdir(os.getcwd()) if not p.startswith(".") and "-" not in p
    ]

    for path in paths:
        comp = kernel.do_complete(path, len(path) - 1)

        if os.path.isdir(path):
            path = path.split()[-1]
            assert path + os.sep in comp["matches"], "'%s' not in '%s'" % (
                path + os.sep,
                comp["matches"],
            )
        else:
            path = path.split()[-1]
            assert path in comp["matches"], (comp["matches"], path)


@pytest.mark.skipif(
    sys.platform == "win32", reason="path completion format differs on Windows"
)
def test_ls_path_complete() -> None:
    kernel = get_kernel()
    comp = kernel.do_complete("! ls ~/.ipytho", len("! ls ~/.ipytho"))
    assert comp["matches"] == ["ipython/"], comp


def test_history() -> None:
    kernel = get_kernel()
    kernel.do_execute("!ls", False)
    kernel.do_execute("%cd ~", False)
    kernel.do_shutdown(False)

    with open(kernel.hist_file, "rb") as fid:
        text = fid.read().decode("utf-8", "replace")

    assert "!ls" in text
    assert "%cd" in text

    kernel = get_kernel()
    kernel.do_history(None, None, None)
    assert "!ls" in "".join(kernel.hist_cache)
    assert "%cd ~"


def test_sticky_magics() -> None:
    kernel = get_kernel()
    kernel.do_execute("%%%html\nhello", None)
    text = get_log_text(kernel)

    assert "html added to session magics" in text
    kernel.do_execute("<b>hello</b>", None)
    kernel.do_execute("%%%html", None)
    text = get_log_text(kernel)
    assert text.count("Display Data") == 2
    assert "html removed from session magics" in text


def test_shell_partial_quote() -> None:
    kernel = get_kernel()
    kernel.do_execute('%cd "/home/', False)
    text = get_log_text(kernel)
    # POSIX: "No such file or directory: '"/home/'"
    # Windows: "[WinError 123] ... syntax is incorrect: '"/home/'"
    assert """'"/home/'""" in text, text


def test_other_kernels() -> None:
    class SchemeKernel(MetaKernel):
        help_suffix = {}  # type: ignore[assignment,var-annotated]

        def do_execute_direct(self, code, *args, **kwargs):
            return "OK"

    kernel = get_kernel(SchemeKernel)
    resp = kernel.do_execute("dir?", None)
    assert len(resp["payload"]) == 0, "should handle this, rather than using help"
    resp = kernel.do_execute("?dir?", None)
    assert len(resp["payload"]) == 1, "should use help"
    message = resp["payload"][0]["data"]["text/plain"]
    assert "Sorry, no help is available on 'dir?'." == message, message

    content = kernel.do_inspect("dir", len("dir"))
    assert content is not None
    assert content["status"] == "aborted" and not content["found"], (
        "do_inspect should abort, and be not found"
    )

    content = kernel.do_inspect("len(dir", len("len(dir"))
    assert content is not None
    assert content["status"] == "aborted" and not content["found"], (
        "do_inspect should abort, and be not found"
    )

    content = kernel.do_inspect("(dir", len("(dir"))
    assert content is not None
    assert content["status"] == "aborted" and not content["found"], (
        "do_inspect should abort, and be not found"
    )

    # Now change it so that there is help available:
    kernel.get_kernel_help_on = (  # type: ignore[method-assign]
        lambda info, level=0, none_on_fail=False: (
            "Help is available on '%s'." % info["obj"]
        )
    )
    content = kernel.do_inspect("dir", len("dir"))
    assert content is not None
    message = content["data"]["text/plain"]
    match = re.match("Help is available on '(.*)'", message)
    assert match is not None
    assert match.groups()[0] == "dir", message + " for 'dir'"

    content = kernel.do_inspect("len(dir", len("len(dir"))
    assert content is not None
    message = content["data"]["text/plain"]
    match = re.match("Help is available on '(.*)'", message)
    assert match is not None
    assert match.groups()[0] == "dir", message + " for 'dir'"

    content = kernel.do_inspect("(dir", len("(dir"))
    assert content is not None
    message = content["data"]["text/plain"]
    match = re.match("Help is available on '(.*)'", message)
    assert match is not None
    assert match.groups()[0] == "dir", message + " for 'dir'"


def test_do_execute_meta() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("~~META~~: reset")
    text = get_log_text(kernel)
    assert "RESET" in text, text
    clear_log_text(kernel)

    kernel.do_execute("~~META~~: stop")
    text = get_log_text(kernel)
    assert "STOP" in text, text
    clear_log_text(kernel)

    kernel.do_execute("~~META~~: step")
    text = get_log_text(kernel)
    assert "STEP" in text, text
    clear_log_text(kernel)

    kernel.do_execute("~~META~~: inspect something")
    text = get_log_text(kernel)
    assert "INSPECT" in text, text
    clear_log_text(kernel)


def test_do_execute_meta2() -> None:
    kernel = get_kernel()
    for code in ["reset, stop", "step", "inspect ", "garbage"]:
        with pytest.raises(Exception):  # noqa: B017
            kernel.do_execute("~~META~~: %s" % code)


def test_misc() -> None:
    class TestKernel(MetaKernel):
        def do_execute_file(self, filename):
            self.Print("This language does not support running files")

        def do_function_direct(self, f, arg):
            self.Print("%s(%s)" % (f, self.repr(arg)))

        def repr(self, arg):
            return "XXX"

    kernel = get_kernel(TestKernel)
    assert kernel.do_execute_direct("garbage") is None
    kernel.do_execute_file("hello.txt")
    assert "This language does not support" in get_log_text(kernel)

    clear_log_text(kernel)

    kernel.do_function_direct("hello", "world")
    text = get_log_text(kernel)
    assert "hello(XXX)" in text, text
    kernel.restart_kernel()

    ret = kernel.do_is_complete("hello\n")
    assert ret == {"status": "complete"}

    assert kernel.do_inspect("hello", 10) is None


def test_error_display_string() -> None:
    kernel = get_kernel()
    kernel.Error_display("something went wrong")
    text = get_log_text(kernel)
    assert "Error: something went wrong" in text


def test_error_display_non_string() -> None:
    kernel = get_kernel()
    display_calls: list[Any] = []
    kernel.Display = lambda *args, **kwargs: display_calls.append(args)  # type: ignore[method-assign]
    kernel.Error_display(42)
    # non-string items are routed to Display, not the error message
    assert display_calls == [(42,)]
    text = get_log_text(kernel)
    # the error message is empty (just a newline)
    assert "Error: \n" in text


def test_error_display_mixed() -> None:
    kernel = get_kernel()
    display_calls: list[Any] = []
    kernel.Display = lambda *args, **kwargs: display_calls.append(args)  # type: ignore[method-assign]
    kernel.Error_display("oops", 99, "again")
    text = get_log_text(kernel)
    # string items join into the error message
    assert "Error: oops again" in text
    # non-string item goes to Display
    assert display_calls == [(99,)]


def test_error_display_redirect_to_log() -> None:
    kernel = get_kernel()
    kernel.redirect_to_log = True
    kernel.Error_display("logged error message")
    text = get_log_text(kernel)
    # info-level log contains the message when redirect_to_log is True
    assert "logged error message" in text
    kernel.redirect_to_log = False


def test_do_execute_meta_direct() -> None:
    kernel = get_kernel(EvalKernel)
    assert kernel.do_execute_meta("reset") == "RESET"
    assert kernel.do_execute_meta("stop") == "STOP"
    assert kernel.do_execute_meta("step") == "STEP"
    assert kernel.do_execute_meta("inspect something") == "INSPECT"
    with pytest.raises(Exception, match="Unknown meta command"):
        kernel.do_execute_meta("bogus")


def test_do_execute_meta_base_direct() -> None:
    kernel = get_kernel()
    for code in ["reset", "stop", "step", "inspect foo"]:
        with pytest.raises(Exception, match="does not implement this meta command"):
            kernel.do_execute_meta(code)
    with pytest.raises(Exception, match="Unknown meta command"):
        kernel.do_execute_meta("garbage")


def test_get_magic_args_no_magic() -> None:
    kernel = get_kernel()
    result = kernel.get_magic_args("just plain text")
    assert result is None


def test_get_magic_args_line_magic() -> None:
    kernel = get_kernel()
    result: Any = kernel.get_magic_args("%cd /tmp")
    assert result is not None
    args, _kwargs, _old_args = result
    assert "/tmp" in args


def test_get_magic_args_no_args_magic() -> None:
    kernel = get_kernel()
    result: Any = kernel.get_magic_args("%lsmagic")
    assert result is not None
    args, kwargs, _old_args = result
    assert args == []
    assert kwargs == {}


def test_get_magic_args_unknown_magic() -> None:
    kernel = get_kernel()
    result = kernel.get_magic_args("%nonexistent_magic_xyz")
    assert result is None


class TestMakeSubkernel:
    def test_no_ipython_copies_session(self) -> None:
        parent = get_kernel()
        child = get_kernel()
        with unittest.mock.patch("IPython.get_ipython", return_value=None):
            child.makeSubkernel(parent)
        assert child.session is parent.session

    def test_no_ipython_copies_send_response(self) -> None:
        parent = get_kernel()
        child = get_kernel()
        with unittest.mock.patch("IPython.get_ipython", return_value=None):
            child.makeSubkernel(parent)
        assert child.send_response == parent.send_response

    def test_no_ipython_copies_display(self) -> None:
        parent = get_kernel()
        child = get_kernel()
        with unittest.mock.patch("IPython.get_ipython", return_value=None):
            child.makeSubkernel(parent)
        assert child.Display == parent.Display

    def test_with_ipython_copies_session_from_shell(self) -> None:
        parent = get_kernel()
        child = get_kernel()
        real_session = ss.Session()
        mock_shell = unittest.mock.MagicMock()
        mock_shell.kernel.session = real_session
        with unittest.mock.patch("IPython.get_ipython", return_value=mock_shell):
            child.makeSubkernel(parent)
        assert child.session is real_session

    def test_with_ipython_sets_display_to_ipython_display(self) -> None:
        parent = get_kernel()
        child = get_kernel()
        mock_display = unittest.mock.MagicMock()
        mock_shell = unittest.mock.MagicMock()
        mock_shell.kernel.session = ss.Session()
        with unittest.mock.patch("IPython.get_ipython", return_value=mock_shell):
            with unittest.mock.patch("IPython.display.display", mock_display):
                child.makeSubkernel(parent)
        assert child.Display is mock_display

    def test_with_ipython_sets_send_response_to_shell_response(self) -> None:
        parent = get_kernel()
        child = get_kernel()
        mock_shell = unittest.mock.MagicMock()
        mock_shell.kernel.session = ss.Session()
        with unittest.mock.patch("IPython.get_ipython", return_value=mock_shell):
            child.makeSubkernel(parent)
        assert child.send_response == child._send_shell_response


class _FakeApp(LoggingConfigurable):
    """Minimal stand-in for an IPKernelApp with extra_args."""


def _make_kernel_with_parent(extra_args: list[str]) -> MetaKernel:
    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.PUB)
    parent = _FakeApp()
    parent.extra_args = extra_args  # type: ignore[attr-defined]
    return MetaKernel(
        session=ss.Session(), iopub_socket=sock, log=get_log(), parent=parent
    )


class TestConstructorWithExtraArgs:
    def test_executes_each_file(self) -> None:
        calls: list[str] = []
        with unittest.mock.patch.object(
            MetaKernel, "do_execute_file", side_effect=lambda f: calls.append(f)
        ):
            _make_kernel_with_parent(["a.py", "b.py"])
        assert calls == ["a.py", "b.py"]

    def test_exception_from_file_does_not_propagate(self) -> None:
        with unittest.mock.patch.object(
            MetaKernel, "do_execute_file", side_effect=RuntimeError("boom")
        ):
            _make_kernel_with_parent(["bad.py"])  # must not raise

    def test_redirect_to_log_restored_after_execution(self) -> None:
        with unittest.mock.patch.object(MetaKernel, "do_execute_file"):
            kernel = _make_kernel_with_parent(["a.py"])
        assert kernel.redirect_to_log is False

    def test_no_extra_args_skips_execution(self) -> None:
        with unittest.mock.patch.object(MetaKernel, "do_execute_file") as mock_exec:
            _make_kernel_with_parent([])
        mock_exec.assert_not_called()


class TestGetVariable:
    def test_base_returns_none(self) -> None:
        kernel = get_kernel()
        assert kernel.get_variable("x") is None

    def test_subclass_returns_set_variable(self) -> None:
        kernel = get_kernel(EvalKernel)
        kernel.set_variable("x", 42)
        assert kernel.get_variable("x") == 42

    def test_subclass_raises_for_unknown_variable(self) -> None:
        kernel = get_kernel(EvalKernel)
        with pytest.raises(KeyError):
            kernel.get_variable("nonexistent_var")


class TestInitializeDebug:
    def test_base_returns_empty_string(self) -> None:
        kernel = get_kernel()
        assert kernel.initialize_debug("some code") == ""

    def test_base_returns_empty_string_for_empty_input(self) -> None:
        kernel = get_kernel()
        assert kernel.initialize_debug("") == ""


class TestPostExecuteSilent:
    def test_send_response_not_called_for_normal_retval(self) -> None:
        kernel = get_kernel(EvalKernel)
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.post_execute("result", "code", silent=True)
        mock_send.assert_not_called()

    def test_send_response_not_called_for_exception_wrapper(self) -> None:
        kernel = get_kernel(EvalKernel)
        kernel.kernel_resp = {"status": "ok"}
        exc = ExceptionWrapper("ValueError", "bad", ["traceback line"])
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.post_execute(exc, "code", silent=True)
        mock_send.assert_not_called()

    def test_send_response_not_called_for_none_retval(self) -> None:
        kernel = get_kernel(EvalKernel)
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.post_execute(None, "code", silent=True)
        mock_send.assert_not_called()

    def test_history_variables_updated(self) -> None:
        # post_execute writes back _ii and _iii as Python attrs; _i goes only
        # through set_variable into the kernel env.
        kernel = get_kernel(EvalKernel)
        kernel.post_execute(None, "first", silent=True)
        kernel.post_execute(None, "second", silent=True)
        assert kernel._ii == "second"
        assert kernel._iii == "first"

    def test_out_variables_updated_for_non_none_retval(self) -> None:
        # post_execute writes back __ as a Python attr; _ goes only through
        # set_variable into the kernel env.
        kernel = get_kernel(EvalKernel)
        kernel.post_execute(42, "code", silent=True)
        assert kernel.__ == 42

    def test_error_status_set_for_exception_wrapper(self) -> None:
        kernel = get_kernel(EvalKernel)
        kernel.kernel_resp = {"status": "ok"}
        exc = ExceptionWrapper("NameError", "x not defined", [])
        kernel.post_execute(exc, "code", silent=True)
        assert kernel.kernel_resp["status"] == "error"


class TestDoIsComplete:
    def test_regular_code_ending_with_newline_is_complete(self) -> None:
        kernel = get_kernel()
        assert kernel.do_is_complete("x = 1\n") == {"status": "complete"}

    def test_regular_code_without_newline_is_incomplete(self) -> None:
        kernel = get_kernel()
        assert kernel.do_is_complete("x = 1") == {"status": "incomplete"}

    def test_magic_ending_with_newline_is_complete(self) -> None:
        kernel = get_kernel()
        assert kernel.do_is_complete("%cd /tmp\n") == {"status": "complete"}

    def test_magic_without_newline_is_incomplete(self) -> None:
        kernel = get_kernel()
        assert kernel.do_is_complete("%cd /tmp") == {"status": "incomplete"}

    def test_empty_string_is_incomplete(self) -> None:
        kernel = get_kernel()
        assert kernel.do_is_complete("") == {"status": "incomplete"}

    def test_bare_newline_is_complete(self) -> None:
        kernel = get_kernel()
        assert kernel.do_is_complete("\n") == {"status": "complete"}


class TestPrintWriteErrorRedirectToLog:
    # --- Print ---

    def test_print_redirect_to_log_calls_log_info(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = True
        clear_log_text(kernel)
        kernel.Print("hello")
        assert "hello" in get_log_text(kernel)

    def test_print_redirect_to_log_skips_send_response(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = True
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.Print("hello")
        mock_send.assert_not_called()

    def test_print_no_redirect_calls_send_response(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = False
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.Print("hello")
        mock_send.assert_called_once()
        _, msg_type, content = mock_send.call_args[0]
        assert msg_type == "stream"
        assert content["name"] == "stdout"
        assert "hello" in content["text"]

    # --- Write ---

    def test_write_redirect_to_log_calls_log_info(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = True
        clear_log_text(kernel)
        kernel.Write("writing")
        assert "writing" in get_log_text(kernel)

    def test_write_redirect_to_log_skips_send_response(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = True
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.Write("writing")
        mock_send.assert_not_called()

    def test_write_no_redirect_calls_send_response(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = False
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.Write("writing")
        mock_send.assert_called_once()
        _, msg_type, content = mock_send.call_args[0]
        assert msg_type == "stream"
        assert content["name"] == "stdout"
        assert "writing" in content["text"]

    # --- Error ---

    def test_error_redirect_to_log_calls_log_info(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = True
        clear_log_text(kernel)
        kernel.Error("oops")
        assert "oops" in get_log_text(kernel)

    def test_error_redirect_to_log_skips_send_response(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = True
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.Error("oops")
        mock_send.assert_not_called()

    def test_error_no_redirect_calls_send_response(self) -> None:
        kernel = get_kernel()
        kernel.redirect_to_log = False
        with unittest.mock.patch.object(kernel, "send_response") as mock_send:
            kernel.Error("oops")
        mock_send.assert_called_once()
        _, msg_type, content = mock_send.call_args[0]
        assert msg_type == "stream"
        assert content["name"] == "stderr"
        assert "oops" in content["text"]


def teardown() -> None:
    if os.path.exists("TEST.txt"):
        os.remove("TEST.txt")
