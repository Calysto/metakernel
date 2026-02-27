# force locale to C to get consistent error messages
import os
import sys

import pytest

from tests.utils import get_kernel, get_log_text

os.environ["LC_ALL"] = "C"
os.environ["LANG"] = "C"
os.environ["LANGUAGE"] = "C"


@pytest.mark.skipif(
    sys.platform == "win32", reason="bash completion not available on Windows"
)
def test_shell_magic() -> None:
    kernel = get_kernel()

    text = "%shell ech"
    comp = kernel.do_complete(text, len(text))

    assert "echo" in comp["matches"]

    helpstr = kernel.get_help_on("!cat")
    assert "Sorry, no help" not in helpstr, helpstr

    helpstr = kernel.get_help_on("%%shell cat", level=1)
    assert "Sorry, no help" not in helpstr

    helpstr = kernel.get_help_on("!lkjalskdfj")
    assert "Sorry, no help" in helpstr


@pytest.mark.skipif(
    sys.platform == "win32", reason="cat/echo shell commands not available on Windows"
)
def test_shell_magic2() -> None:
    kernel = get_kernel()
    kernel.do_execute('!cat "%s"' % __file__, False)
    log_text = get_log_text(kernel)
    assert "metakernel.py" in log_text

    kernel.do_execute('!!\necho "hello"\necho "goodbye"', None)
    log_text = get_log_text(kernel)
    assert '"hello"' in log_text
    assert '"goodbye"' in log_text


def test_shell_magic3() -> None:
    kernel = get_kernel()
    kernel.do_execute("!lalkjds")
    text = get_log_text(kernel)
    # POSIX: ": command not found", Windows: "is not recognized as the name of a cmdlet"
    assert ": command not found" in text or "is not recognized" in text, text
