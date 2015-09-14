
from metakernel.tests.utils import get_kernel, get_log_text

def test_reload_magics_magic():
    kernel = get_kernel()
    kernel.do_execute("%reload_magics")
    text = get_log_text(kernel)

    for item in "%cd %connect_info %download %edit %help %html %install_magic %javascript %kernel %kx %latex %load %lsmagic %magic %parallel %plot %pmap %px %python %reload_magics %restart %run %shell %macro %%debug %%file %%help %%html %%javascript %%kx %%latex %%processing %%px %%python %%shell %%show %%macro %%time".split():
        assert item in text, ("load_magic didn't list '%s'" % item)

