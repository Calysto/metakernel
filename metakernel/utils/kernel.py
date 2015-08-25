import pkgutil
import os
import json
import sys
from distutils import log


def install_kernel_resources(destination, resource="metakernel", files=None):
    """
    Copy the resource files to the kernelspec folder.
    """
    if files is None:
        files = ["logo-64x64.png", "logo-32x32.png"]
    for filename in files:
        try:
            data = pkgutil.get_data(resource, os.path.join('images', filename))
            with open(os.path.join(destination, filename), "wb") as fp:
                fp.write(data)
        except Exception:
            pass


def install_spec(kernel_json):
    user = '--user' in sys.argv
    try:
        from ipykernel.kerspec import install_kernel_spec
    except ImportError:
        from IPython.kernel.kernelspec import install_kernel_spec
    from IPython.utils.tempdir import TemporaryDirectory
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755)  # Starts off as 700, not user readable
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)
        log.info('Installing kernel spec')
        install_kernel_resources(td)
        kernel_name = kernel_json['name']
        try:
            install_kernel_spec(td, kernel_name, user=user,
                                replace=True)
        except:
            install_kernel_spec(td, kernel_name, user=not user,
                                replace=True)
