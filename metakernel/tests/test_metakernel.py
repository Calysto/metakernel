import os
import re
import subprocess
from nose.tools import assert_raises

from metakernel import MetaKernel
from metakernel.tests.utils import (get_kernel, get_log_text, EvalKernel, 
                                    clear_log_text)

def test_magics():
    kernel = get_kernel()
    for magic in ['cd', 'connect_info', 'download', 'html', 'install_magic',
                  'javascript', 'latex', 'lsmagic', 'magic', 'plot',
                  'reload_magics', 'shell']:
        msg = "magic '%s' is not in line_magics" % magic
        assert magic in kernel.line_magics, msg

    for magic in ['file', 'html', 'javascript', 'latex', 'shell', 'time']:
        assert magic in kernel.cell_magics

    with open('TEST.txt', 'wb'):
        pass
    kernel.get_magic('%shell ls')
    log_text = get_log_text(kernel)
    assert 'TEST.txt' in log_text
    os.remove('TEST.txt')


def test_help():
    kernel = get_kernel()
    resp = kernel.get_help_on('%shell', 0)
    assert 'run the line as a shell command' in resp

    resp = kernel.do_execute('%cd?', False)
    assert 'change current directory of session' in resp[
        'payload'][0]['data']['text/plain']

    resp = kernel.get_help_on('what', 0)
    assert resp == "Sorry, no help is available on 'what'.", ("response was actually %s" % resp)


def test_complete():
    kernel = get_kernel()
    comp = kernel.do_complete('%connect_', len('%connect_'))
    assert comp['matches'] == ['%connect_info'], str(comp['matches'])

    comp = kernel.do_complete('%%fil', len('%%fil'))
    assert comp['matches'] == ['%%file'], str(comp['matches'])

    comp = kernel.do_complete('%%', len('%%'))
    assert '%%file' in comp['matches']
    assert '%%html' in comp['matches']


def test_inspect():
    kernel = get_kernel()
    kernel.do_inspect('%lsmagic', len('%lsmagic'))
    log_text = get_log_text(kernel)
    assert "list the current line and cell magics" in log_text

    kernel.do_inspect('%lsmagic ', len('%lsmagic') + 1)


def test_path_complete():
    kernel = get_kernel()
    comp = kernel.do_complete('~/.ipytho', len('~/.ipytho'))
    assert comp['matches'] == ['ipython/']

    paths = [p for p in os.listdir(os.getcwd())
             if not p.startswith('.') and not '-' in p]

    for path in paths:
        comp = kernel.do_complete(path, len(path) - 1)

        if os.path.isdir(path):
            path = path.split()[-1]
            assert path + os.sep in comp['matches'], ("'%s' not in '%s'" % (path + os.sep, comp['matches']))
        else:
            path = path.split()[-1]
            assert path in comp['matches'], (comp['matches'], path)


def test_ls_path_complete():
    kernel = get_kernel()
    comp = kernel.do_complete('! ls ~/.ipytho', len('! ls ~/.ipytho'))
    assert comp['matches'] == ['ipython/'], comp


def test_history():
    kernel = get_kernel()
    kernel.do_execute('!ls', False)
    kernel.do_execute('%cd ~', False)
    kernel.do_shutdown(False)

    with open(kernel.hist_file, 'rb') as fid:
        text = fid.read().decode('utf-8', 'replace')

    assert '!ls' in text
    assert '%cd' in text

    kernel = get_kernel()
    kernel.do_history(None, None, None)
    assert '!ls' in ''.join(kernel.hist_cache)
    assert '%cd ~'


def test_sticky_magics():
    kernel = get_kernel()
    kernel.do_execute('%%%html\nhello', None)
    text = get_log_text(kernel)

    assert 'html added to session magics' in text
    kernel.do_execute('<b>hello</b>', None)
    kernel.do_execute('%%%html', None)
    text = get_log_text(kernel)
    assert text.count('Display Data') == 2
    assert 'html removed from session magics' in text


