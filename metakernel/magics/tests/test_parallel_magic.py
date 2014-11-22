
from metakernel.tests.utils import get_kernel, get_log_text, EvalKernel
import os
import time

def test_parallel_magic():
    kernel = get_kernel(EvalKernel)
    # start up an EvalKernel on each node:
    kernel.do_execute("%parallel metakernel_python MetaKernelPython", False)
    # Now, execute something on each one:
    kernel.do_execute("%px cluster_rank", False)
    results = get_log_text(kernel)
    assert "[0, 1, 2]" in results, results
    
# Starting the cluster from here doesn't work with nosetests
# so we start `ipcluster` before we test.

#def setup_func():
#    ## start up a cluster in the background with three nodes:
#    os.system("ipcluster start --n=3 &")

#def teardown():
#    ## shutdown the cluster:
#    os.system("ipcluster stop")

