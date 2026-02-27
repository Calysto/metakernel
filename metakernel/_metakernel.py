from __future__ import annotations

import glob
import importlib
import inspect
import json
import logging
import os
import pkgutil
import subprocess
import sys
import warnings
from collections import OrderedDict
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Any

import comm
from ipykernel.kernelapp import IPKernelApp
from ipykernel.kernelbase import Kernel
from IPython.core.formatters import DisplayFormatter
from IPython.display import publish_display_data
from IPython.paths import get_ipython_dir
from IPython.utils.tempdir import TemporaryDirectory  # type:ignore[attr-defined]
from jupyter_core.paths import jupyter_config_dir, jupyter_config_path
from traitlets import Dict, Unicode
from traitlets.config import Application

from .config import get_history_file, get_local_magics_dir
from .parser import Parser

if TYPE_CHECKING:
    from .magic import Magic

warnings.filterwarnings("ignore", module="IPython.html.widgets")

PY3 = sys.version_info[0] == 3

try:
    import ipywidgets as widgets  #  type:ignore[import-untyped]
    from ipywidgets.widgets.widget import Widget  #  type:ignore[import-untyped]
except ImportError:
    Widget = None

# Inlined from IPython TermColors after its removal.
RED = "\033[0;31m"
NORMAL = "\033[0m"


class ExceptionWrapper:
    """
    Utility wrapper that we can use to get the kernel to respond properly for errors.

    When the return value of your execute is an instance of this, an error will be thrown similar to Ipykernel
    """

    def __init__(self, ename: str, evalue: Any, traceback: Any) -> None:
        self.ename = ename
        self.evalue = evalue
        self.traceback = traceback

    def __repr__(self) -> str:
        return f"{self.ename}: {self.evalue}\n{self.traceback}"


def lazy_import_handle_comm_opened(*args: Any, **kwargs: Any) -> None:
    if Widget is None:
        return
    Widget.handle_comm_opened(*args, **kwargs)


def get_metakernel() -> MetaKernel | None:
    """
    Get the MetaKernel instance.
    """
    return MetaKernel.meta_kernel


