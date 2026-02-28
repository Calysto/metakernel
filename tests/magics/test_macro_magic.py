from metakernel.magics.macro_magic import MacroMagic
from tests.utils import EvalKernel, clear_log_text, get_kernel, get_log_text


def test_macro_magic() -> None:
    kernel = get_kernel(EvalKernel)
    kernel.do_execute(
        """%%macro testme
print("ok")
    """,
        False,
    )
    kernel.do_execute("%macro testme", False)
    text = get_log_text(kernel)
    assert "ok" in text, text
    clear_log_text(kernel)

    kernel.do_execute("%macro -l learned", False)
    text = get_log_text(kernel)
    assert "testme" in text, text
    clear_log_text(kernel)

    kernel.do_execute("%macro -d testme", False)
    kernel.do_execute("%macro -l learned", False)
    text = get_log_text(kernel)
    assert "testme" not in text, text
    clear_log_text(kernel)


# ---------------------------------------------------------------------------
# Branch 1: -l flag  (name variations not yet covered)
# ---------------------------------------------------------------------------


def test_list_system_macros() -> None:
    """'-l system' prints the system macros and omits the Learned section."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%macro -l system", False)
    text = get_log_text(kernel)
    assert "renumber-cells" in text
    assert "Learned" not in text


def test_list_all_macros() -> None:
    """'-l all' prints both System and Learned sections."""
    kernel = get_kernel(EvalKernel)
    mm = kernel.line_magics["macro"]
    mm.learned["list-all-probe"] = "pass\n"

    kernel.do_execute("%macro -l all", False)
    text = get_log_text(kernel)
    assert "renumber-cells" in text
    assert "list-all-probe" in text


def test_list_all_shows_both_section_headers() -> None:
    """'-l all' emits both 'System:' and 'Learned:' section headers."""
    kernel = get_kernel(EvalKernel)
    mm = kernel.line_magics["macro"]
    mm.learned["section-header-probe"] = "pass\n"

    kernel.do_execute("%macro -l all", False)
    text = get_log_text(kernel)
    assert "System:" in text
    assert "Learned:" in text
    assert "renumber-cells" in text
    assert "section-header-probe" in text


# ---------------------------------------------------------------------------
# Branch 2: -s flag
# ---------------------------------------------------------------------------


def test_show_system_macro() -> None:
    """'-s NAME' for a system macro prints the header and the macro body."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%macro -s renumber-cells", False)
    text = get_log_text(kernel)
    assert "%%macro renumber-cells" in text
    assert "renumber-cells" in MacroMagic.macros
    assert MacroMagic.macros["renumber-cells"].split("\n")[0] in text


def test_show_learned_macro() -> None:
    """'-s NAME' for a learned macro prints the header and the macro body."""
    kernel = get_kernel(EvalKernel)
    mm = kernel.line_magics["macro"]
    mm.learned["show-probe"] = "x = 1\n"

    kernel.do_execute("%macro -s show-probe", False)
    text = get_log_text(kernel)
    assert "%%macro show-probe" in text
    assert "x = 1" in text


def test_show_unknown_macro_prints_only_header() -> None:
    """'-s NAME' for an unknown macro prints just the header with no body."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%macro -s no-such-macro-xyz", False)
    text = get_log_text(kernel)
    assert "%%macro no-such-macro-xyz" in text
    # no body was appended - only the header line should be present
    assert text.strip().endswith("%%macro no-such-macro-xyz")


# ---------------------------------------------------------------------------
# Branch 3b-i: learned macro with pre-existing self.code
# ---------------------------------------------------------------------------


def test_execute_learned_macro_with_prior_code() -> None:
    """A newline separator is inserted when self.code is non-empty before the macro."""
    kernel = get_kernel(EvalKernel)
    mm = kernel.line_magics["macro"]
    mm.learned["add-y"] = "y = 2\n"

    # The body after the magic line becomes self.code = "x = 1"
    kernel.do_execute("%macro add-y\nx = 1", False)

    assert kernel.get_variable("x") == 1
    assert kernel.get_variable("y") == 2


# ---------------------------------------------------------------------------
# Branch 4b / 4b-i: execute a system macro (+ pre-existing code sub-branch)
# ---------------------------------------------------------------------------


def test_execute_system_macro(monkeypatch) -> None:
    """Executing a system macro appends its body to self.code for evaluation."""
    kernel = get_kernel(EvalKernel)
    mm = kernel.line_magics["macro"]
    monkeypatch.setitem(mm.macros, "test-sys-exec", "z = 42\n")

    kernel.do_execute("%macro test-sys-exec", False)

    assert kernel.get_variable("z") == 42


def test_execute_system_macro_with_prior_code(monkeypatch) -> None:
    """A newline separator is inserted when self.code is non-empty for a system macro."""
    kernel = get_kernel(EvalKernel)
    mm = kernel.line_magics["macro"]
    monkeypatch.setitem(mm.macros, "test-sys-prior", "b = 2\n")

    kernel.do_execute("%macro test-sys-prior\na = 1", False)

    assert kernel.get_variable("a") == 1
    assert kernel.get_variable("b") == 2


# ---------------------------------------------------------------------------
# Branch 4a: delete a system macro
# ---------------------------------------------------------------------------


def test_delete_system_macro_raises_error() -> None:
    """'-d NAME' on a system macro logs an error (raises Exception internally)."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%macro -d renumber-cells", False)
    assert "Error" in get_log_text(kernel)


# ---------------------------------------------------------------------------
# Branch 5: empty name
# ---------------------------------------------------------------------------


def test_empty_name_lists_all_macros() -> None:
    """%macro with no name falls through to _list_macros() showing everything."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%macro", False)
    text = get_log_text(kernel)
    assert "Available macros" in text
    assert "renumber-cells" in text


# ---------------------------------------------------------------------------
# Branch 6: unknown name
# ---------------------------------------------------------------------------


def test_unknown_name_logs_error() -> None:
    """%macro with an unrecognised name logs 'No such macro' as an error."""
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%macro totally-unknown-macro-xyz", False)
    text = get_log_text(kernel)
    assert "No such macro" in text
    assert "totally-unknown-macro-xyz" in text
