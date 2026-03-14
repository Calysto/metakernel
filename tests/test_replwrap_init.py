"""Unit tests for REPLWrapper.__init__(), sendline(), and _expect_prompt() branches.

These tests avoid spawning real processes by mocking pexpect and child objects,
so they run on all platforms (unlike the integration tests in test_replwrap.py).
"""

from __future__ import annotations

import errno
import signal
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from metakernel import pexpect as mk_pexpect
from metakernel.replwrap import PEXPECT_CONTINUATION_PROMPT, PEXPECT_PROMPT, REPLWrapper


def _make_child(echo: bool = False) -> MagicMock:
    """Return a mock pexpect child with the given echo attribute."""
    child = MagicMock()
    child.echo = echo
    return child


class TestREPLWrapperInit:
    def test_str_command_spawns_child(self) -> None:
        """When cmd_or_spawn is a str, pexpect.spawnu is called to create the child."""
        mock_child = _make_child(echo=False)
        with patch("metakernel.pexpect.spawnu", return_value=mock_child) as mock_spawn:
            with patch.object(REPLWrapper, "_expect_prompt"):
                with patch("atexit.register"):
                    wrapper = REPLWrapper("bash", r"[$#]", None)
        mock_spawn.assert_called_once_with(
            "bash", echo=False, codec_errors="ignore", encoding="utf-8", env=None
        )
        assert wrapper.child is mock_child

    def test_custom_encoding_passed_to_spawnu(self) -> None:
        """When encoding is specified, pexpect.spawnu is called with that encoding.

        Reproduces issue #171: REPLWrapper hardcoded utf-8, breaking kernels like
        gnuplot on Windows that output in a different encoding (e.g. cp1252).
        """
        mock_child = _make_child(echo=False)
        with patch("metakernel.pexpect.spawnu", return_value=mock_child) as mock_spawn:
            with patch.object(REPLWrapper, "_expect_prompt"):
                with patch("atexit.register"):
                    wrapper = REPLWrapper(
                        "gnuplot", r"gnuplot>", None, encoding="cp1252"
                    )
        mock_spawn.assert_called_once_with(
            "gnuplot", echo=False, codec_errors="ignore", encoding="cp1252", env=None
        )
        assert wrapper.child is mock_child

    def test_spawn_object_used_directly(self) -> None:
        """When cmd_or_spawn is not a str, it is assigned as child directly."""
        mock_child = _make_child(echo=False)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch("atexit.register"):
                wrapper = REPLWrapper(mock_child, r"[$#]", None)
        assert wrapper.child is mock_child

    def test_echo_disabled_when_child_echo_true_and_echo_false(self) -> None:
        """setecho(False) and waitnoecho() are called when child.echo=True and echo=False."""
        mock_child = _make_child(echo=True)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch("atexit.register"):
                REPLWrapper(mock_child, r"[$#]", None, echo=False)
        mock_child.setecho.assert_called_once_with(False)
        mock_child.waitnoecho.assert_called_once()

    def test_echo_not_disabled_when_child_echo_false(self) -> None:
        """setecho() is not called when child.echo is already False."""
        mock_child = _make_child(echo=False)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch("atexit.register"):
                REPLWrapper(mock_child, r"[$#]", None, echo=False)
        mock_child.setecho.assert_not_called()

    def test_echo_not_disabled_when_echo_param_true(self) -> None:
        """setecho() is not called when echo=True, even if child.echo is also True."""
        mock_child = _make_child(echo=True)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch("atexit.register"):
                REPLWrapper(mock_child, r"[$#]", None, echo=True)
        mock_child.setecho.assert_not_called()

    def test_prompt_change_cmd_none_sets_prompt_regex_directly(self) -> None:
        """When prompt_change_cmd is None, prompt_regex is taken from the argument directly."""
        mock_child = _make_child(echo=False)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch("atexit.register"):
                wrapper = REPLWrapper(mock_child, r"[$#]", None)
        assert wrapper.prompt_regex == r"[$#]"
        assert wrapper.prompt_change_cmd is None

    def test_prompt_change_cmd_not_none_calls_set_prompt(self) -> None:
        """When prompt_change_cmd is given, set_prompt is called and new prompt values stored."""
        mock_child = _make_child(echo=False)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch.object(REPLWrapper, "set_prompt") as mock_set:
                with patch("atexit.register"):
                    wrapper = REPLWrapper(mock_child, r"[$#]", "PS1={0!r} PS2={1!r}")
        formatted = f"PS1={PEXPECT_PROMPT!r} PS2={PEXPECT_CONTINUATION_PROMPT!r}"
        mock_set.assert_called_once_with(r"[$#]", formatted)
        assert wrapper.prompt_regex == PEXPECT_PROMPT

    def test_extra_init_cmd_runs_command(self) -> None:
        """When extra_init_cmd is given, run_command is called with it."""
        mock_child = _make_child(echo=False)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch.object(REPLWrapper, "run_command") as mock_run:
                with patch("atexit.register"):
                    REPLWrapper(
                        mock_child, r"[$#]", None, extra_init_cmd="export TERM=dumb"
                    )
        mock_run.assert_called_once_with("export TERM=dumb")

    def test_no_extra_init_cmd_skips_run_command(self) -> None:
        """When extra_init_cmd is None, run_command is not called."""
        mock_child = _make_child(echo=False)
        with patch.object(REPLWrapper, "_expect_prompt"):
            with patch.object(REPLWrapper, "run_command") as mock_run:
                with patch("atexit.register"):
                    REPLWrapper(mock_child, r"[$#]", None)
        mock_run.assert_not_called()


