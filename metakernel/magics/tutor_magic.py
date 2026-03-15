"""
==========
tutormagic
==========

Magics to display pythontutor.com in the notebook.
"""

from __future__ import annotations

# Based on Kiko Correoso's IPython magic:
# https://github.com/kikocorreoso/tutormagic
# and Doug Blank's
# http://jupyter.cs.brynmawr.edu/hub/dblank/public/Examples/Online%20Python%20Tutor.ipynb
# -----------------------------------------------------------------------------
# Copyright (C) 2015 Kiko Correoso and the pythontutor.com developers
#
# Distributed under the terms of the MIT License. The full license is in
# the file LICENSE, distributed as part of this software.
#
# Contributors:
#   kikocorreoso
# -----------------------------------------------------------------------------
from urllib.parse import quote

from IPython.display import HTML

from metakernel import Magic, MetaKernel, option


class TutorMagic(Magic):
    @option(
        "-l",
        "--language",
        action="store",
        nargs=1,
        help=(
            "Possible languages to be displayed within the iframe. "
            + "Possible values are: python, python2, python3, java, javascript"
        ),
    )
    def cell_tutor(self, language: str | None = None) -> None:
        """
        %%tutor [--language=LANGUAGE] - show cell with
        Online Python Tutor.

        Defaults to use the language of the current kernel.
        'python' is an alias for 'python3'.

        Examples:
           %%tutor -l python3
           a = 1
           b = 1
           a + b

           [You will see an iframe with the pythontutor.com page
           including the code above.]

           %%tutor --language=java

           public class Test {
               public Test() {
               }
               public static void main(String[] args) {
                   int x = 1;
                   System.out.println("Hi");
               }
           }
        """
        if language is None:
            language = self.kernel.language_info["name"]
        if language not in ["python", "python2", "python3", "java", "javascript"]:
            raise ValueError(
                f"{language} not supported. Only the following options are allowed: "
                "'python2', 'python3', 'java', 'javascript'"
            )

        url = "https://pythontutor.com/iframe-embed.html#code="
        url += quote(self.code)
        url += "&origin=opt-frontend.js&cumulative=false&heapPrimitives=false"
        url += "&textReferences=false&"
        if language in ["python3", "python"]:
            url += "py=3&rawInputLstJSON=%5B%5D&curInstr=0&codeDivWidth=350&codeDivHeight=400"
        elif language == "python2":
            url += "py=2&rawInputLstJSON=%5B%5D&curInstr=0&codeDivWidth=350&codeDivHeight=400"
        elif language == "java":
            url += "py=java&rawInputLstJSON=%5B%5D&curInstr=0&codeDivWidth=350&codeDivHeight=400"
        elif language == "javascript":
            url += "py=js&rawInputLstJSON=%5B%5D&curInstr=0&codeDivWidth=350&codeDivHeight=400"

        # Display a button that loads the iframe on click (avoids simultaneous
        # requests from multiple %%tutor cells in a static notebook).
        escaped_url = url.replace('"', "&quot;")
        html = (
            f"<div>"
            f'<button onclick="'
            f"this.parentNode.innerHTML='<iframe src=&quot;{escaped_url}&quot; "
            f"width=&quot;100%&quot; height=&quot;500&quot; "
            f"frameborder=&quot;0&quot;></iframe>'"
            f'">Run in Online Python Tutor</button>'
            f"</div>"
        )
        self.kernel.Display(HTML(html))  # type: ignore[no-untyped-call]
        self.evaluate = False


def register_magics(kernel: MetaKernel) -> None:
    kernel.register_magics(TutorMagic)


def register_ipython_magics() -> None:
    from metakernel import IPythonKernel
    from metakernel.magic import register_cell_magic

    kernel = IPythonKernel()
    magic = TutorMagic(kernel)

    @register_cell_magic
    def tutor(line: str, cell: str) -> None:
        magic.code = cell
        magic.cell_tutor(language="python3")
