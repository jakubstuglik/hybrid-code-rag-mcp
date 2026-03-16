import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

from shared.log import log_warn


def get_sqlite_path(index_path: str) -> Path:
    """Get path for the temporary SQLite store."""
    return Path(index_path) / ".dense_temp.sqlite"


def init_sqlite_db(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database with schema for dense vectors."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dense_vectors (
            node_id TEXT PRIMARY KEY,
            dense_vector BLOB NOT NULL,
            payload BLOB NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_node_id ON dense_vectors(node_id)")
    conn.commit()
    return conn


def save_dense_vectors_sqlite(
    db_path: Path,
    node_data: List[Tuple[str, List[float], Dict[str, Any]]],
) -> None:
    """Save dense vectors to SQLite.
    
    Args:
        db_path: Path to SQLite database.
        node_data: List of (node_id, dense_vector, payload) tuples.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO dense_vectors (node_id, dense_vector, payload) VALUES (?, ?, ?)",
            [
                (node_id, json.dumps(dense_vec), json.dumps(payload))
                for node_id, dense_vec, payload in node_data
            ],
        )
        conn.commit()
    finally:
        conn.close()


def read_dense_vectors_sqlite(
    db_path: Path,
    node_ids: List[str],
) -> Dict[str, Tuple[List[float], Dict[str, Any]]]:
    """Read dense vectors from SQLite by node IDs.
    
    Args:
        db_path: Path to SQLite database.
        node_ids: List of node IDs to fetch.
        
    Returns:
        Dict mapping node_id -> (dense_vector, payload).
    """
    if not node_ids:
        return {}
    
    conn = sqlite3.connect(str(db_path))
    try:
        placeholders = ",".join("?" * len(node_ids))
        cursor = conn.execute(
            f"SELECT node_id, dense_vector, payload FROM dense_vectors WHERE node_id IN ({placeholders})",
            node_ids,
        )
        result = {}
        for node_id, dense_vec_json, payload_json in cursor:
            result[node_id] = (json.loads(dense_vec_json), json.loads(payload_json))
        return result
    finally:
        conn.close()


def cleanup_sqlite(db_path: Path) -> None:
    """Drop table, vacuum, and delete SQLite file."""
    if not db_path.exists():
        return
    
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("DROP TABLE IF EXISTS dense_vectors")
        conn.execute("VACUUM")
        conn.commit()
    finally:
        conn.close()
    
    try:
        db_path.unlink()
    except OSError as e:
        log_warn(f"Failed to delete temp SQLite file {db_path}: {e}")
