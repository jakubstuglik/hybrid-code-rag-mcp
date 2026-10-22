# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Pending-points journal: format, last-line-wins, resolution against the manifest."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from shared.pending_points import (
    JOURNAL_SUFFIX,
    PendingJournal,
    journal_path_for,
    read_journal,
    remove_journal,
    unresolved_keys,
)


def test_journal_path_sits_next_to_the_manifest(tmp_path):
    m = tmp_path / "index_manifest_branch_feature_x.json"
    assert journal_path_for(m) == tmp_path / ("index_manifest_branch_feature_x.json" + JOURNAL_SUFFIX)


def test_missing_journal_reads_empty(tmp_path):
    assert read_journal(tmp_path / "nope.jsonl") == {}


def test_record_appends_and_last_line_wins(tmp_path):
    j = PendingJournal(tmp_path / "j.jsonl", fsync=False)
    j.record([("a", None), ("b", "h1")])
    j.record([("a", "h2")])
    assert read_journal(j.path) == {"a": "h2", "b": "h1"}
    assert j.records == 3


def test_record_of_nothing_creates_no_file(tmp_path):
    j = PendingJournal(tmp_path / "j.jsonl")
    j.record([])
    j.record(iter(()))
    assert not j.path.exists()


def test_torn_and_foreign_lines_are_ignored(tmp_path):
    p = tmp_path / "j.jsonl"
    p.write_text(
        '{"k":"a","h":"x"}\n'
        "\n"
        '["not", "a", "dict"]\n'
        '{"h":"no key"}\n'
        '{"k":5,"h":"bad key"}\n'
        '{"k":"b","h":7}\n'
        '{"k":"c","h"',  # cut short by a kill
        encoding="utf-8",
    )
    assert read_journal(p) == {"a": "x", "b": None}


def test_keys_with_unicode_and_quotes_roundtrip(tmp_path):
    j = PendingJournal(tmp_path / "j.jsonl", fsync=False)
    key = 'src/zażółć "q"\\x.py'
    j.record([(key, "h")])
    assert read_journal(j.path) == {key: "h"}


@pytest.mark.parametrize(
    "expected,entry,stale",
    [
        (None, None, False),  # delete done and saved
        (None, {"hash": "h"}, True),  # delete not saved / failed
        ("h", {"hash": "h"}, False),  # upsert saved
        ("h", {"hash": "old"}, True),  # upsert not saved (modify)
        ("h", None, True),  # upsert not saved (add)
        ("", {"hash": ""}, False),  # file changed during the run: entry is dirty already
        ("h", {"vector_ids": []}, True),  # entry without a hash
    ],
)
def test_unresolved_rules(expected, entry, stale):
    files = {} if entry is None else {"k": entry}
    assert (unresolved_keys({"k": expected}, files) == ["k"]) is stale


def test_finish_removes_journal_when_all_resolved(tmp_path):
    j = PendingJournal(tmp_path / "j.jsonl", fsync=False)
    j.record([("a", "h"), ("gone", None)])
    assert j.finish({"a": {"hash": "h"}}) == []
    assert not j.path.exists()


def test_finish_keeps_only_unresolved_entries(tmp_path):
    j = PendingJournal(tmp_path / "j.jsonl", fsync=False)
    j.record([("a", "h"), ("b", "h2"), ("c", None)])
    stale = j.finish({"a": {"hash": "h"}, "b": {"hash": "old"}, "c": {"hash": "x"}})
    assert sorted(stale) == ["b", "c"]
    assert read_journal(j.path) == {"b": "h2", "c": None}
    lines = j.path.read_text(encoding="utf-8").splitlines()
    assert all(json.loads(line) for line in lines) and len(lines) == 2


def test_finish_without_journal_is_a_no_op(tmp_path):
    j = PendingJournal(tmp_path / "j.jsonl")
    assert j.finish({}) == []
    assert not j.path.exists()


def test_remove_journal(tmp_path):
    p = Path(tmp_path / "j.jsonl")
    assert remove_journal(p) is False
    p.write_text("x", encoding="utf-8")
    assert remove_journal(p) is True and not p.exists()


def test_record_is_thread_safe(tmp_path):
    import threading

    j = PendingJournal(tmp_path / "j.jsonl", fsync=False)

    def _work(n):
        for i in range(50):
            j.record([(f"t{n}-{i}", "h")])

    threads = [threading.Thread(target=_work, args=(n,)) for n in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(read_journal(j.path)) == 200
