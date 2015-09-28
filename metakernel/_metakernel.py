from __future__ import print_function

import sys
import warnings
warnings.filterwarnings('ignore', module='IPython.html.widgets')

try:
    try:
        from ipykernel.kernelbase import Kernel
        from ipykernel.comm import CommManager
        from IPython.paths import get_ipython_dir
    except ImportError:
        from IPython.kernel.zmq.kernelbase import Kernel
        from IPython.kernel.comm import CommManager
        from IPython.utils.path import get_ipython_dir
    from IPython.display import HTML
    try:
        from ipywidgets.widgets.widget import Widget
    except ImportError:
        from IPython.html.widgets import Widget
    from IPython.core.formatters import IPythonDisplayFormatter
except ImportError as e:
    warnings.warn("Cannot load module {name} so metakernel will not be available to IPython/jupyter.".format(name=getattr(e, 'name', '')))
    # This module won't be useful without IPython
    # (other parts of metakernel may be useful)
    # but we make it loadable anyway
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
import codecs

PY3 = (sys.version_info[0] >= 3)

def lazy_import_handle_comm_opened(*args, **kwargs):
    Widget.handle_comm_opened(*args, **kwargs)

def get_metakernel():
    """
    Get the MetaKernel instance.
    """
    return MetaKernel.meta_kernel

