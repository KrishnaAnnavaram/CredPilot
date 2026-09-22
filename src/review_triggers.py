"""Mandatory human-review triggers — ``POL-UWR-001`` UWR-HRV-001.

The rule is unusually blunt about its own standing:

    *"The routing table in UWR-HRV-001 is mandatory: a file matching any trigger
    reaches a human regardless of how the rest of the file looks."*

So this is not a scoring input or a risk heuristic. A file that matches one
trigger goes to a human even when every threshold passes, every figure is
comfortable and the risk screen is clean. That is why it is evaluated separately
from eligibility rather than folded into it: an eligible file and a referred file
are not in tension, and treating referral as a kind of failure would put the two
in the same bucket.

The band is read from the retrieved rule, never from here. ``UWR-HRV-001``
carries ``borderline_band_pct_points`` in its parameter table, and a threshold
that lived in Python instead would be a threshold no version boundary could ever
move.

Education has no such number. ``EDU-GOV-002`` defines the four permitted outcomes
and states its referral criterion qualitatively, so the borderline trigger is
reported as unevaluable for that product rather than decided on mortgage's two
points — a threshold from one product governing another is the bleed that
separate collections and a product router exist to prevent.

**What cannot be evaluated.** The rule lists thirteen triggers and this module
evaluates ten. The remaining three — an automated-underwriting result, a
requested policy exception, and a valuation or collateral finding — have no field
in any committed table, and are reported as ``unevaluable`` rather than silently
passing. A trigger nobody checked is not a trigger that did not fire, and a
reviewer reading this output should be able to tell the difference.

That list started at five. "Unsourced large deposit" and "unresolved conflict
between evidence sources" were on it until the data was checked properly: both
live in structured input tables the runtime was already allowed to read.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from src.domain import LendingProductDomain

#: The rule that defines the routing table, per product.
TRIGGER_RULES = {
    LendingProductDomain.MORTGAGE: "UWR-HRV-001",
    LendingProductDomain.EDUCATION_LOAN: "EDU-GOV-002",
}

#: What `UWR-HRV-001` publishes, kept here only so a mortgage file whose routing
#: rule failed to retrieve still gets the tighter, safer treatment rather than
#: none. It is **not** applied to a product whose own rules publish no band —
#: see :func:`evaluate_review_triggers`.
DEFAULT_BORDERLINE_BAND_PCT_POINTS = 2.0

#: Products whose routing rule defines a borderline band at all.
#:
#: Mortgage's `UWR-HRV-001` sets `borderline_band_pct_points`. Education's
#: `EDU-GOV-002` defines the four permitted outcomes and states its referral
#: criterion qualitatively — "falls outside automated decision boundaries and
#: requires manual adjudication" — with no numeric band anywhere. Borrowing
#: mortgage's two points for an education loan would be exactly the cross-product
#: bleed that separate collections and a product router exist to prevent, and the
#: referral it produced would cite an education rule for a mortgage threshold.
PRODUCTS_WITH_A_BORDERLINE_BAND = frozenset({LendingProductDomain.MORTGAGE})

#: Triggers named by UWR-HRV-001 that no committed table has a field for.
#:
#: This list was longer. "Unsourced large deposit" and "unresolved conflict
#: between evidence sources" were on it until the data was checked properly —
#: ``asset_transactions.large_deposit_flag`` with ``source_status``, and
#: ``verifications.result``, both already on the INPUT allowlist. Claiming a
#: control was impossible when it was merely unwritten is a worse error than
#: leaving it unwritten, so the three that remain have been verified absent
#: rather than assumed so.
UNEVALUABLE_TRIGGERS = (
    "automated underwriting refer or caution result",
    "requested policy exception",
    "valuation or collateral finding",
)

#: Verification outcomes that mean the evidence did not line up. ``VERIFIED`` is
#: clean; a flood-determination row carries a FEMA zone code rather than a status
#: and is filtered out by category before this is consulted.
_CONFLICTING_VERIFICATION_RESULTS = frozenset({"CONFLICT", "REFERRED", "DISCREPANCY", "FAILED"})


@dataclass
class ReviewTrigger:
    """One matched trigger, with what matched and why it counts."""

    name: str
    detail: str
    citation: str
    observed: float | None = None
    threshold: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "trigger": self.name,
            "detail": self.detail,
            "citation": self.citation,
            "observed": self.observed,
            "threshold": self.threshold,
        }


@dataclass
class ReviewAssessment:
    """Every trigger evaluated for one file."""

    triggers: list[ReviewTrigger] = field(default_factory=list)
    band_pct_points: float | None = DEFAULT_BORDERLINE_BAND_PCT_POINTS
    band_from_policy: bool = False
    rule_citation: str | None = None
    unevaluable: list[str] = field(default_factory=lambda: list(UNEVALUABLE_TRIGGERS))

    @property
    def required(self) -> bool:
        return bool(self.triggers)

    @property
    def reasons(self) -> list[str]:
        return [f"{t.detail} ({t.citation})" for t in self.triggers]

    def as_dict(self) -> dict[str, Any]:
        return {
            "human_review_required": self.required,
            "triggers": [t.as_dict() for t in self.triggers],
            "trigger_count": len(self.triggers),
            "borderline_band_pct_points": self.band_pct_points,
            "borderline_band_from_policy": self.band_from_policy,
            "rule_citation": self.rule_citation,
            "unevaluable_triggers": self.unevaluable,
            "unevaluable_note": (
                "the packet schema carries no field for these; they were not checked, "
                "which is not the same as their having passed"
            ),
        }


def _find_rule(evidence: Sequence[Mapping[str, Any]], rule_id: str) -> Mapping[str, Any] | None:
    for item in evidence:
        if item.get("rule_id") == rule_id:
            return item
    return None


def _income_types(packet: Mapping[str, Any]) -> set[str]:
    rows = packet.get("declared_income") or []
    return {str(r.get("income_type", "")).lower() for r in rows}


def evaluate_review_triggers(
    domain: LendingProductDomain,
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
    eligibility: Mapping[str, Any],
    risk: Mapping[str, Any],
    *,
    security_findings: Sequence[str] = (),
) -> ReviewAssessment:
    """Apply the mandatory human-review routing table to one file."""
    from src.rules import parameters_of

    rule_id = TRIGGER_RULES.get(domain)
    rule = _find_rule(evidence, rule_id) if rule_id else None
    citation = rule.get("citation") if rule else f"{rule_id} (not retrieved)"

    assessment = ReviewAssessment(rule_citation=citation)

    if rule:
        parameters = parameters_of(rule)
        band = parameters.get("borderline_band_pct_points")
        if isinstance(band, (int, float)):
            assessment.band_pct_points = float(band)
            assessment.band_from_policy = True

    def add(name: str, detail: str, observed: float | None = None,
            threshold: float | None = None) -> None:
        assessment.triggers.append(
            ReviewTrigger(name=name, detail=detail, citation=citation,
                          observed=observed, threshold=threshold)
        )

    # -- a decline always reaches a human ------------------------------------------
    if eligibility.get("status") == "INELIGIBLE":
        add("decline", "a decline recommendation is a mandatory human-review trigger")

    # -- borderline affordability --------------------------------------------------
    # Only where this product's own policy sets a band. Where it does not, the
    # trigger is recorded as unevaluable rather than decided on another product's
    # number.
    evaluations: list[Mapping[str, Any]] = []
    if not assessment.band_from_policy and domain not in PRODUCTS_WITH_A_BORDERLINE_BAND:
        # Naming a width here would be naming the other product's width.
        assessment.unevaluable = sorted({
            *assessment.unevaluable,
            "an affordability result near its limit "
            "(this product's rules publish no borderline band)",
        })
        assessment.band_pct_points = None
    else:
        evaluations = list(eligibility.get("evaluations") or [])

    # The band is in percentage points, and the ratios are fractions, so it is
    # converted once here rather than at each comparison.
    band = (assessment.band_pct_points or 0.0) / 100.0
    for evaluation in evaluations:
        observed = evaluation.get("observed")
        applied = evaluation.get("threshold")
        if observed is None or applied is None:
            continue
        if evaluation.get("comparator") not in ("<=", "<"):
            continue
        # The band is in percentage points, so it means nothing against a
        # measure that is not a ratio. Days past a freshness window, dollars of
        # unsourced deposits and a loan amount all compare with "<=" and none of
        # them is a percentage: a freshness evaluation reporting 0 days over a
        # 0-day allowance referred every clean file as "borderline" until this
        # check existed.
        if str(evaluation.get("unit", "ratio")) != "ratio":
            continue

        # Measured against the tighter of the programme limit and the limit
        # actually applied. Where a discretionary extension was granted — a DTI
        # ceiling raised from 43% to 45% on compensating factors — the applied
        # threshold flatters the file: at 42% it looks three points clear of 45%
        # while sitting one point under the limit the programme really sets.
        # A file that clears only on a concession is closer to a policy edge than
        # its applied threshold suggests, and referral is the safe direction for
        # a rule whose own text calls itself mandatory.
        baseline = evaluation.get("baseline_threshold")
        threshold = min(applied, baseline) if isinstance(baseline, (int, float)) else applied

        margin = threshold - observed
        # Only *approaching* the limit counts. A file already over it is a breach,
        # which is a different trigger and a different conversation.
        if 0 <= margin <= band:
            extended = (
                f" (the applied ceiling was {applied * 100:.2f}% after extension)"
                if threshold != applied else ""
            )
            add(
                "borderline_affordability",
                f"{evaluation.get('measure')} {observed * 100:.2f}% is within "
                f"{assessment.band_pct_points:.2f} percentage points of its "
                f"{threshold * 100:.2f}% limit{extended}",
                observed=observed,
                threshold=threshold,
            )

    # -- exposure ------------------------------------------------------------------
    if str(packet.get("product_family", "")).lower() == "jumbo":
        add("high_value_exposure", "a jumbo transaction is a mandatory human-review trigger")

    # -- income complexity ---------------------------------------------------------
    if any("self" in kind for kind in _income_types(packet)):
        add("self_employment", "self-employment income is a mandatory human-review trigger")

    # -- fraud, identity and security ----------------------------------------------
    flags = {str(f).upper() for f in (risk.get("flags") or [])}
    fraud_flags = {f for f in flags if "FRAUD" in f or "IDENTITY" in f or "DOCUMENT" in f}
    if fraud_flags:
        add("fraud_or_document_integrity",
            f"risk screening raised {', '.join(sorted(fraud_flags))}")

    fraud = packet.get("fraud_screening") or {}
    if fraud:
        if str(fraud.get("kyc_status", "PASS")).upper() != "PASS":
            add("identity_not_clean", f"KYC status is {fraud.get('kyc_status')}")
        if fraud.get("ofac_hit"):
            add("fraud_or_document_integrity", "a sanctions screening hit is present")
        if fraud.get("enrollment_fraud_flag") or fraud.get("address_mismatch_flag"):
            add("fraud_or_document_integrity", "a fraud indicator is present on the file")

    if security_findings:
        add("security_event",
            "applicant-supplied text attempted to alter policy, thresholds or data access")

    # -- occupancy -----------------------------------------------------------------
    occupancy_intent = (packet.get("subject_property") or {}).get("occupancy_intent")
    if occupancy_intent and occupancy_intent != packet.get("occupancy_type"):
        add("occupancy_contradiction",
            f"stated occupancy {packet.get('occupancy_type')} contradicts declared "
            f"intent {occupancy_intent}")

    # -- unsourced large deposit ---------------------------------------------------
    for transaction in packet.get("asset_transactions") or []:
        if transaction.get("large_deposit_flag") and str(
            transaction.get("source_status", "")
        ).upper() != "SOURCED":
            add(
                "unsourced_large_deposit",
                f"a large deposit of {transaction.get('amount')} on "
                f"{transaction.get('transaction_date')} is "
                f"{str(transaction.get('source_status', 'unsourced')).lower()}",
            )
            break

    # -- conflicting evidence ------------------------------------------------------
    # A flood determination reports a FEMA zone code in the same column, so the
    # category is checked before the result is read as a status.
    for verification in packet.get("verification_results") or []:
        if str(verification.get("category", "")) == "flood_determination":
            continue
        result = str(verification.get("result", "")).upper()
        if result in _CONFLICTING_VERIFICATION_RESULTS:
            add(
                "unresolved_evidence_conflict",
                f"{verification.get('category')} verification returned {result}, which the "
                f"deterministic rules cannot reconcile",
            )

    # -- missing evidence ----------------------------------------------------------
    if eligibility.get("status") == "INDETERMINATE":
        add("unresolved_evidence",
            "a rule could not be applied on the evidence available, so the file "
            "cannot be decided automatically")

    return assessment


__all__ = [
    "DEFAULT_BORDERLINE_BAND_PCT_POINTS",
    "PRODUCTS_WITH_A_BORDERLINE_BAND",
    "ReviewAssessment",
    "ReviewTrigger",
    "TRIGGER_RULES",
    "UNEVALUABLE_TRIGGERS",
    "evaluate_review_triggers",
]
