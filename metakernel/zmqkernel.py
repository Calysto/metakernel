# TODO Implement this properly
class ZmqKernel(MetaKernel):
    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        return self.client.execute(code, silent, store_history, user_expressions, allow_stdin)

    def do_complete(self, code, cursor_pos):
        return self.client.complete(code, cursor_pos)

    def do_inspect(self, code, cursor_pos, detail_level=0):
        return self.client.inspect(code, cursor_pos, detail_level)

    def do_history(self, hist_access_type, output, raw, session=None, start=None, stop=None, n=None, pattern=None, unique=False):
        return self.client.history(hist_access_type, output, raw, session, start, stop, n, pattern, unique)

    def do_shutdown(self, restart):
        return self.client.shutdown(restart)
