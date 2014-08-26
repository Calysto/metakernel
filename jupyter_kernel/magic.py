class Magic(object):

    def __init__(self, kernel):
        self.kernel = kernel
        self.evaluate = True
        self.code = ''

    def call_magic(self, mtype, name, code, args):
        self.code = code
        func = getattr(self, mtype + '_' + name)
        func(args)
        return self

    def get_help(self, mtype, name):
        func = getattr(self, mtype + '_' + name)
        return func.__doc__

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
