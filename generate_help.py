from __future__ import print_function

if "kernel" not in globals():
    print("""This file is designed to run like:
    jupyter console --kernel metakernel_python
    In [1]: %run generate_help.py
""")
    kernel = None
else:
    kernel = globals()["kernel"]

if kernel:
    print("Generating README.md...")
    prefix = kernel.magic_prefixes['magic']
    text = "# Line Magics\n\n"
    for magic in sorted(kernel.line_magics.keys()):
        text += "## `" + prefix + magic + "`\n\n"
        text += kernel.get_help_on(prefix + magic) + "\n\n"

    text += "# Cell Magics\n\n"
    for magic in sorted(kernel.cell_magics.keys()):
        text += "## `" + prefix + prefix + magic + "`\n\n"
        text += kernel.get_help_on(prefix + prefix + magic) + "\n\n"

    fp = open("metakernel/magics/README.md", "w")
    fp.write(text)
    fp.close()
    print("done!")
