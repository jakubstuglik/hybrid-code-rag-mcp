"""Git overlay selection shared by the indexer and tests.

A branch overlay keeps the three-dot diff (commits on the branch since it
left main). A tag overlay compares the tag's tree to the main tip. Both
store points under the overlay name. Point ids and manifest file names stay
on the existing branch-overlay scheme.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from shared import git_ops
from shared.git_ops import (
    GitError,
    branch_exists,
    diff_against_main_tip,
    diff_branches,
    get_branch_head,
    get_merge_base,
    resolve_to_commit,
)
from shared.manifest import is_excluded, normalize_file_key
from shared.sql_dialect import sql_dialect_changed

DIFF_MERGE_BASE = "merge_base"
DIFF_AGAINST_MAIN_TIP = "against_main_tip"


def make_overlay_point_id(label: str, file_key: str, index: int) -> str:
    """Deterministic point id for one overlay label.

    The ``{label}::`` prefix is the same string ``make_branch_point_id``
    has always used, so existing branch points keep their ids.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{label}::{file_key}:{index}"))


def overlay_manifest_filename(label: str) -> str:
    """Manifest file name for an overlay label.

    Branch and tag overlays share this pattern:
    ``index_manifest_branch_<sanitized name>.json``.
    """
    # Look up through the module so callers that patch
    # shared.git_ops.sanitize_branch_name still apply.
    return f"index_manifest_branch_{git_ops.sanitize_branch_name(label)}.json"


def configured_overlays(group: dict) -> list[dict]:
    """Overlay specs for a repo group.

    Groups built before overlays existed only have ``branches``. Those names
    are kind ``branch`` with the merge-base diff.
    """
    overlays = group.get("overlays")
    if overlays is None:
        return [
            {"name": name, "kind": "branch", "diff": DIFF_MERGE_BASE}
            for name in (group.get("branches") or [])
        ]
    return list(overlays)


def skip_when_diff_empty(kind: str) -> bool:
    """Whether an empty diff should leave stored overlay points in place.

    Branch indexing has always skipped the run when the three-dot diff is
    empty. A tag overlay's empty diff means the tag tree matches main, so
    every path still in the manifest is a delete.
    """
    return kind != "tag"


@dataclass
class OverlayDiff:
    """Result of resolving one overlay ref and diffing it against main."""

    changes: list[tuple[str, str]]
    read_at: str
    resolved_commit: str
    merge_base: Optional[str]
    kind: str


def diff_overlay(
    repo_path: str,
    main_branch: str,
    spec: dict,
    paths: Optional[list[str]] = None,
) -> Optional[OverlayDiff]:
    """Diff one overlay. Returns None when the name is not a branch or tag.

    ``read_at`` is what ``read_files_to_temp_dir`` should pass to ``git show``.
    Branches pass the branch name. Tags pass the peeled commit so an annotated
    tag and a lightweight tag read the same tree, and the read does not follow
    the working copy.
    """
    name = spec["name"]
    kind = spec["kind"]
    if not branch_exists(repo_path, name):
        return None

    if kind == "branch":
        merge_base = get_merge_base(repo_path, main_branch, name)
        changes = diff_branches(repo_path, main_branch, name, paths=paths)
        resolved = get_branch_head(repo_path, name)
        return OverlayDiff(
            changes=changes,
            read_at=name,
            resolved_commit=resolved,
            merge_base=merge_base,
            kind=kind,
        )

    if kind == "tag":
        if spec.get("diff") not in (None, DIFF_AGAINST_MAIN_TIP):
            raise GitError(
                f"Tag overlay '{name}' requires diff {DIFF_AGAINST_MAIN_TIP!r}"
            )
        resolved = resolve_to_commit(repo_path, name)
        changes = diff_against_main_tip(repo_path, main_branch, name, paths=paths)
        return OverlayDiff(
            changes=changes,
            read_at=resolved,
            resolved_commit=resolved,
            merge_base=None,
            kind=kind,
        )

    raise GitError(f"Unknown overlay kind {kind!r} for '{name}'")


def manifest_progress_fields(
    *,
    kind: str,
    merge_base: Optional[str],
    branch_head: Optional[str],
    resolved_commit: Optional[str],
) -> dict:
    """Manifest keys written after an overlay run.

    Branch overlays keep ``merge_base`` and ``last_branch_commit`` and do not
    gain ``last_resolved_commit``. Tag overlays record the peeled commit in
    ``last_resolved_commit``.
    """
    if kind == "branch":
        fields: dict = {"merge_base": merge_base}
        if branch_head is not None:
            fields["last_branch_commit"] = branch_head
        return fields
    return {"last_resolved_commit": resolved_commit}


def reconcile_overlay_actions(old_files: dict, new_states: dict) -> dict:
    """Hash-compare an overlay manifest to the files still in the diff.

    Paths present in ``old_files`` and absent from ``new_states`` are deletes.
    That is how a tag move drops points whose content now matches main.
    SQL dialect changes still count as modifications, matching main-branch
    change detection when the file hash is unchanged.
    """
    actions: dict[str, list] = {"add": [], "modify": [], "delete": []}
    for path_key, current in new_states.items():
        if path_key not in old_files:
            actions["add"].append(path_key)
            continue
        old_entry = old_files[path_key]
        hash_changed = current.get("hash") != old_entry.get("hash", "")
        if hash_changed or sql_dialect_changed(old_entry, current):
            actions["modify"].append(path_key)
    for path_key in old_files:
        if path_key not in new_states:
            actions["delete"].append(path_key)
    return actions


def collect_vector_ids(old_files: dict, keys: list) -> list[str]:
    """Point ids stored on manifest entries for ``keys``, in key order."""
    ids: list[str] = []
    for key in keys:
        entry = old_files.get(key) or {}
        ids.extend(entry.get("vector_ids") or [])
    return ids


def delete_point_ids(client, collection_name: str, point_ids: list) -> None:
    """Delete overlay points by id. An empty list is a no-op."""
    if not point_ids:
        return
    from qdrant_client import models

    client.delete(
        collection_name=collection_name,
        points_selector=models.PointIdsList(points=list(point_ids)),
    )


def map_git_path_to_file_key(git_path: str, group: dict) -> tuple[str, dict] | None:
    """Map a git-relative path to ``(file_key, resolved_entry)``.

    Returns None when the path is outside the group's sources, the extension
    is not configured, or an exclude pattern matches.
    """
    git_normalized = git_path.replace("\\", "/")

    for entry in group["resolved_entries"]:
        git_prefix = entry["_git_prefix"]
        if not git_prefix or git_prefix == ".":
            relative_posix = git_normalized
        else:
            prefix = git_prefix.replace("\\", "/").rstrip("/") + "/"
            if not git_normalized.startswith(prefix):
                continue
            relative_posix = git_normalized[len(prefix) :]

        ext = "." + git_normalized.rsplit(".", 1)[-1] if "." in git_normalized else ""
        configured_exts = {item.lower() for item in entry.get("extensions", [])}
        if ext.lower() not in configured_exts:
            continue

        full_disk_path = Path(entry["path"]) / relative_posix
        exclude_patterns = entry.get("exclude", [])
        if is_excluded(full_disk_path, exclude_patterns):
            continue

        file_key = normalize_file_key(entry["path"], relative_posix, source_dir=entry)
        return file_key, entry

    return None