class MetaKernel(Kernel):
    """The base MetaKernel class."""

    app_name = "metakernel"
    identifier_regex = r"[^\d\W][\w\.]*"
    func_call_regex = r"([^\d\W][\w\.]*)\([^\)\()]*\Z"
    magic_prefixes = dict(magic="%", shell="!", help="?")
    help_suffix = "?"
    help_links = [
        {
            "text": "MetaKernel Magics",
            "url": "https://metakernel.readthedocs.io/en/latest/source/README.html",
        },
    ]
    language_info: dict[str, Any] = {
        # 'mimetype': 'text/x-python',
        # 'name': 'python',
        # ------ If different from 'language':
        # 'codemirror_mode': {
        #    "version": 2,
        #    "name": "ipython"
        # }
        # 'pygments_lexer': 'language',
        # 'version'       : "x.y.z",
        # 'file_extension': '.py',
        "help_links": help_links,
    }
    plot_settings = Dict(dict(backend="inline")).tag(config=True)

    meta_kernel = None

    @classmethod
    def run_as_main(cls, *args: Any, **kwargs: Any) -> None:
        """Launch or install a metakernel.

        Modules implementing a metakernel subclass can use the following lines:

            if __name__ == '__main__':
                MetaKernelSubclass.run_as_main()
        """
        kwargs["app_name"] = cls.app_name
        MetaKernelApp.launch_instance(kernel_class=cls, *args, **kwargs)  # noqa: B026

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type:ignore[no-untyped-call]
        if MetaKernel.meta_kernel is None:
            MetaKernel.meta_kernel = self
        if self.log is None:
            # This occurs if we call as a stand-alone kernel
            # (eg, not as a process)
            # FIXME: take care of input/output, eg StringIO
            #        make work without a session
            self.log = logging.Logger(".metakernel")  # type:ignore[unreachable]
        else:
            # Write has already been set
            try:
                sys.stdout.write = self.Write  # type: ignore[method-assign]
            except Exception:
                pass  # Can't change stdout
        self.redirect_to_log = False
        self.shell = None
        self.sticky_magics: OrderedDict[str, str] = OrderedDict()
        self._i: str | None = None
        self._ii: str | None = None
        self._iii: str | None = None
        self._: str | None = None
        self.__: str | None = None
        self.___: str | None = None
        self.max_hist_cache = 1000
        self.hist_cache: list[str] = []
        kwargs = {"parent": self, "kernel": self}
        if not PY3:
            kwargs["shell"] = None
        self.comm_manager = comm.get_comm_manager()
        # widgets have changed target name in 8.x, keeping for compatibility
        self.comm_manager.register_target(
            "ipython.widget", lazy_import_handle_comm_opened
        )

        # compatible with widgets 8.x
        if Widget is not None:
            widgets.register_comm_target()

        self.hist_file = get_history_file(self)
        self.parser = Parser(
            self.identifier_regex,
            self.func_call_regex,
            self.magic_prefixes,
            self.help_suffix,
        )
        comm_msg_types = ["comm_open", "comm_msg", "comm_close"]
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(self.comm_manager, msg_type)
        self._display_formatter = DisplayFormatter()  # pass kwargs?
        self.env: dict[str, Any] = {}
        self.reload_magics()
        # provide a way to get the current instance
        self.set_variable("kernel", self)
        # Run command line filenames, if given:
        if self.parent is not None and self.parent.extra_args:
            level = self.log.level
            self.log.setLevel("INFO")
            self.redirect_to_log = True
            self.Write("Executing files...")
            for filename in self.parent.extra_args:
                self.Write("    %s..." % filename)
                try:
                    self.do_execute_file(filename)
                except Exception as exc:
                    self.log.info("    %s" % (exc,))
            self.Write("Executing files: done!")
            self.log.setLevel(level)
            self.redirect_to_log = False

    def makeSubkernel(self, kernel: MetaKernel) -> None:
        """
        Run this method in an IPython kernel to set
        this kernel's input/output settings.
        """
        from IPython import get_ipython  # type:ignore[attr-defined]
        from IPython.display import display

        shell = get_ipython()  # type:ignore[no-untyped-call]
        if shell:  # we are running under an IPython kernel
            self.session = shell.kernel.session
            self.Display = display  # type: ignore[method-assign]
            self.send_response = self._send_shell_response  # type: ignore[method-assign]
        else:
            self.session = kernel.session
            self.send_response = kernel.send_response  # type: ignore[method-assign]
            self.Display = kernel.Display  # type: ignore[method-assign]

    #####################################
    # Methods which provide kernel - specific behavior

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set a variable to a Python-typed value.
        """
        pass

    def get_variable(self, name: str) -> Any:
        """
        Lookup a variable name and return a Python-typed value.
        """
        pass

    def repr(self, item: Any) -> str:
        """The repr of the kernel."""
        return repr(item)

    def get_usage(self) -> str:
        """Get the usage statement for the kernel."""
        return "This is a usage statement."

    def get_kernel_help_on(
        self, info: dict[str, Any], level: int = 0, none_on_fail: bool = False
    ) -> str | None:
        """Get help on an object.  Called by the help magic."""
        if none_on_fail:
            return None
        else:
            return "Sorry, no help is available on '%s'." % info["code"]

    def handle_plot_settings(self) -> None:
        """Handle the current plot settings"""
        pass

    def get_local_magics_dir(self) -> str:
        """
        Returns the path to local magics dir (eg ~/.ipython/metakernel/magics)
        """
        base = get_ipython_dir()
        return os.path.join(base, "metakernel", "magics")

    def get_completions(self, info: dict[str, Any]) -> list[str]:
        """
        Get completions from kernel based on info dict.
        """
        return []

    def do_execute_direct(self, code: str, silent: bool = False) -> Any:
        """
        Execute code in the kernel language.
        """
        pass

    def do_execute_file(self, filename: str) -> Any:
        """
        Default code for running a file. Just opens the file, and sends
        the text to do_execute_direct.
        """
        with open(filename) as f:
            return self.do_execute_direct("".join(f.readlines()))

    def do_execute_meta(self, code: str) -> Any:
        """
        Execute meta code in the kernel. This uses the execute infrastructure
        but allows JavaScript to talk directly to the kernel bypassing normal
        processing.

        When responding to the %%debug magic, the step and reset meta
        commands can answer with a string in the format:

        "highlight: [start_line, start_col, end_line, end_col]"

        for highlighting expressions in the frontend.
        """
        if code == "reset":
            raise Exception("This kernel does not implement this meta command")
        elif code == "stop":
            raise Exception("This kernel does not implement this meta command")
        elif code == "step":
            raise Exception("This kernel does not implement this meta command")
        elif code.startswith("inspect "):
            raise Exception("This kernel does not implement this meta command")
        else:
            raise Exception("Unknown meta command: '%s'" % code)

    def initialize_debug(self, code: str) -> str:
        """
        This function is used with the %%debug magic for highlighting
        lines of code, and for initializing debug functions.

        Return the empty string if highlighting is not supported.
        """
        # return "highlight: [%s, %s, %s, %s]" % (line1, col1, line2, col2)
        return ""

    def do_function_direct(self, function_name: str, arg: Any) -> Any:
        """
        Call a function in the kernel language with args (as a single item).
        """
        f = self.do_execute_direct(function_name)
        return f(arg)

    def restart_kernel(self) -> None:
        """Restart the kernel"""
        pass

    ############################################
    # Implement base class methods

    def do_execute(
        self,
        code: Any,
        silent: Any = False,
        store_history: Any = True,
        user_expressions: Any = None,
        allow_stdin: Any = False,
        *,
        cell_meta: Any = None,
        cell_id: Any = None,
    ) -> Any:
        """Handle code execution.

        https://jupyter-client.readthedocs.io/en/stable/messaging.html#execute
        """
        # Set the ability for the kernel to get standard-in:
        self._allow_stdin = allow_stdin
        # Create a default response:
        self.kernel_resp = {
            "status": "ok",
            # The base class increments the execution count
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }

        # TODO: remove this when IPython fixes this
        # This happens at startup when the language is set to python
        if "_usage.page_guiref" in code:
            return self.kernel_resp

        if code and store_history:
            self.hist_cache.append(code.strip())

        if not code.strip():
            return self.kernel_resp

        info = self.parse_code(code)
        self.payload = []
        retval = None

        if info["magic"] and info["magic"]["name"] == "help":
            if info["magic"]["type"] == "line":
                level = 0
            else:
                level = 1
            text = self.get_help_on(code, level)
            if text:
                content = {
                    "start_line_number": 0,
                    "source": "page",
                }
                if isinstance(text, dict):
                    content["data"] = text  ## {mime-type: ..., mime-type:...}
                    self.log.debug(str(text))
                else:
                    content["data"] = {"text/plain": text}
                    self.log.debug(text)
                self.payload = [content]

        elif info["magic"] or self.sticky_magics:
            retval = None
            if self.sticky_magics:
                magics, code = _split_magics_code(code, self.magic_prefixes)
                code = magics + self._get_sticky_magics() + code
            stack = []
            # Handle magics:
            magic = None
            prefixes = (self.magic_prefixes["shell"], self.magic_prefixes["magic"])
            while code.startswith(prefixes):
                magic = self.get_magic(code)
                if magic is not None:
                    stack.append(magic)
                    code = str(magic.get_code())
                    # signal to exit, maybe error or no block
                    if not magic.evaluate:
                        break
                else:
                    break  # type:ignore[unreachable]
            # Execute code, if any:
            if (magic is None or magic.evaluate) and code.strip() != "":
                if code.startswith("~~META~~:"):
                    retval = self.do_execute_meta(code[9:].strip())
                else:
                    retval = self.do_execute_direct(code)
            # Post-process magics:
            for magic in reversed(stack):
                retval = magic.post_process(retval)
        else:
            if code.startswith("~~META~~:"):
                retval = self.do_execute_meta(code[9:].strip())
            else:
                retval = self.do_execute_direct(code)

        self.post_execute(retval, code, silent)

        if "payload" in self.kernel_resp:
            self.kernel_resp["payload"] = self.payload

        return self.kernel_resp

    def post_execute(self, retval: Any, code: str, silent: bool) -> None:
        """Post-execution actions

        Handle special kernel variables and display response if not silent.
        """
        # Handle in's
        self.set_variable("_iii", self._iii)
        self.set_variable("_ii", self._ii)
        self.set_variable("_i", code)
        self.set_variable("_i" + str(self.execution_count), code)
        self._iii = self._ii
        self._ii = code
        if retval is not None:
            # --------------------------------------
            # Handle out's (only when non-null)
            self.set_variable("___", self.___)
            self.set_variable("__", self.__)
            self.set_variable("_", retval)
            self.set_variable("_" + str(self.execution_count), retval)
            self.___ = self.__
            self.__ = retval
            self.log.debug(retval)
            if isinstance(retval, ExceptionWrapper):
                self.kernel_resp["status"] = "error"
                content = {
                    "traceback": retval.traceback,
                    "evalue": retval.evalue,
                    "ename": retval.ename,
                }
                self.kernel_resp.update(content)
                if not silent:
                    self.send_response(self.iopub_socket, "error", content)
            else:
                try:
                    data = self._display_formatter.format(retval)  # type:ignore[no-untyped-call]
                except Exception as e:
                    self.Error(e)
                    return
                content = {
                    "execution_count": self.execution_count,
                    "data": data[0],
                    "metadata": data[1],
                }
                if not silent:
                    if Widget and isinstance(retval, Widget):
                        self.Display(retval)
                        return
                    self.send_response(self.iopub_socket, "execute_result", content)

    def do_history(
        self,
        hist_access_type: str | None,
        output: str | None,
        raw: bool | None,
        session: Any = None,
        start: int | None = None,
        stop: int | None = None,
        n: int | None = None,
        pattern: Any = None,
        unique: bool = False,
    ) -> dict[str, str | list[Any]]:
        """
        Access history at startup.

        https://jupyter-client.readthedocs.io/en/stable/messaging.html#history
        """
        with open(self.hist_file) as fid:
            self.hist_cache = json.loads(fid.read() or "[]")
        return {"status": "ok", "history": [(None, None, h) for h in self.hist_cache]}

    def do_shutdown(self, restart: bool) -> dict[str, Any]:
        """
        Shut down the app gracefully, saving history.

        https://jupyter-client.readthedocs.io/en/stable/messaging.html#kernel-shutdown
        """
        if self.hist_file:
            with open(self.hist_file, "w") as fid:
                json.dump(self.hist_cache[-self.max_hist_cache :], fid)
        if restart:
            self.Print("Restarting kernel...")
            self.restart_kernel()
            self.reload_magics()
            self.Print("Done!")
        return {"status": "ok", "restart": restart}

    def do_is_complete(self, code: str) -> dict[str, str]:
        """
        Given code as string, returns dictionary with 'status' representing
        whether code is ready to evaluate. Possible values for status are:

           'complete'   - ready to evaluate
           'incomplete' - not yet ready
           'invalid'    - invalid code
           'unknown'    - unknown; the default unless overridden

        Optionally, if 'status' is 'incomplete', you may indicate
        an indentation string.

        Example:

            return {'status' : 'incomplete',
                    'indent': ' ' * 4}

        https://jupyter-client.readthedocs.io/en/stable/messaging.html#code-completeness
        """
        if code.startswith(self.magic_prefixes["magic"]):
            ## force requirement to end with an empty line
            if code.endswith("\n"):
                return {"status": "complete"}
            else:
                return {"status": "incomplete"}
        # otherwise, how to know is complete?
        elif code.endswith("\n"):
            return {"status": "complete"}
        else:
            return {"status": "incomplete"}

    def do_complete(self, code: str, cursor_pos: int) -> dict[str, Any]:
        """Handle code completion for the kernel.

        https://jupyter-client.readthedocs.io/en/stable/messaging.html#completion
        """
        info = self.parse_code(code, 0, cursor_pos)
        content = {
            "matches": [],
            "cursor_start": info["start"],
            "cursor_end": info["end"],
            "status": "ok",
            "metadata": {},
        }

        matches = info["path_matches"]

        if info["magic"]:
            # if the last line contains another magic, use that
            line_info = self.parse_code(info["line"])
            if line_info["magic"]:
                info = line_info

            if info["magic"]["type"] == "line":
                magics = self.line_magics
            else:
                magics = self.cell_magics

            if info["magic"]["name"] in magics:
                magic = magics[info["magic"]["name"]]
                info = info["magic"]
                if info["type"] == "cell" and info["code"]:
                    info = self.parse_code(info["code"])
                else:
                    info = self.parse_code(info["args"])

                matches.extend(magic.get_completions(info))

            elif not info["magic"]["code"] and not info["magic"]["args"]:
                matches = []
                for name in magics.keys():
                    if name.startswith(info["magic"]["name"]):
                        pre = info["magic"]["prefix"]
                        matches.append(pre + name)
                        info["start"] -= len(pre)
                        info["full_obj"] = pre + info["full_obj"]
                        info["obj"] = pre + info["obj"]

        else:
            matches.extend(self.get_completions(info))

        if info["full_obj"] and len(info["full_obj"]) > len(info["obj"]):
            new_list = [m for m in matches if m.startswith(info["full_obj"])]
            if new_list:
                content["cursor_end"] = (
                    content["cursor_end"] + len(info["full_obj"]) - len(info["obj"])
                )
                matches = new_list

        content["matches"] = sorted(matches)

        return content

    def do_inspect(
        self, code: str, cursor_pos: int, detail_level: int = 0, omit_sections: Any = ()
    ) -> dict[str, Any] | None:
        """Object introspection.

        https://jupyter-client.readthedocs.io/en/stable/messaging.html#introspection
        """
        if cursor_pos > len(code):
            return None

        content = {"status": "aborted", "data": {}, "found": False, "metadata": {}}
        docstring = self.get_help_on(
            code, detail_level, none_on_fail=True, cursor_pos=cursor_pos
        )

        if docstring:
            content["status"] = "ok"
            content["found"] = True
            if isinstance(docstring, dict):  ## {"text/plain": ..., mime-type: ...}
                content["data"] = docstring
                self.log.debug(str(docstring))
            else:
                content["data"] = {"text/plain": docstring}
                self.log.debug(docstring)

        return content

    def clear_output(self, wait: bool = False) -> None:
        """Clear the output of the kernel."""
        self.send_response(self.iopub_socket, "clear_output", {"wait": wait})

    def Display(self, *objects: Any, **kwargs: Any) -> None:
        """Display one or more objects using rich display.

        Supports a `clear_output` keyword argument that clears the output before displaying.

        See https://ipython.readthedocs.io/en/stable/config/integrating.html?highlight=display#rich-display
        """
        if kwargs.get("clear_output"):
            self.clear_output(wait=True)

        for item in objects:
            if Widget and isinstance(item, Widget):
                self.log.debug("Display Widget")
                data = {
                    "text/plain": repr(item),
                    "application/vnd.jupyter.widget-view+json": {
                        "version_major": 2,
                        "version_minor": 0,
                        "model_id": item._model_id,
                    },
                }
                content = {"data": data, "metadata": {}}
                self.send_response(self.iopub_socket, "display_data", content)
            else:
                self.log.debug("Display Data")
                try:
                    data = self._display_formatter.format(item)  # type:ignore[no-untyped-call]
                except Exception as e:
                    self.Error(e)
                    return
                content = {"data": data[0], "metadata": data[1]}
                self.send_response(self.iopub_socket, "display_data", content)

    def Print(self, *objects: Any, **kwargs: Any) -> None:
        """Print `objects` to the iopub stream, separated by `sep` and followed by `end`.

        Items can be strings or `Widget` instances.
        """
        for item in objects:
            if Widget and isinstance(item, Widget):
                self.Display(item)

        non_widgets = [i for i in objects if not (Widget and isinstance(i, Widget))]
        message = format_message(*non_widgets, **kwargs)

        stream_content = {"name": "stdout", "text": message}
        self.log.debug("Print: %s" % message.rstrip())
        if self.redirect_to_log:
            self.log.info(message.rstrip())
        else:
            self.send_response(self.iopub_socket, "stream", stream_content)

    def Write(self, message: str) -> None:
        """Write message directly to the iopub stdout with no added end character."""
        stream_content = {"name": "stdout", "text": message}
        self.log.debug("Write: %s" % message)
        if self.redirect_to_log:
            self.log.info(message)
        else:
            self.send_response(self.iopub_socket, "stream", stream_content)

    def Error(self, *objects: Any, **kwargs: Any) -> None:
        """Print `objects` to stdout, separated by `sep` and followed by `end`.

        Objects are cast to strings.
        """
        message = format_message(*objects, **kwargs)
        self.log.debug("Error: %s" % message.rstrip())
        stream_content = {"name": "stderr", "text": RED + message + NORMAL}
        if self.redirect_to_log:
            self.log.info(message.rstrip())
        else:
            self.send_response(self.iopub_socket, "stream", stream_content)

    def Error_display(self, *objects: Any, **kwargs: Any) -> None:
        """Print `objects` to stdout is they area strings, separated by `sep` and followed by `end`.
        All other objects are rendered using the Display method
        Objects are cast to strings.
        """
        msg = []
        msg_dict = {}
        for item in objects:
            if not isinstance(item, str):
                self.log.debug(f"Item type:{type(item)}")
                self.Display(item)
            else:
                # msg is the error for str
                msg.append(item)

        for k, v in kwargs.items():
            if not isinstance(v, str):
                self.Display(k, v)
            else:
                msg_dict[k] = v

        message = format_message(" ".join(msg), **kwargs)
        if len(msg_dict.keys()) > 0:
            message = format_message(" ".join(msg), msg_dict)
        self.log.debug("Error: %s" % message.rstrip())
        stream_content = {"name": "stderr", "text": RED + message + NORMAL}
        if self.redirect_to_log:
            self.log.info(message.rstrip())
        else:
            self.send_response(self.iopub_socket, "stream", stream_content)

    ##############################
    # Private API and methods not likely to be overridden

    def reload_magics(self) -> None:
        """Reload all of the line and cell magics."""
        self.line_magics: dict[str, Any] = {}
        self.cell_magics: dict[str, Any] = {}

        # get base magic files and those relative to the current class
        # directory
        magic_files = []
        # Make a metakernel/magics if it doesn't exist:
        local_magics_dir = get_local_magics_dir()
        # Search all of the places there could be magics:
        try:
            paths = [
                os.path.join(
                    os.path.dirname(os.path.abspath(inspect.getfile(self.__class__))),
                    "magics",
                )
            ]
        except Exception:
            paths = []
        paths += [
            local_magics_dir,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "magics"),
        ]
        for magic_dir in paths:
            sys.path.append(magic_dir)
            magic_files.extend(glob.glob(os.path.join(magic_dir, "*.py")))

        for magic in magic_files:
            basename = os.path.basename(magic)
            if basename == "__init__.py":
                continue
            try:
                module = __import__(os.path.splitext(basename)[0])
                importlib.reload(module)
                module.register_magics(self)
            except Exception as e:
                self.log.error("Can't load '%s': error: %s" % (magic, e))

    def register_magics(self, magic_klass: type[Magic]) -> None:
        """Register magics for a given magic_klass."""
        magic = magic_klass(self)
        line_magics = magic.get_magics("line")
        cell_magics = magic.get_magics("cell")
        for name in line_magics:
            self.line_magics[name] = magic
        for name in cell_magics:
            self.cell_magics[name] = magic

    def send_response(self, *args: Any, **kwargs: Any) -> None:
        ### if we are running via %parallel, we might not have a
        ### session
        if self.session:
            super().send_response(*args, **kwargs)  # type:ignore[no-untyped-call]

    def call_magic(self, line: str) -> Magic:
        """
        Given an line, such as "%download http://example.com/", parse
        and execute magic.
        """
        return self.get_magic(line)

    def get_magic(self, text: str) -> Magic:
        ## FIXME: Bad name, use call_magic instead.
        # if first line matches a magic,
        # call magic.call_magic() and return magic object
        info = self.parse_code(text)
        magic = self.line_magics["magic"]
        return magic.get_magic(info)  # type:ignore[no-any-return]

    def get_magic_args(self, text: str) -> Magic:
        # if first line matches a magic,
        # call magic.call_magic() and return magic args
        info = self.parse_code(text)
        magic = self.line_magics["magic"]
        return magic.get_magic(info, get_args=True)  # type:ignore[no-any-return]

    def get_help_on(
        self,
        expr: str,
        level: int = 0,
        none_on_fail: bool = False,
        cursor_pos: int = -1,
    ) -> Any:
        """Get help for an expression using the help magic."""
        help_magic = self.line_magics["help"]
        return help_magic.get_text_help_on(expr, level, none_on_fail, cursor_pos)

    def parse_code(
        self, code: str, cursor_start: int = 0, cursor_end: int = -1
    ) -> dict[str, Any]:
        """Parse code using our parser."""
        return self.parser.parse_code(code, cursor_start, cursor_end)

    def _get_sticky_magics(self) -> str:
        retval = ""
        for key in self.sticky_magics:
            retval += key + " " + self.sticky_magics[key] + "\n"
        return retval

    def _send_shell_response(self, socket: Any, stream_type: str, content: Any) -> None:
        publish_display_data({"text/plain": content["text"]})  # type:ignore[no-untyped-call]


class MetaKernelApp(IPKernelApp):
    """The MetaKernel launcher application."""

    config_dir = Unicode()

    def _config_dir_default(self) -> str:
        return jupyter_config_dir()

    @property
    def config_file_paths(self) -> list[str]:  # type:ignore[override]
        path = jupyter_config_path()
        if self.config_dir not in path:
            path.insert(0, self.config_dir)
        path.insert(0, os.getcwd())
        return path

    @classmethod
    def launch_instance(cls, *args: Any, **kwargs: Any) -> None:
        cls.name = kwargs.pop("app_name", "metakernel")
        super().launch_instance(*args, **kwargs)

    @property
    def subcommands(self) -> dict[str, Any]:  # type:ignore[override]
        # Slightly awkward way to pass the actual kernel class to the install
        # subcommand.

        class KernelInstallerApp(Application):
            kernel_class = self.kernel_class

            def initialize(self, argv: Any = None) -> None:
                self.argv = argv

            def start(self) -> None:
                kernel_spec = self.kernel_class().kernel_json
                with TemporaryDirectory() as td:
                    dirname = os.path.join(td, kernel_spec["name"])
                    os.mkdir(dirname)
                    with open(os.path.join(dirname, "kernel.json"), "w") as f:
                        json.dump(kernel_spec, f, sort_keys=True)
                    filenames = ["logo-64x64.png", "logo-32x32.png"]
                    name = self.kernel_class.__module__
                    for filename in filenames:
                        try:
                            data = pkgutil.get_data(
                                name.split(".")[0], "images/" + filename
                            )
                        except OSError:
                            data = pkgutil.get_data("metakernel", "images/" + filename)
                        with open(os.path.join(dirname, filename), "wb") as f:
                            f.write(data)  # type:ignore[arg-type]
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "jupyter", "kernelspec", "install"]
                            + self.argv
                            + [dirname]
                        )
                    except CalledProcessError as exc:
                        sys.exit(exc.returncode)

        return {"install": (KernelInstallerApp, "Install this kernel")}


def _split_magics_code(code: str, prefixes: dict[str, Any]) -> tuple[str, str]:
    lines = code.split("\n")
    ret_magics = []
    ret_code = []
    index = 0
    shell = prefixes["shell"]
    magic = prefixes["magic"]
    while index < len(lines) and lines[index].startswith((shell, magic)):
        ret_magics.append(lines[index])
        index += 1
    while index < len(lines):
        ret_code.append(lines[index])
        index += 1
    ret_magics_str = "\n".join(ret_magics)
    if ret_magics_str:
        ret_magics_str += "\n"
    ret_code_str = "\n".join(ret_code)
    if ret_code_str:
        ret_code_str += "\n"
    return (ret_magics_str, ret_code_str)


def format_message(*objects: Any, **kwargs: Any) -> str:
    """
    Format a message like print() does.
    """
    str_objects = [str(i) for i in objects]
    sep: str = kwargs.get("sep", " ")
    end: str = kwargs.get("end", "\n")
    return sep.join(str_objects) + end


class IPythonKernel(MetaKernel):
    """
    Class to make an IPython Kernel look like a MetaKernel Kernel.
    """

    language_info: dict[str, Any] = {
        "mimetype": "text/x-python",
        "name": "python",
        "file_extension": ".py",
    }

    def __init__(self) -> None:
        from metakernel.magics.magic_magic import MagicMagic

        self.line_magics: dict[str, Magic] = {"magic": MagicMagic(self)}
        self.cell_magics = {}
        self.parser = Parser(
            self.identifier_regex,
            self.func_call_regex,
            self.magic_prefixes,
            self.help_suffix,
        )
        self.shell = None

    def Display(self, *objects: Any, **kwargs: Any) -> Any:
        """Display an object in the kernel, using `IPython.display`."""
        from IPython.display import display

        return display(*objects, **kwargs)  # type:ignore[no-untyped-call]

    def Error(self, *objects: Any, **kwargs: Any) -> None:
        """Print `objects` to stderr, separated by `sep` and followed by `end`."""
        sys.stderr.write(format_message(*objects, **kwargs))

    def Print(self, *objects: Any, **kwargs: Any) -> None:
        """Print `objects` to stdout, separated by `sep` and followed by `end`."""
        sys.stdout.write(format_message(*objects, **kwargs))


def register_ipython_magics(*magics: str) -> None:
    """
    Loads all magics (or specified magics) that have a
    register_ipython_magics function defined.
    """
    magic_filenames = [name + "_magic.py" for name in magics] if magics else []
    local_magics_dir = get_local_magics_dir()
    # Search all of the places there could be magics:
    paths = [
        local_magics_dir,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "magics"),
    ]

    magic_files = []
    for magic_dir in paths:
        sys.path.append(magic_dir)
        magic_files.extend(glob.glob(os.path.join(magic_dir, "*.py")))

    for magic in magic_files:
        basename = os.path.basename(magic)
        if basename == "__init__.py":
            continue
        if len(magic_filenames) == 0 or basename in magic_filenames:
            module = __import__(os.path.splitext(basename)[0])
            importlib.reload(module)
            if hasattr(module, "register_ipython_magics"):
                module.register_ipython_magics()
