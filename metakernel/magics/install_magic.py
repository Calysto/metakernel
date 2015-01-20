# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
import os

class InstallMagic(Magic):

    def line_install(self, package):
        """
        %install PACKAGE - install package

        Example:
            %install calico-spell-check
        """
        ## FIXME: get list of known extension names and locations from wiki
        if package == "calico-publish":
            self.kernel.do_execute("!ipython install-nbextension https://bitbucket.org/ipre/calico/raw/master/notebooks/nbextensions/calico-publish.js")
        elif package == "calico-spell-check":
            self.kernel.do_execute("!ipython install-nbextension https://bitbucket.org/ipre/calico/downloads/calico-spell-check-1.0.zip")
        elif package == "calico-cell-tools":
            self.kernel.do_execute("!ipython install-nbextension https://bitbucket.org/ipre/calico/downloads/calico-cell-tools-1.0.zip")
        elif package == "calico-document-tools":
            self.kernel.do_execute("!ipython install-nbextension https://bitbucket.org/ipre/calico/downloads/calico-document-tools-1.0.zip")
        self.enable_extension(package)
        # FIXME: related %config:
        ## // To turn off automatically creating closing parenthesis and bracket:
        ## IPython.CodeCell.options_default.cm_config["autoCloseBrackets"] = "";

    def enable_extension(self, name):
        filename = "~/.ipython/profile_default/static/custom/custom.js"
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        text = open(filename).read()
        if ('IPython.load_extensions("%s");' % name) in text:
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
        text = text.replace("        // INSTALL MAGIC", '        IPython.load_extensions("%s");\n        // INSTALL MAGIC' % name)
        with open(filename, "w") as fp:
            fp.write(text)

def register_magics(kernel):
    kernel.register_magics(InstallMagic)
