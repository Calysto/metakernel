import asyncio
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
    asyncio.run(kernel.do_execute("%jigsaw Processing --workspace workspace1"))
    text = get_log_text(kernel)
    assert os.path.isfile("workspace1.html"), "File does not exist: workspace1.html"


@pytest.mark.skipif(not has_network(), reason="no network")
def test_jigsaw_magic_direct() -> None:
    """Test calling JigsawMagic.line_jigsaw directly with a workspace filename."""
    from metakernel.magics.jigsaw_magic import JigsawMagic

    kernel = get_kernel(EvalKernel)
    magic = JigsawMagic(kernel)
    magic.line_jigsaw("Processing", workspace="workspace1")
    assert os.path.isfile("workspace1.html"), "File does not exist: workspace1.html"


@pytest.mark.skipif(not has_network(), reason="no network")
def test_jigsaw_magic_with_path() -> None:
    """Test that %jigsaw saves files in a subdirectory when path is given in workspace (issue #167)."""
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute(
            "%jigsaw Processing --workspace jigsaw_test_subdir/workspace1"
        )
    )
    assert os.path.isfile("jigsaw_test_subdir/workspace1.html"), (
        "File does not exist: jigsaw_test_subdir/workspace1.html"
    )


def teardown() -> None:
    import shutil

    for fname in ["workspace1.html"]:
        try:
            os.remove(fname)
        except OSError:
            pass
    shutil.rmtree("jigsaw_test_subdir", ignore_errors=True)
