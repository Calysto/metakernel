from metakernel import Magic, option
from metakernel.tests.utils import get_kernel, get_log_text


class Dummy(Magic):

        @option(
        '-s', '--size', action='store',
        help='Pixel size of plots, "width,height"'
         )
        def line_dummy(self, foo, size=None):
            """
            %dummy [options] foo - Perform dummy operation on foo

            This is additional information on dummy.

            """
            self.foo = foo
            self.size = size

        def cell_spam(self):
            """
            %%spam - Cook some spam
            """
            pass

        def line_eggs(self, style):
            """
            %eggs STYLE - cook some eggs in the given style
            """
            pass


def test_get_magics():
    kernel = get_kernel()
    d = Dummy(kernel)
    line = d.get_magics('line')
    cell = d.get_magics('cell')

    assert 'dummy' in line
    assert 'spam' in cell
    assert 'eggs' in line


def test_get_help():
    kernel = get_kernel()
    d = Dummy(kernel)

    dummy_help = d.get_help('line', 'dummy', 0)
    assert dummy_help.startswith("%dummy")
    assert "    This is additional information on dummy" in d.line_dummy.__doc__, "Checking indents"
    assert "\nThis is additional information on dummy" in dummy_help, "Checking indent removal"

    dummy_help = d.get_help('line', 'dummy', 1)
    # will show this entire file, including this sentence
    assert "# will show this entire file, including this sentence" in \
            dummy_help

    spam_help = d.get_help('cell', 'spam', 0)
    assert spam_help.startswith("%%spam"), spam_help

    spam_help = d.get_help('cell', 'spam', 1)
    assert "# will show this entire file, including this sentence" in \
            spam_help


def test_option():
    kernel = get_kernel()
    d = Dummy(kernel)
    assert 'Options:' in d.line_dummy.__doc__
    assert '--size' in d.line_dummy.__doc__

    ret = d.call_magic('line', 'dummy', '', 'hey -s400,200')
    assert ret == d
    assert d.foo == 'hey', d.foo
    assert d.size == (400, 200)

    ret = d.call_magic('line', 'dummy', '', 'hey there')
    assert d.foo == 'hey there'

    ret = d.call_magic('line', 'dummy', '', 'range(1, 10)')
    assert d.foo == range(1, 10)

    ret = d.call_magic('line', 'dummy', '', '[1, 2, 3]')
    assert d.foo == [1, 2, 3]

    ret = d.call_magic('line', 'dummy', '', 'hey -l -s400,200')
    assert d.size == (400, 200)
    assert d.foo == "hey -l"

    ret = d.call_magic('line', 'dummy', '', 'hey -s -- -s400,200')
    assert d.size == (400, 200)
    assert d.foo == "hey -s"