def test_shell_partial_quote():
    kernel = get_kernel()
    kernel.do_execute('%cd "/home/', False)
    text = get_log_text(kernel)
    assert """No such file or directory: '"/home/'""" in text, text

def test_other_kernels():
    class SchemeKernel(MetaKernel):
        help_suffix = {}
        def do_execute_direct(self, code):
            return "OK"

    kernel = get_kernel(SchemeKernel)
    resp = kernel.do_execute('dir?', None)
    assert len(resp['payload']) == 0, "should handle this, rather than using help"
    resp = kernel.do_execute('?dir?', None)
    assert len(resp['payload']) == 1, "should use help"
    message = resp['payload'][0]['data']['text/plain']
    assert "Sorry, no help is available on 'dir?'." == message, message

    content = kernel.do_inspect('dir', len('dir'))
    assert (content['status'] == 'aborted' and 
            content['found'] == False), "do_inspect should abort, and be not found"

    content = kernel.do_inspect('len(dir', len('len(dir'))
    assert (content['status'] == 'aborted' and 
            content['found'] == False), "do_inspect should abort, and be not found"

    content = kernel.do_inspect('(dir', len('(dir'))
    assert (content['status'] == 'aborted' and 
            content['found'] == False), "do_inspect should abort, and be not found"

    # Now change it so that there is help available:
    kernel.get_kernel_help_on = lambda info, level=0, none_on_fail=False: \
                                   "Help is available on '%s'." % info['obj']
    content = kernel.do_inspect('dir', len('dir'))
    message = content["data"]["text/plain"]
    match = re.match("Help is available on '(.*)'", message)
    assert match.groups()[0] == "dir", message + " for 'dir'"

    content = kernel.do_inspect('len(dir', len('len(dir'))
    message = content["data"]["text/plain"]
    match = re.match("Help is available on '(.*)'", message)
    assert match.groups()[0] == "dir", message + " for 'dir'"

    content = kernel.do_inspect('(dir', len('(dir'))
    message = content["data"]["text/plain"]
    match = re.match("Help is available on '(.*)'", message)
    assert match.groups()[0] == "dir", message + " for 'dir'"


def test_do_execute_meta():
    kernel = get_kernel(EvalKernel)
    kernel.do_execute("~~META~~: reset")
    text = get_log_text(kernel)
    assert "RESET" in text, text
    clear_log_text(kernel)

    kernel.do_execute("~~META~~: stop")
    text = get_log_text(kernel)
    assert "STOP" in text, text
    clear_log_text(kernel)

    kernel.do_execute("~~META~~: step")
    text = get_log_text(kernel)
    assert "STEP" in text, text
    clear_log_text(kernel)

    kernel.do_execute("~~META~~: inspect something")
    text = get_log_text(kernel)
    assert "INSPECT" in text, text
    clear_log_text(kernel)


def test_do_execute_meta2():
    kernel = get_kernel()
    for code in ['reset, stop', 'step', 'inspect ', 'garbage']:
        assert_raises(Exception, kernel.do_execute, "~~META~~: %s" % code)


def test_misc():
    class TestKernel(MetaKernel):
        def do_execute_file(self, filename):
            self.Print("This language does not support running files")

        def do_function_direct(self, f, arg):
            self.Print("%s(%s)" % (f, self.repr(arg)))

        def repr(self, arg):
            return "XXX"

    kernel = get_kernel(TestKernel)
    assert kernel.do_execute_direct('garbage') is None
    kernel.do_execute_file('hello.txt')
    assert "This language does not support" in get_log_text(kernel)

    clear_log_text(kernel)

    kernel.do_function_direct('hello', 'world')
    text = get_log_text(kernel)
    assert "hello(XXX)" in text, text
    kernel.restart_kernel()

    ret = kernel.do_is_complete('hello\n')
    assert ret == {'status': 'complete'}

    assert kernel.do_inspect('hello', 10) is None

def teardown():
    if os.path.exists("TEST.txt"):
        os.remove("TEST.txt")
