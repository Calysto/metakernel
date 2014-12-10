# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic

class SetMagic(Magic):
    def line_set(self, variable, value):
        """
        %set VARIABLE VALUE - set a variable in the kernel.

        This line magic is used to set a variable to a Python value.

        Examples:
            %set x 42
            %set x [1, 2, 3]
        """
        self.kernel.set_variable(variable, value)

    def post_process(self, retval):
        return retval


def register_magics(kernel):
   kernel.register_magics(SetMagic)
