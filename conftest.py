import asyncio
import sys

if sys.platform == "win32":
    if sys.version_info >= (3, 14):
        asyncio.set_event_loop(asyncio.SelectorEventLoop())
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
