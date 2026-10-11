"""Moving git tag as an overlay.

Tests build throwaway git repos. They do not need a GPU, TEI, or network.
Qdrant runs in-process (`:memory:`) only to check point deletes and filters.
"""

from __future__ import annotations

import types
import uuid
from pathlib import Path
from unittest.mock import MagicMock

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from config_loader import get_repo_groups
from shared.branch_dedup import (
    BRANCH_PARAMETER_DESCRIPTION,
    build_branch_filter,
    dedup_branch_results,
    get_branch_tombstones,
)
from shared.git_ops import (
    branch_exists,
    diff_against_main_tip,
    diff_branches,
    read_files_to_temp_dir,
    resolve_to_commit,
)
from shared.manifest import compute_file_hash
from shared.overlay import (
    collect_vector_ids,
    delete_point_ids,
    diff_overlay,
    make_overlay_point_id,
    manifest_progress_fields,
    map_git_path_to_file_key,
    overlay_manifest_filename,
    reconcile_overlay_actions,
    skip_when_diff_empty,
)
from shared.readers import load_nodes_for_file
from tests.repo_util import commit_files, git, git_out, head, init_repo, worktree_count, write_files

PY_BODY = 'def release_marker():\n    return "from-overlay"\n'
PY_V1 = 'def release_marker():\n    return "v1"\n'
PY_V2 = 'def release_marker():\n    return "v2"\n'
PY_BASE = 'def release_marker():\n    return "base"\n'


def _group(repo: Path, **extra):
    entry = {
        "type": "git_repo",
        "path": str(repo),
        "main_branch": "main",
        "sources": [{"path": "src", "extensions": [".py", ".png"]}],
    }
    entry.update(extra)
    cfg = types.SimpleNamespace(
        SOURCE_DIRS=[entry],
        DIFF_FULL_REINDEX_THRESHOLD=0.5,
    )
    return get_repo_groups(cfg)[0]


def _spec(group, name: str) -> dict:
    for item in group["overlays"]:
        if item["name"] == name:
            return item
    raise AssertionError(name)


def _states(repo: Path, group: dict, spec: dict):
    diff = diff_overlay(
        str(repo),
        "main",
        spec,
        paths=group.get("git_prefixes") or None,
    )
    assert diff is not None
    index_paths = [path for status, path in diff.changes if status != "D"]
    deleted_paths = [path for status, path in diff.changes if status == "D"]
    states = {}
    tombstones = []
    temp = None
    try:
        readable = []
        for path in index_paths:
            mapping = map_git_path_to_file_key(path, group)
            if mapping is None:
                continue
            readable.append((path, mapping[0]))
        if readable:
            temp = read_files_to_temp_dir(
                str(repo), diff.read_at, [path for path, _key in readable]
            )
            for path, key in readable:
                full = Path(temp) / path
                states[key] = {
                    "file_path": key,
                    "full_path": str(full),
                    "mtime": 0,
                    "hash": compute_file_hash(full),
                }
        for path in deleted_paths:
            mapping = map_git_path_to_file_key(path, group)
            if mapping is not None:
                tombstones.append(mapping[0])
    finally:
        if temp:
            import shutil

            shutil.rmtree(temp, ignore_errors=True)
    return diff, states, sorted(tombstones)


def _manifest_from_states(label: str, states: dict) -> dict:
    files = {}
    for key, state in states.items():
        files[key] = {
            "file_path": key,
            "hash": state["hash"],
            "mtime": 0,
            "vector_ids": [make_overlay_point_id(label, key, 0)],
        }
    return files


def _memory_collection():
    client = QdrantClient(":memory:")
    client.create_collection(
        collection_name="overlay",
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )
    return client


def _point(label: str, file_key: str, slot: int = 0) -> PointStruct:
    return PointStruct(
        id=make_overlay_point_id(label, file_key, slot),
        vector=[0.1, 0.2, 0.3, 0.4],
        payload={"branch": label, "file_path": file_key},
    )


def _labels(client, query_label: str | None) -> set[str]:
    filt = build_branch_filter("main", query_label)
    points, _offset = client.scroll(
        collection_name="overlay",
        scroll_filter=filt,
        limit=20,
        with_payload=True,
    )
    return {point.payload["branch"] for point in points}