def _make_wrapper(**kwargs: Any) -> REPLWrapper:
    """Create a REPLWrapper with a mock child, bypassing real subprocess spawning."""
    mock_child = _make_child()
    with patch.object(REPLWrapper, "_expect_prompt"):
        with patch("atexit.register"):
            wrapper = REPLWrapper(mock_child, r"[$#]", None, **kwargs)
    return wrapper


class TestSendline:
    def test_echo_false_does_not_readline(self) -> None:
        """With echo=False, only sendline is called — readline is not."""
        wrapper = _make_wrapper(echo=False)
        wrapper.sendline("hello")
        wrapper.child.sendline.assert_called_once_with("hello")
        wrapper.child.readline.assert_not_called()

    def test_echo_true_calls_readline_after_sendline(self) -> None:
        """With echo=True, readline() is called after sendline() to consume the echo."""
        wrapper = _make_wrapper(echo=True)
        wrapper.sendline("hello")
        wrapper.child.sendline.assert_called_once_with("hello")
        wrapper.child.readline.assert_called_once()


class TestExpectPrompt:
    def test_prompt_emit_cmd_sends_line(self) -> None:
        """When prompt_emit_cmd is set, it is sent via sendline before waiting."""
        wrapper = _make_wrapper(prompt_emit_cmd="echo __ready__")
        wrapper.child.expect.return_value = 0
        with patch.object(wrapper, "sendline") as mock_send:
            wrapper._expect_prompt()
        mock_send.assert_called_once_with("echo __ready__")

    def test_no_prompt_emit_cmd_skips_sendline(self) -> None:
        """When prompt_emit_cmd is falsy, sendline is not called for it."""
        wrapper = _make_wrapper()
        wrapper.prompt_emit_cmd = None
        wrapper.child.expect.return_value = 0
        with patch.object(wrapper, "sendline") as mock_send:
            wrapper._expect_prompt()
        mock_send.assert_not_called()

    def test_stream_handler_delegates_to_expect_prompt_stream(self) -> None:
        """When _stream_handler is set, _expect_prompt_stream is called and its value returned."""
        wrapper = _make_wrapper()
        wrapper._stream_handler = lambda x: None
        with patch.object(
            wrapper, "_expect_prompt_stream", return_value=0
        ) as mock_stream:
            result = wrapper._expect_prompt()
        mock_stream.assert_called_once_with(
            [
                wrapper.prompt_regex,
                wrapper.continuation_prompt_regex,
                wrapper.stdin_prompt_regex,
            ],
            None,
        )
        assert result == 0

    def test_no_stream_handler_does_not_delegate(self) -> None:
        """When _stream_handler is None, _expect_prompt_stream is never called."""
        wrapper = _make_wrapper()
        wrapper._stream_handler = None
        wrapper.child.expect.return_value = 0
        with patch.object(wrapper, "_expect_prompt_stream") as mock_stream:
            wrapper._expect_prompt()
        mock_stream.assert_not_called()

    def test_line_handler_appends_crlf_to_expects(self) -> None:
        """When _line_handler is set, child.crlf is appended to the expects list."""
        wrapper = _make_wrapper()
        wrapper._line_handler = lambda x: None
        wrapper.child.crlf = "\r\n"
        wrapper.child.expect.return_value = 0
        wrapper._expect_prompt()
        expects_arg = wrapper.child.expect.call_args[0][0]
        assert "\r\n" in expects_arg

    def test_no_line_handler_does_not_append_crlf(self) -> None:
        """When _line_handler is None, child.crlf is not appended to expects."""
        wrapper = _make_wrapper()
        wrapper._line_handler = None
        wrapper.child.crlf = "\r\n"
        wrapper.child.expect.return_value = 0
        wrapper._expect_prompt()
        expects_arg = wrapper.child.expect.call_args[0][0]
        assert "\r\n" not in expects_arg

    def test_pos_0_returns_0(self) -> None:
        """pos=0 (main prompt matched) causes _expect_prompt to return 0."""
        wrapper = _make_wrapper()
        wrapper.child.expect.return_value = 0
        assert wrapper._expect_prompt() == 0

    def test_pos_1_returns_1(self) -> None:
        """pos=1 (continuation prompt matched) causes _expect_prompt to return 1."""
        wrapper = _make_wrapper()
        wrapper.child.expect.return_value = 1
        assert wrapper._expect_prompt() == 1

    def test_pos_2_without_stdin_handler_raises(self) -> None:
        """pos=2 (stdin prompt) with no _stdin_handler raises ValueError."""
        wrapper = _make_wrapper()
        wrapper._stdin_handler = None
        wrapper.child.expect.return_value = 2
        with pytest.raises(ValueError, match="Stdin Requested"):
            wrapper._expect_prompt()

    def test_pos_2_with_stdin_handler_calls_it_and_loops(self) -> None:
        """pos=2 with _stdin_handler calls the handler, sends response, then loops to prompt."""
        wrapper = _make_wrapper()
        wrapper._stdin_handler = lambda after: "response"
        wrapper.child.after = "Password: "
        wrapper.child.expect.side_effect = [2, 0]
        with patch.object(wrapper, "sendline") as mock_send:
            result = wrapper._expect_prompt()
        mock_send.assert_called_once_with("response")
        assert result == 0

    def test_pos_3_calls_line_handler_and_loops(self) -> None:
        """pos>=3 (newline) calls _line_handler with the buffered output, then loops."""
        wrapper = _make_wrapper()
        lines: list[str] = []
        wrapper._line_handler = lines.append
        wrapper.child.crlf = "\r\n"
        wrapper.child.before = "output line"
        wrapper.child.expect.side_effect = [3, 0]
        result = wrapper._expect_prompt()
        assert lines == ["output line"]
        assert result == 0


