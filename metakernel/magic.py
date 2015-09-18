import traceback
import optparse
import inspect
import sys
import os
import shlex

try:
    _maxsize = sys.maxint
except:
    # python3
    _maxsize = sys.maxsize

class MagicOptionParser(optparse.OptionParser):
    def error(self, msg):
        raise Exception('Magic Parse error: "%s"' % msg)

    def exit(self, status=0, msg=None):
        if msg:
            sys.stderr.write(msg)
        raise Exception(msg)

    ## FIXME: override help to also stop processing
    ## currently --help gives syntax error

class Magic(object):

    def __init__(self, kernel):
        self.kernel = kernel
        self.evaluate = True
        self.code = ''

    def get_args(self, mtype, name, code, args) :
        self.code = code
        old_args = args
        mtype = mtype.replace('sticky', 'cell')

        func = getattr(self, mtype + '_' + name)
        try:
            args, kwargs = _parse_args(func, args, usage=self.get_help(mtype, name))
        except Exception as e:
            self.kernel.Error(str(e))
            return self

        arg_spec = inspect.getargspec(func)
        fargs = arg_spec.args
        if fargs[0] == 'self':
            fargs = fargs[1:]

        fargs = [f for f in fargs if not f in kwargs.keys()]
        if len(args) > len(fargs) and not arg_spec.varargs:
            extra = ' '.join(str(s) for s in (args[len(fargs) - 1:]))
            args = args[:len(fargs) - 1] + [extra]

        return (args, kwargs, old_args)

    def call_magic(self, mtype, name, code, args):
        self.code = code
        old_args = args
        mtype = mtype.replace('sticky', 'cell')

        func = getattr(self, mtype + '_' + name)
        try:
            args, kwargs = _parse_args(func, args, usage=self.get_help(mtype, name))
        except Exception as e:
            self.kernel.Error(str(e))
            return self

        arg_spec = inspect.getargspec(func)
        fargs = arg_spec.args
        if fargs[0] == 'self':
            fargs = fargs[1:]

        fargs = [f for f in fargs if not f in kwargs.keys()]
        if len(args) > len(fargs) and not arg_spec.varargs:
            extra = ' '.join(str(s) for s in (args[len(fargs) - 1:]))
            args = args[:len(fargs) - 1] + [extra]

        try:
            try:
                func(*args, **kwargs)
            except TypeError:
                func(old_args)
        except Exception as exc:
            msg = "Error in calling magic '%s' on %s:\n    %s\n    args: %s\n    kwargs: %s" % (
                name, mtype, str(exc), args, kwargs)
            self.kernel.Error(msg)
            self.kernel.Error(traceback.format_exc())
            self.kernel.Error(self.get_help(mtype, name))
            # return dummy magic to end processing:
            return Magic(self.kernel)
        return self

    def get_help(self, mtype, name, level=0):
        if hasattr(self, mtype + '_' + name):
            func = getattr(self, mtype + '_' + name)
            if level == 0:
                if func.__doc__:
                    return _trim(func.__doc__)
                else:
                    return "No help available for magic '%s' for %ss." % (name, mtype)
            else:
                filename = inspect.getfile(func)
                if filename and os.path.exists(filename):
                    return open(filename).read()
                else:
                    return "No help available for magic '%s' for %ss." % (name, mtype)
        else:
            return "No such magic '%s' for %ss." % (name, mtype)

    def get_help_on(self, info, level=0):
        return "Sorry, no help is available on '%s'." % info['code']

    def get_completions(self, info):
            """
            Get completions based on info dict from magic.
            """
            return []

    def get_magics(self, mtype):
        magics = []
        for name in dir(self):
            if name.startswith(mtype + '_'):
                magics.append(name.replace(mtype + '_', ''))
        return magics

    def get_code(self):
        return self.code

    def post_process(self, retval):
        return retval


def option(*args, **kwargs):
    """Return decorator that adds a magic option to a function.
    """
    def decorator(func):
        help_text = ""
        if not getattr(func, 'has_options', False):
            func.has_options = True
            func.options = []
            help_text += 'Options:\n-------\n'
        try:
            option = optparse.Option(*args, **kwargs)
        except optparse.OptionError:
            help_text += args[0] + "\n"
        else:
            help_text += _format_option(option) + "\n"
            func.options.append(option)
        func.__doc__ += _indent(func.__doc__, help_text)
        return func
    return decorator


def _parse_args(func, args, usage=None):
    """Parse the arguments given to a magic function"""
    if isinstance(args, list):
        args = ' '.join(args)

    args = _split_args(args)

    kwargs = dict()
    if getattr(func, 'has_options', False):
        parser = MagicOptionParser(usage=usage)
        parser.add_options(func.options)

        left = []
        value = None
        if '--' in args:
            left = args[:args.index('--')]
            value, args = parser.parse_args(args[args.index('--') + 1:])
        else:
            while args:
                try:
                    value, args = parser.parse_args(args)
                except Exception:
                    left.append(args.pop(0))
                else:
                    break
        args = left + args
        if value:
            kwargs = value.__dict__

    new_args = []
    for arg in args:
        try:
            new_args.append(eval(arg))
        except:
            new_args.append(arg)

    for (key, value) in kwargs.items():
        try:
            kwargs[key] = eval(value)
        except:
            pass

    return new_args, kwargs


def _split_args(args):
    try:
        # do not use posix mode, to avoid eating quote characters
        args = shlex.split(args, posix=False)
    except:
        # parse error; let's pass args along rather than crashing
        args = args.split()

    new_args = []
    temp = ''
    for arg in args:
        if arg.startswith('-'):
            new_args.append(arg)

        elif temp:

            arg = temp + ' ' + arg
            try:
                eval(arg)
            except:
                temp = arg
            else:
                new_args.append(arg)
                temp = ''

        elif arg.startswith(('(', '[', '{')) or '(' in arg:
            try:
                eval(arg)
            except:
                temp = arg
            else:
                new_args.append(arg)

        else:
            new_args.append(arg)

    if temp:
        new_args.append(temp)

    return new_args


def _format_option(option):
    output = ''
    if option._short_opts:
        output = option._short_opts[0] + ' '
    output += option.get_opt_string() + ' '
    output += ' ' * (15 - len(output))
    output += option.help + ' '
    if not option.default == ('NO', 'DEFAULT'):
        output += '[default: %s]' % option.default
    return output


def _trim(docstring, return_lines=False):
    """
    Trim of unnecessary leading indentations.
    """
    # from: http://legacy.python.org/dev/peps/pep-0257/
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    indent = _min_indent(lines)
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < _maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    if return_lines:
        return trimmed
    else:
        # Return a single string:
        return '\n'.join(trimmed)

def _min_indent(lines):
    """
    Determine minimum indentation (first line doesn't count):
    """
    indent = _maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    return indent

def _indent(docstring, text):
    """
    Returns text indented at appropriate indententation level.
    """
    if not docstring:
        return text
    lines = docstring.expandtabs().splitlines()
    indent = _min_indent(lines)
    if indent < _maxsize:
        newlines = _trim(text, return_lines=True)
        return "\n" + ("\n".join([(" " * indent) + line for line in newlines]))
    else:
        return "\n" + text
