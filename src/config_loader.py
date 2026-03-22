import os
import sys
import types
from pathlib import Path
from typing import Any, List
from importlib.util import spec_from_file_location, module_from_spec

from shared.log import log_warn, log_error
from shared.manifest import make_repo_key


def get_config(config_path: str = None, config_name: str = None) -> types.ModuleType:
    """Load config with optional override.

    Args:
        config_path: Full path to config file (e.g., "./self-index/config.py")
        config_name: Just the name, assumes "./{name}/config.py" (e.g., "self-index")

    Priority: config_path > config_name > env var RAG_CONFIG
    """
    base_config = __import__("config")

    override_path = None
    if config_path:
        p = Path(config_path)
        if p.suffix == ".py":
            # Explicit .py file path — use directly
            override_path = p
        elif p.is_dir():
            # Directory — look for config.py inside it
            override_path = p / "config.py"
        else:
            # Name without extension (e.g. "self-index", "config_informica", "test-sources")
            # Search order:
            #   1. {name}/config.py          (e.g. self-index/config.py)
            #   2. project-configs/{name}/config.py  (private, gitignored)
            #   3. {name}.py                 (legacy root-level .py)
            dir_path = p / "config.py"
            project_path = Path("project-configs") / p / "config.py"
            file_path = p.with_suffix(".py")
            if dir_path.exists():
                override_path = dir_path
            elif project_path.exists():
                override_path = project_path
            elif file_path.exists():
                override_path = file_path
            else:
                override_path = dir_path  # Fall through to "not found" below
    elif config_name:
        p = Path(config_name)
        dir_path = p / "config.py"
        project_path = Path("project-configs") / p / "config.py"
        file_path = p.with_suffix(".py")
        if dir_path.exists():
            override_path = dir_path
        elif project_path.exists():
            override_path = project_path
        elif file_path.exists():
            override_path = file_path
        else:
            override_path = dir_path  # Fall through to "not found" below
    elif os.getenv("RAG_CONFIG"):
        env_val = os.getenv("RAG_CONFIG", "")
        env_p = Path(env_val)
        dir_path = env_p / "config.py"
        project_path = Path("project-configs") / env_p / "config.py"
        file_path = env_p.with_suffix(".py")
        if dir_path.exists():
            override_path = dir_path
        elif project_path.exists():
            override_path = project_path
        elif file_path.exists():
            override_path = file_path
        else:
            override_path = dir_path

    if override_path and not override_path.exists():
        # A config name/path was requested but the file was not found.
        # Silently falling back to base config.py would be dangerous: config.py
        # alone has no SOURCE_DIRS or COLLECTION_NAME and is not designed to run
        # standalone.  Raise a clear error so the user can fix the typo.
        raise RuntimeError(
            f"[config_loader] Project config not found: {override_path}\n"
            f"  Searched for: '{override_path}'\n"
            f"  Check the --config name for typos (use underscores, not dashes, etc.).\n"
            f"  Expected locations:\n"
            f"    {Path(config_path or config_name or '') / 'config.py'}\n"
            f"    project-configs/{config_path or config_name or ''}/config.py"
        )

    if override_path and override_path.exists():
        spec = spec_from_file_location("config_override", override_path)
        if spec is None or spec.loader is None:
            log_warn(f"[config_loader] Could not load config from {override_path}")
            return base_config

        override_mod = module_from_spec(spec)
        try:
            spec.loader.exec_module(override_mod)
        except Exception as e:
            log_warn(f"[config_loader] Error loading {override_path}: {e}")
            return base_config

        merged = types.ModuleType("config")
        merged.__dict__.update(base_config.__dict__)
        merged.__dict__.update(override_mod.__dict__)

        # Auto-set BASE_PATH based on override config location if not explicitly defined
        if "BASE_PATH" not in override_mod.__dict__:
            config_dir = override_path.parent.resolve()
            merged.__dict__["BASE_PATH"] = str(config_dir / "qdrant")

        # Rebind functions so they see the merged module's globals
        # (e.g. get_index_path() needs to read the overridden BASE_PATH)
        for key, value in list(merged.__dict__.items()):
            if isinstance(value, types.FunctionType):
                merged.__dict__[key] = types.FunctionType(
                    value.__code__,
                    merged.__dict__,
                    value.__name__,
                    value.__defaults__,
                    value.__closure__,
                )

        _validate_config(merged, override_path)
        return merged

    # No --config / config_name / RAG_CONFIG was given at all.
    # config.py is the common system defaults layer only — it has no SOURCE_DIRS,
    # COLLECTION_NAME, or Qdrant connection.  Running it standalone would produce
    # confusing errors downstream.  Fail hard so the user knows what is missing.
    raise RuntimeError(
        "[config_loader] No project config specified.\n"
        "  Pass --config <name> (e.g. --config self-index) or set the RAG_CONFIG "
        "environment variable.\n"
        "  config.py is the common system defaults layer and cannot be used standalone."
    )


