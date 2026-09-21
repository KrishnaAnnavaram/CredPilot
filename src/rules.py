"""The rule engine: retrieved policy applied to computed figures.

The division of responsibility is deliberate and load-bearing:

* :mod:`src.calculations` produces the figures, from the application data.
* The RAG retriever produces the *rules*, from the policy corpus.
* This module applies one to the other and records which rule decided what.
* Gemini explains the outcome. It never produces a figure, a threshold or a
  verdict.

Thresholds are **parsed out of the retrieved policy text**, not hardcoded here.
That is what makes the retrieval subsystem load-bearing rather than decorative:
when ``POL-DTI-001`` moves from v1.0's unconditional 45% to v2.0's 43%-with-
extension, nothing in this file changes — the retriever returns the version in
force on the underwriting date, and the ceiling moves with it.

When a threshold cannot be found in the retrieved evidence the rule is reported
INDETERMINATE. It is never treated as absent, and absence is never read as
permission (``POL-GEN-001`` GEN-ELG-005).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Mapping, Sequence

from src.domain import LendingProductDomain

# ``| `max_back_end_dti` | 43% |`` — the parameter tables both corpora publish.
_PARAM_ROW = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE)

# ``| GR | 43% | REFER for manual review |`` — the education product matrices.
_PRODUCT_ROW = re.compile(
    r"^\|\s*(UG|GR|SP|INTL|REFI)\s*\|\s*\*{0,2}([\d.]+)\s*%\s*\*{0,2}\s*\|", re.MULTILINE
)

_PERCENT = re.compile(r"^([\d.]+)\s*%$")
_MONEY = re.compile(r"^\$?([\d,]+(?:\.\d+)?)$")


class Verdict(str):
    """Outcome of one rule evaluation."""

    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class RuleEvaluation:
    """One rule, applied, with everything needed to audit the outcome."""

    rule_id: str | None
    citation: str
    measure: str
    verdict: str
    observed: float | None = None
    threshold: float | None = None
    comparator: str = "<="
    detail: str = ""
    factors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "citation": self.citation,
            "measure": self.measure,
            "verdict": self.verdict,
            "observed": self.observed,
            "threshold": self.threshold,
            "comparator": self.comparator,
            "detail": self.detail,
            "compensating_factors": self.factors,
        }


# ======================================================================================
# Parameter extraction
# ======================================================================================


def parse_value(raw: str) -> Any:
    """Coerce a parameter-table value: percentages to fractions, money to float."""
    text = str(raw).strip().strip("`").replace("**", "")
    pct = _PERCENT.match(text)
    if pct:
        return float(Decimal(pct.group(1)) / Decimal("100"))
    money = _MONEY.match(text)
    if money:
        return float(money.group(1).replace(",", ""))
    lowered = text.lower()
    if lowered in ("yes", "true"):
        return True
    if lowered in ("no", "false"):
        return False
    return text


def parameters_of(item: Mapping[str, Any]) -> dict[str, Any]:
    """Pull the parameter table out of **one** evidence chunk.

    Always prefer this over :func:`extract_parameters` when the rule is known:
    it reads the numbers from the exact chunk that will be cited, so the
    threshold and the citation can never come from different versions.
    """
    return {
        name: parse_value(raw)
        for name, raw in _PARAM_ROW.findall(item.get("text") or "")
    }


class MixedVersionEvidenceError(ValueError):
    """Raised when evidence contains two versions of the same policy.

    Temporal filtering guarantees this cannot happen through the retriever
    (:mod:`src.rag.applicability` drops superseded versions before ranking). It
    is checked here anyway, because a caller assembling evidence by hand and
    getting v1.0's 45% ceiling while citing v2.0 is precisely the silent
    wrong-answer this subsystem exists to prevent.
    """


def assert_single_version(evidence: Sequence[Mapping[str, Any]]) -> None:
    """Fail loudly if evidence mixes versions of one policy."""
    seen: dict[str, set[str]] = {}
    for item in evidence:
        policy_id = item.get("policy_id")
        if not policy_id:
            citation = str(item.get("citation", ""))
            policy_id = citation.split()[0] if citation else None
        if not policy_id:
            continue
        seen.setdefault(policy_id, set()).add(str(item.get("policy_version") or ""))
    mixed = {p: sorted(v) for p, v in seen.items() if len(v) > 1}
    if mixed:
        raise MixedVersionEvidenceError(
            f"evidence contains multiple versions of the same policy: {mixed}. "
            f"Retrieval must select the version governing the as-of date before "
            f"the rule engine sees it."
        )


def extract_parameters(
    evidence: Sequence[Mapping[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Pull every parameter table out of the retrieved evidence.

    Keyed by rule id, so a caller can ask for the parameters of the rule it
    means rather than whichever rule mentioned a number first.

    The evidence must already be version-resolved — see
    :func:`assert_single_version`, which this calls. Two versions of one rule
    carry the same rule id and different numbers, and merging them would hand
    back v1.0's ceiling under v2.0's citation.
    """
    assert_single_version(evidence)
    out: dict[str, dict[str, Any]] = {}
    for item in evidence:
        key = item.get("rule_id") or item.get("citation") or ""
        if not key:
            continue
        params = out.setdefault(key, {"__citation__": item.get("citation", "")})
        params.update(parameters_of(item))
    return out


