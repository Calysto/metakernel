# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.


from metakernel import Magic, option
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

class DownloadMagic(Magic):

    @option(
        '-f', '--filename', action='store', default=None,
        help='use the provided name as filename'
    )
    def line_download(self, url, filename=None):
        """
        %download URL [-f FILENAME] - download file from URL

        This line magic will download and save a file. By
        default it will use the same filename as the URL.
        You can give it another name using -f.

        Examples:
            %%download http://some/file/from/internet.txt -f myfile.txt
            %%download http://some/file/from/program.ss

        """
        if filename is None:
            parts = urlparse.urlsplit(url)
            #('http', 'example.com', '/somefile.zip', '', '')
            path = parts[2]
            filename = os.path.basename(path)
            if filename != '':
                basename, extname = os.path.splitext(filename)
                if extname == '':
                    filename += ".html"
                filename = filename.replace("~", "")
                filename = filename.replace("%20", "_")
            else:
                filename = "output.html"
        try:
            download(url, filename)
            self.kernel.Print("Downloaded '%s'." % filename)
        except Exception as e:
            self.kernel.Error(str(e))


def register_magics(kernel):
    kernel.register_magics(DownloadMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = DownloadMagic(kernel)
    # Make magics callable:
    kernel.line_magics["download"] = magic

    @register_line_magic
    def download(line):
        kernel.call_magic("%download " + line)
