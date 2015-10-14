# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import logging
import time

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
    retry = False

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

        cluster_size and cluster_rank variables are set upon 
        initialization of the remote node (if the kernel 
        supports %set).

        Use %px or %%px to send code to the cluster.
        """
        try:
            from ipyparallel import Client
        except ImportError:
            from IPython.parallel import Client
        count = 1
        while count <= 5:
            try:
                self.client = Client()
                break
            except:
                print("Waiting on cluster to start...")
                time.sleep(2)
            count += 1
        if count == 6:
            raise Exception("Cluster was not started.")
        if ids is None:
            count = 1
            while count <= 5:
                try:
                    self.view = self.client[:]
                    break
                except:
                    print("Waiting for engines...")
                    time.sleep(2)
                count += 1
            if count == 6:
                raise Exception("Engines were not started.")
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
                count = 1
                while count <= 5:
                    try:
                        self.view = self.client[ids_slice]
                        break
                    except:
                        print("Waiting for engines...")
                        time.sleep(2)
                    count += 1
                if count == 6:
                    raise Exception("Engines were not started.")
            else: # tuple of indexes/slices
                # FIXME: if so, handle Ellipsis
                view = None
                for item in ids_slice:
                    count = 1
                    while count <= 5:
                        try:
                            client = self.client[item]
                            if view:
                                ## FIXME: can't do this:
                                view.append(client)
                            else:
                                view = client
                            break
                        except:
                            print("Waiting on cluster to start...")
                            time.sleep(2)
                        count += 1
                    if count == 6:
                        raise Exception("Cluster was not started.")
                self.view = view
        self.view_load_balanced = self.client.load_balanced_view()
        self.module_name = module_name
        self.class_name = class_name
        self.kernel_name = kernel_name
        self.view.execute("""
import os
for key, value in %(env)s.items():
    os.environ[key] = value
try:
    kernels
except:
    kernels = {}
from %(module_name)s import %(class_name)s
%(class_name)s.subkernel(get_ipython().parent)
kernels['%(kernel_name)s'] = %(class_name)s()
""" % {"module_name": module_name, 
       "class_name": class_name,
       "kernel_name": kernel_name,
       "env": str(self.kernel.env)}, 
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
            %px cluster_rank

        cluster_size and cluster_rank variables are set upon 
        initialization of the remote node (if the kernel 
        supports %set).

        Use %parallel to initialize the cluster.
        """
        expression = str(expression)
        if kernel_name is None:
            kernel_name = self.kernel_name
        if self.retry:
            count = 1
            while count <= 5:
                try:
                    self.retval = self.view["kernels['%s'].do_execute_direct(\"%s\")" % (
                        kernel_name, self._clean_code(expression))]
                    break
                except:
                    print("Waiting on cluster clients to start...")
                    time.sleep(2)
                count += 1
            if count == 6:
                raise Exception("Cluster clients have not started.")
            self.retry = False
        else:
            try:
                self.retval = self.view["kernels['%s'].do_execute_direct(\"%s\")" % (
                    kernel_name, self._clean_code(expression))]
            except Exception as e:
                self.retval = str(e)
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
        %pmap FUNCTION [ARGS1,ARGS2,...] - ("parallel map") call a FUNCTION on args

        This line magic will apply a function name to all of the
        arguments given one at a time using a dynamic load balancing scheduler.

        Currently, the args are provided as a Python expression (with no spaces).

        You must first setup a cluster using the %parallel magic.

        Examples:

            %pmap function-name-in-language range(10)
            %pmap function-name-in-language [1,2,3,4]
            %pmap run_experiment range(1,100,5)
            %pmap run_experiment ["test1","test2","test3"]
            %pmap f [(1,4,7),(2,3,5),(7,2,2)]

        The function name must be a function that is available on all
        nodes in the cluster. For example, you could:

            %%px
            (define myfunc
               (lambda (n)
                 (+ n 1)))

        to define myfunc on all machines (use %%px -e to also define
        it in the running notebook or console). Then you can apply it
        to a list of arguments:

            %%pmap myfunc range(100)

        The load balancer will run myfunc on the next available node
        in the cluster.

        Note: not all languages may support running a function via this magic.
        """
        if kernel_name is None:
            kernel_name = self.kernel_name

        # To make sure we can find `kernels`:
        try:
            from ipyparallel.util import interactive
        except ImportError:
            from IPython.parallel.util import interactive
        f = interactive(lambda arg, kname=kernel_name, fname=function_name: \
                        kernels[kname].do_function_direct(fname, arg))
        self.retval = self.view_load_balanced.map_async(f, eval(args))

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