def extract_product_ceilings(
    evidence: Sequence[Mapping[str, Any]], rule_id: str
) -> dict[str, float]:
    """Read an education product/ceiling matrix (``| GR | 43% | ... |``)."""
    for item in evidence:
        if item.get("rule_id") != rule_id:
            continue
        found = _PRODUCT_ROW.findall(item.get("text") or "")
        if found:
            return {code: float(Decimal(value) / Decimal("100")) for code, value in found}
    return {}


def find_rule(evidence: Sequence[Mapping[str, Any]], rule_id: str) -> Mapping[str, Any] | None:
    for item in evidence:
        if item.get("rule_id") == rule_id:
            return item
    return None


# ======================================================================================
# Mortgage affordability
# ======================================================================================

#: The five factors DTI-CONV-003 recognises, each mapped to the parameter that
#: sets its bar. The parameter values come from the retrieved rule, not from here.
_COMPENSATING_FACTORS: tuple[tuple[str, str], ...] = (
    ("reserves_at_least_six_months", "factor_reserves_months"),
    ("representative_score_at_or_above_720", "factor_min_credit_score"),
    ("payment_shock_within_tolerance", "factor_max_payment_shock"),
    ("employment_tenure_at_or_above_60_months", "factor_min_employment_months"),
    ("loan_to_value_at_or_below_75_percent", "factor_max_ltv"),
)


