try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup
import sys


svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)


with open('jupyter_kernel/__init__.py', 'rb') as fid:
    for line in fid:
        line = line.decode('utf-8')
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break


setup(name='jupyter_kernel',
      version=version,
      description='Jupyter Kernel Tools',
      long_description="Jupyter Kernel Tools using kernel wrappers",
      author='Steven Silvester',
      author_email='steven.silvester@ieee.org',
      url="https://github.com/blink1073/jupyter_kernel",
      install_requires=['IPython'],
      packages=['jupyter_kernel', 'jupyter_kernel.magics',
                'jupyter_kernel.tests'],
      classifiers=[
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Programming Language :: Scheme',
          'Topic :: System :: Shells',
      ]
      )
