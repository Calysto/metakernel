from distutils.command.install import install
from distutils.core import setup
import os.path
import json
import sys

kernel_json = {
    "argv": [sys.executable,
	     "-m", "bash_kernel",
	     "-f", "{connection_file}"],
    "display_name": "bash_kernel",
    "language": "Bash"
}

class install_with_kernelspec(install):
    def run(self):
        install.run(self)
        from IPython.kernel.kernelspec import KernelSpecManager
        from IPython.utils.path import ensure_dir_exists
        destdir = os.path.join(KernelSpecManager().user_kernel_dir,
                               'bash_kernel')
        ensure_dir_exists(destdir)
        with open(os.path.join(destdir, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='bash_kernel',
      version='0.1',
      description='A simple bash kernel for Jupyter/IPython',
      long_description="A simple bash kernel for Jupyter/IPython, based on MagicKernel",
      url="https://github.com/blink1073/jupyter_kernel/tree/master/bash_kernel",
      author='Steven Silvester',
      author_email='steven.silvester@ieee.org',
      py_modules=['bash_kernel'],
      install_requires=["jupyter_kernel"],
      cmdclass={'install': install_with_kernelspec},
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)
