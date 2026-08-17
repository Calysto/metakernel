"""Tests for the PowerShell prompt handshake in :func:`metakernel.replwrap.powershell`.

These drive a scripted stand-in for the child process, so they exercise the
Windows code path on every platform.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from metakernel import pexpect, replwrap
from metakernel.pexpect import TIMEOUT
from metakernel.replwrap import PEXPECT_PROMPT

BANNER_HEAD = "Windows PowerShell\r\n"
# The rest of the banner, ending in PowerShell's own first prompt.  It arrives
# only once the first line has been sent, which is what makes the handshake
# racy against a real shell.
BANNER_TAIL = (
    "Copyright (C) Microsoft Corporation. All rights reserved.\r\n\r\nPS C:\\> "
)

LS_COMMAND = "ls C:/Users/RUNNER~1/AppData/Local/Temp/tmp_pmy5t3z"
LS_OUTPUT = (
    "\r\n    Directory: C:\\Users\\RUNNER~1\\AppData\\Local\\Temp\r\n\r\n"
    "Mode                 LastWriteTime         Length Name\r\n"
    "----                 -------------   ------------ ----\r\n"
    "-a---           8/17/2026 10:04 AM              0 tmp_pmy5t3z\r\n\r\n"
)


class FakePowerShell:
    """A scripted stand-in for a PowerShell child process.

    PowerShell echoes each line it is sent, then writes that command's output
    followed by the next prompt.  ``Function prompt`` lines are interpreted the
    way PowerShell would: the double-quoted pieces are concatenated and become
    the prompt from then on.
    """

    crlf = "\r\n"

    def __init__(self, outputs: dict[str, str] | None = None) -> None:
        self.buffer = BANNER_HEAD
        self.pending = [BANNER_TAIL]
        self.outputs = outputs or {}
        self.prompt = "PS C:\\> "
        self.echo = True
        self.before = ""
        self.after = ""
        self.sent: list[str] = []

    def expect(self, patterns: Any, timeout: Any = None) -> int:
        if not isinstance(patterns, list):
            patterns = [patterns]
        best_index = None
        best_match = None
        for index, pattern in enumerate(patterns):
            if pattern is None:
                continue
            match = re.search(pattern, self.buffer)
            if match is None:
                continue
            if best_match is None or match.start() < best_match.start():
                best_index, best_match = index, match
        if best_match is None or best_index is None:
            raise TIMEOUT("no match in buffer")
        self.before = self.buffer[: best_match.start()]
        self.after = best_match.group()
        self.buffer = self.buffer[best_match.end() :]
        return best_index

    def readline(self) -> str:
        index = self.buffer.find(self.crlf)
        if index == -1:
            raise TIMEOUT("no complete line in buffer")
        line = self.buffer[: index + len(self.crlf)]
        self.buffer = self.buffer[index + len(self.crlf) :]
        return line

    def sendline(self, line: str) -> None:
        self.sent.append(line)
        if self.pending:
            self.buffer += self.pending.pop(0)
        self.buffer += line + self.crlf
        if line.startswith("Function prompt"):
            self.prompt = "".join(re.findall(r'"([^"]*)"', line))
        else:
            self.buffer += self.outputs.get(line, "")
        self.buffer += self.prompt

    def close(self) -> None:
        pass

    def terminate(self) -> None:
        pass

    def kill(self, sig: int) -> None:
        pass


@pytest.fixture
def repl(monkeypatch: pytest.MonkeyPatch) -> replwrap.REPLWrapper:
    child = FakePowerShell(outputs={LS_COMMAND: LS_OUTPUT})
    monkeypatch.setattr(pexpect, "spawnu", lambda *a, **kw: child)
    return replwrap.powershell()


def test_prompt_change_cmd_does_not_spell_out_the_prompt(
    repl: replwrap.REPLWrapper,
) -> None:
    """The command that installs the prompt must not contain the prompt.

    PowerShell echoes it back, and an echo containing the prompt is
    indistinguishable from the prompt itself.
    """
    assert repl.prompt_change_cmd is not None
    assert PEXPECT_PROMPT not in repl.prompt_change_cmd


def test_command_output_survives_the_prompt_handshake(
    repl: replwrap.REPLWrapper,
) -> None:
    """Output must not be dropped by a wrapper left one prompt behind."""
    streamed: list[str] = []
    repl.run_command('cd "C:/work"')
    repl.run_command(LS_COMMAND, stream_handler=streamed.append)
    assert "tmp_pmy5t3z" in "".join(streamed)
