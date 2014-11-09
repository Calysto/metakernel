
from metakernel.tests.utils import get_kernel


def test_plot_magic():
    kernel = get_kernel()
    kernel.do_execute('%plot qt -f svg -s400,200', None)
    assert kernel.plot_settings['size'] == (400, 200)
    assert kernel.plot_settings['format'] == 'svg'
    assert kernel.plot_settings['backend'] == 'qt'

