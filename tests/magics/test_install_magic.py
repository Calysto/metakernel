import os
import sys

import pytest

pytestmark = [
    pytest.mark.skipif(
        sys.platform == "win32",
        reason="install_magic path assertions use POSIX separators",
    ),
    # install_magic.py uses open() without a context manager; suppress the
    # resulting ResourceWarning so tests are not failed by a pre-existing issue
    # in the code under test.
    pytest.mark.filterwarnings("ignore::ResourceWarning"),
]

from tests.utils import get_kernel

_CUSTOM_JS_TILDE = "~/.ipython/profile_default/static/custom/custom.js"


def _setup(tmp_path, monkeypatch, initial_content=""):
    """Return (kernel, custom_js_path, inner_calls).

    The kernel's do_execute is wrapped so that any !-prefixed (shell) call is
    captured in *inner_calls* rather than actually executed.  expanduser is
    patched to redirect the custom.js path to a temp file.
    """
    custom_js = tmp_path / "custom.js"
    custom_js.write_text(initial_content)

    original_expanduser = os.path.expanduser
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda p: str(custom_js) if p == _CUSTOM_JS_TILDE else original_expanduser(p),
    )

    kernel = get_kernel()
    inner_calls: list[str] = []
    original_do_execute = kernel.do_execute

    def capturing_do_execute(code, *args, **kwargs):
        if code.startswith("!"):
            inner_calls.append(code)
            return {
                "status": "ok",
                "execution_count": 0,
                "payload": [],
                "user_expressions": {},
            }
        return original_do_execute(code, *args, **kwargs)

    kernel.do_execute = capturing_do_execute  # type:ignore[method-assign]
    return kernel, custom_js, inner_calls


# ---------------------------------------------------------------------------
# line_install branches: known packages each dispatch a specific shell command
# ---------------------------------------------------------------------------


def test_line_install_calico_publish(tmp_path, monkeypatch) -> None:
    """calico-publish dispatches the correct ipython install-nbextension URL."""
    kernel, _, inner_calls = _setup(tmp_path, monkeypatch)

    kernel.do_execute("%install calico-publish")

    assert len(inner_calls) == 1
    assert "ipython install-nbextension" in inner_calls[0]
    assert "calico-publish.js" in inner_calls[0]


def test_line_install_calico_spell_check(tmp_path, monkeypatch) -> None:
    """calico-spell-check dispatches the correct ipython install-nbextension URL."""
    kernel, _, inner_calls = _setup(tmp_path, monkeypatch)

    kernel.do_execute("%install calico-spell-check")

    assert len(inner_calls) == 1
    assert "ipython install-nbextension" in inner_calls[0]
    assert "calico-spell-check-1.0.zip" in inner_calls[0]


def test_line_install_calico_cell_tools(tmp_path, monkeypatch) -> None:
    """calico-cell-tools dispatches the correct ipython install-nbextension URL."""
    kernel, _, inner_calls = _setup(tmp_path, monkeypatch)

    kernel.do_execute("%install calico-cell-tools")

    assert len(inner_calls) == 1
    assert "ipython install-nbextension" in inner_calls[0]
    assert "calico-cell-tools-1.0.zip" in inner_calls[0]


def test_line_install_calico_document_tools(tmp_path, monkeypatch) -> None:
    """calico-document-tools dispatches the correct ipython install-nbextension URL."""
    kernel, _, inner_calls = _setup(tmp_path, monkeypatch)

    kernel.do_execute("%install calico-document-tools")

    assert len(inner_calls) == 1
    assert "ipython install-nbextension" in inner_calls[0]
    assert "calico-document-tools-1.0.zip" in inner_calls[0]


def test_line_install_unknown_package_no_shell_dispatch(tmp_path, monkeypatch) -> None:
    """An unrecognised package name dispatches no shell command."""
    kernel, custom_js, inner_calls = _setup(tmp_path, monkeypatch)

    kernel.do_execute("%install my-custom-package")

    assert inner_calls == [], "unexpected shell command dispatched for unknown package"
    # enable_extension still runs and registers the extension
    assert 'IPython.load_extensions("my-custom-package");' in custom_js.read_text()


# ---------------------------------------------------------------------------
# enable_extension branches (exercised via line_install with unknown packages)
# ---------------------------------------------------------------------------


def test_enable_extension_already_installed(tmp_path, monkeypatch) -> None:
    """enable_extension returns early when the extension is already present."""
    initial = 'IPython.load_extensions("my-ext");\n'
    kernel, custom_js, _ = _setup(tmp_path, monkeypatch, initial_content=initial)

    kernel.do_execute("%install my-ext")

    assert custom_js.read_text() == initial


def test_enable_extension_no_install_magic_marker(tmp_path, monkeypatch) -> None:
    """enable_extension appends the boilerplate block when // INSTALL MAGIC is absent."""
    kernel, custom_js, _ = _setup(tmp_path, monkeypatch, initial_content="")

    kernel.do_execute("%install fresh-ext")

    content = custom_js.read_text()
    assert "// INSTALL MAGIC" in content
    assert 'IPython.load_extensions("fresh-ext");' in content
    # extension load call must appear before the marker
    assert content.index('IPython.load_extensions("fresh-ext");') < content.index(
        "// INSTALL MAGIC"
    )


def test_enable_extension_existing_install_magic_marker(tmp_path, monkeypatch) -> None:
    """enable_extension inserts the load call before // INSTALL MAGIC when marker exists."""
    existing = (
        'require(["base/js/events"], function (events) {\n'
        '    events.on("app_initialized.NotebookApp", function () {\n'
        "        // INSTALL MAGIC\n"
        "    });\n"
        "});\n"
    )
    kernel, custom_js, _ = _setup(tmp_path, monkeypatch, initial_content=existing)

    kernel.do_execute("%install another-ext")

    content = custom_js.read_text()
    assert 'IPython.load_extensions("another-ext");' in content
    assert "// INSTALL MAGIC" in content
    assert content.index('IPython.load_extensions("another-ext");') < content.index(
        "// INSTALL MAGIC"
    )
    # the marker itself must still be present after the insertion
    assert content.count("// INSTALL MAGIC") == 1
