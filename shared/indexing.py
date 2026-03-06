from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict

from llama_index.core.schema import TextNode

import config
from shared.readers import get_reader
from shared.manifest import compute_file_hash, is_excluded, normalize_file_key


def load_all_sources() -> Tuple[List[TextNode], Dict[str, dict]]:
    """Load all source files and return nodes with consistent path metadata.

    Iterates over config.SOURCE_DIRS, finds files matching each configured
    extension, and uses the reader registry to parse them.  Every node's
    ``file_path`` metadata is normalised to the canonical
    ``{source_dir_path}/{posix_relative}`` format (e.g. ``source/Common/foo.pas``).

    Returns:
        Tuple of:
          - all_nodes: flat list of TextNodes ready for indexing
          - file_states: dict keyed by canonical path with mtime/hash/full_path
    """
    all_nodes: List[TextNode] = []
    file_states: Dict[str, dict] = {}
    step_count = len(config.SOURCE_DIRS) + 1

    ext_file_counts: Dict[str, int] = defaultdict(int)
    ext_node_counts: Dict[str, int] = defaultdict(int)

    for idx, source_dir in enumerate(config.SOURCE_DIRS, start=1):
        dir_path = Path(source_dir["path"])
        extensions = source_dir["extensions"]
        exclude_patterns = source_dir.get("exclude", [])
        ext_label = ", ".join(extensions)
        print(f"\n[{idx}/{step_count}] Loading files from {dir_path}/ ({ext_label})...")

        files: List[Path] = []
        for ext in extensions:
            for f in dir_path.rglob(f"*{ext}"):
                if f.is_file() and not is_excluded(f, exclude_patterns):
                    files.append(f)
        print(f"      Found {len(files)} files")

        dir_nodes: List[TextNode] = []
        for f in files:
            reader = get_reader(f.suffix)
            if reader is None:
                continue

            # Canonical path key via shared normalization
            relative_posix = f.relative_to(dir_path).as_posix()
            path_key = normalize_file_key(source_dir["path"], relative_posix)

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

        print(f"      Created {len(dir_nodes)} nodes")
        all_nodes.extend(dir_nodes)

    # Summary: per-extension breakdown
    print(f"\n[{step_count}/{step_count}] Source loading complete")
    print(f"      Total files: {sum(ext_file_counts.values())}")
    print(f"      Total nodes: {len(all_nodes)}")
    for ext in sorted(ext_file_counts):
        print(f"        {ext}: {ext_file_counts[ext]} files, {ext_node_counts[ext]} nodes")

    return all_nodes, file_states
