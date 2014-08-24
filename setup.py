from distutils.core import setup
import sys

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='ipython_kernel',
      version='0.1.0',
      description='IPython Kernel Tools',
      long_description="IPython Kernel Tools using kernel wrappers",
      author='Steven Silvester',
      author_email='steven.silvester@ieee.or',
      url="https://github.com/blink1073/ipython_kernel",
      packages=['ipython_kernel', 'ipython_kernel.magics'],
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Programming Language :: Scheme',
          'Topic :: System :: Shells',
      ]
)
