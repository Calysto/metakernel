import asyncio
import json

from tests.utils import get_kernel, get_log_text


def test_connect_info_magic_reads_existing_connection_file(tmp_path) -> None:
    connection_info = {
        "stdin_port": 1,
        "shell_port": 2,
        "iopub_port": 3,
        "hb_port": 4,
        "ip": "127.0.0.1",
        "key": "abc123",
        "signature_scheme": "hmac-sha256",
        "transport": "tcp",
    }
    connection_file = tmp_path / "kernel-connection.json"
    connection_file.write_text(json.dumps(connection_info))

    kernel = get_kernel()
    kernel.config["IPKernelApp"]["connection_file"] = str(connection_file)
    asyncio.run(kernel.do_execute("%connect_info"))
    text = get_log_text(kernel)

    assert '"ip": "127.0.0.1"' in text
    assert '"key": "abc123"' in text
    assert "$> ipython <app> --existing abc123" in text


def test_connect_info_magic() -> None:
    kernel = get_kernel()
    asyncio.run(kernel.do_execute("%connect_info"))
    text = get_log_text(kernel)
    assert (
        """{
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
""".strip()
        in text
    ), text
