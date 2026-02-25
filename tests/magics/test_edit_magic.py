from tests.utils import EvalKernel, get_kernel


def test_edit_magic() -> None:
    kernel = get_kernel(EvalKernel)

    results = kernel.do_execute("%%edit %s" % __file__)
    text = results["payload"][0]["text"]
    assert text.startswith("%%file")
    assert "def test_edit_magic" in text
