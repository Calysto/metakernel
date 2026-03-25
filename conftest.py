import asyncio
import sys

# Exclude logo-generation scripts that require optional Graphics/Myro packages
collect_ignore_glob = ["metakernel/images/*.py"]

if sys.platform == "win32":
    if sys.version_info >= (3, 14):
        asyncio.set_event_loop(asyncio.SelectorEventLoop())
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
