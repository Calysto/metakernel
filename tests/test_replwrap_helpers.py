"""Integration tests for replwrap helper functions python() and powershell()."""

from __future__ import annotations

import sys

import pytest

from metakernel import replwrap


@pytest.mark.skipif(
    sys.platform in ("win32", "darwin"),
    reason="python() requires a pty (not on Windows) and has REPL differences on macOS",
)
def test_python_repl() -> None:
    """python() starts a Python REPL that can evaluate expressions."""
    repl = replwrap.python(sys.executable)
    result = repl.run_command("1 + 1")
    assert result.strip() == "2"


@pytest.mark.skipif(
    sys.platform != "win32", reason="powershell() is only meaningful on Windows"
)
def test_powershell_repl() -> None:
    """powershell() starts a PowerShell REPL that can run commands."""
    repl = replwrap.powershell()
    result = repl.run_command("Write-Output hello")
    assert "hello" in result
