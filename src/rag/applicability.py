"""Applicability and temporal validation.

Retrieval must return the policy that governed the file on the day it was
underwritten — not the newest document in the corpus. The mortgage corpus makes
this concrete: ``POL-DTI-001`` exists at v1.0 (effective 2026-01-01, allowing 45%
back-end DTI unconditionally) and v2.0 (effective 2026-07-01, 43% with a
compensating-factor extension). A file at 44% underwritten on 2026-06-25 passes;
the same ratio on 2026-07-08 breaches. Retrieving the wrong version silently
flips the decision, so version selection is a hard filter, not a ranking hint.

Two mechanisms, applied in order:

1. **Effective-date window** — a document is eligible when
   ``effective_date <= as_of_date`` and either no expiration is published or
   ``as_of_date <= expiration_date``.
2. **Latest-eligible version per policy id** — where several versions of the same
   policy are eligible, the one with the newest effective date on or before the
   as-of date wins, and the others are marked ``SUPERSEDED``.

Product scope (``product_scope``, ``purpose_scope``, ``occupancy_scope``) is a
*soft* signal, not a hard filter: an overlay that omits a scope list still
governs, and over-filtering removes valid evidence. Only the product domain and
the effective-date window are hard.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Sequence

from src.rag.models import ApplicabilityStatus


@dataclass
class ApplicabilityDecision:
    status: ApplicabilityStatus
    reason: str = ""

    @property
    def applicable(self) -> bool:
        return self.status is ApplicabilityStatus.APPLICABLE


def _as_date(value: Any) -> date | None:
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value.strip())
    if isinstance(value, int):
        return date.fromordinal(value)
    return None


def evaluate_temporal(meta: Mapping[str, Any], as_of: date | None) -> ApplicabilityDecision:
    """Check one chunk's effective-date window against the underwriting as-of date."""
    if as_of is None:
        return ApplicabilityDecision(ApplicabilityStatus.UNDETERMINED, "no as_of_date supplied")

    effective = _as_date(meta.get("effective_date"))
    expiration = _as_date(meta.get("expiration_date"))

    if effective is not None and as_of < effective:
        return ApplicabilityDecision(
            ApplicabilityStatus.NOT_YET_EFFECTIVE,
            f"effective {effective.isoformat()} > as-of {as_of.isoformat()}",
        )
    if expiration is not None and as_of > expiration:
        return ApplicabilityDecision(
            ApplicabilityStatus.EXPIRED,
            f"expired {expiration.isoformat()} < as-of {as_of.isoformat()}",
        )
    if effective is None:
        return ApplicabilityDecision(
            ApplicabilityStatus.UNDETERMINED, "document publishes no effective date"
        )
    return ApplicabilityDecision(ApplicabilityStatus.APPLICABLE, "within effective window")


def _version_key(version: str | None) -> tuple:
    """Sort versions numerically where possible (``10.0`` after ``2.0``)."""
    if not version:
        return (0,)
    parts = []
    for piece in str(version).split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def select_effective_versions(
    metadatas: Sequence[Mapping[str, Any]], as_of: date | None
) -> dict[str, tuple[str | None, date | None]]:
    """Pick the governing version of each policy id for a given as-of date.

    Returns ``{policy_id: (version, effective_date)}``. Policies with no eligible
    version are absent from the mapping.
    """
    best: dict[str, tuple[str | None, date | None]] = {}
    for meta in metadatas:
        policy_id = meta.get("policy_id")
        if not policy_id:
            continue
        if not evaluate_temporal(meta, as_of).applicable and as_of is not None:
            continue
        version = meta.get("policy_version")
        effective = _as_date(meta.get("effective_date"))
        current = best.get(policy_id)
        if current is None:
            best[policy_id] = (version, effective)
            continue
        cur_version, cur_effective = current
        cur_eff_ord = cur_effective.toordinal() if cur_effective else -1
        new_eff_ord = effective.toordinal() if effective else -1
        if (new_eff_ord, _version_key(version)) > (cur_eff_ord, _version_key(cur_version)):
            best[policy_id] = (version, effective)
    return best


def classify(
    meta: Mapping[str, Any],
    *,
    as_of: date | None,
    governing_versions: Mapping[str, tuple[str | None, date | None]] | None = None,
    temporal_filtering: bool = True,
) -> ApplicabilityDecision:
    """Full applicability verdict for one chunk."""
    if not temporal_filtering:
        return ApplicabilityDecision(ApplicabilityStatus.UNDETERMINED, "temporal filtering off")

    decision = evaluate_temporal(meta, as_of)
    if not decision.applicable:
        return decision

    if governing_versions is not None:
        policy_id = meta.get("policy_id")
        governing = governing_versions.get(policy_id) if policy_id else None
        if governing is not None:
            governing_version, _ = governing
            if meta.get("policy_version") != governing_version:
                return ApplicabilityDecision(
                    ApplicabilityStatus.SUPERSEDED,
                    f"{policy_id} v{meta.get('policy_version')} superseded by "
                    f"v{governing_version} at as-of {as_of.isoformat() if as_of else '?'}",
                )
    return decision


def scope_affinity(meta: Mapping[str, Any], context: Mapping[str, Any]) -> float:
    """A small, bounded ranking boost for chunks matching the application context.

    Deliberately a *soft* signal in ``[0, 1]``: scope metadata is incomplete
    across the corpus, and hard-filtering on it would drop policies that govern
    every programme. Only ever added on top of the reranker's ordering.
    """
    hits = 0
    checks = 0
    pairs = (
        ("product_scope", context.get("product_family")),
        ("purpose_scope", context.get("loan_purpose")),
        ("occupancy_scope", context.get("occupancy_type")),
        ("product_scope", context.get("education_product_code")),
    )
    for field, wanted in pairs:
        if not wanted:
            continue
        raw = meta.get(field)
        if not raw:
            continue
        checks += 1
        values = {v.strip().lower() for v in str(raw).split("|") if v.strip()}
        if str(wanted).strip().lower() in values:
            hits += 1
    return hits / checks if checks else 0.0
