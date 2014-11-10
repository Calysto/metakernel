from metakernel.tests.utils import get_kernel, EvalKernel, get_log_text


def test_restart_magic():
    kernel = get_kernel(EvalKernel)

    kernel.do_execute('a=1')
    kernel.do_execute("%restart")
    kernel.do_execute('a')

    text = get_log_text(kernel)
    assert 'NameError' in text
