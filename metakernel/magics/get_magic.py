# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

import inspect

from metakernel import Magic


class GetMagic(Magic):
    async def line_get(self, variable) -> None:
        """
        %get VARIABLE - get a variable from the kernel in a Python-type.

        This line magic is used to get a variable.

        Examples:
            %get x
        """
        result = self.kernel.get_variable(variable)
        if inspect.isawaitable(result):
            result = await result
        self.retval = result

    def post_process(self, retval):
        return self.retval


def register_magics(kernel) -> None:
    kernel.register_magics(GetMagic)
