from __future__ import print_function
import sys

from metakernel_python import MetaKernelPython

kernel = MetaKernelPython()

path = "metakernel/magics/README.md"

with open(path) as fid:
    prev = fid.read()

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

# Fix for "Title underline too short".
text = text.replace('-------', '--------')

with open(path, 'w') as fid:
    fid.write(text)

print("done!")

if text != prev:
    print('Readme changed, please commit the changes')
    print('If this is on CI, run `make help` locally to regenerate')
    sys.exit(1)
