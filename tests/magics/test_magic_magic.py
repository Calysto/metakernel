import asyncio

from tests.utils import get_kernel, get_log_text


def test_magic_magic() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%magic", None))
    text = get_log_text(kernel)
    assert "! COMMAND ... - execute command in shell" in text
