try:
    from IPython.kernel.zmq.kernelbase import Kernel
    from IPython.utils.path import get_ipython_dir
    from IPython.html.widgets import Widget
except:
    Kernel = object
import os
import sys
import glob
import base64
from .magic import Magic
from .config import get_history_file, get_local_magics_dir
import imp
import re
import inspect


class MagicKernel(Kernel):
    def __init__(self, *args, **kwargs):
        super(MagicKernel, self).__init__(*args, **kwargs)
        self.sticky_magics = {}
        self._i = None
        self._ii = None
        self._iii = None
        self._ = None
        self.__ = None
        self.___ = None
        self.max_hist_cache = 1000
        self.hist_cache = []
        self.plot_settings = dict(backend='inline', format=None, size=None)
        self.hist_file = get_history_file(self)
        self.reload_magics()
        try:
            sys.stdout.write = self.Write
        except:
            pass  # Can't change stdout
        # provide a way to get the current instance
        import jupyter_kernel
        jupyter_kernel.JUPYTER_INSTANCE = self
        self.set_variable("get_jupyter", jupyter_kernel.get_jupyter)

    #####################################
    # Methods which provide kernel - specific behavior

    def set_variable(self, name, value):
        """
        Set a variable in the kernel language.
        """
        pass

    def get_variable(self, name):
        """
        Get a variable from the kernel language.
        """
        pass

    def repr(self, item):
        return repr(item)

    def get_usage(self):
        return "This is a usage statement."

    def get_kernel_help_on(self, expr, level=0):
        return "Sorry, no help is available on '%s'." % expr

    def handle_plot_settings(self):
        """Handle the current plot settings"""
        pass

    def get_local_magics_dir(self):
        """
        Returns the path to local magics dir (eg ~/.ipython/jupyter_kernel/magics)
        """
        base = get_ipython_dir()
        return os.path.join(base, 'jupyter_kernel', 'magics')

    def add_complete(self, matches, token):
        """
        Add matches based on token from kernel.
        """
        return

    def do_execute_direct(self, code):
        """
        Execute code in the kernel language.
        """
        pass

    ############################################
    # Implement base class methods

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if code and store_history:
            self.hist_cache.append(code.strip())
        # Handle Magics
        payload = self._process_help(code)
        if not payload:
            retval = None
            if self.sticky_magics:
                magics, code = _split_magics_code(code)
                code = magics + self._get_sticky_magics() + code
            stack = []
            # Handle magics:
            magic = None
            while code.startswith("%") or code.startswith("!"):
                magic = self.get_magic(code)
                if magic != None:
                    stack.append(magic)
                    code = magic.get_code()
                    if not magic.evaluate: # signal to exit, maybe error or no block
                        break
                else:
                    break
            # Execute code, if any:
            if ((magic is None or magic.evaluate) and code.strip() != ""):
                retval = self.do_execute_direct(code)
            # Post-process magics:
            for magic in reversed(stack):
                retval = magic.post_process(retval)
            ## Handle in's
            self.set_variable("_iii", self._iii);
            self.set_variable("_ii", self._ii);
            self.set_variable("_i", code);
            self.set_variable("_i" + str(self.execution_count), code);
            self._iii = self._ii;
            self._ii = code;
            if (retval is not None):
                ## --------------------------------------
                ## Handle out's (only when non-null)
                self.set_variable("___", self.___)
                self.set_variable("__", self.__)
                self.set_variable("_", retval)
                self.set_variable("_" + str(self.execution_count), retval)
                self.___ = self.__
                self.__ = retval
                self.log.debug(retval)
                content = {'execution_count': self.execution_count,
                                    'data': self._formatter(retval),
                                    'metadata': dict()}
                self.send_response(self.iopub_socket, 'execute_result', content)
        return {
            'status': 'ok',
            # The base class increments the execution count
            'execution_count': self.execution_count,
            'payload': payload,
            'user_expressions': {},
        }

    def do_history(self, hist_access_type, output, raw, session=None,
                   start=None, stop=None, n=None, pattern=None, unique=False):
        """
        Access history at startup.
        """
        if not self.hist_file:
            return {'history': []}
        # else:
        if not os.path.exists(self.hist_file):
            with open(self.hist_file, 'wb') as fid:
                fid.write('')
        with open(self.hist_file, 'rb') as fid:
            history = fid.read().decode('utf-8', 'replace')
        history = history.splitlines()
        history = history[:self.max_hist_cache]
        self.hist_cache = history
        history = [(None, None, h) for h in history]
        return {'history': history}

    def do_shutdown(self, restart):
        """
        Shut down the app gracefully, saving history.
        """
        if self.hist_file:
            with open(self.hist_file, 'wb') as fid:
                data = '\n'.join(self.hist_cache[-self.max_hist_cache:])
                fid.write(data.encode('utf-8'))
        return {'status': 'ok', 'restart': restart}

    def do_complete(self, code, cursor_pos):
        token, start, end = self._get_complete(code, 0, cursor_pos)
        content = {
            'matches' : [],
            'cursor_start' : start,
            'cursor_end' : end,
            'metadata' : {},
            'status' : 'ok'
        }
        # from magics:
        if code.startswith("%%"):
            for name in self.cell_magics.keys():
                if name.startswith(token[2:]):
                    content['matches'].append('%%' + name)
        elif code.startswith('%'):
            for name in self.line_magics.keys():
                if name.startswith(token[1:]):
                    content['matches'].append("%" + name)
        # from shell
        if code.startswith(('!', "%shell", "%%shell")):
            shell_magic = self.line_magics['shell']
            content['matches'].extend(shell_magic.get_complete(token))
        # Add more from kernel:
        self.add_complete(content["matches"], token)
        content['matches'].extend(_complete_path(token))
        content["matches"] = sorted(content["matches"])
        return content

    def do_inspect(self, code, cursor_pos, detail_level=0):
        # Object introspection
        token, start, end = self._get_complete(code, 0, cursor_pos)
        self.log.debug(code)
        content = {'status': 'aborted', 'data': {}, 'found': False}
        docstring = self.get_help_on(token)
        if docstring:
            content["data"] = {"text/plain": docstring}
            content["status"] = "ok"
            content["found"] = True
            self.log.debug(docstring)
        return content

    ##############################
    # Private API and methods not likely to be overridden

    def reload_magics(self):
        self.line_magics = {}
        self.cell_magics = {}

        # get base magic files and those relative to the current class directory
        magic_files = []
        # Make a jupyter_kernel/magics if it doesn't exist:
        local_magics_dir = get_local_magics_dir()
        # Search all of the places there could be magics:
        paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "magics"),
                 os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(self.__class__))), "magics"),
                 local_magics_dir]
        for magic_dir in paths:
            sys.path.append(magic_dir)
            magic_files.extend(glob.glob(os.path.join(magic_dir, "*.py")))

        for magic in magic_files:
            basename = os.path.basename(magic)
            if basename == "__init__.py":
                continue
            try:
                module = __import__(os.path.splitext(basename)[0])
                imp.reload(module)
                module.register_magics(self)
            except Exception as e:
                print("Can't load '%s': error: %s" % (magic, e))

    def register_magics(self, magic_klass):
        magic = magic_klass(self)
        line_magics = magic.get_magics('line')
        cell_magics = magic.get_magics('cell')
        for name in line_magics:
            self.line_magics[name] = magic
        for name in cell_magics:
            self.cell_magics[name] = magic

    def display_widget(self, widget):
        content = {"data"   : {"method": "display"},
                   "comm_id": widget.model_id}
        self.send_response(self.iopub_socket, "comm_open",
                           {"data": content})

    def Display(self, *args):
        for message in args:
            if isinstance(message, Widget):
                self.log.debug('Display Widget')
                self.display_widget(message)
            else:
                self.log.debug('Display Data')
                self.send_response(self.iopub_socket, 'display_data',
                                   {'data': self._formatter(message),
                                    'metadata': dict()})

    def Print(self, *args, **kwargs):
        end = kwargs["end"] if ("end" in kwargs) else "\n"
        message = " ".join(args) + end
        stream_content = {'name': 'stdout', 'data': message, 'metadata': dict()}
        self.log.debug('Print: %s' % message)
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Write(self, message):
        stream_content = {'name': 'stdout', 'data': message, 'metadata': dict()}
        self.log.debug('Write: %s' % message)
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Error(self, *args, **kwargs):
        end = kwargs["end"] if ("end" in kwargs) else "\n"
        message = " ".join([str(a) for a in args]) + end
        self.log.debug('Error: %s' % message)
        stream_content = {'name': 'stderr', 'data': message, 'metadata': dict()}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def update_plot_settings(self, backend, size, format):
        """Update the default plot settings for the kernel."""
        self.plot_settings['backend'] = backend
        size = size or self.plot_settings['size']
        self.plot_settings['size'] = size
        format = format or self.plot_settings['format']
        self.plot_settings['format'] = format

    def get_magic(self, text):
        # if first line matches a magic,
        # call magic.call_magic() and return magic object
        parts = _parse_magic(text)
        if parts:
            command, args, code = parts
            if command.startswith("%%%"):
                name = "%%" + command[3:]
                if name in self.sticky_magics:
                    del self.sticky_magics[name]
                    self.Print("%s removed from session magics.\n" % name)
                    # dummy magic to eat this line and continue:
                    return Magic(self)
                else:
                    self.sticky_magics[name] = args
                    self.Print("%s added to session magics.\n" % name)
                    name = command[3:]
                    mtype = "cell"
            elif command.startswith("%%"):
                name = command[2:]
                mtype = "cell"
            elif command.startswith("%"):
                name = command[1:]
                mtype = "line"
            elif command.startswith("!!"):
                name = "shell"
                mtype = "cell"
            elif command.startswith("!"):
                name = "shell"
                mtype = "line"
            else:
                return None
            if mtype == 'cell' and name in self.cell_magics.keys():
                magic = self.cell_magics[name]
                return magic.call_magic(mtype, name, code, args)
            elif mtype == 'line' and name in self.line_magics.keys():
                magic = self.line_magics[name]
                return magic.call_magic(mtype, name, code, args)
            else:
                # FIXME: Raise an error
                return None
        return None

    def get_help_on(self, expr, level=0):
        if expr.startswith('%'):
            name = expr.split(" ")[0].split("%")[-1]
            mtype = "cell" if expr.startswith("%%") else "line"
            return self._get_help_on_magic(name, mtype, level)
        elif expr.startswith('!'):
            name = "shell"
            mtype = "cell" if expr.startswith("!!") else "line"
            return self._get_help_on_magic(name, mtype, level)
        else:
            return self.get_kernel_help_on(expr, level)

    def help_patterns(self):
        # Longest first:
        return [
            ("^(.*)\?\?$", 1,
             "item?? - get detailed help on item"), # "code??", level, explain
            ("^(.*)\?$", 0,
             "item? - get help on item"),   # "code?"
            ("^\?\?(.*)$", 1,
             "??item - get detailed help on item"), # "??code"
            ("^\?(.*)$", 0,
             "?item - get help on item"),   # "?code"
        ]
    def _get_sticky_magics(self):
        retval = ""
        for key in self.sticky_magics:
            retval += (key + " " + " ".join(self.sticky_magics[key])).strip() + "\n"
        return retval

    def _handle_help(self, item, level):
        if item == "":            # help!
            return [{"start_line_number": 0,
                     "data": {"text/plain": self.get_usage()},
                     "source": "page"}]
        else:
            return [{"data": {"text/plain": self.get_help_on(item, level)},
                     "start_line_number": 0,
                     "source": "page"}]

    def _process_help(self, code):
        for (pattern, level, doc) in self.help_patterns():
            match = re.match(pattern, code.strip())
            if match:
                return self._handle_help(match.groups()[0], level)
        return []

    def _get_help_on_magic(self, name, mtype, level=0):
        if mtype == "cell" and name in self.cell_magics:
            magic = self.cell_magics[name]
        elif mtype == "line" and name in self.line_magics:
            magic = self.line_magics[name]
        else:
            return "No such %s magic '%s'" % (mtype, name)
        return magic.get_help(mtype, name, level)

    def _formatter(self, data):
        retval = {}
        retval["text/plain"] = self.repr(data)
        if hasattr(data, "_repr_png_"):
            obj = data._repr_png_()
            if obj:
                retval["image/png"] = base64.encodestring(obj)
        if hasattr(data, "_repr_jpeg_"):
            obj = data._repr_jpeg_()
            if obj:
                retval["image/jpeg"] = base64.encodestring(obj)
        if hasattr(data, "_repr_html_"):
            obj = data._repr_html_()
            if obj:
                retval["text/html"] = obj
        if hasattr(data, "_repr_markdown_"):
            obj = data._repr_markdown_()
            if obj:
                retval["text/markdown"] = obj
        if hasattr(data, "_repr_svg_"):
            obj = data._repr_svg_()
            if obj:
                retval["image/svg+xml"] = obj
        if hasattr(data, "_repr_latex_"):
            obj = data._repr_latex_()
            if obj:
                retval["text/latex"] = obj
        if hasattr(data, "_repr_json_"):
            obj = data._repr_json_()
            if obj:
                retval["application/json"] = obj
        if hasattr(data, "_repr_javascript_"):
            obj = data._repr_javascript_()
            if obj:
                retval["application/javascript"] = obj
        if hasattr(data, "_repr_pdf_"):
            obj = data._repr_pdf_()
            if obj:
                retval["application/pdf"] = obj
        return retval

    def _get_complete(self, code, start, end):
        """
        Parse the code line to get the element that we want to get help on.
        """
        token = ""
        end = min(end, len(code))
        current = end - 1
        while current >= 0:
            # go backwards until we find end of token:
            if code[current] in ["(", " ", ")", "\n", "\t", '"', ";", "!"]:
                return (token, current + 1, end)
            token = code[current] + token
            current -= 1
        return (token, start, end)

