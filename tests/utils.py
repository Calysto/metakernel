from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from logging import Logger, StreamHandler
from typing import Any, TypeVar, overload

import zmq
from jupyter_client import session as ss

from metakernel import MetaKernel

__all__ = [
    "EvalKernel",
    "capture_send_messages",
    "clear_log_text",
    "get_kernel",
    "get_log",
    "get_log_text",
    "ss",
]

_KT = TypeVar("_KT", bound=MetaKernel)


class EvalKernel(MetaKernel):
    implementation = "Eval"
    implementation_version = "1.0"
    language = "python"
    language_version = "0.1"
    banner = "Eval kernel - evaluates simple Python statements and expressions"

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set a variable in the kernel language.
        """
        python_magic = self.line_magics["python"]
        python_magic.env[name] = value

    def get_variable(self, name: str) -> Any:
        """
        Get a variable from the kernel language.
        """
        python_magic = self.line_magics["python"]
        return python_magic.env[name]

    def do_execute_direct(self, code: str, silent: bool = False) -> Any:
        python_magic = self.line_magics["python"]
        return python_magic.eval(code.strip())

    def do_execute_meta(self, code: str) -> str | None:
        if code == "reset":
            return "RESET"
        elif code == "stop":
            return "STOP"
        elif code == "step":
            return "STEP"
        elif code.startswith("inspect "):
            return "INSPECT"
        else:
            raise Exception("Unknown meta command: '%s'" % code)

    def initialize_debug(self, code: str) -> str:
        return "highlight: [%s, %s, %s, %s]" % (0, 0, 1, 0)


def has_network() -> bool:
    import requests

    try:
        _ = requests.head("http://google.com", timeout=3)
        return True
    except requests.exceptions.RequestException:
        print("No internet connection available.")
    return False


def get_log() -> Logger:
    log = logging.getLogger("test")
    log.setLevel(logging.DEBUG)

    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    hdlr = StreamHandler(StringIO())
    hdlr.setLevel(logging.DEBUG)
    log.addHandler(hdlr)

    return log


@overload
def get_kernel() -> MetaKernel: ...


@overload
def get_kernel(kernel_class: type[_KT]) -> _KT: ...


def get_kernel(kernel_class: type[MetaKernel] = MetaKernel) -> MetaKernel:
    import weakref

    context = zmq.Context.instance()
    iopub_socket = context.socket(zmq.PUB)

    kernel = kernel_class(
        session=ss.Session(), iopub_socket=iopub_socket, log=get_log()
    )
    weakref.finalize(kernel, iopub_socket.close)
    return kernel


def clear_log_text(obj: Any) -> None:
    """Clear the log text from a kernel or a log object."""
    if isinstance(obj, MetaKernel):
        log = obj.log
    else:
        log = obj
    handler = log.handlers[0]
    assert isinstance(handler, StreamHandler)
    handler.stream.truncate(0)
    handler.stream.seek(0)


@contextmanager
def capture_send_messages(
    kernel: MetaKernel,
) -> Iterator[list[tuple[str, dict[str, Any]]]]:
    """Context manager that captures messages sent via kernel.send_response.

    Yields a list of (msg_type, content) tuples accumulated during the block.
    """
    sent: list[tuple[str, dict[str, Any]]] = []
    original = kernel.send_response

    def _capture(
        socket: Any, msg_type: str, content: dict[str, Any], **kwargs: Any
    ) -> Any:
        sent.append((msg_type, content))
        return original(socket, msg_type, content, **kwargs)

    kernel.send_response = _capture  # type: ignore[method-assign]
    try:
        yield sent
    finally:
        kernel.send_response = original  # type: ignore[method-assign]


def get_log_text(obj: Any) -> str:
    """Get the log text from a kernel or a log object."""
    if isinstance(obj, MetaKernel):
        log = obj.log
    else:
        log = obj
    handler = log.handlers[0]
    assert isinstance(handler, StreamHandler)
    return handler.stream.getvalue()  # type:ignore[no-any-return]
