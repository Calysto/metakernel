# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option
import logging

class ParallelMagic(Magic):
    client = None
    view = None
    module_name = None
    class_name = None
    kernel_name = None
    retval = None

    def line_parallel(self, module_name, class_name, kernel_name, ids=None):
        """
        %parallel MODULE CLASS NAME ids[...] - construct an interface to the cluster.

        Example:

            %parallel bash_kernel BashKernel bash 
            %parallel bash_kernel BashKernel bash [0, 2, 4]

        Use %px or %%px to send code to the cluster.
        """
        from IPython.parallel import Client
        self.client = Client()
        if ids is None:
            self.view = self.client[:]
        # ids[:] = slice(None, None, None)
        # ids[1:3] = slice(1, 3, None)
        # ids[1:3:1] = slice(1, 3, 1)
        # ids[1, 2, ...] = [1, 2, Ellipsis]
        # ids[1, 2:4, ...] = [1, slice(2, 4, None), Ellipsis]
        self.module_name = module_name
        self.class_name = class_name
        self.kernel_name = kernel_name
        self.view.execute("""
from %(module_name)s import %(class_name)s
import logging
%(class_name)s.log = logging.Logger(".kernel")
kernel = %(class_name)s()
""" % {"module_name": module_name, 
       "class_name": class_name}, block=True)
        self.retval = None

    def line_px(self, expression):
        """
        %px EXPRESSION - send EXPRESSION to the cluster.

        Example:

            %px sys.version
            %px (define x 42)
            %px x

        Use %parallel to initialize the cluster.
        """
        self.retval = self.view["kernel.do_execute_direct(\"%s\")" % expression.replace('"', '\\"')]

    def cell_px(self):
        """
        %%px - send cell to the cluster.

        Example:

            %%px 
            (define x 42)

        Use %parallel to initialize the cluster.
        """
        self.retval = self.view["kernel.do_execute_direct(\"%s\")" % self.code.replace('"', '\\"')]
        self.evaluate = False

    def post_process(self, retval):
        return self.retval

def register_magics(kernel):
    kernel.register_magics(ParallelMagic)
