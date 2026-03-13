import asyncio
import textwrap

from tests.utils import capture_send_messages, clear_log_text, get_kernel, get_log_text


def test_python_magic() -> None:
    kernel = get_kernel()

    text = "%python imp"
    comp = asyncio.run(kernel.do_complete(text, len(text)))

    assert "import" in comp["matches"]

    helpstr = kernel.get_help_on("%python bin")
    assert "Return the binary representation of an integer" in helpstr, helpstr


def test_python_magic2() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%python retval = 1", None))
    assert "1" in get_log_text(kernel)

    asyncio.run(
        kernel.do_execute(
            textwrap.dedent("""\
    %%python
    def test(a):
        return a + 1
    retval = test(2)"""),
            None,
        )
    )
    assert "3" in get_log_text(kernel)

    asyncio.run(
        kernel.do_execute(
            textwrap.dedent("""\
    %%python
    def test(a):
        return a + 1
    test(2)"""),
            None,
        )
    )
    assert "3" in get_log_text(kernel)


def test_python_magic3() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%python -e\n1 + 2", None))
    magic = kernel.get_magic("%%python")
    assert magic.retval is None  # type:ignore[attr-defined]

    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%python\n1 + 2", None))
    magic = kernel.get_magic("%%python")
    assert magic.retval == 3  # type:ignore[attr-defined]

    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%python\n1 + 2\n2 + 3", None))
    magic = kernel.get_magic("%%python")
    assert magic.retval == 5  # type:ignore[attr-defined]

    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%python\nretval = 1 + 2\n2 + 3", None))
    magic = kernel.get_magic("%%python")
    assert magic.retval == 3  # type:ignore[attr-defined]

    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%python\nimport math", None))
    magic = kernel.get_magic("%%python")
    assert magic.retval is None  # type:ignore[attr-defined]


def test_python_magic4() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("?%python", None))
    assert "%python CODE" in get_log_text(kernel)

    clear_log_text(kernel)

    ret = asyncio.run(kernel.do_execute("?%python a", None))
    assert ret["payload"][0]["data"]["text/plain"] == 'No help available for "a"'
    ret = asyncio.run(kernel.do_execute("?%%python a.b", None))
    assert ret["payload"][0]["data"]["text/plain"] == 'No help available for "a.b"'

    ret = asyncio.run(kernel.do_execute("??%%python oct", None))
    assert (
        "Return the octal representation of an integer"
        in ret["payload"][0]["data"]["text/plain"]
    ), ret["payload"][0]["data"]["text/plain"]


def test_python_magic5() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%python print('hello')"))

    assert "hello" in get_log_text(kernel)


def test_python_magic_html_display() -> None:
    """%%python cell should display HTML objects as text/html (issue #187)."""
    kernel = get_kernel()

    # Returning an HTML object as the last expression should yield text/html
    with capture_send_messages(kernel) as sent:
        asyncio.run(
            kernel.do_execute(
                "%%python\nfrom IPython.display import HTML\nHTML('<b>hello</b>')",
                False,
            )
        )
    result_msgs = [c for msg_type, c in sent if msg_type == "execute_result"]
    assert result_msgs, "expected an execute_result message"
    assert "text/html" in result_msgs[0]["data"], (
        "expected text/html in execute_result data"
    )
    assert result_msgs[0]["data"]["text/html"] == "<b>hello</b>"

    # Calling display(HTML(...)) explicitly should emit display_data with text/html
    kernel2 = get_kernel()
    with capture_send_messages(kernel2) as sent2:
        asyncio.run(
            kernel2.do_execute(
                textwrap.dedent("""\
                %%python
                from IPython.display import HTML, display
                display(HTML('<i>world</i>'))"""),
                False,
            )
        )
    display_msgs = [c for msg_type, c in sent2 if msg_type == "display_data"]
    assert display_msgs, "expected a display_data message"
    assert "text/html" in display_msgs[0]["data"], "expected text/html in display_data"
    assert display_msgs[0]["data"]["text/html"] == "<i>world</i>"

    # A function that calls display(HTML(...)) internally should also work
    kernel3 = get_kernel()
    with capture_send_messages(kernel3) as sent3:
        asyncio.run(
            kernel3.do_execute(
                textwrap.dedent("""\
                %%python
                from IPython.display import HTML, display
                def plan():
                    display(HTML('<b>plan</b>'))
                plan()"""),
                False,
            )
        )
    display_msgs3 = [c for msg_type, c in sent3 if msg_type == "display_data"]
    assert display_msgs3, "expected a display_data message from plan()"
    assert display_msgs3[0]["data"]["text/html"] == "<b>plan</b>"
