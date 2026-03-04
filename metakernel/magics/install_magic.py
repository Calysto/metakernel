# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import os
from typing import Any

from metakernel import Magic


class InstallMagic(Magic):
    def line_install(self, package: str) -> None:
        """
        %install PACKAGE - install package

        Example:
            %install calico-spell-check
        """
        ## FIXME: get list of known extension names and locations from wiki
        shell = self.kernel.line_magics.get("shell")
        if package == "calico-publish" and shell is not None:
            shell.line_shell(
                "ipython install-nbextension https://bitbucket.org/ipre/calico/raw/master/notebooks/nbextensions/calico-publish.js"
            )
        elif package == "calico-spell-check" and shell is not None:
            shell.line_shell(
                "ipython install-nbextension https://bitbucket.org/ipre/calico/downloads/calico-spell-check-1.0.zip"
            )
        elif package == "calico-cell-tools" and shell is not None:
            shell.line_shell(
                "ipython install-nbextension https://bitbucket.org/ipre/calico/downloads/calico-cell-tools-1.0.zip"
            )
        elif package == "calico-document-tools" and shell is not None:
            shell.line_shell(
                "ipython install-nbextension https://bitbucket.org/ipre/calico/downloads/calico-document-tools-1.0.zip"
            )
        self.enable_extension(package)
        # FIXME: related %config:
        ## // To turn off automatically creating closing parenthesis and bracket:
        ## IPython.CodeCell.options_default.cm_config["autoCloseBrackets"] = "";

    def enable_extension(self, name: str) -> None:
        filename = "~/.ipython/profile_default/static/custom/custom.js"
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        text = open(filename).read()
        if (f'IPython.load_extensions("{name}");') in text:
            return
        if "// INSTALL MAGIC" not in text:
            text += """
require(["base/js/events"], function (events) {
    events.on("app_initialized.NotebookApp", function () {
        // INSTALL MAGIC
        // To turn off automatically creating closing parenthesis and bracket:
        IPython.CodeCell.options_default.cm_config["autoCloseBrackets"] = "";
    });
});
"""
        text = text.replace(
            "        // INSTALL MAGIC",
            f'        IPython.load_extensions("{name}");\n        // INSTALL MAGIC',
        )
        with open(filename, "w") as fp:
            fp.write(text)


def register_magics(kernel: Any) -> None:
    kernel.register_magics(InstallMagic)
