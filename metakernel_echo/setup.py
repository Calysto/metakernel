from setuptools import setup


setup(name='metakernel_echo',
      version='0.19.1',
      description='A simple echo kernel for Jupyter/IPython',
      long_description='A simple echo kernel for Jupyter/IPython, based on MetaKernel',
      url='https://github.com/calysto/metakernel/tree/master/metakernel_echo',
      author='Douglas Blank',
      author_email='doug.blank@gmail.com',
      py_modules=['metakernel_echo'],
      install_requires=['metakernel'],
      classifiers = [
          'Framework :: IPython',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Shells',
      ]
)
