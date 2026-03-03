# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

import inspect
import os
import urllib.parse as urlparse
import urllib.request

from metakernel import Magic


def download(url, filename):
    g = urllib.request.urlopen(url)
    with open(filename, "wb") as f:
        f.write(g.read())


class InstallMagicMagic(Magic):
    async def line_install_magic(self, url) -> None:
        """
        %install_magic URL - download and install magic from URL

        This line magic will copy the file at the URL into your
        personal magic folder.

        Example:
            %install_magic http://path/to/some/magic.py

        """
        parts = urlparse.urlsplit(url)
        # ('http', 'example.com', '/somefile.zip', '', '')
        path = parts[2]
        filename = os.path.basename(path)
        local_magics_dir = self.kernel.get_local_magics_dir()
        if inspect.isawaitable(local_magics_dir):
            local_magics_dir = await local_magics_dir
        magic_filename = os.path.join(local_magics_dir, filename)
        try:
            download(url, magic_filename)
            self.kernel.Print(f"Downloaded '{magic_filename}'.")
            self.code = "%reload_magics\n" + self.code
        except Exception as e:
            self.kernel.Error(str(e))


def register_magics(kernel) -> None:
    kernel.register_magics(InstallMagicMagic)
