"""
Example use of jupyter_kernel_test, with tests for the default python3 kernel
(IPyKernel). This includes all the currently available tests.
"""

import unittest
import jupyter_kernel_test as jkt

class MetaKernelPythonTests(jkt.KernelTests):

    # REQUIRED

    # the kernel to be tested
    # this is the normally the name of the directory containing the
    # kernel.json file - you should be able to do
    # `jupyter console --kernel KERNEL_NAME`
    kernel_name = "metakernel_python"

    # Everything else is OPTIONAL

    # the name of the language the kernel executes
    # checked against language_info.name in kernel_info_reply
    language_name = "python"

    # the normal file extension (including the leading dot) for this language
    # checked against language_info.file_extension in kernel_info_reply
    file_extension = ".py"

    # code which should write the exact string `hello, world` to STDOUT
    code_hello_world = "print('hello, world')"

    # code which should cause (any) text to be written to STDERR
    code_stderr = "import sys; print('test', file=sys.stderr)"

    # samples for the autocompletion functionality
    # for each dictionary, `text` is the input to try and complete, and
    # `matches` the list of all complete matching strings which should be found
    completion_samples = [
        {
            'text': 'zi',
            'matches': {'zip'},
        },
    ]

    # samples for testing code-completeness (used by console only)
    # these samples should respectively be unambigiously complete statements
    # (which should be executed on <enter>), incomplete statements or code
    # which should be identified as invalid
    complete_code_samples = ['1', "print('hello, world')", "def f(x):\n  return x*2\n\n\n"]
    incomplete_code_samples = ["print('''hello", "def f(x):\n  x*2"]
    invalid_code_samples = ['import = 7q']

    # code which should cause a help pager to be displayed (as of 4.1, this is
    # displayed by the notebook only as inline text, so it's probably more
    # useful for console clients)
    code_page_something = "zip?"

    # code which should generate a (user-level) error in the kernel, and send
    # a traceback to the client
    code_generate_error = "raise"

    # a statement or block of code which generates a result (which is shown
    # as Out[n] instead of just something printed to stdout)
    # running each `code` should cause `result` to be displayed (note that the
    # result here will always be a string representation of whatever the actual
    # result type is - be careful of string formatting)
    code_execute_result = [
        {'code': "1+2+3", 'result': "6"},
        {'code': "[n*n for n in range(1, 4)]", 'result': "[1, 4, 9]"}
    ]

    # code which generates some sort of rich output
    # for each `code` input a single rich display object with the specified
    # `mime` type should be sent to the frontend
    # note that this expects a `display_data` message rather than
    # `execute_result`; this test might be a little too inflexible in some cases
    code_display_data = [
        {'code': "from IPython.display import HTML, display; display(HTML('<b>test</b>'))",
         'mime': "text/html"},
        {'code': "from IPython.display import Math, display; display(Math('\\frac{1}{2}'))",
         'mime': "text/latex"}
    ]

    # test the support for searching/recalling history (used by console only)
    # the history tests re-use the code blocks in `code_execute_result` above,
    # so will not run if no test code is available
    # `code_history_pattern` is a glob-style pattern which should match at least
    # one code sample in `code_execute_result`
    # `supported_history_operations` is a list of the `hist_access_type` options
    # which should be tested; possible values are "tail", "range" and "search"
    code_history_pattern = "1?2*"
    supported_history_operations = ("tail", "search")

    # test the support for object inspection
    # the sample should be a name about which the kernel can give some help
    # information (a built-in function is probably a good choice)
    # only the default inspection level (equivalent to ipython "obj?")
    # is currently tested
    code_inspect_sample = "zip"

    # a code sample which should cause a `clear_output` message to be sent to
    # the client
    code_clear_output = "from IPython.display import clear_output; clear_output()"

if __name__ == '__main__':
    unittest.main()
