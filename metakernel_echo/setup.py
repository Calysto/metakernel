from distutils.command.install import install
from distutils.core import setup
from distutils import log
import os
import json
import sys

kernel_json = {
    "argv": [sys.executable,
	     "-m", "metakernel_echo",
	     "-f", "{connection_file}"],
    "display_name": "MetaKernel Echo",
    "language": "text",
    "codemirror_mode": "text"
}

class install_with_kernelspec(install):
    def run(self):
        install.run(self)
        from IPython.kernel.kernelspec import install_kernel_spec
        from IPython.utils.tempdir import TemporaryDirectory
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755) # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            # TODO: Copy resources once they're specified
            log.info('Installing kernel spec')
            try:
                install_kernel_spec(td, 'metakernel_echo', system=not self.user, replace=True)
            except:
                install_kernel_spec(td, 'metakernel_echo', system=False, replace=True)


svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='metakernel_echo',
      version='0.5.1',
      description='A simple echo kernel for Jupyter/IPython',
      long_description="A simple echo kernel for Jupyter/IPython, based on MetaKernel",
      url="https://github.com/blink1073/metakernel/tree/master/metakernel_echo",
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
