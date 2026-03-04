# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

from typing import Any

from metakernel import Magic


class SetMagic(Magic):
    def line_set(self, variable: str, value: str) -> None:
        """
        %set VARIABLE VALUE - set a variable in the kernel.

        This line magic is used to set a variable to a Python value.

        Examples:
            %set x 42
            %set x [1, 2, 3]
        """
        value = self.kernel.do_execute_direct(value)
        self.kernel.set_variable(variable, value)

    def post_process(self, retval: Any) -> Any:
        return retval


def register_magics(kernel: Any) -> None:
    kernel.register_magics(SetMagic)
