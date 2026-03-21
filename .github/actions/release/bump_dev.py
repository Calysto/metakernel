#!/usr/bin/env python3
"""
Transform a version string to a .dev version:
  - "1.2.3"           -> "1.2.3.dev0"
  - "1.2.3rc1"        -> "1.2.3.dev0"
  - "1.2.3beta2"      -> "1.2.3.dev0"
  - "1.2.3alpha1"     -> "1.2.3.dev0"
  - "1.2.3.dev4"      -> "1.2.3.dev5"  (incremented)
"""

import re
import sys


def transform_version(version: str) -> str:
    # If already has .dev, increment the dev number
    m = re.match(r"^(.+\.dev)(\d+)$", version)
    if m:
        return f"{m.group(1)}{int(m.group(2)) + 1}"

    # Strip pre-release suffixes: rc, beta, alpha (and any trailing digits)
    cleaned = re.sub(r"(rc|beta|alpha)\w*$", "", version, flags=re.IGNORECASE)

    # Remove any trailing dot or separator left behind
    cleaned = cleaned.rstrip(".-_")

    return f"{cleaned}.dev0"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: bump_dev.py <version>")
        sys.exit(1)

    result = transform_version(sys.argv[1])
    print(result)
