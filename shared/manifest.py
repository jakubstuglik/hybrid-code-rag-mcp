from pathlib import Path
from typing import List
import hashlib

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


def get_source_files() -> List[Path]:
    """Get all source files that should be indexed, driven by config.SOURCE_DIRS."""
    files = []
    for source_dir in config.SOURCE_DIRS:
        dir_path = Path(source_dir["path"])
        if not dir_path.exists():
            continue
        for ext in source_dir["extensions"]:
            files.extend(dir_path.rglob(f"*{ext}"))
    return sorted(files)