class MetaKernel(Kernel):

    identifier_regex = r'[^\d\W][\w\.]*'
    func_call_regex = r'([^\d\W][\w\.]*)\([^\)\()]*\Z'
    magic_prefixes = dict(magic='%', shell='!', help='?')
    help_suffix = '?'
    help_links = [
        {
            'text': "MetaKernel Magics",
            'url': "https://github.com/calysto/metakernel/blob/master/metakernel/magics/README.md",
        },
    ]
    language_info = {
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
        'help_links': help_links,
    }
    meta_kernel = None

    def __init__(self, *args, **kwargs):
        super(MetaKernel, self).__init__(*args, **kwargs)
        if MetaKernel.meta_kernel is None:
            MetaKernel.meta_kernel = self
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
        self.comm_manager = CommManager(shell=None, parent=self,
                                        kernel=self)
        self.comm_manager.register_target('ipython.widget',
            lazy_import_handle_comm_opened)

        self.plot_settings = dict(backend='inline')
        self.hist_file = get_history_file(self)
        self.reload_magics()
        # provide a way to get the current instance
        self.set_variable("kernel", self)
        self.parser = Parser(self.identifier_regex, self.func_call_regex,
                             self.magic_prefixes, self.help_suffix)
        self.comm_manager = CommManager(shell=None, parent=self,
                                        kernel=self)
        self.comm_manager.register_target('ipython.widget',
                                          lazy_import_handle_comm_opened)
        comm_msg_types = ['comm_open', 'comm_msg', 'comm_close']
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(self.comm_manager, msg_type)
        self._ipy_formatter = IPythonDisplayFormatter()

    @classmethod
    def subkernel(cls, kernel):
        """
        Handle issues regarding making a kernel a subkernel to this
        one. Used in %parallel and %kernel.
        """
        pass

    def makeSubkernelTo(self, main_kernel, display_function):
        """
        Handle issues regarding making this kernel be a subkernel to
        another. Used in making metakernels be magics for IPython.
        """
        self.session = main_kernel.session
        self.Display = display_function

    def makeSubkernelToIPython(self):
        """
        Run this method in an IPython kernel to set
        this kernel's input/output settings.
        """
        from IPython import get_ipython
        from IPython.display import display
        ip = get_ipython()
        if ip: # we are running under an IPython kernel
            self.makeSubkernelTo(ip.parent, display)
        else:
            raise Exception("Need to run under an IPython kernel")

    #####################################
    # Methods which provide kernel - specific behavior

    def set_variable(self, name, value):
        """
        Set a variable to a Python-typed value.
        """
        pass

    def get_variable(self, name):
        """
        Lookup a variable name and return a Python-typed value.
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

    def do_execute_direct(self, code, silent=False):
        """
        Execute code in the kernel language.
        """
        pass

    def do_execute_file(self, filename):
        """
        Default code for running a file. Just opens the file, and sends
        the text to do_execute_direct.
        """
        code = "".join(open(filename).readlines())
        return self.do_execute_direct(code)

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

    def initialize_debug(self, code):
        """
        This function is used with the %%debug magic for highlighting
        lines of code, and for initializing debug functions.

        Return the empty string if highlighting is not supported.
        """
        #return "highlight: [%s, %s, %s, %s]" % (line1, col1, line2, col2)
        return ""

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

    def do_execute(self, code, silent=False, store_history=True, user_expressions=None,
                   allow_stdin=False):
        # Set the ability for the kernel to get standard-in:
        self._allow_stdin = allow_stdin
        # Create a default response:
        self.kernel_resp = {
            'status': 'ok',
            # The base class increments the execution count
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

        # TODO: remove this when IPython fixes this
        # This happens at startup when the language is set to python
        if '_usage.page_guiref' in code:
            return self.kernel_resp

        if code and store_history:
            self.hist_cache.append(code.strip())

        if not code.strip():
            return self.kernel_resp

        info = self.parse_code(code)
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

        self.post_execute(retval, code, silent)

        if 'payload' in self.kernel_resp:
            self.kernel_resp['payload'] = self.payload

        return self.kernel_resp

    def post_execute(self, retval, code, silent):
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
            try:
                content = {'execution_count': self.execution_count,
                           'data': _formatter(retval, self.repr),
                           'metadata': dict()}
            except Exception as e:
                self.Error(e)
                return
            if not silent:
                if isinstance(retval, Widget):
                    self.Display(retval)
                    return
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
            self.Print("Restarting kernel...")
            self.reload_magics()
            self.restart_kernel()
            self.Print("Done!")
        return {'status': 'ok', 'restart': restart}

    def do_is_complete(self, code):
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
        """
        return {'status' : 'unknown'}

    def do_complete(self, code, cursor_pos):
        info = self.parse_code(code, 0, cursor_pos)
        content = {
            'matches': [],
            'cursor_start': info['start'],
            'cursor_end': info['end'],
            'metadata': {},
            'status': 'ok'
        }

        matches = info['path_matches']

        if info['magic']:

            # if the last line contains another magic, use that
            line_info = self.parse_code(info['line'])
            if line_info['magic']:
                info = line_info

            if info['magic']['type'] == 'line':
                magics = self.line_magics
            else:
                magics = self.cell_magics

            if info['magic']['name'] in magics:
                magic = magics[info['magic']['name']]
                info = info['magic']
                if info['type'] == 'cell' and info['code']:
                    info = self.parse_code(info['code'])
                else:
                    info = self.parse_code(info['args'])

                matches.extend(magic.get_completions(info))

            elif not info['magic']['code'] and not info['magic']['args']:
                matches = []
                for name in magics.keys():
                    if name.startswith(info['magic']['name']):
                        pre = info['magic']['prefix']
                        matches.append(pre + name)
                        info['start'] -= len(pre)
                        info['full_obj'] = pre + info['full_obj']
                        info['obj'] = pre + info['obj']

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
        docstring = self.get_help_on(code, detail_level, none_on_fail=True,
             cursor_pos=cursor_pos)

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
        paths = [local_magics_dir,
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "magics")]
        try:
            paths += [os.path.join(os.path.dirname(
                os.path.abspath(inspect.getfile(self.__class__))), "magics")]
        except:
            pass
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

    def clear_output(self, wait=False):
        self.send_response(self.iopub_socket, 'clear_output',
                           {'wait': wait})

    def Display(self, *args, **kwargs):
        clear_output = kwargs.get("clear_output", False)
        for message in args:
            if isinstance(message, HTML):
                if clear_output:
                    self.send_response(self.iopub_socket, 'clear_output',
                                       {'wait': True})
            if isinstance(message, Widget):
                self.log.debug('Display Widget')
                self._ipy_formatter(message)
            else:
                self.log.debug('Display Data')
                try:
                    data = _formatter(message, self.repr)
                except Exception as e:
                    self.Error(e)
                    return
                self.send_response(self.iopub_socket, 'display_data',
                                   {'data': data,
                                    'metadata': dict()})

    def Print(self, *args, **kwargs):
        end = kwargs["end"] if ("end" in kwargs) else "\n"
        message = ""
        for item in args:
            if isinstance(item, Widget):
                self.Display(item)
            else:
                if message:
                    message += " "
                if PY3:
                    message += str(item)
                else:
                    message += codecs.encode(item, "utf-8")
        message += end
        stream_content = {
            'name': 'stdout', 'text': message, 'metadata': dict()}
        self.log.debug('Print: %s' % message)
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Write(self, message):
        stream_content = {
            'name': 'stdout', 'text': message, 'metadata': dict()}
        self.log.debug('Write: %s' % message)
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Error(self, *args, **kwargs):
        message = format_message(*args, **kwargs)
        self.log.debug('Error: %s' % message)
        stream_content = {
            'name': 'stderr', 'text': message, 'metadata': dict()}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def call_magic(self, line):
        """
        Given an line, such as "%download http://example.com/", parse
        and execute magic.
        """
        return self.get_magic(line)

    def get_magic(self, text):
        ## FIXME: Bad name, use call_magic instead.
        # if first line matches a magic,
        # call magic.call_magic() and return magic object
        info = self.parse_code(text)
        magic = self.line_magics['magic']
        return magic.get_magic(info)

    def get_magic_args(self, text):
        # if first line matches a magic,
        # call magic.call_magic() and return magic args
        info = self.parse_code(text)
        magic = self.line_magics['magic']
        return magic.get_magic(info, get_args=True)

    def get_help_on(self, expr, level=0, none_on_fail=False,
            cursor_pos=-1):
        help_magic = self.line_magics['help']
        return help_magic.get_help_on(expr, level, none_on_fail, cursor_pos)

    def parse_code(self, code, cursor_start=0, cursor_end=-1):
        return self.parser.parse_code(code, cursor_start, cursor_end)

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
    reprs = {}
    reprs['text/plain'] = repr_func(data)

    lut = [("_repr_png_", "image/png"),
           ("_repr_jpeg_", "image/jpeg"),
           ("_repr_html_", "text/html"),
           ("_repr_markdown_", "text/markdown"),
           ("_repr_svg_", "image/svg+xml"),
           ("_repr_latex_", "text/latex"),
           ("_repr_json_", "application/json"),
           ("_repr_javascript_", "application/javascript"),
           ("_repr_pdf_", "application/pdf")]

    for (attr, mimetype) in lut:
        obj = getattr(data, attr, None)
        if obj:
            reprs[mimetype] = obj

    retval = {}
    for (mimetype, value) in reprs.items():
        try:
            value = value()
        except Exception:
            pass
        if not value:
            continue
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except Exception:
                value = base64.encodestring(value)
                value = value.decode('utf-8')
        retval[mimetype] = str(value)
    return retval

