# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import importlib
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

        This line magic will contruct a kernel language so that you can
        communicate.

        Example:

            %kernel bash_kernel BashKernel -k bash

        Use `%kx` or `%%kx` to send code to the kernel.

        Also returns the kernel as output.
        """
        self.kernel_name = kernel_name
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        kernel = class_()
        self.kernel.makeSubkernel(self.kernel)
        kernel.makeSubkernel(self.kernel)
        self.kernels[kernel_name] = kernel
        self.kernels[kernel_name].kernel = self.kernel
        self.retval = self.kernels[kernel_name]

    @option(
        '-k', '--kernel_name', action='store', default=None,
        help='kernel name given to use for execution'
    )
    def cell_kx(self, kernel_name=None):
        """
        %%kx [-k NAME] - send the cell code to the kernel.

        This cell magic will send the cell to be evaluated by
        the kernel. The kernel must have been created use the
        %%kernel magic.

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

        This line magic will send the CODE to the kernel
        for execution.

        Returns the result of the execution as output.

        Example:

            %kernel ls -al 

        Use `%kernel MODULE CLASS [-k NAME]` to create a kernel.
        """
        if kernel_name is None:
            kernel_name = self.kernel_name
        # make sure the code is sent as a string for execution
        code = str(code)
        self.retval = self.kernels[kernel_name].do_execute_direct(code)

    def post_process(self, retval):
        return self.retval

def register_magics(kernel):
    kernel.register_magics(KernelMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic, register_cell_magic
    kernel = IPythonKernel()
    magic = KernelMagic(kernel)

    @register_line_magic
    def kernel(line):
        """
        line is module_name, class_name[, kernel_name]
        """
        if line.strip().count(" ") == 1:
            kernel_name = "default"
            module_name, class_name = [item.strip() for item in line.strip().split(" ", 1)]
        else:
            module_name, class_name, kernel_name = [item.strip() for item in line.strip().split(" ", 2)]
        magic.line_kernel(module_name, class_name, kernel_name)

    @register_cell_magic
    def kx(line, cell):
        """
        line is kernel_name, or "default"
        """
        if line.strip():
            module_name = line.strip()
        else:
            module_name = "default"
        magic.code = cell
        magic.cell_kx(module_name)
