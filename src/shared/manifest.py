from pathlib import Path, PurePosixPath
from typing import List
import hashlib
import fnmatch
import os
import re
import sys

from typing import Any
from shared.log import log, log_warn


def make_repo_key(repo_path: str) -> str:
    """Build a platform-independent key for a git repo path.

    Uses only the last path component (directory name), e.g.::

        "../my-webapp"            → "my-webapp"
        "C:/Projects/MyProject"   → "MyProject"
        "/home/user/my-webapp"    → "my-webapp"

    This key is **the same regardless of OS or machine**, making manifests
    portable across Windows/Linux and different directory layouts.

    The key is stored in ``manifest["repo_commits"]`` and used for lookup
    in ``determine_actions()`` and ``_build_repo_group_file_map()``.
    """
    # Normalize to posix, resolve ".." components, take the last segment.
    # PurePosixPath handles both "/" and already-posix paths correctly.
    normalized = repo_path.replace("\\", "/").rstrip("/")
    # Use PurePosixPath to get the name without resolving against the filesystem,
    # so the result is identical on any OS.
    name = PurePosixPath(normalized).name
    if not name or name == "..":
        # PurePosixPath(".").name is "" and PurePosixPath("..").name is ".." —
        # neither is a real directory name.  Resolve against the filesystem to
        # get the actual directory name (e.g. "." -> "hybrid-code-rag-mcp",
        # ".." -> "GitRepos").  Similarly for "/" or other degenerate paths.
        resolved = Path(repo_path).resolve()
        name = resolved.name
    if not name:
        # Still empty (e.g. filesystem root "/") — use the normalized string
        return normalized
    return name


def prune_repo_commits(repo_commits: dict, configured_keys) -> list[str]:
    """Drop ``repo_commits`` entries of repos that are no longer configured.

    Mutates *repo_commits* in place and returns the removed keys (sorted).
    Keys are compared after ``make_repo_key()``-style normalization, so the
    caller passes the keys of the currently configured repo groups.  Entries
    that are not configured any more would otherwise stay in the manifest
    forever and show up in the index-state report.
    """
    if not isinstance(repo_commits, dict) or not repo_commits:
        return []
    keep = set(configured_keys)
    removed = sorted(k for k in repo_commits if k not in keep)
    for key in removed:
        del repo_commits[key]
    return removed


def migrate_repo_commits(repo_commits: dict) -> tuple[dict, bool]:
    """Migrate old absolute-path repo_commits keys to platform-independent format.

    Old manifests stored keys like ``C:/Projects/MyProject`` (Windows) or
    ``/home/user/my-webapp`` (Linux).  This function detects such keys and
    rewrites them to directory-name-only format (``my-webapp``).

    A key is considered "old format" if it contains a ``/`` and is not already
    a bare directory name.

    Args:
        repo_commits: The ``repo_commits`` dict from the manifest.

    Returns:
        Tuple of (migrated_dict, was_migrated).  ``was_migrated`` is True if
        any keys were rewritten.
    """
    if not repo_commits:
        return repo_commits, False

    migrated: dict = {}
    was_migrated = False

    for old_key, value in repo_commits.items():
        new_key = make_repo_key(old_key)
        if new_key != old_key:
            was_migrated = True
            log(f"Migrating repo_commits key: {old_key} -> {new_key}")
        if new_key in migrated:
            # Collision during migration (two old absolute paths have the same
            # directory name).  Keep the one with the newer commit or the first.
            log_warn(
                f"repo_commits migration collision: both '{old_key}' and a "
                f"previous key resolve to '{new_key}'. Keeping the first."
            )
            continue
        migrated[new_key] = value

    return migrated, was_migrated


def _resolve_entries(cfg: Any) -> list:
    """Resolve SOURCE_DIRS via config_loader.resolve_source_entries().

    This is a thin wrapper that avoids a circular import by importing
    config_loader lazily.  All functions in this module that used to
    iterate ``cfg.SOURCE_DIRS`` directly should call this instead.
    """
    from config_loader import resolve_source_entries

    return resolve_source_entries(cfg)


def _get_canonical_prefix(source_dir: dict) -> str:
    """Get the canonical prefix for a source dir entry.

    Resolution order:
      1. ``map_to_path`` if present (explicit override)
      2. Last segment of ``path`` (e.g. ``../my_project/delphi_src`` → ``delphi_src``)
      3. Empty string when ``path`` is ``"."`` or ``""``

    Returns:
        Canonical prefix string (no trailing slash), or empty string for root.
    """
    map_to = source_dir.get("map_to_path")
    if map_to:
        return map_to.replace("\\", "/").rstrip("/")

    raw_path = source_dir.get("path", "").replace("\\", "/").rstrip("/")
    if not raw_path or raw_path == ".":
        return ""

    # Last segment of path: "../my_project/delphi_src" -> "delphi_src"
    return raw_path.rsplit("/", 1)[-1]


