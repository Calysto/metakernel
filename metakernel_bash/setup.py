from distutils.command.install import install
from distutils.core import setup
import sys

kernel_json = {
    "argv": [sys.executable,
	     "-m", "metakernel_bash",
	     "-f", "{connection_file}"],
    "display_name": "MetaKernel Bash",
    "language": "bash",
    "name": "metakernel_bash",
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

setup(name='metakernel_bash',
      version='0.7.0',
      description='A Bash kernel for Jupyter/IPython',
      long_description="A Bash kernel for Jupyter/IPython, based on MetaKernel",
      url="https://github.com/calysto/metakernel/tree/master/metakernel_bash",
      author='Steven Silvester',
      author_email='steven.silvester@ieee.org',
      py_modules=['metakernel_bash'],
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
