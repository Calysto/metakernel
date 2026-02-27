import sys

import pytest
from IPython.display import HTML

from metakernel.process_metakernel import BashKernel
from tests.utils import get_kernel, get_log_text

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="BashKernel requires bash/pexpect, not available on Windows",
)


def test_process_metakernel() -> None:
    kernel = get_kernel(BashKernel)
    kernel.do_execute('cat "%s"' % __file__, False)
    log_text = get_log_text(kernel)
    assert "metakernel.py" in log_text, log_text

    kernel.do_execute('echo "hello"\necho "goodbye"', None)
    log_text = get_log_text(kernel)
    assert '"hello"' in log_text
    assert '"goodbye"' in log_text

    kernel.do_execute("lalkjds")
    text = get_log_text(kernel)
    assert ": command not found" in text, text

    html = HTML("some html")
    kernel.Display(html)

    kernel.do_execute(r'for i in {1..3};do echo -ne "$i\r"; sleep 1; done', None)
    text = get_log_text(kernel)
    assert r"1\r2\r3\r" in text
