# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic
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
    def download(url, filename):
        g = urllib.request.urlopen(url)
        with open(filename, 'wb') as f:
            f.write(g.read())

class InstallMagicMagic(Magic):

    def line_install_magic(self, url):
        """
        %install_magic URL - download and install magic from URL

        This line magic will copy the file at the URL into your 
        personal magic folder.

        Example:
            %install_magic http://path/to/some/magic.py

        """
        parts = urlparse.urlsplit(url)
        #('http', 'example.com', '/somefile.zip', '', '')
        path = parts[2]
        filename = os.path.basename(path)
        magic_filename = os.path.join(self.kernel.get_local_magics_dir(), filename)
        try:
            download(url, magic_filename)
            self.kernel.Print("Downloaded '%s'." % magic_filename)
            self.code = "%reload_magics\n" + self.code
        except Exception as e:
            self.kernel.Error(str(e))

def register_magics(kernel):
    kernel.register_magics(InstallMagicMagic)

