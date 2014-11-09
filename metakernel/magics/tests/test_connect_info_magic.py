
from metakernel.tests.utils import get_kernel, get_log_text


def test_connect_info_magic():
    kernel = get_kernel()
    kernel.do_execute("%connect_info")
    text = get_log_text(kernel)
    assert """{
  "stdin_port": UNKNOWN,
  "shell_port": UNKNOWN,
  "iopub_port": UNKNOWN,
  "hb_port": UNKNOWN,
  "ip": "UNKNOWN",
  "key": "UNKNOWN",
  "signature_scheme": "UNKNOWN",
  "transport": "UNKNOWN"
}

Paste the above JSON into a file, and connect with:
    $> ipython <app> --existing <file>
or, if you are local, you can connect with just:
    $> ipython <app> --existing UNKNOWN

or even just:
    $> ipython <app> --existing
if this is the most recent Jupyter session you have started.
""" in text, text

