#!/usr/bin/env python3
"""
Transform a version string to the next .dev version:
  - "1.2.3"           -> "1.2.4.dev0"  (patch bumped)
  - "1.2.3.dev4"      -> no change (already a dev version)
  - "1.2.3rc1"        -> no change (has pre-release suffix)
  - "1.2.3beta2"      -> no change (has pre-release suffix)
  - "1.2.3alpha1"     -> no change (has pre-release suffix)
"""

import re
import sys


def has_suffix(version: str) -> bool:
    """Return True if the version has any pre-release or dev suffix."""
    return bool(
        re.search(
            r"(\.dev\d*|rc\d*|alpha\d*|beta\d*|a\d+|b\d+)", version, flags=re.IGNORECASE
        )
    )


def transform_version(version: str) -> str:
    # If version has any suffix (dev, rc, alpha, beta, etc.), do not bump
    if has_suffix(version):
        return version

    # Bump the patch segment, then append .dev0
    m = re.match(r"^(\d+\.\d+\.)(\d+)$", version)
    if m:
        return f"{m.group(1)}{int(m.group(2)) + 1}.dev0"

    # Fallback: just append .dev0 if version doesn't match expected format
    return f"{version}.dev0"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: bump_dev.py <version>")
        sys.exit(1)

    result = transform_version(sys.argv[1])
    print(result)
