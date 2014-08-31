from IPython.utils.path import get_ipython_dir
import os


def _get_kernel_dir(name):
    base = get_ipython_dir()
    kernel_dir = os.path.join(base, 'kernels', name)
    if not os.path.exists(kernel_dir):
        raise ValueError('No kernel named %s exists!' % name)
    return kernel_dir


def _get_profile_dir(kernel_name, profile_name):
    kernel_dir = _get_kernel_dir(kernel_name)
    return os.path.join(kernel_dir, 'profile_%s' % profile_name)


def get_startup_files(kernel_name, profile_name):
    profile_dir = _get_profile_dir(kernel_name, profile_name)
    startup_dir = os.path.join(profile_dir, 'startup')
    fnames = os.listdir(startup_dir)
    return sorted(os.path.join(startup_dir, f) for f in fnames)


def get_history_file(kernel_name, profile_name):
    profile_dir = _get_profile_dir(kernel_name, profile_name)
    return os.path.join(os.path.join(profile_dir, 'history.txt'))


def create_kernel_dir(name):
    kernel_dir = _get_kernel_dir(name)
    if not 'extensions' in os.listdir(kernel_dir):
        for dname in ['extensions', 'nbextensions']:
            os.mkdir(os.path.join(kernel_dir, dname))
    create_profile_dir(name, 'default')


def create_profile_dir(kernel_name, profile_name):
    profile_dir = _get_profile_dir(kernel_name, profile_name)
    if os.path.exists(profile_dir):
        raise ValueError('Profile "%s" already exists' % profile_name)
    os.makedirs(os.path.join(profile_dir, 'startup'))
    with open(os.path.join(profile_dir, 'startup', 'README.txt'), 'wb') as fid:
        fid.write("""This is the  %s Jupyter startup directory

.py  files in this directory will be run *prior* to any code or files specified
via the exec_lines or exec_files configurables whenever you load this profile.
You can also put files in the native kernel language that will be executed at startup.

Files will be run in lexicographical order, so you can control the execution order of files
with a prefix, e.g. for a javascript kernel::

    00-first.py
    50-middle.js
    99-last.py

""" % kernel_name)
    open(os.path.join(profile_dir, 'history.txt'), 'w').close()


if __name__ == '__main__':
    create_kernel_dir('echo_kernel')
