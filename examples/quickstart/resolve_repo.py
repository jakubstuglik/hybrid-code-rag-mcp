#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Resolve the tree to index from REPO_PATH / REPO_URL / REPO_REF.

Prints two lines to stdout:
  1. Absolute path of the source tree
  2. Kind: sample | path | url

Used by entrypoint.sh.  Does not index anything.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SAMPLE = Path("/app/examples/quickstart/sample")
MOUNT = Path("/data/repo")
CLONE_ROOT = Path("/data/clone")
STAMP = CLONE_ROOT / ".origin"


def _env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def _looks_populated(path: Path) -> bool:
    if not path.is_dir():
        return False
    try:
        next(path.iterdir())
    except StopIteration:
        return False
    return True


def _clone(url: str, ref: str, dest: Path) -> None:
    if shutil.which("git") is None:
        raise SystemExit(
            "git is not installed in the app image; cannot clone REPO_URL. "
            "Rebuild the image, or clone the repo on the host and pass REPO_PATH."
        )
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Cloning {url} into {dest} ...", file=sys.stderr, flush=True)
    if ref:
        try:
            _run(["git", "clone", "--depth", "1", "--branch", ref, url, str(dest)])
            return
        except subprocess.CalledProcessError:
            print(
                f"--branch {ref} failed (it may be a commit); cloning and checking out ...",
                file=sys.stderr,
                flush=True,
            )
            _run(["git", "clone", url, str(dest)])
            _run(["git", "checkout", "--detach", ref], cwd=dest)
            return
    _run(["git", "clone", "--depth", "1", url, str(dest)])


def resolve() -> tuple[Path, str]:
    url = _env("REPO_URL")
    path = _env("REPO_PATH")
    ref = _env("REPO_REF")

    if url:
        if path:
            print(
                "Both REPO_URL and REPO_PATH are set; using REPO_URL.",
                file=sys.stderr,
                flush=True,
            )
        dest = CLONE_ROOT / "repo"
        wanted = f"{url}\n{ref}\n"
        if dest.is_dir() and STAMP.is_file() and STAMP.read_text() == wanted:
            print("Reusing the existing clone (URL and ref unchanged).", file=sys.stderr)
        else:
            _clone(url, ref, dest)
            STAMP.write_text(wanted)
        return dest, "url"

    if _looks_populated(MOUNT):
        if ref:
            print(
                "REPO_REF is ignored when using a bind-mounted REPO_PATH; "
                "check out that ref on the host before starting Compose.",
                file=sys.stderr,
                flush=True,
            )
        # A populated mount is either the user's REPO_PATH or the default
        # ./sample bind.  The entrypoint still distinguishes the bundled
        # sample via HCR_SOURCE_KIND=path vs sample by comparing to SAMPLE
        # only when the mount was not requested...  Kind "path" is always
        # used here; the entrypoint maps the default mount to "sample".
        return MOUNT, "path"

    if SAMPLE.is_dir():
        return SAMPLE, "sample"

    raise SystemExit(
        "No source tree found. Set REPO_PATH or REPO_URL, or keep the bundled sample."
    )


def main() -> int:
    try:
        root, kind = resolve()
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or exc.stdout or str(exc))
        return 1
    print(root)
    print(kind)
    return 0


if __name__ == "__main__":
    sys.exit(main())
