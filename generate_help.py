
try:
    kernel
except:
    print("This file is designed to run with ipython console --kernel eval_kernel")
    kernel = None

if kernel:
    text = "# Line Magics\n\n"
    for magic in sorted(kernel.line_magics.keys()):
        text += "## `%" + magic + "`\n\n"
        text += kernel.get_help_on("%" + magic) + "\n\n"

    text = "# Cell Magics\n\n"
    for magic in sorted(kernel.cell_magics.keys()):
        text += "## `%%" + magic + "`\n\n"
        text += kernel.get_help_on("%%" + magic) + "\n\n"

    fp = open("MagicHelp.md", "w")
    fp.write(text)
    fp.close()
