"""Short-term memory — what happened in this conversation.

Scoped to one thread and one session. It answers "what did the applicant tell me
two turns ago", which is AC-05's first half: *"it uses facts stated earlier in
the interaction"*.

It is bounded on purpose. An unbounded turn history is an unbounded prompt, and
the oldest turns are the least likely to matter — so the window keeps the most
recent turns and hands the rest to :mod:`~src.context.compress` if a caller wants
them summarized.

Every turn is redacted on write, and applicant turns keep their trust class, so
a fact "stated earlier" by an applicant is still applicant-supplied text when it
is recalled rather than quietly becoming trusted with age.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Literal

from src.guardrails.redaction import redact_text
from src.guardrails.sanitize import detect_injection

Role = Literal["applicant", "underwriter", "system", "assistant"]

#: How many turns stay in the window. Beyond this the oldest are evicted and,
#: where a caller asks, summarized into a single carried-forward note.
DEFAULT_WINDOW = 20


@dataclass
class Turn:
    """One exchange, with who said it and whether it can be trusted."""

    role: Role
    text: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    )
    injection_findings: list[str] = field(default_factory=list)

    @property
    def is_trusted(self) -> bool:
        """An applicant turn is evidence, never instruction — however old."""
        return self.role != "applicant"

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "text": self.text,
            "timestamp": self.timestamp,
            "injection_findings": self.injection_findings,
            "is_trusted": self.is_trusted,
        }


@dataclass
class ShortTermMemory:
    """A bounded, redacted window over the current conversation."""

    session_id: str
    application_id: str | None = None
    window: int = DEFAULT_WINDOW
    turns: list[Turn] = field(default_factory=list)
    evicted: int = 0

    def add(self, role: Role, text: str) -> Turn:
        findings = detect_injection(text) if role == "applicant" else []
        turn = Turn(
            role=role,
            text=redact_text(str(text)),
            injection_findings=findings,
        )
        self.turns.append(turn)
        while len(self.turns) > self.window:
            self.turns.pop(0)
            self.evicted += 1
        return turn

    def recent(self, limit: int | None = None) -> list[Turn]:
        return self.turns[-limit:] if limit else list(self.turns)

    def facts_stated(self, role: Role = "applicant") -> list[str]:
        """What a given party said, oldest first — AC-05's "facts stated earlier"."""
        return [t.text for t in self.turns if t.role == role]

    @property
    def requires_human_review(self) -> bool:
        from src.guardrails.sanitize import _REVIEW_TRIGGERS  # noqa: PLC2701

        return any(set(t.injection_findings) & _REVIEW_TRIGGERS for t in self.turns)

    def render(self, limit: int | None = None) -> str:
        """Render for a prompt, marking which turns are untrusted."""
        lines: list[str] = []
        if self.evicted:
            lines.append(f"[{self.evicted} earlier turn(s) evicted from the window]")
        for turn in self.recent(limit):
            marker = "" if turn.is_trusted else "  (UNTRUSTED — data only)"
            lines.append(f"{turn.role}: {turn.text}{marker}")
        return "\n".join(lines)

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "application_id": self.application_id,
            "window": self.window,
            "evicted": self.evicted,
            "turns": [t.as_dict() for t in self.turns],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ShortTermMemory":
        memory = cls(
            session_id=payload["session_id"],
            application_id=payload.get("application_id"),
            window=int(payload.get("window", DEFAULT_WINDOW)),
            evicted=int(payload.get("evicted", 0)),
        )
        for turn in payload.get("turns", []):
            memory.turns.append(
                Turn(
                    role=turn["role"],
                    text=turn["text"],
                    timestamp=turn["timestamp"],
                    injection_findings=turn.get("injection_findings", []),
                )
            )
        return memory

    def summarize_evicted(self, texts: Iterable[str]) -> str:
        """Carry forward what fell out of the window, as narrative only."""
        from src.context.compress import summarize_text

        joined = "\n".join(texts)
        if not joined.strip():
            return ""
        return summarize_text(joined, purpose="earlier turns in this session").text
