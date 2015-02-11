
from metakernel.tests.utils import get_kernel


def test_plot_magic_backend():
    kernel = get_kernel()
    kernel.do_execute('%plot qt -f svg -s400,200', None)
    assert kernel.plot_settings['size'] == (400, 200)
    assert kernel.plot_settings['format'] == 'svg'
    assert kernel.plot_settings['backend'] == 'qt'

def test_plot_magic_format():
    kernel = get_kernel()
    kernel.do_execute('%plot qt -f svg')
    assert kernel.plot_settings['backend'] == 'qt', kernel.plot_settings
    assert kernel.plot_settings['format'] == 'svg', kernel.plot_settings

def test_plot_magic_size():
    kernel = get_kernel()
    kernel.do_execute('%plot qt4 -s 400,200')
    assert kernel.plot_settings['size'] == (400, 200), kernel.plot_settings
    assert kernel.plot_settings['backend'] == 'qt4', kernel.plot_settings

def test_plot_magic_all():
    kernel = get_kernel()
    kernel.do_execute('%plot -b qt5 -f svg -s 400,200')
    assert kernel.plot_settings['size'] == (400, 200), kernel.plot_settings
    assert kernel.plot_settings['format'] == 'svg', kernel.plot_settings
    assert kernel.plot_settings['backend'] == 'qt5', kernel.plot_settings

