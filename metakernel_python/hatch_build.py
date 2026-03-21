import json
import os
import shutil
import sys
from tempfile import TemporaryDirectory

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from jupyter_client.kernelspec import KernelSpecManager


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        here = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, here)
        from metakernel_python import MetaKernelPython

        kernel_json = MetaKernelPython.kernel_json
        prefix = os.path.join(here, "data_kernelspec")

        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)  # noqa: S103 Starts off as 700, not user readable
            with open(os.path.join(td, "kernel.json"), "w") as f:
                json.dump(kernel_json, f, sort_keys=True)
            print("Installing Jupyter kernel spec")

            cur_path = os.path.dirname(os.path.realpath(__file__))
            for logo in ["logo-32x32.png", "logo-64x64.png"]:
                try:
                    shutil.copy(os.path.join(cur_path, logo), td)
                except FileNotFoundError:
                    pass

            KernelSpecManager().install_kernel_spec(
                td, "metakernel_python", user=False, prefix=prefix
            )