class TestPointIdentity:
    def test_point_id_formula_is_unchanged_for_branch_labels(self):
        label = "feature/example"
        file_key = "src/app.py"
        expected = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{label}::{file_key}:0"))
        assert make_overlay_point_id(label, file_key, 0) == expected

    def test_manifest_filename_stays_on_the_branch_pattern(self):
        assert (
            overlay_manifest_filename("feature/example")
            == "index_manifest_branch_feature_example.json"
        )
        assert (
            overlay_manifest_filename("current_release")
            == "index_manifest_branch_current_release.json"
        )

    def test_two_labels_on_one_path_are_different_points(self):
        key = "src/app.py"
        branch_id = make_overlay_point_id("feature/example", key, 0)
        tag_id = make_overlay_point_id("current_release", key, 0)
        assert branch_id != tag_id

    def test_branch_progress_does_not_add_resolved_commit(self):
        fields = manifest_progress_fields(
            kind="branch",
            merge_base="abc",
            branch_head="def",
            resolved_commit="def",
        )
        assert fields == {"merge_base": "abc", "last_branch_commit": "def"}
        assert "last_resolved_commit" not in fields

    def test_tag_progress_stores_resolved_commit_only(self):
        fields = manifest_progress_fields(
            kind="tag",
            merge_base=None,
            branch_head=None,
            resolved_commit="abc123",
        )
        assert fields == {"last_resolved_commit": "abc123"}


class TestReconcile:
    def test_dropped_path_is_a_delete(self):
        old = {"src/b.py": {"hash": "old", "vector_ids": ["b-id"]}}
        actions = reconcile_overlay_actions(old, {})
        assert actions["delete"] == ["src/b.py"]
        assert collect_vector_ids(old, actions["delete"]) == ["b-id"]

    def test_same_hash_is_a_no_op(self):
        old = {"src/a.py": {"hash": "same", "vector_ids": ["a-id"]}}
        new = {"src/a.py": {"hash": "same", "file_path": "src/a.py"}}
        actions = reconcile_overlay_actions(old, new)
        assert actions == {"add": [], "modify": [], "delete": []}

    def test_sql_dialect_change_still_modifies(self):
        old = {
            "sql/a.sql": {
                "hash": "same",
                "sql_dialect": "postgresql",
                "vector_ids": ["sql-id"],
            }
        }
        new = {"sql/a.sql": {"hash": "same", "file_path": "sql/a.sql"}}
        actions = reconcile_overlay_actions(old, new)
        assert actions["modify"] == ["sql/a.sql"]

    def test_empty_diff_policy_preserves_branch_skip(self):
        assert skip_when_diff_empty("branch") is True
        assert skip_when_diff_empty("tag") is False


