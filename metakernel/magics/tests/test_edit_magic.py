
from metakernel.tests.utils import (get_kernel, get_log_text, 
                                    clear_log_text, EvalKernel)

def test_edit_magic():
    kernel = get_kernel(EvalKernel)
    results = kernel.do_execute("%edit LICENSE.txt")
    text = results["payload"][0]["text"]
    assert '%%file LICENSE.txt\n\n# Copyright (c) Ipython Kernel Development Team.\n# Distributed under the terms of the Modified BSD License.\n\n\n# Copyright (c) Metakernel Development Team.\n# Distributed under the terms of the Modified BSD License.\n\n' == text, text

