
from metakernel.tests.utils import get_kernel

EXECUTION = ""

def test_include_magic():
    global EXECUTION
    kernel = get_kernel()
    def do_execute_direct(code):
        global EXECUTION
        EXECUTION = code
    kernel.do_execute_direct = do_execute_direct
    kernel.do_execute("%%include %s" % __file__)
    assert "metakernel" in EXECUTION
    assert "AND " + "THIS" not in EXECUTION

    EXECUTION = ""
    kernel.do_execute(("%%%%include %s\nAND" + " THIS") % __file__)
    assert "metakernel" in EXECUTION
    assert "AND " + "THIS" in EXECUTION
