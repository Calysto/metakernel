import pkgutil
import os

def install_kernel_resources(destination):
    """
    Copy the resource files to the kernelspec folder.
    """
    for filename in ["logo-64x64.png", "logo-32x32.png"]:
        data = pkgutil.get_data("metakernel", filename)
        with open(os.path.join(destination, filename), "w") as fp:
            fp.write(data)
