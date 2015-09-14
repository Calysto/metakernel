
from metakernel.tests.utils import get_kernel, get_log_text


def test_lsmagic_magic():
    kernel = get_kernel()
    kernel.do_execute("%lsmagic")
    text = get_log_text(kernel)

    for item in "%cd %connect_info %download %edit %help %html %install_magic %javascript %kernel %kx %latex %load %lsmagic %magic %parallel %plot %pmap %px %python %reload_magics %restart %run %shell %macro %%debug %%file %%help %%html %%javascript %%kx %%latex %%processing %%px %%python %%shell %%show %%macro %%time".split():
        assert item in text, ("lsmagic didn't list '%s'" % item)
  

