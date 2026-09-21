"""Deterministic underwriting calculations.

Every figure a decision rests on is produced here, by code, with its inputs
recorded — never by a language model. That is not a stylistic preference: it is
what ``POL-DTI-001`` rule ``DTI-CALC-002`` requires ("No affordability value may
originate from a language model's arithmetic"), and what the education corpus's
``EDU-INC-002`` assumes when it states its DTI formula.

The division of labour across the system is:

    application packet  ->  this module          ->  DTI = 44.00%
    policy corpus       ->  the RAG retriever    ->  threshold = 43%
    both                ->  the rule engine      ->  breach
    the breach          ->  Gemini               ->  the written explanation

Mortgage and education calculations are kept apart on purpose. They share a name
("DTI") and almost nothing else: a mortgage ratio is built from a qualifying
housing expense the education product does not have, and an education file's
capacity may rest on a cosigner's income, or on projected post-graduation income,
neither of which exists in a mortgage packet.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

from src.domain import LendingProductDomain

#: Ratios are reported to four decimal places and money to cents, half-up, as
#: POL-DTI-001 DTI-CALC-002 specifies.
_RATIO_PLACES = Decimal("0.0001")
_MONEY_PLACES = Decimal("0.01")


def _dec(value: Any, default: str = "0") -> Decimal:
    """Parse a money/ratio value from the corpora, which store them as strings."""
    if value in (None, "", "null"):
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _ratio(numerator: Decimal, denominator: Decimal) -> float | None:
    """Divide, returning ``None`` rather than 0 or infinity on zero income.

    ``POL-DTI-001`` DTI-CALC-001 is explicit that zero income yields
    INDETERMINATE, never zero and never infinite.
    """
    if denominator <= 0:
        return None
    return float((numerator / denominator).quantize(_RATIO_PLACES))


def _money(value: Decimal) -> float:
    return float(value.quantize(_MONEY_PLACES))


# ======================================================================================
# Mortgage
# ======================================================================================


def mortgage_affordability(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Compute the mortgage affordability and leverage figures.

    Returns the ratios, the money amounts behind them, and the provenance of each
    input, so a narrative can quote a figure and an auditor can retrace it.
    """
    income_rows: Sequence[Mapping[str, Any]] = packet.get("declared_income") or []
    asset_rows: Sequence[Mapping[str, Any]] = packet.get("declared_assets") or []
    loan = packet.get("requested_loan") or {}
    prop = packet.get("subject_property") or {}
    costs: Mapping[str, Any] = packet.get("property_costs") or {}

    monthly_income = sum(
        (_dec(r.get("declared_monthly_amount") or r.get("monthly_amount")) for r in income_rows),
        Decimal("0"),
    )

    # Prefer the verified liabilities with their inclusion decision (POL-LIA-001);
    # fall back to what the applicant declared when no verified set is present.
    verified_liabilities: Sequence[Mapping[str, Any]] = packet.get("verified_liabilities") or []
    if verified_liabilities:
        liability_rows = [r for r in verified_liabilities if r.get("include_in_dti", True)]
        liabilities_source = "verified"
    else:
        liability_rows = list(packet.get("declared_liabilities") or [])
        liabilities_source = "declared"
    monthly_liabilities = sum(
        (_dec(r.get("monthly_payment")) for r in liability_rows), Decimal("0")
    )

    base_loan = _dec(loan.get("base_loan_amount"))
    rate = _dec(loan.get("interest_rate"))
    term_months = int(loan.get("term_months") or 360)
    # The rate sheet's own amortised payment governs where one is recorded; the
    # amortisation formula reproduces it when it is not.
    principal_and_interest = _dec(costs.get("principal_and_interest")) or _amortised_payment(
        base_loan, rate, term_months
    )

    # Tax and hazard are published annually and enter the housing expense at one
    # twelfth (synthetic_data/mortgage/DATA_DICTIONARY.md); association dues and
    # mortgage insurance are already monthly.
    escrow = (
        _dec(costs.get("annual_property_tax")) / Decimal("12")
        + _dec(costs.get("annual_hazard_premium")) / Decimal("12")
        + _dec(costs.get("monthly_hoa"))
        + _dec(costs.get("monthly_mortgage_insurance"))
    ).quantize(_MONEY_PLACES)
    housing_expense = (principal_and_interest + escrow).quantize(_MONEY_PLACES)
    total_obligations = (housing_expense + monthly_liabilities).quantize(_MONEY_PLACES)

    # Leverage uses the lesser of price and appraised value on a purchase, which
    # is what value_used_for_ltv already records.
    value = (
        _dec(costs.get("value_used_for_ltv"))
        or _dec(prop.get("purchase_price"))
        or _dec(prop.get("appraised_value"))
    )
    liquid_assets = sum(
        (_dec(r.get("verified_balance") or r.get("declared_balance")) for r in asset_rows),
        Decimal("0"),
    )

    ratios = {
        "back_end_dti": _ratio(total_obligations, monthly_income),
        "front_end_dti": _ratio(housing_expense, monthly_income),
        "ltv": _ratio(base_loan, value),
    }
    residual = monthly_income - total_obligations

    return {
        "product_domain": LendingProductDomain.MORTGAGE.value,
        "ratios": {k: v for k, v in ratios.items() if v is not None},
        "indeterminate": [k for k, v in ratios.items() if v is None],
        "amounts": {
            "qualifying_monthly_income": _money(monthly_income),
            "housing_expense_pitia": _money(housing_expense),
            "principal_and_interest": _money(principal_and_interest),
            "escrow_components": _money(escrow),
            "monthly_liabilities": _money(monthly_liabilities),
            "total_monthly_obligations": _money(total_obligations),
            "residual_income_monthly": _money(residual),
            "verified_liquid_assets": _money(liquid_assets),
            "base_loan_amount": _money(base_loan),
            "property_value": _money(value),
        },
        "months_of_reserves": (
            float((liquid_assets / housing_expense).quantize(_RATIO_PLACES))
            if housing_expense > 0
            else None
        ),
        "formula_version": "mortgage-affordability-1.0",
        "inputs": {
            "income_rows": len(income_rows),
            "liability_rows": len(liability_rows),
            "liabilities_source": liabilities_source,
            "asset_rows": len(asset_rows),
            "term_months": term_months,
            "property_costs_available": bool(costs),
        },
    }


