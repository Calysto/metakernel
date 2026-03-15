import asyncio
import os
import re
from pathlib import Path

import pytest

from tests.utils import (
    EvalKernel,
    get_kernel,
    get_log_text,
    has_network,
)

LANGUAGES = ["Processing", "Python", "Test"]

skip_no_network = pytest.mark.skipif(not has_network(), reason="no network")


@skip_no_network
@pytest.mark.parametrize("language", LANGUAGES)
def test_jigsaw_magic(tmp_path: Path, language: str) -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute(f"%jigsaw {language} --workspace {tmp_path}/workspace1")
    )
    get_log_text(kernel)
    assert os.path.isfile(f"{tmp_path}/workspace1.html")


@skip_no_network
@pytest.mark.parametrize("language", LANGUAGES)
def test_jigsaw_magic_direct(tmp_path: Path, language: str) -> None:
    """Test calling JigsawMagic.line_jigsaw directly with a workspace filename."""
    from metakernel.magics.jigsaw_magic import JigsawMagic

    kernel = get_kernel(EvalKernel)
    magic = JigsawMagic(kernel)
    magic.line_jigsaw(language, workspace=str(tmp_path / "workspace1"))
    assert os.path.isfile(f"{tmp_path}/workspace1.html")


@skip_no_network
@pytest.mark.parametrize("language", LANGUAGES)
def test_jigsaw_html_content(tmp_path: Path, language: str) -> None:
    """Generated HTML uses postMessage, has no window.parent violations, and embeds saved-XML placeholder."""
    from metakernel.magics.jigsaw_magic import JigsawMagic

    kernel = get_kernel(EvalKernel)
    magic = JigsawMagic(kernel)
    magic.line_jigsaw(language, workspace=str(tmp_path / "workspace1"))

    with open(f"{tmp_path}/workspace1.html") as f:
        html = f.read()

    # postMessage helpers must be present.
    assert "_jigsaw_send" in html
    assert "_jigsaw_run" in html
    assert "_jigsaw_insert" in html
    assert "_jigsaw_clear" in html
    assert "postMessage" in html

    # No direct cross-origin property writes.
    assert not re.search(r"window\.parent\.\w+\s*=", html), (
        "Direct window.parent property assignment found"
    )
    assert "window.parent.document.jigsaw_" not in html

    # Saved-XML placeholder must be present (magic fills it at runtime).
    assert "window.__jigsaw_saved_xml__" in html


@skip_no_network
def test_jigsaw_magic_with_path(tmp_path: Path) -> None:
    """Test that %jigsaw saves files in a subdirectory when path is given in workspace (issue #167)."""
    kernel = get_kernel(EvalKernel)
    workspace = tmp_path / "subdir" / "workspace1"
    asyncio.run(kernel.do_execute(f"%jigsaw Processing --workspace {workspace}"))
    assert os.path.isfile(f"{workspace}.html")
