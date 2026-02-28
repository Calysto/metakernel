from unittest.mock import MagicMock, patch

from metakernel import IPythonKernel, register_ipython_magics


class TestIPythonKernel:
    def test_init(self) -> None:
        kernel = IPythonKernel()
        assert "magic" in kernel.line_magics
        assert kernel.cell_magics == {}
        assert kernel.shell is None
        assert kernel.parser is not None

    def test_print_stdout(self, capsys) -> None:
        kernel = IPythonKernel()
        kernel.Print("hello", "world")
        captured = capsys.readouterr()
        assert captured.out == "hello world\n"

    def test_print_kwargs(self, capsys) -> None:
        kernel = IPythonKernel()
        kernel.Print("a", "b", sep="-", end="!")
        captured = capsys.readouterr()
        assert captured.out == "a-b!"

    def test_error_stderr(self, capsys) -> None:
        kernel = IPythonKernel()
        kernel.Error("oops")
        captured = capsys.readouterr()
        assert captured.err == "oops\n"

    def test_display(self) -> None:
        kernel = IPythonKernel()
        mock_obj = MagicMock()
        with patch("IPython.display.display") as mock_display:
            kernel.Display(mock_obj)
        mock_display.assert_called_once_with(mock_obj)

    def test_display_multiple(self) -> None:
        kernel = IPythonKernel()
        a, b = MagicMock(), MagicMock()
        with patch("IPython.display.display") as mock_display:
            kernel.Display(a, b)
        mock_display.assert_called_once_with(a, b)


class TestRegisterIPythonMagics:
    def test_register_line_magic(self) -> None:
        with (
            patch("IPython.core.magic.register_line_magic") as mock_line,
            patch("IPython.core.magic.register_cell_magic"),
        ):
            register_ipython_magics("download")
        assert mock_line.called

    def test_register_cell_magic(self) -> None:
        with (
            patch("IPython.core.magic.register_line_magic"),
            patch("IPython.core.magic.register_cell_magic") as mock_cell,
        ):
            register_ipython_magics("pipe")
        assert mock_cell.called

    def test_register_unknown_magic_no_error(self) -> None:
        # An unknown magic name is silently skipped — no matching file exists.
        register_ipython_magics("nonexistent_magic_xyz")

    def test_register_all_magics(self) -> None:
        registered: list[tuple[object, ...]] = []

        def capture(*args, **kwargs):
            registered.append(args)
            return args[0] if args else None

        with (
            patch("IPython.core.magic.register_line_magic", side_effect=capture),
            patch("IPython.core.magic.register_cell_magic", side_effect=capture),
        ):
            register_ipython_magics()

        assert len(registered) > 0, "Expected at least one magic to be registered"

    def test_register_specific_only(self) -> None:
        """Passing a name should register only that magic, not all of them."""
        registered: list[tuple[object, ...]] = []

        def capture(*args, **kwargs):
            registered.append(args)
            return args[0] if args else None

        with (
            patch("IPython.core.magic.register_line_magic", side_effect=capture),
            patch("IPython.core.magic.register_cell_magic", side_effect=capture),
        ):
            register_ipython_magics("download")

        # download_magic registers exactly one line magic
        assert len(registered) == 1