def _validate_config(cfg: types.ModuleType, source_path) -> None:
    """Validate the merged config for removed/renamed settings.

    Raises RuntimeError for fatal configuration errors.
    """
    # ── QDRANT_USE_DOCKER removed (replaced by QDRANT_MODE) ─────
    if hasattr(cfg, "QDRANT_USE_DOCKER"):
        source = f" (in {source_path})" if source_path else ""
        raise RuntimeError(
            f"QDRANT_USE_DOCKER has been removed{source}. "
            f"Replace with QDRANT_MODE = 'local' (Docker container) "
            f"or QDRANT_MODE = 'remote' (remote server). "
            f"See config.py for documentation."
        )

    # ── QDRANT_MODE must be valid ────────────────────────────────
    mode = getattr(cfg, "QDRANT_MODE", None)
    if mode not in ("local", "remote"):
        raise RuntimeError(
            f"QDRANT_MODE must be 'local' or 'remote', got {mode!r}. "
            f"See config.py for documentation."
        )

    # ── Validate SOURCE_DIRS entry types ─────────────────────────
    _validate_source_dirs_entries(cfg, source_path)


def _validate_source_dirs_entries(cfg: types.ModuleType, source_path) -> None:
    """Validate SOURCE_DIRS entries: type field, git_repo uniqueness, required fields.

    Raises RuntimeError for fatal configuration errors.
    """
    source_dirs = getattr(cfg, "SOURCE_DIRS", [])
    if not source_dirs:
        return

    git_repo_paths: dict[str, int] = {}  # normalized path -> entry index

    for idx, entry in enumerate(source_dirs):
        entry_type = entry.get("type")

        if entry_type == "git_repo":
            # Required fields
            if "path" not in entry:
                source = f" (in {source_path})" if source_path else ""
                raise RuntimeError(
                    f"SOURCE_DIRS[{idx}]: git_repo entry missing 'path'{source}."
                )
            if "sources" not in entry or not entry["sources"]:
                source = f" (in {source_path})" if source_path else ""
                raise RuntimeError(
                    f"SOURCE_DIRS[{idx}]: git_repo entry missing 'sources' list{source}."
                )

            # Validate each source within the git_repo
            for src_idx, src in enumerate(entry["sources"]):
                if "path" not in src:
                    source = f" (in {source_path})" if source_path else ""
                    raise RuntimeError(
                        f"SOURCE_DIRS[{idx}].sources[{src_idx}]: "
                        f"missing 'path'{source}."
                    )
                if "extensions" not in src:
                    source = f" (in {source_path})" if source_path else ""
                    raise RuntimeError(
                        f"SOURCE_DIRS[{idx}].sources[{src_idx}]: "
                        f"missing 'extensions'{source}."
                    )

            # Check for duplicate git_repo paths
            repo_path = Path(entry["path"]).resolve().as_posix()
            if repo_path in git_repo_paths:
                other_idx = git_repo_paths[repo_path]
                source = f" (in {source_path})" if source_path else ""
                raise RuntimeError(
                    f"SOURCE_DIRS[{idx}] and SOURCE_DIRS[{other_idx}] both point to "
                    f"git repo '{entry['path']}'{source}. "
                    f"Duplicate git_repo entries for the same path are not allowed. "
                    f"Combine sources into a single git_repo entry."
                )
            git_repo_paths[repo_path] = idx

        elif entry_type == "source_set":
            # Same validation as legacy flat format
            if "path" not in entry:
                source = f" (in {source_path})" if source_path else ""
                raise RuntimeError(
                    f"SOURCE_DIRS[{idx}]: source_set entry missing 'path'{source}."
                )
            if "extensions" not in entry:
                source = f" (in {source_path})" if source_path else ""
                raise RuntimeError(
                    f"SOURCE_DIRS[{idx}]: source_set entry missing 'extensions'{source}."
                )

        elif entry_type is None:
            # Legacy flat format — validate basic fields
            if "path" not in entry:
                source = f" (in {source_path})" if source_path else ""
                raise RuntimeError(f"SOURCE_DIRS[{idx}]: entry missing 'path'{source}.")
            if "extensions" not in entry:
                source = f" (in {source_path})" if source_path else ""
                raise RuntimeError(
                    f"SOURCE_DIRS[{idx}]: entry missing 'extensions'{source}."
                )

        else:
            source = f" (in {source_path})" if source_path else ""
            raise RuntimeError(
                f"SOURCE_DIRS[{idx}]: unknown type '{entry_type}'{source}. "
                f"Must be 'git_repo', 'source_set', or omitted (legacy)."
            )


