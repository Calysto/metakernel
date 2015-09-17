# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
from IPython.display import HTML
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

    def line_jigsaw(self, language):
        """
        %jigsaw LANGUAGE - show visual code editor/generator

        This line magic will allow visual code editing or generation.

        Example:
            %jigsaw Processing
        """
        # Copy iframe html to here (must come from same domain):
        ##if not os.path.isfile("Processing.html"):
        download("https://calysto.github.io/jigsaw/" + language + ".html", 
                 language + ".html")
        # Display iframe:
        iframe = """<iframe src="%s.html" width="100%%" height="350" style="resize: both; overflow: auto;"></frame>""" % language
        self.kernel.Display(HTML(iframe))

def register_magics(kernel):
    kernel.register_magics(JigsawMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = JigsawMagic(kernel)

    @register_line_magic
    def jigsaw(line):
        magic.line_jigsaw(line)
