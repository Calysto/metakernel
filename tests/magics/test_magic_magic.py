import asyncio

from tests.utils import get_kernel, get_log_text


def test_magic_magic() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%magic", None))
    text = get_log_text(kernel)
    assert "! COMMAND ... - execute command in shell" in text


def test_get_magic_returns_none_without_magic_info() -> None:
    """get_magic returns None immediately when info['magic'] is falsy."""
    kernel = get_kernel()
    magic = kernel.line_magics["magic"]
    assert magic.get_magic({"magic": None}) is None


def test_get_magic_returns_none_for_unmatched_type() -> None:
    """get_magic returns None when the named magic doesn't exist for that type."""
    kernel = get_kernel()
    magic = kernel.line_magics["magic"]
    info = {"magic": {"name": "no_such_magic", "type": "line", "args": "", "code": ""}}
    assert magic.get_magic(info) is None


def test_get_magic_with_get_args_true() -> None:
    """get_magic(get_args=True) returns the parsed args instead of calling the magic."""
    kernel = get_kernel()
    magic = kernel.line_magics["magic"]
    info = {"magic": {"name": "python", "type": "line", "args": "1 + 1", "code": ""}}
    result = magic.get_magic(info, get_args=True)
    assert result is not None


def test_get_magic_sticky_add_and_remove() -> None:
    """A sticky magic is added to the session on first use and removed on second."""
    kernel = get_kernel()
    magic = kernel.line_magics["magic"]
    info = {"magic": {"name": "python", "type": "sticky", "args": "", "code": ""}}

    magic.get_magic(info)
    sname = "%%python"
    assert sname in kernel.sticky_magics
    text = get_log_text(kernel)
    assert "added to session magics" in text

    result = magic.get_magic(info)
    assert sname not in kernel.sticky_magics
    text = get_log_text(kernel)
    assert "removed from session magics" in text
    assert result is not None