def _listdir(root):
    "List directory 'root' appending the path separator to subdirs."
    res = []
    root = os.path.expanduser(root)
    try:
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
    except:
        pass # no need to report invalid paths
    return res


def _complete_path(path=None):
    """Perform completion of filesystem path.

    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """
    if not path:
        return _listdir('.')
    dirname, rest = os.path.split(path)
    tmp = dirname if dirname else '.'
    res = [os.path.join(dirname, p)
           for p in _listdir(tmp) if p.startswith(rest)]
    # more than one match, or single match which does not exist (typo)
    if len(res) > 1 or not os.path.exists(path):
        return res
    # resolved to a single directory, so return list of files below it
    if os.path.isdir(path):
        return [os.path.join(path, p) for p in _listdir(path)]
    # exact file match terminates this completion
    return [path + ' ']

def _parse_magic(text):
        lines = text.split("\n")
        command = lines[0]
        if command.startswith("%"):
            if " " in command:
                command, args = command.split(" ", 1)
            else:
                args = ""
        elif command.startswith("!"):
            args = command[1:]
        else:
            args = ""
        code = "\n".join(lines[1:])
        args = args.strip()
        return command, args, code


def _split_magics_code(code):
        lines = code.split("\n")
        ret_magics = []
        ret_code = []
        index = 0
        while index < len(lines) and (lines[index].startswith("!") or
                                      lines[index].startswith("%")):
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
