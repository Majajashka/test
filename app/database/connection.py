import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"

_conn: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30, isolation_level=None)
        _conn.execute("PRAGMA foreign_keys = ON")
        _conn.execute("PRAGMA busy_timeout = 30000")
        _conn.execute("PRAGMA journal_mode = WAL")
        _conn.row_factory = sqlite3.Row
    return _conn