class TestRunCommand:
    def test_empty_command_raises(self) -> None:
        """An empty string has no cmdlines after splitlines(), raising ValueError."""
        wrapper = _make_wrapper()
        with pytest.raises(ValueError, match="No command was given"):
            wrapper.run_command("")

    def test_trailing_newline_appends_empty_line(self) -> None:
        """A trailing newline causes an extra empty string to be appended to cmdlines."""
        wrapper = _make_wrapper()
        wrapper.child.before = ""
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline") as mock_send:
                wrapper.run_command("cmd\n")
        sent = [c[0][0] for c in mock_send.call_args_list]
        assert sent == ["cmd", ""]

    def test_single_line_returns_output(self) -> None:
        """A single-line command returns child.before as the result."""
        wrapper = _make_wrapper()
        wrapper.child.before = "result"
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline"):
                result = wrapper.run_command("cmd")
        assert result == "result"

    def test_multiline_no_prompt_emit_cmd_calls_intermediate_expect(self) -> None:
        """Without prompt_emit_cmd, _expect_prompt is called between each submitted line."""
        wrapper = _make_wrapper()
        wrapper.prompt_emit_cmd = None
        wrapper.child.before = ""
        with patch.object(wrapper, "_expect_prompt", return_value=0) as mock_ep:
            with patch.object(wrapper, "sendline"):
                wrapper.run_command("line1\nline2")
        # once for the intermediate line, once for the final prompt
        assert mock_ep.call_count == 2

    def test_multiline_with_prompt_emit_cmd_skips_intermediate_expect(self) -> None:
        """With prompt_emit_cmd set, intermediate _expect_prompt calls are skipped."""
        wrapper = _make_wrapper(prompt_emit_cmd="echo __ready__")
        wrapper.child.before = ""
        with patch.object(wrapper, "_expect_prompt", return_value=0) as mock_ep:
            with patch.object(wrapper, "sendline"):
                wrapper.run_command("line1\nline2")
        # only the final prompt wait — no intermediate call
        assert mock_ep.call_count == 1

    def test_continuation_prompt_interrupts_and_raises(self) -> None:
        """When _expect_prompt returns 1 (continuation), interrupt is called and ValueError raised."""
        wrapper = _make_wrapper()
        with patch.object(wrapper, "_expect_prompt", return_value=1):
            with patch.object(wrapper, "sendline"):
                with patch.object(wrapper, "interrupt") as mock_interrupt:
                    with pytest.raises(ValueError, match="Continuation prompt"):
                        wrapper.run_command("incomplete")
        mock_interrupt.assert_called_once_with(continuation=True)

    def test_stream_handler_returns_empty_string(self) -> None:
        """When stream_handler is set, run_command returns '' regardless of output."""
        wrapper = _make_wrapper()
        wrapper.child.before = "ignored"
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline"):
                result = wrapper.run_command("cmd", stream_handler=lambda x: None)
        assert result == ""

    def test_line_handler_returns_empty_string(self) -> None:
        """When line_handler is set, run_command returns '' regardless of output."""
        wrapper = _make_wrapper()
        wrapper.child.before = "ignored"
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline"):
                result = wrapper.run_command("cmd", line_handler=lambda x: None)
        assert result == ""

    def test_no_handlers_returns_child_before(self) -> None:
        """With no stream/line handler, run_command returns the accumulated output."""
        wrapper = _make_wrapper()
        wrapper.child.before = "output"
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline"):
                result = wrapper.run_command("cmd")
        assert result == "output"


