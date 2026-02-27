import os
import re
import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="install_magic path assertions use POSIX separators"
)

from metakernel.config import get_local_magics_dir
from tests.utils import (
    EvalKernel,
    get_kernel,
    get_log_text,
    has_network,
)

filename = get_local_magics_dir() + os.sep + "cd_magic.py"


@pytest.mark.skipif(not has_network(), reason="no network")
def test_install_magic_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(
        "%install_magic https://raw.githubusercontent.com/calysto/metakernel/main/metakernel/magics/cd_magic.py"
    )
    text = get_log_text(kernel)
    assert re.match(
        ".*Downloaded '.*ipython/metakernel/magics/cd_magic.py'", text, re.DOTALL | re.M
    ), "Not downloaded"
    assert os.path.isfile(filename), "File not found: %s" % filename


def teardown() -> None:
    try:
        os.remove(filename)
    except OSError:
        pass
