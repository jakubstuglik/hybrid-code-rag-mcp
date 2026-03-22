#!/usr/bin/env python3
"""Simple git pull for all repos in a config's SOURCE_DIRS.

Usage:
    python src/git_pull_all.py --config config_informica_tei_jinaai
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
for _p in (_root, _here):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def git_pull_repo(repo_path: str) -> tuple[str, int]:
    result = subprocess.run(
        ["git", "-C", repo_path, "pull"],
        capture_output=True,
        text=True,
    )
    return repo_path, result.returncode, result.stdout, result.stderr


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg_name = args.config
    cfg_path = Path(_root) / "project-configs" / cfg_name / "config.py"
    if not cfg_path.exists():
        cfg_path = Path(_root) / f"{cfg_name}.py"
    if not cfg_path.exists():
        print(f"Config not found: {cfg_name}")
        sys.exit(1)

    import importlib.util

    spec = importlib.util.spec_from_file_location("config", cfg_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg = mod

    repos = [src["path"] for src in cfg.SOURCE_DIRS if src.get("type") == "git_repo"]

    if not repos:
        print(f"No git_repo sources in {cfg_name}")
        sys.exit(0)

    print(f"Pulling {len(repos)} repos for {cfg_name}")
    for repo, rc, out, err in [git_pull_repo(r) for r in repos]:
        if rc == 0:
            print(f"  [OK] {repo}: {out.strip()}")
        else:
            print(f"  [FAIL] {repo}: {err.strip()}")


if __name__ == "__main__":
    main()