def normalize_file_key(
    source_dir_path: str, relative_posix: str, source_dir: dict | None = None
) -> str:
    """Build the canonical file key from a source directory and a relative posix path.

    This is the **single source of truth** for file path keys used in:
      - Qdrant ``file_path`` payload
      - Manifest dict keys
      - UUID generation for Qdrant point IDs
      - Delete filter matching

    When ``source_dir`` dict is provided, the canonical prefix is derived from
    ``map_to_path`` (if set) or the last segment of ``path``.  This decouples
    the key from the raw ``path`` value, so changing ``path`` from ``"source"``
    to ``"../my_project/delphi_src"`` produces the same key as long as the
    last segment (or ``map_to_path``) is unchanged.

    When ``source_dir`` is None, falls back to legacy behaviour using
    ``source_dir_path`` directly (for backward compatibility during migration).

    Examples:
        >>> normalize_file_key("source", "Common/foo.pas")
        'source/Common/foo.pas'
        >>> sd = {"path": "../my_project/delphi_src", "extensions": [".pas"]}
        >>> normalize_file_key(sd["path"], "Common/foo.pas", source_dir=sd)
        'delphi_src/Common/foo.pas'
        >>> sd = {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]}
        >>> normalize_file_key(sd["path"], "Common/foo.pas", source_dir=sd)
        'delphi_src/Common/foo.pas'
        >>> normalize_file_key(".", "config.py")
        'config.py'
    """
    if source_dir is not None:
        prefix = _get_canonical_prefix(source_dir)
    else:
        # Legacy fallback: use source_dir_path directly
        prefix = source_dir_path.replace("\\", "/").rstrip("/")
        if prefix == ".":
            prefix = ""

    relative = relative_posix.replace("\\", "/")

    if not prefix:
        raw = relative
    else:
        raw = f"{prefix}/{relative}"

    if raw.startswith("./"):
        raw = raw[2:]
    return raw


def resolve_key_to_disk_path(canonical_key: str, cfg: Any = None) -> str:
    """Resolve a canonical file key to the actual disk path for reading.

    Canonical keys use the last segment of ``path`` (or ``map_to_path``) as prefix.
    This function reverses that to find the actual ``path`` on disk.

    For example, if SOURCE_DIRS has::

        {"path": "../my_project/delphi_src", "extensions": [".pas"]}

    Then canonical key ``delphi_src/Common/foo.pas`` resolves to
    ``../my_project/delphi_src/Common/foo.pas``.

    Args:
        canonical_key: Canonical file key (e.g. ``delphi_src/Common/foo.pas``).
        cfg: Merged config object with SOURCE_DIRS. Required.

    Returns:
        The disk-relative path string.  If no SOURCE_DIR matches, returns
        the canonical_key unchanged.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )
    normalized = canonical_key.replace("\\", "/")

    for source_dir in _resolve_entries(cfg):
        prefix = _get_canonical_prefix(source_dir)
        raw_path = source_dir["path"].replace("\\", "/").rstrip("/")

        if not prefix:
            # Root dir ("." or "")  — key IS the relative path, prepend raw_path
            if raw_path and raw_path != ".":
                return f"{raw_path}/{normalized}"
            return normalized

        canon_prefix = prefix + "/"

        if normalized.startswith(canon_prefix) or normalized == prefix:
            # Strip canonical prefix, prepend actual disk path
            if normalized == prefix:
                return raw_path
            relative = normalized[len(canon_prefix) :]
            return f"{raw_path}/{relative}"

    return normalized


def map_path_to_qdrant(file_path: str, cfg: Any = None) -> str:
    """Map a local relative path to its Qdrant mapped path, if map_to_path is configured.

    .. deprecated::
        This function exists for backward compatibility during migration.
        New code should use ``normalize_file_key(source_dir=...)`` which produces
        canonical keys directly.  After migration, canonical keys ARE the Qdrant
        payload values — no further mapping needed.

    Args:
        file_path: Local relative path to map.
        cfg: Merged config object with SOURCE_DIRS. Required.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )
    normalized = file_path.replace("\\", "/")
    # Strip leading "./" if present
    if normalized.startswith("./"):
        normalized = normalized[2:]

    for source_dir in _resolve_entries(cfg):
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


