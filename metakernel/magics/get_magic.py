# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

from typing import Any

from metakernel import Magic


class GetMagic(Magic):
    def line_get(self, variable: str) -> None:
        """
        %get VARIABLE - get a variable from the kernel in a Python-type.

        This line magic is used to get a variable.

        Examples:
            %get x
        """
        self.retval = self.kernel.get_variable(variable)

    def post_process(self, retval: Any) -> Any:
        return self.retval


def register_magics(kernel: Any) -> None:
    kernel.register_magics(GetMagic)
