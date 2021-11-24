import platform
import unittest
import re
import os
import sys

from metakernel import pexpect, replwrap
from metakernel.tests.utils import get_log, get_log_text

class REPLWrapTestCase(unittest.TestCase):

    def setUp(self):
        super(REPLWrapTestCase, self).setUp()
        self.save_ps1 = os.getenv('PS1', r'\$')
        self.save_ps2 = os.getenv('PS2', '>')
        os.putenv('PS1', r'\$')
        os.putenv('PS2', '>')

    def tearDown(self):
        super(REPLWrapTestCase, self).tearDown()
        os.putenv('PS1', self.save_ps1)
        os.putenv('PS2', self.save_ps2)

    def test_bash(self):
        bash = replwrap.bash()
        res = bash.run_command("time")
        assert 'real' in res, res

        # PAGER should be set to cat, otherwise man hangs
        res = bash.run_command('man sleep', timeout=2)
        assert 'SLEEP' in res, res

        # should handle CR by default
        cmd = r'for i in {1..3};do echo -ne "\r$i"; sleep 1; done'
        res = bash.run_command(cmd)
        assert '\r1\r2\r3' in res

        # should handle CRs in a stream
        res = bash.run_command(cmd, stream_handler=sys.stdout.write)
        assert res == ''

        # should handle lines with a line handler
        logger = get_log()
        res = bash.run_command('echo "1\n2\n3"', line_handler=logger.info)
        assert res == ''
        text = get_log_text(logger)
        assert '1\n2\n3' in text

    def test_multiline(self):
        bash = replwrap.bash()
        res = bash.run_command("echo '1 2\n3 4'")
        self.assertEqual(res.strip().splitlines(), ['1 2', '3 4'])

        # Should raise ValueError if input is incomplete
        try:
            bash.run_command("echo '5 6")
        except ValueError:
            pass
        else:
            assert False, "Didn't raise ValueError for incomplete input"

        # Check that the REPL was reset (SIGINT) after the incomplete input
        res = bash.run_command("echo '1 2\n3 4'")
        self.assertEqual(res.strip().splitlines(), ['1 2', '3 4'])

    def test_existing_spawn(self):
        child = pexpect.spawnu("bash", timeout=5, echo=False)
        repl = replwrap.REPLWrapper(child, re.compile('[$#]'),
                                    "PS1='{0}' PS2='{1}' "
                                    "PROMPT_COMMAND='' TERM='dumb'")

        res = repl.run_command("echo $HOME")
        assert res.startswith('/'), res

    def test_python(self):
        if platform.python_implementation() == 'PyPy':
            raise unittest.SkipTest("This test fails on PyPy because of REPL differences")

        if platform.system() == 'Darwin':
            raise unittest.SkipTest("This test fails on macOS because of REPL differences")

        p = replwrap.python(sys.executable)
        res = p.run_command('4+7')
        assert res.strip() == '11'

        res = p.run_command('for a in range(3): print(a)\n')
        assert res.strip().splitlines() == ['0', '1', '2']


if __name__ == '__main__':
    unittest.main()
