"""A Python kernel for Jupyter."""

from typing import Any

from IPython.core.inputtransformer2 import TransformerManager

from metakernel import MetaKernel

__version__ = "0.19.1"


class MetaKernelPython(MetaKernel):
    implementation = "MetaKernel Python"
    implementation_version = "1.0"
    language = "python"
    language_version = "0.1"
    banner = "MetaKernel Python - evaluates Python statements and expressions"
    language_info = {
        "mimetype": "text/x-python",
        "name": "python",
        # ------ If different from 'language':
        # 'codemirror_mode': {
        #    "version": 2,
        #    "name": "ipython"
        # }
        # 'pygments_lexer': 'language',
        # 'version'       : "x.y.z",
        "file_extension": ".py",
        "help_links": MetaKernel.help_links,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.transformer_manager = TransformerManager()  # type:ignore[no-untyped-call]

    def get_usage(self) -> str:
        return "This is MetaKernel Python. It implements a Python " + "interpreter."

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set a variable in the kernel language.
        """
        python_magic = self.line_magics["python"]
        python_magic.env[name] = value

    def get_variable(self, name: str) -> Any:
        """
        Get a variable from the kernel language.
        """
        python_magic = self.line_magics["python"]
        return python_magic.env.get(name, None)

    def do_execute_direct(self, code: str, *args: Any, **kwargs: Any) -> Any:
        python_magic = self.line_magics["python"]
        return python_magic.eval(code.strip())

    def get_completions(self, info: dict[str, Any]) -> list[str]:
        python_magic = self.line_magics["python"]
        return python_magic.get_completions(info)  # type:ignore[no-any-return]

    def get_kernel_help_on(
        self, info: dict[str, Any], level: int = 0, none_on_fail: bool = False
    ) -> str | None:
        python_magic = self.line_magics["python"]
        return python_magic.get_help_on(info, level, none_on_fail)  # type:ignore[no-any-return]

    def do_is_complete(self, code: str) -> dict[str, Any]:
        status, indent_spaces = self.transformer_manager.check_complete(code)
        r = {"status": status}
        if status == "incomplete":
            r["indent"] = " " * indent_spaces
        return r
