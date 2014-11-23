
import os
from metakernel.tests.utils import get_kernel


def test_file_magic():
    kernel = get_kernel()
    kernel.do_execute("""%%file TEST.txt
LINE1
LINE2
LINE3""", False)
    assert os.path.exists("TEST.txt")
    with open("TEST.txt") as fp:
        lines = fp.readlines()
        assert len(lines) == 3
        assert lines[0] == "LINE1\n"
        assert lines[1] == "LINE2\n"
        assert lines[2] == "LINE3"

    kernel.do_execute("""%%file -a TEST.txt

LINE4
LINE5
LINE6""", False)
    assert os.path.exists("TEST.txt")
    with open("TEST.txt") as fp:
        lines = fp.readlines()
        assert len(lines) == 6
        assert lines[3] == "LINE4\n"
        assert lines[4] == "LINE5\n"
        assert lines[5] == "LINE6"

    kernel.do_execute("""%%file /tmp/tmp/TEST.txt
TEST1
TEST2
TEST3""")
    with open("/tmp/tmp/TEST.txt") as fp:
        lines = fp.readlines()
        assert len(lines) == 3
        assert lines[0] == "TEST1\n"
        assert lines[1] == "TEST2\n"
        assert lines[2] == "TEST3"

def teardown():
    import shutil
    shutil.rmtree("/tmp/tmp", ignore_errors=True)
