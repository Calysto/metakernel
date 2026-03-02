import asyncio

from tests.utils import EvalKernel, clear_log_text, get_kernel, get_log_text


def test_run_magic() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(kernel.do_execute("%%run %s" % __file__.replace(".pyc", ".py")))
    asyncio.run(kernel.do_execute("TEST"))
    text = get_log_text(kernel)
    assert "42" in text, "Didn't run this file"

    clear_log_text(kernel)
    asyncio.run(
        kernel.do_execute(
            "%%run --language python %s" % __file__.replace(".pyc", ".py")
        )
    )
    asyncio.run(kernel.do_execute("TEST"))
    text = get_log_text(kernel)
    assert "42" in text, "Didn't run this file"


TEST = 42
