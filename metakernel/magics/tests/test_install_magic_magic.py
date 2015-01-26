
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)
import re
import os
from metakernel.config import get_local_magics_dir

filename = get_local_magics_dir() + os.sep + "cd_magic.py"

def test_install_magic_magic():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("%install_magic https://raw.githubusercontent.com/calysto/metakernel/master/metakernel/magics/cd_magic.py")
    text = get_log_text(kernel)
    assert re.match(".*Downloaded '.*ipython/metakernel/magics/cd_magic.py'", text, re.DOTALL | re.M), "Not downloaded"
    assert os.path.isfile(filename), ("File not found: %s" % filename)

def teardown():
    os.remove(filename)
