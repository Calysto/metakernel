from setuptools import setup


setup(name='metakernel_python',
      version='0.19.1',
      description='A Python kernel for Jupyter/IPython',
      long_description='A Python kernel for Jupyter/IPython, based on MetaKernel',
      url='https://github.com/calysto/metakernel/tree/master/metakernel_python',
      author='Douglas Blank',
      author_email='doug.blank@gmail.com',
      install_requires=['metakernel', 'jedi'],
      py_modules=['metakernel_python'],
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)
