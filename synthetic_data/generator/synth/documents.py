"""
Applicant document corpus.

Each document is an original synthetic approximation carrying the *fields* an
underwriter needs. No proprietary or copyrighted form layout is reproduced.

Documents are rendered from the same structured values the tables carry, so a
cross-check between a paystub and the income table reconciles - except where the
scenario deliberately moves exactly one value, which is recorded in the scenario's
expected_discrepancies.

Sensitive identifiers appear only in masked form. A document never contains a
plaintext taxpayer identifier, account number or credit-file identifier, which is
what NFR-05 requires and what the repository's own leak scan enforces.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import synthetic_data_utils as u  # noqa: E402
from synthetic_data_utils import money  # noqa: E402

from .build import BuiltApplication  # noqa: E402

ZERO = Decimal("0")
LENDER = "Northwind Residential Lending (fictional)"

PERIODS_PER_YEAR = {"bi_weekly": 26, "semi_monthly": 24, "weekly": 52, "monthly": 12}


@dataclass
class Document:
    document_id: str
    application_id: str
    borrower_id: str | None
    document_type: str
    document_date: date
    received_date: date
    issuer_type: str
    source: str
    verification_status: str
    contains_pii: bool
    masked: bool
    tampering_indicator: bool
    trust_class: str
    filename: str
    body: str
    expected_extracted_fields: tuple[str, ...] = ()
    related_entities: tuple[str, ...] = ()
    contains_untrusted_text: bool = False
    is_stale: bool = False
    extractions: list[dict[str, Any]] = field(default_factory=list)


def _money(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return f"{Decimal(value):,.2f}"


def _pct(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return f"{Decimal(value) * 100:.2f}%"


class DocumentBuilder:
    """Renders the document set for one built application."""

    def __init__(self, seed: int) -> None:
        self.seed = seed

    def build(self, built: BuiltApplication) -> list[Document]:
        spec = built.scenario
        app_id = built.application["application_id"]
        as_of = built.application["underwriting_as_of_date"]
        primary = built.borrowers[0]
        docs: list[Document] = []
        seq = 0

        def new_id() -> str:
            nonlocal seq
            seq += 1
            return f"{app_id}-DOC-{seq:02d}"

        def want(doc_type: str) -> bool:
            return doc_type not in spec.missing_document_types

        def stale(doc_type: str) -> bool:
            return doc_type in spec.stale_document_types

        docs.append(self._application_summary(built, new_id(), as_of))
        docs.append(self._identity_summary(built, new_id(), as_of))
        docs.append(self._credit_summary(built, new_id(), as_of))

        employed = [e for e in built.employments if e["is_current"]]
        for emp in employed:
            person = next(
                (b for b in built.borrowers if b.borrower_id == emp["borrower_id"]),
                primary,
            )
            if emp["self_employed_flag"]:
                if want("profit_and_loss"):
                    docs.append(self._profit_and_loss(built, new_id(), emp, person, as_of))
                if want("tax_return"):
                    docs.append(self._tax_return(built, new_id(), emp, person, as_of))
            else:
                if want("paystub"):
                    docs.append(
                        self._paystub(
                            built, new_id(), emp, person, as_of, stale("paystub")
                        )
                    )
                if want("w2"):
                    docs.append(self._w2(built, new_id(), emp, person, as_of))
                if want("employment_verification"):
                    docs.append(
                        self._employment_verification(built, new_id(), emp, person, as_of)
                    )

        for asset in built.assets:
            if asset["asset_type"] in ("checking", "savings") and want("bank_statement"):
                docs.append(
                    self._bank_statement(
                        built, new_id(), asset, primary, as_of, stale("bank_statement")
                    )
                )
            if asset["asset_type"] in ("brokerage", "retirement") and want(
                "asset_verification"
            ):
                docs.append(
                    self._asset_verification(built, new_id(), asset, primary, as_of)
                )
            if asset["asset_type"] == "gift_funds" and want("gift_letter"):
                docs.append(self._gift_letter(built, new_id(), asset, primary, as_of))

        if built.application["loan_purpose"] == "purchase" and want("purchase_agreement"):
            docs.append(self._purchase_agreement(built, new_id(), as_of))
        else:
            if want("payoff_statement"):
                docs.append(self._payoff_statement(built, new_id(), as_of))

        if built.appraisal is not None:
            if want("appraisal_report"):
                docs.append(self._appraisal_report(built, new_id(), as_of))
        else:
            docs.append(self._value_acceptance(built, new_id(), as_of))

        if want("title_report"):
            docs.append(self._title_report(built, new_id(), as_of))
        if want("homeowner_insurance_evidence"):
            docs.append(self._hazard_evidence(built, new_id(), as_of))
        if spec.flood_zone_sfha and want("flood_insurance_evidence"):
            docs.append(self._flood_evidence(built, new_id(), as_of))

        if any("rental" in s["income_type"] for s in built.income_sources) or (
            spec.occupancy_contradiction
        ):
            docs.append(self._lease(built, new_id(), primary, as_of))

        if spec.untrusted_text:
            docs.append(self._untrusted_document(built, new_id(), primary, as_of))
        elif built.engine_result.conditions:
            docs.append(self._letter_of_explanation(built, new_id(), primary, as_of))

        if built.engine_result.conditions:
            docs.append(self._condition_response(built, new_id(), primary, as_of))

        return docs

    # -- individual documents ---------------------------------------------

    def _wrap(self, title: str, lines: list[str]) -> str:
        """Frame a document.

        The banner does not name the lender: an employer issues the paystub, a
        bureau issues the credit report and an appraiser issues the valuation.
        Attributing all of them to the lender would misrepresent who produced
        the evidence. What the banner does say, on every document, is that the
        record is synthetic.
        """
        head = [
            "=" * 74,
            f"  {title}",
            "  SYNTHETIC DOCUMENT - generated for CredPilot testing. Not a real record.",
            "  No real person, employer, institution or property is represented.",
            "=" * 74,
            "",
        ]
        return "\n".join(head + lines).rstrip() + "\n"

    def _application_summary(
        self, b: BuiltApplication, doc_id: str, as_of: date
    ) -> Document:
        app = b.application
        primary = b.borrowers[0]
        lines = [
            f"Application reference : {app['application_id']}",
            f"Application date      : {app['application_date']}",
            f"Loan purpose          : {app['loan_purpose']}",
            f"Product               : {app['product_family']}",
            f"Occupancy             : {app['occupancy_type']}",
            f"Household size        : {app['household_size']}",
            "",
            "-- Borrowers " + "-" * 60,
        ]
        for ab in b.application_borrowers:
            person = next(p for p in b.borrowers if p.borrower_id == ab["borrower_id"])
            lines += [
                f"  {ab['borrower_role'].upper()} ({person.borrower_id})",
                f"    Name              : {person.full_name}",
                f"    Date of birth     : {person.date_of_birth}",
                f"    Taxpayer ID       : {person.ssn_masked}  [masked]",
                f"    Contact           : {person.email} / {person.phone}",
                f"    Current address   : {person.street}, {person.city}, "
                f"{person.state} {person.postal_code}",
            ]
            if person.prior_street:
                lines.append(
                    f"    Previous address  : {person.prior_street}, {person.prior_city}, "
                    f"{person.prior_state} {person.prior_postal_code}"
                )
            lines.append(
                f"    Years at address  : {person.years_at_current_address}"
            )
            lines.append("")
        lines += [
            "-- Declared income " + "-" * 54,
        ]
        for src in b.income_sources:
            lines.append(
                f"  {src['income_type']:<20} declared monthly "
                f"{_money(src['declared_monthly_amount'])}"
            )
        lines += [
            "",
            "-- Requested loan " + "-" * 55,
            f"  Base loan amount     : {_money(b.loan['base_loan_amount'])}",
            f"  Note amount          : {_money(b.loan['note_amount'])}",
            f"  Term (months)        : {b.loan['term_months']}",
            f"  Interest rate        : {_pct(b.loan['interest_rate'])}",
            "",
            "-- Subject property " + "-" * 53,
            f"  Address              : {b.prop['street']}, {b.prop['city']}, "
            f"{b.prop['state']} {b.prop['postal_code']}",
            f"  Property type        : {b.prop['property_type']} "
            f"({b.prop['units']} unit(s))",
            f"  Purchase price       : {_money(b.prop['purchase_price'])}",
            f"  Occupancy intent     : {b.prop['occupancy_type']}",
            "",
            "-- Declared liabilities " + "-" * 49,
        ]
        for lia in b.liabilities:
            # An obligation the applicant did not declare is, by definition, absent
            # from the application they filled in. It appears on the credit report
            # instead, which is where the reconciliation has to find it.
            if lia["source"] == "credit_report_only":
                continue
            lines.append(
                f"  {lia['liability_type']:<24} balance {_money(lia['balance']):>14}  "
                f"monthly {_money(lia['monthly_payment']):>10}"
            )
        extractions = [
            _ex(doc_id, "application_id", app["application_id"], 1),
            _ex(doc_id, "loan_purpose", app["loan_purpose"], 1),
            _ex(doc_id, "requested_loan_amount", b.loan["base_loan_amount"], 1),
            _ex(doc_id, "occupancy_type", b.prop["occupancy_type"], 1),
            _ex(
                doc_id, "declared_monthly_income",
                sum((s["declared_monthly_amount"] for s in b.income_sources), ZERO), 1,
            ),
        ]
        return Document(
            document_id=doc_id,
            application_id=app["application_id"],
            borrower_id=primary.borrower_id,
            document_type="loan_application_summary",
            document_date=app["application_date"],
            received_date=app["application_date"],
            issuer_type="applicant",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="01_loan_application_summary.txt",
            body=self._wrap("UNIFORM LOAN APPLICATION SUMMARY", lines),
            expected_extracted_fields=(
                "application_id", "loan_purpose", "requested_loan_amount",
                "occupancy_type", "declared_monthly_income",
            ),
            related_entities=("applications", "loans", "properties", "income"),
            extractions=extractions,
        )

    def _identity_summary(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        primary = b.borrowers[0]
        ver = next(v for v in b.verifications if v["category"] == "identity")
        lines = [
            f"Subject               : {primary.full_name} ({primary.borrower_id})",
            f"Date of birth         : {primary.date_of_birth}",
            f"Taxpayer ID           : {primary.ssn_masked}  [masked]",
            f"Address on file       : {primary.street}, {primary.city}, "
            f"{primary.state} {primary.postal_code}",
            "Identification type   : State-issued driver licence (synthetic)",
            f"Identification number : {primary.credit_file_masked}  [masked]",
            "",
            f"Verification provider : {ver['provider']}",
            f"Verification date     : {ver['completed_date']}",
            f"Result                : {ver['result']}",
            "",
            "Elements checked      : name, date of birth, address, identification number",
        ]
        if ver["result"] != "VERIFIED":
            lines += [
                "",
                "One or more identity elements did not match across the sources "
                "consulted.",
            ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=primary.borrower_id,
            document_type="identity_verification_summary",
            document_date=ver["completed_date"],
            received_date=ver["completed_date"],
            issuer_type="third_party_provider",
            source="verification_service",
            verification_status=ver["result"],
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="02_identity_verification_summary.txt",
            body=self._wrap("IDENTITY VERIFICATION SUMMARY", lines),
            expected_extracted_fields=(
                "identity_verification_status", "verified_name", "verified_date_of_birth",
            ),
            related_entities=("verifications", "borrowers"),
            extractions=[
                _ex(doc_id, "identity_verification_status", ver["result"], 1),
                _ex(doc_id, "verified_name", primary.full_name, 1),
                _ex(doc_id, "verified_date_of_birth", primary.date_of_birth, 1),
            ],
        )

    def _credit_summary(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        lines: list[str] = []
        for prof in b.credit_profiles:
            person = next(
                p for p in b.borrowers if p.borrower_id == prof["borrower_id"]
            )
            lines += [
                f"-- {person.full_name} ({person.borrower_id}) " + "-" * 30,
                f"  Credit file reference : {prof['credit_file_masked']}  [masked]",
                f"  Report date           : {prof['report_date']}"
                f"   ({prof['report_age_days']} days old at the as-of date)",
                f"  Bureau / vendor       : {prof['bureau_vendor']}",
                f"  Score model           : {prof['score_model']}",
                f"  Scores returned       : {prof['score_1']}, {prof['score_2']}, "
                f"{prof['score_3']}",
                f"  Scoreable tradelines  : {prof['scoreable_tradelines']}",
                f"  Inquiries (90 days)   : {prof['recent_inquiries_90d']}",
                "",
            ]
        lines += ["-- Tradelines " + "-" * 58]
        for acct in b.credit_accounts:
            lines.append(
                f"  {acct['account_type']:<24} {acct['creditor']:<32} "
                f"balance {_money(acct['balance']):>13}"
            )
            lines.append(
                f"      limit {_money(acct['credit_limit']):>12}   "
                f"monthly {_money(acct['monthly_payment']):>10}   "
                f"opened {acct['opened_date']}   "
                f"late 30/60/90 in 24m: {acct['lates_30d_24m']}/"
                f"{acct['lates_60d_24m']}/{acct['lates_90d_24m']}"
            )
        if b.credit_events:
            lines += ["", "-- Significant derogatory events " + "-" * 40]
            for ev in b.credit_events:
                lines.append(
                    f"  {ev['event_type']:<24} anchor {ev['anchor_date']} "
                    f"({ev['anchor_basis']}), seasoned {ev['seasoning_months']} months"
                )
        app_score = b.derived["representative_credit_score"]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=b.borrowers[0].borrower_id,
            document_type="credit_report_summary",
            document_date=b.credit_profiles[0]["report_date"],
            received_date=b.credit_profiles[0]["report_date"],
            issuer_type="credit_bureau",
            source="third_party",
            verification_status="VERIFIED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="03_credit_report_summary.txt",
            body=self._wrap("TRI-MERGE CREDIT REPORT SUMMARY", lines),
            expected_extracted_fields=(
                "score_1", "score_2", "score_3", "report_date", "revolving_balance",
                "revolving_limit", "monthly_liability_payments",
            ),
            related_entities=("credit_profiles", "credit_accounts", "liabilities"),
            extractions=[
                _ex(doc_id, "score_1", b.credit_profiles[0]["score_1"], 1),
                _ex(doc_id, "score_2", b.credit_profiles[0]["score_2"], 1),
                _ex(doc_id, "score_3", b.credit_profiles[0]["score_3"], 1),
                _ex(doc_id, "report_date", b.credit_profiles[0]["report_date"], 1),
                _ex(doc_id, "recent_inquiries_90d",
                    b.credit_profiles[0]["recent_inquiries_90d"], 1),
            ],
        )
        _ = app_score

    def _paystub(
        self, b: BuiltApplication, doc_id: str, emp: dict[str, Any], person: Any,
        as_of: date, is_stale: bool,
    ) -> Document:
        spec = b.scenario
        src = _income_for(b, person.borrower_id)
        annual = money(src["verified_monthly_amount"] * 12)
        periods_per_year = PERIODS_PER_YEAR[emp["pay_frequency"]]
        gross_per_period = money(annual / periods_per_year)

        doc_date = as_of - timedelta(days=64 if is_stale else 11)
        elapsed = (doc_date - date(doc_date.year, 1, 1)).days
        periods_elapsed = max(1, elapsed // (365 // periods_per_year))
        ytd_gross = money(gross_per_period * periods_elapsed)
        if spec.ytd_reconciliation_variance:
            # The one controlled mismatch for this scenario.
            ytd_gross = money(
                ytd_gross * (Decimal(1) + spec.as_decimal("ytd_reconciliation_variance"))
            )

        federal = money(ytd_gross * Decimal("0.152"))
        fica = money(ytd_gross * Decimal("0.0765"))
        net_period = money(gross_per_period * Decimal("0.7415"))

        lines = [
            f"Employer              : {emp['employer_name']}",
            f"Employee              : {person.full_name} ({person.borrower_id})",
            f"Taxpayer ID           : {person.ssn_masked}  [masked]",
            f"Pay frequency         : {emp['pay_frequency']} "
            f"({periods_per_year} periods per year)",
            f"Pay period end        : {doc_date}",
            f"Periods elapsed (YTD) : {periods_elapsed}",
            "",
            "-- Current period " + "-" * 55,
            f"  Gross earnings      : {_money(gross_per_period)}",
            f"  Net pay             : {_money(net_period)}",
            "",
            "-- Year to date " + "-" * 57,
            f"  Gross earnings YTD  : {_money(ytd_gross)}",
            f"  Federal tax YTD     : {_money(federal)}",
            f"  Social contributions: {_money(fica)}",
            "",
            f"Annual salary rate    : {_money(annual)}",
        ]
        if spec.document_tampering:
            lines += [
                "",
                "-- Line item detail " + "-" * 53,
                f"  Base earnings YTD   : {_money(money(ytd_gross * Decimal('0.61')))}",
                f"  Overtime YTD        : {_money(money(ytd_gross * Decimal('0.14')))}",
                f"  Other YTD           : {_money(money(ytd_gross * Decimal('0.09')))}",
            ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="paystub",
            document_date=doc_date,
            received_date=doc_date + timedelta(days=2),
            issuer_type="employer",
            source="applicant_supplied",
            verification_status="QUARANTINED" if spec.document_tampering else "RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=spec.document_tampering,
            trust_class="customer_evidence",
            filename=f"10_paystub_{person.borrower_id}.txt",
            body=self._wrap("EARNINGS STATEMENT", lines),
            expected_extracted_fields=(
                "employer_name", "pay_period_end", "gross_per_period", "ytd_gross",
                "pay_frequency",
            ),
            related_entities=("employment", "income"),
            is_stale=is_stale,
            extractions=[
                _ex(doc_id, "employer_name", emp["employer_name"], 1),
                _ex(doc_id, "pay_period_end", doc_date, 1),
                _ex(doc_id, "gross_per_period", gross_per_period, 1),
                _ex(doc_id, "ytd_gross", ytd_gross, 1,
                    confidence="0.91" if spec.document_tampering else "0.98"),
                _ex(doc_id, "pay_frequency", emp["pay_frequency"], 1),
            ],
        )

    def _w2(
        self, b: BuiltApplication, doc_id: str, emp: dict[str, Any], person: Any,
        as_of: date,
    ) -> Document:
        src = _income_for(b, person.borrower_id)
        prior_year_wages = money(src["verified_monthly_amount"] * 12 * Decimal("0.965"))
        doc_date = date(as_of.year - 1, 12, 31)
        lines = [
            f"Tax year              : {as_of.year - 1}",
            f"Employer              : {emp['employer_name']}",
            f"Employee              : {person.full_name} ({person.borrower_id})",
            f"Taxpayer ID           : {person.ssn_masked}  [masked]",
            "",
            f"Wages, tips and other compensation : {_money(prior_year_wages)}",
            "Federal income tax withheld        : "
            f"{_money(money(prior_year_wages * Decimal('0.148')))}",
            f"Social contribution wages          : {_money(prior_year_wages)}",
            "",
            "This statement reports the prior tax year only.",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="w2",
            document_date=doc_date,
            received_date=as_of - timedelta(days=13),
            issuer_type="employer",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename=f"11_w2_{person.borrower_id}.txt",
            body=self._wrap("WAGE AND TAX STATEMENT (SYNTHETIC)", lines),
            expected_extracted_fields=("tax_year", "employer_name", "annual_wages"),
            related_entities=("employment", "income"),
            extractions=[
                _ex(doc_id, "tax_year", as_of.year - 1, 1),
                _ex(doc_id, "employer_name", emp["employer_name"], 1),
                _ex(doc_id, "annual_wages", prior_year_wages, 1),
            ],
        )

    def _employment_verification(
        self, b: BuiltApplication, doc_id: str, emp: dict[str, Any], person: Any,
        as_of: date,
    ) -> Document:
        spec = b.scenario
        lines = [
            f"Employer              : {emp['employer_name']}",
            f"Employee              : {person.full_name} ({person.borrower_id})",
            f"Position              : {emp['occupation']}",
            f"Employment status     : {'Current' if emp['is_current'] else 'Ended'}",
            f"Start date            : {emp['verified_start_date']}",
            f"Pay frequency         : {emp['pay_frequency']}",
            "",
            "Verification method   : written verification obtained directly from the "
            "employer",
            f"Verification date     : {as_of - timedelta(days=8)}",
        ]
        if spec.future_employment_months_ahead is not None:
            lines += [
                "",
                "This is a non-contingent written offer. Employment has not yet begun.",
                "Agreed start date     : "
                f"{u.add_months(as_of, spec.future_employment_months_ahead)}",
            ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="employment_verification",
            document_date=as_of - timedelta(days=8),
            received_date=as_of - timedelta(days=8),
            issuer_type="employer",
            source="third_party",
            verification_status=(
                "CONFLICT" if spec.employment_verification_conflict else "VERIFIED"
            ),
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename=f"12_employment_verification_{person.borrower_id}.txt",
            body=self._wrap("VERIFICATION OF EMPLOYMENT", lines),
            expected_extracted_fields=(
                "employer_name", "employment_start_date", "employment_status", "position",
            ),
            related_entities=("employment", "verifications"),
            extractions=[
                _ex(doc_id, "employer_name", emp["employer_name"], 1),
                _ex(doc_id, "employment_start_date", emp["verified_start_date"], 1),
                _ex(doc_id, "employment_status", "Current", 1),
                _ex(doc_id, "position", emp["occupation"], 1),
            ],
        )

    def _profit_and_loss(
        self, b: BuiltApplication, doc_id: str, emp: dict[str, Any], person: Any,
        as_of: date,
    ) -> Document:
        qualifying = _income_for(b, person.borrower_id)["verified_monthly_amount"]
        annual_cash_flow = money(qualifying * 12)
        revenue = money(annual_cash_flow * Decimal("3.4"))
        expenses = money(revenue - annual_cash_flow - money(annual_cash_flow * Decimal("0.18")))
        depreciation = money(annual_cash_flow * Decimal("0.18"))
        lines = [
            f"Business              : {emp['employer_name']}",
            f"Owner                 : {person.full_name} ({person.borrower_id})",
            f"Ownership             : {emp['business_ownership_pct']}%",
            f"Period                : 01 January {as_of.year} to {as_of}",
            "",
            f"  Gross receipts                 : {_money(revenue)}",
            f"  Operating expenses             : ({_money(expenses)})",
            f"  Depreciation (non-cash)        : ({_money(depreciation)})",
            "  Net profit                     : "
            f"{_money(money(revenue - expenses - depreciation))}",
            "",
            f"  Owner distributions taken      : {_money(annual_cash_flow)}",
            f"  Ownership                      : {emp['business_ownership_pct']}%",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="profit_and_loss",
            document_date=as_of - timedelta(days=5),
            received_date=as_of - timedelta(days=4),
            issuer_type="applicant_business",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="13_self_employment_profit_and_loss.txt",
            body=self._wrap("BUSINESS PROFIT AND LOSS STATEMENT", lines),
            expected_extracted_fields=(
                "gross_receipts", "net_profit", "depreciation_addback",
                "owner_cash_flow",
            ),
            related_entities=("employment", "income"),
            extractions=[
                _ex(doc_id, "gross_receipts", revenue, 1),
                _ex(doc_id, "net_profit", money(revenue - expenses - depreciation), 1),
                _ex(doc_id, "depreciation_addback", depreciation, 1),
                _ex(doc_id, "owner_cash_flow", annual_cash_flow, 1),
            ],
        )

    def _tax_return(
        self, b: BuiltApplication, doc_id: str, emp: dict[str, Any], person: Any,
        as_of: date,
    ) -> Document:
        qualifying = _income_for(b, person.borrower_id)["verified_monthly_amount"]
        prior = money(qualifying * 12 * Decimal("0.94"))
        lines = [
            f"Tax year              : {as_of.year - 1}",
            f"Filer                 : {person.full_name} ({person.borrower_id})",
            f"Taxpayer ID           : {person.ssn_masked}  [masked]",
            f"Filing status         : {person.marital_status}",
            "",
            f"  Business net profit            : {_money(prior)}",
            "  Depreciation claimed           : "
            f"{_money(money(prior * Decimal('0.19')))}",
            "  Adjusted gross income          : "
            f"{_money(money(prior * Decimal('1.04')))}",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="tax_return",
            document_date=date(as_of.year, 4, 15),
            received_date=as_of - timedelta(days=6),
            issuer_type="applicant",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="14_tax_return_summary.txt",
            body=self._wrap("PERSONAL TAX RETURN SUMMARY (SYNTHETIC)", lines),
            expected_extracted_fields=(
                "tax_year", "business_net_profit", "adjusted_gross_income",
            ),
            related_entities=("income", "employment"),
            extractions=[
                _ex(doc_id, "tax_year", as_of.year - 1, 1),
                _ex(doc_id, "business_net_profit", prior, 1),
            ],
        )

    def _bank_statement(
        self, b: BuiltApplication, doc_id: str, asset: dict[str, Any], person: Any,
        as_of: date, is_stale: bool,
    ) -> Document:
        spec = b.scenario
        doc_date = as_of - timedelta(days=75 if is_stale else 9)
        txns = [t for t in b.asset_transactions if t["asset_id"] == asset["asset_id"]]
        ending = asset["verified_balance"]
        opening = ending
        for t in txns:
            opening = money(
                opening + t["amount"] if t["transaction_type"] == "withdrawal"
                else opening - t["amount"]
            )
        lines = [
            f"Institution           : {asset['institution']}",
            f"Account holder        : {person.full_name} ({person.borrower_id})",
            f"Account type          : {asset['asset_type']}",
            f"Account number        : {asset['account_masked']}  [masked]",
            f"Statement period end  : {doc_date}",
            "",
            f"  Opening balance                : {_money(opening)}",
        ]
        for t in txns:
            sign = "-" if t["transaction_type"] == "withdrawal" else "+"
            lines.append(
                f"  {t['transaction_date']}  {sign}{_money(t['amount']):>13}  "
                f"{t['description']}"
            )
        lines += [
            f"  Closing balance                : {_money(ending)}",
        ]
        if spec.security_event_types and "INSTRUCTION_SMUGGLING" in spec.security_event_types:
            lines += [
                "",
                "-- Memo line " + "-" * 59,
                f"  {spec.untrusted_text}",
            ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="bank_statement",
            document_date=doc_date,
            received_date=doc_date + timedelta(days=2),
            issuer_type="financial_institution",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename=f"20_bank_statement_{asset['asset_id'].split('-')[-1]}.txt",
            body=self._wrap("DEPOSIT ACCOUNT STATEMENT", lines),
            expected_extracted_fields=(
                "institution", "account_masked", "closing_balance", "statement_period_end",
            ),
            related_entities=("assets", "asset_transactions"),
            contains_untrusted_text=bool(
                spec.untrusted_text
                and "INSTRUCTION_SMUGGLING" in spec.security_event_types
            ),
            is_stale=is_stale,
            extractions=[
                _ex(doc_id, "institution", asset["institution"], 1),
                _ex(doc_id, "account_masked", asset["account_masked"], 1),
                _ex(doc_id, "closing_balance", ending, 1),
                _ex(doc_id, "statement_period_end", doc_date, 1),
            ],
        )

    def _asset_verification(
        self, b: BuiltApplication, doc_id: str, asset: dict[str, Any], person: Any,
        as_of: date,
    ) -> Document:
        lines = [
            f"Custodian             : {asset['institution']}",
            f"Account holder        : {person.full_name} ({person.borrower_id})",
            f"Account type          : {asset['asset_type']}",
            f"Account number        : {asset['account_masked']}  [masked]",
            f"Valuation date        : {as_of - timedelta(days=7)}",
            "",
            f"  Current balance                : {_money(asset['verified_balance'])}",
            "",
        ]
        if asset["asset_type"] == "retirement":
            lines += [
                "The plan does not permit withdrawal or a participant loan for the "
                "purpose stated in the request.",
            ]
        else:
            lines += [
                "Holdings are publicly traded securities valued at the market close on "
                "the valuation date.",
            ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="asset_verification",
            document_date=as_of - timedelta(days=7),
            received_date=as_of - timedelta(days=6),
            issuer_type="financial_institution",
            source="third_party",
            verification_status="VERIFIED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename=f"21_asset_verification_{asset['asset_id'].split('-')[-1]}.txt",
            body=self._wrap("VERIFICATION OF ASSETS", lines),
            expected_extracted_fields=("verified_balance", "asset_type", "institution"),
            related_entities=("assets",),
            extractions=[
                _ex(doc_id, "verified_balance", asset["verified_balance"], 1),
                _ex(doc_id, "asset_type", asset["asset_type"], 1),
            ],
        )

    def _gift_letter(
        self, b: BuiltApplication, doc_id: str, asset: dict[str, Any], person: Any,
        as_of: date,
    ) -> Document:
        spec = b.scenario
        documented = spec.gift_documented
        lines = [
            f"Recipient             : {person.full_name} ({person.borrower_id})",
            f"Donor                 : R. {person.last_name} (parent)",
            "Relationship          : Parent of the recipient",
            f"Gift amount           : {_money(asset['verified_balance'])}",
            f"Date of transfer      : {as_of - timedelta(days=14)}",
            f"Receiving account     : {asset['account_masked']}  [masked]",
            "",
            "The donor certifies that the sum above is a gift, that no repayment is",
            "expected or implied, and that the donor has no interest in the property or",
            "the transaction.",
            "",
            f"Donor signature       : [signed] {as_of - timedelta(days=15)}",
            f"Recipient signature   : [signed] {as_of - timedelta(days=15)}",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="gift_letter",
            document_date=as_of - timedelta(days=15),
            received_date=as_of - timedelta(days=13),
            issuer_type="donor",
            source="applicant_supplied",
            verification_status="RECEIVED" if documented else "OUTSTANDING",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="22_gift_letter.txt",
            body=self._wrap("GIFT LETTER", lines),
            expected_extracted_fields=(
                "gift_amount", "donor_relationship", "no_repayment_statement",
            ),
            related_entities=("assets",),
            extractions=[
                _ex(doc_id, "gift_amount", asset["verified_balance"], 1),
                _ex(doc_id, "donor_relationship", "parent", 1),
                _ex(doc_id, "no_repayment_statement", "true", 1),
            ],
        )

    def _purchase_agreement(
        self, b: BuiltApplication, doc_id: str, as_of: date
    ) -> Document:
        loan = b.loan
        prop = b.prop
        lines = [
            f"Property              : {prop['street']}, {prop['city']}, "
            f"{prop['state']} {prop['postal_code']}",
            f"Purchaser             : {b.borrowers[0].full_name}",
            "Seller                : M. Ashgrove (synthetic counterparty)",
            f"Contract date         : {as_of - timedelta(days=26)}",
            f"Expected closing      : {as_of + timedelta(days=21)}",
            "",
            f"  Purchase price                 : {_money(prop['purchase_price'])}",
            f"  Earnest money deposit          : {_money(loan['earnest_money_paid'])}",
            f"  Seller credit to costs         : {_money(loan['seller_credits'])}",
            "  Financing contingency          : yes",
            "  Appraisal contingency          : yes",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=b.borrowers[0].borrower_id,
            document_type="purchase_agreement",
            document_date=as_of - timedelta(days=26),
            received_date=as_of - timedelta(days=24),
            issuer_type="settlement_parties",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="30_purchase_agreement.txt",
            body=self._wrap("RESIDENTIAL PURCHASE AGREEMENT SUMMARY", lines),
            expected_extracted_fields=(
                "purchase_price", "contract_date", "earnest_money", "seller_credits",
            ),
            related_entities=("properties", "loans"),
            extractions=[
                _ex(doc_id, "purchase_price", prop["purchase_price"], 1),
                _ex(doc_id, "contract_date", as_of - timedelta(days=26), 1),
                _ex(doc_id, "earnest_money", loan["earnest_money_paid"], 1),
                _ex(doc_id, "seller_credits", loan["seller_credits"], 1),
            ],
        )

    def _payoff_statement(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        lines = [
            "Servicer              : Sablefield Mortgage Servicing",
            f"Borrower              : {b.borrowers[0].full_name}",
            f"Property              : {b.prop['street']}, {b.prop['city']}, "
            f"{b.prop['state']}",
            f"Statement date        : {as_of - timedelta(days=4)}",
            f"Good through          : {as_of + timedelta(days=26)}",
            "",
            f"  Unpaid principal balance       : {_money(b.loan['payoff_amount'])}",
            f"  Total payoff                   : {_money(b.loan['payoff_amount'])}",
            "",
            "Ownership since       : "
            f"{u.add_months(as_of, -(b.prop['ownership_months'] or 0))}"
            f"  ({b.prop['ownership_months']} months)",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=b.borrowers[0].borrower_id,
            document_type="payoff_statement",
            document_date=as_of - timedelta(days=4),
            received_date=as_of - timedelta(days=3),
            issuer_type="servicer",
            source="third_party",
            verification_status="VERIFIED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="31_payoff_statement.txt",
            body=self._wrap("MORTGAGE PAYOFF STATEMENT", lines),
            expected_extracted_fields=("payoff_amount", "ownership_start_date"),
            related_entities=("loans", "properties"),
            extractions=[
                _ex(doc_id, "payoff_amount", b.loan["payoff_amount"], 1),
                _ex(doc_id, "ownership_months", b.prop["ownership_months"], 1),
            ],
        )

    def _appraisal_report(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        apr = b.appraisal
        prop = b.prop
        lines = [
            f"Subject property      : {prop['street']}, {prop['city']}, "
            f"{prop['state']} {prop['postal_code']}",
            f"Property type         : {prop['property_type']} ({prop['units']} unit(s))",
            f"Effective date        : {apr['appraisal_date']}",
            f"Valuation method      : {apr['valuation_method']}",
            f"Appraiser licence     : {apr['appraiser_licence']}  [synthetic]",
            f"Dataset version       : {apr['dataset_version']}",
            "",
            f"  Opinion of value               : {_money(apr['appraised_value'])}",
            f"  Contract price                 : {_money(prop['purchase_price'])}",
            f"  Condition rating               : {apr['condition_rating']}",
            "",
            "-- Comparable sales (synthetic) " + "-" * 41,
            "  Comparable 1                   : "
            f"{_money(money(apr['appraised_value'] * Decimal('0.97')))}",
            "  Comparable 2                   : "
            f"{_money(money(apr['appraised_value'] * Decimal('1.02')))}",
            "  Comparable 3                   : "
            f"{_money(money(apr['appraised_value'] * Decimal('0.995')))}",
        ]
        if apr["condition_finding"]:
            lines += [
                "",
                "Observed condition    : deferred maintenance affecting habitability was",
                "observed at the subject property. Items noted: roof covering at end of",
                "serviceable life; exterior stair handrail absent; furnace non-operational",
                "at time of inspection.",
            ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=None,
            document_type="appraisal_report",
            document_date=apr["appraisal_date"],
            received_date=apr["appraisal_date"] + timedelta(days=3),
            issuer_type="appraiser",
            source="third_party",
            verification_status="VERIFIED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="40_appraisal_report.txt",
            body=self._wrap("UNIFORM RESIDENTIAL APPRAISAL SUMMARY (SYNTHETIC)", lines),
            expected_extracted_fields=(
                "appraised_value", "effective_date", "condition_rating", "property_type",
            ),
            related_entities=("appraisals", "properties"),
            extractions=[
                _ex(doc_id, "appraised_value", apr["appraised_value"], 1),
                _ex(doc_id, "effective_date", apr["appraisal_date"], 1),
                _ex(doc_id, "condition_rating", apr["condition_rating"], 1),
            ],
        )

    def _value_acceptance(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        prop = b.prop
        lines = [
            f"Subject property      : {prop['street']}, {prop['city']}, {prop['state']}",
            f"Offer date            : {as_of - timedelta(days=b.scenario.valuation_age_days)}",
            f"Accepted value        : {_money(prop['appraised_value'])}",
            "Valuation method      : value_acceptance",
            "",
            "The automated underwriting system returned a value acceptance offer for",
            "this transaction. The offer expires with the casefile that issued it.",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=None,
            document_type="value_acceptance_record",
            document_date=as_of - timedelta(days=b.scenario.valuation_age_days),
            received_date=as_of - timedelta(days=b.scenario.valuation_age_days),
            issuer_type="automated_underwriting_system",
            source="third_party",
            verification_status="VERIFIED",
            contains_pii=False,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="40_value_acceptance_record.txt",
            body=self._wrap("VALUE ACCEPTANCE OFFER RECORD", lines),
            expected_extracted_fields=("accepted_value", "valuation_method"),
            related_entities=("properties",),
            extractions=[
                _ex(doc_id, "accepted_value", prop["appraised_value"], 1),
                _ex(doc_id, "valuation_method", "value_acceptance", 1),
            ],
        )

    def _title_report(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        ttl = b.title_records[0]
        lines = [
            f"Property              : {b.prop['street']}, {b.prop['city']}, "
            f"{b.prop['state']}",
            f"Commitment date       : {ttl['commitment_date']}",
            f"Required lien position: {ttl['required_lien_position']}",
            f"Vesting matches note  : {'yes' if ttl['vesting_matches_borrowers'] else 'no'}",
            f"Exceptions recorded   : {ttl['exception_count']}",
            "",
            f"  Exception detail               : {ttl['exception_summary']}",
        ]
        if ttl["blocking_exception"]:
            lines += [
                "",
                "The exception recorded above is a recorded judgment that would take",
                "priority over a new lien if not satisfied or subordinated before",
                "recording.",
            ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=None,
            document_type="title_report",
            document_date=ttl["commitment_date"],
            received_date=ttl["commitment_date"],
            issuer_type="title_provider",
            source="third_party",
            verification_status="VERIFIED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="41_title_report.txt",
            body=self._wrap("TITLE COMMITMENT SUMMARY", lines),
            expected_extracted_fields=("lien_position", "exception_count", "vesting"),
            related_entities=("title_records", "properties"),
            extractions=[
                _ex(doc_id, "lien_position", ttl["required_lien_position"], 1),
                _ex(doc_id, "exception_count", ttl["exception_count"], 1),
            ],
        )

    def _hazard_evidence(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        ins = next(i for i in b.insurance_records if i["coverage_type"] == "hazard")
        lines = [
            f"Carrier               : {ins['carrier']}",
            f"Insured               : {b.borrowers[0].full_name}",
            f"Property              : {b.prop['street']}, {b.prop['city']}, "
            f"{b.prop['state']}",
            f"Coverage amount       : {_money(ins['coverage_amount'])}",
            f"Annual premium        : {_money(ins['annual_premium'])}",
            f"Monthly escrow        : {_money(money(ins['annual_premium'] / 12))}",
            f"Effective date        : {ins['effective_date']}",
            f"Mortgagee clause      : {LENDER}, its successors and assigns",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=b.borrowers[0].borrower_id,
            document_type="homeowner_insurance_evidence",
            document_date=as_of - timedelta(days=3),
            received_date=as_of - timedelta(days=2),
            issuer_type="insurer",
            source="third_party",
            verification_status="VERIFIED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="42_homeowner_insurance_evidence.txt",
            body=self._wrap("EVIDENCE OF PROPERTY INSURANCE", lines),
            expected_extracted_fields=(
                "coverage_amount", "annual_premium", "effective_date",
            ),
            related_entities=("insurance_records", "properties"),
            extractions=[
                _ex(doc_id, "coverage_amount", ins["coverage_amount"], 1),
                _ex(doc_id, "annual_premium", ins["annual_premium"], 1),
                _ex(doc_id, "effective_date", ins["effective_date"], 1),
            ],
        )

    def _flood_evidence(self, b: BuiltApplication, doc_id: str, as_of: date) -> Document:
        ins = next(i for i in b.insurance_records if i["coverage_type"] == "flood")
        lines = [
            f"Flood zone determination : {b.prop['flood_zone']} "
            "(special flood hazard area: "
            f"{'yes' if b.prop['flood_zone_sfha'] else 'no'})",
            f"Determination date       : {as_of - timedelta(days=11)}",
            "",
            f"Carrier                  : {ins['carrier']}",
            f"Coverage amount          : {_money(ins['coverage_amount'])}",
            f"Annual premium           : {_money(ins['annual_premium'])}",
            f"Effective date           : {ins['effective_date']}",
            f"Evidence on file         : {'yes' if ins['evidenced'] else 'NO - OUTSTANDING'}",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=None,
            document_type="flood_insurance_evidence",
            document_date=as_of - timedelta(days=11),
            received_date=as_of - timedelta(days=10),
            issuer_type="insurer",
            source="third_party",
            verification_status="VERIFIED" if ins["evidenced"] else "OUTSTANDING",
            contains_pii=False,
            masked=True,
            tampering_indicator=False,
            trust_class="authoritative_evidence",
            filename="43_flood_insurance_evidence.txt",
            body=self._wrap("FLOOD DETERMINATION AND COVERAGE EVIDENCE", lines),
            expected_extracted_fields=("flood_zone", "coverage_amount", "effective_date"),
            related_entities=("insurance_records", "properties"),
            extractions=[
                _ex(doc_id, "flood_zone", b.prop["flood_zone"], 1),
                _ex(doc_id, "coverage_amount", ins["coverage_amount"], 1),
            ],
        )

    def _lease(
        self, b: BuiltApplication, doc_id: str, person: Any, as_of: date
    ) -> Document:
        spec = b.scenario
        rental = next(
            (s for s in b.income_sources if "rental" in s["income_type"]), None
        )
        gross_rent = (
            money(abs(rental["verified_monthly_amount"]) * Decimal("2.1"))
            if rental
            else money(Decimal("2150"))
        )
        subject = spec.occupancy_contradiction
        lines = [
            "Premises              : "
            + (
                f"{b.prop['street']}, {b.prop['city']}, {b.prop['state']}  "
                "[THE SUBJECT PROPERTY]"
                if subject
                else f"4120 Halloway Street, {person.city}, {person.state}"
            ),
            f"Landlord              : {person.full_name} ({person.borrower_id})",
            "Tenant                : J. Rennard (synthetic counterparty)",
            f"Term                  : 12 months from {as_of - timedelta(days=95)}",
            f"Monthly rent          : {_money(gross_rent)}",
            "Tenancy status        : occupied by the tenant named above",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="lease_agreement",
            document_date=as_of - timedelta(days=95),
            received_date=as_of - timedelta(days=10),
            issuer_type="applicant",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="50_lease_agreement.txt",
            body=self._wrap("RESIDENTIAL LEASE SUMMARY", lines),
            expected_extracted_fields=("monthly_rent", "premises_address", "lease_term"),
            related_entities=("income", "properties"),
            extractions=[
                _ex(doc_id, "monthly_rent", gross_rent, 1),
                _ex(doc_id, "lease_term_months", 12, 1),
            ],
        )

    def _untrusted_document(
        self, b: BuiltApplication, doc_id: str, person: Any, as_of: date
    ) -> Document:
        spec = b.scenario
        event = spec.security_event_types[0] if spec.security_event_types else "UNKNOWN"
        if event == "INSTRUCTION_SMUGGLING":
            # Already carried inside the bank statement; this records the message.
            heading = "APPLICANT MESSAGE"
        else:
            heading = "APPLICANT LETTER OF EXPLANATION"
        lines = [
            f"From                  : {person.full_name} ({person.borrower_id})",
            f"Received              : {as_of - timedelta(days=5)}",
            "Channel               : applicant portal",
            "Trust class           : customer_evidence  [UNTRUSTED_APPLICANT_TEXT]",
            "",
            "-- Applicant text, reproduced verbatim as data " + "-" * 26,
            "",
            f"  {spec.untrusted_text}",
        ]
        _ = event
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="letter_of_explanation",
            document_date=as_of - timedelta(days=5),
            received_date=as_of - timedelta(days=5),
            issuer_type="applicant",
            source="applicant_supplied",
            verification_status="QUARANTINED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="60_applicant_untrusted_text.txt",
            body=self._wrap(heading, lines),
            expected_extracted_fields=("applicant_statement", "security_event_type"),
            related_entities=("security_events",),
            contains_untrusted_text=True,
            extractions=[
                _ex(doc_id, "security_event_type", event, 1),
                _ex(doc_id, "quarantined", "true", 1),
            ],
        )

    def _letter_of_explanation(
        self, b: BuiltApplication, doc_id: str, person: Any, as_of: date
    ) -> Document:
        cond = b.engine_result.conditions[0]
        lines = [
            f"From                  : {person.full_name} ({person.borrower_id})",
            f"Date                  : {as_of - timedelta(days=3)}",
            f"Subject               : {cond['category'].lower()} documentation",
            "Trust class           : customer_evidence",
            "",
            "I am writing in response to the item raised on my application:",
            "",
            f"  \"{cond['text']}\"",
            "",
            "I have provided what I have available and will supply the remaining",
            "documentation as soon as I can obtain it from the issuer.",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="letter_of_explanation",
            document_date=as_of - timedelta(days=3),
            received_date=as_of - timedelta(days=3),
            issuer_type="applicant",
            source="applicant_supplied",
            verification_status="RECEIVED",
            contains_pii=True,
            masked=True,
            tampering_indicator=False,
            trust_class="customer_evidence",
            filename="60_letter_of_explanation.txt",
            body=self._wrap("LETTER OF EXPLANATION", lines),
            expected_extracted_fields=("applicant_statement",),
            related_entities=("conditions",),
            extractions=[_ex(doc_id, "applicant_statement", "provided", 1)],
        )

    def _condition_response(
        self, b: BuiltApplication, doc_id: str, person: Any, as_of: date
    ) -> Document:
        lines = [
            f"Application           : {b.application['application_id']}",
            f"Prepared              : {as_of}",
            f"Open conditions       : {len(b.engine_result.conditions)}",
            "",
            "-- Outstanding items " + "-" * 52,
        ]
        for idx, cond in enumerate(b.engine_result.conditions, 1):
            lines += [
                f"  {idx}. [{cond['category']}] {cond['text']}",
                f"     Required evidence : {cond['required_evidence']}",
                f"     Raised by rule    : {cond['rule_id']}",
                f"     Timing            : {cond['timing']}",
                f"     Status            : {cond['status']}",
                "",
            ]
        lines += [
            "UWR-CND-001: a condition moves to CLEARED only when the evidence is",
            "received and accepted, or to WAIVED only under an approved exception.",
            "Clearing a condition can introduce new information, which requires the",
            "affected calculations and rules to be re-run.",
        ]
        return Document(
            document_id=doc_id,
            application_id=b.application["application_id"],
            borrower_id=person.borrower_id,
            document_type="condition_response",
            document_date=as_of,
            received_date=as_of,
            issuer_type="lender",
            source="internal",
            verification_status="OPEN",
            contains_pii=False,
            masked=True,
            tampering_indicator=False,
            trust_class="internal_record",
            filename="70_condition_register.txt",
            body=self._wrap("CONDITION REGISTER", lines),
            expected_extracted_fields=("open_condition_count", "condition_rule_ids"),
            related_entities=("conditions",),
            extractions=[
                _ex(doc_id, "open_condition_count", len(b.engine_result.conditions), 1)
            ],
        )


def _income_for(b: BuiltApplication, borrower_id: str) -> dict[str, Any]:
    """The wage-type income row belonging to this borrower.

    A document must render that borrower's own earnings; using the application's
    first income row would put the primary borrower's salary on the co-borrower's
    paystub, which is exactly the kind of inconsistency this dataset exists to let
    a system detect.
    """
    wage_types = ("salaried", "hourly_variable", "self_employed", "commission")
    own = [s for s in b.income_sources if s["borrower_id"] == borrower_id]
    for src in own:
        if src["income_type"] in wage_types:
            return src
    if own:
        return own[0]
    return b.income_sources[0]


def _ex(
    doc_id: str, field_name: str, value: Any, page: int, confidence: str = "0.98"
) -> dict[str, Any]:
    return {
        "document_id": doc_id,
        "field_name": field_name,
        "extracted_value": value,
        "page": page,
        "extraction_confidence": confidence,
    }
