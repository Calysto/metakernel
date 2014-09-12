# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic, option
import logging

class Slice(object):
    """Utility class for making slice ranges."""
    def __getitem__(self, item):
        return item

slicer = Slice() ## instance to parse slices

class ParallelMagic(Magic):
    client = None
    view = None
    view_load_balanced = None
    module_name = None
    class_name = None
    kernel_name = None
    ids = None
    retval = None

    @option(
        '-k', '--kernel_name', action='store', default="default",
        help='arbitrary name given to reference kernel'
    )
    @option(
        '-i', '--ids', action='store', default=None,
        help='the machine ids to use from the cluster'
        
    )
    def line_parallel(self, module_name, class_name, kernel_name="default", ids=None):
        """
        %parallel MODULE CLASS [-k NAME] [-i [...]] - construct an interface to the cluster.

        Example:

            %parallel bash_kernel BashKernel 
            %parallel bash_kernel BashKernel -k bash
            %parallel bash_kernel BashKernel --i [0,2:5,9,...]

        Use %px or %%px to send code to the cluster.
        """
        from IPython.parallel import Client
        self.client = Client()
        if ids is None:
            self.view = self.client[:]
        else:
            # ids[:] = slice(None, None, None)
            # ids[1:3] = slice(1, 3, None)
            # ids[1:3:1] = slice(1, 3, 1)
            # ids[1, 2, ...] = [1, 2, Ellipsis]
            # ids[1, 2:4, ...] = [1, slice(2, 4, None), Ellipsis]
            try:
                ids_slice = eval("slicer%s" % ids) # slicer[0,...,7]
            except:
                ids_slice = slicer[:]
            if isinstance(ids_slice, (slice, int)):
                self.view = self.client[ids_slice]
            else: # tuple of indexes/slices
                # TEST: can we do this?
                # FIXME: if so, handle Ellipsis
                view = []
                for item in ids_slice:
                    view.append(self.client[item])
                self.view = view
        self.view_load_balanced = self.client.load_balanced_view()
        self.module_name = module_name
        self.class_name = class_name
        self.kernel_name = kernel_name
        self.view.execute("""
try:
    kernels
except:
    kernels = {}
from %(module_name)s import %(class_name)s
%(class_name)s.subkernel(get_ipython().parent)
kernels['%(kernel_name)s'] = %(class_name)s()
""" % {"module_name": module_name, 
       "class_name": class_name,
       "kernel_name": kernel_name}, 
                          block=True)

        self.view["kernels['%s'].set_variable(\"cluster_size\", %s)" % (
            kernel_name, len(self.client))]
        self.client[:].scatter('cluster_rank', self.client.ids, flatten=True)
        self.view["kernels['%s'].set_variable(\"cluster_rank\", cluster_rank)" % (
            kernel_name)]
        self.retval = None

    @option(
        '-k', '--kernel_name', action='store', default=None,
        help='kernel name given to use for execution'
    )
    @option(
        '-e', '--evaluate', action='store_true', default=False,
        help=('evaluate code in the current kernel, too. The current ' +
              'kernel should be of the same language as the cluster.')
    )
    def line_px(self, expression, kernel_name=None, evaluate=False):
        """
        %px EXPRESSION - send EXPRESSION to the cluster.

        Example:

            %px sys.version
            %px -k scheme (define x 42)
            %px x

        Use %parallel to initialize the cluster.
        """
        if kernel_name is None:
            kernel_name = self.kernel_name
        self.retval = self.view["kernels['%s'].do_execute_direct(\"%s\")" % (
            kernel_name, self._clean_code(expression))]
        if evaluate:
            self.code = expression

    def _clean_code(self, expr):
        return expr.strip().replace('"', '\\"').replace("\n", "\\n")

    ## px --kernel NAME
    @option(
        '-k', '--kernel_name', action='store', default=None,
        help='kernel name given to use for execution'
    )
    @option(
        '-e', '--evaluate', action='store_true', default=False,
        help=('evaluate code in the current kernel, too. The current ' +
              'kernel should be of the same language as the cluster.')
    )
    def cell_px(self, kernel_name=None, evaluate=False):
        """
        %%px - send cell to the cluster.

        Example:

            %%px 
            (define x 42)

        Use %parallel to initialize the cluster.
        """
        if kernel_name is None:
            kernel_name = self.kernel_name
        self.retval = self.view["kernels['%s'].do_execute_direct(\"%s\")" % (
            kernel_name, self._clean_code(self.code))]
        self.evaluate = evaluate

    def line_pmap(self, function_name, args, kernel_name=None):
        """
        %pmap FUNCTION [ARGS1, ARGS2, ...] - call FUNCTION
        """
        if kernel_name is None:
            kernel_name = self.kernel_name

        # FIXME: horrible hack
        self.view.execute("""
import os
os.kernels = kernels
""")
        self.retval = self.view_load_balanced.map_async(
            lambda arg, kname=kernel_name, fname=function_name: os.kernels[kname].do_function_direct(fname, arg),
            eval(args))

    def post_process(self, retval):
        try:
            ## any will crash on numpy arrays
            if isinstance(self.retval, list) and not any(self.retval):
                return None
        except:
            pass
        return self.retval

def register_magics(kernel):
    kernel.register_magics(ParallelMagic)
