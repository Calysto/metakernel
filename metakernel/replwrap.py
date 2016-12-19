import re
import sys
from pexpect.replwrap import REPLWrapper, bash


IS_WINDOWS = sys.platform == 'win32'


class IREPLWrapper(REPLWrapper):
    """A subclass of REPLWrapper that gives incremental output.

    The parameters are the same as for REPLWrapper, except for one
    extra parameter:
    :param line_output_callback: a callback method to receive each batch
      of incremental output. It takes one string parameter.
    """
    def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
                 extra_init_cmd=None, line_output_callback=None):
        self.line_output_callback = line_output_callback
        REPLWrapper.__init__(self, cmd_or_spawn, orig_prompt,
                                      prompt_change, extra_init_cmd=extra_init_cmd)

    def _expect_prompt(self, timeout=-1):
        if timeout is None:
            # "None" means we are executing code from a Jupyter cell by way of the run_command
            # in the do_execute() code below, so do incremental output.
            while True:
                pos = self.child.expect_exact([self.prompt, self.continuation_prompt, '\r\n'],
                                              timeout=None)
                if pos == 2:
                    # End of line received
                    self.line_output_callback(self.child.before + '\n')
                else:
                    if len(self.child.before) != 0:
                        # prompt received, but partial line precedes it
                        self.line_output_callback(self.child.before)
                    break
        else:
            # Otherwise, use existing non-incremental code
            pos = REPLWrapper._expect_prompt(self, timeout=timeout)

        # Prompt received, so return normally
        return pos


def python(command="python"):
    """Start a Python shell and return a :class:`REPLWrapper` object."""
    if IS_WINDOWS:
        raise OSError('Not supported on platform "%s"' % sys.platform)
    return IREPLWrapper(command, u">>> ",
                       u"import sys; sys.ps1={0!r}; sys.ps2={1!r}")


def cmd(command='cmd', prompt_regex=re.compile(r'[A-Z]:\\.*>')):
    """"Start a cmd shell and return a :class:`REPLWrapper` object."""
    if IS_WINDOWS:
        raise OSError('cmd only available on Windows')
    return IREPLWrapper(command, prompt_regex, None, echo=True)
