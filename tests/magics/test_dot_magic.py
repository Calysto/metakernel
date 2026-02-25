import shutil

import pytest

from tests.utils import EvalKernel, get_kernel, get_log_text

NO_DOT = shutil.which("dot") is None


@pytest.mark.skipif(NO_DOT, reason="Requires dot from graphviz")
def test_dot_magic_cell() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("""%%dot

graph A { a->b };
""")

    text = get_log_text(kernel)
    assert "Display Data" in text, text


@pytest.mark.skipif(NO_DOT, reason="Requires dot from graphviz")
def test_dot_magic_line() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%dot graph A { a->b };")

    text = get_log_text(kernel)
    assert "Display Data" in text, text
