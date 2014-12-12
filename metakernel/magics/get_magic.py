# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic

class GetMagic(Magic):
    def line_get(self, variable):
        """
        %get VARIABLE - get a variable from the kernel in a Python-type.

        This line magic is used to get a variable.

        Examples:
            %get x 
        """
        self.retval = self.kernel.get_variable(variable)

    def post_process(self, retval):
        return self.retval


def register_magics(kernel):
   kernel.register_magics(GetMagic)
