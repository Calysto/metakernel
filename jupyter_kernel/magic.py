import optparse


class Magic(object):

    def __init__(self, kernel):
        self.kernel = kernel
        self.evaluate = True
        self.code = ''

    def call_magic(self, mtype, name, code, args):
        self.code = code
        func = getattr(self, mtype + '_' + name)
        args, kwargs = _parse_args(func, args)
        func(*args, **kwargs)
        return self

    def get_help(self, mtype, name):
        func = getattr(self, mtype + '_' + name)
        msg = "(no help available for magic '%s' operating on a %s)"
        return func.__doc__ if func.__doc__ else msg % (name, mtype)

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


def argument(*args, **kwargs):
    """Return decorator that adds a magic argument to a function.
    """
    def decorator(func):
        if not getattr(func, 'has_arguments', False):
            func.has_arguments = True
            func.arguments = []
            func.__doc__ += '\nOptions:\n-------'
        try:
            option = optparse.Option(*args, **kwargs)
        except optparse.OptionError:
            func.__doc__ += '\n' + args[0]
        else:
            func.__doc__ += '\n' + _format_option(option)
            func.arguments.append(option)
        return func
    return decorator


def _parse_args(func, args):
    """Parse the arguments given to a magic function"""
    if not isinstance(args, list):
        args = args.split()
    if not getattr(func, 'has_arguments', False):
        return args, dict()
    parser = optparse.OptionParser()
    parser.add_options(func.arguments)
    value, args = parser.parse_args(args)
    return args, value.__dict__


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
