"""Select — choose what this turn needs, not everything the run has.

A full mortgage assessment gathers around fifty evidence chunks across eight
policy questions. The eligibility agent needs the affordability and leverage
rules; the risk agent needs fraud, occupancy and identity; the narrative needs
whatever the decision actually turned on. Passing all fifty to each of them
costs tokens and, worse, buries the three rules that matter among forty-seven
that do not.

Selection here is deterministic and explainable. Every chunk kept can be traced
to why it was kept, which matters when a reviewer asks why a rule was or was not
in front of the model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

#: Which policy families each worker role cares about, by rule-id prefix. Derived
#: from the corpora's own identifier taxonomy rather than invented: mortgage uses
#: ``DTI-``, ``AST-``, ``CRD-`` and so on; education uses ``EDU-INC-``,
#: ``EDU-COS-``, ``EDU-FRD-``.
ROLE_PREFIXES: dict[str, tuple[str, ...]] = {
    "eligibility": (
        "DTI-", "AST-", "CONV-", "INC-", "EMP-", "LIA-", "GEN-", "JMB-", "FHA-",
        "VA-", "USD-", "CRD-SCR-",
        "EDU-INC-", "EDU-UW-", "EDU-COS-", "EDU-SCH-", "EDU-RG-", "EDU-INTL-",
    ),
    "risk": (
        "FRD-", "KYC-", "CRD-EVT-", "CRD-DLQ-", "PRP-", "VAL-", "TTL-", "SEC-",
        "EDU-FRD-", "EDU-FL-", "EDU-EXC-",
    ),
    "recommendation": (
        "DEC-", "UWR-", "GEN-", "DTI-BRE-",
        "EDU-GOV-", "EDU-AA-", "EDU-DIS-", "EDU-EXC-",
    ),
    "narrative": (),  # decided by the decision itself; see select_for_decision
}


@dataclass
class SelectionResult:
    """What was selected, and why each item survived."""

    selected: list[Mapping[str, Any]] = field(default_factory=list)
    reasons: dict[str, str] = field(default_factory=dict)
    considered: int = 0

    @property
    def dropped(self) -> int:
        return self.considered - len(self.selected)

    def summary(self) -> dict[str, Any]:
        return {
            "considered": self.considered,
            "selected": len(self.selected),
            "dropped": self.dropped,
            "reasons": dict(sorted(self.reasons.items())),
        }


def _identifier(chunk: Mapping[str, Any]) -> str:
    return str(chunk.get("rule_id") or chunk.get("citation") or chunk.get("chunk_id") or "")


def select_for_role(
    evidence: Sequence[Mapping[str, Any]],
    role: str,
    *,
    limit: int | None = None,
) -> SelectionResult:
    """Keep the evidence a given worker role needs.

    A role with no configured prefixes keeps everything — better to pass too much
    than to silently starve a worker whose taxonomy nobody mapped.
    """
    prefixes = ROLE_PREFIXES.get(role)
    result = SelectionResult(considered=len(evidence))

    if not prefixes:
        result.selected = list(evidence)[: limit or len(evidence)]
        for chunk in result.selected:
            result.reasons[_identifier(chunk)] = f"role '{role}' has no filter; kept"
        return result

    for chunk in evidence:
        rule_id = str(chunk.get("rule_id") or "")
        matched = next((p for p in prefixes if rule_id.startswith(p)), None)
        if matched:
            result.selected.append(chunk)
            result.reasons[_identifier(chunk)] = f"matches '{matched}' for role '{role}'"
        if limit and len(result.selected) >= limit:
            break
    return result


def select_evidence(
    evidence: Sequence[Mapping[str, Any]],
    *,
    rule_ids: Iterable[str] = (),
    policy_ids: Iterable[str] = (),
    limit: int | None = None,
) -> SelectionResult:
    """Keep evidence naming specific rules or policies, preserving rank order."""
    wanted_rules = {r for r in rule_ids if r}
    wanted_policies = {p for p in policy_ids if p}
    result = SelectionResult(considered=len(evidence))

    for chunk in evidence:
        rule_id = chunk.get("rule_id")
        policy_id = chunk.get("policy_id")
        if rule_id and rule_id in wanted_rules:
            result.selected.append(chunk)
            result.reasons[_identifier(chunk)] = f"rule {rule_id} was requested"
        elif policy_id and policy_id in wanted_policies:
            result.selected.append(chunk)
            result.reasons[_identifier(chunk)] = f"policy {policy_id} was requested"
        if limit and len(result.selected) >= limit:
            break
    return result


def select_for_decision(
    evidence: Sequence[Mapping[str, Any]],
    eligibility: Mapping[str, Any],
    risk: Mapping[str, Any] | None = None,
    *,
    limit: int = 8,
) -> SelectionResult:
    """Keep exactly the evidence the decision turned on.

    This is what the narrative gets. A rationale should quote the rules that
    decided the file — the breached threshold, the rule that granted an
    extension, the one that could not be evaluated — not a sample of everything
    retrieved.
    """
    wanted: list[str] = []
    for bucket in ("breaches", "indeterminate", "evaluations"):
        for evaluation in eligibility.get(bucket) or []:
            rule_id = evaluation.get("rule_id")
            if rule_id and rule_id not in wanted:
                wanted.append(rule_id)

    # The rule a granted extension depends on is part of the reasoning even
    # though it is not itself an evaluation.
    for evaluation in eligibility.get("evaluations") or []:
        for token in str(evaluation.get("detail", "")).split():
            token = token.strip(",.;()")
            if token.count("-") == 2 and token.upper() == token and token not in wanted:
                wanted.append(token)

    result = select_evidence(evidence, rule_ids=wanted, limit=limit)

    if risk and result.considered and len(result.selected) < limit:
        for flag in risk.get("flags") or []:
            remaining = limit - len(result.selected)
            if remaining <= 0:
                break
            extra = select_for_role(evidence, "risk", limit=remaining)
            for chunk in extra.selected:
                if chunk not in result.selected:
                    result.selected.append(chunk)
                    result.reasons[_identifier(chunk)] = f"risk flag {flag}"
            break
    return result
