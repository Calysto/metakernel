# Convenience imports from pexpect
from __future__ import absolute_import
import os
import signal
from pexpect import is_executable_file, EOF, TIMEOUT, __file__ as PEXPECT_DIR

try:
    from pexpect import spawn as pty_spawn
    import pty
except ImportError:
    from pexpect.popen_spawn import PopenSpawn
    pty = None


def spawn(command, args=[], timeout=30, maxread=2000,
          searchwindowsize=None, logfile=None, cwd=None, env=None,
          ignore_sighup=True, echo=True, encoding='utf-8', **kwargs):
    '''This is the main entry point for Pexpect. Use this functio to start
    and control child applications.

    See https://github.com/pexpect/pexpect/blob/master/pexpect/pty_spawn.py
    for more information.
    '''
    codec_errors = kwargs.get('codec_errors', kwargs.get('errors', 'strict'))
    if pty is None:
        if args:
            command += ' ' + ' '.join(args)
        child = PopenSpawn(command, timeout=timeout, maxread=maxread,
                           searchwindowsize=searchwindowsize,
                           logfile=logfile, cwd=cwd, env=env,
                           encoding=encoding, codec_errors=codec_errors)
        child.echo = echo
    else:
        try:
            # Signal handlers are inherited by forked processes, and we can't easily
            # reset it from the subprocess. Since kernelapp ignores SIGINT except in
            # message handlers, we need to temporarily reset the SIGINT handler here
            # so that the child and its children are interruptible.
            try:
                sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
            except ValueError:
                # Only Main Thread can handle signals
                sig = None
            child = pty_spawn(command, args=args, timeout=timeout,
                              maxread=maxread,
                              searchwindowsize=searchwindowsize,
                              logfile=logfile, cwd=cwd, env=env,
                              encoding=encoding, codec_errors=codec_errors)
        finally:
            if sig:
                signal.signal(signal.SIGINT, sig)
    return child


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
