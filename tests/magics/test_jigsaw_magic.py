import os

import pytest

from tests.utils import (
    EvalKernel,
    get_kernel,
    get_log_text,
    has_network,
)


@pytest.mark.skipif(not has_network(), reason="no network")
def test_jigsaw_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%jigsaw Processing --workspace workspace1")
    text = get_log_text(kernel)
    assert os.path.isfile("workspace1.html"), "File does not exist: workspace1.html"


def teardown() -> None:
    for fname in ["workspace1.html"]:
        try:
            os.remove(fname)
        except OSError:
            pass
