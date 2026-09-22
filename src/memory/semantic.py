"""LangMem-backed long-term memory, over a LangGraph SQLite store.

The source document's Memory row names two things together:

    langgraph-checkpoint-sqlite (SQLite file) + LangMem

The checkpointer covers *this* conversation — it is what makes a thread
resumable. LangMem covers what survives between conversations, and that is what
this module provides: writes and semantic recall through LangMem's own tool API,
against a ``langgraph.store.sqlite.SqliteStore`` backed by a file on disk.

Why the policy sits in front of LangMem rather than behind it
------------------------------------------------------------
LangMem will store whatever it is handed. Everything this system must *not*
remember is therefore refused before the write reaches it:

* **decisions and thresholds** — a prior APPROVE is not evidence for the next
  application, and a cached threshold outlives the boundary that replaced it.
  Refused by kind, using the same closed set :mod:`src.memory.long_term`
  enforces, so there is one rulebook rather than two that can drift apart.
* **identifiers in the clear** — content is redacted on the way in, not on the
  way out. A store that holds an unredacted identifier has already leaked it;
  redacting at read time only hides it from the honest caller.
* **instruction-shaped applicant text** — applicant text is evidence, never
  instruction (``POL-SEC-001`` SEC-INJ-001). Text carrying an injection is
  refused rather than stored, because a memory is replayed into a later prompt
  with more trust than the message it arrived in, which is precisely the
  property an attacker is looking for.

Isolation is structural, not filtered
-------------------------------------
Each subject owns a namespace — ``("credpilot", scope, subject_id)`` — and every
read is issued *against that namespace*. One applicant's recall cannot return
another's file because the query is never broad enough to see it, rather than
because a filter removed it afterwards. ``POL-SEC-001`` SEC-INJ-002 is the rule;
a post-filter would be one ranking bug away from breaking it.

Failure is never fatal
----------------------
Memory enriches an assessment and must never gate one. If the backend cannot be
opened, :attr:`SemanticMemory.available` is ``False``, reads return nothing and
writes return ``None``. The caller gets a file it can still assess on policy and
the packet alone.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from src.config import REPO_ROOT

#: The LangMem store file. A sibling of the long-term store rather than the same
#: file: LangMem owns its schema and migrates it, and sharing a file would mean
#: two writers with different ideas about what the tables are.
LANGMEM_DB = REPO_ROOT / "data" / "memory" / "credpilot_langmem.sqlite"

#: The namespace root. Present so every namespace this process writes is
#: recognisable in a store that something else might also be using.
NAMESPACE_ROOT = "credpilot"


class MemoryBackendUnavailable(RuntimeError):
    """The LangMem store could not be opened or set up."""


class ForbiddenMemoryContent(ValueError):
    """The content itself may not be stored, whatever its kind."""


@dataclass
class SemanticRecord:
    """One memory recalled through LangMem."""

    id: str
    subject_id: str
    scope: str
    content: str
    kind: str | None
    metadata: dict[str, Any]
    created_at: str | None
    updated_at: str | None
    score: float | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "id": self.id,
            "subject_id": self.subject_id,
            "scope": self.scope,
            "content": self.content,
            "kind": self.kind,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "backend": "langmem",
        }
        if self.score is not None:
            payload["score"] = round(float(self.score), 4)
        return payload


def _check_kind(kind: str) -> None:
    """Refuse the kinds memory must not hold.

    Imported lazily so this module and :mod:`src.memory.long_term` can refer to
    each other without an import cycle. The closed set lives there because that
    is where its reasoning is written down; duplicating it here would let the two
    drift, and the one that drifts is the one that stops refusing decisions.
    """
    from src.memory.long_term import ALLOWED_KINDS, FORBIDDEN_KINDS, ForbiddenMemoryError

    if kind in FORBIDDEN_KINDS:
        raise ForbiddenMemoryError(
            f"refusing to store kind '{kind}': {FORBIDDEN_KINDS[kind]}"
        )
    if kind not in ALLOWED_KINDS:
        raise ForbiddenMemoryError(
            f"unknown memory kind '{kind}'; allowed: {sorted(ALLOWED_KINDS)}"
        )


class SemanticMemory:
    """Cross-session memory through LangMem, scoped per subject.

    ``embed`` is optional. With it, recall is ranked by similarity; without it,
    LangMem still stores and retrieves within the namespace, unranked. It is
    optional because loading a sentence-transformer costs seconds that most
    tests should not pay, and because ranking is an improvement to recall rather
    than the thing that makes recall correct.
    """

    def __init__(
        self,
        path: "str | Path | None" = None,
        *,
        embed: Callable[[Sequence[str]], list[list[float]]] | None = None,
        dims: int | None = None,
    ):
        self.path = Path(path) if path else LANGMEM_DB
        self._embed = embed
        self._dims = dims
        self._store = None
        self._conn: sqlite3.Connection | None = None
        self._error: str | None = None
        self._open()

    # -- lifecycle ------------------------------------------------------------

    def _open(self) -> None:
        try:
            from langgraph.store.sqlite import SqliteStore

            self.path.parent.mkdir(parents=True, exist_ok=True)
            # check_same_thread=False because the web surface serves SSE from a
            # worker thread while the CLI stays on the main one.
            #
            # isolation_level=None matters more than it looks. SqliteStore issues
            # its own BEGIN, and Python's sqlite3 opens an implicit transaction
            # by default; leaving the default turns every write into "cannot
            # start a transaction within a transaction", which this class would
            # then swallow as a backend failure and report as empty recall.
            self._conn = sqlite3.connect(
                str(self.path), check_same_thread=False, isolation_level=None
            )
            index = None
            if self._embed is not None and self._dims:
                index = {"dims": int(self._dims), "embed": self._embed, "fields": ["content"]}
            self._store = SqliteStore(self._conn, index=index)
            self._store.setup()
        except Exception as exc:  # noqa: BLE001 - memory must never block a file
            self._error = f"{type(exc).__name__}: {exc}"
            self._store = None
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:  # noqa: BLE001
                    pass
                self._conn = None

    @property
    def available(self) -> bool:
        """Whether the backend opened. ``False`` degrades every call, quietly."""
        return self._store is not None

    @property
    def error(self) -> str | None:
        """Why the backend is unavailable, if it is."""
        return self._error

    @property
    def store(self):
        """The underlying LangGraph store, for callers that hold a graph."""
        return self._store

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            finally:
                self._conn = None
                self._store = None

    def __enter__(self) -> "SemanticMemory":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- namespacing ----------------------------------------------------------

    def namespace(self, subject_id: str, scope: str = "applicant") -> tuple[str, ...]:
        """The namespace one subject's memories live in.

        Every read and write goes through here, so there is exactly one place
        where isolation could be got wrong, and it is three lines long.
        """
        if not subject_id:
            raise ValueError("a memory needs a subject to belong to")
        return (NAMESPACE_ROOT, str(scope), str(subject_id))

    # -- LangMem tools --------------------------------------------------------

    def _manage_tool(self, subject_id: str, scope: str):
        from langmem import create_manage_memory_tool

        return create_manage_memory_tool(
            namespace=self.namespace(subject_id, scope), store=self._store
        )

    def _search_tool(self, subject_id: str, scope: str):
        from langmem import create_search_memory_tool

        return create_search_memory_tool(
            namespace=self.namespace(subject_id, scope), store=self._store
        )

    def tools(self, subject_id: str, scope: str = "applicant") -> list[Any]:
        """LangMem's two tools, bound to one subject's namespace.

        Returned for an agent to call directly. Bound rather than generic on
        purpose: a tool that takes the subject as an argument is a tool an
        injected instruction can point at someone else.
        """
        if not self.available:
            return []
        return [self._manage_tool(subject_id, scope), self._search_tool(subject_id, scope)]

    # -- writes ---------------------------------------------------------------

    def write(
        self,
        *,
        subject_id: str,
        content: str,
        kind: str = "context_note",
        scope: str = "applicant",
        key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        session_id: str | None = None,
    ) -> str | None:
        """Store one memory, after refusing everything memory must not hold.

        Returns the LangMem memory id, or ``None`` if the backend is down or the
        content did not survive redaction.
        """
        from src.guardrails.redaction import redact_text
        from src.guardrails.sanitize import detect_injection

        _check_kind(kind)

        raw = str(content or "")
        findings = detect_injection(raw)
        if findings:
            # Not stored, and not silently dropped either: the caller is told,
            # so a repeated attempt shows up as a review trigger rather than as
            # a memory that mysteriously never appears.
            raise ForbiddenMemoryContent(
                f"refusing to store text carrying {sorted(set(findings))}; "
                "applicant text is evidence, never instruction (POL-SEC-001 SEC-INJ-001)"
            )

        redacted = redact_text(raw).strip()
        if not redacted:
            return None

        if not self.available:
            return None

        payload = {
            "content": redacted,
            "kind": kind,
            "key": key,
            "subject_id": str(subject_id),
            "scope": str(scope),
            "session_id": str(session_id or ""),
            "metadata": dict(metadata or {}),
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # A keyed memory is corrected in place rather than appended to, so a
            # revised fact replaces the stale one instead of sitting beside it
            # and letting recall return both.
            if key is not None:
                existing = self._find_by_key(subject_id, key, scope)
                if existing is not None:
                    self._store.put(self.namespace(subject_id, scope), existing, payload)
                    return existing

            result = self._manage_tool(subject_id, scope).invoke(
                {"content": json.dumps(payload, ensure_ascii=False), "action": "create"}
            )
            return _memory_id_from(result)
        except Exception as exc:  # noqa: BLE001
            self._error = f"{type(exc).__name__}: {exc}"
            return None

    def forget(self, subject_id: str, scope: str = "applicant") -> int:
        """Erase everything held about one subject."""
        if not self.available:
            return 0
        namespace = self.namespace(subject_id, scope)
        try:
            items = self._store.search(namespace, limit=1000)
            for item in items:
                self._store.delete(namespace, item.key)
            return len(items)
        except Exception as exc:  # noqa: BLE001
            self._error = f"{type(exc).__name__}: {exc}"
            return 0

    # -- reads ----------------------------------------------------------------

    def _find_by_key(self, subject_id: str, key: str, scope: str) -> str | None:
        """The id of this subject's memory under ``key``, if one exists."""
        for record in self.recall(subject_id, scope=scope, limit=1000):
            if record.metadata.get("__key__") == key:
                return record.id
        return None

    def recall(
        self, subject_id: str, *, scope: str = "applicant", limit: int = 10
    ) -> list[SemanticRecord]:
        """Everything held about one subject, newest first."""
        if not self.available:
            return []
        try:
            items = self._store.search(self.namespace(subject_id, scope), limit=limit)
        except Exception as exc:  # noqa: BLE001
            self._error = f"{type(exc).__name__}: {exc}"
            return []
        records = [_to_record(i, subject_id, scope) for i in items]
        records.sort(key=lambda r: (r.updated_at or "", r.created_at or ""), reverse=True)
        return records

    def search(
        self,
        subject_id: str,
        query: str,
        *,
        scope: str = "applicant",
        limit: int = 5,
    ) -> list[SemanticRecord]:
        """Semantic recall through LangMem's search tool, inside one namespace."""
        if not self.available:
            return []
        try:
            raw = self._search_tool(subject_id, scope).invoke(
                {"query": str(query or ""), "limit": int(limit)}
            )
        except Exception as exc:  # noqa: BLE001
            self._error = f"{type(exc).__name__}: {exc}"
            return []

        try:
            items = json.loads(raw) if isinstance(raw, str) else list(raw or [])
        except json.JSONDecodeError:
            return []
        return [_to_record(i, subject_id, scope) for i in items]

    def render(self, subject_id: str, *, scope: str = "applicant", limit: int = 10) -> str:
        """Recalled memory, rendered for a prompt."""
        records = self.recall(subject_id, scope=scope, limit=limit)
        if not records:
            return ""
        lines = [f"Prior context for {subject_id}:"]
        lines.extend(f"- [{r.kind or 'note'}] {r.content}" for r in records)
        return "\n".join(lines)

    def count(self, subject_id: str, *, scope: str = "applicant") -> int:
        return len(self.recall(subject_id, scope=scope, limit=1000))

    def subjects(self, scope: str = "applicant") -> list[str]:
        """Subjects with at least one memory, for bookkeeping and tests."""
        if not self.available:
            return []
        try:
            namespaces = self._store.list_namespaces(prefix=(NAMESPACE_ROOT, str(scope)))
        except Exception as exc:  # noqa: BLE001
            self._error = f"{type(exc).__name__}: {exc}"
            return []
        return sorted({ns[-1] for ns in namespaces if len(ns) >= 3})


