import asyncio
import os
import re
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

import metakernel.magics.jigsaw_magic as _jm
from metakernel.magics.jigsaw_magic import JigsawMagic, register_ipython_magics
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


def test_line_jigsaw_generates_default_workspace_name(tmp_path, monkeypatch) -> None:
    """With no --workspace given, a random `jigsaw-workspace-XXXXXX` name is used."""
    monkeypatch.chdir(tmp_path)
    kernel = get_kernel(EvalKernel)
    magic = JigsawMagic(kernel)
    with patch.object(_jm, "download", return_value="<html>FAKE</html>"):
        magic.line_jigsaw("Test")
    matches = list(tmp_path.glob("jigsaw-workspace-*.html"))
    assert len(matches) == 1


def test_line_jigsaw_creates_subdirectory_for_workspace_path(tmp_path) -> None:
    """A workspace path with a directory component creates that directory."""
    kernel = get_kernel(EvalKernel)
    magic = JigsawMagic(kernel)
    workspace = tmp_path / "newsubdir" / "workspace1"
    with patch.object(_jm, "download", return_value="<html>FAKE</html>"):
        magic.line_jigsaw("Test", workspace=str(workspace))
    assert os.path.isdir(tmp_path / "newsubdir")
    assert os.path.isfile(f"{workspace}.html")


def test_line_jigsaw_embeds_previously_saved_xml(tmp_path) -> None:
    """An existing workspace XML file is read and embedded in the generated HTML."""
    kernel = get_kernel(EvalKernel)
    magic = JigsawMagic(kernel)
    workspace = tmp_path / "workspace1"
    (tmp_path / "workspace1.xml").write_text("<xml>SAVED</xml>")
    with patch.object(
        _jm,
        "download",
        return_value='window.__jigsaw_saved_xml__ = "";',
    ):
        magic.line_jigsaw("Test", workspace=str(workspace))
    html = (tmp_path / "workspace1.html").read_text()
    assert "SAVED" in html


def test_line_jigsaw_ignores_oserror_reading_saved_xml(tmp_path) -> None:
    """An OSError while reading an existing workspace XML file is swallowed."""
    kernel = get_kernel(EvalKernel)
    magic = JigsawMagic(kernel)
    workspace = tmp_path / "workspace1"
    xml_path = tmp_path / "workspace1.xml"
    xml_path.write_text("<xml>SAVED</xml>")

    real_open = open

    def fake_open(path, *args, **kwargs):
        if str(path) == str(xml_path):
            raise OSError("boom")
        return real_open(path, *args, **kwargs)

    with (
        patch.object(_jm, "download", return_value="<html>FAKE</html>"),
        patch("builtins.open", side_effect=fake_open),
    ):
        magic.line_jigsaw("Test", workspace=str(workspace))
    assert os.path.isfile(f"{workspace}.html")


def test_register_ipython_magics() -> None:
    """The registered `jigsaw` line-magic forwards to kernel.call_magic."""
    captured: dict[str, Any] = {}
    with patch(
        "IPython.core.magic.register_line_magic",
        lambda f: captured.update(jigsaw=f) or f,  # type:ignore[redundant-expr]
    ):
        register_ipython_magics()

    with patch("metakernel.IPythonKernel.call_magic") as mock_call_magic:
        captured["jigsaw"]("Test --workspace foo")
    mock_call_magic.assert_called_once_with("%jigsaw Test --workspace foo")
