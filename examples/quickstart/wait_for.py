#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Wait until an HTTP endpoint responds, used by the Compose entrypoint."""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: wait_for.py URL NAME [ATTEMPTS]", file=sys.stderr)
        return 2
    url = sys.argv[1]
    name = sys.argv[2]
    attempts = int(sys.argv[3]) if len(sys.argv) > 3 else 180
    print(f"Waiting for {name} at {url} ...", flush=True)
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= response.status < 500:
                    print(f"{name} is ready.", flush=True)
                    return 0
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            time.sleep(2)
    print(
        f"ERROR: {name} was not ready after {attempts * 2}s: {url}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
