import asyncio
import os
import sys
from types import ModuleType
from typing import Any
from unittest.mock import patch

import pytest

from metakernel.magics.download_magic import register_ipython_magics
from tests.utils import (
    EvalKernel,
    clear_log_text,
    get_kernel,
    get_log_text,
    has_network,
)


def _magic_module(magic: Any) -> ModuleType:
    """The magics loader imports magic files as bare top-level modules
    (e.g. `download_magic`), separate from the `metakernel.magics.download_magic`
    package import. Patch targets must go through the module a given magic
    instance actually belongs to."""
    return sys.modules[type(magic).__module__]


@pytest.mark.skipif(not has_network(), reason="no network")
def test_download_magic() -> None:
    kernel = get_kernel(EvalKernel)
    asyncio.run(
        kernel.do_execute(
            "%download --filename TEST.txt https://raw.githubusercontent.com/calysto/metakernel/main/LICENSE.txt"
        )
    )
    text = get_log_text(kernel)
    assert "Downloaded 'TEST.txt'" in text, text
    assert os.path.isfile("TEST.txt"), "File does not exist: TEST.txt"

    clear_log_text(kernel)

    asyncio.run(
        kernel.do_execute(
            "%download https://raw.githubusercontent.com/calysto/metakernel/main/LICENSE.txt"
        )
    )
    text = get_log_text(kernel)
    assert "Downloaded 'LICENSE.txt'" in text, text
    assert os.path.isfile("LICENSE.txt"), "File does not exist: LICENSE.txt"


def teardown() -> None:
    for fname in ["TEST.txt", "LICENSE.txt"]:
        try:
            os.remove(fname)
        except OSError:
            pass


def test_line_download_url_with_embedded_space() -> None:
    """A single url argument containing a space is split into url and filename."""
    kernel = get_kernel()
    magic = kernel.line_magics["download"]
    with patch.object(_magic_module(magic), "download") as mock_download:
        magic.line_download("http://example.com/file.txt myname.txt")
    mock_download.assert_called_once_with("http://example.com/file.txt", "myname.txt")
    text = get_log_text(kernel)
    assert "Downloaded 'myname.txt'" in text, text


def test_line_download_invalid_arguments() -> None:
    """More than one space with no -f filename raises an error."""
    kernel = get_kernel()
    magic = kernel.line_magics["download"]
    with pytest.raises(Exception, match="invalid arguments to %download"):
        magic.line_download("http://example.com/file.txt too many parts")


def test_line_download_appends_html_extension() -> None:
    """A filename without an extension gets '.html' appended."""
    kernel = get_kernel()
    magic = kernel.line_magics["download"]
    with patch.object(_magic_module(magic), "download") as mock_download:
        magic.line_download("http://example.com/file", filename="noext")
    mock_download.assert_called_once_with("http://example.com/file", "noext.html")
    text = get_log_text(kernel)
    assert "Downloaded 'noext.html'" in text, text


def test_line_download_reports_error_on_failure() -> None:
    """When download() raises, the error is reported via kernel.Error."""
    kernel = get_kernel()
    magic = kernel.line_magics["download"]
    with patch.object(_magic_module(magic), "download", side_effect=OSError("boom")):
        magic.line_download("http://example.com/file.txt", filename="file.txt")
    text = get_log_text(kernel)
    assert "boom" in text, text


def test_register_ipython_magics() -> None:
    """The registered `download` line-magic forwards to kernel.call_magic."""
    captured: dict[str, Any] = {}
    with patch(
        "IPython.core.magic.register_line_magic",
        lambda f: captured.update(download=f) or f,  # type:ignore[redundant-expr]
    ):
        register_ipython_magics()

    with patch("metakernel.IPythonKernel.call_magic") as mock_call_magic:
        captured["download"]("http://example.com/file.txt")
    mock_call_magic.assert_called_once_with("%download http://example.com/file.txt")
