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


def _make_jigsaw_html(workspace_name: str = "MYWORKSPACENAME") -> str:
    """Return a minimal jigsaw HTML snippet with all cross-origin patterns."""
    return (
        "<html><head></head><body>"
        "<script>\n"
        "      // Make Blockly available to notebook:\n"
        "      window.parent.Blockly = Blockly;\n"
        "      window.parent.DOMParser = DOMParser;\n"
        "      var xml_init = document.getElementById('workspace');\n"
        f'      window.parent.document.jigsaw_register_workspace("{workspace_name}", workspace, xml_init);\n'
        f"window.parent.document.jigsaw_generate('{workspace_name}', 'Python');\n"
        f"window.parent.document.jigsaw_generate('{workspace_name}', 'Python', 1);\n"
        f"window.parent.document.jigsaw_clear_output('{workspace_name}');\n"
        "window.parent.block = block;\n"
        "</script>"
        "</body></html>"
    )


def test_fix_cross_origin_jupyterhub(tmp_path: "os.PathLike[str]") -> None:
    """_fix_cross_origin removes all direct window.parent property accesses.

    Under JupyterHub / Apache reverse-proxy the jigsaw iframe is served from
    a different origin (or as a null-origin sandboxed iframe), so any direct
    ``window.parent.<property>`` access raises a SecurityError.  This test
    verifies that ``_fix_cross_origin`` replaces every such pattern with
    postMessage-based alternatives so that ``%jigsaw`` works in those
    environments (issue #196).
    """
    from metakernel.magics.jigsaw_magic import _fix_cross_origin

    html_in = _make_jigsaw_html()
    html_out = _fix_cross_origin(html_in, "Python", saved_xml="")

    # All direct cross-origin window.parent accesses must be gone.
    assert "window.parent.Blockly" not in html_out
    assert "window.parent.DOMParser" not in html_out
    assert "window.parent.document.jigsaw_register_workspace" not in html_out
    assert "window.parent.document.jigsaw_generate" not in html_out
    assert "window.parent.document.jigsaw_clear_output" not in html_out
    assert "window.parent.block = block" not in html_out

    # postMessage helper infrastructure must be injected.
    assert "postMessage" in html_out
    assert "_jigsaw_send" in html_out
    assert "_jigsaw_run" in html_out
    assert "_jigsaw_insert" in html_out
    assert "_jigsaw_clear" in html_out


def test_fix_cross_origin_embeds_saved_xml() -> None:
    """Saved workspace XML is embedded in the HTML, not fetched via XHR.

    Under JupyterHub / reverse-proxy a sandboxed iframe cannot make XHR
    requests back to the server to load the workspace file.  The fix embeds
    the XML directly as a JS variable so no network request is needed
    (issue #196).
    """
    from metakernel.magics.jigsaw_magic import _fix_cross_origin

    saved_xml = '<xml id="workspace"><block type="controls_if"/></xml>'
    html_in = _make_jigsaw_html() + ""  # fresh copy
    html_out = _fix_cross_origin(html_in, "Python", saved_xml=saved_xml)

    # The XML must appear as an embedded JS variable, not require an XHR.
    assert "__jigsaw_saved_xml__" in html_out
    assert "controls_if" in html_out  # actual XML content is present


def teardown() -> None:
    import shutil

    for fname in ["workspace1.html"]:
        try:
            os.remove(fname)
        except OSError:
            pass
    shutil.rmtree("jigsaw_test_subdir", ignore_errors=True)