def _amortised_payment(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    """Level-payment amortisation. Zero rate degrades to straight-line."""
    if principal <= 0 or months <= 0:
        return Decimal("0")
    if annual_rate <= 0:
        return (principal / Decimal(months)).quantize(_MONEY_PLACES)
    monthly_rate = annual_rate / Decimal("12")
    growth = (Decimal("1") + monthly_rate) ** months
    return (principal * monthly_rate * growth / (growth - Decimal("1"))).quantize(_MONEY_PLACES)


# ======================================================================================
# Education
# ======================================================================================


def education_affordability(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Compute the education-loan capacity figures.

    Capacity rests on whichever party the file qualifies on. Where a cosigner is
    present the corpus evaluates the cosigner's income and DTI (``POL-004``
    ``EDU-COS-002``), which is a materially different calculation from the
    mortgage one and is kept separate for that reason.
    """
    verifications: Sequence[Mapping[str, Any]] = packet.get("income_verification") or []
    certification = packet.get("school_certification") or {}
    exposure = packet.get("aggregate_exposure") or {}

    annual_income = max(
        (_dec(v.get("gross_annual_income") or v.get("annual_income")) for v in verifications),
        default=Decimal("0"),
    )
    other_income = sum((_dec(v.get("other_income")) for v in verifications), Decimal("0"))
    monthly_income = (
        (annual_income + other_income) / Decimal("12")
    ).quantize(_MONEY_PLACES)
    monthly_obligations = max(
        (
            _dec(v.get("monthly_debt_service") or v.get("monthly_debt"))
            for v in verifications
        ),
        default=Decimal("0"),
    )
    # The corpus records dti_pct as a decimal fraction (0.1618 = 16.18%), despite
    # the field name. Values above 1 are read as percentages.
    stated_dti = max((_dec(v.get("dti_pct")) for v in verifications), default=Decimal("0"))
    if stated_dti > 1:
        stated_dti = stated_dti / Decimal("100")

    coa = _dec(certification.get("cost_of_attendance"))
    other_aid = _dec(certification.get("other_financial_aid"))
    federal = _dec(certification.get("federal_loans_amount"))
    certified_max = _dec(certification.get("certified_max_eligible"))
    requested = _dec(packet.get("requested_amount"))

    # Cost of attendance less every other source of funding is the gap a private
    # loan may fill; the school's certified figure governs where both are present.
    computed_gap = coa - other_aid - federal
    eligible_amount = certified_max if certified_max > 0 else computed_gap

    ratios = {
        "education_dti": (
            float(stated_dti.quantize(_RATIO_PLACES))
            if stated_dti > 0
            else _ratio(monthly_obligations, monthly_income)
        ),
        "debt_to_projected_income": (
            float(_dec(exposure.get("debt_to_projected_income_ratio")))
            if exposure.get("debt_to_projected_income_ratio") is not None
            else None
        ),
    }

    return {
        "product_domain": LendingProductDomain.EDUCATION_LOAN.value,
        "ratios": {k: v for k, v in ratios.items() if v is not None},
        "indeterminate": [k for k, v in ratios.items() if v is None],
        "amounts": {
            "qualifying_monthly_income": _money(monthly_income),
            "monthly_obligations": _money(monthly_obligations),
            "residual_income_monthly": _money(monthly_income - monthly_obligations),
            "cost_of_attendance": _money(coa),
            "other_financial_aid": _money(other_aid),
            "federal_loans_amount": _money(federal),
            "computed_funding_gap": _money(computed_gap),
            "certified_max_eligible": _money(certified_max),
            "eligible_amount": _money(eligible_amount),
            "requested_amount": _money(requested),
            "total_education_debt": _money(_dec(exposure.get("total_education_debt"))),
        },
        "within_certified_max": bool(eligible_amount >= requested) if eligible_amount > 0 else None,
        "formula_version": "education-capacity-1.0",
        "inputs": {
            "income_verification_rows": len(verifications),
            "has_cosigner": bool(packet.get("has_cosigner")),
            "certification_status": certification.get("certification_status"),
        },
    }


def compute_affordability(
    domain: LendingProductDomain, packet: Mapping[str, Any]
) -> dict[str, Any]:
    """Dispatch to the product's own calculator."""
    if domain is LendingProductDomain.MORTGAGE:
        return mortgage_affordability(packet)
    return education_affordability(packet)


# ======================================================================================
# Risk screening
# ======================================================================================


def screen_risk(domain: LendingProductDomain, packet: Mapping[str, Any]) -> dict[str, Any]:
    """Deterministic risk flags from the packet.

    Flags are observations, not decisions. ``POL-FRD-001`` FRD-IND-004 is explicit
    that an indicator is not by itself an adverse-action reason.
    """
    flags: list[str] = []

    if domain is LendingProductDomain.MORTGAGE:
        occupancy_intent = (packet.get("subject_property") or {}).get("occupancy_intent")
        if occupancy_intent and occupancy_intent != packet.get("occupancy_type"):
            flags.append("OCCUPANCY_INCONSISTENCY")
        if packet.get("product_family") == "jumbo":
            flags.append("JUMBO_MANDATORY_REVIEW")
        kinds = {str(i.get("income_type", "")).lower() for i in packet.get("declared_income") or []}
        if any("self" in k for k in kinds):
            flags.append("SELF_EMPLOYED_MANDATORY_REVIEW")
        if not packet.get("supplied_documents"):
            flags.append("NO_DOCUMENTS_SUPPLIED")
    else:
        fraud = packet.get("fraud_screening") or {}
        if fraud.get("ofac_hit"):
            flags.append("OFAC_HIT")
        if fraud.get("kyc_status") not in (None, "PASS"):
            flags.append("KYC_NOT_PASSED")
        if fraud.get("velocity_flag"):
            flags.append("VELOCITY_FLAG")
        if fraud.get("enrollment_fraud_flag"):
            flags.append("ENROLLMENT_FRAUD_FLAG")
        if fraud.get("address_mismatch_flag"):
            flags.append("ADDRESS_MISMATCH")
        score = fraud.get("synthetic_identity_score")
        if isinstance(score, (int, float)) and score >= 50:
            flags.append("SYNTHETIC_IDENTITY_SCORE_ELEVATED")
        certification = packet.get("school_certification") or {}
        if certification.get("certification_status") not in (None, "RECEIVED"):
            flags.append("SCHOOL_CERTIFICATION_OUTSTANDING")

    blocking = {"OFAC_HIT", "KYC_NOT_PASSED", "ENROLLMENT_FRAUD_FLAG", "OCCUPANCY_INCONSISTENCY"}
    review = {"JUMBO_MANDATORY_REVIEW", "SELF_EMPLOYED_MANDATORY_REVIEW"}

    if set(flags) & blocking:
        level = "HIGH"
    elif set(flags) & review or len(flags) >= 2:
        level = "MEDIUM"
    elif flags:
        level = "LOW"
    else:
        level = "LOW"

    return {
        "product_domain": domain.value,
        "level": level,
        "flags": flags,
        "screen_version": "risk-screen-1.0",
    }
