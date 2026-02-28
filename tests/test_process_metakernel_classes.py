import sys
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from metakernel import MetaKernel
from metakernel.process_metakernel import (
    BashKernel,
    DynamicKernel,
    ProcessMetaKernel,
    TextOutput,
)
from tests.utils import get_kernel


@pytest.fixture(autouse=True)
def _restore_process_language_info():
    """Restore ProcessMetaKernel.language_info after each test.

    DynamicKernel.__init__ mutates the class-level dict in-place, so without
    this fixture the changes leak across tests.
    """
    original = dict(ProcessMetaKernel.language_info)
    yield
    ProcessMetaKernel.language_info.clear()
    ProcessMetaKernel.language_info.update(original)


# ---------------------------------------------------------------------------
# TextOutput
# ---------------------------------------------------------------------------


def test_textoutput_stores_output() -> None:
    t = TextOutput("some text")
    assert t.output == "some text"


def test_textoutput_repr_returns_output() -> None:
    t = TextOutput("hello world")
    assert repr(t) == "hello world"


def test_textoutput_repr_not_quoted() -> None:
    """repr(TextOutput) returns the raw string, unlike Python's repr("...")."""
    t = TextOutput("hello")
    assert repr(t) != repr("hello")  # str repr is "'hello'"; TextOutput repr is "hello"


# ---------------------------------------------------------------------------
# ProcessMetaKernel — concrete subclass used across tests
# ---------------------------------------------------------------------------


class _TestKernel(ProcessMetaKernel):
    _banner = "Test Kernel version 2.5.1"

    def makeWrapper(self) -> MagicMock:
        wrapper = MagicMock()
        wrapper.run_command.return_value = ""
        return wrapper


# ---------------------------------------------------------------------------
# banner and language_version
# ---------------------------------------------------------------------------


def test_banner_property() -> None:
    kernel = get_kernel(_TestKernel)
    assert kernel.banner == "Test Kernel version 2.5.1"


def test_language_version_extracted_from_banner() -> None:
    kernel = get_kernel(_TestKernel)
    assert kernel.language_version == "2.5.1"


def test_language_version_none_when_absent_from_banner() -> None:
    class _NoBannerKernel(ProcessMetaKernel):
        _banner = "No version info here"

        def makeWrapper(self) -> None:  # type: ignore[override]
            pass

    kernel = get_kernel(_NoBannerKernel)
    assert kernel.language_version is None


# ---------------------------------------------------------------------------
# do_execute_direct
# ---------------------------------------------------------------------------


def test_do_execute_direct_returns_none_for_blank_code() -> None:
    kernel = get_kernel(_TestKernel)
    assert kernel.do_execute_direct("   ") is None


def test_do_execute_direct_blank_code_does_not_call_run_command() -> None:
    kernel = get_kernel(_TestKernel)
    kernel.do_execute_direct("   ")
    assert kernel.wrapper is not None
    cast(MagicMock, kernel.wrapper.run_command).assert_not_called()


def test_do_execute_direct_calls_run_command_with_code() -> None:
    kernel = get_kernel(_TestKernel)
    kernel.do_execute_direct("echo hi")
    assert kernel.wrapper is not None
    mock_run = cast(MagicMock, kernel.wrapper.run_command)
    mock_run.assert_called_once()
    args, _ = mock_run.call_args
    assert args[0] == "echo hi"


def test_do_execute_direct_strips_trailing_whitespace_from_code() -> None:
    kernel = get_kernel(_TestKernel)
    kernel.do_execute_direct("echo hi\n\n")
    assert kernel.wrapper is not None
    args, _ = cast(MagicMock, kernel.wrapper.run_command).call_args
    assert args[0] == "echo hi"


def test_do_execute_direct_not_silent_passes_write_as_stream_handler() -> None:
    kernel = get_kernel(_TestKernel)
    kernel.do_execute_direct("ls")
    assert kernel.wrapper is not None
    _, kwargs = cast(MagicMock, kernel.wrapper.run_command).call_args
    assert kwargs["stream_handler"] == kernel.Write


def test_do_execute_direct_silent_passes_none_as_stream_handler() -> None:
    kernel = get_kernel(_TestKernel)
    mock_wrapper = MagicMock()
    mock_wrapper.run_command.return_value = ""
    kernel.wrapper = mock_wrapper
    kernel.do_execute_direct("ls", silent=True)
    _, kwargs = mock_wrapper.run_command.call_args
    assert kwargs["stream_handler"] is None


def test_do_execute_direct_silent_with_output_returns_textoutput() -> None:
    kernel = get_kernel(_TestKernel)
    mock_wrapper = MagicMock()
    mock_wrapper.run_command.return_value = "result text"
    kernel.wrapper = mock_wrapper
    result = kernel.do_execute_direct("echo hi", silent=True)
    assert isinstance(result, TextOutput)
    assert result.output == "result text"


def test_do_execute_direct_silent_with_no_output_returns_none() -> None:
    kernel = get_kernel(_TestKernel)
    mock_wrapper = MagicMock()
    mock_wrapper.run_command.return_value = ""
    kernel.wrapper = mock_wrapper
    assert kernel.do_execute_direct("echo hi", silent=True) is None


