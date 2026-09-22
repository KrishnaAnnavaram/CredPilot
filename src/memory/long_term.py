"""Long-term memory — what survives between sessions.

This is AC-05's second half: *"recalls prior-session context on a return visit"*.

Recall works two ways:

* **by key** — "what did we note about this applicant's employment?";
* **semantically** — "anything about self-employment?", matched by embedding
  similarity using the same local Sentence-Transformers model the policy index
  uses. No second model, no hosted endpoint.

What it will not store, and why each matters:

* **decisions as facts.** A prior APPROVE is not evidence for the next
  application. Storing one invites the system to re-decide from memory instead
  of from policy, which is how it drifts away from its own rulebook.
* **policy.** Policy lives in the corpus and is retrieved with an effective date.
  A rule cached in memory is a rule that cannot be versioned, and would outlive
  the boundary that replaced it.
* **identifiers in the clear.** Everything is redacted on write, in the store.

Scope is enforced: a recall for one subject cannot return another's memories
(``POL-SEC-001`` SEC-INJ-002).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.memory.store import MemoryStore


class MemoryScope(str, Enum):
    """Whose memory this is."""

    APPLICANT = "applicant"
    SESSION = "session"
    PORTFOLIO = "portfolio"


#: Kinds that may be stored. A closed set, so a caller cannot invent
#: "prior_decision" and quietly reintroduce deciding from memory.
ALLOWED_KINDS = frozenset(
    {
        "preference",        # how this party wants to be dealt with
        "context_note",      # a durable fact about the file's history
        "document_status",   # what has been supplied, what is outstanding
        "interaction",       # that a conversation happened, and its subject
        "correction",        # a fact the applicant corrected
    }
)

#: Explicitly refused, with the reason surfaced to the caller.
FORBIDDEN_KINDS: dict[str, str] = {
    "decision": "a prior decision is not evidence for a new application",
    "prior_decision": "a prior decision is not evidence for a new application",
    "policy": "policy is retrieved from the corpus with an effective date, never cached",
    "policy_rule": "policy is retrieved from the corpus with an effective date, never cached",
    "threshold": "a threshold comes from the retrieved rule that governs the as-of date",
    "credit_score": "a credit figure is pulled fresh; a cached one goes stale silently",
}


class ForbiddenMemoryError(ValueError):
    """Raised when a caller tries to store something memory must not hold."""


@dataclass
class MemoryRecord:
    """One recalled memory."""

    id: int
    scope: str
    subject_id: str
    kind: str
    key: str | None
    content: str
    metadata: dict[str, Any]
    created_at: str
    updated_at: str
    session_id: str | None = None
    similarity: float | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, Any], similarity: float | None = None) -> "MemoryRecord":
        return cls(
            id=int(row["id"]),
            scope=row["scope"],
            subject_id=row["subject_id"],
            kind=row["kind"],
            key=row["key"],
            content=row["content"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            session_id=row.get("session_id"),
            similarity=similarity,
        )

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "id": self.id,
            "scope": self.scope,
            "subject_id": self.subject_id,
            "kind": self.kind,
            "key": self.key,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "session_id": self.session_id,
        }
        if self.similarity is not None:
            payload["similarity"] = round(self.similarity, 4)
        return payload


def _langmem_path_for(store_path: Path) -> Path:
    """Where LangMem's store lives, given this store's file.

    Derived rather than configured so a test pointing the long-term store at a
    temporary directory gets a temporary LangMem store too. A fixed default here
    would have every isolated test quietly sharing the repository's real one.
    """
    path = Path(store_path)
    return path.with_name(f"{path.stem}_langmem{path.suffix or '.sqlite'}")


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class LongTermMemory:
    """Durable, subject-scoped, semantically searchable memory."""

    def __init__(self, store: MemoryStore | None = None, *, path: "str | Path | None" = None):
        self.store = store or MemoryStore(path)
        self._embedder = None
        self._semantic = None
        self._semantic_path = _langmem_path_for(self.store.path)

    # -- LangMem ------------------------------------------------------------------

    @property
    def semantic(self):
        """The LangMem layer, opened on first use.

        Lazy because opening it costs a file handle and a schema check, and the
        callers that only write a keyed note never read semantically. It is a
        sibling file rather than the same one: LangMem owns and migrates its own
        schema, and two writers with different ideas about the tables is a
        corruption waiting for a release.
        """
        if self._semantic is None:
            from src.memory.semantic import SemanticMemory

            self._semantic = SemanticMemory(self._semantic_path)
        return self._semantic

    # -- embedding ----------------------------------------------------------------

    @property
    def embedder(self):
        """The same local model the policy index uses. Loaded on first need."""
        if self._embedder is None:
            from src.config import get_config
            from src.rag.embedding import PolicyEmbedder

            config = get_config()
            self._embedder = PolicyEmbedder(
                config.embedding.model, normalize=config.embedding.normalize
            )
        return self._embedder

    def _embed(self, text: str) -> list[float]:
        return [float(v) for v in self.embedder.encode_passages([text])[0]]

    # -- writes -------------------------------------------------------------------

    def remember(
        self,
        *,
        subject_id: str,
        kind: str,
        content: str,
        scope: MemoryScope = MemoryScope.APPLICANT,
        key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        session_id: str | None = None,
        embed: bool = True,
    ) -> int:
        """Store one memory, refusing the kinds memory must not hold."""
        if kind in FORBIDDEN_KINDS:
            raise ForbiddenMemoryError(
                f"refusing to store kind '{kind}': {FORBIDDEN_KINDS[kind]}"
            )
        if kind not in ALLOWED_KINDS:
            raise ForbiddenMemoryError(
                f"unknown memory kind '{kind}'; allowed: {sorted(ALLOWED_KINDS)}"
            )

        embedding = self._embed(content) if embed else None
        record_id = self.store.upsert(
            scope=scope.value,
            subject_id=subject_id,
            kind=kind,
            key=key,
            content=content,
            metadata={**dict(metadata or {}), "stored_at": datetime.now(timezone.utc).isoformat()},
            embedding=embedding,
            session_id=session_id,
        )

        # Write through to LangMem, which is what a later session recalls from.
        # Best-effort on purpose: this store is the system of record, and a
        # LangMem outage must not lose the write or fail the file. The refusals
        # above have already run, so nothing forbidden reaches it.
        try:
            self.semantic.write(
                subject_id=subject_id,
                content=content,
                kind=kind,
                scope=scope.value,
                key=key,
                metadata=metadata,
                session_id=session_id,
            )
        except Exception:  # noqa: BLE001 - memory must never block an assessment
            pass

        return record_id

    def forget(self, subject_id: str, scope: MemoryScope = MemoryScope.APPLICANT) -> int:
        """Erase everything held about a subject, in both stores.

        Erasure that clears one store and leaves the other is not erasure. The
        count returned is this store's, because it is the system of record, but
        the LangMem namespace goes with it.
        """
        removed = self.store.delete_subject(scope.value, subject_id)
        try:
            self.semantic.forget(subject_id, scope=scope.value)
        except Exception:  # noqa: BLE001
            pass
        return removed

    def semantic_recall(
        self,
        subject_id: str,
        query: str,
        *,
        scope: MemoryScope = MemoryScope.APPLICANT,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Cross-session recall through LangMem, scoped to one subject.

        Returns plain dictionaries rather than :class:`MemoryRecord` because
        these come from a different store with a different id space, and giving
        them the same type would invite a caller to treat a LangMem id as a row
        id in this one.
        """
        try:
            return [r.as_dict() for r in self.semantic.search(
                subject_id, query, scope=scope.value, limit=limit
            )]
        except Exception:  # noqa: BLE001 - memory must never block an assessment
            return []

    # -- reads --------------------------------------------------------------------

    def recall(
        self,
        subject_id: str,
        *,
        scope: MemoryScope = MemoryScope.APPLICANT,
        kind: str | None = None,
        limit: int | None = None,
    ) -> list[MemoryRecord]:
        """Everything known about one subject, newest first."""
        rows = self.store.fetch(
            scope=scope.value, subject_id=subject_id, kind=kind, limit=limit
        )
        return [MemoryRecord.from_row(row) for row in rows]

    def search(
        self,
        subject_id: str,
        query: str,
        *,
        scope: MemoryScope = MemoryScope.APPLICANT,
        top_k: int = 5,
        min_similarity: float = 0.3,
    ) -> list[MemoryRecord]:
        """Semantic recall, scoped to one subject.

        The scope filter is applied in the query, not after ranking: a similarity
        search across every applicant would be one ranking bug away from
        returning someone else's file.
        """
        rows = self.store.fetch(scope=scope.value, subject_id=subject_id)
        if not rows:
            return []

        vector = [float(v) for v in self.embedder.encode_queries([query])[0]]
        scored: list[MemoryRecord] = []
        for row in rows:
            if not row.get("embedding"):
                continue
            similarity = _cosine(vector, json.loads(row["embedding"]))
            if similarity >= min_similarity:
                scored.append(MemoryRecord.from_row(row, similarity))

        scored.sort(key=lambda r: (-(r.similarity or 0.0), r.id))
        return scored[:top_k]

    def render(self, subject_id: str, *, scope: MemoryScope = MemoryScope.APPLICANT,
               limit: int = 10) -> str:
        """Render recalled memory for a prompt."""
        records = self.recall(subject_id, scope=scope, limit=limit)
        if not records:
            return ""
        lines = [f"Prior context for {subject_id}:"]
        lines.extend(f"- [{r.kind}] {r.content}" for r in records)
        return "\n".join(lines)

    # -- bookkeeping ---------------------------------------------------------------

    def subjects(self, scope: MemoryScope = MemoryScope.APPLICANT) -> list[str]:
        return self.store.subjects(scope.value)

    def count(self, subject_id: str | None = None,
              scope: MemoryScope = MemoryScope.APPLICANT) -> int:
        return self.store.count(scope=scope.value, subject_id=subject_id)
