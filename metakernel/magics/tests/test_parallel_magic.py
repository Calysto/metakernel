
from metakernel.tests.utils import get_kernel, get_log_text, EvalKernel
import os
import time

#def setup_func():
#    ## start up a cluster in the background with three nodes:
#    os.system("ipcluster start --n=3 &")
#    time.sleep(5) ## give the cluster time to start

def test_parallel_magic():
    kernel = get_kernel(EvalKernel)
    # start up an EvalKernel on each node:
    kernel.do_execute("%parallel eval_kernel EvalKernel", False)
    time.sleep(5) ## give the clients time to start
    # Now, execute something on each one:
    kernel.do_execute("%px cluster_rank", False)
    results = eval(get_log_text(kernel).strip())
    assert sorted(results) == [0, 1, 2], ("Results were actually %s" % results)
    
#def teardown():
#    ## shutdown the cluster:
#    os.system("ipcluster stop")
