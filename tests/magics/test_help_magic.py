import asyncio

from tests.utils import clear_log_text, get_kernel, get_log_text


def test_help_magic() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("?%magic", None))
    text = get_log_text(kernel)
    assert "%magic - show installed magics" in text, repr(text)

    asyncio.run(kernel.do_execute("%lsmagic??", None))
    text = get_log_text(kernel)
    assert "class LSMagicMagic" in text

    asyncio.run(kernel.do_execute("?", None))
    text = get_log_text(kernel)
    assert "This is a usage statement." in text

    asyncio.run(kernel.do_execute("?%", None))
    text = get_log_text(kernel)
    assert "This is a usage statement." in text

    asyncio.run(kernel.do_execute("?%whatwhat", None))
    text = get_log_text(kernel)
    assert "No such line magic 'whatwhat'" in text

    clear_log_text(kernel)

    asyncio.run(kernel.do_execute("%%help %magic", None))
    text = get_log_text(kernel)
    assert "MagicMagic" in text

    asyncio.run(kernel.do_execute("%%help\n%python", None))
    text = get_log_text(kernel)
    assert "PythonMagic" in text
