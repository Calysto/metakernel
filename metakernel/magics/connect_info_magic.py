# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic
import json

class ConnectInfoMagic(Magic):

    def line_connect_info(self, dummy=None):
        """
        %connect_info - show connection information

        This line magic will show the connection information for this
        language kernel instance. This information is only necessary
        if you are interested in making additional connections to the
        running kernel.

        Example:
            %connect_info

        Paste the given JSON into a file, and connect with:

            $> ipython <app> --existing <file>

        or, if you are local, you can connect with just:

            $> ipython <app> --existing %(key)s

        or even just:
            $> ipython <app> --existing

        if this is the most recent Jupyter session you have started.
        """
        connection_file = self.kernel.config["IPKernelApp"]["connection_file"]
        try:
            config = json.loads(open(connection_file).read())
        except:
            config = {"stdin_port": "UNKNOWN",
                      "shell_port": "UNKNOWN",
                      "iopub_port": "UNKNOWN",
                      "hb_port": "UNKNOWN",
                      "ip": "UNKNOWN",
                      "key": "UNKNOWN",
                      "signature_scheme": "UNKNOWN",
                      "transport": "UNKNOWN"
            }
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
if this is the most recent Jupyter session you have started.
""" % config
        self.kernel.Print(retval)

def register_magics(kernel):
    kernel.register_magics(ConnectInfoMagic)
