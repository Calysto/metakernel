# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from calico import Magic
import urllib
import urlparse
import os

class DownloadMagic(Magic):
    name = "download"
    help_lines = [" %download URL [FILENAME] - download file from URL"]

    def line(self, args):
        opener = urllib.URLopener()
        if " " in args:
            url, filename = args.split(" ", 1)
        else:
            url = args
            parts = urlparse.urlsplit(url)
            #('http', 'example.com', '/somefile.zip', '', '')
            path = parts[2]
            filename = os.path.basename(path)
        try:
            opener.retrieve(url, filename)
            self.kernel.Print("Downloaded '%s'." % filename)
        except Exception as e:
            self.kernel.Error(e.message)

def register_magics(magics):
    magics[DownloadMagic.name] = DownloadMagic
    
