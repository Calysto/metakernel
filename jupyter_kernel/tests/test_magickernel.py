import os
from jupyter_kernel.tests.utils import get_kernel, get_log_text


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


def test_inspect():
    kernel = get_kernel()
    kernel.do_inspect('%lsmagic', len('%lsmagic'))
    log_text = get_log_text(kernel)
    assert "list the current line and cell magics" in log_text

    kernel.do_inspect('%lsmagic ', len('%lsmagic') + 1)
    assert True, "This was hanging..."

def test_path_complete():
    kernel = get_kernel()
    comp = kernel.do_complete('~/.ipytho', len('~/.ipytho'))
    assert comp['matches'] == ['~' + os.sep + '.ipython' + os.sep]

    path = os.listdir(os.getcwd())[0]
    comp = kernel.do_complete(path, len(path) - 1)
    if os.path.isdir(path):
        assert path + os.sep in comp['matches']
    else:
        assert path in comp['matches']


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


def test_other_kernels():
    from jupyter_kernel import MagicKernel
    class SchemeKernel(MagicKernel):
        magic_suffixes = {}
        def do_execute_direct(self, code):
            return "OK"

    kernel = get_kernel(SchemeKernel)
    resp = kernel.do_execute('dir?', None)
    assert len(resp['payload']) == 0, "should handle this, rather than using help"
    resp = kernel.do_execute('?dir?', None)
    assert len(resp['payload']) == 1, "should use help"
    message = resp['payload'][0]['data']['text/plain']
    assert "Sorry, no help is available on 'dir?'." == message, message

    comp = kernel.parse_code('dir', 0, len('dir'))
    assert (comp["start"] == 0 and 
            comp["end"] ==  3 and 
            comp["obj"] == "dir"), comp

    comp = kernel.parse_code('len(dir', 0, len('len(dir'))
    assert (comp["start"] == 4 and 
            comp["end"] ==  7 and 
            comp["obj"] == "dir"), comp

    comp = kernel.parse_code('(dir', 0, len('(dir'))
    assert (comp["start"] == 1 and 
            comp["end"] ==  4 and 
            comp["obj"] == "dir"), comp

def teardown():
    if os.path.exists("TEST.txt"):
        os.remove("TEST.txt")