def map_path_from_qdrant(mapped_path: str, cfg: Any = None) -> str:
    """Map a Qdrant mapped path back to the local relative path.

    .. deprecated::
        This function exists for backward compatibility during migration.
        New code should use ``resolve_key_to_disk_path()`` instead, which
        resolves canonical keys (= Qdrant payload values) back to disk paths.

    Args:
        mapped_path: Qdrant mapped path to reverse-map.
        cfg: Merged config object with SOURCE_DIRS. Required.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )
    normalized = mapped_path.replace("\\", "/")

    for source_dir in _resolve_entries(cfg):
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


def validate_source_dirs(cfg: Any = None) -> list[str]:
    """Validate SOURCE_DIRS for duplicate canonical prefix collisions.

    Two source dirs whose canonical prefix (from map_to_path or last path segment)
    resolves to the same string would cause key collisions.

    Args:
        cfg: Merged config object with SOURCE_DIRS. Required.

    Returns:
        List of error strings. Empty list means no issues.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )
    errors = []
    seen: dict[str, str] = {}
    for source_dir in _resolve_entries(cfg):
        prefix = _get_canonical_prefix(source_dir)
        raw_path = source_dir["path"]
        if prefix in seen:
            errors.append(
                f"SOURCE_DIRS collision: '{raw_path}' and '{seen[prefix]}' both resolve "
                f"to canonical prefix '{prefix}'. Use 'map_to_path' to disambiguate."
            )
        else:
            seen[prefix] = raw_path
    return errors


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file, normalizing CRLF to LF before hashing.

    Normalization ensures identical hashes across Windows (CRLF working copies)
    and Linux (LF working copies) for the same logical file content, making
    incremental refresh cross-platform safe when sharing a manifest between
    machines.
    """
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        content = content.replace(b"\r\n", b"\n")
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        log_warn(f"Could not hash {file_path}: {e}")
        return ""


def is_excluded(path: Path, exclude_patterns: List[str]) -> bool:
    """Check if any part of the path matches an exclude pattern.

    Supports both single-segment patterns (e.g. "__pycache__", "*.pyc") and
    multi-segment patterns (e.g. "LANGS/ENG").  Single-segment patterns are
    matched against each individual path component.  Multi-segment patterns
    are matched against sliding windows of consecutive path components joined
    with "/".
    """
    if not exclude_patterns:
        return False
    parts = path.parts
    for pattern in exclude_patterns:
        # Normalise separators so "LANGS\\ENG" is treated like "LANGS/ENG"
        normalised = pattern.replace("\\", "/")
        if "/" in normalised:
            # Multi-segment pattern — match against sliding windows
            seg_count = normalised.count("/") + 1
            for i in range(len(parts) - seg_count + 1):
                window = "/".join(parts[i : i + seg_count])
                if fnmatch.fnmatch(window, normalised):
                    return True
        else:
            # Single-segment pattern — original behaviour
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
    return False


def _is_excluded_leaf(path: Path, exclude_patterns: List[str]) -> bool:
    """``is_excluded`` for a path whose parent is known not to be excluded.

    Every window over the parent's parts was already checked (and did not
    match), so only the last part and the multi-segment windows that end at
    the last part can still match. Gives the same answer as ``is_excluded``
    under that precondition, at a fraction of the cost on deep trees.
    """
    parts = path.parts
    last = len(parts)
    for pattern in exclude_patterns:
        normalised = pattern.replace("\\", "/")
        if "/" in normalised:
            seg_count = normalised.count("/") + 1
            if last >= seg_count:
                window = "/".join(parts[last - seg_count : last])
                if fnmatch.fnmatch(window, normalised):
                    return True
        elif parts and fnmatch.fnmatch(parts[-1], pattern):
            return True
    return False


# Path.rglob walks with a stack since Python 3.13 (last subdirectory first);
# 3.12 and older walk depth-first in directory order.
_RGLOB_LAST_SUBDIR_FIRST = sys.version_info >= (3, 13)


def _name_matchers(extensions: List[str]) -> List[Any]:
    """Compile one ``*<ext>`` name matcher per extension, like ``rglob``.

    Case sensitivity follows the platform, as ``Path.rglob`` does by
    default: case-insensitive on Windows, case-sensitive on POSIX.
    """
    flags = 0 if os.path.normcase("Aa") == "Aa" else re.IGNORECASE
    return [re.compile(fnmatch.translate(f"*{ext}"), flags).match for ext in extensions]


def find_source_files(
    dir_path: Path, extensions: List[str], exclude_patterns: List[str]
) -> List[Path]:
    """Files under ``dir_path`` with one of ``extensions``, minus excludes.

    Same result, in the same order, as the classic scan::

        for ext in extensions:
            for f in dir_path.rglob(f"*{ext}"):
                if not is_excluded(f, exclude_patterns) and f.is_file():
                    yield f

    but walks the tree once instead of once per extension, and skips
    excluded directories instead of listing and rejecting every file under
    them. Details kept from ``rglob``:

    * order: grouped by extension in ``extensions`` order; inside a group,
      the directory order of ``rglob`` on the running Python (a directory's
      files are listed when its parent is visited; Python 3.13+ then descends
      into the last subdirectory first, older versions into the first) and
      ``os.scandir`` order inside a directory;
    * a file whose name matches several extensions is listed once per
      matching extension, as before;
    * symlinked directories are not descended into; symlinks to files are
      kept, broken symlinks are dropped (``is_file`` follows symlinks);
    * extension matching is case-insensitive on Windows only;
    * a missing or unreadable ``dir_path`` yields no files.
    """
    dir_path = Path(dir_path)
    patterns = list(exclude_patterns or [])
    matchers = _name_matchers(list(extensions))
    buckets: List[List[Path]] = [[] for _ in matchers]
    if not matchers or (patterns and is_excluded(dir_path, patterns)):
        return []

    def _list(path: str) -> List[Any]:
        try:
            with os.scandir(path) as it:
                return list(it)
        except OSError:
            return []

    def _collect(entries: List[Any]) -> List[str]:
        subdirs: List[str] = []
        for entry in entries:
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                is_dir = False
            if is_dir:
                subdirs.append(entry.path)
                continue
            hits = [i for i, m in enumerate(matchers) if m(entry.name)]
            if not hits:
                continue
            f = Path(entry.path)
            if patterns and _is_excluded_leaf(f, patterns):
                continue
            try:
                if not entry.is_file():
                    continue
            except OSError:
                continue
            for i in hits:
                buckets[i].append(f)
        return subdirs

    root = str(dir_path)
    stack = [(root, _collect(_list(root)))]
    while stack:
        _, subdirs = stack.pop()
        children = [
            (sub, _collect(_list(sub)))
            for sub in subdirs
            if not (patterns and _is_excluded_leaf(Path(sub), patterns))
        ]
        # Which subdirectory is descended into first follows the running
        # Python's rglob: the last one found on 3.13+, the first one before.
        stack.extend(children if _RGLOB_LAST_SUBDIR_FIRST else reversed(children))
    return [f for bucket in buckets for f in bucket]




def filter_out_gitignored(
    files: List[Path],
    source_dir: dict,
    *,
    respect_gitignore: bool = True,
) -> List[Path]:
    """Drop files that git would ignore for ``git_repo`` sources.

    Non-git sources are unchanged. When ``respect_gitignore`` is false, the
    input list is returned as-is. Tracked-but-matching-gitignore files stay
    (git check-ignore does not report tracked paths).

    Args:
        files: Candidate files under ``source_dir["path"]``.
        source_dir: Resolved SOURCE_DIRS entry (needs ``_entry_type`` and
            ``_repo_path`` for git repos).
        respect_gitignore: Master switch from config ``RESPECT_GITIGNORE``.

    Returns:
        Filtered list preserving original order.
    """
    if not respect_gitignore or not files:
        return files
    if source_dir.get("_entry_type") != "git_repo":
        return files
    repo_path = source_dir.get("_repo_path")
    if not repo_path:
        return files

    from shared.git_ops import check_ignored_paths

    repo_root = Path(repo_path)
    try:
        repo_resolved = repo_root.resolve()
    except OSError:
        repo_resolved = repo_root

    rel_paths: List[str] = []
    for f in files:
        try:
            rel = f.resolve().relative_to(repo_resolved).as_posix()
        except (ValueError, OSError):
            continue
        rel_paths.append(rel)

    ignored = check_ignored_paths(str(repo_path), rel_paths)
    if not ignored:
        return files

    out: List[Path] = []
    for f in files:
        try:
            rel = f.resolve().relative_to(repo_resolved).as_posix()
        except (ValueError, OSError):
            out.append(f)
            continue
        if rel not in ignored:
            out.append(f)
    return out

def get_source_files(cfg: Any = None) -> List[Path]:
    """Get all source files that should be indexed, driven by cfg.SOURCE_DIRS.

    Args:
        cfg: Merged config object with SOURCE_DIRS. Required.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )
    files = []
    for source_dir in _resolve_entries(cfg):
        dir_path = Path(source_dir["path"])
        if not dir_path.exists():
            continue
        exclude_patterns = source_dir.get("exclude", [])
        found = find_source_files(dir_path, source_dir["extensions"], exclude_patterns)
        respect = bool(getattr(cfg, "RESPECT_GITIGNORE", True))
        files.extend(filter_out_gitignored(found, source_dir, respect_gitignore=respect))
    return sorted(files)
