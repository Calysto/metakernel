# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import json
from typing import Any

from metakernel import Magic


class RestartMagic(Magic):
    def line_restart(self) -> None:
        """
        %restart - restart session

        This line magic will restart the connection to the language
        kernel.

        Example:
            %restart

        Note that you will lose all computed values.
        """
        kernel = self.kernel
        if kernel.hist_file:
            with open(kernel.hist_file, "w") as fid:
                json.dump(kernel.hist_cache[-kernel.max_hist_cache :], fid)
        kernel.Print("Restarting kernel...")
        kernel.restart_kernel()
        kernel.reload_magics()
        kernel.Print("Done!")


def register_magics(kernel: Any) -> None:
    kernel.register_magics(RestartMagic)
