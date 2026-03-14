from typing import Any, Dict, List, Tuple
from pathlib import Path
from collections import defaultdict

from llama_index.core.schema import TextNode

from shared.log import log, log_raw
from shared.readers import get_reader
from shared.manifest import compute_file_hash, is_excluded, normalize_file_key


def load_all_sources(cfg: Any = None) -> Tuple[List[TextNode], Dict[str, dict]]:
    """Load all source files and return nodes with consistent path metadata.

    Iterates over cfg.SOURCE_DIRS, finds files matching each configured
    extension, and uses the reader registry to parse them.  Every node's
    ``file_path`` metadata is normalised to the canonical key format using
    the last segment of ``path`` (or ``map_to_path``) as prefix
    (e.g. ``delphi_src/Common/foo.pas``).

    Args:
        cfg: Merged config object with SOURCE_DIRS. Required.

    Returns:
        Tuple of:
          - all_nodes: flat list of TextNodes ready for indexing
          - file_states: dict keyed by canonical path with mtime/hash/full_path
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )
    all_nodes: List[TextNode] = []
    file_states: Dict[str, dict] = {}
    step_count = len(cfg.SOURCE_DIRS) + 1

    ext_file_counts: Dict[str, int] = defaultdict(int)
    ext_node_counts: Dict[str, int] = defaultdict(int)

    for idx, source_dir in enumerate(cfg.SOURCE_DIRS, start=1):
        dir_path = Path(source_dir["path"])
        extensions = source_dir["extensions"]
        exclude_patterns = source_dir.get("exclude", [])
        ext_label = ", ".join(extensions)
        log(f"[{idx}/{step_count}] Loading files from {dir_path}/ ({ext_label})...")

        files: List[Path] = []
        for ext in extensions:
            for f in dir_path.rglob(f"*{ext}"):
                if f.is_file() and not is_excluded(f, exclude_patterns):
                    files.append(f)
        log(f"      Found {len(files)} files")

        dir_nodes: List[TextNode] = []
        for f in files:
            reader = get_reader(f.suffix)
            if reader is None:
                continue

            # Canonical path key via shared normalization
            relative_posix = f.relative_to(dir_path).as_posix()
            path_key = normalize_file_key(
                source_dir["path"], relative_posix, source_dir=source_dir
            )

            nodes = reader.load_nodes(f)

            # Normalise file_path metadata on every node
            for node in nodes:
                node.metadata["file_path"] = path_key

            dir_nodes.extend(nodes)

            ext = f.suffix.lower()
            ext_file_counts[ext] += 1
            ext_node_counts[ext] += len(nodes)

            # Collect file state for manifest building
            try:
                file_states[path_key] = {
                    "file_path": path_key,
                    "full_path": str(f),
                    "mtime": int(f.stat().st_mtime),
                    "hash": compute_file_hash(f),
                }
            except Exception:
                pass

        log(f"      Created {len(dir_nodes)} nodes")
        all_nodes.extend(dir_nodes)

    # Summary: per-extension breakdown
    log(f"[{step_count}/{step_count}] Source loading complete")
    log_raw(f"      Total files: {sum(ext_file_counts.values())}")
    log_raw(f"      Total nodes: {len(all_nodes)}")
    for ext in sorted(ext_file_counts):
        log_raw(
            f"        {ext}: {ext_file_counts[ext]} files, {ext_node_counts[ext]} nodes"
        )

    return all_nodes, file_states
