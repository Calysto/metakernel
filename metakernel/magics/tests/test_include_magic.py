
from metakernel.tests.utils import get_kernel

EXECUTION = ""

def test_include_magic():
    global EXECUTION
    kernel = get_kernel()
    def do_execute_direct(code):
        global EXECUTION
        EXECUTION = code
    kernel.do_execute_direct = do_execute_direct
    FILE = __file__
    if FILE.endswith(".pyc"):
        FILE = FILE[:-1]
    kernel.do_execute("%%include %s" % FILE)
    assert "metakernel" in EXECUTION
    assert ("AND " + "THIS") not in EXECUTION

    EXECUTION = ""
    kernel.do_execute(("%%include %s\nAND" + " THIS") % FILE)
    assert "metakernel" in EXECUTION
    assert ("AND " + "THIS") in EXECUTION

    EXECUTION = ""
    kernel.do_execute("%%include '%s' '%s'" % (FILE, FILE))
    assert "metakernel" in EXECUTION
    assert ("AND " + "THIS") not in EXECUTION
