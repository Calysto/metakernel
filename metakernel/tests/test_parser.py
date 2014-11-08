
from metakernel import Parser
import os


def test_parser():
    p = Parser()

    info = p.parse_code('import nump')
    assert info['help_obj'] == info['obj'] == 'nump'

    assert p.parse_code('%python impor', 0, 10)['magic']['name'] == 'python'
    assert p.parse_code('oct(a,')['help_obj'] == 'oct'
    assert p.parse_code('! ls')['magic']['name'] == 'shell'

    info = p.parse_code('%help %lsmagic', 0, 10)
    assert info['help_obj'] == '%lsmagic'
    assert info['obj'] == '%lsm'

    info = p.parse_code('%%python\nprint("hello, world!",')
    assert info['help_obj'] == 'print'

    info = p.parse_code('%lsmagic')
    assert info['help_obj'] == '%lsmagic'

    info = p.parse_code('%')
    assert info['magic']['type'] == 'line'


def test_scheme_parser():
    function_call_regex = r'\(([^\d\W][\w\.]*)[^\)\()]*\Z'
    p = Parser(function_call_regex=function_call_regex)

    info = p.parse_code('(oct a b ')
    assert info['help_obj'] == 'oct'


def test_path_completions():
    p = Parser()

    if not os.name == 'nt':
        code = '/usr/bi'
        assert 'bin/' in p.parse_code(code)['path_matches']
    code = '~/.bashr'
    assert 'bashrc' in p.parse_code(code)['path_matches']

    for f in os.listdir('.'):
        if f.startswith('.'):
            if os.path.isdir(f):
                assert f[1:] + os.sep in p.parse_code('.')['path_matches'], f
            else:
                assert f[1:] in p.parse_code('.')['path_matches']


def test_complete0():
    p = Parser()
    info = p.parse_code('abcdefghijklmnop', 0, 4)
    assert info['obj'] == 'abcd', info


def get_parser():
    p = Parser()
    try:
        os.mkdir("/tmp/Test Dir")
    except OSError:
        pass  # dir exists
    open("/tmp/Test Dir/test.txt", "w").close()
    return p


def test_complete1():
    p = get_parser()
    info = p.parse_code('/tmp/')
    assert "Test\ Dir/" in info['path_matches'], info['path_matches']


def test_complete2():
    p = get_parser()
    info = p.parse_code('open("/tmp/')
    assert "Test Dir/" in info['path_matches'], info


def test_complete3():
    p = get_parser()
    info = p.parse_code('/tmp/Test Dir/temp.txt', 0, 14)
    assert "test.txt" in info['path_matches'], info


def test_complete4():
    p = get_parser()
    info = p.parse_code('/tmp/Test Dir')
    assert 'Dir/test.txt' in info['path_matches'], info


def test_complete5():
    p = get_parser()
    info = p.parse_code('/tmp/Test Dir/')
    assert "test.txt" in info['path_matches'], info


def test_complete6():
    p = get_parser()
    info = p.parse_code('/tmp/Test')
    assert "Test\ Dir/" in info['path_matches'], info['path_matches']


def test_complete7():
    p = get_parser()
    info = p.parse_code('/tmp/Test Dir/test.txt')
    assert not info['path_matches'], info


def test_complete8():
    p = get_parser()
    info = p.parse_code('/tmp/Test Dir/', 0, 9)
    assert 'Test\ Dir/' in info['path_matches'], info


def test_complete9():
    p = get_parser()
    info = p.parse_code('fluff\n/tmp/Test ')
    assert 'Dir/' in info['path_matches'], info


def test_complete10():
    p = get_parser()
    info = p.parse_code('/tmp/Test\\ Dir')
    assert 'Dir/test.txt' in info['path_matches']