class TestInterrupt:
    @pytest.mark.skipif(
        sys.platform == "win32", reason="pexpect.pty not available on Windows"
    )
    def test_pty_not_none_calls_sendintr(self) -> None:
        """When pexpect.pty is available, child.sendintr() is used to interrupt."""
        wrapper = _make_wrapper()
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            wrapper.interrupt()
        wrapper.child.sendintr.assert_called_once()

    def test_pty_none_calls_kill_sigint(self) -> None:
        """When pexpect.pty is None, child.kill(SIGINT) is used instead."""
        wrapper = _make_wrapper()
        with patch.object(mk_pexpect, "pty", None):
            with patch.object(wrapper, "_expect_prompt", return_value=0):
                wrapper.interrupt()
        wrapper.child.kill.assert_called_once_with(signal.SIGINT)

    def test_continuation_and_force_prompt_sends_prompt_change_cmd(self) -> None:
        """continuation=True with _force_prompt_on_continuation sends prompt_change_cmd."""
        wrapper = _make_wrapper()
        wrapper._force_prompt_on_continuation = True
        wrapper.prompt_change_cmd = "PS1='>>> '"
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline") as mock_send:
                wrapper.interrupt(continuation=True)
        mock_send.assert_called_once_with("PS1='>>> '")

    def test_continuation_and_force_prompt_no_prompt_change_cmd_sends_empty(
        self,
    ) -> None:
        """When prompt_change_cmd is None, sendline('') is used as fallback."""
        wrapper = _make_wrapper()
        wrapper._force_prompt_on_continuation = True
        wrapper.prompt_change_cmd = None
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline") as mock_send:
                wrapper.interrupt(continuation=True)
        mock_send.assert_called_once_with("")

    def test_continuation_false_skips_sendline(self) -> None:
        """continuation=False skips the sendline even when _force_prompt_on_continuation=True."""
        wrapper = _make_wrapper()
        wrapper._force_prompt_on_continuation = True
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline") as mock_send:
                wrapper.interrupt(continuation=False)
        mock_send.assert_not_called()

    def test_force_prompt_false_skips_sendline(self) -> None:
        """_force_prompt_on_continuation=False skips sendline even with continuation=True."""
        wrapper = _make_wrapper()
        wrapper._force_prompt_on_continuation = False
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            with patch.object(wrapper, "sendline") as mock_send:
                wrapper.interrupt(continuation=True)
        mock_send.assert_not_called()

    def test_keyboard_interrupt_retries_expect_prompt(self) -> None:
        """A KeyboardInterrupt from _expect_prompt is caught and the loop retries."""
        wrapper = _make_wrapper()
        with patch.object(
            wrapper, "_expect_prompt", side_effect=[KeyboardInterrupt(), 0]
        ) as mock_ep:
            wrapper.interrupt()  # must not raise
        assert mock_ep.call_count == 2

    def test_returns_child_before(self) -> None:
        """interrupt() returns child.before after the prompt is received."""
        wrapper = _make_wrapper()
        wrapper.child.before = "interrupted output"
        with patch.object(wrapper, "_expect_prompt", return_value=0):
            result = wrapper.interrupt()
        assert result == "interrupted output"


