"""Assemble — the four operations, in the order that keeps them honest.

    isolate -> select -> compress -> write

The order is not arbitrary:

* **isolate first.** Selecting before isolating would let applicant text be
  selected *as* evidence; compressing before isolating would let a summarizer
  read it as instruction.
* **select before compress.** Compressing everything and then choosing wastes the
  compression and, where summarization is involved, the model call.
* **write last.** The scratchpad records what was actually assembled, not what
  was considered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from src.context.compress import CompressionResult, compress_evidence
from src.context.isolate import Compartment, IsolatedContext, isolate
from src.context.select import SelectionResult, select_for_decision, select_for_role
from src.context.write import Scratchpad

#: A conservative default for a flash-tier context window, leaving room for the
#: instruction, the question and the answer.
DEFAULT_EVIDENCE_BUDGET_CHARS = 12_000


@dataclass
class AssembledContext:
    """Prompt-ready context, with the audit trail of how it was built."""

    prompt_text: str
    isolated: IsolatedContext
    selection: SelectionResult
    compression: CompressionResult
    scratchpad: Scratchpad | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def requires_human_review(self) -> bool:
        return self.isolated.requires_human_review

    def summary(self) -> dict[str, Any]:
        return {
            "prompt_chars": len(self.prompt_text),
            "isolation": self.isolated.summary(),
            "selection": self.selection.summary(),
            "compression": self.compression.summary(),
            "notes": self.notes,
        }


def build_context(
    *,
    role: str,
    policy_evidence: Sequence[Mapping[str, Any]] = (),
    computed_facts: Mapping[str, Any] | None = None,
    application_facts: Mapping[str, Any] | None = None,
    untrusted_text: Any = None,
    eligibility: Mapping[str, Any] | None = None,
    risk: Mapping[str, Any] | None = None,
    budget_chars: int = DEFAULT_EVIDENCE_BUDGET_CHARS,
    scratchpad: Scratchpad | None = None,
) -> AssembledContext:
    """Assemble context for one worker role.

    ``role`` drives selection. ``"narrative"`` selects what the decision turned
    on; every other role selects by its policy families.
    """
    # 1. isolate
    isolated = isolate(
        policy_evidence=policy_evidence,
        computed_facts=computed_facts,
        application_facts=application_facts,
        untrusted_text=untrusted_text,
    )

    # 2. select
    evidence = isolated.get(Compartment.POLICY_EVIDENCE)
    if role == "narrative" and eligibility is not None:
        selection = select_for_decision(evidence, eligibility, risk)
    else:
        selection = select_for_role(evidence, role)

    if not selection.selected and evidence:
        # Never starve a worker because a taxonomy did not match. Say so.
        selection.selected = list(evidence)
        selection.reasons["__fallback__"] = (
            f"no chunk matched role '{role}'; passing all {len(evidence)} rather "
            f"than reasoning with none"
        )

    # 3. compress
    compression = compress_evidence(selection.selected, max_chars=budget_chars)

    # Render from the selected-and-compressed evidence, not the original.
    narrowed = IsolatedContext(
        compartments={
            **isolated.compartments,
            Compartment.POLICY_EVIDENCE: selection.selected,
        },
        injection_findings=isolated.injection_findings,
        requires_human_review=isolated.requires_human_review,
    )
    prompt_text = narrowed.render()
    if compression.dropped_items:
        prompt_text = prompt_text.replace(
            "## POLICY_EVIDENCE",
            f"## POLICY_EVIDENCE\n_{compression.dropped_items} chunk(s) omitted for budget._",
            1,
        )

    # 4. write
    notes: list[str] = []
    if isolated.injection_findings:
        notes.append(
            f"applicant text carried {sorted(set(isolated.injection_findings))}; "
            f"quarantined as data and flagged for review"
        )
    if scratchpad is not None:
        scratchpad.write(
            "context",
            f"assembled for '{role}': {len(selection.selected)} of "
            f"{selection.considered} chunks, {len(prompt_text)} chars",
            role=role,
            selected=len(selection.selected),
            dropped=selection.dropped,
            compression=compression.method,
        )

    return AssembledContext(
        prompt_text=prompt_text,
        isolated=isolated,
        selection=selection,
        compression=compression,
        scratchpad=scratchpad,
        notes=notes,
    )