def resolve_source_entries(cfg: Any) -> List[dict]:
    """Resolve SOURCE_DIRS into a flat list of normalized source entries.

    This is the central normalization function. Every downstream consumer
    (manifest.py, indexing.py, index_rag.py) should use this resolved list
    instead of iterating cfg.SOURCE_DIRS directly.

    Each resolved entry is a dict with:
        path        - Absolute or relative path to the source directory on disk.
        extensions  - List of file extensions.
        exclude     - List of exclude patterns (may be empty).
        map_to_path - Optional canonical prefix override.
        _entry_type - "git_repo" | "source_set" | "legacy"
        _repo_path  - Path to git repo root (only for git_repo entries, else None).
        _main_branch   - Main branch name (only for git_repo, else None).
        _branches      - List of feature branch names (only for git_repo, else []).
        _diff_threshold - Diff full reindex threshold (only for git_repo, else None).

    Legacy flat entries and source_set entries are passed through with disk
    path unchanged. git_repo entries are expanded: each source within the
    git_repo becomes a separate resolved entry with path = repo_path/source_path.

    Args:
        cfg: Merged config module with SOURCE_DIRS.

    Returns:
        List of resolved source entry dicts.
    """
    source_dirs = getattr(cfg, "SOURCE_DIRS", [])
    global_threshold = getattr(cfg, "DIFF_FULL_REINDEX_THRESHOLD", 0.5)
    resolved = []

    for entry in source_dirs:
        entry_type = entry.get("type")

        if entry_type == "git_repo":
            repo_path = entry["path"]
            main_branch = entry.get("main_branch", "master")
            branches = entry.get("branches", [])
            threshold = entry.get("diff_full_reindex_threshold", global_threshold)

            for src in entry["sources"]:
                # Build the full disk path: repo_path / source_path
                src_path = src["path"]
                repo_normalized = repo_path.replace("\\", "/").rstrip("/")
                src_normalized = src_path.replace("\\", "/").strip("/")

                if not src_normalized or src_normalized == ".":
                    disk_path = repo_normalized if repo_normalized else "."
                else:
                    if repo_normalized and repo_normalized != ".":
                        disk_path = f"{repo_normalized}/{src_normalized}"
                    else:
                        disk_path = src_normalized

                resolved_entry = {
                    "path": disk_path,
                    "extensions": src["extensions"],
                    "exclude": src.get("exclude", []),
                    "_entry_type": "git_repo",
                    "_repo_path": repo_path,
                    "_git_prefix": src_normalized,
                    "_main_branch": main_branch,
                    "_branches": list(branches),
                    "_diff_threshold": threshold,
                }
                if "map_to_path" in src:
                    resolved_entry["map_to_path"] = src["map_to_path"]

                resolved.append(resolved_entry)

        elif entry_type == "source_set":
            resolved.append(
                {
                    "path": entry["path"],
                    "extensions": entry["extensions"],
                    "exclude": entry.get("exclude", []),
                    "_entry_type": "source_set",
                    "_repo_path": None,
                    "_git_prefix": None,
                    "_main_branch": None,
                    "_branches": [],
                    "_diff_threshold": None,
                    **(
                        {"map_to_path": entry["map_to_path"]}
                        if "map_to_path" in entry
                        else {}
                    ),
                }
            )

        else:
            # Legacy flat format — treat as source_set
            resolved.append(
                {
                    "path": entry["path"],
                    "extensions": entry["extensions"],
                    "exclude": entry.get("exclude", []),
                    "_entry_type": "legacy",
                    "_repo_path": None,
                    "_git_prefix": None,
                    "_main_branch": None,
                    "_branches": [],
                    "_diff_threshold": None,
                    **(
                        {"map_to_path": entry["map_to_path"]}
                        if "map_to_path" in entry
                        else {}
                    ),
                }
            )

    return resolved


