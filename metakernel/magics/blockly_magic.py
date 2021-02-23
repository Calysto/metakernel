# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.

from metakernel import Magic, option
from IPython.display import IFrame, Javascript
import string
import random
import os


class BlocklyMagic(Magic):

    @option(
        '-o', '--html_from_origin', action='store', default=None,
        help='use the provided name as filename of html origin'
    )
    @option(
        '-l', '--html_from_local', action='store', default=None,
        help='use the provided name as filename of html page'
    )
    @option(
        '-t', '--template_data', action='store', default=None,
        help='generate page based on template, must be used with parameters(-ho or -hl)'
             'use the provided name as workspace filename\n example : -ht xxx \n local include file: \n\txxx-toolbox.xml \n\txxx-workspace.xml \n\txxx-blocks.js'
    )
    @option(
        '-h', '--height', action='store', default=350,
        help='set height of iframe '
    )
    def line_blockly(self, html_from_origin=None, html_from_local=None, template_data=None, height=350):
        """
        %blockly - show visual code

        This line magic will allow visual code editing

        Examples:
            %blockly --html_from_origin http://host:port/blockly_page.html
            %blockly --html_from_local blockly_page.html
            %blockly --html_from_origin http://host:port/blockly_template.html --template_data template_data
        """
        # Display iframe:
        script = """
        if(document.receiveBlocklyPythonCode === undefined) {
            document.receiveBlocklyPythonCode = function ( event ) {
                //console.log( 'receiveMessage[Index]', event );
                IPython.notebook.insert_cell_at_index(0, 2).set_text(event.data);
            }
            window.addEventListener("message", document.receiveBlocklyPythonCode, false)
        }
        """
        #print(script)
        self.kernel.Display(Javascript(script))
        if height is None:
            height = 350
        if template_data is not None:
            if html_from_origin is not None:
                try:
                    import urllib.request
                    urlopen = urllib.request.urlopen
                except:  # python2
                    import urllib
                    urlopen = urllib.urlopen
                html_template = urlopen(html_from_origin).read().decode("utf-8")
            elif html_from_local is not None:
                with open(html_from_local, "rb") as fp:
                    html_template = fp.read().decode("utf-8")
            else:
                raise
            with open(template_data+'-toolbox.xml', "rb") as fp:
                blockly_toolbar = fp.read().decode("utf-8")
            with open(template_data + '-workspace.xml', "rb") as fp:
                blockly_workspace = fp.read().decode("utf-8")
            with open(template_data + '-blocks.js', "rb") as fp:
                blockly_blocks = fp.read().decode("utf-8")
            html_template = html_template.replace("MY_BLOCKLY_TOOLBAR", blockly_toolbar)
            html_template = html_template.replace("MY_BLOCKLY_WORKSPACE", blockly_workspace)
            html_template = html_template.replace("MY_BLOCKLY_BLOCKS", blockly_blocks)
            with open(template_data + '.html', 'w') as fp:
                fp.write(html_template)
            html_from_local = template_data + '.html'
        if html_from_local is not None:
            self.kernel.Display(IFrame(html_from_local, width='100%', height=height))
        elif html_from_origin is not None:
            self.kernel.Display(IFrame(html_from_origin, width='100%', height=height))
        else:
            raise


def register_magics(kernel):
    kernel.register_magics(Magic)


def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = BlocklyMagic(kernel)
    # Make magics callable:
    kernel.line_magics["blockly"] = magic

    @register_line_magic
    def blockly(line):
        """
        Use the blockly code visualizer and generator.
        """
        kernel.call_magic("%blockly " + line)
