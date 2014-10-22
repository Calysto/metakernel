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
from .config import get_history_file, get_local_magics_dir
from .parser import Parser
import imp
import inspect
import logging


class MetaKernel(Kernel):

    identifier_regex = r'[^\d\W]\w*'
    func_call_regex = r'([^\d\W][\w\.]*)\([^\)\()]*\Z'
    magic_prefixes = dict(magic='%', shell='!', help='?')
    help_suffix = '?'

    def __init__(self, *args, **kwargs):
        super(MetaKernel, self).__init__(*args, **kwargs)
        global JUPYTER_INSTANCE
        if self.log is None:
            # This occurs if we call as a stand-alone kernel
            # (eg, not as a process)
            # FIXME: take care of input/output, eg StringIO
            #        make work without a session
            self.log = logging.Logger(".metakernel")
        else:
            # Write has already been set
            try:
                sys.stdout.write = self.Write
            except:
                pass  # Can't change stdout
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
        # provide a way to get the current instance
        self.set_variable("get_kernel", lambda: self)
        self.parser = Parser(self.identifier_regex, self.func_call_regex,
                             self.magic_prefixes, self.help_suffix)

    @classmethod
    def subkernel(cls, kernel):
        """
        FIXME: monkeypatch to Make this kernel class be a subkernel to another.
        """
        cls.log = kernel.log
        cls.session = kernel.session
        cls.iopub_socket = kernel.iopub_socket
        cls._parent_header = kernel._parent_header

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

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        if none_on_fail:
            return None
        else:
            return "Sorry, no help is available on '%s'." % info['code']

    def handle_plot_settings(self):
        """Handle the current plot settings"""
        pass

    def get_local_magics_dir(self):
        """
        Returns the path to local magics dir (eg ~/.ipython/metakernel/magics)
        """
        base = get_ipython_dir()
        return os.path.join(base, 'metakernel', 'magics')

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        return []

    def do_execute_direct(self, code):
        """
        Execute code in the kernel language.
        """
        pass

    def do_execute_meta(self, code):
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

    def do_execute_file(self, filename):
        """
        Execute a file in the kernel language.
        """
        self.Error("This language does not support \"%run filename\".")

    def do_function_direct(self, function_name, arg):
        """
        Call a function in the kernel language with args (as a single item).
        """
        self.Error("This language does not support \"%pmap function args\".")
        
    def restart_kernel(self):
        """Restart the kernel"""
        pass

    ############################################
    # Implement base class methods

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        # Set the ability for the kernel to get standard-in:
        self._allow_stdin = allow_stdin
        # Create a default response:
        kernel_resp = {
            'status': 'ok',
            # The base class increments the execution count
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

        # TODO: remove this when IPython fixes this
        # This happens at startup when the language is set to python
        if '_usage.page_guiref' in code:
            return kernel_resp

        if code and store_history:
            self.hist_cache.append(code.strip())

        if not code.strip():
            return kernel_resp

        info = self.parser.parse_code(code)
        self.payload = []
        retval = None

        if info['magic'] and info['magic']['name'] == 'help':

            if info['magic']['type'] == 'line':
                level = 0
            else:
                level = 1
            text = self.get_help_on(code, level)
            self.log.debug(text)
            if text:
                self.payload = [{"data": {"text/plain": text},
                                 "start_line_number": 0,
                                 "source": "page"}]

        elif info['magic'] or self.sticky_magics:
            retval = None
            if self.sticky_magics:
                magics, code = _split_magics_code(code, self.magic_prefixes)
                code = magics + self._get_sticky_magics() + code
            stack = []
            # Handle magics:
            magic = None
            prefixes = ((self.magic_prefixes['shell'],
                         self.magic_prefixes['magic']))
            while code.startswith(prefixes):
                magic = self.get_magic(code)
                if magic is not None:
                    stack.append(magic)
                    code = magic.get_code()
                    # signal to exit, maybe error or no block
                    if not magic.evaluate:
                        break
                else:
                    break
            # Execute code, if any:
            if ((magic is None or magic.evaluate) and code.strip() != ""):
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

        self.post_execute(retval, code)

        kernel_resp['payload'] = self.payload
        return kernel_resp

    def post_execute(self, retval, code):
        # Handle in's
        self.set_variable("_iii", self._iii)
        self.set_variable("_ii", self._ii)
        self.set_variable("_i", code)
        self.set_variable("_i" + str(self.execution_count), code)
        self._iii = self._ii
        self._ii = code
        if (retval is not None):
            # --------------------------------------
            # Handle out's (only when non-null)
            self.set_variable("___", self.___)
            self.set_variable("__", self.__)
            self.set_variable("_", retval)
            self.set_variable("_" + str(self.execution_count), retval)
            self.___ = self.__
            self.__ = retval
            self.log.debug(retval)
            content = {'execution_count': self.execution_count,
                       'data': _formatter(retval, self.repr),
                       'metadata': dict()}
            self.send_response(self.iopub_socket, 'execute_result', content)

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
        if restart:
            self.reload_magics()
            self.restart_kernel()
        return {'status': 'ok', 'restart': restart}

    def do_complete(self, code, cursor_pos):
        info = self.parser.parse_code(code, 0, cursor_pos)

        content = {
            'matches': [],
            'cursor_start': info['start'],
            'cursor_end': info['end'],
            'metadata': {},
            'status': 'ok'
        }

        matches = info['path_matches']
        if info['magic']:
            # TODO: go down the parse tree here
            if info['magic']['type'] == 'line':
                magics = self.line_magics
            else:
                magics = self.cell_magics
            if info['magic']['name'] in magics:
                magic = magics[info['magic']['name']]
                info = self.parse_code(info['magic']['name']['args'])
                matches.extend(magic.get_completions(info))
            else:
                for name in magics.keys():
                    if name.startswith(info['magic']['name']):
                        content['matches'].append(info['magic']['full_name'])
        else:
            matches.extend(self.get_completions(info))

        if info['full_obj'] and len(info['full_obj']) > len(info['obj']):
            new_list = [m for m in matches if m.startswith(info['full_obj'])]
            if new_list:
                content['cursor_end'] = (content['cursor_end'] +
                                         len(info['full_obj']) -
                                         len(info['obj']))
                matches = new_list

        content["matches"] = sorted(matches)

        return content

    def do_inspect(self, code, cursor_pos, detail_level=0):
        # Object introspection
        if cursor_pos > len(code):
            return

        content = {'status': 'aborted', 'data': {}, 'found': False}
        docstring = self.get_help_on(code, detail_level, none_on_fail=True)

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

        # get base magic files and those relative to the current class
        # directory
        magic_files = []
        # Make a metakernel/magics if it doesn't exist:
        local_magics_dir = get_local_magics_dir()
        # Search all of the places there could be magics:
        paths = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "magics"),
                 os.path.join(
                     os.path.dirname(os.path.abspath(inspect.getfile(self.__class__))), "magics"),
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
                self.log.error("Can't load '%s': error: %s" % (magic, e))

    def register_magics(self, magic_klass):
        magic = magic_klass(self)
        line_magics = magic.get_magics('line')
        cell_magics = magic.get_magics('cell')
        for name in line_magics:
            self.line_magics[name] = magic
        for name in cell_magics:
            self.cell_magics[name] = magic

    def display_widget(self, widget):
        content = {"data": {"method": "display"},
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
                                   {'data': _formatter(message, self.repr),
                                    'metadata': dict()})

    def Print(self, *args, **kwargs):
        end = kwargs["end"] if ("end" in kwargs) else "\n"
        message = " ".join(args) + end
        stream_content = {
            'name': 'stdout', 'data': message, 'metadata': dict()}
        self.log.debug('Print: %s' % message)
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Write(self, message):
        stream_content = {
            'name': 'stdout', 'data': message, 'metadata': dict()}
        self.log.debug('Write: %s' % message)
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Error(self, *args, **kwargs):
        end = kwargs["end"] if ("end" in kwargs) else "\n"
        message = " ".join([str(a) for a in args]) + end
        self.log.debug('Error: %s' % message)
        stream_content = {
            'name': 'stderr', 'data': message, 'metadata': dict()}
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
        info = self.parser.parse_code(text)
        magic = self.line_magics['magic']
        return magic.get_magic(info)

    def get_help_on(self, expr, level=0, none_on_fail=False):
        info = self.parser.parse_code(expr)
        help_magic = self.line_magics['help']
        return help_magic.get_help_on(info, level, none_on_fail)

    def _get_sticky_magics(self):
        retval = ""
        for key in self.sticky_magics:
            retval += (key + " " +
                       " ".join(self.sticky_magics[key])).strip() + "\n"
        return retval


def _split_magics_code(code, prefixes):
    lines = code.split("\n")
    ret_magics = []
    ret_code = []
    index = 0
    shell = prefixes['shell']
    magic = prefixes['magic']
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


def _formatter(data, repr_func):
    retval = {}
    retval["text/plain"] = repr_func(data)
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
