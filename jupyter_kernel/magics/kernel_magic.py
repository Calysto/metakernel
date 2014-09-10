# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option
import logging

class KernelMagic(Magic):
    kernels = {}
    kernel_name = None

    @option(
        '-k', '--kernel_name', action='store', default="default",
        help='kernel name given to use for execution'
    )
    def line_kernel(self, module_name, class_name, kernel_name="default"):
        """
        %kernel MODULE CLASS [-k NAME] - construct a kernel for sending code.

        Also returns the kernel as output.

        Example:

            %kernel bash_kernel BashKernel -k bash

        Use `%kx` or `%%kx` to send code to the kernel.
        """
        self.kernel_name = kernel_name
        module = __import__(module_name)
        class_ = getattr(module, class_name)
        # FIXME: monkeypatch to replace methods of class
        #        with methods of instance
        class_.subkernel(self.kernel)
        self.kernels[kernel_name] = class_()
        self.retval = self.kernels[kernel_name]

    @option(
        '-k', '--kernel_name', action='store', default=None,
        help='kernel name given to use for execution'
    )
    def cell_kx(self, kernel_name=None):
        """
        %%kx [-k NAME] - send the cell code to the kernel.

        Returns the result of the execution as output.

        Example:

            %%kernel bash
            ls -al 

        Use `%kernel MODULE CLASS [-k NAME]` to create a kernel.
        """
        if kernel_name is None:
            kernel_name = self.kernel_name
        self.retval = self.kernels[kernel_name].do_execute_direct(self.code)
        self.evaluate = False

    @option(
        '-k', '--kernel_name', action='store', default=None,
        help='kernel name given to use for execution'
    )
    def line_kx(self, code, kernel_name=None):
        """
        %kx CODE [-k NAME] - send the code to the kernel.

        Returns the result of the execution as output.

        Example:

            %kernel ls -al 

        Use `%kernel MODULE CLASS [-k NAME]` to create a kernel.
        """
        if kernel_name is None:
            kernel_name = self.kernel_name
        self.retval = self.kernels[kernel_name].do_execute_direct(code)

    def post_process(self, retval):
        return self.retval

def register_magics(kernel):
    kernel.register_magics(KernelMagic)
