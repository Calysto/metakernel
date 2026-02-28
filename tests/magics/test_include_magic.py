import os

from tests.utils import get_kernel, get_log_text

EXECUTION = ""


def test_include_magic() -> None:
    global EXECUTION
    kernel = get_kernel()

    def do_execute_direct(code):
        global EXECUTION
        EXECUTION = code

    kernel.do_execute_direct = do_execute_direct  # type: ignore[method-assign,assignment]
    FILE = __file__
    if FILE.endswith(".pyc"):
        FILE = FILE[:-1]
    kernel.do_execute("%%include %s" % FILE)
    assert "metakernel" in EXECUTION
    assert ("AND " + "THIS") not in EXECUTION

    EXECUTION = ""
    kernel.do_execute(("%%include %s\nAND" + " THIS") % FILE)
    assert "metakernel" in EXECUTION
    assert ("AND " + "THIS") in EXECUTION

    EXECUTION = ""
    kernel.do_execute("%%include '%s' '%s'" % (FILE, FILE))
    assert "metakernel" in EXECUTION
    assert ("AND " + "THIS") not in EXECUTION


def test_line_include_single_file(tmp_path) -> None:
    """Test %include (line magic) with a single file."""
    kernel = get_kernel()
    executed = []

    def do_execute_direct(code):
        executed.append(code)

    kernel.do_execute_direct = do_execute_direct  # type: ignore[method-assign,assignment]

    f = tmp_path / "snippet.py"
    f.write_text("x = 42\n")

    kernel.do_execute(f"%include {f}")
    assert executed, "do_execute_direct was never called"
    assert "x = 42" in executed[-1]


def test_line_include_with_trailing_code(tmp_path) -> None:
    """Test %include inserts file content before subsequent code lines."""
    kernel = get_kernel()
    executed = []

    def do_execute_direct(code):
        executed.append(code)

    kernel.do_execute_direct = do_execute_direct  # type: ignore[method-assign,assignment]

    f = tmp_path / "snippet.py"
    f.write_text("y = 10\n")

    kernel.do_execute(f"%include {f}\nz = 20")
    assert executed
    result = executed[-1]
    assert "y = 10" in result
    assert "z = 20" in result


def test_line_include_multiple_files(tmp_path) -> None:
    """Test %include with multiple space-separated filenames."""
    kernel = get_kernel()
    executed = []

    def do_execute_direct(code):
        executed.append(code)

    kernel.do_execute_direct = do_execute_direct  # type: ignore[method-assign,assignment]

    f1 = tmp_path / "a.py"
    f1.write_text("a = 1\n")
    f2 = tmp_path / "b.py"
    f2.write_text("b = 2\n")

    kernel.do_execute(f"%include {f1} {f2}")
    assert executed
    result = executed[-1]
    assert "a = 1" in result
    assert "b = 2" in result


def test_line_include_tilde_expansion(tmp_path, monkeypatch) -> None:
    """Test that ~ in filename is expanded to the home directory."""
    kernel = get_kernel()
    executed = []

    def do_execute_direct(code):
        executed.append(code)

    kernel.do_execute_direct = do_execute_direct  # type: ignore[method-assign,assignment]

    f = tmp_path / "home_snippet.py"
    f.write_text("home_var = True\n")

    original_expanduser = os.path.expanduser
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda p: str(f) if p == "~/home_snippet.py" else original_expanduser(p),
    )

    kernel.do_execute("%include ~/home_snippet.py")
    assert executed
    assert "home_var = True" in executed[-1]


def test_line_include_file_not_found() -> None:
    """Test that including a nonexistent file logs an error."""
    kernel = get_kernel()
    kernel.do_execute("%include /nonexistent_path_xyz_abc/file.py")
    log_text = get_log_text(kernel)
    assert "Error" in log_text
