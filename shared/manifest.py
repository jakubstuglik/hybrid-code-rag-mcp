from pathlib import Path
from typing import List
import hashlib
import fnmatch

import config


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"      Warning: Could not hash {file_path}: {e}")
        return ""


def is_excluded(path: Path, exclude_patterns: List[str]) -> bool:
    """Check if any part of the path matches an exclude pattern."""
    if not exclude_patterns:
        return False
    parts = path.parts
    for pattern in exclude_patterns:
        for part in parts:
            if fnmatch.fnmatch(part, pattern):
                return True
    return False


def get_source_files() -> List[Path]:
    """Get all source files that should be indexed, driven by config.SOURCE_DIRS."""
    files = []
    for source_dir in config.SOURCE_DIRS:
        dir_path = Path(source_dir["path"])
        if not dir_path.exists():
            continue
        exclude_patterns = source_dir.get("exclude", [])
        for ext in source_dir["extensions"]:
            for f in dir_path.rglob(f"*{ext}"):
                if f.is_file() and not is_excluded(f, exclude_patterns):
                    files.append(f)
    return sorted(files)
