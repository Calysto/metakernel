# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
from IPython.display import HTML, Javascript
import string
import random
import os

try:
    import urllib.request
    urlopen = urllib.request.urlopen
except: # python2
    import urllib
    urlopen = urllib.urlopen

def download(url):
    g = urlopen(url)
    return g.read().decode("utf-8")

class JigsawMagic(Magic):

    @option(
        '-w', '--workspace', action='store', default=None,
        help='use the provided name as workspace filename'
    )
    def line_jigsaw(self, language, workspace=None):
        """
        %jigsaw LANGUAGE - show visual code editor/generator

        This line magic will allow visual code editing or generation.

        Examples:
            %jigsaw Processing
            %jigsaw Python
            %jigsaw Processing --workspace workspace1
        """
        # Copy iframe html to here (must come from same domain):
        # Make up a random workspace name:
        if workspace is None:
            workspace = "jigsaw-workspace-" + (''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(6)))
        workspace_filename = workspace + ".xml"
        html_text = download("https://calysto.github.io/jigsaw/" + language + ".html")
        html_filename = workspace + ".html"
        html_text = html_text.replace("MYWORKSPACENAME", workspace_filename)
        with open(html_filename, "w") as fp:
            fp.write(html_text)
        # Display iframe:
        script = """
    if (document.jigsaw_register_workspace === undefined) {

        document.jigsaw_workspaces = {};

        document.jigsaw_register_workspace = function(workspace_filename, workspace, xml_init) {
            workspace.element = document.element;
            document.jigsaw_workspaces[workspace_filename] = workspace;

            try {
                $([window.parent.IPython.events]).on('notebook_saved.Notebook', function() { 
                    try {
                        document.jigsaw_save_workspace(workspace_filename); 
                    } catch(err) {
                        // ignore failure, might not exist
                    }
                });
            } catch (err) {
                // rendering for display
            }
            
            var xml = document.jigsaw_loadXMLDoc(workspace_filename);
            if (xml === null) {
                xml = xml_init;
                if (xml === null) {
                    xml = Blockly.Xml.textToDom('<xml id="workspace"></xml>');
                }
            } else {
                xml = xml.children[0]; // document
            }
            Blockly.Xml.domToWorkspace(workspace, xml);
        };

        document.jigsaw_handle_output = function(workspace_filename, out) {
            var workspace = document.jigsaw_workspaces[workspace_filename];
            //var output_area = workspace.element.output_area;
            var cell_index = document.jigsaw_get_cell(workspace.element);
            var cell = IPython.notebook.get_cell(cell_index);
            var res = null;
            var data = null;
            document.cell = cell;
            document.out = out;
            if (out.msg_type == "stream") {
                res = out.content.text;
                //document.getElementById('code_output').value += res.toString();
            } else if (out.msg_type === "pyout") {
                // if output is a python object
                res = out.content.data["text/plain"];
                //document.getElementById('code_output').value += res.toString(); 
            } else if (out.msg_type == "pyerr") {
                // if output is a python error
                res = out.content.data["text/plain"];
                //document.getElementById('code_output').value += res.toString();
            } else if (out.msg_type == "execute_result") {
                var str = out.content.data["text/plain"];
                res = str;
                if (res.indexOf("u") == 0)
                    res = res.substring(2, res.length - 1) + "\\n";
                if (res) {
                    //document.getElementById('code_output').value += res.toString();
                }
            } else if (out.msg_type == "error") {
                res = out.content.ename + ": " + out.content.evalue + "\\n";
                // FIXME: out.traceback is Array of terminal color-coded [-codes
            } else {
                // if output is something we haven't thought of
                res = out.toString();
                //document.getElementById('code_output').value += res.toString();
            }
            if (res) {
                cell.output_area.append_output({output_type: "stream", text: res.toString(), name: "output"});
            }
        };
        
        document.jigsaw_generate = function(workspace_filename, language, insert_code) {
            var workspace = document.jigsaw_workspaces[workspace_filename];
            var callbacks = { 'iopub' : {'output' : function(out) { document.jigsaw_handle_output(workspace_filename, out); }}};
            var code = Blockly[language].workspaceToCode(workspace);
            if (insert_code == 1) {
                var cell_index = document.jigsaw_get_cell(workspace.element);
                var cell = IPython.notebook.insert_cell_at_index(0, cell_index + 1);
                cell.set_text(code);
            } else {
                window.parent.IPython.notebook.kernel.execute(code,
                                                              callbacks,
                                                              {silent: false});
            }
        };
        
        document.jigsaw_save_workspace = function(workspace_filename) {
            var workspace = document.jigsaw_workspaces[workspace_filename];
            var xml = Blockly.Xml.workspaceToDom(workspace);
            document.xml = xml;
            if (xml !== undefined) {
                console.log(xml);
                //xml.style = "display: none";
                //xml.id = "workspace";
                var xml_text = Blockly.Xml.domToText(xml)
                IPython.notebook.kernel.execute('%%file ' + workspace_filename + '\\n' + xml_text);
            }
        };
        
        document.jigsaw_loadXMLDoc = function(filename) {
            var xhttp = new XMLHttpRequest();
            xhttp.open("GET", filename, false);
            xhttp.send();
            return xhttp.responseXML;
        };
    }

    document.jigsaw_get_cell = function (element) {
        // FIXME: brittle and ugly:
        var mydiv = element[0].parentNode.parentNode.parentNode.parentNode;
        var cells = IPython.notebook.get_cells();
        for (var i = 0; i < cells.length; i++) {
            if (mydiv === cells[i].element[0]) {
                return i;
            }
        }
        return null;
    };

    document.jigsaw_clear_output = function (workspace_filename) {
        var workspace = document.jigsaw_workspaces[workspace_filename];
        var cell_index = document.jigsaw_get_cell(workspace.element);
        var cell = IPython.notebook.get_cell(cell_index);
        // FIXME: brittle and ugly:
        cell.element[0].children[2].children[1].children[2].children[1].children[0].innerHTML = ""
        cell.output_area.outputs[2].text = ""
    };

    try {
        document.element = element;
    } catch (err) {
        // rendering
    }
"""
        script = script.replace("MYWORKSPACENAME", workspace_filename);
        iframe = """<iframe src="%s" width="100%%" height="350" style="resize: both; overflow: auto;"></iframe>""" % html_filename
        self.kernel.Display(Javascript(script))
        self.kernel.Display(HTML(iframe))

def register_magics(kernel):
    kernel.register_magics(JigsawMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = JigsawMagic(kernel)
    # Make magics callable:
    kernel.line_magics["jigsaw"] = magic

    @register_line_magic
    def jigsaw(line):
        """
        Use the Jigsaw code visualizer and generator.
        """
        kernel.call_magic("%jigsaw " + line)
