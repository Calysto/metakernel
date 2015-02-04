import pkgutil
import os


def install_kernel_resources(destination, resource="metakernel", files=None):
    """
    Copy the resource files to the kernelspec folder.
    """
    if files is None:
        files = ["logo-64x64.png", "logo-32x32.png"]
    for filename in files:
        data = pkgutil.get_data(resource, os.path.join('images', filename))
        with open(os.path.join(destination, filename), "wb") as fp:
            fp.write(data)
