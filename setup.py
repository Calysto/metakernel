from distutils.core import setup
import sys

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='calico',
      version='0.2.8',
      description='Tools for Python and IPython',
      long_description="Tools for IPython, and Scheme for Python",
      author='Douglas Blank',
      author_email='doug.blank@gmail.com',
      url="https://bitbucket.org/ipre/calico/src/master/src/",
      packages=['calico', 'calico.magics'],
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Programming Language :: Scheme',
          'Topic :: System :: Shells',
      ]
)
