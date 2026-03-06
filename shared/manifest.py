from pathlib import Path
from typing import List
import hashlib
import fnmatch

import config


def normalize_file_key(source_dir_path: str, relative_posix: str) -> str:
    """Build the canonical file key from a source directory path and a relative posix path.

    This is the **single source of truth** for file path keys used in:
      - Qdrant ``file_path`` payload
      - Manifest dict keys
      - UUID generation for Qdrant point IDs
      - Delete filter matching

    The canonical form is ``"{source_dir_path}/{relative_posix}"`` with the
    special case that a leading ``"./"`` is stripped (when the source dir is ``"."``).

    Examples:
        >>> normalize_file_key("source", "Common/foo.pas")
        'source/Common/foo.pas'
        >>> normalize_file_key(".", "config.py")
        'config.py'
        >>> normalize_file_key(".", "shared/manifest.py")
        'shared/manifest.py'
    """
    raw = f"{source_dir_path}/{relative_posix}".replace("\\", "/")
    if raw.startswith("./"):
        raw = raw[2:]
    return raw


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
