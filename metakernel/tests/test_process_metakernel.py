
from metakernel.tests.utils import get_kernel, get_log_text
from metakernel.process_metakernel import BashKernel


def test_process_metakernel():
    kernel = get_kernel(BashKernel)
    kernel.do_execute("cat \"%s\"" % __file__, False)
    log_text = get_log_text(kernel)
    assert 'metakernel.py' in log_text, log_text

    kernel.do_execute('echo "hello"\necho "goodbye"', None)
    log_text = get_log_text(kernel)
    assert '"hello"' in log_text
    assert '"goodbye"' in log_text

    kernel.do_execute('lalkjds')
    text = get_log_text(kernel)
    assert ': command not found' in text, text
