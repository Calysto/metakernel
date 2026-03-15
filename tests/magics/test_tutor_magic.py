from unittest.mock import patch

import pytest

from tests.utils import EvalKernel, get_kernel


def _run_tutor(code: str, language: str | None = None):
    """Helper: run cell_tutor and return the HTML object passed to Display."""
    kernel = get_kernel(EvalKernel)
    magic = kernel.cell_magics["tutor"]
    magic.code = code
    captured = {}
    with patch.object(
        kernel, "Display", side_effect=lambda obj: captured.update({"obj": obj})
    ):
        magic.cell_tutor(language=language)
    return magic, captured.get("obj")


def _get_url(html_obj) -> str:
    """Extract the pythontutor URL embedded in the HTML button output."""
    return str(html_obj.data)


def test_tutor_python3_url() -> None:
    """%%tutor with python3 builds a URL with py=3."""
    _, html = _run_tutor("x = 1", language="python3")
    assert "py=3" in _get_url(html)
    assert "pythontutor.com" in _get_url(html)


def test_tutor_python_alias_url() -> None:
    """'python' is an alias for python3 and produces the same py=3 URL."""
    _, html_py = _run_tutor("x = 1", language="python")
    _, html_py3 = _run_tutor("x = 1", language="python3")
    assert "py=3" in _get_url(html_py)
    assert _get_url(html_py) == _get_url(html_py3)


def test_tutor_python2_url() -> None:
    """%%tutor with python2 builds a URL with py=2."""
    _, html = _run_tutor("x = 1", language="python2")
    assert "py=2" in _get_url(html)


def test_tutor_java_url() -> None:
    """%%tutor with java builds a URL with py=java."""
    _, html = _run_tutor('System.out.println("hi");', language="java")
    assert "py=java" in _get_url(html)


def test_tutor_javascript_url() -> None:
    """%%tutor with javascript builds a URL with py=js."""
    _, html = _run_tutor("var x = 1;", language="javascript")
    assert "py=js" in _get_url(html)


def test_tutor_code_encoded_in_url() -> None:
    """The cell code is URL-encoded and present in the button HTML."""
    _, html = _run_tutor("a = 1\nb = 2", language="python3")
    assert "pythontutor.com" in _get_url(html)


def test_tutor_button_rendered() -> None:
    """%%tutor renders a button that loads the iframe on click."""
    _, html = _run_tutor("x = 1", language="python3")
    data = _get_url(html)
    assert "<button" in data
    assert "onclick" in data
    assert "<iframe" in data


def test_tutor_evaluate_set_false() -> None:
    """cell_tutor sets magic.evaluate to False to prevent re-execution."""
    magic, _ = _run_tutor("x = 1", language="python3")
    assert magic.evaluate is False


def test_tutor_default_language_from_kernel() -> None:
    """When no language is given, the kernel's language_info['name'] is used."""
    kernel = get_kernel(EvalKernel)
    kernel.language_info = {"name": "python3"}
    magic = kernel.cell_magics["tutor"]
    magic.code = "x = 1"
    captured = {}
    with patch.object(
        kernel, "Display", side_effect=lambda obj: captured.update({"obj": obj})
    ):
        magic.cell_tutor(language=None)
    assert "py=3" in captured["obj"].data


def test_tutor_unsupported_language_raises() -> None:
    """An unsupported language raises ValueError."""
    kernel = get_kernel(EvalKernel)
    magic = kernel.cell_magics["tutor"]
    magic.code = "x = 1"
    with pytest.raises(ValueError, match="not supported"):
        magic.cell_tutor(language="ruby")


def test_tutor_help() -> None:
    kernel = get_kernel()
    helpstr = kernel.get_help_on("%%tutor")
    assert "tutor" in helpstr.lower(), helpstr
