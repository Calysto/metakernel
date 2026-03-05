"""
Magics to have disqus conversation in the notebook.
"""

from __future__ import annotations

from IPython.display import HTML

from metakernel import Magic, MetaKernel


class ConversationMagic(Magic):
    def cell_conversation(self, id: str) -> None:
        """
        %conversation ID - insert conversation by ID
        %%conversation ID - insert conversation by ID
        """
        html = f"""
<div id="disqus_thread"></div>
<script>
(function() {{ // DON'T EDIT BELOW THIS LINE
    var d = document, s = d.createElement('script');
    s.src = '//{id}.disqus.com/embed.js';
    s.setAttribute('data-timestamp', +new Date());
    (d.head || d.body).appendChild(s);
}})();
</script>
<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
"""
        self.kernel.Display(HTML(html))  # type: ignore[no-untyped-call]

    def line_conversation(self, id: str) -> None:
        """
        %conversation ID - insert conversation by ID
        %%conversation ID - insert conversation by ID
        """
        self.cell_conversation(id)
        self.evaluate = False


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(ConversationMagic)


def register_ipython_magics() -> None:
    from metakernel import IPythonKernel
    from metakernel.magic import register_cell_magic, register_line_magic

    kernel = IPythonKernel()
    magic = ConversationMagic(kernel)

    @register_line_magic
    def conversation(id: str) -> None:
        magic.line_conversation(id)

    @register_cell_magic  # type: ignore[no-redef]
    def conversation(id: str, cell: str) -> None:  # noqa: F811
        magic.code = cell
        magic.cell_conversation(id)