def format_message(*args, **kwargs):
    """
    Format args like Print does.
    """
    end = kwargs["end"] if ("end" in kwargs) else "\n"
    message = " ".join([str(a) for a in args]) + end
    return message

class IPythonKernel(MetaKernel):
    """
    Class to make an IPython Kernel look like a MetaKernel Kernel.
    """
    language_info = {
        'mimetype': 'text/x-python',
        'name': 'python',
        'file_extension': '.py',
    }

    def __init__(self):
        from metakernel.magics.magic_magic import MagicMagic
        self.line_magics = {'magic': MagicMagic(self)}
        self.cell_magics = {}
        self.parser = Parser(self.identifier_regex, self.func_call_regex,
                             self.magic_prefixes, self.help_suffix)

    def Display(self, *args, **kwargs):
        from IPython.display import display
        return display(*args, **kwargs)

    def Error(self, *args, **kwargs):
        sys.stderr.write(format_message(*args, **kwargs))

    def Print(self, *args, **kwargs):
        sys.stdout.write(format_message(*args, **kwargs))

def register_ipython_magics(*magics):
    """
    Loads all magics (or specified magics) that have a
    register_ipython_magics function defined.
    """
    if magics:
        # filename is name of magic + "_magic.py"
        magics = [name + "_magic.py" for name in magics]
    local_magics_dir = get_local_magics_dir()
    # Search all of the places there could be magics:
    paths = [local_magics_dir,
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "magics")]

    magic_files = []
    for magic_dir in paths:
        sys.path.append(magic_dir)
        magic_files.extend(glob.glob(os.path.join(magic_dir, "*.py")))

    for magic in magic_files:
        basename = os.path.basename(magic)
        if basename == "__init__.py":
            continue
        if len(magics) == 0 or basename in magics:
            module = __import__(os.path.splitext(basename)[0])
            imp.reload(module)
            if hasattr(module, "register_ipython_magics"):
                module.register_ipython_magics()
