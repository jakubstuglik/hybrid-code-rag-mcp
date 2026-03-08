from pathlib import Path
from typing import List
import hashlib
import fnmatch

import config
from shared.log import log_warn


def normalize_file_key(source_dir_path: str, relative_posix: str) -> str:
    """Build the canonical file key from a source directory path and a relative posix path.

    This is the **single source of truth** for file path keys used in:
      - Qdrant ``file_path`` payload (before mapping)
      - Manifest dict keys
      - UUID generation for Qdrant point IDs (using mapped path)
      - Delete filter matching (using mapped path)

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
    if not source_dir_path or source_dir_path == ".":
        raw = relative_posix.replace("\\", "/")
    else:
        raw = f"{source_dir_path}/{relative_posix}".replace("\\", "/")

    if raw.startswith("./"):
        raw = raw[2:]
    return raw


def map_path_to_qdrant(file_path: str) -> str:
    """Map a local relative path to its Qdrant mapped path, if map_to_path is configured."""
    normalized = file_path.replace("\\", "/")
    # Strip leading "./" if present
    if normalized.startswith("./"):
        normalized = normalized[2:]

    for source_dir in config.SOURCE_DIRS:
        prefix = source_dir["path"].replace("\\", "/")

        # Handle empty string (root folder) case
        if not prefix or prefix == ".":
            map_to = source_dir.get("map_to_path")
            if map_to:
                map_to = map_to.replace("\\", "/")
                if not map_to.endswith("/"):
                    map_to += "/"
                return map_to + normalized
            return normalized

        if not prefix.endswith("/"):
            prefix += "/"

        # Check if the path is exactly the prefix (without trailing slash) or starts with the prefix directory
        if normalized.startswith(prefix) or normalized == prefix[:-1]:
            map_to = source_dir.get("map_to_path")
            if map_to:
                map_to = map_to.replace("\\", "/")
                if not map_to.endswith("/"):
                    map_to += "/"
                # Replace the prefix with the mapped path prefix
                mapped = normalized.replace(prefix, map_to, 1)
                if normalized == prefix[:-1]:
                    mapped = map_to[:-1]
                return mapped
    return normalized


def map_path_from_qdrant(mapped_path: str) -> str:
    """Map a Qdrant mapped path back to the local relative path."""
    normalized = mapped_path.replace("\\", "/")

    for source_dir in config.SOURCE_DIRS:
        map_to = source_dir.get("map_to_path")
        if map_to:
            map_to = map_to.replace("\\", "/").rstrip("/") + "/"

            # Check if the mapped path starts with the map_to prefix or is exactly the map_to prefix (without trailing slash)
            if normalized.startswith(map_to) or normalized == map_to[:-1]:
                prefix = source_dir["path"].replace("\\", "/").rstrip("/")

                # If prefix is empty or ".", we just strip the map_to part
                if not prefix or prefix == ".":
                    unmapped = normalized.replace(map_to, "", 1)
                    if normalized == map_to[:-1]:
                        return ""
                    return unmapped

                prefix += "/"
                # Replace the mapped prefix with the local prefix
                unmapped = normalized.replace(map_to, prefix, 1)
                if normalized == map_to[:-1]:
                    unmapped = prefix[:-1]
                return unmapped
    return normalized


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        log_warn(f"Could not hash {file_path}: {e}")
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