class TestTerminate:
    @pytest.mark.skipif(
        sys.platform == "win32", reason="pexpect.pty not available on Windows"
    )
    def test_pty_not_none_calls_close_and_terminate(self) -> None:
        """When pexpect.pty is available, child.close() then child.terminate() are called."""
        wrapper = _make_wrapper()
        wrapper.child.terminate.return_value = "done"
        result = wrapper.terminate()
        wrapper.child.close.assert_called_once()
        wrapper.child.terminate.assert_called_once()
        assert result == "done"

    def test_pty_none_calls_kill_sigterm(self) -> None:
        """When pexpect.pty is None, child.kill(SIGTERM) is called."""
        wrapper = _make_wrapper()
        with patch.object(mk_pexpect, "pty", None):
            wrapper.terminate()
        wrapper.child.kill.assert_called_once_with(signal.SIGTERM)

    def test_pty_none_kill_raises_eacces_is_ignored(self) -> None:
        """An EACCES error from kill() is silently swallowed."""
        wrapper = _make_wrapper()
        wrapper.child.kill.side_effect = OSError(errno.EACCES, "Permission denied")
        with patch.object(mk_pexpect, "pty", None):
            wrapper.terminate()  # must not raise

    def test_pty_none_kill_raises_other_errno_is_reraised(self) -> None:
        """Any non-EACCES error from kill() is re-raised."""
        wrapper = _make_wrapper()
        wrapper.child.kill.side_effect = OSError(errno.EPERM, "Operation not permitted")
        with patch.object(mk_pexpect, "pty", None):
            with pytest.raises(OSError):
                wrapper.terminate()