# ---------------------------------------------------------------------------
# check_exitcode
# ---------------------------------------------------------------------------


def test_check_exitcode_returns_zero_and_none() -> None:
    kernel = get_kernel(_TestKernel)
    code, trace = kernel.check_exitcode()
    assert code == 0
    assert trace is None


# ---------------------------------------------------------------------------
# makeWrapper
# ---------------------------------------------------------------------------


def test_make_wrapper_raises_not_implemented() -> None:
    class _AbstractKernel(ProcessMetaKernel):
        pass

    kernel = get_kernel(_AbstractKernel)
    with pytest.raises(NotImplementedError):
        kernel.makeWrapper()


# ---------------------------------------------------------------------------
# do_shutdown and restart_kernel
# ---------------------------------------------------------------------------


def test_do_shutdown_calls_terminate_on_wrapper() -> None:
    kernel = get_kernel(_TestKernel)
    mock_wrapper = MagicMock()
    kernel.wrapper = mock_wrapper
    kernel.do_shutdown(False)
    mock_wrapper.terminate.assert_called_once()


def test_do_shutdown_with_no_wrapper_does_not_raise() -> None:
    kernel = get_kernel(_TestKernel)
    kernel.wrapper = None
    kernel.do_shutdown(False)  # should not raise


def test_restart_kernel_replaces_wrapper() -> None:
    kernel = get_kernel(_TestKernel)
    kernel.do_execute_direct("echo hi")  # initialises self.wrapper
    first_wrapper = kernel.wrapper
    kernel.restart_kernel()
    assert kernel.wrapper is not first_wrapper


# ---------------------------------------------------------------------------
# BashKernel
# ---------------------------------------------------------------------------

_bash_skip = pytest.mark.skipif(
    sys.platform == "win32",
    reason="BashKernel requires bash/pexpect, not available on Windows",
)


@pytest.fixture()
def _fresh_bash_banner():
    """Reset BashKernel._banner so each test fetches it fresh."""
    original = BashKernel._banner
    BashKernel._banner = None
    yield
    BashKernel._banner = original


@_bash_skip
def test_bash_kernel_banner_contains_bash(_fresh_bash_banner) -> None:
    kernel = get_kernel(BashKernel)
    assert "bash" in kernel.banner.lower()


@_bash_skip
def test_bash_kernel_banner_contains_version(_fresh_bash_banner) -> None:
    kernel = get_kernel(BashKernel)
    assert "version" in kernel.banner.lower()


@_bash_skip
def test_bash_kernel_language_version_is_not_none(_fresh_bash_banner) -> None:
    kernel = get_kernel(BashKernel)
    assert kernel.language_version is not None


@_bash_skip
def test_bash_kernel_banner_is_cached(_fresh_bash_banner) -> None:
    # BashKernel.banner caches the result on the instance via self._banner.
    # Access banner twice; the second call must return the same value and the
    # instance attribute must be populated after the first access.
    kernel = get_kernel(BashKernel)
    banner1 = kernel.banner
    assert kernel._banner is not None  # cached on instance after first access
    banner2 = kernel.banner
    assert banner1 == banner2


# ---------------------------------------------------------------------------
# DynamicKernel
# ---------------------------------------------------------------------------


def test_dynamic_kernel_sets_all_attributes() -> None:
    with patch.object(MetaKernel, "__init__", return_value=None):
        k = DynamicKernel(
            "bash",
            "bash",
            mimetype="text/x-bash",
            implementation="bash_kernel",
            file_extension="sh",
            orig_prompt="[$#]",
            prompt_change="PS1='{0}'",
            extra_init_cmd="export PAGER=cat",
        )
    assert k.executable == "bash"
    assert k.language == "bash"
    assert k.implementation == "bash_kernel"
    assert k.orig_prompt == "[$#]"
    assert k.prompt_change == "PS1='{0}'"
    assert k.prompt_cmd is None
    assert k.extra_init_cmd == "export PAGER=cat"
    assert k.stdin_prompt_regex is None
    assert k.language_info["mimetype"] == "text/x-bash"
    assert k.language_info["language"] == "bash"
    assert k.language_info["file_extension"] == "sh"


def test_dynamic_kernel_default_attributes() -> None:
    with patch.object(MetaKernel, "__init__", return_value=None):
        k = DynamicKernel("python", "python")
    assert k.implementation == "metakernel"
    assert k.language_info["mimetype"] == "text/plain"
    assert k.language_info["file_extension"] == "txt"


def test_dynamic_kernel_make_wrapper_passes_correct_args() -> None:
    with (
        patch.object(MetaKernel, "__init__", return_value=None),
        patch("metakernel.process_metakernel.REPLWrapper") as mock_repl,
    ):
        k = DynamicKernel(
            "bash",
            "bash",
            orig_prompt="[$#]",
            prompt_change="PS1='{0}' PS2='{1}'",
        )
        k.makeWrapper()
    mock_repl.assert_called_once_with(
        "bash",
        "[$#]",
        "PS1='{0}' PS2='{1}'",
        prompt_emit_cmd=None,
        stdin_prompt_regex=None,
        extra_init_cmd=None,
    )
