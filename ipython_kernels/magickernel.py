try:
    from IPython.kernel.zmq.kernelbase import Kernel
except:
    Kernel = object
import os
import sys
import glob
import base64
from magic import Magic
import imp
import re

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
        self.reload_magics()
        sys.stdout.write = self.Write

    def reload_magics(self):
        self.magics = {}
        magic_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "magics")
        sys.path.append(magic_directory)
        magic_files = glob.glob(os.path.join(magic_directory, "*.py"))
        for magic in magic_files:
            basename = os.path.basename(magic)
            if basename == "__init__.py":
                continue
            try:
                module = __import__(os.path.splitext(basename)[0])
                imp.reload(module)
                module.register_magics(self.magics)
            except Exception as e:
                print("Can't load '%s': error: %s" % (magic, e.message))

    def parse_magic(self, text):
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

    def Display(self, *args):
        for message in args:
            self.send_response(self.iopub_socket, 'display_data', 
                               {'data': self.formatter(message)})

    def Print(self, *args, **kwargs):
        end = kwargs["end"] if ("end" in kwargs) else "\n"
        message = " ".join(args) + end
        stream_content = {'name': 'stdout', 'data': message}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Write(self, message):
        stream_content = {'name': 'stdout', 'data': message}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def Error(self, *args, **kwargs):
        end = kwargs["end"] if ("end" in kwargs) else "\n"
        message = " ".join(args) + end
        stream_content = {'name': 'stderr', 'data': message}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def get_magic(self, text):
        # if first line matches a magic,
        # return Magic(self, code, args)
        parts = self.parse_magic(text)
        if parts:
            command, args, code = parts
            if command.startswith("%%%"):
                name = "%%" + command[3:]
                if name in self.sticky_magics:
                    del self.sticky_magics[name]
                    self.Print("%s removed from session magics.\n" % name)
                    # dummy magic to eat this line and continue:
                    return Magic(self, code, "cell", args)
                else:
                    self.sticky_magics[name] = args
                    self.Print("%s added to session magics.\n" % name)
                    name = name[2:]
                    mtype = "cell"
            elif command.startswith("%%"):
                name = command[2:]
                mtype = "cell"
            elif command.startswith("%"):
                name = command[1:]
                mtype = "line"
            elif command.startswith("!"):
                name = "shell"
                mtype = "line"
            elif command.startswith("!!"):
                name = "shell"
                mtype = "cell"
            else:
                return None
            if name in self.magics:
                klass = self.magics[name]
                return klass(self, code, mtype, args)
            else:
                # FIXME: Raise an error
                return None
        return None

    def set_variable(self, name, value):
        """
        Set a variable in the kernel language.
        """
        pass

    def get_sticky_magics(self):
        retval = ""
        for key in self.sticky_magics:
            retval += (key + " " + " ".join(self.sticky_magics[key])).strip() + "\n"
        return retval

    def split_magics_code(self, code):
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

    def repr(self, item):
        return repr(item)

    def formatter(self, data):
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

    def help_patterns(self):
        # Longest first:
        return [
            ("^(.*)\?\?$", 2, 
             "item?? - get detailed help on item"), # "code??", level, explain
            ("^(.*)\?$", 1, 
             "item? - get help on item"),   # "code?"
            ("^\?\?(.*)$", 2, 
             "??item - get detailed help on item"), # "??code"
            ("^\?(.*)$", 1, 
             "?item - get help on item"),   # "?code"
        ]
        
    def get_help_on(self, expr, level):
        return "Sorry, no help is available."

    def get_usage(self):
        return "This is a usage statement."

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

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        # Handle Magics
        payload = self._process_help(code)
        if not payload:
            retval = None
            if self.sticky_magics:
                magics, code = self.split_magics_code(code)
                code = magics + self.get_sticky_magics() + code
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
                content = {'execution_count': self.execution_count, 'data': self.formatter(retval)}
                self.send_response(self.iopub_socket, 'execute_result', content)
        return {
            'status': 'ok',
            # The base class increments the execution count
            'execution_count': self.execution_count,
            'payload': payload,
            'user_expressions': {},
        }


