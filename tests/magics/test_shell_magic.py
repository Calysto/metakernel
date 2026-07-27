# force locale to C to get consistent error messages
import asyncio
import os
import sys
from types import ModuleType
from typing import Any

import pytest

from tests.utils import get_kernel, get_log_text


def _magic_module(magic: Any) -> ModuleType:
    """The magics loader imports magic files as bare top-level modules
    (e.g. `shell_magic`), separate from the `metakernel.magics.shell_magic`
    package import. Patch targets must go through the module a given magic
    instance actually belongs to."""
    return sys.modules[type(magic).__module__]


os.environ["LC_ALL"] = "C"
os.environ["LANG"] = "C"
os.environ["LANGUAGE"] = "C"


@pytest.mark.skipif(
    sys.platform == "win32", reason="bash completion not available on Windows"
)
def test_shell_magic() -> None:
    kernel = get_kernel()

    text = "%shell ech"
    comp = asyncio.run(kernel.do_complete(text, len(text)))

    assert "echo" in comp["matches"]

    helpstr = kernel.get_help_on("!cat")
    assert "Sorry, no help" not in helpstr, helpstr

    helpstr = kernel.get_help_on("%%shell cat", level=1)
    assert "Sorry, no help" not in helpstr

    helpstr = kernel.get_help_on("!lkjalskdfj")
    assert "Sorry, no help" in helpstr


@pytest.mark.skipif(
    sys.platform == "win32", reason="cat/echo shell commands not available on Windows"
)
def test_shell_magic2() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute('!cat "%s"' % __file__, False))
    log_text = get_log_text(kernel)
    assert "metakernel.py" in log_text

    asyncio.run(kernel.do_execute('!!\necho "hello"\necho "goodbye"', None))
    log_text = get_log_text(kernel)
    assert '"hello"' in log_text
    assert '"goodbye"' in log_text


def test_shell_magic3() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("!lalkjds"))
    text = get_log_text(kernel)
    # POSIX: ": command not found", Windows: "is not recognized as the name of a cmdlet"
    assert ": command not found" in text or "is not recognized" in text, text


@pytest.mark.skipif(sys.platform == "win32", reason="posix-only shell behavior")
def test_line_shell_changes_directory_when_cwd_exists(monkeypatch, tmp_path) -> None:
    """When eval("pwd") returns a real, existing path, the process chdir's to it."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]

    def fake_eval(cmd, incremental=False):
        if cmd == "pwd":
            return str(tmp_path)
        return ""

    monkeypatch.setattr(magic, "eval", fake_eval)
    original_cwd = os.getcwd()
    try:
        magic.line_shell("true")
        assert os.getcwd() == str(tmp_path)
    finally:
        os.chdir(original_cwd)


def test_line_shell_windows_cmd_uses_echo_percent_cd(monkeypatch) -> None:
    """When self.cmd == 'cmd' (Windows), cwd is queried via 'echo %cd%'."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]
    magic.cmd = "cmd"
    calls = []

    def fake_eval(cmd, incremental=False):
        calls.append(cmd)
        return ""

    monkeypatch.setattr(magic, "eval", fake_eval)
    magic.line_shell("dir")
    assert "echo %cd%" in calls


@pytest.mark.skipif(sys.platform == "win32", reason="posix-only shell behavior")
def test_start_process_terminates_existing_repl() -> None:
    """Calling start_process() again terminates the previous repl child."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]
    magic.start_process()
    assert magic.repl is not None
    magic.start_process()
    assert magic.repl is not None


@pytest.mark.skipif(sys.platform == "win32", reason="posix-only shell behavior")
def test_start_process_falls_back_to_sh(monkeypatch) -> None:
    """When bash isn't available but sh is, sh is used instead."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]
    magic.cmd = None
    magic.repl = None
    sm = _magic_module(magic)

    def fake_which(cmd):
        return "/bin/sh" if cmd == "sh" else None

    monkeypatch.setattr(sm.pexpect, "which", fake_which)
    fake_repl = object()
    monkeypatch.setattr(sm, "bash", lambda command=None: fake_repl)
    magic.start_process()
    assert magic.cmd == "sh"
    assert magic.repl is fake_repl


@pytest.mark.skipif(sys.platform == "win32", reason="posix-only shell behavior")
def test_start_process_raises_without_bash_or_sh(monkeypatch) -> None:
    """When neither bash nor sh are found, a clear exception is raised."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]
    magic.cmd = None
    magic.repl = None
    sm = _magic_module(magic)
    monkeypatch.setattr(sm.pexpect, "which", lambda cmd: None)
    with pytest.raises(Exception, match="was not found or was not executable"):
        magic.start_process()


def test_start_process_uses_powershell_on_windows(monkeypatch) -> None:
    """On Windows (os.name == 'nt'), start_process() uses powershell."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]
    magic.cmd = None
    magic.repl = None
    sm = _magic_module(magic)

    class FakeOS:
        name = "nt"

    # `sm.os` is the real stdlib `os` module (a process-wide singleton), so
    # monkeypatching `os.name` directly would corrupt pathlib's platform
    # detection for the rest of the test session. Replace the module-level
    # `os` reference instead, scoped to this test only.
    monkeypatch.setattr(sm, "os", FakeOS())
    fake_repl = object()
    monkeypatch.setattr(sm, "powershell", lambda: fake_repl)
    magic.start_process()
    assert magic.cmd == "powershell"
    assert magic.repl is fake_repl


def test_get_completions_cmd_returns_empty() -> None:
    """On Windows cmd shell, get_completions is a no-op."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]
    magic.cmd = "cmd"
    assert magic.get_completions({"code": "ech"}) == []


def test_get_help_on_cmd_uses_help_command(monkeypatch) -> None:
    """On Windows cmd shell, get_help_on runs 'help <expr>'."""
    kernel = get_kernel()
    magic = kernel.line_magics["shell"]
    magic.cmd = "cmd"
    monkeypatch.setattr(magic, "eval", lambda cmd: "HELP for dir")
    result = magic.get_help_on({"code": "dir"})
    assert "HELP for dir" in result
