# Copyright (c) Metakernel Development Team.
# Distributed under the terms of the Modified BSD License.
# @author ChrisJaunes

from metakernel import Magic, option
from IPython.display import IFrame, Javascript


class BlocklyMagic(Magic):

    @option(
        '-o', '--page_from_origin', action='store', default=None,
        help='Load remote page about blockly'
    )
    @option(
        '-l', '--page_from_local', action='store', default=None,
        help='Load local page about blockly'
    )
    @option(
        '-t', '--template_data', action='store', default=None,
        help='generate page based on template and load, must be used with parameters(-o or -l)'
     )
    @option(
        '-h', '--height', action='store', default=350,
        help='set height of iframe '
    )
    def line_blockly(self, page_from_origin=None, page_from_local=None, template_data=None, height=350):
        """
        %blockly - show visual code

        This line magic will allow visual code editing
        If both -o and -l are provided, only -l is used
        
        Examples:
            %blockly --page_from_origin http://host[:port]/blockly_page.html
            %blockly --page_from_local blockly_page.html
            %blockly --page_from_origin http://host[:port]/blockly_template.html --template_data template_data
            %blockly --height 600
        """
        # Display iframe:
        script = """
        if(document.receiveBlocklyPythonCode === undefined) {
            document.receiveBlocklyPythonCode = function ( event ) {
                IPython.notebook.insert_cell_above().set_text(event.data);
            }
            window.addEventListener("message", document.receiveBlocklyPythonCode, false)
        }
        """
        #print(script)
        self.kernel.Display(Javascript(script))

        if height is None:
            height = 350
        if template_data is not None:
            if page_from_local is not None:
                with open(html_from_local, "rb") as fp:
                    html_template = fp.read().decode("utf-8")
            elif page_from_origin is not None:
                try:
                    import urllib.request
                    urlopen = urllib.request.urlopen
                except:  # python2
                    import urllib
                    urlopen = urllib.urlopen
                page_template = urlopen(page_from_origin).read().decode("utf-8")
            else:
                raise ValueError("No -l or -o is provided")
            with open(template_data+'-toolbox.xml', "rb") as fp:
                blockly_toolbox = fp.read().decode("utf-8")
            html_template = html_template.replace("MY_BLOCKLY_TOOLBOX", blockly_toolbox)
            with open(template_data + '-workspace.xml', "rb") as fp:
                blockly_workspace = fp.read().decode("utf-8")
            html_template = html_template.replace("MY_BLOCKLY_WORKSPACE", blockly_workspace)
            with open(template_data + '-blocks.js', "rb") as fp:
                blockly_blocks = fp.read().decode("utf-8")
            html_template = html_template.replace("MY_BLOCKLY_BLOCKS_JS", blockly_blocks)
            with open(template_data + '.html', 'w') as fp:
                fp.write(html_template)
            page_from_local = template_data + '.html'
        if page_from_local is not None:
            self.kernel.Display(IFrame(page_from_local, width='100%', height=height))
        elif page_from_origin is not None:
            self.kernel.Display(IFrame(page_from_origin, width='100%', height=height))
        else:
            self.kernel.Display(IFrame("https://developers-dot-devsite-v2-prod.appspot.com/blockly/blockly-demo/blockly-demo", width='100%', height=height))


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
