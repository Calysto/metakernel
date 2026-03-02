import asyncio

from tests.utils import EvalKernel, get_kernel, get_log_text


def test_restart_magic() -> None:
    kernel = get_kernel(EvalKernel)

    asyncio.run(kernel.do_execute("a=1"))
    asyncio.run(kernel.do_execute("%restart"))
    asyncio.run(kernel.do_execute("a"))

    text = get_log_text(kernel)
    assert "NameError" in text