def evaluate_mortgage_affordability(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Apply the retrieved affordability rules to the computed ratios."""
    assert_single_version(evidence)
    dti_rule = find_rule(evidence, "DTI-CONV-001")
    observed = calculations.get("ratios", {}).get("back_end_dti")

    if dti_rule is None:
        return [
            RuleEvaluation(
                rule_id="DTI-CONV-001",
                citation="",
                measure="back_end_dti",
                verdict=Verdict.INDETERMINATE,
                observed=observed,
                detail=(
                    "the affordability ceiling was not retrieved; the rule cannot be "
                    "applied and absence is not permission (GEN-ELG-005)"
                ),
            )
        ]

    citation = dti_rule.get("citation", "")
    # Read the thresholds from the chunk that will be cited, so the number and
    # the citation can never come from different versions.
    dti_params = parameters_of(dti_rule)
    base = dti_params.get("max_back_end_dti")
    extended = dti_params.get("max_back_end_dti_with_factors")
    min_factors = dti_params.get("min_compensating_factors")

    if base is None or observed is None:
        return [
            RuleEvaluation(
                rule_id="DTI-CONV-001",
                citation=citation,
                measure="back_end_dti",
                verdict=Verdict.INDETERMINATE,
                observed=observed,
                detail="no ceiling in the retrieved rule, or income is zero",
            )
        ]

    threshold = float(base)
    factors: list[str] = []
    detail = f"ceiling {threshold:.2%} from {citation}"

    # The extension exists only where the retrieved rule publishes one.
    if extended is not None and min_factors is not None:
        factor_rule = find_rule(evidence, "DTI-CONV-003")

        if factor_rule is None:
            # DTI-CONV-001 grants an extension on factors that DTI-CONV-003
            # defines. Without that rule the engine does not know what counts as
            # a factor — it cannot conclude that none are documented, only that
            # it cannot tell. Reporting FAIL here would decline a file because
            # retrieval missed a rule, which GEN-ELG-005 forbids: missing
            # evidence yields INDETERMINATE, never a negative result.
            return [
                RuleEvaluation(
                    rule_id="DTI-CONV-001",
                    citation=citation,
                    measure="back_end_dti",
                    verdict=Verdict.INDETERMINATE,
                    observed=observed,
                    threshold=float(base),
                    comparator="<=",
                    detail=(
                        f"{citation} extends the {float(base):.2%} ceiling to "
                        f"{float(extended):.2%} on compensating factors defined in "
                        f"DTI-CONV-003, which was not retrieved. The extension cannot "
                        f"be evaluated, so the file is referred rather than decided"
                    ),
                )
            ]

        factor_params = parameters_of(factor_rule)
        excluded = _excluded_products(evidence)
        product = str(packet.get("product_family", ""))
        purpose = str(packet.get("loan_purpose", ""))
        if product in excluded or purpose in excluded:
            detail += (
                f"; the compensating-factor extension is not available on "
                f"{product or purpose} (DTI-CONV-003)"
            )
        else:
            factors = _documented_factors(calculations, packet, factor_params)
            if len(factors) >= int(min_factors):
                threshold = float(extended)
                detail = (
                    f"ceiling extended to {threshold:.2%} on "
                    f"{len(factors)} documented compensating factors "
                    f"(minimum {int(min_factors)}), per {citation} and DTI-CONV-003"
                )
            else:
                detail += (
                    f"; extension to {float(extended):.2%} unavailable — "
                    f"{len(factors)} of {int(min_factors)} required factors documented"
                )

    verdict = Verdict.PASS if observed <= threshold else Verdict.FAIL
    return [
        RuleEvaluation(
            rule_id="DTI-CONV-001",
            citation=citation,
            measure="back_end_dti",
            verdict=verdict,
            observed=observed,
            threshold=threshold,
            comparator="<=",
            detail=detail,
            factors=factors,
        )
    ]


def _excluded_products(evidence: Sequence[Mapping[str, Any]]) -> set[str]:
    rule = find_rule(evidence, "DTI-CONV-003")
    if not rule:
        return set()
    match = re.search(
        r"\|\s*`excluded_products`\s*\|\s*([^|]+?)\s*\|", rule.get("text") or ""
    )
    if not match:
        return set()
    return {part.strip() for part in match.group(1).split(",") if part.strip()}


def _documented_factors(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    factor_params: Mapping[str, Any],
) -> list[str]:
    """Which recognised compensating factors this file documents.

    A factor counts only where the file carries the evidence for it. An asserted
    but undocumented factor does not count (DTI-CONV-003).
    """
    found: list[str] = []
    amounts = calculations.get("amounts", {})
    ratios = calculations.get("ratios", {})

    months = calculations.get("months_of_reserves")
    required_months = factor_params.get("factor_reserves_months")
    if months is not None and required_months is not None and months >= float(required_months):
        found.append(f"verified reserves of {months:.1f} months (>= {required_months})")

    score = _representative_score(packet)
    min_score = factor_params.get("factor_min_credit_score")
    if score is not None and min_score is not None and score >= float(min_score):
        found.append(f"representative credit score {score:.0f} (>= {min_score:.0f})")

    ltv = ratios.get("ltv")
    max_ltv = factor_params.get("factor_max_ltv")
    if ltv is not None and max_ltv is not None and ltv <= float(max_ltv):
        found.append(f"loan-to-value {ltv:.2%} (<= {float(max_ltv):.0%})")

    tenure = _employment_tenure_months(packet)
    min_tenure = factor_params.get("factor_min_employment_months")
    if tenure is not None and min_tenure is not None and tenure >= float(min_tenure):
        found.append(f"employment tenure {tenure} months (>= {min_tenure:.0f})")

    shock = _payment_shock(packet, amounts)
    max_shock = factor_params.get("factor_max_payment_shock")
    if shock is not None and max_shock is not None and shock <= float(max_shock):
        found.append(f"payment shock {shock:.2%} (<= {float(max_shock):.0%})")

    return found


def _representative_score(packet: Mapping[str, Any]) -> float | None:
    """The representative score, as CRD-SCR-002 defines it: middle of three."""
    summary = packet.get("credit_summary") or {}
    stated = summary.get("representative_score")
    if stated:
        try:
            return float(stated)
        except (TypeError, ValueError):
            pass
    scores = [
        float(s)
        for s in (summary.get("score_1"), summary.get("score_2"), summary.get("score_3"))
        if s
    ]
    if len(scores) >= 3:
        return sorted(scores)[1]
    return min(scores) if scores else None


def _employment_tenure_months(packet: Mapping[str, Any]) -> int | None:
    from datetime import date

    rows = [e for e in packet.get("employment") or [] if e.get("is_current")]
    as_of = packet.get("underwriting_as_of_date")
    if not rows or not as_of:
        return None
    try:
        end = date.fromisoformat(str(as_of))
    except ValueError:
        return None
    longest = None
    for row in rows:
        start_raw = row.get("declared_start_date")
        if not start_raw:
            continue
        try:
            start = date.fromisoformat(str(start_raw))
        except ValueError:
            continue
        months = (end.year - start.year) * 12 + (end.month - start.month)
        longest = months if longest is None else max(longest, months)
    return longest


def _payment_shock(packet: Mapping[str, Any], amounts: Mapping[str, Any]) -> float | None:
    """Proposed housing payment as a multiple of the current one, minus one.

    ``None`` when no current housing payment is documented — the factor cannot be
    claimed on evidence that is not in the file.
    """
    current = packet.get("current_housing_payment") or (
        packet.get("property_costs") or {}
    ).get("current_housing_payment")
    proposed = amounts.get("housing_expense_pitia")
    if not current or not proposed:
        return None
    try:
        current_value = float(current)
    except (TypeError, ValueError):
        return None
    if current_value <= 0:
        return None
    return (float(proposed) / current_value) - 1.0


# ======================================================================================
# Education capacity
# ======================================================================================


def evaluate_education_capacity(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Apply the retrieved education capacity rules."""
    product = str(packet.get("product_code", "")).upper()
    observed = calculations.get("ratios", {}).get("education_dti")
    evaluations: list[RuleEvaluation] = []

    ceilings = extract_product_ceilings(evidence, "EDU-INC-003")
    dti_rule = find_rule(evidence, "EDU-INC-003")
    citation = dti_rule.get("citation", "") if dti_rule else ""

    if not ceilings or observed is None:
        evaluations.append(
            RuleEvaluation(
                rule_id="EDU-INC-003",
                citation=citation,
                measure="education_dti",
                verdict=Verdict.INDETERMINATE,
                observed=observed,
                detail=(
                    "the product DTI ceiling was not retrieved"
                    if not ceilings
                    else "capacity could not be computed from the file"
                ),
            )
        )
    else:
        threshold = ceilings.get(product)
        if threshold is None:
            evaluations.append(
                RuleEvaluation(
                    rule_id="EDU-INC-003",
                    citation=citation,
                    measure="education_dti",
                    verdict=Verdict.INDETERMINATE,
                    observed=observed,
                    detail=f"no ceiling published for product {product or '(unknown)'}",
                )
            )
        else:
            evaluations.append(
                RuleEvaluation(
                    rule_id="EDU-INC-003",
                    citation=citation,
                    measure="education_dti",
                    verdict=Verdict.PASS if observed <= threshold else Verdict.FAIL,
                    observed=observed,
                    threshold=threshold,
                    comparator="<=",
                    detail=f"{product} ceiling {threshold:.0%} from {citation}",
                )
            )

    # Residual income floor, EDU-INC-004.
    residual_rule = find_rule(evidence, "EDU-INC-004")
    residual = calculations.get("amounts", {}).get("residual_income_monthly")
    if residual_rule and residual is not None:
        floor = _residual_floor(residual_rule.get("text") or "")
        if floor is None:
            evaluations.append(
                RuleEvaluation(
                    rule_id="EDU-INC-004",
                    citation=residual_rule.get("citation", ""),
                    measure="residual_income_monthly",
                    verdict=Verdict.INDETERMINATE,
                    observed=residual,
                    detail="the residual-income floor was not present in the retrieved rule",
                )
            )
        else:
            evaluations.append(
                RuleEvaluation(
                    rule_id="EDU-INC-004",
                    citation=residual_rule.get("citation", ""),
                    measure="residual_income_monthly",
                    verdict=Verdict.PASS if residual >= floor else Verdict.FAIL,
                    observed=residual,
                    threshold=floor,
                    comparator=">=",
                    detail=(
                        f"floor ${floor:,.0f} per month"
                        + (
                            "; a REFI shortfall is a hard knockout with no exception pathway"
                            if product == "REFI"
                            else "; a shortfall refers the file for manual review"
                        )
                    ),
                )
            )

    # Certified maximum, EDU-SCH-005.
    certified = calculations.get("amounts", {}).get("certified_max_eligible")
    requested = calculations.get("amounts", {}).get("requested_amount")
    cert_rule = find_rule(evidence, "EDU-SCH-005")
    if certified and requested:
        evaluations.append(
            RuleEvaluation(
                rule_id="EDU-SCH-005" if cert_rule else None,
                citation=cert_rule.get("citation", "") if cert_rule else "",
                measure="requested_vs_certified_max",
                verdict=Verdict.PASS if requested <= certified else Verdict.FAIL,
                observed=float(requested),
                threshold=float(certified),
                comparator="<=",
                detail="the school-certified maximum eligible amount caps the loan",
            )
        )

    return evaluations


def _residual_floor(text: str) -> float | None:
    match = re.search(r"\*\*\$?([\d,]+)(?:\.\d+)?\s*(?:per month)?\*\*", text)
    if not match:
        match = re.search(r"\$([\d,]+)\s*(?:per month|residual)", text, re.I)
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


# ======================================================================================
# Dispatch
# ======================================================================================


def evaluate(
    domain: LendingProductDomain,
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Apply the product's retrieved rules to its computed figures."""
    if domain is LendingProductDomain.MORTGAGE:
        return evaluate_mortgage_affordability(calculations, packet, evidence)
    return evaluate_education_capacity(calculations, packet, evidence)


def summarize(evaluations: Sequence[RuleEvaluation]) -> dict[str, Any]:
    """Roll rule evaluations up into an eligibility verdict."""
    failures = [e for e in evaluations if e.verdict == Verdict.FAIL]
    indeterminate = [e for e in evaluations if e.verdict == Verdict.INDETERMINATE]

    if failures:
        status = "INELIGIBLE"
    elif indeterminate:
        # Missing evidence yields INDETERMINATE, never a negative result
        # (POL-GEN-001 GEN-ELG-005).
        status = "INDETERMINATE"
    else:
        status = "ELIGIBLE"

    return {
        "status": status,
        "breaches": [e.as_dict() for e in failures],
        "indeterminate": [e.as_dict() for e in indeterminate],
        "evaluations": [e.as_dict() for e in evaluations],
        "thresholds_applied": {
            e.measure: e.citation for e in evaluations if e.threshold is not None
        },
    }
