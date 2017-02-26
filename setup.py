import io
import sys

from setuptools import find_packages, setup


with io.open('metakernel/__init__.py', encoding='utf-8') as fid:
    for line in fid:
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break


setup(name='metakernel',
      version=version,
      description='Metakernel for Jupyter',
      long_description=open('README.rst', 'rb').read().decode('utf-8'),
      author='Steven Silvester',
      author_email='steven.silvester@ieee.org',
      url='https://github.com/Calysto/metakernel',
      requires=['ipykernel', 'pexpect (>= 4.2)'],
      install_requires=['ipykernel', 'pexpect>=4.2'],
      packages=find_packages(include=['metakernel', 'metakernel.*']),
      package_data={'metakernel': ['images/*.png']},
      classifiers=[
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
      )
