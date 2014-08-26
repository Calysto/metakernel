# Copyright (c) Calico Development Team.
# Distributed under the terms of the Modified BSD License.
# http://calicoproject.org/

from jupyter_kernel import Magic
import json

class ConnectInfoMagic(Magic):

    def line_connect_info(self, args):
        """%connect_info - show connection information"""
        connection_file = self.kernel.config["IPKernelApp"]["connection_file"]
        config = json.loads(open(connection_file).read())
        retval = """{
  "stdin_port": %(stdin_port)s,
  "shell_port": %(shell_port)s,
  "iopub_port": %(iopub_port)s,
  "hb_port": %(hb_port)s,
  "ip": "%(ip)s",
  "key": "%(key)s",
  "signature_scheme": "%(signature_scheme)s",
  "transport": "%(transport)s"
}

Paste the above JSON into a file, and connect with:
    $> ipython <app> --existing <file>
or, if you are local, you can connect with just:
    $> ipython <app> --existing %(key)s

or even just:
    $> ipython <app> --existing
if this is the most recent ICalico session you have started.
""" % config
        self.kernel.Print(retval)

def register_magics(kernel):
    kernel.register_magics(ConnectInfoMagic)
