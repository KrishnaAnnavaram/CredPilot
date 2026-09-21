"""Write — the run scratchpad.

The "write" operation in context engineering is recording what happened in a
form that can be read back later, rather than holding it all in the prompt.
Here it is a scratchpad the graph appends to as it works: which questions were
asked, which rules came back, what was computed, what was decided.

Two properties it has to have, for the same reason the audit trail does:

* **redacted on write** — an applicant identifier that reaches the scratchpad
  reaches whatever the scratchpad is later written to;
* **serializable** — it crosses the checkpointer, so it is plain data, not
  objects only this process can read back.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.guardrails.redaction import redact_structure, redact_text


@dataclass
class ContextRecord:
    """One thing that happened, with when and what kind."""

    kind: str
    summary: str
    detail: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "kind": self.kind,
            "summary": self.summary,
            "detail": self.detail,
        }


@dataclass
class Scratchpad:
    """An append-only record of a run, safe to persist.

    Redaction happens at :meth:`write`, not at read: something that was never
    recorded cannot leak from a later copy of the record.
    """

    application_id: str | None = None
    records: list[ContextRecord] = field(default_factory=list)

    def write(self, kind: str, summary: str, **detail: Any) -> ContextRecord:
        record = ContextRecord(
            kind=kind,
            summary=redact_text(summary),
            detail=redact_structure(detail),
        )
        self.records.append(record)
        return record

    def of_kind(self, kind: str) -> list[ContextRecord]:
        return [r for r in self.records if r.kind == kind]

    def render(self, *, kinds: tuple[str, ...] | None = None, limit: int | None = None) -> str:
        """Render for a prompt — most recent last, oldest dropped first."""
        records = [r for r in self.records if kinds is None or r.kind in kinds]
        if limit:
            records = records[-limit:]
        return "\n".join(f"- [{r.kind}] {r.summary}" for r in records)

    def as_dict(self) -> dict[str, Any]:
        return {
            "application_id": self.application_id,
            "record_count": len(self.records),
            "records": [r.as_dict() for r in self.records],
        }

    def save(self, path: "str | Path") -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.as_dict(), indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        return target

    @classmethod
    def load(cls, path: "str | Path") -> "Scratchpad":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        pad = cls(application_id=payload.get("application_id"))
        for record in payload.get("records", []):
            pad.records.append(
                ContextRecord(
                    kind=record["kind"],
                    summary=record["summary"],
                    detail=record.get("detail", {}),
                    timestamp=record["timestamp"],
                )
            )
        return pad

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> "Scratchpad":
        """Build a scratchpad from a finished graph state.

        Used to hand a completed run to the narrative node and to memory without
        either of them having to understand the graph's internals.
        """
        pad = cls(application_id=state.get("application_id"))
        pad.write(
            "intake",
            f"{state.get('application_id')} routed to {state.get('loan_domain')} "
            f"as of {state.get('as_of_date')}",
            loan_domain=state.get("loan_domain"),
            as_of_date=state.get("as_of_date"),
        )
        for question in state.get("policy_questions") or []:
            pad.write("policy_question", question.get("query", ""), topic=question.get("topic"))

        evidence = state.get("policy_evidence") or []
        if evidence:
            pad.write(
                "evidence",
                f"{len(evidence)} policy chunks retrieved, "
                f"{len({e.get('policy_id') for e in evidence})} distinct policies",
                citations=sorted({e.get("citation") for e in evidence if e.get("citation")})[:20],
            )

        calculations = state.get("calculations") or {}
        if calculations.get("ratios"):
            pad.write(
                "calculation",
                ", ".join(f"{k}={v}" for k, v in sorted(calculations["ratios"].items())),
                formula_version=calculations.get("formula_version"),
            )

        eligibility = state.get("eligibility") or {}
        if eligibility:
            pad.write(
                "eligibility",
                f"{eligibility.get('status')} with {len(eligibility.get('breaches') or [])} breach(es)",
                breaches=eligibility.get("breaches"),
            )

        risk = state.get("risk") or {}
        if risk:
            pad.write("risk", f"{risk.get('level')} {risk.get('flags') or ''}")

        recommendation = state.get("recommendation") or {}
        if recommendation:
            pad.write(
                "recommendation",
                f"{recommendation.get('outcome')} "
                f"(human review: {state.get('requires_human_review')})",
                citations=recommendation.get("citations", [])[:20],
            )
        return pad
