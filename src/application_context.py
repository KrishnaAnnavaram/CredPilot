"""Assembling the underwriting input for one application.

An application packet is what the applicant submitted. It does not carry every
figure underwriting needs — a mortgage packet states the loan amount and the
purchase price but not the property tax, the hazard premium or the mortgage
insurance, because those come off the appraisal, the insurance evidence and the
rate sheet rather than off the application form.

Those figures live in the committed structured extract at
``synthetic_data/mortgage/structured/``. This module reads them, and reads
**only inputs**.

The distinction is enforced, not just intended. ``INPUT_TABLES`` is an allowlist
of the tables that hold facts about the applicant and the transaction.
``OUTCOME_TABLES`` names the tables that hold the answer — computed ratios, rule
evaluations, eligibility results, decisions, conditions, risk flags — and reading
one raises. A retriever or an underwriting agent that could read
``underwriting_calculations.csv`` would not be underwriting; it would be copying.
``tests/rag/test_no_golden_leakage.py`` checks the boundary holds.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from src.config import REPO_ROOT
from src.domain import LendingProductDomain, load_application

STRUCTURED_ROOT = REPO_ROOT / "synthetic_data" / "mortgage" / "structured"

#: Tables describing what the applicant submitted or what a third party verified.
#: These are underwriting *inputs*.
INPUT_TABLES = frozenset(
    {
        "applications",
        "application_borrowers",
        "borrowers",
        "employment",
        "income",
        "assets",
        "asset_transactions",
        "liabilities",
        "credit_accounts",
        "credit_events",
        "credit_profiles",
        "properties",
        "appraisals",
        "title_records",
        "insurance_records",
        "loans",
        "documents",
        "document_extractions",
        "verifications",
    }
)

#: Tables holding the generator's own answers. Reading these from runtime code
#: would make an evaluation meaningless.
OUTCOME_TABLES = frozenset(
    {
        "underwriting_calculations",
        "eligibility_results",
        "rule_evaluations",
        "decisions",
        "decision_reasons",
        "conditions",
        "human_reviews",
        "risk_flags",
        "fraud_checks",
        "scenario_assignments",
        "security_events",
        "audit_events",
        "borrower_demographics",
    }
)


class OutcomeAccessError(PermissionError):
    """Raised when runtime code tries to read a table holding the answer."""


@lru_cache(maxsize=32)
def _load_table(name: str) -> tuple[dict[str, str], ...]:
    if name in OUTCOME_TABLES:
        raise OutcomeAccessError(
            f"{name}.csv holds underwriting outcomes, not inputs. Runtime code must "
            f"compute the answer, not read it. Evaluation code may compare against "
            f"the golden set instead."
        )
    if name not in INPUT_TABLES:
        raise KeyError(f"{name} is not a known structured table")
    path = STRUCTURED_ROOT / f"{name}.csv"
    if not path.exists():
        return ()
    with path.open("r", encoding="utf-8", newline="") as fh:
        return tuple(dict(row) for row in csv.DictReader(fh))


def rows_for(name: str, application_id: str) -> list[dict[str, str]]:
    """Every row of an input table belonging to one application."""
    return [r for r in _load_table(name) if r.get("application_id") == application_id]


def row_for(name: str, application_id: str) -> dict[str, str] | None:
    rows = rows_for(name, application_id)
    return rows[0] if rows else None


def mortgage_property_costs(application_id: str) -> dict[str, Any]:
    """Recurring property costs that enter the housing expense.

    Sourced from the appraisal and insurance records rather than the application
    form, which is where an underwriter finds them too.
    """
    prop = row_for("properties", application_id) or {}
    loan = row_for("loans", application_id) or {}
    return {
        "annual_property_tax": prop.get("annual_property_tax"),
        "annual_hazard_premium": prop.get("annual_hazard_premium"),
        "monthly_hoa": prop.get("monthly_hoa"),
        "flood_zone_sfha": str(prop.get("flood_zone_sfha", "")).lower() == "true",
        "appraised_value": prop.get("appraised_value"),
        "value_used_for_ltv": prop.get("value_used_for_ltv"),
        "principal_and_interest": loan.get("principal_and_interest"),
        "monthly_mortgage_insurance": loan.get("monthly_mortgage_insurance"),
        "note_amount": loan.get("note_amount"),
        "financed_premium_amount": loan.get("financed_premium_amount"),
        "down_payment_amount": loan.get("down_payment_amount"),
        "seller_credits": loan.get("seller_credits"),
    }


def mortgage_liabilities(application_id: str) -> list[dict[str, Any]]:
    """Liabilities with the inclusion decision the credit report supports.

    ``include_in_dti`` is a property of the obligation recorded at intake (see
    ``POL-LIA-001`` LIA-INC-001..006), not a computed outcome: it is which debts
    exist and which of them recur, which is an input to affordability.
    """
    return [
        {
            "liability_type": r.get("liability_type"),
            "monthly_payment": r.get("monthly_payment"),
            "balance": r.get("balance"),
            "remaining_term_months": r.get("remaining_term_months"),
            "include_in_dti": str(r.get("include_in_dti", "")).lower() == "true",
            "source": r.get("source"),
        }
        for r in rows_for("liabilities", application_id)
    ]


def mortgage_credit(application_id: str) -> dict[str, Any]:
    """The representative credit inputs from the bureau pull."""
    profile = row_for("credit_profiles", application_id) or {}
    return {
        k: profile.get(k)
        for k in (
            "representative_score",
            "score_model",
            "pull_date",
            "file_depth",
            "revolving_utilisation",
            "inquiries_6mo",
        )
        if k in profile
    }


def build_underwriting_input(
    application_path: "str | Path", *, domain: LendingProductDomain | None = None
) -> dict[str, Any]:
    """Assemble a packet plus its committed supporting inputs.

    Education packets already carry everything the education calculations need
    (income verification, certification, aggregate exposure), so nothing is
    added for them.
    """
    packet = load_application(application_path)
    application_id = packet.get("application_id", "")
    resolved = domain or (
        LendingProductDomain.MORTGAGE
        if "subject_property" in packet
        else LendingProductDomain.EDUCATION_LOAN
    )
    if resolved is not LendingProductDomain.MORTGAGE:
        return packet

    enriched = dict(packet)
    enriched["property_costs"] = mortgage_property_costs(application_id)
    enriched["verified_liabilities"] = mortgage_liabilities(application_id)
    credit = mortgage_credit(application_id)
    if credit:
        enriched["credit_summary"] = credit
    return enriched


def available_inputs(application_id: str) -> dict[str, int]:
    """Row counts per input table, for diagnostics."""
    return {name: len(rows_for(name, application_id)) for name in sorted(INPUT_TABLES)}


__all__ = [
    "INPUT_TABLES",
    "OUTCOME_TABLES",
    "OutcomeAccessError",
    "available_inputs",
    "build_underwriting_input",
    "mortgage_credit",
    "mortgage_liabilities",
    "mortgage_property_costs",
    "row_for",
    "rows_for",
]
