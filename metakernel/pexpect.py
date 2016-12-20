# Convenience imports from pexpect
from __future__ import absolute_import
from pexpect import which as which_base, is_executable_file, EOF, TIMEOUT
import os

try:
    from pexpect import spawn
    import pty
except ImportError:
    from pexpect.popen_spawn import PopenSpawn
    pty = None


# Add a spawn adapter for Windows
if pty is None:
    class spawn(PopenSpawn):
        def __init__(self, cmd, args=[], timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None, env=None, encoding=None, codec_errors='strict', echo=False):
            if args:
                cmd += ' ' + ' '.join(args)
            PopenSpawn.__init__(self, cmd, timeout=timeout, maxread=maxread, 
                                searchwindowsize=searchwindowsize, logfile=logfile,
                                cwd=cwd, env=env, encoding=encoding, codec_errors=codec_errors)
            self.echo = echo


# For backwards compatibility
spawnu = spawn


def which(filename):
    '''This takes a given filename; tries to find it in the environment path;
    then checks if it is executable. This returns the full path to the filename
    if found and executable. Otherwise this returns None.'''

    # Special case where filename contains an explicit path.
    if os.path.dirname(filename) != '' and is_executable_file(filename):
        return filename
    if 'PATH' not in os.environ or os.environ['PATH'] == '':
        p = os.defpath
    else:
        p = os.environ['PATH']
    pathlist = p.split(os.pathsep)
    for path in pathlist:
        ff = os.path.join(path, filename)
        if pty:
            if is_executable_file(ff):
                return ff
        else:
            pathext = os.environ.get('Pathext', '.exe;.com;.bat;.cmd')
            pathext = pathext.split(os.pathsep) + ['']
            for ext in pathext:
                if os.access(ff + ext, os.X_OK):
                    return ff + ext
    return None
