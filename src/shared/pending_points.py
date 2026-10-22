# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Journal of Qdrant changes not yet covered by a saved manifest.

A refresh changes Qdrant first and records the result in the manifest
afterwards. A run killed in between (cron guard, OOM, reboot) leaves points
the manifest does not know about, or misses points the manifest still lists.
Later runs compare files against the manifest only, so they never repair
that: the points of a file added and then deleted stay in search results,
and a file whose old points were deleted keeps its old manifest entry.

The journal closes that gap. Before the indexer deletes or upserts points of
a file it appends one line ``{"k": <file key>, "h": <hash or null>}`` to
``<manifest>.pending.jsonl``: the content hash the file's points will have
afterwards, or ``null`` when its points are being deleted. The last line of
a key wins. A journal entry is *resolved* when the manifest agrees with it:
``h`` is null and the manifest has no entry, or the manifest entry's hash is
``h``. After a run the journal keeps only unresolved entries (it is removed
when none are left). At the start of the next run every unresolved key has
its points deleted and its manifest entry dropped, so the run re-indexes the
file from disk (or forgets it when the file is gone).
"""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Iterable
from pathlib import Path

JOURNAL_SUFFIX = ".pending.jsonl"


class PendingRecoveryError(RuntimeError):
    """The points of an interrupted run could not be repaired.

    The journal is kept. The run must stop: going on would re-add the
    journalled files without deleting their old points first.
    """


def journal_path_for(manifest_path: Path) -> Path:
    """Return the journal path that belongs to *manifest_path*."""
    manifest_path = Path(manifest_path)
    return manifest_path.with_name(manifest_path.name + JOURNAL_SUFFIX)


def read_journal(path: Path) -> dict[str, str | None]:
    """Return ``{file key: hash or None}`` from *path* (last line per key wins).

    A missing file is an empty journal. Lines that do not parse (a write cut
    short by a kill) are ignored: the change they announce never started,
    because the line is complete before Qdrant is touched.
    """
    path = Path(path)
    result: dict[str, str | None] = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(item, dict) or not isinstance(item.get("k"), str):
                    continue
                h = item.get("h")
                result[item["k"]] = h if isinstance(h, str) else None
    except FileNotFoundError:
        return {}
    return result


def unresolved_keys(journal: dict[str, str | None], files: dict) -> list[str]:
    """Return the journal keys whose manifest entry disagrees with the journal."""
    stale = []
    for key, expected in journal.items():
        entry = files.get(key)
        if expected is None:
            if entry is not None:
                stale.append(key)
        elif entry is None or entry.get("hash") != expected:
            stale.append(key)
    return stale


class PendingJournal:
    """Append-only writer for one manifest's journal (thread-safe)."""

    def __init__(self, path: Path, *, fsync: bool = True) -> None:
        self.path = Path(path)
        self._fsync = fsync
        self._lock = threading.Lock()
        self.records = 0

    def record(self, items: Iterable[tuple[str, str | None]]) -> None:
        """Append ``(key, hash or None)`` items and flush them to disk."""
        lines = [
            json.dumps({"k": key, "h": h}, separators=(",", ":")) + "\n"
            for key, h in items
        ]
        if not lines:
            return
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write("".join(lines))
                f.flush()
                if self._fsync:
                    os.fsync(f.fileno())
            self.records += len(lines)

    def finish(self, files: dict) -> list[str]:
        """Keep only entries the manifest *files* does not resolve.

        Call after the manifest that holds *files* was saved. Removes the
        journal when every entry is resolved; otherwise rewrites it with the
        unresolved entries and returns their keys.
        """
        with self._lock:
            journal = read_journal(self.path)
            stale = unresolved_keys(journal, files)
            if not stale:
                remove_journal(self.path)
                return []
            tmp = self.path.with_name(self.path.name + f".{os.getpid()}.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                for key in stale:
                    f.write(json.dumps({"k": key, "h": journal[key]}, separators=(",", ":")) + "\n")
                f.flush()
                if self._fsync:
                    os.fsync(f.fileno())
            os.replace(tmp, self.path)
            return stale


def remove_journal(path: Path) -> bool:
    """Delete the journal at *path*; return True when a file was removed."""
    try:
        Path(path).unlink()
        return True
    except FileNotFoundError:
        return False
