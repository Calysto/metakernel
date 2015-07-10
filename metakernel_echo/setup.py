from distutils.command.install import install
from distutils.core import setup
import sys

PY3 = sys.version_info[0] >= 3

kernel_json = {
    "argv": [sys.executable,
	     "-m", "metakernel_echo",
	     "-f", "{connection_file}"],
    "display_name": "MetaKernel Echo %i" % (3 if PY3 else 2),
    "language": "echo",
    "name": "metakernel_echo",
}


class install_with_kernelspec(install):

    def run(self):
        install.run(self)
        from metakernel.utils import install_spec
        install_spec(kernel_json)

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='metakernel_echo',
      version='0.7.0',
      description='A simple echo kernel for Jupyter/IPython',
      long_description="A simple echo kernel for Jupyter/IPython, based on MetaKernel",
      url="https://github.com/calysto/metakernel/tree/master/metakernel_echo",
      author='Douglas Blank',
      author_email='doug.blank@gmail.com',
      py_modules=['metakernel_echo'],
      install_requires=["metakernel"],
      cmdclass={'install': install_with_kernelspec},
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)
