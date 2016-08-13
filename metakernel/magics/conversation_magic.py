"""
Magics to have disqus conversation in the notebook.
"""

from metakernel import Magic
from IPython.display import HTML

class ConversationMagic(Magic):

    def cell_conversation(self, id):
        """
        %conversation ID - insert conversation by ID
        %%conversation ID - insert conversation by ID
        """
        html = """
<div id="disqus_thread"></div>
<script>
(function() { // DON'T EDIT BELOW THIS LINE
    var d = document, s = d.createElement('script');
    s.src = '//%s.disqus.com/embed.js';
    s.setAttribute('data-timestamp', +new Date());
    (d.head || d.body).appendChild(s);
})();
</script>
<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
""" % id
        self.kernel.Display(HTML(html))

    def line_conversation(self, id):
        """
        %conversation ID - insert conversation by ID
        %%conversation ID - insert conversation by ID
        """
        self.cell_conversation(id)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(ConversationMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic, register_cell_magic
    kernel = IPythonKernel()
    magic = ConversationMagic(kernel)

    @register_line_magic
    def conversation(id):
        magic.line_conversation(id)

    @register_cell_magic
    def conversation(id, cell):
        magic.code = cell
        magic.cell_conversation(id)
