import asyncio
import importlib.util
from typing import Any
from unittest.mock import MagicMock

import pytest

import metakernel.magics.brain_magic as _bm
from metakernel.magics.brain_magic import register_ipython_magics
from tests.utils import get_kernel

has_calysto = importlib.util.find_spec("calysto") is not None


@pytest.fixture()
def ipython_brain_magic(monkeypatch):
    """Yield the registered `brain` cell-magic function with IPython stubbed out."""
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "IPython.core.magic.register_cell_magic",
        lambda f: captured.update(brain=f) or f,  # type:ignore[redundant-expr]
    )

    register_ipython_magics()

    yield captured["brain"]


def test_brain_code_transform() -> None:
    """%%brain wraps cell body in a brain() function with simulation boilerplate."""
    kernel = get_kernel()
    magic = kernel.cell_magics["brain"]
    magic.code = "robot.forward(1)"
    magic.cell_brain()

    assert "from calysto.simulation import *" in magic.code
    assert "robot = get_robot()" in magic.code
    assert "def brain():" in magic.code
    assert "robot.forward(1)" in magic.code
    assert "robot.brain = brain" in magic.code


def test_brain_code_transform_multiline() -> None:
    """Multi-line cell body is preserved in the transformed code."""
    kernel = get_kernel()
    magic = kernel.cell_magics["brain"]
    magic.code = "robot.forward(1)\nrobot.back(1)"
    magic.cell_brain()

    assert "robot.forward(1)" in magic.code
    assert "robot.back(1)" in magic.code
    assert "robot.brain = brain" in magic.code


def test_brain_code_transform_structure() -> None:
    """Transformed code starts with pre-code and ends with the brain assignment."""
    kernel = get_kernel()
    magic = kernel.cell_magics["brain"]
    magic.code = "pass"
    magic.cell_brain()

    lines = magic.code.splitlines()
    # pre_code comes first
    assert any("from calysto.simulation import *" in line for line in lines)
    # post_code comes last (non-empty line)
    non_empty = [line for line in lines if line.strip()]
    assert non_empty[-1].strip() == "robot.brain = brain"


def test_brain_help() -> None:
    kernel = get_kernel()
    helpstr = kernel.get_help_on("%%brain")
    assert "brain" in helpstr.lower(), helpstr


@pytest.mark.skipif(not has_calysto, reason="calysto is not installed")
def test_brain_cell_magic_executes() -> None:
    """%%brain executes without error when calysto is available."""
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%%brain\nrobot.forward(1)", None))
    magic = kernel.cell_magics["brain"]
    assert magic.code is not None


def test_register_ipython_magics_noop_without_ipython(
    ipython_brain_magic, monkeypatch
) -> None:
    """The registered `brain` function is a no-op when get_ipython() returns None."""
    monkeypatch.setattr(_bm, "get_ipython", lambda: None)
    assert ipython_brain_magic("", "robot.forward(1)") is None


def test_register_ipython_magics_executes_transformed_code(
    ipython_brain_magic, monkeypatch
) -> None:
    """The registered `brain` function transforms and executes the cell."""
    mock_ipkernel = MagicMock()
    monkeypatch.setattr(_bm, "get_ipython", lambda: mock_ipkernel)

    ipython_brain_magic("", "robot.forward(1)")

    executed_code = mock_ipkernel.kernel.do_execute.call_args[0][0]
    assert "robot.forward(1)" in executed_code
    assert "robot.brain = brain" in executed_code
    mock_ipkernel.kernel.do_execute.assert_called_once_with(executed_code, silent=True)
