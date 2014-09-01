# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import urllib
try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse
import os

class InstallMagicMagic(Magic):

    def line_install_magic(self, url):
        """%install_magic URL - download and install magic from URL"""
        opener = urllib.URLopener()
        parts = urlparse.urlsplit(url)
        #('http', 'example.com', '/somefile.zip', '', '')
        path = parts[2]
        filename = os.path.basename(path)
        magic_filename = os.path.join(self.kernel.get_local_magics_dir(), filename)
        try:
            opener.retrieve(url, magic_filename)
            self.kernel.Print("Downloaded '%s'." % magic_filename)
            self.code = "%reload_magics\n" + self.code
        except Exception as e:
            self.kernel.Error(str(e))

def register_magics(kernel):
    kernel.register_magics(InstallMagicMagic)

