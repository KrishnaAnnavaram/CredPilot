"""Tiered memory (REQ-075).

*"src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log |
short + long/semantic memory; cross-session recall test with committed output
log"*

Two tiers, because they answer different questions:

* **Short-term** (:mod:`~src.memory.short_term`) — what happened in *this*
  conversation. Lives on the LangGraph checkpointer, scoped to a thread, and
  disappears with it.
* **Long-term** (:mod:`~src.memory.long_term`) — what this system knows about an
  applicant or a broker across *separate* sessions. Lives in SQLite, survives the
  process, and is searchable semantically as well as by key.
* **Semantic / cross-session** (:mod:`~src.memory.semantic`) — the same durable
  facts through **LangMem**, over a LangGraph SQLite store, which is what the
  source document's Memory row asks for alongside the checkpointer. Every
  long-term write goes through to it, and a returning session recalls from it.

What memory is deliberately **not** allowed to do here:

* it never stores a decision as a fact to be reused — a prior APPROVE is not
  evidence for the next application, and re-deciding from memory rather than from
  policy is how a system drifts away from its own rulebook;
* it never stores an applicant identifier in the clear — everything written is
  redacted first, exactly as the audit trail is;
* it is scoped by subject, so recalling one applicant cannot surface another's
  file (``POL-SEC-001`` SEC-INJ-002).
"""

from src.memory.long_term import (
    LongTermMemory,
    MemoryRecord,
    MemoryScope,
)
from src.memory.semantic import (
    LANGMEM_DB,
    ForbiddenMemoryContent,
    SemanticMemory,
    SemanticRecord,
)
from src.memory.short_term import (
    ShortTermMemory,
    Turn,
)
from src.memory.store import MEMORY_DB, MemoryStore

__all__ = [
    "LANGMEM_DB",
    "MEMORY_DB",
    "ForbiddenMemoryContent",
    "LongTermMemory",
    "MemoryRecord",
    "MemoryScope",
    "MemoryStore",
    "SemanticMemory",
    "SemanticRecord",
    "ShortTermMemory",
    "Turn",
]
