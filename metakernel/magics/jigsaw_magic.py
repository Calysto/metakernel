# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
from IPython.display import HTML
import string
import random
import urllib
try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse
import os

try:
    urllib.URLopener
    def download(url, filename):
        opener = urllib.URLopener()
        opener.retrieve(url, filename)
except: # python3
    import urllib.request
    def download(url, filename):
        g = urllib.request.urlopen(url)
        with open(filename, 'wb') as f:
            f.write(g.read())        

class JigsawMagic(Magic):

    @option(
        '-w', '--workspace', action='store', default=None,
        help='use the provided name as workspace filename'
    )
    def line_jigsaw(self, language, workspace=None):
        """
        %jigsaw LANGUAGE - show visual code editor/generator

        This line magic will allow visual code editing or generation.

        Examples:
            %jigsaw Processing
            %jigsaw Python
            %jigsaw Processing --workspace prog1.xml
        """
        # Copy iframe html to here (must come from same domain):
        ##if not os.path.isfile("Processing.html"):
        download("https://calysto.github.io/jigsaw/" + language + ".html", 
                 language + ".html")
        # Make up a random workspace name:
        if workspace is None:
            workspace = ".jigsaw-workspace-" + (''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(6))) + ".xml"
        # Display iframe:
        iframe = """<iframe src="%s.html?workspace=%s" width="100%%" height="350" style="resize: both; overflow: auto;"></frame>""" % (language, workspace)
        self.kernel.Display(HTML(iframe))

def register_magics(kernel):
    kernel.register_magics(JigsawMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = JigsawMagic(kernel)
    # Make magics callable:
    kernel.line_magics["jigsaw"] = magic

    @register_line_magic
    def jigsaw(line):
        """
        Use the Jigsaw code visualizer and generator.
        """
        kernel.call_magic("%jigsaw " + line)
