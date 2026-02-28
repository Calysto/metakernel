import os
from unittest.mock import MagicMock, patch

import pytest
from ipykernel.kernelapp import IPKernelApp
from jupyter_core.paths import jupyter_config_dir, jupyter_config_path

from metakernel import MetaKernelApp


class TestMetaKernelAppConfig:
    def test_config_dir_default(self) -> None:
        app = MetaKernelApp()
        assert app.config_dir == jupyter_config_dir()

    def test_config_file_paths_starts_with_cwd(self) -> None:
        app = MetaKernelApp()
        assert app.config_file_paths[0] == os.getcwd()

    def test_config_file_paths_contains_config_dir(self) -> None:
        app = MetaKernelApp()
        assert app.config_dir in app.config_file_paths

    def test_config_file_paths_config_dir_appears_once(self) -> None:
        app = MetaKernelApp()
        paths = app.config_file_paths
        assert paths.count(app.config_dir) == 1

    def test_config_file_paths_contains_jupyter_config_paths(self) -> None:
        app = MetaKernelApp()
        for path in jupyter_config_path():
            assert path in app.config_file_paths

    def test_config_file_paths_custom_config_dir(self) -> None:
        app = MetaKernelApp()
        app.config_dir = "/tmp/custom_config_dir"
        paths = app.config_file_paths
        assert "/tmp/custom_config_dir" in paths
        assert paths[0] == os.getcwd()


class TestMetaKernelAppLaunchInstance:
    def test_sets_app_name(self) -> None:
        with patch.object(IPKernelApp, "launch_instance"):
            MetaKernelApp.launch_instance(app_name="mykernel")
        assert MetaKernelApp.name == "mykernel"

    def test_default_name_is_metakernel(self) -> None:
        with patch.object(IPKernelApp, "launch_instance"):
            MetaKernelApp.launch_instance()
        assert MetaKernelApp.name == "metakernel"

    def test_app_name_not_forwarded_to_super(self) -> None:
        with patch.object(IPKernelApp, "launch_instance") as mock_launch:
            MetaKernelApp.launch_instance(app_name="x", extra="y")
        call_kwargs = mock_launch.call_args[1]
        assert "app_name" not in call_kwargs

    def test_extra_kwargs_forwarded_to_super(self) -> None:
        with patch.object(IPKernelApp, "launch_instance") as mock_launch:
            MetaKernelApp.launch_instance(app_name="x", extra="y")
        call_kwargs = mock_launch.call_args[1]
        assert call_kwargs.get("extra") == "y"

    def test_calls_super_launch_instance(self) -> None:
        with patch.object(IPKernelApp, "launch_instance") as mock_launch:
            MetaKernelApp.launch_instance()
        mock_launch.assert_called_once()


class TestMetaKernelAppSubcommands:
    def test_subcommands_has_install(self) -> None:
        app = MetaKernelApp()
        assert "install" in app.subcommands

    def test_install_description(self) -> None:
        app = MetaKernelApp()
        _, description = app.subcommands["install"]
        assert description == "Install this kernel"

    def test_install_app_class_has_kernel_class(self) -> None:
        app = MetaKernelApp()
        KernelInstallerApp, _ = app.subcommands["install"]
        assert hasattr(KernelInstallerApp, "kernel_class")
        assert KernelInstallerApp.kernel_class is app.kernel_class

    def test_install_app_initialize_stores_argv(self) -> None:
        app = MetaKernelApp()
        KernelInstallerApp, _ = app.subcommands["install"]
        installer = KernelInstallerApp()
        installer.initialize(["--user"])
        assert installer.argv == ["--user"]

    def test_install_start_calls_kernelspec_install(self) -> None:
        kernel_json = {
            "argv": ["python", "-m", "test_kernel"],
            "display_name": "Test Kernel",
            "language": "test",
            "name": "test-kernel",
        }
        mock_kernel_class = MagicMock()
        mock_kernel_class.return_value.kernel_json = kernel_json
        mock_kernel_class.__module__ = "metakernel"

        app = MetaKernelApp()
        # KernelInstallerApp.kernel_class is a plain attribute, not a traitlet —
        # set it directly to avoid MetaKernelApp.kernel_class type validation.
        KernelInstallerApp, _ = app.subcommands["install"]
        KernelInstallerApp.kernel_class = mock_kernel_class

        installer = KernelInstallerApp()
        installer.argv = ["--user"]

        with patch("subprocess.check_call") as mock_check:
            installer.start()

        mock_check.assert_called_once()
        cmd = mock_check.call_args[0][0]
        assert "kernelspec" in cmd
        assert "install" in cmd
        assert "--user" in cmd

    def test_install_start_exits_on_failure(self) -> None:
        import subprocess

        kernel_json = {
            "argv": [],
            "display_name": "Test",
            "language": "test",
            "name": "test-kernel",
        }
        mock_kernel_class = MagicMock()
        mock_kernel_class.return_value.kernel_json = kernel_json
        mock_kernel_class.__module__ = "metakernel"

        app = MetaKernelApp()
        KernelInstallerApp, _ = app.subcommands["install"]
        KernelInstallerApp.kernel_class = mock_kernel_class

        installer = KernelInstallerApp()
        installer.argv = []

        with patch(
            "subprocess.check_call",
            side_effect=subprocess.CalledProcessError(1, "jupyter"),
        ):
            with pytest.raises(SystemExit) as exc_info:
                installer.start()
        assert exc_info.value.code == 1
