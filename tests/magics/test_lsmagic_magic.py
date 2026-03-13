import asyncio
import os
import tempfile
import unittest.mock

from tests.utils import get_kernel, get_log_text


def test_lsmagic_magic() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%lsmagic"))
    text = get_log_text(kernel)

    for item in "%cd %connect_info %download %edit %help %html %install_magic %javascript %kernel %kx %latex %load %lsmagic %magic %parallel %plot %pmap %px %python %reload_magics %restart %run %shell %macro %%debug %%file %%help %%html %%javascript %%kx %%latex %%processing %%px %%python %%shell %%show %%macro %%time".split():
        assert item in text, "lsmagic didn't list '%s'" % item


def test_lsmagic_verbose() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%lsmagic -v"))
    text = get_log_text(kernel)

    assert "Magic search paths:" in text
    assert "No load errors." in text


def test_lsmagic_verbose_with_load_error() -> None:
    with tempfile.TemporaryDirectory() as local_magics_dir:
        broken_magic = os.path.join(local_magics_dir, "broken_magic.py")
        with open(broken_magic, "w") as f:
            f.write("this is not valid python )(")

        with unittest.mock.patch(
            "metakernel._metakernel.get_local_magics_dir",
            return_value=local_magics_dir,
        ):
            kernel = get_kernel()

        assert local_magics_dir in kernel.magic_search_paths
        assert any(broken_magic in path for path, _ in kernel.magic_load_errors)

        asyncio.run(kernel.do_execute("%lsmagic -v"))
        text = get_log_text(kernel)

    assert local_magics_dir in text
    assert "Load errors:" in text
    assert "broken_magic.py" in text
