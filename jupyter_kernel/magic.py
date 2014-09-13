import optparse
import inspect
import os


class Magic(object):

    def __init__(self, kernel):
        self.kernel = kernel
        self.evaluate = True
        self.code = ''

    def call_magic(self, mtype, name, code, args):
        self.code = code
        old_args = args
        mtype = mtype.replace('sticky', 'cell')
        func = getattr(self, mtype + '_' + name)
        args, kwargs = _parse_args(func, args)

        argspec = inspect.getargspec(func)
        if not argspec.defaults is None:
            total_args = len(argspec.args) - len(argspec.defaults) - 1
        else:
            total_args = len(argspec.args) - 1
        if total_args == 0 and argspec.varargs is None:
            args = []

        try:
            try:
                func(*args, **kwargs)
            except TypeError:
                func(old_args)
        except Exception as exc:
            msg = "Error in calling magic '%s' on %s:\n    %s\n    args: %s\n    kwargs: %s" % (
                name, mtype, str(exc), args, kwargs)
            self.kernel.Error(msg)
            self.kernel.Error(self.get_help(mtype, name))
            # return dummy magic to end processing:
            return Magic(self.kernel)
        return self

    def get_help(self, mtype, name, level=0):
        if hasattr(self, mtype + '_' + name):
            func = getattr(self, mtype + '_' + name)
            if level == 0:
                if func.__doc__:
                    return func.__doc__.lstrip()
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
        return "Sorry, no help is available on '%s'." % info["code"]

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
        if not getattr(func, 'has_options', False):
            func.has_options = True
            func.options = []
            func.__doc__ += '\nOptions:\n-------'
        try:
            option = optparse.Option(*args, **kwargs)
        except optparse.OptionError:
            func.__doc__ += '\n' + args[0]
        else:
            func.__doc__ += '\n' + _format_option(option)
            func.options.append(option)
        return func
    return decorator


def _parse_args(func, args):
    """Parse the arguments given to a magic function"""
    if not isinstance(args, list):
        args = args.split()

    if not getattr(func, 'has_options', False):
        kwargs = dict()
    else:
        parser = optparse.OptionParser()
        parser.add_options(func.options)
        value, args = parser.parse_args(args)
        kwargs = value.__dict__

    return args, kwargs


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
