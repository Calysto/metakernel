import importlib.util

import pytest

from tests.utils import get_kernel

has_calysto = importlib.util.find_spec("calysto") is not None


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
    kernel.do_execute("%%brain\nrobot.forward(1)", None)
    magic = kernel.cell_magics["brain"]
    assert magic.code is not None
