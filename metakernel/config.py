try:
    from IPython.paths import get_ipython_dir
except ImportError:
    from IPython.utils.path import get_ipython_dir
import os


def get_history_file(kernel):
    """Gets the history file for the kernel.

    Histories are stored in ~/.ipython/metakernel/history
    """
    base = get_ipython_dir()
    dname = os.path.join(base, 'metakernel', 'history')
    if not os.path.exists(dname):
            os.makedirs(dname)
    if hasattr(kernel, 'implementation'):
        fname = kernel.implementation.lower()
    else:
        fname = kernel.__class__.__name__
        fname = fname.replace("Magic", '').lower()
    path = os.path.join(dname, fname + '.txt')
    if not os.path.exists(path):
        with open(path, 'wb'):
            pass
    return path


def get_local_magics_dir():
    """
    Ensures that there is a ~/.ipython/metakernel/magics directory,
    and returns the path to it.
    """
    base = get_ipython_dir()
    dname = os.path.join(base, 'metakernel', 'magics')
    if not os.path.exists(dname):
        os.makedirs(dname)
    return dname
