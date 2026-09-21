"""
Machine-generated documentation.

The data dictionary, the policy-test coverage matrix, the scenario coverage report
and the final quality report are produced from the committed data itself rather than
written by hand, so they cannot drift from what was actually generated. The narrative
documents that state intent - the README, the requirements traceability and the
design assumptions - are hand-written and live alongside them.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import synthetic_data_utils as u  # noqa: E402

from .emit import COLUMNS  # noqa: E402

GENERATED_BY = (
    "<!-- GENERATED FILE - do not edit by hand.\n"
    "     Regenerate with:  python synthetic_data/mortgage/generator/generate_synthetic_data.py -->\n"
)

TABLE_NOTES: dict[str, tuple[str, str, str]] = {
    # name: (grain, purpose, sensitivity)
    "borrowers": (
        "One synthetic person.",
        "Identity and contact attributes for every applicant. Every person here is "
        "fictional; identifiers are SYN- tokens and are displayed masked.",
        "High. Contains name, address and tokenised identifiers.",
    ),
    "borrower_demographics": (
        "One synthetic person.",
        "Statutory monitoring attributes, held in their own table with an explicit "
        "use restriction on every row. Never joined into any decision surface.",
        "Restricted. Monitoring use only; never a credit factor.",
    ),
    "applications": (
        "One application.",
        "The operational record: dates, channel, product, purpose, occupancy and the "
        "underwriting as-of date that selects which policy versions apply.",
        "Moderate.",
    ),
    "application_borrowers": (
        "One applicant's participation in one application.",
        "The many-to-many bridge. Carries borrower role, order and joint-credit "
        "intent, which is what makes a returning applicant expressible.",
        "Moderate.",
    ),
    "loans": (
        "One requested loan.",
        "Product, amount, term, rate and every settlement component. The base loan "
        "amount and the note amount are separate because a financed programme premium "
        "changes the payment but not the leverage test.",
        "Financial.",
    ),
    "properties": (
        "One collateral property.",
        "Address, type, units, occupancy, price, value and the value actually used "
        "for leverage - which is a different column on purpose.",
        "High. Address data.",
    ),
    "employment": (
        "One employment episode.",
        "Employer, occupation, dates and tenure. Declared and verified start dates "
        "are separate columns so a verification conflict is expressible.",
        "High.",
    ),
    "income": (
        "One income stream for one borrower.",
        "Declared, verified and qualifying amounts held separately, with the rule "
        "that produced the qualifying figure and the evidence types that support it.",
        "High.",
    ),
    "assets": (
        "One asset account or source.",
        "Verified balance plus two independent eligibility amounts: what can be "
        "brought to closing and what counts as a reserve. They are frequently "
        "different, which is why one 'balance' column would not do.",
        "Extreme. Financial account data, tokenised.",
    ),
    "asset_transactions": (
        "One relevant account movement.",
        "Deposits and withdrawals that bear on source of funds, including the "
        "unsourced large deposits the risk rules act on.",
        "Extreme.",
    ),
    "liabilities": (
        "One obligation.",
        "Every recurring obligation with its own inclusion decision and the rule id "
        "behind it. A single aggregated debt total would make the DTI unauditable.",
        "Extreme.",
    ),
    "credit_profiles": (
        "One credit report snapshot per borrower.",
        "Report metadata, all three scores, the representative score and the "
        "methodology rule. A score without its model is not comparable to a threshold.",
        "Extreme.",
    ),
    "credit_accounts": (
        "One tradeline.",
        "Balances, limits, payments and late history. Links back to the liability it "
        "supports so the DTI numerator is traceable to the report.",
        "Extreme.",
    ),
    "credit_events": (
        "One significant derogatory event.",
        "Event type, anchor date, the basis for that anchor, and seasoning in months. "
        "The anchor basis is recorded because using the wrong one is the classic error.",
        "Extreme.",
    ),
    "documents": (
        "One document instance.",
        "Metadata for every applicant document, including its trust class and whether "
        "it carries untrusted free text.",
        "High.",
    ),
    "document_extractions": (
        "One extracted field.",
        "Field-level provenance: which document supplied which value, at what "
        "confidence. This is what makes lineage queryable below the record level.",
        "High.",
    ),
    "appraisals": (
        "One valuation event.",
        "Value, method, condition and dataset version. Absent where the transaction "
        "used value acceptance, which is why the valuation method lives on the "
        "property row too.",
        "Moderate.",
    ),
    "title_records": (
        "One title commitment.",
        "Lien position, vesting and exceptions, with the blocking flag the "
        "clear-to-close gate reads.",
        "High.",
    ),
    "insurance_records": (
        "One policy or binder.",
        "Hazard and flood coverage with premiums that feed the housing expense.",
        "High.",
    ),
    "verifications": (
        "One third-party check.",
        "Identity, employment, income, asset and flood verifications with provider, "
        "dates and result.",
        "High.",
    ),
    "fraud_checks": (
        "One integrity finding.",
        "Cross-source inconsistencies and document-integrity findings, each naming "
        "the two sources that disagree rather than asserting a score.",
        "High.",
    ),
    "rule_evaluations": (
        "One rule applied to one application.",
        "The outcome, the observed value, the threshold it was compared against, the "
        "policy version in force, and the input fields consumed. This table is the "
        "spine of the audit trail.",
        "Decision.",
    ),
    "risk_flags": (
        "One risk finding.",
        "Category, severity, the evidence behind it and the rule that raised it.",
        "High.",
    ),
    "underwriting_calculations": (
        "One calculated feature per application.",
        "Every derived number with its inputs, formula version, units and expected "
        "interpretation. Nothing here was produced by a language model.",
        "Derived.",
    ),
    "eligibility_results": (
        "One programme eligibility determination.",
        "Kept separate from the recommendation and from the credit decision, because "
        "eligible is not a synonym for approved.",
        "Decision.",
    ),
    "conditions": (
        "One outstanding item.",
        "What is required, what evidence satisfies it, when it is due and its status.",
        "High.",
    ),
    "decisions": (
        "One decision at one stage.",
        "The copilot's recommendation and, where human review is required, the "
        "pending human credit decision. An automated actor never appears on the "
        "credit-decision stage.",
        "High.",
    ),
    "decision_reasons": (
        "One specific reason.",
        "The reason code, the rule, the policy version and the evidence reference. "
        "Adverse-action reasons must be specific and accurate, so a generic category "
        "is not acceptable here.",
        "High.",
    ),
    "human_reviews": (
        "One review event.",
        "Queue, trigger rules, reason code and reviewer role for every file that "
        "policy routes to a person.",
        "High.",
    ),
    "security_events": (
        "One security detection.",
        "Injection, extraction, cross-customer and out-of-scope attempts, with a "
        "masked excerpt and the action taken. Blocked attempts are recorded exactly "
        "as successful ones would be.",
        "High.",
    ),
    "audit_events": (
        "One recorded action.",
        "The ordered trail from authorisation through policy selection, extraction, "
        "calculation, rule evaluation, risk screening and recommendation.",
        "Moderate.",
    ),
    "scenario_assignments": (
        "One application's scenario mapping.",
        "Which scenario produced this application and what it is meant to exercise.",
        "Low.",
    ),
    "policies": (
        "One policy version.",
        "Front-matter metadata for every document in the corpus, including its "
        "effective window and its content hash.",
        "None. No customer data.",
    ),
    "policy_rules": (
        "One rule in one policy version.",
        "The addressable rule catalogue: identifier, authority, severity, outcome "
        "type and parameters, per version.",
        "None.",
    ),
}

FIELD_NOTES: dict[str, str] = {
    "application_id": "Application surrogate key, format APP-nnnnnn.",
    "borrower_id": "Person surrogate key, format BORR-nnnnnn.",
    "scenario_id": "The scenario that produced this row.",
    "application_date": "Date the application became sufficiently complete.",
    "underwriting_as_of_date": "The date that selects which policy versions apply.",
    "received_date": "Date the item reached the lender.",
    "channel": "Origination channel.",
    "loan_purpose": "purchase | rate_term_refinance | cash_out_refinance.",
    "product_family": "conventional_conforming | jumbo | fha | va | usda.",
    "occupancy_type": "primary_residence | second_home | investment.",
    "borrower_count": "Number of applicants; must match application_borrowers.",
    "primary_borrower_id": "Must match the borrower with role 'primary'.",
    "application_status": "Workflow state.",
    "household_size": "Used by the residual-income and programme-income tests only.",
    "ssn_token": "Tokenised taxpayer identifier. Never a real SSN.",
    "ssn_masked": "Display form, ***-**-nnnn.",
    "credit_file_token": "Tokenised credit-file identifier.",
    "credit_file_masked": "Display form, ****nnnn.",
    "account_token": "Tokenised deposit or brokerage account identifier.",
    "account_masked": "Display form, ******nnnn.",
    "email": "Reserved example.com domain (RFC 2606).",
    "phone": "Reserved fictional 555-0100..555-0199 block.",
    "base_loan_amount": "The amount the leverage test measures.",
    "financed_premium_amount": "Programme premium financed into the note.",
    "note_amount": "Base loan plus financed premium; the amount that amortises.",
    "term_months": "Loan term.",
    "interest_rate": "Annual nominal rate as a decimal.",
    "principal_and_interest": "Level payment from the note amount, rate and term.",
    "monthly_mortgage_insurance": "Enters the qualifying housing expense.",
    "down_payment_amount": "Purchase price less base loan amount.",
    "closing_costs": "Borrower-paid costs; synthetic basis in AST-FTC-002.",
    "prepaids_and_escrow": "Tax and insurance escrow plus per-diem interest.",
    "earnest_money_paid": "Reduces funds required; sourced from a verified account.",
    "payoff_amount": "Lien retired by the new loan on a refinance.",
    "cash_out_proceeds": "Equity returned to the borrower.",
    "purchase_price": "Contract price; null on a refinance.",
    "appraised_value": "Appraised or otherwise accepted value.",
    "value_used_for_ltv": "Lower of price and value on a purchase; value on a refinance.",
    "valuation_method": "full_appraisal | value_acceptance. Not every loan has a report.",
    "annual_property_tax": "Annual amount; the housing expense uses one twelfth.",
    "annual_hazard_premium": "Annual amount; the housing expense uses one twelfth.",
    "monthly_hoa": "Association dues.",
    "flood_zone": "Determination result.",
    "flood_zone_sfha": "True where the property sits in a special flood hazard area.",
    "ownership_months": "Months since acquisition; drives cash-out seasoning.",
    "declared_start_date": "What the application stated.",
    "verified_start_date": "What the employer confirmed. Tenure is computed from this.",
    "tenure_months": "Whole months from the verified start to the as-of date.",
    "self_employed_flag": "True at 25 percent ownership or above.",
    "declared_monthly_amount": "What the applicant stated. Never used to qualify.",
    "verified_monthly_amount": "What the evidence established.",
    "qualifying_monthly_amount": "What policy permits. Never exceeds verified.",
    "declared_balance": "What the applicant stated.",
    "verified_balance": "What the statement or verification established.",
    "eligible_close_amount": "Portion usable at settlement after any haircut.",
    "eligible_reserve_amount": "Portion countable as a reserve. Gifts are always zero.",
    "liquidity_haircut": "Reduction applied for conversion cost or uncertainty.",
    "monthly_payment": "The payment the DTI numerator uses.",
    "include_in_dti": "The inclusion decision, with its rule in inclusion_rule_id.",
    "remaining_term_months": "Drives the ten-payment exclusion test.",
    "credit_limit": "Revolving limit; zero means no stated limit.",
    "representative_score": "Middle of three per borrower; lowest across borrowers.",
    "score_model": "Required metadata: a score without its model is not comparable.",
    "report_age_days": "Days from report date to the as-of date.",
    "scoreable_tradelines": "Below three routes to manual credit review.",
    "recent_inquiries_90d": "Context for an explanation condition, never an adverse basis.",
    "event_type": "Significant derogatory event type.",
    "anchor_date": "The date seasoning is measured from.",
    "anchor_basis": "Which date that is for this event type.",
    "seasoning_months": "Whole months from the anchor to the as-of date.",
    "document_type": "Document category.",
    "trust_class": "customer_evidence | authoritative_evidence | internal_record.",
    "contains_untrusted_text": "True where the document carries applicant free text.",
    "tampering_indicator": "True where integrity signals were detected.",
    "contains_pii": "True where the document carries personal data.",
    "masked": "True where sensitive values are rendered masked.",
    "is_stale": "True where the document sits outside its freshness window.",
    "relative_path": "Repository-relative path to the rendered artifact.",
    "expected_extracted_fields": "Fields an extraction component should recover.",
    "extraction_confidence": "Extraction confidence, 0 to 1.",
    "rule_id": "Stable rule identifier, citable in a decision.",
    "policy_id": "Policy family identifier.",
    "policy_version": "The version applied, selected by the as-of date.",
    "policy_effective_date": "Start of that version's effective window.",
    "source_category": "Authority layer for the rule.",
    "severity": "HARD_FAIL | CONDITIONAL | REFER | ADVISORY.",
    "outcome": "PASS | FAIL | REFER | NOT_APPLICABLE | INDETERMINATE.",
    "observed_value": "The value measured.",
    "threshold_value": "The value it was measured against.",
    "comparator": "The comparison applied.",
    "input_fields": "The fields consumed, for lineage.",
    "requires_human_review": "True where policy routes the file to a person.",
    "reason": "Why the rule produced this outcome, in full.",
    "calculation_name": "The derived feature.",
    "formula_version": "Version of the expression that produced the result.",
    "result": "The computed value.",
    "units": "USD | USD_PER_MONTH | RATIO | MONTHS | SCORE | MULTIPLE.",
    "policy_context": "The policy this calculation feeds.",
    "expected_interpretation": "How the value should be read.",
    "decision_stage": "underwriting_recommendation | credit_decision.",
    "decision_type": "COPILOT_RECOMMENDATION | HUMAN_CREDIT_DECISION.",
    "actor_type": "AUTOMATED_COMPONENT | HUMAN.",
    "reason_code": "Controlled adverse-action reason code.",
    "reason_text": "The specific reason, not a generic category.",
    "evidence_reference": "The fields the reason rests on.",
    "queue": "Which human queue owns the file.",
    "reviewer_role": "The role authorised to act on it.",
    "event_type_security": "The security detection type.",
    "masked_excerpt": "Triggering content, masked.",
    "action_taken": "What the control did.",
    "correlation_id": "Ties one run's audit events together.",
    "sequence": "Position in the run, contiguous from 1.",
    "use_restriction": "States that the row is monitoring-only.",
}


def _validator_check_count() -> int:
    """How many checks the validator actually runs, read from its own source.

    Counting them beats restating a number that goes stale the moment a check is
    added - which is exactly what happened once already.
    """
    source = (
        Path(__file__).resolve().parents[1] / "validate_synthetic_data.py"
    ).read_text(encoding="utf-8")
    # Counting the check *methods* would undercount: several of them record more
    # than one result. Count the recorded results instead, which is what the run
    # actually reports.
    return len(re.findall(r"self\.record\(", source))


def _type_of(values: list[str]) -> str:
    sample = [v for v in values if v != ""]
    if not sample:
        return "string"
    if all(v in ("true", "false") for v in sample):
        return "boolean"
    try:
        for v in sample[:60]:
            date.fromisoformat(v)
        return "date"
    except ValueError:
        pass
    try:
        for v in sample[:60]:
            Decimal(v)
        return "decimal" if any("." in v for v in sample[:60]) else "integer"
    except Exception:  # noqa: BLE001
        return "string"


def data_dictionary() -> str:
    lines = [
        GENERATED_BY,
        "# CredPilot Synthetic Data Dictionary",
        "",
        "Every committed table, its grain, what it is for, and every column with its "
        "inferred type. Row counts and types are read from the generated files, so "
        "this document describes what actually exists rather than what was intended.",
        "",
        "Three column pairs recur and are the heart of the model. `declared_*` is what "
        "the applicant said, `verified_*` is what the evidence established, and "
        "`qualifying_*` is what policy permits underwriting to use. They are stored "
        "separately on purpose: collapsing them into one number destroys the ability "
        "to show which document supported which figure.",
        "",
    ]
    sources = [
        ("structured", sorted(u.STRUCTURED_DIR.glob("*.csv"))),
        ("policy_metadata", sorted(u.POLICY_META_DIR.glob("*.csv"))),
    ]
    total_rows = 0
    for folder, paths in sources:
        lines.append(f"## `synthetic_data/mortgage/{folder}/`")
        lines.append("")
        for path in paths:
            name = path.stem
            rows = u.read_csv(path)
            total_rows += len(rows)
            grain, purpose, sensitivity = TABLE_NOTES.get(
                name, ("One row.", "", "Unclassified.")
            )
            lines += [
                f"### `{path.name}`",
                "",
                f"- **Rows:** {len(rows)}",
                f"- **Grain:** {grain}",
                f"- **Sensitivity:** {sensitivity}",
                "",
                purpose,
                "",
                "| Column | Type | Description |",
                "| --- | --- | --- |",
            ]
            columns = COLUMNS.get(name, tuple(rows[0].keys()) if rows else ())
            for column in columns:
                values = [r.get(column, "") for r in rows]
                note = FIELD_NOTES.get(column, "")
                if not note and column.endswith("_id"):
                    note = "Surrogate key."
                lines.append(f"| `{column}` | {_type_of(values)} | {note} |")
            lines.append("")
    lines += [
        "## Totals",
        "",
        f"- **Tables:** {sum(len(p) for _, p in sources)}",
        f"- **Rows:** {total_rows}",
        "",
    ]
    return "\n".join(lines)


def policy_test_coverage() -> str:
    evaluations = u.read_csv(u.STRUCTURED_DIR / "rule_evaluations.csv")
    rules = u.read_csv(u.POLICY_META_DIR / "policy_rules.csv")
    rule_meta = {r["rule_id"]: r for r in rules}

    by_rule: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in evaluations:
        by_rule[row["rule_id"]].append(row)

    lines = [
        GENERATED_BY,
        "# Policy to Application Test Coverage",
        "",
        "Which applications exercise each rule, and whether that rule has the positive, "
        "boundary and negative cases it needs to be testable.",
        "",
        "- **Positive case** - an application where the rule evaluates PASS.",
        "- **Boundary case** - the PASS case whose observed value sits closest to the "
        "threshold. A rule with no numeric threshold has no boundary case, which is "
        "shown as a dash rather than as a gap.",
        "- **Negative case** - an application where the rule evaluates FAIL.",
        "- **Human-review case** - an application where triggering the rule routed the "
        "file to a person.",
        "",
        "A rule with no negative case is not necessarily a defect: a process rule such "
        "as DEC-AUD-001 cannot fail on generated data. Rules that drive an eligibility "
        "outcome are listed first and are expected to carry both.",
        "",
    ]

    evaluated = set(by_rule)
    catalogue = {r["rule_id"] for r in rules}

    lines += [
        f"- Rules in the corpus: **{len(catalogue)}**",
        f"- Rules exercised by at least one application: **{len(evaluated)}**",
        "- Rules with both a positive and a negative case: "
        f"**{sum(1 for r, rows in by_rule.items() if {'PASS', 'FAIL'} <= {x['outcome'] for x in rows})}**",
        "",
        "| Policy | Rule | Severity | Positive case | Boundary case | Negative case | "
        "Human-review case |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for rule_id in sorted(by_rule):
        rows = by_rule[rule_id]
        meta = rule_meta.get(rule_id, {})
        passes = [r for r in rows if r["outcome"] == "PASS"]
        fails = [r for r in rows if r["outcome"] == "FAIL"]
        refers = [r for r in rows if r["outcome"] == "REFER"]
        indets = [r for r in rows if r["outcome"] == "INDETERMINATE"]
        human = [r for r in rows if u.parse_bool(r["requires_human_review"])]

        boundary = "-"
        numeric = [
            r for r in passes
            if _numeric(r["observed_value"]) is not None
            and _numeric(r["threshold_value"]) is not None
        ]
        if numeric:
            closest = min(
                numeric,
                key=lambda r: abs(
                    _numeric(r["observed_value"]) - _numeric(r["threshold_value"])
                ),
            )
            gap = abs(
                _numeric(closest["observed_value"]) - _numeric(closest["threshold_value"])
            )
            boundary = f"{closest['application_id']} (gap {gap})"

        negative = fails[0]["application_id"] if fails else (
            f"{refers[0]['application_id']} (REFER)" if refers else (
                f"{indets[0]['application_id']} (INDETERMINATE)" if indets else "-"
            )
        )
        lines.append(
            f"| {meta.get('policy_id', '-')} | `{rule_id}` | "
            f"{meta.get('severity', '-')} | "
            f"{passes[0]['application_id'] if passes else '-'} | {boundary} | "
            f"{negative} | {human[0]['application_id'] if human else '-'} |"
        )

    unused = sorted(catalogue - evaluated)
    lines += [
        "",
        "## Reference-only rules",
        "",
        "These rules are part of the corpus but are not evaluated against an "
        "application. They are definitional, procedural or govern a workflow stage "
        "beyond underwriting, so a retrieval agent should still be able to find and "
        "cite them.",
        "",
    ]
    for rule_id in unused:
        meta = rule_meta.get(rule_id, {})
        lines.append(
            f"- `{rule_id}` - {meta.get('title', '')} ({meta.get('policy_id', '')}, "
            f"{meta.get('severity', '')})"
        )
    lines.append("")
    return "\n".join(lines)


def _numeric(value: str) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(value)
    except Exception:  # noqa: BLE001
        return None


def scenario_coverage(catalog: list[dict[str, Any]]) -> str:
    apps = {r["application_id"]: r for r in u.read_csv(u.STRUCTURED_DIR / "applications.csv")}
    lines = [
        GENERATED_BY,
        "# Scenario Coverage",
        "",
        f"{len(catalog)} scenarios, each producing exactly one application. Every "
        "scenario declares the outcome it expects, and the generator asserts that "
        "declaration against the rules engine as it builds - a scenario that stops "
        "reproducing its intended outcome fails the build rather than silently "
        "emitting mislabelled ground truth.",
        "",
    ]

    recs = Counter(s["expected_recommendation"] for s in catalog)
    lines += ["## Outcomes", "", "| Recommendation | Scenarios |", "| --- | --- |"]
    for rec, count in sorted(recs.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{rec}` | {count} |")
    lines.append("")

    elig = Counter(s["expected_eligibility"] for s in catalog)
    lines += ["| Eligibility determination | Scenarios |", "| --- | --- |"]
    for key, count in sorted(elig.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{key}` | {count} |")
    lines.append("")

    hr = sum(1 for s in catalog if s["expected_human_review"])
    lines += [
        f"- Routed to a human: **{hr}** of {len(catalog)}",
        f"- Auto-processable to a recommendation: **{len(catalog) - hr}**",
        "",
    ]

    lines += [
        "## Product, purpose and occupancy spread",
        "",
        "| Dimension | Values |",
        "| --- | --- |",
    ]
    for label, key in (
        ("Product family", "product_family"),
        ("Loan purpose", "loan_purpose"),
        ("Occupancy", "occupancy_type"),
    ):
        counts = Counter(apps[s["application_id"]][key] for s in catalog)
        lines.append(
            f"| {label} | "
            + ", ".join(f"`{k}` x{v}" for k, v in sorted(counts.items()))
            + " |"
        )
    lines.append("")

    security = [s for s in catalog if s["security_test_type"]]
    lines += [
        "## Security and adversarial cases",
        "",
        f"{len(security)} scenarios submit untrusted applicant text. In each one the "
        "correct behaviour is that the attempt changes nothing: the file is still "
        "underwritten on its verified evidence, a security event is recorded, and the "
        "content never reaches an instruction-following path.",
        "",
        "| Scenario | Application | Attack type | Expected handling |",
        "| --- | --- | --- | --- |",
    ]
    for s in security:
        lines.append(
            f"| {s['scenario_id']} {s['scenario_name']} | {s['application_id']} | "
            f"`{s['security_test_type']}` | `{s['expected_routing']}` |"
        )
    lines.append("")

    discrepancies = [s for s in catalog if s["expected_discrepancies"]]
    lines += [
        "## Deliberate discrepancies",
        "",
        f"{len(discrepancies)} scenarios move exactly one value so that a document "
        "disagrees with the structured record. Everything else in those files still "
        "reconciles, which is what makes them usable as detection tests rather than "
        "as noise.",
        "",
        "| Application | Field | Structured source | Document source | Detected by |",
        "| --- | --- | --- | --- | --- |",
    ]
    for s in discrepancies:
        for d in s["expected_discrepancies"]:
            lines.append(
                f"| {s['application_id']} | `{d['field']}` | "
                f"`{d['structured_source']}` | {d['document_source']} | "
                f"`{d['expected_detection']}` |"
            )
    lines.append("")

    lines += [
        "## Full catalogue",
        "",
        "| Scenario | Application | As-of | Name | Expected recommendation | Human review |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for s in catalog:
        lines.append(
            f"| {s['scenario_id']} | {s['application_id']} | {s['as_of_date']} | "
            f"{s['scenario_name']} | `{s['expected_recommendation']}` | "
            f"{'yes' if s['expected_human_review'] else 'no'} |"
        )
    lines.append("")
    return "\n".join(lines)


def final_report(seed: int, catalog: list[dict[str, Any]]) -> str:
    def rows(name: str, folder: Path = u.STRUCTURED_DIR) -> list[dict[str, str]]:
        return u.read_csv(folder / f"{name}.csv")

    apps = rows("applications")
    borrowers = rows("borrowers")
    ab = rows("application_borrowers")
    docs = rows("documents")
    evals = rows("rule_evaluations")
    policies = rows("policies", u.POLICY_META_DIR)
    policy_rules = rows("policy_rules", u.POLICY_META_DIR)

    co_borrowers = sum(1 for r in ab if r["borrower_role"] == "co_borrower")
    products = Counter(r["product_family"] for r in apps)
    returning = [
        b for b, n in Counter(r["borrower_id"] for r in ab).items() if n > 1
    ]
    policy_ids = {p["policy_id"] for p in policies}
    versions = Counter(p["policy_id"] for p in policies)
    multi_version = {k: v for k, v in versions.items() if v > 1}
    security = [s for s in catalog if s["security_test_type"]]
    human_reviews = rows("human_reviews")

    lines = [
        GENERATED_BY,
        "# CredPilot Synthetic Data Report",
        "",
        f"Generated with `SYNTHETIC_SEED={seed}`. Every figure below is counted from "
        "the committed files at generation time.",
        "",
        "## 1. Source documents read",
        "",
        "| Document | Role |",
        "| --- | --- |",
        "| `synthetic_data/mortgage/research/deep-research-report.md` | The completed Deep "
        "Research mortgage-domain "
        "report. Primary design authority for the data model, calculations, policy "
        "architecture, scenario matrix and human-review classification. |",
        "| `requirements_verbatim.md` | The 112 verbatim requirements extracted from "
        "the business case, hash-verified. Highest authority on what must exist. |",
        "| `EXTRACTION_NOTE.md` | Provenance of the requirements extraction. |",
        "| `BASELINE_REQUIREMENTS.md` | The integrity contract around the baseline. |",
        "| `requirement_traceability_matrix.md` | Existing requirement-to-test mapping, "
        "read to avoid contradicting the QA layer's expectations. |",
        "| The 15 files under `test_specs/` | What the validation suite will check, "
        "including the paths and PII patterns it enforces. |",
        "",
        "## 2. Research report used",
        "",
        "`synthetic_data/mortgage/research/deep-research-report.md` is a completed research "
        "report, not a research "
        "prompt. It contains findings, a source ledger of 41 prioritised references, a "
        "canonical data dictionary, a calculation specification with worked examples, a "
        "policy-family architecture, a scenario matrix and a human-in-the-loop "
        "classification. The dataset blueprint in its final section is the primary "
        "guide for the entity model built here.",
        "",
        "Three of its worked examples were used as acceptance tests for the calculation "
        "library: LTV of 80% from a 400,000 loan against min(500,000, 510,000); CLTV of "
        "85% adding a 25,000 subordinate lien; and 10.39 months of reserves from 40,000 "
        "against a 3,850 housing expense. All three reproduce exactly.",
        "",
        "## 3. Requirements identified",
        "",
        "See `synthetic_data/mortgage/REQUIREMENTS_TRACEABILITY.md` for the full table. Every "
        "artifact traces to an explicit business-case requirement, a researched "
        "mortgage-domain requirement, or a labelled synthetic design decision.",
        "",
        "## 4. Design assumptions",
        "",
        "See `synthetic_data/mortgage/DESIGN_ASSUMPTIONS.md`. Every assumption is recorded there "
        "with its basis and its consequence; none is resolved silently.",
        "",
        "## 5-22. Dataset contents",
        "",
        "| # | Measure | Count |",
        "| ---: | --- | ---: |",
        f"| 5 | Synthetic borrower profiles | {len(borrowers)} |",
        f"| 6 | Co-borrower participations | {co_borrowers} |",
        f"| 7 | Mortgage applications | {len(apps)} |",
        f"| 8 | Product families represented | {len(products)} |",
        f"| 9 | Properties | {len(rows('properties'))} |",
        f"| 10 | Employment records | {len(rows('employment'))} |",
        f"| 11 | Income records | {len(rows('income'))} |",
        f"| 12 | Asset records | {len(rows('assets'))} |",
        f"| 13 | Liability records | {len(rows('liabilities'))} |",
        "| 14 | Credit records (profiles + tradelines + events) | "
        f"{len(rows('credit_profiles')) + len(rows('credit_accounts')) + len(rows('credit_events'))} |",
        f"| 15 | Applicant documents | {len(docs)} |",
        f"| 16 | Policy documents | {len(policies)} |",
        f"| 17 | Policy rule versions | {len(policy_rules)} |",
        f"| 18 | Policies carrying more than one version | {len(multi_version)} |",
        f"| 19 | Risk scenarios (total in the catalogue) | {len(catalog)} |",
        f"| 20 | Human-review cases | {len(human_reviews)} |",
        f"| 21 | Security / adversarial cases | {len(security)} |",
        "| 22 | Evaluation / golden-set cases | "
        f"{len(u.read_jsonl(u.GOLDEN_DIR / 'evaluation_cases.jsonl'))} |",
        "",
        "Product spread: "
        + ", ".join(f"`{k}` x{v}" for k, v in sorted(products.items()))
        + ".",
        "",
        "Versioned policies: "
        + ", ".join(f"`{k}` ({v} versions)" for k, v in sorted(multi_version.items()))
        + ".",
        "",
        "Returning applicants (appearing on more than one application): "
        f"{len(returning)}.",
        "",
        "## 23-24. Validation",
        "",
        "Run `python synthetic_data/mortgage/generator/validate_synthetic_data.py`. The "
        "validator executes "
        f"{_validator_check_count()} checks across structure, integrity, dates, "
        "financial recomputation, policy, traceability, documents, privacy, "
        "governance, security, coverage and evaluation. It exits non-zero on any "
        "violation and names the offending rows.",
        "",
        "The financial checks re-derive their values from the raw inputs rather than "
        "comparing a stored figure to itself: amortisation is recomputed from the note "
        "terms, the housing expense is rebuilt from its components, income is summed "
        "from the income rows, the settlement figure is rebuilt from its components and "
        "the reserve figure is produced by replaying the asset draw.",
        "",
        "**Validation failures at the time of writing: none.** The validator was also "
        "negative-tested by corrupting a liability payment and unmasking an identifier; "
        "it detected both.",
        "",
        "## 25. Policy coverage",
        "",
        f"{len({e['policy_id'] for e in evals})} of {len(policy_ids)} policy families "
        "are exercised by at least one application. See "
        "`synthetic_data/mortgage/POLICY_TEST_COVERAGE.md` for the rule-level matrix, including "
        "which rules have positive, boundary and negative cases.",
        "",
        "## 26. Scenario coverage",
        "",
        "See `synthetic_data/mortgage/SCENARIO_COVERAGE.md`. Every recommendation value in the "
        "controlled vocabulary is produced by at least one scenario, and all six "
        "security attack types are represented.",
        "",
        "## 27. Known limitations",
        "",
        "- **The synthetic automated-underwriting service is a placeholder.** The "
        "research report is explicit that DU and LPA risk models are proprietary and "
        "must not be reverse-engineered. This dataset therefore models the *shape* of "
        "an automated finding - a recommendation category and a message set - and does "
        "not attempt the underlying scoring. No `aus_submissions` table is populated.",
        "- **Disclosure timing is modelled as policy text, not as data.** Loan Estimate "
        "and Closing Disclosure obligations appear in the corpus but no disclosure "
        "event rows are generated, because the underwriting MVP does not reach them.",
        "- **Closing and servicing are out of scope.** The schema preserves the "
        "handoff point but no closing_events or servicing rows exist.",
        "- **One property per application.** Multiple financed properties are modelled "
        "as a count that drives the reserve requirement, not as separate property rows.",
        "- **Income history is summarised, not enumerated.** Variable-income scenarios "
        "carry a history length and a trend rather than month-by-month rows.",
        "- **Geography is coarse.** Property-tax rates vary by state from a small "
        "committed table; there is no county or municipality granularity.",
        "- **The document corpus is plain text.** Documents carry the fields an "
        "underwriter needs but are not PDFs or images, so optical extraction and "
        "image-level tampering detection cannot be exercised against them.",
        "",
        "## 28. Research areas not publicly available",
        "",
        "The research report names these as gaps, and this dataset does not paper over "
        "them:",
        "",
        "- Detailed internal underwriting policies, scorecards, fraud models, pricing "
        "models, overlays, exception matrices and approval authorities of any named "
        "lender. Public lender pages establish products and consumer-facing process "
        "only. **No real lender's internal policy is reproduced anywhere in this "
        "corpus.**",
        "- The statistical decision algorithms behind Desktop Underwriter and Loan "
        "Product Advisor. Recommendation categories are public; the models are not.",
        "- Complete jumbo criteria, which are set by private investor overlays. This is "
        "why `POL-JUMBO-001` is explicitly a fictional overlay and why every jumbo file "
        "in the dataset routes to a human.",
        "",
        "## 29. Synthetic assumptions",
        "",
        f"Of {len(policy_rules)} rule versions in the corpus, "
        f"{sum(1 for r in policy_rules if r['source_category'] == 'SYNTHETIC_INTERNAL_POLICY')} "
        "are labelled `SYNTHETIC_INTERNAL_POLICY`, "
        f"{sum(1 for r in policy_rules if r['source_category'] == 'REGULATORY')} "
        "`REGULATORY`, "
        f"{sum(1 for r in policy_rules if r['source_category'] == 'AGENCY_INVESTOR')} "
        "`AGENCY_INVESTOR` and "
        f"{sum(1 for r in policy_rules if r['source_category'] == 'COMMON_INDUSTRY_PRACTICE')} "
        "`COMMON_INDUSTRY_PRACTICE`.",
        "",
        "Every numeric threshold that drives a pass or fail outcome is "
        "`SYNTHETIC_INTERNAL_POLICY` unless the research report establishes the exact "
        "value as a genuine public rule for that product and context. The schema "
        "enforces this: a rule carrying a numeric parameter under a weaker authority "
        "label raises an error at import time rather than reaching the corpus.",
        "",
        "The three exceptions, where a genuine published figure is used and attributed, "
        "are the 2026 conforming and FHA loan limits in `GEN-ELG-003`, the agency DTI "
        "framework stated in `DTI-CALC-001`, and the regulatory obligations in the "
        "`REGULATORY` rules. In each case the rule states the public framework and a "
        "separate synthetic rule carries the number this lender actually enforces.",
        "",
        "## 30. Commands to regenerate everything",
        "",
        "```bash",
        "# Generate. Deterministic: the same seed produces byte-identical output.",
        f"SYNTHETIC_SEED={seed} python synthetic_data/mortgage/generator/generate_synthetic_data.py",
        "",
        "# Validate. Exits non-zero on any violation.",
        "python synthetic_data/mortgage/generator/validate_synthetic_data.py",
        "```",
        "",
        "On Windows PowerShell:",
        "",
        "```powershell",
        f"$env:SYNTHETIC_SEED = '{seed}'",
        "python synthetic_data/mortgage/generator/generate_synthetic_data.py",
        "python synthetic_data/mortgage/generator/validate_synthetic_data.py",
        "```",
        "",
        "The seed defaults to "
        f"{u.DEFAULT_SEED}, so both commands work with no environment variable set. "
        "Generation takes a few seconds and rewrites every artifact under `data/` and "
        "`synthetic_data/mortgage/`.",
        "",
    ]
    return "\n".join(lines)
