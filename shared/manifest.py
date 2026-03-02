from pathlib import Path
from typing import List, Optional, Dict
import hashlib
import json


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
    """Get all source files that should be indexed."""
    source_extensions = [".pas", ".dpr", ".dfm", ".fr3", ".sql"]
    files = []

    if Path("source").exists():
        for ext in source_extensions:
            files.extend(Path("source").rglob(f"*{ext}"))

    if Path("schemas").exists():
        files.extend(Path("schemas").rglob("*.sql"))

    return sorted(files)
