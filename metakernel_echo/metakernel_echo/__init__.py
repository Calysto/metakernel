"""A Echo kernel for Jupyter"""

from typing import Any

from metakernel import MetaKernel

__version__ = "0.19.1"


class MetaKernelEcho(MetaKernel):
    implementation = "MetaKernel Echo"
    implementation_version = "1.0"
    language = "text"
    language_version = "0.1"
    banner = "MetaKernel Echo - as useful as a parrot"
    language_info = {
        "mimetype": "text/plain",
        "name": "text",
        # ------ If different from 'language':
        # 'codemirror_mode': {
        #    "version": 2,
        #    "name": "ipython"
        # }
        # 'pygments_lexer': 'language',
        # 'version'       : "x.y.z",
        "file_extension": ".txt",
        "help_links": MetaKernel.help_links,
    }

    def get_usage(self) -> str:
        return "This is the echo kernel."

    def do_execute_direct(self, code: str, *args: Any, **kwargs: Any) -> str:
        return code.rstrip()

    def repr(self, data: Any) -> str:
        return repr(data)