def _memory_id_from(result: Any) -> str | None:
    """LangMem reports a write as ``'created memory <uuid>'``."""
    text = str(result or "")
    parts = text.strip().split()
    return parts[-1] if parts else None


def _to_record(item: Any, subject_id: str, scope: str) -> SemanticRecord:
    """Normalise a store ``Item`` or a search-tool dict into one shape."""
    if isinstance(item, Mapping):
        key = str(item.get("key") or "")
        value = item.get("value") or {}
        created = item.get("created_at")
        updated = item.get("updated_at")
        score = item.get("score")
    else:
        key = str(getattr(item, "key", "") or "")
        value = getattr(item, "value", {}) or {}
        created = getattr(item, "created_at", None)
        updated = getattr(item, "updated_at", None)
        score = getattr(item, "score", None)

    inner = value.get("content") if isinstance(value, Mapping) else None
    payload: dict[str, Any] = {}
    if isinstance(inner, str):
        try:
            decoded = json.loads(inner)
            if isinstance(decoded, dict):
                payload = decoded
        except json.JSONDecodeError:
            payload = {"content": inner}
    elif isinstance(inner, Mapping):
        payload = dict(inner)

    return SemanticRecord(
        id=key,
        subject_id=str(payload.get("subject_id") or subject_id),
        scope=str(payload.get("scope") or scope),
        content=str(payload.get("content") or inner or ""),
        kind=payload.get("kind"),
        metadata={
            **dict(payload.get("metadata") or {}),
            "__key__": payload.get("key"),
            "session_id": payload.get("session_id"),
        },
        created_at=str(created) if created is not None else None,
        updated_at=str(updated) if updated is not None else None,
        score=float(score) if isinstance(score, (int, float)) else None,
    )
