"""The SQLite file behind long-term memory.

SQLite because the stack requires no external database service (REQ-032) and
because the checkpointer already uses it — one storage technology, one backup,
one thing to reason about.

Every write is redacted before it lands. Memory outlives the run that created it,
so an identifier written here is an identifier that persists.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from src.config import REPO_ROOT
from src.guardrails.redaction import redact_structure, redact_text

MEMORY_DB = REPO_ROOT / "data" / "memory" / "credpilot_memory.sqlite"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    scope         TEXT NOT NULL,
    subject_id    TEXT NOT NULL,
    kind          TEXT NOT NULL,
    key           TEXT,
    content       TEXT NOT NULL,
    metadata      TEXT NOT NULL DEFAULT '{}',
    embedding     TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    session_id    TEXT,
    UNIQUE(scope, subject_id, kind, key)
);
CREATE INDEX IF NOT EXISTS idx_memories_subject ON memories(scope, subject_id);
CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(scope, subject_id, kind);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class MemoryStore:
    """A small, thread-safe SQLite store for long-term memory."""

    def __init__(self, path: "str | Path | None" = None):
        self.path = Path(path) if path else MEMORY_DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(str(self.path), timeout=30)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    # -- writes -------------------------------------------------------------------

    def upsert(
        self,
        *,
        scope: str,
        subject_id: str,
        kind: str,
        content: str,
        key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        embedding: Sequence[float] | None = None,
        session_id: str | None = None,
    ) -> int:
        """Write or update one memory. Redacted on the way in."""
        safe_content = redact_text(str(content), use_presidio=True)
        safe_metadata = json.dumps(
            redact_structure(dict(metadata or {}), use_presidio=True), sort_keys=True
        )
        vector = json.dumps([float(v) for v in embedding]) if embedding is not None else None
        timestamp = _now()

        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO memories
                    (scope, subject_id, kind, key, content, metadata, embedding,
                     created_at, updated_at, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(scope, subject_id, kind, key) DO UPDATE SET
                    content = excluded.content,
                    metadata = excluded.metadata,
                    embedding = excluded.embedding,
                    updated_at = excluded.updated_at,
                    session_id = excluded.session_id
                """,
                (
                    scope, subject_id, kind, key, safe_content, safe_metadata,
                    vector, timestamp, timestamp, session_id,
                ),
            )
            return int(cursor.lastrowid or 0)

    def delete_subject(self, scope: str, subject_id: str) -> int:
        """Erase everything held about one subject.

        A data-subject deletion has to be a single, complete operation, not a
        sweep a caller might get wrong.
        """
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM memories WHERE scope = ? AND subject_id = ?",
                (scope, subject_id),
            )
            return int(cursor.rowcount or 0)

    # -- reads --------------------------------------------------------------------

    def fetch(
        self,
        *,
        scope: str,
        subject_id: str,
        kind: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Every memory for one subject. Scoped — never crosses subjects."""
        query = "SELECT * FROM memories WHERE scope = ? AND subject_id = ?"
        params: list[Any] = [scope, subject_id]
        if kind:
            query += " AND kind = ?"
            params.append(kind)
        query += " ORDER BY updated_at DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as connection:
            return [dict(row) for row in connection.execute(query, params)]

    def count(self, *, scope: str | None = None, subject_id: str | None = None) -> int:
        query = "SELECT COUNT(*) AS n FROM memories WHERE 1=1"
        params: list[Any] = []
        if scope:
            query += " AND scope = ?"
            params.append(scope)
        if subject_id:
            query += " AND subject_id = ?"
            params.append(subject_id)
        with self._connect() as connection:
            return int(connection.execute(query, params).fetchone()["n"])

    def subjects(self, scope: str) -> list[str]:
        with self._connect() as connection:
            return [
                row["subject_id"]
                for row in connection.execute(
                    "SELECT DISTINCT subject_id FROM memories WHERE scope = ? "
                    "ORDER BY subject_id",
                    (scope,),
                )
            ]