class TestRefs:
    def test_annotated_and_lightweight_tags_peel_to_the_same_commit(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        commit_files(repo, {"src/app.py": PY_BODY}, "base")
        commit = head(repo)
        git(repo, "tag", "light_release", commit)
        git(repo, "tag", "-a", "annotated_release", "-m", "release", commit)

        assert branch_exists(str(repo), "light_release")
        assert branch_exists(str(repo), "annotated_release")
        assert branch_exists(str(repo), "main")
        assert not branch_exists(str(repo), "missing_name")

        light = resolve_to_commit(str(repo), "light_release")
        annotated = resolve_to_commit(str(repo), "annotated_release")
        assert light == annotated == commit
        tag_object = git_out(repo, "rev-parse", "annotated_release")
        assert tag_object != annotated

    def test_branch_still_exists(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        commit_files(repo, {"src/app.py": PY_BASE}, "base")
        git(repo, "branch", "feature/example")
        assert branch_exists(str(repo), "feature/example")
        assert resolve_to_commit(str(repo), "feature/example") == head(repo)


class TestDiffKinds:
    def _build(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        commit_files(
            repo,
            {
                "src/keep.py": PY_BASE,
                "src/only_main.py": PY_BASE,
                "src/gone.py": PY_BASE,
                "src/old.py": PY_BASE,
            },
            "base",
        )
        git(repo, "branch", "feature/example")
        git(repo, "checkout", "feature/example")
        git(repo, "mv", "src/old.py", "src/new.py")
        commit_files(repo, {"src/keep.py": PY_V1}, "feature edit")
        feature = head(repo)
        git(repo, "tag", "current_release", feature)
        git(repo, "checkout", "main")
        git(repo, "rm", "src/gone.py")
        commit_files(repo, {"src/only_main.py": PY_V2}, "main moves")
        return repo, feature

    def test_tag_diff_is_against_main_tip_and_branch_diff_is_three_dot(self, tmp_path):
        repo, _feature = self._build(tmp_path)
        prefixes = ["src"]
        branch_changes = diff_branches(
            str(repo), "main", "feature/example", paths=prefixes
        )
        tag_changes = diff_against_main_tip(
            str(repo), "main", "current_release", paths=prefixes
        )
        branch_paths = {path for _status, path in branch_changes}
        tag_paths = {path for _status, path in tag_changes}

        assert "src/keep.py" in branch_paths
        assert "src/only_main.py" not in branch_paths
        assert "src/gone.py" not in branch_paths

        assert "src/keep.py" in tag_paths
        assert "src/only_main.py" in tag_paths
        assert ("A", "src/gone.py") in tag_changes

    def test_rename_splits_into_delete_and_add(self, tmp_path):
        repo, _feature = self._build(tmp_path)
        changes = diff_against_main_tip(
            str(repo), "main", "current_release", paths=["src"]
        )
        assert ("D", "src/old.py") in changes
        assert ("A", "src/new.py") in changes
        assert all(not status.startswith(("R", "C")) for status, _path in changes)
        assert all("\t" not in path for _status, path in changes)

    def test_kind_selects_the_diff(self, tmp_path):
        repo, _feature = self._build(tmp_path)
        group = _group(
            repo,
            branches=["feature/example"],
            overlays=[
                {
                    "name": "current_release",
                    "kind": "tag",
                    "diff": "against_main_tip",
                }
            ],
        )
        branch_diff = diff_overlay(
            str(repo),
            "main",
            _spec(group, "feature/example"),
            paths=["src"],
        )
        tag_diff = diff_overlay(
            str(repo),
            "main",
            _spec(group, "current_release"),
            paths=["src"],
        )
        direct_branch = diff_branches(
            str(repo), "main", "feature/example", paths=["src"]
        )
        assert branch_diff.changes == direct_branch
        assert branch_diff.read_at == "feature/example"
        assert branch_diff.merge_base
        assert tag_diff.read_at == tag_diff.resolved_commit
        assert tag_diff.merge_base is None
        assert ("A", "src/gone.py") in tag_diff.changes
        assert ("A", "src/gone.py") not in branch_diff.changes

    def test_branches_list_diff_matches_kind_branch(self, tmp_path):
        repo, _feature = self._build(tmp_path)
        listed = _group(repo, branches=["feature/example"])
        explicit = _group(
            repo, overlays=[{"name": "feature/example", "kind": "branch"}]
        )
        left = diff_overlay(
            str(repo), "main", listed["overlays"][0], paths=["src"]
        )
        right = diff_overlay(
            str(repo), "main", explicit["overlays"][0], paths=["src"]
        )
        assert left.changes == right.changes
        assert listed["branches"] == explicit["branches"] == ["feature/example"]

    def test_tag_equal_to_main_is_an_empty_overlay(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        commit_files(repo, {"src/app.py": PY_BASE}, "base")
        git(repo, "tag", "current_release")
        group = _group(
            repo,
            overlays=[
                {
                    "name": "current_release",
                    "kind": "tag",
                    "diff": "against_main_tip",
                }
            ],
        )
        diff = diff_overlay(
            str(repo), "main", group["overlays"][0], paths=["src"]
        )
        assert diff.changes == []
        assert diff.resolved_commit == head(repo)


class TestReadWithoutCheckout:
    def test_detached_dirty_worktree_does_not_change_the_overlay(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        commit_files(repo, {"src/app.py": PY_BASE}, "base")
        git(repo, "checkout", "-b", "feature/example")
        commit_files(repo, {"src/app.py": PY_V1}, "feature")
        feature = head(repo)
        git(repo, "tag", "-a", "current_release", "-m", "rel", feature)
        git(repo, "checkout", "main")
        commit_files(repo, {"src/other.py": PY_BASE}, "main moves")
        git(repo, "checkout", "--detach", feature)
        write_files(repo, {"src/app.py": "dirty worktree\n", "src/untracked.py": PY_V2})

        before_head = head(repo)
        before_branch = git_out(repo, "branch", "--show-current")
        before_worktrees = worktree_count(repo)

        group = _group(
            repo,
            overlays=[
                {
                    "name": "current_release",
                    "kind": "tag",
                    "diff": "against_main_tip",
                }
            ],
        )
        diff, states, _tombstones = _states(repo, group, group["overlays"][0])
        temp = read_files_to_temp_dir(str(repo), diff.read_at, ["src/app.py"])
        try:
            text = (Path(temp) / "src/app.py").read_text(encoding="utf-8")
        finally:
            import shutil

            shutil.rmtree(temp, ignore_errors=True)

        assert "v1" in text
        assert "dirty" not in text
        assert "src/untracked.py" not in {path for _s, path in diff.changes}
        assert any(key.endswith("app.py") for key in states)
        assert head(repo) == before_head
        assert git_out(repo, "branch", "--show-current") == before_branch
        assert worktree_count(repo) == before_worktrees

    def test_binary_file_is_in_the_diff_and_readers_skip_it(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        commit_files(repo, {"src/app.py": PY_BASE}, "base")
        git(repo, "checkout", "-b", "release-work")
        png = b"\x89PNG\r\n\x1a\n" + b"\x00\xff" * 32
        commit_files(
            repo,
            {"src/app.py": PY_V1, "src/logo.png": png},
            "release files",
        )
        git(repo, "tag", "current_release")
        git(repo, "checkout", "main")
        group = _group(
            repo,
            overlays=[
                {
                    "name": "current_release",
                    "kind": "tag",
                    "diff": "against_main_tip",
                }
            ],
        )
        diff = diff_overlay(
            str(repo), "main", group["overlays"][0], paths=["src"]
        )
        paths = {path for _status, path in diff.changes}
        assert "src/app.py" in paths
        assert "src/logo.png" in paths

        temp = read_files_to_temp_dir(
            str(repo), diff.read_at, ["src/app.py", "src/logo.png"]
        )
        try:
            py_nodes = load_nodes_for_file(
                {"full_path": str(Path(temp) / "src/app.py"), "file_path": "src/app.py"}
            )
            png_nodes = load_nodes_for_file(
                {
                    "full_path": str(Path(temp) / "src/logo.png"),
                    "file_path": "src/logo.png",
                }
            )
        finally:
            import shutil

            shutil.rmtree(temp, ignore_errors=True)

        assert py_nodes
        assert png_nodes == []


class TestTagMoves:
    def _repo(self, tmp_path):
        repo = init_repo(tmp_path / "repo")
        commit_files(repo, {"src/a.py": PY_BASE}, "base")
        main_base = head(repo)
        git(repo, "checkout", "-b", "release-line")
        c1 = commit_files(repo, {"src/a.py": PY_V1}, "v1")
        git(repo, "tag", "-a", "current_release", "-m", "v1", c1)
        c2 = commit_files(
            repo, {"src/a.py": PY_V2, "src/b.py": PY_V2}, "v2"
        )
        git(repo, "checkout", "main")
        return repo, main_base, c1, c2

    def _spec(self, repo):
        group = _group(
            repo,
            overlays=[
                {
                    "name": "current_release",
                    "kind": "tag",
                    "diff": "against_main_tip",
                }
            ],
        )
        return group, group["overlays"][0]

    def test_forward_and_backward_refresh_deletes_points(self, tmp_path):
        repo, main_base, c1, c2 = self._repo(tmp_path)
        group, spec = self._spec(repo)
        label = "current_release"

        diff1, states1, _t1 = _states(repo, group, spec)
        assert diff1.resolved_commit == c1
        assert set(states1) == {"src/a.py"}
        files = _manifest_from_states(label, states1)

        git(repo, "tag", "-f", "-a", "current_release", "-m", "v2", c2)
        diff2, states2, _t2 = _states(repo, group, spec)
        assert diff2.resolved_commit == c2
        assert set(states2) == {"src/a.py", "src/b.py"}
        actions_forward = reconcile_overlay_actions(files, states2)
        assert "src/b.py" in actions_forward["add"]
        assert "src/a.py" in actions_forward["modify"]
        assert actions_forward["delete"] == []
        files = _manifest_from_states(label, states2)
        progress = manifest_progress_fields(
            kind="tag",
            merge_base=None,
            branch_head=None,
            resolved_commit=diff2.resolved_commit,
        )
        assert progress["last_resolved_commit"] == c2

        git(repo, "tag", "-f", "-a", "current_release", "-m", "v1", c1)
        diff3, states3, _t3 = _states(repo, group, spec)
        assert diff3.resolved_commit == c1
        actions_back = reconcile_overlay_actions(files, states3)
        assert actions_back["delete"] == ["src/b.py"]
        assert "src/a.py" in actions_back["modify"]
        dropped = collect_vector_ids(files, actions_back["delete"])

        client = _memory_collection()
        client.upsert(
            collection_name="overlay",
            points=[
                _point("main", "src/a.py"),
                _point(label, "src/a.py"),
                _point(label, "src/b.py"),
                _point("feature/example", "src/a.py"),
            ],
        )
        delete_point_ids(client, "overlay", dropped)
        assert _labels(client, label) == {"main", label}
        remaining = client.scroll(
            collection_name="overlay",
            scroll_filter=build_branch_filter("main", label),
            limit=20,
        )[0]
        remaining_paths = {
            (point.payload["branch"], point.payload["file_path"]) for point in remaining
        }
        assert ("current_release", "src/b.py") not in remaining_paths
        assert ("feature/example", "src/a.py") not in remaining_paths
        assert ("current_release", "src/a.py") in remaining_paths

        git(repo, "tag", "-f", "current_release", main_base)
        diff4, states4, tomb4 = _states(repo, group, spec)
        assert diff4.changes == []
        assert states4 == {}
        assert tomb4 == []
        actions_clear = reconcile_overlay_actions(files, states4)
        assert set(actions_clear["delete"]) == {"src/a.py", "src/b.py"}
        delete_point_ids(
            client, "overlay", collect_vector_ids(files, actions_clear["delete"])
        )
        assert _labels(client, label) == {"main"}

    def test_same_commit_second_pass_skips_hash_work(self, tmp_path):
        repo, _main, c1, _c2 = self._repo(tmp_path)
        group, spec = self._spec(repo)
        _diff, states, _tomb = _states(repo, group, spec)
        files = _manifest_from_states("current_release", states)
        _diff2, states2, _tomb2 = _states(repo, group, spec)
        assert _diff2.resolved_commit == c1
        assert reconcile_overlay_actions(files, states2) == {
            "add": [],
            "modify": [],
            "delete": [],
        }


class TestQuery:
    def test_tool_description_asks_for_a_configured_overlay_name(self):
        text = BRANCH_PARAMETER_DESCRIPTION.lower()
        assert "overlay" in text
        assert "tag" in text
        assert "never been indexed" in text
        assert "main" in text
        source = Path("src/rag_mcp.py").read_text(encoding="utf-8")
        assert "BRANCH_PARAMETER_DESCRIPTION" in source

    def test_unindexed_label_returns_main_only(self):
        client = _memory_collection()
        client.upsert(
            collection_name="overlay",
            points=[_point("main", "src/a.py")],
        )
        assert _labels(client, "current_release") == {"main"}

    def test_query_names_one_label(self):
        client = _memory_collection()
        client.upsert(
            collection_name="overlay",
            points=[
                _point("main", "src/a.py"),
                _point("current_release", "src/a.py"),
                _point("feature/example", "src/a.py"),
            ],
        )
        assert _labels(client, "current_release") == {"main", "current_release"}
        assert _labels(client, "feature/example") == {"main", "feature/example"}

        overlay_node = _node("src/a.py", "current_release", score=0.4)
        main_node = _node("src/a.py", "main", score=0.9)
        kept = dedup_branch_results(
            [main_node, overlay_node],
            feature_branch="current_release",
            desired_top_k=5,
        )
        assert len(kept) == 1
        assert kept[0].node.metadata["branch"] == "current_release"

    def test_tombstones_load_from_the_overlay_manifest_name(self, tmp_path):
        index = tmp_path / "index"
        index.mkdir()
        name = "current_release"
        manifest = index / overlay_manifest_filename(name)
        manifest.write_text(
            '{"branch": "current_release", "tombstones": ["src/gone.py"]}',
            encoding="utf-8",
        )
        cfg = types.SimpleNamespace()
        cfg.get_index_path = lambda: str(index)
        assert get_branch_tombstones(name, cfg) == ["src/gone.py"]


def _node(file_path: str, branch: str, score: float):
    node = MagicMock()
    node.metadata = {"file_path": file_path, "branch": branch}
    wrapped = MagicMock()
    wrapped.node = node
    wrapped.score = score
    return wrapped
