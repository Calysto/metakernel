from __future__ import print_function

if "kernel" not in globals():
    print("This file is designed to run with ipython console --kernel eval_kernel")
    kernel = None
else:
    kernel = globals()["kernel"]

if kernel:
    print("Generating README.md...")
    text = "# Line Magics\n\n"
    for magic in sorted(kernel.line_magics.keys()):
        text += "## `%" + magic + "`\n\n"
        text += kernel.get_help_on("%" + magic) + "\n\n"

    text += "# Cell Magics\n\n"
    for magic in sorted(kernel.cell_magics.keys()):
        text += "## `%%" + magic + "`\n\n"
        text += kernel.get_help_on("%%" + magic) + "\n\n"

    fp = open("metakernel/magics/README.md", "w")
    fp.write(text)
    fp.close()
    print("done!")
