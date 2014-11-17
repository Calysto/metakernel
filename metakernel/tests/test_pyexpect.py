from metakernel.pyexpect import spawn, bash, cmd, python, ExceptionPyExpect
from numpy.testing.decorators import skipif
from numpy.testing import assert_raises
import os


@skipif(os.name != 'nt')
def test_windows():

    prompt = r'C:\\.*>'
    p = spawn('cmd')
    p.expect(prompt)

    p.write('echo %PATH%\n')
    path = p.expect(prompt)
    print(path)
    assert ';C:' in path

    p.write('dir\n')
    files = p.expect(prompt)
    print(files)
    assert os.listdir('.')[0] in files

    r = cmd()
    ret = r.run_command('echo %PATH%')
    print(ret)
    assert ';C:' in ret

    r.run_command('exit')
    assert_raises(ExceptionPyExpect, r.run_command, 'dir')


def test_bash():

    r = bash()
    ret = r.run_command('echo $PATH')
    print(ret)
    assert ':/usr/local' in ret

    ret = r.run_command('exit')
    print(ret)
    assert 'exit' in ret

    assert_raises(ExceptionPyExpect, r.run_command, 'ls')


@skipif(os.name == 'nt')
def test_posix():

    prompt = '>>'
    p = spawn('python')
    p.expect(prompt)

    p.write('print("hello")\n')
    resp = p.expect(prompt)
    print(resp)
    assert 'hello' in resp

    p.write('dir\n')
    resp = p.expect(prompt)
    print(resp)
    assert '<built-in function dir>' in resp

    r = python()
    ret = r.run_command('import pdb; dir(pdb)')
    print(ret)
    assert 'set_trace' in ret

    ret = r.run_command('exit()')
    assert_raises(ExceptionPyExpect, r.run_command, 'help')