def get_repo_groups(cfg: Any) -> List[dict]:
    """Extract unique git repo groups from config.

    Returns a list of repo group dicts, each with:
        repo_path      - Path to git repo root.
        main_branch    - Main branch name.
        branches       - List of feature branch names.
        diff_threshold - Diff full reindex threshold.
        git_prefixes   - List of git-relative source paths within the repo.
        resolved_entries - List of resolved source entries belonging to this group.
    """
    source_dirs = getattr(cfg, "SOURCE_DIRS", [])
    global_threshold = getattr(cfg, "DIFF_FULL_REINDEX_THRESHOLD", 0.5)
    groups: dict[str, dict] = {}  # keyed by repo directory name
    seen_paths: dict[
        str, str
    ] = {}  # repo_key -> resolved absolute path (collision check)

    resolved = resolve_source_entries(cfg)

    for entry in resolved:
        if entry["_entry_type"] != "git_repo":
            continue

        repo_key = make_repo_key(entry["_repo_path"])
        resolved_path = Path(entry["_repo_path"]).resolve().as_posix()

        # Collision check: two different repos with the same directory name
        if repo_key in seen_paths and seen_paths[repo_key] != resolved_path:
            raise RuntimeError(
                f"Repo key collision: '{entry['_repo_path']}' and another repo "
                f"both resolve to repo_key '{repo_key}'. "
                f"Repos must have unique directory names for portable manifest keys."
            )
        seen_paths[repo_key] = resolved_path

        if repo_key not in groups:
            groups[repo_key] = {
                "repo_path": entry["_repo_path"],
                "main_branch": entry["_main_branch"],
                "branches": list(entry["_branches"]),
                "diff_threshold": entry["_diff_threshold"],
                "git_prefixes": [],
                "resolved_entries": [],
            }

        git_prefix = entry.get("_git_prefix", "")
        if git_prefix and git_prefix not in groups[repo_key]["git_prefixes"]:
            groups[repo_key]["git_prefixes"].append(git_prefix)
        groups[repo_key]["resolved_entries"].append(entry)

    return list(groups.values())
