import json
import os
import pkgutil
import subprocess
from subprocess import CalledProcessError
import sys

from IPython.utils.tempdir import TemporaryDirectory
try:
    from traitlets.config import Application
    _module_name = 'jupyter'
except ImportError:
    from IPython.config import Application
    _module_name = 'IPython'


class BaseInstallerApp(Application):
    def initialize(self, argv=None):
        self.argv = argv

    def start(self):
        kernel_spec = self.kernel_class.kernel_json
        with TemporaryDirectory() as td:
            dirname = os.path.join(td, kernel_spec['name'])
            os.mkdir(dirname)
            with open(os.path.join(dirname, 'kernel.json'), 'w') as f:
                json.dump(kernel_spec, f, sort_keys=True)
            filenames = ['logo-64x64.png', 'logo-32x32.png']
            for filename in filenames:
                data = pkgutil.get_data(__name__.split('.')[0],
                                        os.path.join('images', filename))
                with open(os.path.join(dirname, filename), 'wb') as f:
                    f.write(data)
            try:
                subprocess.check_call(
                    [sys.executable, '-m', _module_name,
                     'kernelspec', 'install'] + self.argv + [dirname])
            except CalledProcessError as exc:
                sys.exit(exc.returncode)
