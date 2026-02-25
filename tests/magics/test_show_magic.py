from tests.utils import EvalKernel, get_kernel


def test_show_magic() -> None:
    kernel = get_kernel(EvalKernel)
    results = kernel.do_execute("""%%show
Welcome to the big show!
""")
    text = results["payload"][0]["data"]["text/plain"]
    assert "Welcome to the big show!" in text, text

    results = kernel.do_execute("""%%show --output
# Welcome to the big show!
retval = "This is a test"
""")
    text = results["payload"][0]["data"]["text/plain"]
    assert "Welcome to the big show!" not in text, text
    assert "This is a test" in text, text
