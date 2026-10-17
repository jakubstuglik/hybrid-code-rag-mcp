"""Pull step force-updates configured tag overlays (git_pull_guard)."""

from __future__ import annotations

from pathlib import Path

import git_pull_guard as gpg
from shared.overlay import diff_overlay
from tests.repo_util import commit_files, git, git_out, init_repo


def _setup(tmp_path: Path):
    origin_work = init_repo(tmp_path / "upstream")
    commit_files(origin_work, {"src/a.py": "a = 1\n", "src/b.py": "b = 1\n"}, "base")
    git(origin_work, "branch", "feature/x")
    git(origin_work, "checkout", "-q", "--detach")
    commit_files(origin_work, {"src/a.py": "a = 2\n"}, "release 1")
    git(origin_work, "tag", "-a", "rel", "-m", "rel 1")
    git(origin_work, "checkout", "-q", "main")
    bare = tmp_path / "remote.git"
    git(tmp_path, "clone", "-q", "--bare", str(origin_work), str(bare))
    local = tmp_path / "local"
    git(tmp_path, "clone", "-q", str(bare), str(local))
    git(local, "config", "user.email", "t@example.com")
    git(local, "config", "user.name", "T")
    return origin_work, bare, local


def _info(local: Path, tags=("rel",), branches=("feature/x",)):
    return {
        "repo_path": str(local),
        "main_branch": "main",
        "branches": list(branches),
        "overlays": [{"name": b, "kind": "branch", "diff": "merge_base"} for b in branches]
        + [{"name": t, "kind": "tag", "diff": "against_main_tip"} for t in tags],
    }


def _move_tag_on_remote(origin_work: Path, bare: Path, content: str) -> str:
    git(origin_work, "checkout", "-q", "--detach", "rel")
    commit_files(origin_work, {"src/b.py": content}, "release 2")
    git(origin_work, "tag", "-f", "-a", "rel", "-m", "rel 2")
    git(origin_work, "push", "-q", "--force", str(bare), "refs/tags/rel:refs/tags/rel")
    git(origin_work, "checkout", "-q", "main")
    return git_out(origin_work, "rev-parse", "rel^{commit}")


def test_moved_remote_tag_is_force_updated_and_overlay_refreshes(tmp_path):
    origin_work, bare, local = _setup(tmp_path)
    spec = {"name": "rel", "kind": "tag", "diff": "against_main_tip"}
    before = diff_overlay(str(local), "main", spec)
    assert {p for _, p in before.changes} == {"src/a.py"}

    new_commit = _move_tag_on_remote(origin_work, bare, "b = 2\n")
    git(local, "fetch", "-q", "origin")  # plain fetch does not move the tag
    assert git_out(local, "rev-parse", "rel^{commit}") == before.resolved_commit

    result = gpg._pull_repo(_info(local))
    assert result["warnings"] == []
    assert git_out(local, "rev-parse", "rel^{commit}") == new_commit
    after = diff_overlay(str(local), "main", spec)
    assert after.resolved_commit == new_commit
    assert {p for _, p in after.changes} == {"src/a.py", "src/b.py"}


def test_other_tags_and_branches_are_not_forced(tmp_path):
    origin_work, bare, local = _setup(tmp_path)
    # An unconfigured tag also moves on the remote; it must stay put locally.
    git(origin_work, "tag", "other", "main")
    git(origin_work, "push", "-q", str(bare), "refs/tags/other")
    git(local, "fetch", "-q", "--tags", "origin")
    other_before = git_out(local, "rev-parse", "other")
    git(origin_work, "tag", "-f", "other", "rel^{commit}")
    git(origin_work, "push", "-q", "--force", str(bare), "refs/tags/other")
    # Local branch diverges from remote: not fast-forwardable, must not be forced.
    git(local, "branch", "feature/x", "origin/feature/x")
    git(local, "checkout", "-q", "feature/x")
    local_feat = commit_files(local, {"src/c.py": "c = 1\n"}, "local only")
    git(local, "checkout", "-q", "main")
    git(origin_work, "checkout", "-q", "feature/x")
    commit_files(origin_work, {"src/d.py": "d = 1\n"}, "remote only")
    git(origin_work, "push", "-q", str(bare), "feature/x")
    git(origin_work, "checkout", "-q", "main")
    _move_tag_on_remote(origin_work, bare, "b = 3\n")

    result = gpg._pull_repo(_info(local))
    assert git_out(local, "rev-parse", "other") == other_before
    assert git_out(local, "rev-parse", "feature/x") == local_feat
    assert any("fast-forward feature/x" in e for e in result["errors"])


def test_fetch_failure_warns_and_keeps_local_tag(tmp_path, capsys):
    _origin_work, bare, local = _setup(tmp_path)
    local_commit = git_out(local, "rev-parse", "rel^{commit}")
    git(local, "remote", "set-url", "origin", str(tmp_path / "missing.git"))

    result = gpg._pull_repo(_info(local, branches=()))
    assert len(result["warnings"]) == 1 and "rel" in result["warnings"][0]
    assert "WARNING" in capsys.readouterr().out
    assert git_out(local, "rev-parse", "rel^{commit}") == local_commit
    spec = {"name": "rel", "kind": "tag", "diff": "against_main_tip"}
    assert diff_overlay(str(local), "main", spec).resolved_commit == local_commit


def test_no_tag_overlays_runs_no_tag_fetch(tmp_path, monkeypatch):
    _o, _b, local = _setup(tmp_path)
    calls = []
    monkeypatch.setattr(gpg, "_git_force_update_tag", lambda *a: calls.append(a) or (a[0], True, ""))
    gpg._pull_repo({"repo_path": str(local), "main_branch": "main", "branches": ["feature/x"]})
    assert calls == []
