class Magic(object):
    name = None
    help_lines = []
    def __init__(self, kernel, code, mtype, args):
        self.kernel = kernel
        self.code = code
        self.mtype = mtype
        self.args = args
        self.evaluate = True
        if mtype == "line":
            self.line(args)
        elif mtype == "cell":
            self.cell(args)

    def cell(self, args):
        pass

    def line(self, args):
        pass

    def get_code(self):
        return self.code
        
    def post_process(self, retval):
        return retval
