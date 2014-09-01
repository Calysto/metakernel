from distutils.core import setup
import sys

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='jupyter_kernel',
      version='0.2',
      description='Jupyter Kernel Tools',
      long_description="Jupyter Kernel Tools using kernel wrappers",
      author='Steven Silvester',
      author_email='steven.silvester@ieee.or',
      url="https://github.com/blink1073/jupyter_kernel",
      packages=['jupyter_kernel', 'jupyter_kernel.magics'],
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Programming Language :: Scheme',
          'Topic :: System :: Shells',
      ]
)
