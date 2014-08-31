# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import urllib
import urlparse
import os

class InstallMagicMagic(Magic):

    def line_install(self, url):
        """%install_magic URL - download and install magic from URL"""
        opener = urllib.URLopener()
        parts = urlparse.urlsplit(url)
        #('http', 'example.com', '/somefile.zip', '', '')
        path = parts[2]
        filename = os.path.basename(path)
        magic_filename = os.path.join(os.path.abspath(__file__), filename)
        try:
            opener.retrieve(url, magic_filename)
            self.kernel.Print("Downloaded '%s'." % magic_filename)
            self.code = "%reload_magics\n" + self.code
        except Exception as e:
            self.kernel.Error(e.message)

def register_magics(kernel):
    kernel.register_magics(InstallMagicMagic)

