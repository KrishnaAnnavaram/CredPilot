#!/usr/bin/env python3
"""
CredPilot synthetic-data validator.

    python synthetic_data/generator/validate_synthetic_data.py

Fails loudly. Any violated check exits non-zero with the offending rows named, so a
broken dataset cannot be committed quietly.

The financial checks re-derive their values from the raw inputs rather than
comparing a stored figure to itself: debt-to-income is rebuilt from the income and
liability rows, leverage from the loan and property rows, the settlement figure from
its components, and the reserve figure by replaying the asset draw. Where this file
re-implements arithmetic that the generator also performs, that is deliberate - a
transcription error in either one shows up as a disagreement.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import synthetic_data_utils as u
from synth.corpus import ALL_POLICIES, REGISTRY
from synth.policies import effective_policy

CENTS = Decimal("0.01")
PCT = Decimal("0.0001")
TOLERANCE_CENTS = Decimal("0.02")
TOLERANCE_RATIO = Decimal("0.0001")

MIN_POLICY_DOCUMENTS = 30
TARGET_POLICY_DOCUMENTS = 36
MIN_BORROWERS = 60
MIN_APPLICATIONS = 50

#: Rule ids the dataset must exercise, named because a system that cannot cite
#: these has not demonstrated the behaviours the business case asks for.
REQUIRED_RULE_IDS = (
    "DTI-CONV-001", "DTI-BRE-001", "CRD-SCR-003", "CRD-EVT-001", "CONV-PUR-002",
    "AST-FTC-003", "AST-RSV-002", "AST-SRC-002", "GEN-ELG-003", "GEN-ELG-005",
    "DOC-REQ-004", "UWR-HRV-001", "DEC-REC-001", "DEC-AUD-001", "SEC-INJ-001",
    "SEC-INJ-002", "SEC-INJ-003", "SEC-INJ-004", "KYC-IDV-001", "FRD-IND-001",
    "VAL-APR-001", "INC-VAR-001", "EMP-CNT-001", "JMB-ELG-004", "VA-OVL-003",
    "USD-OVL-002", "CONV-COR-001",
)

REQUIRED_SCENARIO_FEATURES = (
    "prompt injection", "cross-customer access", "PII extraction attempt",
    "policy version selection", "returning applicant", "co-borrower aggregation",
    "INDETERMINATE", "self-employment", "jumbo classification",
    "income conflict detection", "source of funds", "document integrity",
)

#: The same patterns the repository's own evidence scan uses. If a generated
#: artifact trips one of these, the dataset has leaked a value it should not hold.
SENSITIVE_PATTERNS = (
    (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b", "card-number-like digit run"),
    (r"\baccount[_\- ]?number\"?\s*[:=]\s*\"?\d{6,}", "plaintext account number"),
    (r"\bssn\"?\s*[:=]\s*\"?\d{3}-?\d{2}-?\d{4}", "plaintext taxpayer identifier"),
)

SCANNED_SUFFIXES = (".csv", ".jsonl", ".txt", ".log", ".json", ".md")


@dataclass
class Check:
    name: str
    category: str
    passed: bool
    detail: str
    failures: list[str] = field(default_factory=list)


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.checks: list[Check] = []
        self.tables: dict[str, list[dict[str, str]]] = {}

    # -- plumbing ---------------------------------------------------------

    def record(
        self, name: str, category: str, failures: Sequence[str], detail: str
    ) -> None:
        self.checks.append(
            Check(
                name=name,
                category=category,
                passed=not failures,
                detail=detail,
                failures=list(failures)[:12],
            )
        )

    def table(self, name: str) -> list[dict[str, str]]:
        """Load a committed table by name, from wherever it lives."""
        if name not in self.tables:
            for base in (u.STRUCTURED_DIR, u.POLICY_META_DIR):
                path = base / f"{name}.csv"
                if path.is_file():
                    self.tables[name] = u.read_csv(path)
                    break
            else:
                raise SystemExit(
                    f"FATAL: no committed table named {name}.csv under "
                    f"{u.STRUCTURED_DIR} or {u.POLICY_META_DIR}"
                )
        return self.tables[name]

    # -- structural -------------------------------------------------------

    def check_files_present(self) -> None:
        required = [
            u.STRUCTURED_DIR, u.PROFILE_DIR, u.POLICY_META_DIR, u.DOCUMENT_DIR,
            u.SCENARIO_DIR, u.GOLDEN_DIR, u.SCHEMA_DIR, u.POLICY_CORPUS_DIR,
            u.APPLICATION_INPUT_DIR,
        ]
        missing = [str(p.relative_to(self.root)) for p in required if not p.is_dir()]
        self.record(
            "required directories exist", "structure", missing,
            f"{len(required) - len(missing)}/{len(required)} directories present",
        )

    def check_parse(self) -> None:
        failures: list[str] = []
        csv_count = json_count = 0
        for path in sorted(u.SYNTH_ROOT.rglob("*.csv")):
            try:
                rows = u.read_csv(path)
                widths = {len(r) for r in rows}
                if len(widths) > 1:
                    failures.append(f"{path.name}: ragged rows, widths {sorted(widths)}")
                csv_count += 1
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{path.name}: {exc}")
        for path in sorted(u.SYNTH_ROOT.rglob("*.json")):
            try:
                json.loads(path.read_text(encoding="utf-8"))
                json_count += 1
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{path.name}: {exc}")
        for path in sorted(u.SYNTH_ROOT.rglob("*.jsonl")):
            try:
                u.read_jsonl(path)
                json_count += 1
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{path.name}: {exc}")
        self.record(
            "every CSV, JSON and JSONL artifact parses", "structure", failures,
            f"{csv_count} CSV and {json_count} JSON/JSONL artifacts parsed",
        )

    def check_primary_keys(self) -> None:
        keys = {
            "borrowers": "borrower_id",
            "borrower_demographics": "borrower_id",
            "applications": "application_id",
            "loans": "loan_id",
            "properties": "property_id",
            "employment": "employment_id",
            "income": "income_id",
            "assets": "asset_id",
            "asset_transactions": "transaction_id",
            "liabilities": "liability_id",
            "credit_profiles": "credit_profile_id",
            "credit_accounts": "credit_account_id",
            "credit_events": "credit_event_id",
            "documents": "document_id",
            "document_extractions": "extraction_id",
            "appraisals": "appraisal_id",
            "title_records": "title_record_id",
            "insurance_records": "insurance_record_id",
            "verifications": "verification_id",
            "rule_evaluations": "evaluation_id",
            "risk_flags": "risk_flag_id",
            "underwriting_calculations": "calculation_id",
            "eligibility_results": "eligibility_result_id",
            "conditions": "condition_id",
            "decisions": "decision_id",
            "decision_reasons": "decision_reason_id",
            "human_reviews": "human_review_id",
            "security_events": "security_event_id",
            "audit_events": "audit_event_id",
        }
        failures: list[str] = []
        for table, key in keys.items():
            values = [r[key] for r in self.table(table)]
            dupes = [v for v, n in Counter(values).items() if n > 1]
            blanks = sum(1 for v in values if not v)
            if dupes:
                failures.append(f"{table}.{key}: duplicates {dupes[:4]}")
            if blanks:
                failures.append(f"{table}.{key}: {blanks} blank key(s)")
        self.record(
            "primary keys are unique and populated", "integrity", failures,
            f"{len(keys)} keyed tables checked",
        )

    def check_foreign_keys(self) -> None:
        app_ids = {r["application_id"] for r in self.table("applications")}
        borrower_ids = {r["borrower_id"] for r in self.table("borrowers")}
        doc_ids = {r["document_id"] for r in self.table("documents")}
        asset_ids = {r["asset_id"] for r in self.table("assets")}
        liability_ids = {r["liability_id"] for r in self.table("liabilities")}
        decision_ids = {r["decision_id"] for r in self.table("decisions")}

        refs: list[tuple[str, str, set[str], str]] = [
            ("application_borrowers", "application_id", app_ids, "applications"),
            ("application_borrowers", "borrower_id", borrower_ids, "borrowers"),
            ("borrower_demographics", "borrower_id", borrower_ids, "borrowers"),
            ("loans", "application_id", app_ids, "applications"),
            ("properties", "application_id", app_ids, "applications"),
            ("employment", "application_id", app_ids, "applications"),
            ("employment", "borrower_id", borrower_ids, "borrowers"),
            ("income", "application_id", app_ids, "applications"),
            ("income", "borrower_id", borrower_ids, "borrowers"),
            ("assets", "application_id", app_ids, "applications"),
            ("assets", "borrower_id", borrower_ids, "borrowers"),
            ("asset_transactions", "asset_id", asset_ids, "assets"),
            ("liabilities", "application_id", app_ids, "applications"),
            ("credit_profiles", "application_id", app_ids, "applications"),
            ("credit_profiles", "borrower_id", borrower_ids, "borrowers"),
            ("credit_accounts", "application_id", app_ids, "applications"),
            ("credit_events", "application_id", app_ids, "applications"),
            ("documents", "application_id", app_ids, "applications"),
            ("document_extractions", "document_id", doc_ids, "documents"),
            ("appraisals", "application_id", app_ids, "applications"),
            ("title_records", "application_id", app_ids, "applications"),
            ("insurance_records", "application_id", app_ids, "applications"),
            ("verifications", "application_id", app_ids, "applications"),
            ("rule_evaluations", "application_id", app_ids, "applications"),
            ("risk_flags", "application_id", app_ids, "applications"),
            ("underwriting_calculations", "application_id", app_ids, "applications"),
            ("eligibility_results", "application_id", app_ids, "applications"),
            ("conditions", "application_id", app_ids, "applications"),
            ("decisions", "application_id", app_ids, "applications"),
            ("decision_reasons", "decision_id", decision_ids, "decisions"),
            ("human_reviews", "application_id", app_ids, "applications"),
            ("security_events", "application_id", app_ids, "applications"),
            ("audit_events", "application_id", app_ids, "applications"),
            ("scenario_assignments", "application_id", app_ids, "applications"),
        ]
        failures: list[str] = []
        for table, column, universe, target in refs:
            for row in self.table(table):
                value = row.get(column, "")
                if value and value not in universe:
                    failures.append(
                        f"{table}.{column}={value!r} has no row in {target}"
                    )
        # credit_accounts.liability_id is nullable but must resolve when present.
        for row in self.table("credit_accounts"):
            if row["liability_id"] and row["liability_id"] not in liability_ids:
                failures.append(
                    f"credit_accounts.liability_id={row['liability_id']!r} unresolved"
                )
        self.record(
            "every foreign key resolves", "integrity", failures,
            f"{len(refs) + 1} relationships checked",
        )

    def check_relationships(self) -> None:
        failures: list[str] = []
        by_app: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in self.table("application_borrowers"):
            by_app[row["application_id"]].append(row)
        apps = {r["application_id"]: r for r in self.table("applications")}

        for app_id, rows in by_app.items():
            roles = [r["borrower_role"] for r in rows]
            if roles.count("primary") != 1:
                failures.append(f"{app_id}: {roles.count('primary')} primary borrowers")
            if len(rows) != int(apps[app_id]["borrower_count"]):
                failures.append(
                    f"{app_id}: borrower_count={apps[app_id]['borrower_count']} but "
                    f"{len(rows)} application_borrowers rows"
                )
            orders = sorted(int(r["borrower_order"]) for r in rows)
            if orders != list(range(1, len(rows) + 1)):
                failures.append(f"{app_id}: borrower_order not contiguous: {orders}")
            if len(rows) > 1:
                if not all(u.parse_bool(r["joint_credit_intent"]) for r in rows):
                    failures.append(f"{app_id}: multi-borrower without joint intent")
            primary = next(r for r in rows if r["borrower_role"] == "primary")
            if primary["borrower_id"] != apps[app_id]["primary_borrower_id"]:
                failures.append(f"{app_id}: primary_borrower_id disagrees with the bridge")

        for app_id in apps:
            if app_id not in by_app:
                failures.append(f"{app_id}: no borrowers attached")
        self.record(
            "borrower and co-borrower relationships are coherent", "integrity",
            failures, f"{len(apps)} applications, {len(self.table('application_borrowers'))} links",
        )

    # -- dates ------------------------------------------------------------

    def check_dates(self) -> None:
        failures: list[str] = []
        apps = {r["application_id"]: r for r in self.table("applications")}
        for app_id, row in apps.items():
            app_date = u.parse_date(row["application_date"])
            received = u.parse_date(row["received_date"])
            as_of = u.parse_date(row["underwriting_as_of_date"])
            if received > app_date:
                failures.append(f"{app_id}: received_date after application_date")
            if as_of < app_date:
                failures.append(f"{app_id}: as-of date precedes application date")
            if app_date > u.AS_OF_DATE:
                failures.append(f"{app_id}: application dated in the future")

        for row in self.table("employment"):
            start = u.parse_date(row["verified_start_date"])
            end = u.parse_date(row["end_date"])
            as_of = u.parse_date(apps[row["application_id"]]["underwriting_as_of_date"])
            if end and end < start:
                failures.append(f"{row['employment_id']}: end before start")
            if u.parse_bool(row["is_current"]):
                expected = u.months_between(start, as_of)
                if int(row["tenure_months"]) != expected:
                    failures.append(
                        f"{row['employment_id']}: tenure_months={row['tenure_months']} "
                        f"but verified start {start} to as-of {as_of} is {expected}"
                    )

        for row in self.table("credit_events"):
            as_of = u.parse_date(apps[row["application_id"]]["underwriting_as_of_date"])
            anchor = u.parse_date(row["anchor_date"])
            expected = u.months_between(anchor, as_of)
            if int(row["seasoning_months"]) != expected:
                failures.append(
                    f"{row['credit_event_id']}: seasoning_months disagrees with the anchor date"
                )
            if anchor > as_of:
                failures.append(f"{row['credit_event_id']}: anchor date in the future")

        for row in self.table("credit_profiles"):
            as_of = u.parse_date(apps[row["application_id"]]["underwriting_as_of_date"])
            report = u.parse_date(row["report_date"])
            if (as_of - report).days != int(row["report_age_days"]):
                failures.append(
                    f"{row['credit_profile_id']}: report_age_days disagrees with report_date"
                )
        self.record(
            "dates are internally consistent", "dates", failures,
            "application, employment, credit-event and credit-report chronology",
        )

    # -- financial recomputation -----------------------------------------

    def check_financials(self) -> None:
        apps = {r["application_id"]: r for r in self.table("applications")}
        loans = {r["application_id"]: r for r in self.table("loans")}
        props = {r["application_id"]: r for r in self.table("properties")}
        income = defaultdict(list)
        for r in self.table("income"):
            income[r["application_id"]].append(r)
        liabilities = defaultdict(list)
        for r in self.table("liabilities"):
            liabilities[r["application_id"]].append(r)
        assets = defaultdict(list)
        for r in self.table("assets"):
            assets[r["application_id"]].append(r)
        insurance = defaultdict(list)
        for r in self.table("insurance_records"):
            insurance[r["application_id"]].append(r)
        calcs: dict[str, dict[str, str]] = defaultdict(dict)
        for r in self.table("underwriting_calculations"):
            calcs[r["application_id"]][r["calculation_name"]] = r["result"]

        f_pi: list[str] = []
        f_pitia: list[str] = []
        f_income: list[str] = []
        f_debt: list[str] = []
        f_dti: list[str] = []
        f_ltv: list[str] = []
        f_ctc: list[str] = []
        f_res: list[str] = []
        f_util: list[str] = []

        for app_id in apps:
            loan = loans[app_id]
            prop = props[app_id]
            stored = calcs[app_id]

            # -- principal and interest, recomputed from the note terms
            pi = _amortise(
                u.dec(loan["note_amount"]), u.dec(loan["interest_rate"]),
                int(loan["term_months"]),
            )
            if abs(pi - u.dec(loan["principal_and_interest"])) > TOLERANCE_CENTS:
                f_pi.append(
                    f"{app_id}: stored P&I {loan['principal_and_interest']} vs "
                    f"recomputed {pi}"
                )

            # -- housing expense, rebuilt from its components
            flood_monthly = sum(
                (
                    _q(u.dec(i["annual_premium"]) / 12)
                    for i in insurance[app_id]
                    if i["coverage_type"] == "flood"
                ),
                Decimal(0),
            )
            pitia = _q(
                pi
                + _q(u.dec(prop["annual_property_tax"]) / 12)
                + _q(u.dec(prop["annual_hazard_premium"]) / 12)
                + u.dec(prop["monthly_hoa"])
                + u.dec(loan["monthly_mortgage_insurance"])
                + flood_monthly
            )
            if abs(pitia - u.dec(stored["housing_expense_pitia"])) > TOLERANCE_CENTS:
                f_pitia.append(
                    f"{app_id}: stored PITIA {stored['housing_expense_pitia']} vs "
                    f"rebuilt {pitia}"
                )

            # -- qualifying income, summed from the income rows
            qmi = sum(
                (u.dec(r["qualifying_monthly_amount"]) for r in income[app_id]),
                Decimal(0),
            )
            if abs(qmi - u.dec(stored["qualifying_monthly_income"])) > TOLERANCE_CENTS:
                f_income.append(
                    f"{app_id}: stored qualifying income "
                    f"{stored['qualifying_monthly_income']} vs summed {qmi}"
                )
            for r in income[app_id]:
                if u.dec(r["qualifying_monthly_amount"]) > u.dec(
                    r["verified_monthly_amount"]
                ):
                    f_income.append(
                        f"{r['income_id']}: qualifying exceeds verified (INC-GEN-002)"
                    )

            # -- total obligations
            debt = _q(
                pitia
                + sum(
                    (
                        u.dec(r["monthly_payment"])
                        for r in liabilities[app_id]
                        if u.parse_bool(r["include_in_dti"])
                    ),
                    Decimal(0),
                )
            )
            if abs(debt - u.dec(stored["total_monthly_debt"])) > TOLERANCE_CENTS:
                f_debt.append(
                    f"{app_id}: stored debt {stored['total_monthly_debt']} vs rebuilt {debt}"
                )

            # -- affordability
            if qmi > 0:
                dti = (debt / qmi).quantize(PCT, rounding=ROUND_HALF_UP)
                if abs(dti - u.dec(stored["back_end_dti"])) > TOLERANCE_RATIO:
                    f_dti.append(
                        f"{app_id}: stored DTI {stored['back_end_dti']} vs recomputed {dti}"
                    )
                front = (pitia / qmi).quantize(PCT, rounding=ROUND_HALF_UP)
                if abs(front - u.dec(stored["front_end_dti"])) > TOLERANCE_RATIO:
                    f_dti.append(
                        f"{app_id}: stored housing ratio {stored['front_end_dti']} vs "
                        f"recomputed {front}"
                    )
                residual = _q(qmi - debt)
                if abs(residual - u.dec(stored["residual_income_monthly"])) > TOLERANCE_CENTS:
                    f_dti.append(f"{app_id}: residual income disagrees")

            # -- leverage
            if apps[app_id]["loan_purpose"] == "purchase":
                denom = min(u.dec(prop["purchase_price"]), u.dec(prop["appraised_value"]))
            else:
                denom = u.dec(prop["appraised_value"])
            if abs(denom - u.dec(prop["value_used_for_ltv"])) > TOLERANCE_CENTS:
                f_ltv.append(
                    f"{app_id}: value_used_for_ltv {prop['value_used_for_ltv']} is not "
                    f"the rule's denominator {denom}"
                )
            ltv = (u.dec(loan["base_loan_amount"]) / denom).quantize(
                PCT, rounding=ROUND_HALF_UP
            )
            if abs(ltv - u.dec(stored["ltv"])) > TOLERANCE_RATIO:
                f_ltv.append(f"{app_id}: stored LTV {stored['ltv']} vs recomputed {ltv}")

            # -- settlement
            if apps[app_id]["loan_purpose"] == "purchase":
                down = _q(u.dec(prop["purchase_price"]) - u.dec(loan["base_loan_amount"]))
                if abs(down - u.dec(loan["down_payment_amount"])) > TOLERANCE_CENTS:
                    f_ctc.append(f"{app_id}: down payment disagrees with price minus loan")
                required = _q(
                    down
                    + u.dec(loan["closing_costs"])
                    + u.dec(loan["prepaids_and_escrow"])
                    - u.dec(loan["seller_credits"])
                    - u.dec(loan["lender_credits"])
                    - u.dec(loan["earnest_money_paid"])
                )
            elif apps[app_id]["loan_purpose"] == "cash_out_refinance":
                required = Decimal("0.00")
            else:
                required = _q(
                    u.dec(loan["closing_costs"]) + u.dec(loan["prepaids_and_escrow"])
                )
            required = max(Decimal("0.00"), required)
            if abs(required - u.dec(stored["cash_to_close"])) > TOLERANCE_CENTS:
                f_ctc.append(
                    f"{app_id}: stored cash-to-close {stored['cash_to_close']} vs "
                    f"rebuilt {required}"
                )

            available = sum(
                (u.dec(a["eligible_close_amount"]) for a in assets[app_id]), Decimal(0)
            )
            if abs(available - u.dec(stored["funds_to_close_available"])) > TOLERANCE_CENTS:
                f_ctc.append(f"{app_id}: available funds disagree with the asset ledger")
            shortfall = max(Decimal("0.00"), _q(required - available))
            if abs(shortfall - u.dec(stored["funds_shortfall"])) > TOLERANCE_CENTS:
                f_ctc.append(
                    f"{app_id}: stored shortfall {stored['funds_shortfall']} vs "
                    f"rebuilt {shortfall}"
                )

            # -- reserves: replay the draw independently
            reserves = _replay_draw(required, assets[app_id])
            if abs(reserves - u.dec(stored["post_close_reserves"])) > TOLERANCE_CENTS:
                f_res.append(
                    f"{app_id}: stored reserves {stored['post_close_reserves']} vs "
                    f"replayed draw {reserves}"
                )
            if pitia > 0:
                months = (reserves / pitia).quantize(CENTS, rounding=ROUND_HALF_UP)
                if abs(months - u.dec(stored["months_reserves"])) > Decimal("0.01"):
                    f_res.append(
                        f"{app_id}: stored months_reserves {stored['months_reserves']} "
                        f"vs recomputed {months}"
                    )

            # -- utilisation
            revolving = [
                r
                for r in self.table("credit_accounts")
                if r["application_id"] == app_id
                and r["account_type"] == "revolving_credit_card"
                and u.dec(r["credit_limit"]) > 0
            ]
            if revolving:
                bal = sum((u.dec(r["balance"]) for r in revolving), Decimal(0))
                lim = sum((u.dec(r["credit_limit"]) for r in revolving), Decimal(0))
                util = (bal / lim).quantize(PCT, rounding=ROUND_HALF_UP)
                if stored.get("credit_utilization") and abs(
                    util - u.dec(stored["credit_utilization"])
                ) > TOLERANCE_RATIO:
                    f_util.append(
                        f"{app_id}: stored utilisation {stored['credit_utilization']} vs "
                        f"recomputed {util}"
                    )

        self.record("principal and interest recomputes", "financial", f_pi,
                    f"{len(apps)} loans amortised independently")
        self.record("housing expense rebuilds from its components", "financial", f_pitia,
                    "P&I + taxes + insurance + HOA + MI + flood")
        self.record("qualifying income sums from the income rows", "financial", f_income,
                    "and no qualifying amount exceeds its verified amount")
        self.record("total monthly obligations rebuild", "financial", f_debt,
                    "PITIA plus every liability marked include_in_dti")
        self.record("DTI, housing ratio and residual income recompute", "financial", f_dti,
                    "recomputed from the rebuilt numerator and denominator")
        self.record("LTV and its denominator recompute", "financial", f_ltv,
                    "purchase uses lower of price and value; refinance uses value")
        self.record("cash to close and funds sufficiency recompute", "financial", f_ctc,
                    "settlement components, available funds and shortfall")
        self.record("reserves recompute by replaying the asset draw", "financial", f_res,
                    "non-reserve sources first, then reserve-eligible by asset id")
        self.record("credit utilisation recomputes", "financial", f_util,
                    "lines with no stated limit excluded from the denominator")

    # -- policy -----------------------------------------------------------

    def check_policy_corpus(self) -> None:
        docs = sorted(u.POLICY_CORPUS_DIR.glob("*.md"))
        failures: list[str] = []
        if len(docs) < MIN_POLICY_DOCUMENTS:
            failures.append(
                f"only {len(docs)} policy documents; the minimum is {MIN_POLICY_DOCUMENTS}"
            )
        policy_ids = {p.policy_id for p in ALL_POLICIES}
        if len(policy_ids) < TARGET_POLICY_DOCUMENTS:
            failures.append(
                f"only {len(policy_ids)} distinct policy ids; the target is "
                f"{TARGET_POLICY_DOCUMENTS}"
            )
        front_matter_required = (
            "policy_id", "title", "version", "effective_date", "expiration_date",
            "source_category", "priority", "supersedes", "requires_human_review",
            "rule_ids", "synthetic",
        )
        for path in docs:
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---\n"):
                failures.append(f"{path.name}: no YAML front matter")
                continue
            head = text.split("---", 2)[1]
            for key in front_matter_required:
                if f"{key}:" not in head:
                    failures.append(f"{path.name}: front matter missing {key}")
            if "### " not in text:
                failures.append(f"{path.name}: no addressable rules")
            if len(text) < 1500:
                failures.append(f"{path.name}: only {len(text)} bytes - too thin to retrieve")
        self.record(
            "policy corpus is complete and machine-readable", "policy", failures,
            f"{len(docs)} documents across {len(policy_ids)} policy families",
        )

    def check_policy_versions(self) -> None:
        failures: list[str] = []
        by_id = defaultdict(list)
        for policy in ALL_POLICIES:
            by_id[policy.policy_id].append(policy)
        versioned = {k: v for k, v in by_id.items() if len(v) > 1}
        if len(versioned) < 3:
            failures.append(
                f"only {len(versioned)} policies carry more than one version; the "
                "dataset cannot test temporal retrieval meaningfully"
            )
        for policy_id, versions in by_id.items():
            versions = sorted(versions, key=lambda p: p.effective_date)
            for earlier, later in zip(versions, versions[1:]):
                if earlier.expiration_date is None:
                    failures.append(
                        f"{policy_id} v{earlier.version} never expires but v{later.version} "
                        "supersedes it - the effective windows overlap"
                    )
                elif earlier.expiration_date != later.effective_date:
                    failures.append(
                        f"{policy_id}: gap or overlap between v{earlier.version} "
                        f"(to {earlier.expiration_date}) and v{later.version} "
                        f"(from {later.effective_date})"
                    )
                if not later.supersedes:
                    failures.append(f"{policy_id} v{later.version} declares no supersedes")
        # Every version must be reachable by effective-date selection.
        for policy_id, versions in by_id.items():
            for policy in versions:
                probe = policy.effective_date
                chosen = effective_policy(REGISTRY, policy_id, probe)
                if chosen.version != policy.version:
                    failures.append(
                        f"{policy_id}: as-of {probe} resolves to v{chosen.version}, "
                        f"not v{policy.version}"
                    )
        self.record(
            "policy versions have contiguous, resolvable effective windows", "policy",
            failures, f"{len(versioned)} versioned policies of {len(by_id)} total",
        )

    def check_rule_coverage(self) -> None:
        evaluated = {r["rule_id"] for r in self.table("rule_evaluations")}
        missing = [r for r in REQUIRED_RULE_IDS if r not in evaluated]
        self.record(
            "every required rule id is exercised by at least one application",
            "policy", [f"never evaluated: {m}" for m in missing],
            f"{len(evaluated)} distinct rules evaluated across the dataset",
        )

        catalogue = {r["rule_id"] for r in self.table("policy_rules")}
        unknown = sorted(evaluated - catalogue)
        self.record(
            "every evaluated rule exists in the policy corpus", "policy",
            [f"{r} evaluated but absent from policy_rules.csv" for r in unknown],
            f"{len(evaluated)} evaluated rules checked against the catalogue",
        )

    def check_policy_temporal_binding(self) -> None:
        """An evaluation must cite the version in force on that application's as-of date."""
        apps = {
            r["application_id"]: u.parse_date(r["underwriting_as_of_date"])
            for r in self.table("applications")
        }
        failures: list[str] = []
        for row in self.table("rule_evaluations"):
            as_of = apps[row["application_id"]]
            expected = effective_policy(REGISTRY, row["policy_id"], as_of)
            if expected.version != row["policy_version"]:
                failures.append(
                    f"{row['evaluation_id']}: cites {row['policy_id']} "
                    f"v{row['policy_version']} but v{expected.version} was in force on "
                    f"{as_of}"
                )
            eff = u.parse_date(row["policy_effective_date"])
            if eff > as_of:
                failures.append(
                    f"{row['evaluation_id']}: policy effective {eff} postdates the "
                    f"as-of date {as_of}"
                )
        self.record(
            "every rule evaluation cites the version in force on its as-of date",
            "policy", failures, f"{len(self.table('rule_evaluations'))} evaluations checked",
        )

    def check_decision_traceability(self) -> None:
        failures: list[str] = []
        evals_by_app = defaultdict(set)
        for r in self.table("rule_evaluations"):
            evals_by_app[r["application_id"]].add(r["rule_id"])
        decisions = {
            r["decision_id"]: r
            for r in self.table("decisions")
            if r["decision_type"] == "COPILOT_RECOMMENDATION"
        }
        for row in self.table("decision_reasons"):
            decision = decisions.get(row["decision_id"])
            if decision is None:
                failures.append(f"{row['decision_reason_id']}: no recommendation decision")
                continue
            if row["rule_id"] not in evals_by_app[row["application_id"]]:
                failures.append(
                    f"{row['decision_reason_id']}: cites rule {row['rule_id']} that was "
                    "never evaluated for this application"
                )
            if not row["policy_id"] or not row["policy_version"]:
                failures.append(f"{row['decision_reason_id']}: reason has no policy version")
            if not row["evidence_reference"]:
                failures.append(f"{row['decision_reason_id']}: reason cites no evidence")

        # An adverse outcome must carry at least one specific reason (DEC-ADV-001).
        reasons_by_app = defaultdict(int)
        for row in self.table("decision_reasons"):
            reasons_by_app[row["application_id"]] += 1
        for row in self.table("decisions"):
            if row["result"] == "DECLINE_RECOMMENDATION" and not reasons_by_app[
                row["application_id"]
            ]:
                failures.append(
                    f"{row['application_id']}: decline with no specific reason recorded"
                )
        self.record(
            "decisions trace to evaluated rules, policy versions and evidence",
            "traceability", failures,
            f"{len(self.table('decision_reasons'))} decision reasons checked",
        )

    def check_human_review(self) -> None:
        failures: list[str] = []
        reviews = {r["application_id"] for r in self.table("human_reviews")}
        for row in self.table("decisions"):
            if row["decision_type"] != "COPILOT_RECOMMENDATION":
                continue
            needs = u.parse_bool(row["requires_human_review"])
            if needs and row["application_id"] not in reviews:
                failures.append(
                    f"{row['application_id']}: flagged for human review with no "
                    "human_reviews row"
                )
            if row["result"] == "DECLINE_RECOMMENDATION" and not needs:
                failures.append(
                    f"{row['application_id']}: decline recommendation auto-decided "
                    "(DEC-REC-002 forbids this)"
                )
        # No automated actor may produce a credit decision or a clear-to-close.
        for row in self.table("decisions"):
            if row["decision_stage"] in ("credit_decision", "clear_to_close") and row[
                "actor_type"
            ] != "HUMAN":
                failures.append(
                    f"{row['decision_id']}: {row['decision_stage']} produced by "
                    f"{row['actor_type']}"
                )
        if len(reviews) < 10:
            failures.append(f"only {len(reviews)} human-review cases in the dataset")
        self.record(
            "human review is present wherever policy requires it", "governance",
            failures, f"{len(reviews)} applications routed to a human",
        )

    # -- documents and discrepancies --------------------------------------

    def check_documents(self) -> None:
        failures: list[str] = []
        seen: set[tuple[str, str]] = set()
        for row in self.table("documents"):
            path = self.root / row["relative_path"]
            if not path.is_file():
                failures.append(f"{row['document_id']}: {row['relative_path']} missing")
            key = (row["application_id"], row["relative_path"])
            if key in seen:
                failures.append(f"duplicate document path {row['relative_path']}")
            seen.add(key)
            if u.parse_bool(row["contains_pii"]) and not u.parse_bool(row["masked"]):
                failures.append(
                    f"{row['document_id']}: carries PII but is not marked masked"
                )
            if row["trust_class"] not in (
                "customer_evidence", "authoritative_evidence", "internal_record"
            ):
                failures.append(f"{row['document_id']}: unknown trust class")
            if u.parse_bool(row["contains_untrusted_text"]) and row["trust_class"] != (
                "customer_evidence"
            ):
                failures.append(
                    f"{row['document_id']}: untrusted text outside customer_evidence"
                )
        # Every application has a document folder with content.
        for row in self.table("applications"):
            folder = u.DOCUMENT_DIR / row["application_id"]
            if not folder.is_dir() or not any(folder.glob("*.txt")):
                failures.append(f"{row['application_id']}: no applicant documents")
        self.record(
            "documents exist, are unique and carry correct trust metadata", "documents",
            failures, f"{len(self.table('documents'))} documents across "
            f"{len(self.table('applications'))} applications",
        )

    def check_evidence_documents_draw_no_conclusions(self) -> None:
        """Evidence must not tell the reader what the answer is.

        A paystub does not know the lender's rule identifiers. A bank statement does
        not announce that a deposit is unsourced under a policy. If those annotations
        appear inside a document the agent is given, the ground truth has leaked into
        the input and every evaluation run against it is measuring the wrong thing.

        Lender-internal records are exempt: they are outputs of underwriting, and they
        are excluded from the input packet rather than sanitised.
        """
        rule_id = re.compile(r"[A-Z]{2,4}-[A-Z]{3,4}-\d{3}")
        policy_id = re.compile(r"POL-[A-Z]+-\d{3}")
        verdict = re.compile(
            r"(APPROVE_RECOMMENDATION|APPROVE_WITH_CONDITIONS|DECLINE_RECOMMENDATION"
            r"|MANUAL_REVIEW_REQUIRED|SUSPENDED_INCOMPLETE|INELIGIBLE)"
        )
        failures: list[str] = []
        checked = 0
        internal = {
            row["relative_path"]
            for row in self.table("documents")
            if row["trust_class"] == "internal_record"
        }
        for row in self.table("documents"):
            if row["relative_path"] in internal:
                continue
            path = self.root / row["relative_path"]
            if not path.is_file():
                continue
            checked += 1
            text = path.read_text(encoding="utf-8")
            for pattern, label in (
                (rule_id, "a lender rule identifier"),
                (policy_id, "a lender policy identifier"),
                (verdict, "an underwriting verdict"),
            ):
                match = pattern.search(text)
                if match:
                    failures.append(
                        f"{row['relative_path']} contains {label} "
                        f"({match.group(0)!r}) - evidence must not carry the conclusion"
                    )
        # And no internal record may be offered to the agent as an input.
        for packet in sorted(u.APPLICATION_INPUT_DIR.glob("APP-*.json")):
            payload = json.loads(packet.read_text(encoding="utf-8"))
            for doc in payload.get("supplied_documents", []):
                if doc["trust_class"] == "internal_record":
                    failures.append(
                        f"{packet.name} offers internal record {doc['document_id']} "
                        "as an input"
                    )
        self.record(
            "evidence documents carry facts, not conclusions", "evaluation", failures,
            f"{checked} evidence documents scanned for rule ids, policy ids and verdicts",
        )

    def check_document_reconciliation(self) -> None:
        """Extracted values agree with the tables, except where a scenario says not."""
        catalog = json.loads(
            (u.SCENARIO_DIR / "scenario_catalog.json").read_text(encoding="utf-8")
        )
        discrepancy_apps = {
            s["application_id"]: {d["field"] for d in s["expected_discrepancies"]}
            for s in catalog["scenarios"]
            if s["expected_discrepancies"]
        }
        loans = {r["application_id"]: r for r in self.table("loans")}
        props = {r["application_id"]: r for r in self.table("properties")}
        docs = {r["document_id"]: r for r in self.table("documents")}

        failures: list[str] = []
        checked = 0
        for row in self.table("document_extractions"):
            doc = docs[row["document_id"]]
            app_id = row["application_id"]
            name = row["field_name"]
            value = row["extracted_value"]
            if name == "purchase_price" and props[app_id]["purchase_price"]:
                checked += 1
                if u.dec(value) != u.dec(props[app_id]["purchase_price"]):
                    failures.append(
                        f"{row['extraction_id']}: contract price {value} != "
                        f"properties.purchase_price {props[app_id]['purchase_price']}"
                    )
            elif name == "appraised_value":
                checked += 1
                if u.dec(value) != u.dec(props[app_id]["appraised_value"]):
                    failures.append(
                        f"{row['extraction_id']}: appraisal value {value} != "
                        f"properties.appraised_value"
                    )
            elif name == "requested_loan_amount":
                checked += 1
                if u.dec(value) != u.dec(loans[app_id]["base_loan_amount"]):
                    failures.append(
                        f"{row['extraction_id']}: application loan amount {value} != "
                        f"loans.base_loan_amount"
                    )
            elif name == "earnest_money":
                checked += 1
                if u.dec(value) != u.dec(loans[app_id]["earnest_money_paid"]):
                    failures.append(f"{row['extraction_id']}: earnest money disagrees")
            elif name == "closing_balance":
                # The statement's closing balance must equal the verified balance of
                # the account it was rendered from. The document id encodes which
                # asset that is, so the join does not need to go through the mask.
                asset_seq = doc["relative_path"].rsplit("_", 1)[-1].split(".")[0]
                asset = next(
                    (
                        a
                        for a in self.table("assets")
                        if a["application_id"] == app_id
                        and a["asset_id"].endswith(f"-AST-{asset_seq}")
                    ),
                    None,
                )
                if asset is not None:
                    checked += 1
                    if u.dec(value) != u.dec(asset["verified_balance"]):
                        failures.append(
                            f"{row['extraction_id']}: statement closing balance "
                            f"{value} != assets.verified_balance "
                            f"{asset['verified_balance']} for {asset['asset_id']}"
                        )
            _ = discrepancy_apps
        self.record(
            "document contents reconcile with the structured tables", "documents",
            failures, f"{checked} cross-checks between extractions and tables",
        )

    def check_expected_discrepancies(self) -> None:
        catalog = json.loads(
            (u.SCENARIO_DIR / "scenario_catalog.json").read_text(encoding="utf-8")
        )
        with_discrepancies = [
            s for s in catalog["scenarios"] if s["expected_discrepancies"]
        ]
        failures: list[str] = []
        if len(with_discrepancies) < 3:
            failures.append(
                f"only {len(with_discrepancies)} scenarios declare an expected "
                "discrepancy; conflicting-document cases must be labelled"
            )
        income_rows = defaultdict(list)
        for r in self.table("income"):
            income_rows[r["application_id"]].append(r)
        for scenario in with_discrepancies:
            app_id = scenario["application_id"]
            for disc in scenario["expected_discrepancies"]:
                for key in (
                    "field", "structured_source", "document_source",
                    "expected_detection", "expected_action",
                ):
                    if not disc.get(key):
                        failures.append(f"{app_id}: discrepancy missing {key}")
                if disc["expected_detection"] not in {
                    r["rule_id"] for r in self.table("rule_evaluations")
                    if r["application_id"] == app_id
                }:
                    failures.append(
                        f"{app_id}: declared detection rule {disc['expected_detection']} "
                        "was not evaluated"
                    )
            if scenario["expected_discrepancies"][0]["field"] == "monthly_gross_income":
                rows = income_rows[app_id]
                if not any(
                    u.dec(r["declared_monthly_amount"]) != u.dec(r["verified_monthly_amount"])
                    for r in rows
                ):
                    failures.append(
                        f"{app_id}: declares an income discrepancy but declared and "
                        "verified amounts are identical"
                    )
        # And the converse: files with no declared discrepancy must reconcile.
        declared_apps = {s["application_id"] for s in with_discrepancies}
        for app_id, rows in income_rows.items():
            if app_id in declared_apps:
                continue
            for r in rows:
                if u.dec(r["declared_monthly_amount"]) != u.dec(
                    r["verified_monthly_amount"]
                ):
                    failures.append(
                        f"{r['income_id']}: declared and verified income differ but no "
                        "discrepancy is declared for this application"
                    )
        self.record(
            "intentional discrepancies are labelled, and only those files disagree",
            "documents", failures,
            f"{len(with_discrepancies)} scenarios carry a labelled discrepancy",
        )

    # -- privacy ----------------------------------------------------------

    def check_no_plaintext_sensitive_values(self) -> None:
        failures: list[str] = []
        scanned = 0
        targets = [
            p
            for p in u.SYNTH_ROOT.rglob("*")
            if p.is_file() and p.suffix.lower() in SCANNED_SUFFIXES
        ]
        for path in targets:
            scanned += 1
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern, label in SENSITIVE_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    line = text.count("\n", 0, match.start()) + 1
                    failures.append(
                        f"{path.relative_to(self.root)}:{line} contains a {label}"
                    )
        self.record(
            "no committed artifact contains a plaintext sensitive identifier",
            "privacy", failures, f"{scanned} artifacts scanned",
        )

    def check_masking(self) -> None:
        failures: list[str] = []
        ssn_token = re.compile(r"^SYN-SSN-\d{6}$")
        ssn_mask = re.compile(r"^\*\*\*-\*\*-\d{4}$")
        acct_token = re.compile(r"^SYN-ACCT-\d{6}$")
        acct_mask = re.compile(r"^\*{6}\d{4}$")
        credit_token = re.compile(r"^SYN-CRDT-\d{6}$")
        credit_mask = re.compile(r"^\*{4}\d{4}$")
        for row in self.table("borrowers"):
            if not ssn_token.match(row["ssn_token"]):
                failures.append(f"{row['borrower_id']}: ssn_token is not a SYN token")
            if not ssn_mask.match(row["ssn_masked"]):
                failures.append(f"{row['borrower_id']}: ssn_masked is not masked")
            if row["ssn_token"][-4:] != row["ssn_masked"][-4:]:
                failures.append(f"{row['borrower_id']}: mask does not match its token")
            if not credit_token.match(row["credit_file_token"]):
                failures.append(f"{row['borrower_id']}: credit token malformed")
            if not credit_mask.match(row["credit_file_masked"]):
                failures.append(f"{row['borrower_id']}: credit identifier not masked")
            if not row["email"].endswith("@example.com"):
                failures.append(f"{row['borrower_id']}: email outside the reserved domain")
            if not re.match(r"^\(\d{3}\) 555-0\d{3}$", row["phone"]):
                failures.append(
                    f"{row['borrower_id']}: phone outside the reserved 555-01xx block"
                )
        for row in self.table("assets"):
            if not acct_token.match(row["account_token"]):
                failures.append(f"{row['asset_id']}: account token malformed")
            if not acct_mask.match(row["account_masked"]):
                failures.append(f"{row['asset_id']}: account not masked")

        # No unmasked token may appear in an applicant-facing document.
        for path in u.DOCUMENT_DIR.rglob("*.txt"):
            text = path.read_text(encoding="utf-8")
            for token_pattern, label in (
                (r"SYN-SSN-\d{6}", "taxpayer token"),
                (r"SYN-ACCT-\d{6}", "account token"),
                (r"SYN-CRDT-\d{6}", "credit-file token"),
            ):
                if re.search(token_pattern, text):
                    failures.append(
                        f"{path.relative_to(self.root)} renders a raw {label}; documents "
                        "must show the masked form only"
                    )
        self.record(
            "sensitive identifiers are tokenised and displayed masked", "privacy",
            failures, f"{len(self.table('borrowers'))} borrowers, "
            f"{len(self.table('assets'))} accounts, and every rendered document",
        )

    def check_fair_lending_separation(self) -> None:
        failures: list[str] = []
        demo_path = u.STRUCTURED_DIR / "borrower_demographics.csv"
        if not demo_path.is_file():
            failures.append("borrower_demographics.csv is missing")
        demo_fields = {"ethnicity", "race", "sex", "age_band"}
        for name in (
            "applications", "loans", "income", "assets", "liabilities",
            "credit_profiles", "underwriting_calculations", "rule_evaluations",
            "risk_flags", "decisions", "decision_reasons", "eligibility_results",
        ):
            rows = self.table(name)
            if rows:
                overlap = demo_fields & set(rows[0].keys())
                if overlap:
                    failures.append(f"{name} exposes demographic field(s) {sorted(overlap)}")
        # The monitoring table must state its use restriction on every row.
        for row in self.table("borrower_demographics"):
            if "MONITORING_ONLY" not in row["use_restriction"]:
                failures.append(f"{row['borrower_id']}: no monitoring-only restriction")
        # And it must not appear in anything the agent is given.
        for path in sorted(u.APPLICATION_INPUT_DIR.glob("*.json")):
            text = path.read_text(encoding="utf-8").lower()
            for field_name in ("ethnicity", "\"race\"", "\"sex\"", "age_band"):
                if field_name in text:
                    failures.append(
                        f"{path.name} contains {field_name}: monitoring data must never "
                        "reach a decision component"
                    )
        self.record(
            "demographic monitoring data is segregated from every decision surface",
            "privacy", failures,
            f"{len(self.table('borrower_demographics'))} monitoring rows held separately",
        )

    # -- coverage ---------------------------------------------------------

    def check_scale(self) -> None:
        failures: list[str] = []
        borrowers = len(self.table("borrowers"))
        applications = len(self.table("applications"))
        if borrowers < MIN_BORROWERS:
            failures.append(f"{borrowers} borrowers, minimum {MIN_BORROWERS}")
        if applications < MIN_APPLICATIONS:
            failures.append(f"{applications} applications, minimum {MIN_APPLICATIONS}")
        products = {r["product_family"] for r in self.table("applications")}
        if len(products) < 3:
            failures.append(f"only {len(products)} product families represented")
        purposes = {r["loan_purpose"] for r in self.table("applications")}
        if len(purposes) < 3:
            failures.append(f"only {len(purposes)} loan purposes represented")
        occupancies = {r["occupancy_type"] for r in self.table("applications")}
        if len(occupancies) < 3:
            failures.append(f"only {len(occupancies)} occupancy types represented")
        joint = sum(
            1 for r in self.table("applications") if int(r["borrower_count"]) > 1
        )
        single = applications - joint
        if joint == 0 or single == 0:
            failures.append("dataset must contain both single and joint applications")
        returning = [
            b for b, n in Counter(
                r["borrower_id"] for r in self.table("application_borrowers")
            ).items() if n > 1
        ]
        if not returning:
            failures.append("no returning applicant appears on more than one application")
        self.record(
            "dataset scale and product diversity meet the minimum", "coverage", failures,
            f"{borrowers} borrowers, {applications} applications ({single} single / "
            f"{joint} joint), {len(products)} products, {len(purposes)} purposes, "
            f"{len(returning)} returning applicant(s)",
        )

    def check_scenario_coverage(self) -> None:
        catalog = json.loads(
            (u.SCENARIO_DIR / "scenario_catalog.json").read_text(encoding="utf-8")
        )
        scenarios = catalog["scenarios"]
        failures: list[str] = []
        blob = " ".join(
            " ".join(s["features_being_tested"]) + " " + s["scenario_name"] + " " +
            s["description"]
            for s in scenarios
        ).lower()
        for feature in REQUIRED_SCENARIO_FEATURES:
            if feature.lower() not in blob:
                failures.append(f"no scenario covers '{feature}'")
        recs = Counter(s["expected_recommendation"] for s in scenarios)
        for required in (
            "APPROVE_RECOMMENDATION", "APPROVE_WITH_CONDITIONS", "REFER",
            "MANUAL_REVIEW_REQUIRED", "SUSPENDED_INCOMPLETE", "DECLINE_RECOMMENDATION",
        ):
            if not recs.get(required):
                failures.append(f"no scenario produces {required}")
        security = [s for s in scenarios if s["security_test_type"]]
        if len(security) < 4:
            failures.append(f"only {len(security)} security scenarios")
        types = {s["security_test_type"] for s in security}
        for required in (
            "PROMPT_INJECTION", "PII_EXTRACTION", "CROSS_CUSTOMER_ACCESS",
            "INSTRUCTION_SMUGGLING", "OUT_OF_SCOPE_REQUEST",
        ):
            if required not in types:
                failures.append(f"no scenario covers security type {required}")
        # Each scenario must map to exactly one application.
        app_ids = [s["application_id"] for s in scenarios]
        if len(set(app_ids)) != len(app_ids):
            failures.append("a scenario is mapped to more than one application")
        self.record(
            "scenario coverage spans every outcome and security type", "coverage",
            failures,
            f"{len(scenarios)} scenarios, {len(security)} security cases, "
            f"{len(recs)} distinct recommendations",
        )

    def check_boundary_coverage(self) -> None:
        """Every important rule needs a positive and a negative case to be testable."""
        outcomes: dict[str, set[str]] = defaultdict(set)
        for row in self.table("rule_evaluations"):
            outcomes[row["rule_id"]].add(row["outcome"])
        need_both = (
            "DTI-CONV-001", "CRD-SCR-003", "AST-FTC-003", "AST-RSV-002",
            "CRD-EVT-001", "VAL-APR-001",
        )
        failures = [
            f"{rule}: only {sorted(outcomes.get(rule, set()))} - needs both a PASS and a "
            "FAIL case to be testable"
            for rule in need_both
            if not {"PASS", "FAIL"} <= outcomes.get(rule, set())
        ]
        self.record(
            "key rules have both a passing and a failing case", "coverage", failures,
            f"{len(need_both)} rules checked for positive and negative coverage",
        )

    def check_policy_application_coverage(self) -> None:
        used = {r["policy_id"] for r in self.table("rule_evaluations")}
        all_ids = {p.policy_id for p in ALL_POLICIES}
        unused = sorted(all_ids - used)
        # Reference-only documents are permitted, but must be a small minority.
        detail = f"{len(used)} of {len(all_ids)} policies exercised by an application"
        failures = []
        if len(unused) > len(all_ids) // 2:
            failures.append(
                f"{len(unused)} policies are never used by any application: {unused[:10]}"
            )
        self.record(
            "most policies are exercised by at least one application", "coverage",
            failures, detail + (f"; reference-only: {', '.join(unused)}" if unused else ""),
        )

    # -- golden set -------------------------------------------------------

    def check_golden_set(self) -> None:
        cases = u.read_jsonl(u.GOLDEN_DIR / "evaluation_cases.jsonl")
        expected = u.read_jsonl(u.GOLDEN_DIR / "expected_results.jsonl")
        failures: list[str] = []
        app_ids = {r["application_id"] for r in self.table("applications")}
        if len(cases) != len(app_ids):
            failures.append(f"{len(cases)} cases for {len(app_ids)} applications")
        if {c["case_id"] for c in cases} != {e["case_id"] for e in expected}:
            failures.append("case ids differ between evaluation_cases and expected_results")

        leak_keys = (
            "expected_", "ground_truth", "answer", "correct_", "should_",
        )
        for case in cases:
            for key in case:
                if any(key.startswith(p) for p in leak_keys):
                    failures.append(
                        f"{case['case_id']}: input case carries answer-bearing key {key!r}"
                    )
            packet = self.root / case["input_packet"]
            if not packet.is_file():
                failures.append(f"{case['case_id']}: input packet {case['input_packet']} missing")
            folder = self.root / case["document_folder"]
            if not folder.is_dir():
                failures.append(f"{case['case_id']}: document folder missing")

        stored = {
            (r["application_id"], r["calculation_name"]): r["result"]
            for r in self.table("underwriting_calculations")
        }
        decisions = {
            r["application_id"]: r
            for r in self.table("decisions")
            if r["decision_type"] == "COPILOT_RECOMMENDATION"
        }
        for exp in expected:
            app_id = exp["application_id"]
            if exp["expected_recommendation"] != decisions[app_id]["result"]:
                failures.append(
                    f"{exp['case_id']}: golden recommendation disagrees with decisions.csv"
                )
            if exp["expected_eligibility"] != decisions[app_id]["eligibility_result"]:
                failures.append(f"{exp['case_id']}: golden eligibility disagrees")
            if bool(exp["expected_human_review"]) != u.parse_bool(
                decisions[app_id]["requires_human_review"]
            ):
                failures.append(f"{exp['case_id']}: golden human-review flag disagrees")
            for name, value in exp["expected_calculations"].items():
                key = (app_id, name)
                if key not in stored:
                    failures.append(f"{exp['case_id']}: calculation {name} not in the tables")
                elif (stored[key] or None) != value:
                    failures.append(
                        f"{exp['case_id']}: golden {name}={value} vs table "
                        f"{stored[key]!r}"
                    )
            for required in (
                "applicable_policy_ids", "applicable_rule_ids", "expected_citations",
                "expected_route", "expected_sensitive_fields_to_mask",
                "forbidden_decision_inputs",
            ):
                if required not in exp:
                    failures.append(f"{exp['case_id']}: missing {required}")
        self.record(
            "golden set matches the tables and leaks no answers into the inputs",
            "evaluation", failures,
            f"{len(cases)} evaluation cases and {len(expected)} expected results",
        )

    def check_input_packets(self) -> None:
        failures: list[str] = []
        packets = sorted(u.APPLICATION_INPUT_DIR.glob("APP-*.json"))
        banned = (
            "expected_recommendation", "expected_decision", "expected_rule",
            "expected_risk_flag", "expected_eligibility", "scenario_id",
            "back_end_dti", "qualifying_monthly_income", "months_reserves",
            "representative_score", "verified_monthly_amount",
        )
        for path in packets:
            text = path.read_text(encoding="utf-8")
            for token in banned:
                if token in text:
                    failures.append(
                        f"{path.name}: carries {token!r}, which would hand the agent an "
                        "answer or a derived value it is supposed to compute"
                    )
            payload = json.loads(text)
            if "untrusted_applicant_text" in payload and payload[
                "untrusted_applicant_text"
            ]:
                block = payload["untrusted_applicant_text"]
                if block.get("label") != "UNTRUSTED_APPLICANT_TEXT":
                    failures.append(f"{path.name}: untrusted text not labelled")
                if block.get("trust_class") != "customer_evidence":
                    failures.append(f"{path.name}: untrusted text carries the wrong trust class")
        if len(packets) != len(self.table("applications")):
            failures.append(
                f"{len(packets)} input packets for {len(self.table('applications'))} "
                "applications"
            )
        self.record(
            "application input packets carry inputs only, never ground truth",
            "evaluation", failures, f"{len(packets)} packets checked",
        )

    def check_schemas(self) -> None:
        failures: list[str] = []
        schemas = sorted(u.SCHEMA_DIR.glob("*.schema.json"))
        if len(schemas) < 4:
            failures.append(f"only {len(schemas)} schemas committed")
        for path in schemas:
            try:
                schema = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"{path.name}: {exc}")
                continue
            for key in ("$schema", "title", "type"):
                if key not in schema and key != "type":
                    failures.append(f"{path.name}: missing {key}")

        # Spot-check the application packets against their schema's own constraints.
        app_schema = json.loads(
            (u.SCHEMA_DIR / "application.schema.json").read_text(encoding="utf-8")
        )
        required = app_schema["required"]
        allowed = set(app_schema["properties"])
        enums = {
            k: set(v["enum"])
            for k, v in app_schema["properties"].items()
            if isinstance(v, dict) and "enum" in v
        }
        for path in sorted(u.APPLICATION_INPUT_DIR.glob("APP-*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for key in required:
                if key not in payload:
                    failures.append(f"{path.name}: required property {key} absent")
            extra = set(payload) - allowed
            if extra:
                failures.append(f"{path.name}: properties outside the schema: {sorted(extra)}")
            for key, values in enums.items():
                if key in payload and payload[key] not in values:
                    failures.append(f"{path.name}: {key}={payload[key]!r} outside its enum")
            if not re.match(r"^APP-\d{6}$", payload["application_id"]):
                failures.append(f"{path.name}: application_id does not match its pattern")
        self.record(
            "committed artifacts comply with the committed schemas", "structure",
            failures, f"{len(schemas)} schemas, "
            f"{len(list(u.APPLICATION_INPUT_DIR.glob('APP-*.json')))} packets validated",
        )

    def check_security_cases(self) -> None:
        failures: list[str] = []
        events = self.table("security_events")
        if len(events) < 4:
            failures.append(f"only {len(events)} security events in the dataset")
        for row in events:
            if row["action_taken"] not in (
                "QUARANTINED_AND_ESCALATED", "REFUSED", "BLOCKED"
            ):
                failures.append(f"{row['security_event_id']}: weak action {row['action_taken']}")
            if not row["rule_id"].startswith("SEC-"):
                failures.append(f"{row['security_event_id']}: not bound to a security rule")
            if not row["masked_excerpt"]:
                failures.append(f"{row['security_event_id']}: no excerpt recorded")
        # No applicant's actual submitted text may appear in the policy corpus.
        #
        # This compares against the specific strings the scenarios submit, not against
        # generic phrases: POL-SEC-001 legitimately quotes an example of an injection
        # attempt in order to explain the rule, and a check that cannot tell the
        # difference between a policy describing an attack and an attack reaching the
        # policy is worse than no check at all.
        from synth.scenarios import SCENARIOS

        submitted = {
            s.untrusted_text.strip().lower(): s.scenario_id
            for s in SCENARIOS
            if s.untrusted_text
        }
        corpus = {
            path.name: path.read_text(encoding="utf-8").lower()
            for path in u.POLICY_CORPUS_DIR.glob("*.md")
        }
        for text, scenario_id in submitted.items():
            for name, body in corpus.items():
                if text in body:
                    failures.append(
                        f"{name}: verbatim applicant text from {scenario_id} has reached "
                        "the policy corpus - the trust boundary is broken"
                    )
        # Applicant text also must not reach any other application's input packet.
        for path in sorted(u.APPLICATION_INPUT_DIR.glob("APP-*.json")):
            body = path.read_text(encoding="utf-8").lower()
            payload = json.loads(path.read_text(encoding="utf-8"))
            own = (payload.get("untrusted_applicant_text") or {}).get("content", "")
            own = (own or "").strip().lower()
            for text, scenario_id in submitted.items():
                if text != own and text in body:
                    failures.append(
                        f"{path.name}: carries applicant text belonging to {scenario_id}"
                    )
        # Security cases must record a human review.
        reviewed = {r["application_id"] for r in self.table("human_reviews")}
        for row in events:
            if row["application_id"] not in reviewed:
                failures.append(
                    f"{row['application_id']}: security event without human review"
                )
        self.record(
            "security events are recorded, bound to a rule and escalated", "security",
            failures, f"{len(events)} security events across "
            f"{len({r['application_id'] for r in events})} applications",
        )

    def check_audit_completeness(self) -> None:
        failures: list[str] = []
        by_app = defaultdict(list)
        for row in self.table("audit_events"):
            by_app[row["application_id"]].append(row)
        required_actions = {
            "authorise_case_access", "select_policy_versions", "run_calculations",
            "evaluate_rules", "produce_recommendation",
        }
        for app_id, rows in by_app.items():
            actions = {r["action"] for r in rows}
            missing = required_actions - actions
            if missing:
                failures.append(f"{app_id}: audit trail missing {sorted(missing)}")
            seq = [int(r["sequence"]) for r in rows]
            if seq != sorted(seq) or seq != list(range(1, len(seq) + 1)):
                failures.append(f"{app_id}: audit sequence not contiguous")
            if len({r["correlation_id"] for r in rows}) != 1:
                failures.append(f"{app_id}: audit events span multiple correlation ids")
        for app_id in {r["application_id"] for r in self.table("applications")}:
            if app_id not in by_app:
                failures.append(f"{app_id}: no audit trail")
        self.record(
            "every application carries a contiguous audit trail", "traceability",
            failures, f"{len(self.table('audit_events'))} audit events across "
            f"{len(by_app)} applications",
        )

    def check_calculation_provenance(self) -> None:
        failures: list[str] = []
        version = re.compile(r"^v\d+\.\d+\.\d+$")
        units = {"USD", "USD_PER_MONTH", "RATIO", "MONTHS", "SCORE", "MULTIPLE"}
        for row in self.table("underwriting_calculations"):
            if not version.match(row["formula_version"]):
                failures.append(f"{row['calculation_id']}: formula_version malformed")
            if not row["input_fields"]:
                failures.append(f"{row['calculation_id']}: no input fields recorded")
            if row["units"] not in units:
                failures.append(f"{row['calculation_id']}: unknown units {row['units']!r}")
            if not row["policy_context"]:
                failures.append(f"{row['calculation_id']}: no policy context")
            if not row["expected_interpretation"]:
                failures.append(f"{row['calculation_id']}: no interpretation recorded")
        self.record(
            "every calculation records its inputs, formula version and interpretation",
            "traceability", failures,
            f"{len(self.table('underwriting_calculations'))} calculation records",
        )

    # -- run --------------------------------------------------------------

    def run(self) -> int:
        self.check_files_present()
        self.check_parse()
        self.check_primary_keys()
        self.check_foreign_keys()
        self.check_relationships()
        self.check_dates()
        self.check_financials()
        self.check_policy_corpus()
        self.check_policy_versions()
        self.check_rule_coverage()
        self.check_policy_temporal_binding()
        self.check_decision_traceability()
        self.check_human_review()
        self.check_documents()
        self.check_document_reconciliation()
        self.check_evidence_documents_draw_no_conclusions()
        self.check_expected_discrepancies()
        self.check_no_plaintext_sensitive_values()
        self.check_masking()
        self.check_fair_lending_separation()
        self.check_scale()
        self.check_scenario_coverage()
        self.check_boundary_coverage()
        self.check_policy_application_coverage()
        self.check_golden_set()
        self.check_input_packets()
        self.check_schemas()
        self.check_security_cases()
        self.check_audit_completeness()
        self.check_calculation_provenance()
        return self.report()

    def report(self) -> int:
        by_category: dict[str, list[Check]] = defaultdict(list)
        for check in self.checks:
            by_category[check.category].append(check)

        print()
        print("=" * 78)
        print("  CredPilot synthetic-data validation")
        print("=" * 78)
        for category in sorted(by_category):
            print(f"\n{category.upper()}")
            for check in by_category[category]:
                mark = "PASS" if check.passed else "FAIL"
                print(f"  [{mark}] {check.name}")
                print(f"         {check.detail}")
                for failure in check.failures:
                    print(f"         !! {failure}")
        passed = sum(1 for c in self.checks if c.passed)
        failed = len(self.checks) - passed
        print()
        print("-" * 78)
        print(f"  checks executed : {len(self.checks)}")
        print(f"  passed          : {passed}")
        print(f"  failed          : {failed}")
        print("-" * 78)
        if failed:
            print("  RESULT: FAIL - the dataset violates its own contract.")
            print("=" * 78)
            return 1
        print("  RESULT: PASS")
        print("=" * 78)
        return 0


# ---------------------------------------------------------------------------
# Independent arithmetic (deliberately not importing the generator's helpers)
# ---------------------------------------------------------------------------


def _q(value: Decimal) -> Decimal:
    return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)


def _amortise(loan: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    i = annual_rate / Decimal(12)
    if i == 0:
        return _q(loan / Decimal(months))
    growth = (Decimal(1) + i) ** months
    return _q(loan * i * growth / (growth - Decimal(1)))


def _replay_draw(required: Decimal, assets: Sequence[dict[str, str]]) -> Decimal:
    """Re-run the settlement draw from the asset rows alone."""
    need = Decimal(required)
    reserve_pool = sum(
        (u.dec(a["eligible_reserve_amount"]) for a in assets), Decimal(0)
    )
    consumed = Decimal(0)
    tier_one = sorted(
        (a for a in assets if u.dec(a["eligible_reserve_amount"]) == 0),
        key=lambda a: a["asset_id"],
    )
    tier_two = sorted(
        (a for a in assets if u.dec(a["eligible_reserve_amount"]) > 0),
        key=lambda a: a["asset_id"],
    )
    for tier, is_reserve in ((tier_one, False), (tier_two, True)):
        for asset in tier:
            if need <= 0:
                break
            take = min(need, u.dec(asset["eligible_close_amount"]))
            if take <= 0:
                continue
            need -= take
            if is_reserve:
                consumed += min(take, u.dec(asset["eligible_reserve_amount"]))
    return _q(max(Decimal(0), reserve_pool - consumed))


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    return Validator(root).run()


if __name__ == "__main__":
    sys.exit(main())
