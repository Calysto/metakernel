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
import imp
import re
import inspect


class MagicKernel(Kernel):

    split_characters = "( )\n\;'\""
    magic_prefixes = dict(magic='%', shell='!', help='?')
    magic_suffixes = dict(help='?')

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
        Returns the path to local magics dir (eg ~/.ipython/jupyter_kernel/magics)
        """
        base = get_ipython_dir()
        return os.path.join(base, 'jupyter_kernel', 'magics')

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

    def restart_kernel(self):
        """Restart the kernel"""
        pass

    ############################################
    # Implement base class methods

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
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

        info = self.parse_code(code)
        payload = []
        retval = None

        if info['magic'] and info['magic']['name'] == 'help':

            if info['magic']['type'] == 'line':
                level = 0
            else:
                level = 1
            text = self.get_help_on(code, level)
            self.log.debug(text)
            payload = [{"data": {"text/plain": text},
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
                retval = self.do_execute_direct(code)
            # Post-process magics:
            for magic in reversed(stack):
                retval = magic.post_process(retval)
        else:
            retval = self.do_execute_direct(code)

        self.post_execute(retval, code)

        kernel_resp['payload'] = payload
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
        self.log.info("do_complete: code=%s" % code)
        code, start, cursor_pos = _parse_partial(code, cursor_pos, 
                                                 self.split_characters)
        self.log.info("do_complete: code=%s" % code)
        info = self.parse_code(code, start, cursor_pos)
        self.log.info("do_complete: info=%s" % str(info))
        content = {
            'matches': [],
            'cursor_start': info['start'],
            'cursor_end': info['end'],
            'metadata': {},
            'status': 'ok'
        }

        if info['magic']:
            if info['magic']['type'] == 'line':
                magics = self.line_magics
            else:
                magics = self.cell_magics
            if info['rest'] and info['magic']['name'] in magics:
                magic = magics[info['magic']['name']]
                content['matches'].extend(magic.get_completions(info))
            else:
                for name in magics.keys():
                    if name.startswith(info['magic']['name']):
                        full_name = info['magic']['symbol'] + name
                        content['matches'].append(full_name)
        else:
            content['matches'].extend(self.get_completions(info))

        if not info['magic'] or info['rest']:
            content['matches'].extend(_complete_path(info['obj']))
        content["matches"] = sorted(content["matches"])

        return content

    def do_inspect(self, code, cursor_pos, detail_level=0):
        # Object introspection
        self.log.info("do_inspect, detail_level=%d" % detail_level)
        if cursor_pos > len(code):
            return
        partial, start, end = _parse_partial(code, cursor_pos, self.split_characters)
        content = {'status': 'aborted', 'data': {}, 'found': False}
        docstring = self.get_help_on(partial, detail_level, none_on_fail=True)

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
        # Make a jupyter_kernel/magics if it doesn't exist:
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
        info = self.parse_code(text)
        magic = self.line_magics['magic']
        return magic.get_magic(info)

    def get_help_on(self, expr, level=0, none_on_fail=False):
        info = self.parse_code(expr)
        help_magic = self.line_magics['help']
        return help_magic.get_help_on(info, level, none_on_fail)

    def parse_code(self, code, start=0, end=-1):
        info = _parse_code(code, self.magic_prefixes, self.magic_suffixes,
                           start, end)

        split_str = self.split_characters
        if '|' in split_str and not r'\|' in split_str:
            split_str = split_str.replace('|', r'\|')

        tokens = re.split('|'.join(split_str), info['rest'])
        if tokens:
            info['obj'] = tokens[-1].rstrip()

        return info

    def _get_sticky_magics(self):
        retval = ""
        for key in self.sticky_magics:
            retval += (key + " " +
                       " ".join(self.sticky_magics[key])).strip() + "\n"
        return retval


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
        pass  # no need to report invalid paths
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


def _parse_magic(text, prefixes):
    lines = text.split("\n")
    command = lines[0]
    shell_prefix = prefixes['shell']
    if command.startswith(prefixes['magic']):
        if " " in command:
            command, args = command.split(" ", 1)
        else:
            args = ""
    elif command.startswith('{0}{0}'.format(shell_prefix)):
        args = command[2:]
    elif command.startswith(shell_prefix):
        args = command[1:]
    else:
        args = ""
    code = "\n".join(lines[1:])
    args = args.strip()
    return command, args, code


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


def _parse_partial(code, cursor_pos, split_characters):
    if cursor_pos == len(code):
        cursor_position = len(code) - 1
    # skip over non-interesting characters:
    while (cursor_pos - 1 > 0 and 
           code[cursor_pos - 1] in split_characters):
        cursor_pos -= 1
    # include only interesting characters:
    start = cursor_pos
    while (start - 1 >= 0 and 
           code[start - 1] not in split_characters):
        start -= 1
    return code[start:cursor_pos], start, cursor_pos

        
def _parse_code(code, prefixes, suffixes, start=0, end=-1):
    if end == -1:
        end = len(code)
    end = min(end, len(code))

    start = min(start, len(code))
    snip = code[start: end].rstrip()

    info = dict(type=None, magic={}, end=end, obj='',
                start=start, rest=snip, code=code)

    tokens = snip.split()
    if not tokens:
        return info

    # find magic characters - help overrides any others
    pre_magics = {}
    for (name, prefix) in prefixes.items():
        pre = ''
        while len(pre) < len(snip) and snip[len(pre)] == prefix:
            pre += prefix
        if pre:
            pre_magics[name] = pre

    post_magics = {}
    for (name, suffix) in suffixes.items():
        post = ''
        while len(post) < len(snip) and snip[-len(post) - 1] == suffix:
            post += suffix
        if post:
            post_magics[name] = post

    if 'help' in pre_magics:
        info['magic']['name'] = 'help'
        info['magic']['symbol'] = pre_magics['help']
        info['rest'] = info['rest'][len(pre_magics['help']):]

    elif 'help' in post_magics:
        info['magic']['name'] = 'help'
        info['magic']['symbol'] = post_magics['help']
        info['rest'] = info['rest'][:-len(post_magics['help'])]

    elif 'shell' in pre_magics:
        info['magic']['name'] = 'shell'
        info['magic']['symbol'] = pre_magics['shell']
        info['rest'] = info['rest'][len(pre_magics['shell']):]

    elif 'magic' in pre_magics:
        first = tokens[0]
        info['magic']['name'] = first[len(pre_magics['magic']):]
        info['magic']['symbol'] = pre_magics['magic']
        info['rest'] = info['rest'][len(first):]

    if info['magic']:
        if len(info['magic']['symbol']) == 3:
            info['magic']['type'] = 'sticky'
        elif len(info['magic']['symbol']) == 2:
            info['magic']['type'] = 'cell'
        else:
            info['magic']['type'] = 'line'

        cmd, args, magic_code = _parse_magic(snip, prefixes)
        info['magic']['cmd'] = cmd
        info['magic']['args'] = args
        info['magic']['code'] = magic_code

    return info


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
