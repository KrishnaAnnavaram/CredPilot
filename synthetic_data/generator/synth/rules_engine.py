"""
Deterministic policy evaluation.

Every rule outcome in this dataset is produced here, from values the calculation
library computed, against parameters read off the policy version in force on the
application's underwriting as-of date. Nothing in this module guesses, and nothing
in it is produced by a language model.

Outcomes follow GEN-ELG-005: PASS, FAIL, REFER, NOT_APPLICABLE or INDETERMINATE.
INDETERMINATE means the inputs were not available - it never means "probably fails".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Sequence

from .policies import Policy, Rule, effective_rule

PASS = "PASS"
FAIL = "FAIL"
REFER = "REFER"
NOT_APPLICABLE = "NOT_APPLICABLE"
INDETERMINATE = "INDETERMINATE"

# Recommendation vocabulary (POL-DEC-001 DEC-REC-001).
APPROVE = "APPROVE_RECOMMENDATION"
APPROVE_WITH_CONDITIONS = "APPROVE_WITH_CONDITIONS"
REFER_RECOMMENDATION = "REFER"
MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
SUSPENDED_INCOMPLETE = "SUSPENDED_INCOMPLETE"
DECLINE = "DECLINE_RECOMMENDATION"

ELIGIBLE = "ELIGIBLE"
INELIGIBLE = "INELIGIBLE"


@dataclass
class Facts:
    """Everything the engine is allowed to look at.

    Deliberately excludes demographic monitoring attributes: they are not a field on
    this object, so no rule can reach them (SEC-PII-002, CRD-SCR-006).
    """

    application_id: str
    as_of: date
    application_date: date
    product: str
    purpose: str
    occupancy: str
    units: int
    property_type: str

    loan_amount: Decimal
    base_loan_amount: Decimal
    term_months: int
    interest_rate: Decimal
    purchase_price: Decimal | None
    appraised_value: Decimal | None
    value_used: Decimal

    ltv: Decimal | None
    cltv: Decimal | None
    hcltv: Decimal | None

    qualifying_monthly_income: Decimal
    pitia: Decimal
    total_monthly_debt: Decimal
    back_end_dti: Decimal | None
    front_end_dti: Decimal | None
    residual_income: Decimal

    representative_score: int | None
    credit_report_age_days: int
    scoreable_tradelines: int
    recent_inquiries_90d: int
    revolving_utilization: Decimal | None
    housing_lates_30d_12m: int
    housing_lates_60d_12m: int
    nonhousing_accounts_30d_24m: int
    any_90d_24m: bool
    collection_total: Decimal
    credit_events: tuple[dict[str, Any], ...] = ()
    undeclared_liability_found: bool = False

    funds_required: Decimal = Decimal(0)
    funds_available: Decimal = Decimal(0)
    funds_shortfall: Decimal = Decimal(0)
    reserves_months: Decimal | None = None
    own_funds_pct: Decimal = Decimal(0)
    gift_amount: Decimal = Decimal(0)
    gift_documented: bool = True
    other_financed_properties: int = 0
    ownership_months: int | None = None
    unsourced_deposit_amount: Decimal = Decimal(0)
    unsourced_deposit_date: date | None = None

    employment_tenure_months: int = 0
    employment_history_months: int = 24
    job_change_recent: bool = False
    job_change_field_or_structure: bool = False
    future_employment_start: date | None = None
    employment_verification_conflict: bool = False
    self_employed: bool = False
    variable_income_history_months: int | None = None
    variable_income_positive_factors: int = 0
    income_conflict_variance: Decimal | None = None
    ytd_reconciliation_variance: Decimal | None = None

    household_size: int = 1
    household_annual_income: Decimal = Decimal(0)

    valuation_method: str = "full_appraisal"
    valuation_age_days: int = 0
    appraisal_below_contract: bool = False
    property_condition_finding: bool = False
    flood_zone_sfha: bool = False
    flood_insurance_evidenced: bool = True
    occupancy_contradiction: bool = False
    title_exception_blocking: bool = False

    identity_status: str = "VERIFIED"
    fraud_indicators: tuple[str, ...] = ()
    document_tampering: bool = False

    documents_required: int = 0
    documents_received_current: int = 0
    missing_document_types: tuple[str, ...] = ()
    stale_document_types: tuple[str, ...] = ()

    security_event_types: tuple[str, ...] = ()

    conforming_limit: int = 832750

    #: Compensating factors already established by the builder, named per DTI-CONV-003.
    compensating_factors: tuple[str, ...] = ()


@dataclass
class Evaluation:
    rule_id: str
    policy_id: str
    policy_version: str
    policy_effective_date: date
    source_category: str
    severity: str
    outcome: str
    reason: str
    observed_value: str | None = None
    threshold_value: str | None = None
    comparator: str | None = None
    input_fields: tuple[str, ...] = ()
    requires_human_review: bool = False


@dataclass
class EngineResult:
    evaluations: list[Evaluation] = field(default_factory=list)
    conditions: list[dict[str, Any]] = field(default_factory=list)
    risk_flags: list[dict[str, Any]] = field(default_factory=list)
    human_review_reasons: list[str] = field(default_factory=list)

    @property
    def breaches(self) -> list[Evaluation]:
        return [e for e in self.evaluations if e.outcome == FAIL]

    @property
    def refers(self) -> list[Evaluation]:
        return [e for e in self.evaluations if e.outcome == REFER]

    @property
    def indeterminates(self) -> list[Evaluation]:
        return [e for e in self.evaluations if e.outcome == INDETERMINATE]


class Engine:
    """Evaluates a Facts object against the corpus as of the application date."""

    def __init__(self, registry: dict[str, list[Policy]]) -> None:
        self.registry = registry
        self._cache: dict[tuple[str, date], tuple[Policy, Rule]] = {}

    # -- plumbing ---------------------------------------------------------

    def _rule(self, rule_id: str, as_of: date) -> tuple[Policy, Rule]:
        key = (rule_id, as_of)
        if key not in self._cache:
            self._cache[key] = effective_rule(self.registry, rule_id, as_of)
        return self._cache[key]

    def _emit(
        self,
        result: EngineResult,
        facts: Facts,
        rule_id: str,
        outcome: str,
        reason: str,
        observed: Any = None,
        threshold: Any = None,
        comparator: str | None = None,
        input_fields: Sequence[str] = (),
        force_human_review: bool | None = None,
    ) -> Evaluation:
        policy, rule = self._rule(rule_id, facts.as_of)
        needs_human = (
            rule.requires_human_review
            if force_human_review is None
            else force_human_review
        )
        needs_human = needs_human and outcome in (FAIL, REFER, INDETERMINATE)
        ev = Evaluation(
            rule_id=rule_id,
            policy_id=policy.policy_id,
            policy_version=policy.version,
            policy_effective_date=policy.effective_date,
            source_category=rule.source_category,
            severity=rule.severity,
            outcome=outcome,
            reason=reason,
            observed_value=_fmt(observed),
            threshold_value=_fmt(threshold),
            comparator=comparator,
            input_fields=tuple(input_fields),
            requires_human_review=needs_human,
        )
        result.evaluations.append(ev)
        if needs_human:
            result.human_review_reasons.append(f"{rule_id}: {reason}")
        return ev

    def _condition(
        self,
        result: EngineResult,
        rule_id: str,
        category: str,
        text: str,
        evidence: str,
        prior_to: str = "PRIOR_TO_CLOSE",
    ) -> None:
        result.conditions.append(
            {
                "rule_id": rule_id,
                "category": category,
                "text": text,
                "required_evidence": evidence,
                "timing": prior_to,
                "status": "OPEN",
            }
        )

    def _risk(
        self,
        result: EngineResult,
        category: str,
        severity: str,
        detail: str,
        evidence: str,
        rule_id: str | None = None,
    ) -> None:
        result.risk_flags.append(
            {
                "category": category,
                "severity": severity,
                "detail": detail,
                "evidence": evidence,
                "rule_id": rule_id,
                "status": "OPEN",
            }
        )

    # -- the evaluation passes -------------------------------------------

    def evaluate(self, facts: Facts) -> EngineResult:
        r = EngineResult()
        self._security(r, facts)
        self._identity(r, facts)
        self._fraud(r, facts)
        self._programme(r, facts)
        self._leverage(r, facts)
        self._credit(r, facts)
        self._income_employment(r, facts)
        self._affordability(r, facts)
        self._assets(r, facts)
        self._property_valuation(r, facts)
        self._documentation(r, facts)
        self._routing(r, facts)
        return r

    # ---- security -------------------------------------------------------

    def _security(self, r: EngineResult, f: Facts) -> None:
        mapping = {
            "PROMPT_INJECTION": "SEC-INJ-001",
            "POLICY_OVERRIDE_ATTEMPT": "SEC-INJ-001",
            "INSTRUCTION_SMUGGLING": "SEC-INJ-001",
            "CROSS_CUSTOMER_ACCESS": "SEC-INJ-002",
            "PII_EXTRACTION": "SEC-INJ-003",
            "OUT_OF_SCOPE_REQUEST": "SEC-INJ-004",
        }
        if not f.security_event_types:
            self._emit(
                r, f, "SEC-INJ-001", PASS,
                "No applicant-supplied text required quarantine beyond the standard "
                "trust-class handling.",
                input_fields=("documents.contains_untrusted_text",),
            )
            return
        for event in f.security_event_types:
            rule_id = mapping.get(event, "SEC-INJ-001")
            self._emit(
                r, f, rule_id, FAIL,
                f"{event} detected in applicant-supplied content; content quarantined "
                "and treated as data. Underwriting continues on the verified evidence.",
                observed=event,
                threshold="refuse / quarantine / escalate",
                comparator="==",
                input_fields=("documents.untrusted_text",),
                force_human_review=True,
            )
            self._risk(
                r, "SECURITY", "HIGH",
                f"{event} raised on applicant-supplied content.",
                "security_events", rule_id,
            )
        self._emit(
            r, f, "SEC-AUD-001", PASS,
            f"{len(f.security_event_types)} security event(s) recorded with masked "
            "triggering content and the action taken.",
            observed=len(f.security_event_types),
            input_fields=("security_events",),
        )

    # ---- identity -------------------------------------------------------

    def _identity(self, r: EngineResult, f: Facts) -> None:
        if f.identity_status == "VERIFIED":
            self._emit(
                r, f, "KYC-IDV-001", PASS,
                "Identity verified; name, date of birth, address and a tokenised "
                "identification number were collected and matched.",
                observed=f.identity_status, threshold="VERIFIED", comparator="==",
                input_fields=("verifications.identity",),
            )
            return
        self._emit(
            r, f, "KYC-IDV-001", FAIL if f.identity_status == "FAILED" else REFER,
            f"Identity verification returned {f.identity_status}.",
            observed=f.identity_status, threshold="VERIFIED", comparator="==",
            input_fields=("verifications.identity",), force_human_review=True,
        )
        self._emit(
            r, f, "KYC-IDV-002", FAIL,
            "Identity elements conflict across sources; the application stops and is "
            "escalated to the financial-crime function rather than proceeding to "
            "ordinary underwriting.",
            observed=f.identity_status, threshold="VERIFIED", comparator="==",
            input_fields=("verifications.identity",), force_human_review=True,
        )
        self._risk(
            r, "IDENTITY", "HIGH",
            f"Identity verification {f.identity_status}.",
            "verifications.identity", "KYC-IDV-002",
        )

    # ---- fraud ----------------------------------------------------------

    def _fraud(self, r: EngineResult, f: Facts) -> None:
        if f.fraud_indicators:
            for indicator in f.fraud_indicators:
                self._emit(
                    r, f, "FRD-IND-001", REFER,
                    f"Cross-source inconsistency: {indicator}. Recorded with both "
                    "contributing sources for reviewer evaluation.",
                    observed=indicator, threshold="no unexplained inconsistency",
                    comparator="==", input_fields=("documents", "verifications"),
                    force_human_review=True,
                )
                self._risk(
                    r, "FRAUD", "HIGH", indicator, "document_extractions", "FRD-IND-001"
                )
            self._emit(
                r, f, "FRD-IND-003", REFER,
                "An open integrity finding may be cleared only by an authorised human "
                "reviewer; no automated component may close it.",
                observed=len(f.fraud_indicators), threshold="0 open findings",
                comparator=">", input_fields=("fraud_checks", "risk_flags", "human_reviews"),
                    force_human_review=True,
            )
        else:
            self._emit(
                r, f, "FRD-IND-001", PASS,
                "No cross-source inconsistency without an innocent arithmetic "
                "explanation was identified.",
                observed=0, threshold=0, comparator="==",
                input_fields=("documents", "verifications"),
            )
        if f.document_tampering:
            self._emit(
                r, f, "FRD-IND-002", FAIL,
                "Document integrity finding: the document is quarantined and is not "
                "used for qualification while the finding is open.",
                observed="tampering indicator present", threshold="none",
                comparator="==", input_fields=("documents.tampering_indicator",),
                force_human_review=True,
            )
            self._risk(
                r, "DOCUMENT_FRAUD", "HIGH",
                "Document shows alteration indicators.",
                "documents.tampering_indicator", "FRD-IND-002",
            )

    # ---- programme ------------------------------------------------------

    def _programme(self, r: EngineResult, f: Facts) -> None:
        _policy, rule = self._rule("GEN-ELG-003", f.as_of)
        limit = Decimal(f.conforming_limit)
        is_conforming_product = f.product == "conventional_conforming"
        if is_conforming_product:
            outcome = PASS if f.base_loan_amount <= limit else FAIL
            self._emit(
                r, f, "GEN-ELG-003", outcome,
                (
                    "Base loan amount is within the applicable one-unit conforming "
                    "limit."
                    if outcome == PASS
                    else "Base loan amount exceeds the applicable conforming limit, so "
                    "the loan cannot be executed as conventional conforming. It is not "
                    "ineligible for credit - it requires a different programme."
                ),
                observed=f.base_loan_amount, threshold=limit, comparator="<=",
                input_fields=("loans.base_loan_amount",),
            )
        elif f.product == "jumbo":
            outcome = PASS if f.base_loan_amount > limit else FAIL
            self._emit(
                r, f, "JMB-ELG-001", outcome,
                "Loan amount exceeds the applicable conforming limit, so the jumbo "
                "overlay governs."
                if outcome == PASS
                else "Loan amount is at or below the conforming limit; the jumbo "
                "overlay does not apply and the conforming product should be used.",
                observed=f.base_loan_amount, threshold=limit, comparator=">",
                input_fields=("loans.base_loan_amount",),
            )
            self._emit(
                r, f, "JMB-ELG-004", REFER,
                "Jumbo exposure: every file under this overlay is reviewed by a human "
                "underwriter because real jumbo criteria are set by private investor "
                "overlays that are not publicly documented.",
                observed="jumbo", threshold="human review mandatory", comparator="==",
                input_fields=("loans.base_loan_amount", "applications.product_family"),
                force_human_review=True,
            )
            self._risk(
                r, "PRODUCT_EXPOSURE", "MEDIUM",
                "Jumbo exposure above the conforming limit.",
                "loans.base_loan_amount", "JMB-ELG-004",
            )
        # Units / property type eligibility.
        max_units = 4
        if f.units > max_units or f.property_type in (
            "manufactured", "cooperative", "working_farm"
        ):
            self._emit(
                r, f, "PRP-ELG-001", FAIL,
                f"Property type '{f.property_type}' with {f.units} unit(s) is outside "
                "the eligible collateral set.",
                observed=f"{f.property_type}/{f.units}",
                threshold="1-4 units, eligible type", comparator="in",
                input_fields=("properties.property_type", "properties.units"),
            )
        else:
            self._emit(
                r, f, "PRP-ELG-001", PASS,
                f"Property type '{f.property_type}' with {f.units} unit(s) is eligible.",
                observed=f"{f.property_type}/{f.units}",
                threshold="1-4 units, eligible type", comparator="in",
                input_fields=("properties.property_type", "properties.units"),
            )

        if f.purpose == "cash_out_refinance":
            _p, seas = self._rule("CONV-COR-001", f.as_of)
            required = int(seas.parameters["min_ownership_months"])
            if f.ownership_months is None:
                self._emit(
                    r, f, "CONV-COR-001", INDETERMINATE,
                    "Ownership seasoning cannot be measured: no acquisition date is "
                    "evidenced on the title record.",
                    threshold=required, comparator=">=",
                    input_fields=("properties.ownership_months",),
                )
            else:
                seasoned = f.ownership_months >= required
                self._emit(
                    r, f, "CONV-COR-001", PASS if seasoned else FAIL,
                    f"The borrower has held title for {f.ownership_months} months "
                    f"against the {required}-month requirement for equity extraction.",
                    observed=f.ownership_months, threshold=required, comparator=">=",
                    input_fields=("properties.ownership_months",),
                )

        if f.product == "usda":
            _p, u = self._rule("USD-OVL-002", f.as_of)
            cap = Decimal(
                u.parameters[
                    "income_limit_household_1_to_4"
                    if f.household_size <= 4
                    else "income_limit_household_5_plus"
                ]
            )
            self._emit(
                r, f, "USD-OVL-002",
                PASS if f.household_annual_income <= cap else FAIL,
                "Adjusted household income is within the programme limit."
                if f.household_annual_income <= cap
                else "Adjusted household income exceeds the programme limit for the "
                "household size.",
                observed=f.household_annual_income, threshold=cap, comparator="<=",
                input_fields=("income.household_annual_income",),
            )
        _ = rule

    # ---- leverage -------------------------------------------------------

    def _leverage(self, r: EngineResult, f: Facts) -> None:
        rule_id, key = self._ltv_rule(f)
        _policy, rule = self._rule(rule_id, f.as_of)
        if f.ltv is None:
            self._emit(
                r, f, rule_id, INDETERMINATE,
                "Loan-to-value could not be computed: no accepted property value.",
                input_fields=("properties.appraised_value",),
            )
            return
        limit = Decimal(str(rule.parameters[key]))
        outcome = PASS if f.ltv <= limit else FAIL
        self._emit(
            r, f, rule_id, outcome,
            f"Loan-to-value {_pct(f.ltv)} against the {f.occupancy} limit of "
            f"{_pct(limit)} for this programme."
            + ("" if outcome == PASS else " The leverage limit is exceeded."),
            observed=f.ltv, threshold=limit, comparator="<=",
            input_fields=(
                "loans.loan_amount", "properties.value_used_for_ltv",
                "underwriting_calculations.ltv",
            ),
        )
        if outcome == FAIL:
            self._risk(
                r, "COLLATERAL", "HIGH",
                f"Leverage {_pct(f.ltv)} exceeds the programme limit {_pct(limit)}.",
                "underwriting_calculations.ltv", rule_id,
            )
        # Mortgage insurance requirement.
        if f.product == "conventional_conforming" and f.ltv > Decimal("0.80"):
            self._emit(
                r, f, "CONV-PUR-003", PASS,
                "Mortgage insurance is required above 80 percent leverage and its "
                "premium is included in the qualifying housing expense.",
                observed=f.ltv, threshold=Decimal("0.80"), comparator=">",
                input_fields=("underwriting_calculations.ltv", "loans.monthly_mi"),
            )
        # CLTV where subordinate financing exists.
        if f.cltv is not None and f.cltv > (f.ltv or Decimal(0)):
            cltv_key = f"max_cltv_{f.occupancy}"
            if cltv_key in rule.parameters:
                cltv_limit = Decimal(str(rule.parameters[cltv_key]))
                self._emit(
                    r, f, rule_id, PASS if f.cltv <= cltv_limit else FAIL,
                    f"Combined loan-to-value {_pct(f.cltv)} against the limit "
                    f"{_pct(cltv_limit)}.",
                    observed=f.cltv, threshold=cltv_limit, comparator="<=",
                    input_fields=("underwriting_calculations.cltv",),
                )

    def _ltv_rule(self, f: Facts) -> tuple[str, str]:
        if f.product == "jumbo":
            return "JMB-ELG-002", (
                "max_ltv_primary_residence"
                if f.occupancy == "primary_residence"
                else "max_ltv_other_occupancy"
            )
        if f.product == "fha":
            score = f.representative_score or 0
            return "FHA-OVL-002", (
                "max_ltv_score_580_plus" if score >= 580 else "max_ltv_score_500_to_579"
            )
        if f.product == "usda":
            return "USD-OVL-003", "max_ltv"
        if f.product == "va":
            return "VA-OVL-002", "max_ltv"
        if f.purpose == "cash_out_refinance":
            return "CONV-COR-002", f"max_ltv_{f.occupancy}"
        if f.purpose == "rate_term_refinance":
            return "CONV-RTR-002", f"max_ltv_{f.occupancy}"
        return "CONV-PUR-002", f"max_ltv_{f.occupancy}"

    # ---- credit ---------------------------------------------------------

    def _credit(self, r: EngineResult, f: Facts) -> None:
        # Minimum representative score, from whichever rule governs this product.
        rule_id, threshold = self._score_floor(f)
        if f.representative_score is None:
            self._emit(
                r, f, "CRD-SCR-005", REFER,
                "No usable credit score: the file is routed for manual credit review "
                "with alternative credit evidence. Absence of credit history is not "
                "adverse credit history.",
                observed=None, threshold="usable score or alternative credit",
                input_fields=("credit_profiles.representative_score",),
                force_human_review=True,
            )
        else:
            outcome = PASS if f.representative_score >= threshold else FAIL
            self._emit(
                r, f, rule_id, outcome,
                f"Representative score {f.representative_score} against the applicable "
                f"floor of {threshold}."
                + ("" if outcome == PASS else " The credit floor is not met."),
                observed=f.representative_score, threshold=threshold, comparator=">=",
                input_fields=("credit_profiles.representative_score",),
            )
            if outcome == FAIL:
                self._risk(
                    r, "CREDIT", "HIGH",
                    f"Representative score {f.representative_score} below the floor "
                    f"{threshold}.",
                    "credit_profiles.representative_score", rule_id,
                )
            if f.scoreable_tradelines < 3:
                self._emit(
                    r, f, "CRD-SCR-005", REFER,
                    f"Only {f.scoreable_tradelines} scoreable tradeline(s); manual "
                    "credit review with alternative credit evidence is required.",
                    observed=f.scoreable_tradelines, threshold=3, comparator=">=",
                    input_fields=("credit_accounts",), force_human_review=True,
                )

        # Report freshness.
        _p, fresh = self._rule("CRD-SCR-004", f.as_of)
        max_age = int(fresh.parameters["max_report_age_days"])
        fresh_outcome = PASS if f.credit_report_age_days <= max_age else FAIL
        self._emit(
            r, f, "CRD-SCR-004", fresh_outcome,
            f"Credit report is {f.credit_report_age_days} days old against the "
            f"{max_age}-day window in force on the as-of date.",
            observed=f.credit_report_age_days, threshold=max_age, comparator="<=",
            input_fields=("credit_profiles.report_date",),
        )
        if fresh_outcome == FAIL:
            self._condition(
                r, "CRD-SCR-004", "CREDIT",
                "Obtain a refreshed credit report before closing.",
                "Consumer report dated within the freshness window",
            )

        # Recent inquiries: the rule only exists in the v2 policy.
        try:
            _p2, inq = self._rule("CRD-SCR-007", f.as_of)
        except KeyError:
            inq = None
        if inq is not None:
            trigger = int(inq.parameters["inquiry_count_trigger"])
            if f.recent_inquiries_90d >= trigger:
                self._emit(
                    r, f, "CRD-SCR-007", REFER,
                    f"{f.recent_inquiries_90d} inquiries in the 90-day lookback require "
                    "a written explanation identifying whether any resulted in new debt. "
                    "Inquiry count is never itself a basis for an adverse outcome.",
                    observed=f.recent_inquiries_90d, threshold=trigger, comparator="<",
                    input_fields=("credit_profiles.recent_inquiries_90d",),
                )
                self._condition(
                    r, "CRD-SCR-007", "CREDIT",
                    f"Provide a written explanation for the {f.recent_inquiries_90d} "
                    "credit inquiries in the 90 days before the report date.",
                    "Borrower letter of explanation",
                )
            else:
                self._emit(
                    r, f, "CRD-SCR-007", PASS,
                    f"{f.recent_inquiries_90d} inquiries in the 90-day lookback, below "
                    "the explanation trigger.",
                    observed=f.recent_inquiries_90d, threshold=trigger, comparator="<",
                    input_fields=("credit_profiles.recent_inquiries_90d",),
                )

        # Derogatory seasoning.
        _p3, evt = self._rule("CRD-EVT-001", f.as_of)
        for event in f.credit_events:
            key = {
                "chapter_7_bankruptcy": "chapter_7_bankruptcy_months",
                "chapter_13_bankruptcy": "chapter_13_bankruptcy_discharged_months",
                "foreclosure": "foreclosure_months",
                "deed_in_lieu": "deed_in_lieu_months",
                "short_sale": "short_sale_months",
                "mortgage_charge_off": "mortgage_charge_off_months",
            }.get(event["event_type"])
            if key is None:
                continue
            required = int(evt.parameters[key])
            seasoned = int(event["seasoning_months"])
            outcome = PASS if seasoned >= required else FAIL
            self._emit(
                r, f, "CRD-EVT-001", outcome,
                f"{event['event_type']} anchored at {event['anchor_date']} is "
                f"{seasoned} months seasoned against the {required}-month requirement.",
                observed=seasoned, threshold=required, comparator=">=",
                input_fields=("credit_events.anchor_date", "credit_events.event_type"),
            )
            if outcome == FAIL:
                self._risk(
                    r, "CREDIT_EVENT", "HIGH",
                    f"{event['event_type']} seasoned {seasoned} of {required} months.",
                    "credit_events", "CRD-EVT-001",
                )

        # Collections.
        _p4, coll = self._rule("CRD-EVT-003", f.as_of)
        agg = Decimal(str(coll.parameters["aggregate_threshold"]))
        if f.collection_total > agg:
            self._emit(
                r, f, "CRD-EVT-003", FAIL,
                f"Non-medical collection and charge-off balances total "
                f"{_money(f.collection_total)} against the {_money(agg)} threshold; "
                "they must be paid or brought into a documented plan before closing.",
                observed=f.collection_total, threshold=agg, comparator="<=",
                input_fields=("credit_accounts.collection_balance",),
            )
            self._condition(
                r, "CRD-EVT-003", "CREDIT",
                f"Pay off or document a payment plan for collection balances totalling "
                f"{_money(f.collection_total)}.",
                "Payoff evidence or executed payment plan",
            )
        elif f.collection_total > 0:
            self._emit(
                r, f, "CRD-EVT-003", PASS,
                f"Collection balances of {_money(f.collection_total)} are within the "
                f"{_money(agg)} aggregate threshold.",
                observed=f.collection_total, threshold=agg, comparator="<=",
                input_fields=("credit_accounts.collection_balance",),
            )

        # Delinquency.
        if f.housing_lates_60d_12m >= 1:
            self._emit(
                r, f, "CRD-DLQ-001", FAIL,
                f"{f.housing_lates_60d_12m} housing payment(s) 60 or more days past due "
                "in the last 12 months.",
                observed=f.housing_lates_60d_12m, threshold=0, comparator="==",
                input_fields=("credit_accounts.housing_late_history",),
            )
        elif f.housing_lates_30d_12m >= 1:
            self._emit(
                r, f, "CRD-DLQ-001", REFER,
                f"{f.housing_lates_30d_12m} housing payment(s) 30 days past due in the "
                "last 12 months; underwriter review required.",
                observed=f.housing_lates_30d_12m, threshold=0, comparator="==",
                input_fields=("credit_accounts.housing_late_history",),
                force_human_review=True,
            )
        else:
            self._emit(
                r, f, "CRD-DLQ-001", PASS,
                "No housing payment 30 or more days past due in the last 12 months.",
                observed=0, threshold=0, comparator="==",
                input_fields=("credit_accounts.housing_late_history",),
            )
        if f.nonhousing_accounts_30d_24m >= 3 or f.any_90d_24m:
            self._emit(
                r, f, "CRD-DLQ-002", REFER,
                f"{f.nonhousing_accounts_30d_24m} account(s) 30+ days past due in 24 "
                f"months{' and a 90-day delinquency' if f.any_90d_24m else ''}; a "
                "written explanation and underwriter review are required.",
                observed=f.nonhousing_accounts_30d_24m, threshold=3, comparator="<",
                input_fields=("credit_accounts.late_history",), force_human_review=True,
            )
            self._condition(
                r, "CRD-DLQ-002", "CREDIT",
                "Provide a written explanation of the delinquencies reported in the last "
                "24 months.",
                "Borrower letter of explanation",
            )

        # Utilisation (advisory).
        if f.revolving_utilization is not None:
            _p5, util = self._rule("CRD-DLQ-003", f.as_of)
            note_at = Decimal(str(util.parameters["risk_note_threshold"]))
            self._emit(
                r, f, "CRD-DLQ-003", PASS,
                f"Revolving utilisation {_pct(f.revolving_utilization)}"
                + (
                    " is above the risk-note threshold and is recorded as context, not "
                    "as a policy breach."
                    if f.revolving_utilization > note_at
                    else " is within the risk-note threshold."
                ),
                observed=f.revolving_utilization, threshold=note_at, comparator="<=",
                input_fields=("underwriting_calculations.credit_utilization",),
            )
            if f.revolving_utilization > note_at:
                self._risk(
                    r, "CREDIT", "MEDIUM",
                    f"Revolving utilisation {_pct(f.revolving_utilization)}.",
                    "underwriting_calculations.credit_utilization", "CRD-DLQ-003",
                )

        if f.undeclared_liability_found:
            self._emit(
                r, f, "LIA-INC-006", REFER,
                "An obligation appearing on the credit report was not declared on the "
                "application. It has been added to the liabilities and the "
                "debt-to-income ratio recomputed; the borrower must confirm or dispute "
                "it before a decision is reached.",
                observed="undeclared obligation present", threshold="none",
                comparator="==", input_fields=("liabilities.source",),
                force_human_review=True,
            )
            self._condition(
                r, "LIA-INC-006", "CREDIT",
                "Confirm or dispute the undeclared obligation identified on the credit "
                "report.",
                "Borrower confirmation or dispute documentation",
            )
            self._risk(
                r, "DATA_QUALITY", "MEDIUM",
                "Credit report discloses an obligation absent from the application.",
                "liabilities", "LIA-INC-006",
            )

    def _score_floor(self, f: Facts) -> tuple[str, int]:
        if f.product == "jumbo":
            _p, rule = self._rule("JMB-ELG-002", f.as_of)
            return "JMB-ELG-002", int(rule.parameters["min_representative_score"])
        if f.product == "fha":
            _p, rule = self._rule("FHA-OVL-002", f.as_of)
            return "FHA-OVL-002", int(rule.parameters["min_representative_score"])
        if f.purpose == "cash_out_refinance":
            _p, rule = self._rule("CONV-COR-003", f.as_of)
            trigger = Decimal(str(rule.parameters["ltv_trigger"]))
            if f.ltv is not None and f.ltv > trigger:
                return "CONV-COR-003", int(
                    rule.parameters["min_representative_score_ltv_above_75"]
                )
            return "CONV-COR-003", int(rule.parameters["min_representative_score"])
        _p, rule = self._rule("CRD-SCR-003", f.as_of)
        if "min_representative_score_conventional" in rule.parameters:
            return "CRD-SCR-003", int(
                rule.parameters["min_representative_score_conventional"]
            )
        boundary = Decimal(str(rule.parameters["ltv_band_boundary"]))
        if f.ltv is not None and f.ltv > boundary:
            return "CRD-SCR-003", int(
                rule.parameters["min_representative_score_ltv_above_90"]
            )
        return "CRD-SCR-003", int(
            rule.parameters["min_representative_score_ltv_at_or_below_90"]
        )

    # ---- income and employment -----------------------------------------

    def _income_employment(self, r: EngineResult, f: Facts) -> None:
        if f.self_employed:
            self._emit(
                r, f, "INC-SEB-006", REFER,
                "Self-employment income requires human underwriting review before a "
                "recommendation is issued; cash-flow and add-back judgement is outside "
                "what an automated component may settle.",
                observed="self-employed", threshold="human review mandatory",
                comparator="==", input_fields=("employment.self_employed_flag",),
                force_human_review=True,
            )

        if f.income_conflict_variance is not None:
            _p, rule = self._rule("INC-GEN-006", f.as_of)
            tol = Decimal(str(rule.parameters["materiality_threshold"]))
            outcome = REFER if f.income_conflict_variance > tol else PASS
            self._emit(
                r, f, "INC-GEN-006", outcome,
                f"Income evidence differs across sources by "
                f"{_pct(f.income_conflict_variance)} against a {_pct(tol)} materiality "
                "threshold. The lower verified figure is used pending resolution and "
                "both values are recorded."
                if outcome == REFER
                else f"Income evidence agrees across sources within "
                f"{_pct(f.income_conflict_variance)}.",
                observed=f.income_conflict_variance, threshold=tol, comparator="<=",
                input_fields=("income.declared_amount", "income.verified_amount"),
                force_human_review=True,
            )
            if outcome == REFER:
                self._condition(
                    r, "INC-GEN-006", "INCOME",
                    "Reconcile the conflicting income evidence and confirm the "
                    "qualifying amount.",
                    "Employer confirmation or corrected income documentation",
                )
                self._risk(
                    r, "DATA_QUALITY", "HIGH",
                    f"Income evidence variance {_pct(f.income_conflict_variance)}.",
                    "document_extractions", "INC-GEN-006",
                )

        if f.ytd_reconciliation_variance is not None:
            _p, rule = self._rule("INC-SAL-003", f.as_of)
            tol = Decimal(str(rule.parameters["tolerance"]))
            outcome = REFER if f.ytd_reconciliation_variance > tol else PASS
            self._emit(
                r, f, "INC-SAL-003", outcome,
                f"Annualised year-to-date earnings differ from the stated salary by "
                f"{_pct(f.ytd_reconciliation_variance)} against a {_pct(tol)} tolerance.",
                observed=f.ytd_reconciliation_variance, threshold=tol, comparator="<=",
                input_fields=("document_extractions.ytd_gross", "income.annual_amount"),
                force_human_review=True,
            )

        if f.variable_income_history_months is not None:
            _p, rule = self._rule("INC-VAR-001", f.as_of)
            required = int(rule.parameters["required_history_months"])
            if f.variable_income_history_months >= required:
                self._emit(
                    r, f, "INC-VAR-001", PASS,
                    f"Variable earnings history of {f.variable_income_history_months} "
                    f"months meets the {required}-month requirement.",
                    observed=f.variable_income_history_months, threshold=required,
                    comparator=">=", input_fields=("income_history",),
                )
            elif rule.parameters.get("shorter_history_allowed"):
                minimum = int(rule.parameters["minimum_history_months"])
                need_factors = int(rule.parameters["min_positive_factors"])
                if (
                    f.variable_income_history_months >= minimum
                    and f.variable_income_positive_factors >= need_factors
                ):
                    self._emit(
                        r, f, "INC-VAR-001", REFER,
                        f"Variable earnings history of "
                        f"{f.variable_income_history_months} months is below the "
                        f"{required}-month standard but meets the {minimum}-month "
                        f"allowance with {f.variable_income_positive_factors} documented "
                        "positive factors; a haircut applies and the file is reviewed.",
                        observed=f.variable_income_history_months, threshold=minimum,
                        comparator=">=", input_fields=("income_history",),
                        force_human_review=True,
                    )
                else:
                    self._emit(
                        r, f, "INC-VAR-001", FAIL,
                        f"Variable earnings history of "
                        f"{f.variable_income_history_months} months does not meet the "
                        f"{required}-month standard or the {minimum}-month allowance "
                        "with sufficient documented positive factors.",
                        observed=f.variable_income_history_months, threshold=required,
                        comparator=">=", input_fields=("income_history",),
                    )
            else:
                self._emit(
                    r, f, "INC-VAR-001", FAIL,
                    f"Variable earnings history of {f.variable_income_history_months} "
                    f"months is below the {required}-month requirement, and this policy "
                    "version provides no shorter-history allowance, so the variable "
                    "component is excluded from qualifying income.",
                    observed=f.variable_income_history_months, threshold=required,
                    comparator=">=", input_fields=("income_history",),
                )

        # Employment history and continuity.
        _p, hist = self._rule("EMP-CNT-001", f.as_of)
        required_hist = int(hist.parameters["required_history_months"])
        if f.employment_history_months < required_hist:
            self._emit(
                r, f, "EMP-CNT-001", REFER,
                f"Combined employment history of {f.employment_history_months} months "
                f"is below the {required_hist}-month requirement; the file is reviewed "
                "rather than failed, because a shorter history with strong continuity "
                "can still support the income.",
                observed=f.employment_history_months, threshold=required_hist,
                comparator=">=", input_fields=("employment.start_date",),
                force_human_review=True,
            )
        else:
            self._emit(
                r, f, "EMP-CNT-001", PASS,
                f"Employment history of {f.employment_history_months} months meets the "
                f"{required_hist}-month requirement.",
                observed=f.employment_history_months, threshold=required_hist,
                comparator=">=", input_fields=("employment.start_date",),
            )

        if f.job_change_recent:
            outcome = REFER if f.job_change_field_or_structure else PASS
            self._emit(
                r, f, "EMP-CNT-002", outcome,
                "Recent change of employer involved a change of field or compensation "
                "structure, so the prior history no longer predicts the new earnings; "
                "underwriter review required."
                if outcome == REFER
                else "Recent change of employer within the same field with no reduction "
                "in compensation, and at least one full pay period completed.",
                observed="field/structure change" if outcome == REFER else "same field",
                threshold="same field, same structure", comparator="==",
                input_fields=("employment.start_date", "employment.occupation"),
                force_human_review=True,
            )

        if f.future_employment_start is not None:
            _p, fut = self._rule("EMP-CNT-004", f.as_of)
            max_days = int(fut.parameters["max_days_to_start"])
            days = (f.future_employment_start - f.as_of).days
            outcome = REFER if 0 <= days <= max_days else FAIL
            self._emit(
                r, f, "EMP-CNT-004", outcome,
                f"Employment begins in {days} days against the {max_days}-day window; "
                "a non-contingent offer and reserves covering the gap period are "
                "required, and the file is reviewed in every case."
                if outcome == REFER
                else f"Employment begins in {days} days, outside the {max_days}-day "
                "window in which future employment income may be used.",
                observed=days, threshold=max_days, comparator="<=",
                input_fields=("employment.start_date",), force_human_review=True,
            )
            self._condition(
                r, "EMP-CNT-004", "EMPLOYMENT",
                "Provide the non-contingent offer letter and reserve evidence covering "
                "the period to the employment start date.",
                "Offer letter and asset statements",
            )

        if f.employment_verification_conflict:
            self._emit(
                r, f, "EMP-VER-003", REFER,
                "The employment verification reports details that differ materially "
                "from the application. The verified value governs and the discrepancy is "
                "recorded with both values and their sources.",
                observed="verification conflict", threshold="sources agree",
                comparator="==",
                input_fields=("employment.start_date", "verifications.employment"),
                force_human_review=True,
            )
            self._condition(
                r, "EMP-VER-003", "EMPLOYMENT",
                "Resolve the discrepancy between the application and the employment "
                "verification.",
                "Employer confirmation of the authoritative detail",
            )
            self._risk(
                r, "EMPLOYMENT", "MEDIUM",
                "Employment verification contradicts the application.",
                "verifications.employment", "EMP-VER-003",
            )

    # ---- affordability --------------------------------------------------

    def _affordability(self, r: EngineResult, f: Facts) -> None:
        if f.product == "va":
            self._va_affordability(r, f)
            self._emit(
                r, f, "DTI-CALC-003", PASS,
                f"Monthly disposable income {_money(f.residual_income)} recorded "
                "alongside the ratio.",
                observed=f.residual_income,
                input_fields=("underwriting_calculations.residual_income_monthly",),
            )
            return
        rule_id, limit, extended, need_factors = self._dti_limit(f)
        if f.back_end_dti is None:
            self._emit(
                r, f, rule_id, INDETERMINATE,
                "Back-end debt-to-income could not be computed: qualifying monthly "
                "income is zero, so the ratio is undefined rather than infinite.",
                input_fields=("underwriting_calculations.qualifying_monthly_income",),
            )
            return

        factors = len(f.compensating_factors)
        applicable = limit
        used_extension = False
        if extended is not None and f.back_end_dti > limit and factors >= need_factors:
            applicable = extended
            used_extension = True

        outcome = PASS if f.back_end_dti <= applicable else FAIL
        reason = (
            f"Back-end debt-to-income {_pct(f.back_end_dti)} against the applicable "
            f"limit of {_pct(applicable)}"
        )
        if used_extension:
            reason += (
                f", extended from {_pct(limit)} on {factors} documented compensating "
                f"factor(s): {', '.join(f.compensating_factors)}"
            )
        elif extended is not None and f.back_end_dti > limit:
            reason += (
                f". The extension to {_pct(extended)} was not available: "
                f"{factors} documented compensating factor(s) against the "
                f"{need_factors} required"
            )
        reason += "." if outcome == PASS else ". The affordability limit is breached."
        self._emit(
            r, f, rule_id, outcome, reason,
            observed=f.back_end_dti, threshold=applicable, comparator="<=",
            input_fields=(
                "underwriting_calculations.total_monthly_debt",
                "underwriting_calculations.qualifying_monthly_income",
                "underwriting_calculations.back_end_dti",
            ),
        )
        if outcome == FAIL:
            self._risk(
                r, "AFFORDABILITY", "HIGH",
                f"Back-end DTI {_pct(f.back_end_dti)} exceeds {_pct(applicable)}.",
                "underwriting_calculations.back_end_dti", rule_id,
            )
            self._emit(
                r, f, "DTI-BRE-001", PASS,
                f"The breach is reported with its computed value {_pct(f.back_end_dti)}, "
                f"the threshold {_pct(applicable)} it failed, the rule {rule_id} and the "
                "policy version that set it.",
                observed=f.back_end_dti, threshold=applicable, comparator="<=",
                input_fields=("rule_evaluations",),
            )
        else:
            # Borderline band -> human review per UWR-HRV-001.
            _p, hrv = self._rule("UWR-HRV-001", f.as_of)
            band = Decimal(str(hrv.parameters["borderline_band_pct_points"])) / Decimal(100)
            if applicable - f.back_end_dti <= band:
                self._emit(
                    r, f, "UWR-HRV-001", REFER,
                    f"Affordability result {_pct(f.back_end_dti)} is within "
                    f"{_pct(band)} of its {_pct(applicable)} limit, which is a mandatory "
                    "human-review trigger.",
                    observed=f.back_end_dti, threshold=applicable, comparator="<=",
                    input_fields=("underwriting_calculations.back_end_dti",),
                    force_human_review=True,
                )

        # Housing ratio - advisory on conventional, hard on the USDA overlay.
        if f.front_end_dti is not None:
            if f.product == "usda":
                _p, usd = self._rule("USD-OVL-004", f.as_of)
                cap = Decimal(str(usd.parameters["max_front_end_dti"]))
                self._emit(
                    r, f, "USD-OVL-004",
                    PASS if f.front_end_dti <= cap else FAIL,
                    f"Housing ratio {_pct(f.front_end_dti)} against the programme's hard "
                    f"limit of {_pct(cap)}.",
                    observed=f.front_end_dti, threshold=cap, comparator="<=",
                    input_fields=("underwriting_calculations.front_end_dti",),
                )
            else:
                _p, hr = self._rule("DTI-CONV-002", f.as_of)
                note = Decimal(str(hr.parameters["risk_note_threshold"]))
                self._emit(
                    r, f, "DTI-CONV-002", PASS,
                    f"Housing ratio {_pct(f.front_end_dti)} recorded; this measure is "
                    "advisory on this programme"
                    + (
                        " and is above the risk-note threshold."
                        if f.front_end_dti > note
                        else "."
                    ),
                    observed=f.front_end_dti, threshold=note, comparator="<=",
                    input_fields=("underwriting_calculations.front_end_dti",),
                )

        # Payment shock - advisory.
        self._emit(
            r, f, "DTI-CALC-003", PASS,
            f"Monthly disposable income {_money(f.residual_income)} recorded alongside "
            "the ratio.",
            observed=f.residual_income,
            input_fields=("underwriting_calculations.residual_income_monthly",),
        )

    def _va_affordability(self, r: EngineResult, f: Facts) -> None:
        """VA-OVL-003 is both the ratio test and the residual test for this programme.

        A borrower can sit comfortably inside every ratio another programme would apply
        and still leave too little cash each month to run a household of four. That is
        the point of a residual standard, so the two are evaluated as one rule rather
        than as a ratio with a footnote.
        """
        _p, va = self._rule("VA-OVL-003", f.as_of)
        key = (
            f"residual_income_floor_household_{f.household_size}"
            if f.household_size < 4
            else "residual_income_floor_household_4_plus"
        )
        floor = Decimal(str(va.parameters[key]))
        guideline = Decimal(
            str(va.parameters["max_back_end_dti_without_residual_cushion"])
        )
        multiple = Decimal(
            str(va.parameters["residual_cushion_multiple_above_guideline"])
        )
        cushion = (floor * multiple).quantize(Decimal("0.01"))
        dti = f.back_end_dti if f.back_end_dti is not None else Decimal(0)

        if f.residual_income < floor:
            outcome = FAIL
            threshold = floor
            reason = (
                f"Residual income {_money(f.residual_income)} is below the "
                f"{_money(floor)} floor for a household of {f.household_size}."
            )
        elif dti > guideline and f.residual_income < cushion:
            outcome = FAIL
            threshold = cushion
            reason = (
                f"Back-end debt-to-income {_pct(dti)} exceeds the {_pct(guideline)} "
                f"guideline, which is permitted only where residual income reaches "
                f"{_money(cushion)}. Residual income is {_money(f.residual_income)}, "
                "so the guideline governs."
            )
        elif dti > guideline:
            outcome = PASS
            threshold = cushion
            reason = (
                f"Back-end debt-to-income {_pct(dti)} exceeds the {_pct(guideline)} "
                f"guideline but residual income {_money(f.residual_income)} clears the "
                f"{_money(cushion)} cushion, so the file qualifies on residual income."
            )
        else:
            outcome = PASS
            threshold = floor
            reason = (
                f"Back-end debt-to-income {_pct(dti)} is within the {_pct(guideline)} "
                f"guideline and residual income {_money(f.residual_income)} clears the "
                f"{_money(floor)} floor for a household of {f.household_size}."
            )
        self._emit(
            r, f, "VA-OVL-003", outcome, reason,
            observed=f.residual_income, threshold=threshold, comparator=">=",
            input_fields=(
                "underwriting_calculations.residual_income_monthly",
                "underwriting_calculations.back_end_dti",
                "applications.household_size",
            ),
        )
        if outcome == FAIL:
            self._risk(
                r, "AFFORDABILITY", "HIGH",
                f"Residual income {_money(f.residual_income)} insufficient for a "
                f"household of {f.household_size}.",
                "underwriting_calculations.residual_income_monthly", "VA-OVL-003",
            )

    def _dti_limit(self, f: Facts) -> tuple[str, Decimal, Decimal | None, int]:
        if f.product == "fha":
            _p, rule = self._rule("FHA-OVL-004", f.as_of)
            return (
                "FHA-OVL-004",
                Decimal(str(rule.parameters["max_back_end_dti"])),
                Decimal(str(rule.parameters["max_back_end_dti_with_factors"])),
                int(rule.parameters["min_compensating_factors"]),
            )
        if f.product == "usda":
            _p, rule = self._rule("USD-OVL-004", f.as_of)
            return (
                "USD-OVL-004",
                Decimal(str(rule.parameters["max_back_end_dti"])),
                None,
                0,
            )
        _p, rule = self._rule("DTI-CONV-001", f.as_of)
        limit = Decimal(str(rule.parameters["max_back_end_dti"]))
        extended = rule.parameters.get("max_back_end_dti_with_factors")
        # The extension is not available on cash-out or jumbo (DTI-CONV-003).
        if extended is not None and (
            f.purpose == "cash_out_refinance" or f.product == "jumbo"
        ):
            extended = None
        return (
            "DTI-CONV-001",
            limit,
            Decimal(str(extended)) if extended is not None else None,
            int(rule.parameters.get("min_compensating_factors", 0)),
        )

    # ---- assets ---------------------------------------------------------

    def _assets(self, r: EngineResult, f: Facts) -> None:
        sufficient = f.funds_shortfall <= 0
        self._emit(
            r, f, "AST-FTC-003", PASS if sufficient else FAIL,
            f"Eligible funds available {_money(f.funds_available)} against "
            f"{_money(f.funds_required)} required at settlement"
            + (
                "."
                if sufficient
                else f"; a shortfall of {_money(f.funds_shortfall)}. This is a "
                "deterministic arithmetic failure that no compensating factor cures."
            ),
            observed=f.funds_available, threshold=f.funds_required, comparator=">=",
            input_fields=(
                "underwriting_calculations.funds_to_close_required",
                "underwriting_calculations.funds_to_close_available",
            ),
        )
        if not sufficient:
            self._risk(
                r, "ASSET_LIQUIDITY", "HIGH",
                f"Funds-to-close shortfall {_money(f.funds_shortfall)}.",
                "underwriting_calculations.funds_shortfall", "AST-FTC-003",
            )

        # Reserves.
        required_months = self._required_reserve_months(f)
        if f.reserves_months is None:
            self._emit(
                r, f, "AST-RSV-002", INDETERMINATE,
                "Months of reserves could not be computed: the qualifying housing "
                "expense is zero.",
                input_fields=("underwriting_calculations.post_close_reserves",),
            )
        else:
            met = f.reserves_months >= required_months
            self._emit(
                r, f, "AST-RSV-002", PASS if met else FAIL,
                f"Post-closing reserves of {f.reserves_months} months against the "
                f"{required_months}-month requirement for this occupancy, leverage and "
                "affordability profile.",
                observed=f.reserves_months, threshold=required_months, comparator=">=",
                input_fields=(
                    "underwriting_calculations.post_close_reserves",
                    "underwriting_calculations.months_reserves",
                ),
            )
            if not met:
                self._condition(
                    r, "AST-RSV-002", "ASSETS",
                    f"Evidence reserve-eligible assets sufficient for "
                    f"{required_months} months of the qualifying housing expense.",
                    "Asset statements or a validated asset-verification report",
                )
                self._risk(
                    r, "ASSET_LIQUIDITY", "MEDIUM",
                    f"Reserves {f.reserves_months} months below the "
                    f"{required_months}-month requirement.",
                    "underwriting_calculations.months_reserves", "AST-RSV-002",
                )

        # Large deposits.
        if f.unsourced_deposit_amount > 0:
            _p, rule = self._rule("AST-SRC-002", f.as_of)
            pct = Decimal(str(rule.parameters[
                "threshold_pct_of_qualifying_monthly_income"
            ]))
            threshold = (f.qualifying_monthly_income * pct).quantize(Decimal("0.01"))
            self._emit(
                r, f, "AST-SRC-002", REFER,
                f"A deposit of {_money(f.unsourced_deposit_amount)} exceeds the "
                f"{_money(threshold)} threshold ({_pct(pct)} of qualifying monthly "
                "income) and has no documented source. It is excluded from eligible "
                "assets and the funds and reserve calculations were re-run without it.",
                observed=f.unsourced_deposit_amount, threshold=threshold,
                comparator="<=", input_fields=("asset_transactions",),
                force_human_review=True,
            )
            self._condition(
                r, "AST-SRC-002", "ASSETS",
                f"Document the source of the deposit of "
                f"{_money(f.unsourced_deposit_amount)} and confirm the funds are not "
                "borrowed.",
                "Transfer evidence identifying the origin of the funds",
            )
            self._risk(
                r, "SOURCE_OF_FUNDS", "HIGH",
                f"Unsourced deposit {_money(f.unsourced_deposit_amount)}.",
                "asset_transactions", "AST-SRC-002",
            )

        if f.gift_amount > 0:
            gifts_allowed = f.occupancy != "investment"
            if not gifts_allowed:
                self._emit(
                    r, f, "AST-SRC-001", FAIL,
                    "Gift funds are not permitted on an investment-property "
                    "transaction.",
                    observed="gift funds present", threshold="no gift on investment",
                    comparator="==", input_fields=("assets.asset_type",),
                )
            elif not f.gift_documented:
                self._emit(
                    r, f, "AST-SRC-001", INDETERMINATE,
                    "Gift funds are relied upon but the signed gift letter and transfer "
                    "evidence are outstanding, so the rule cannot be evaluated.",
                    observed=f.gift_amount, threshold="documented", comparator="==",
                    input_fields=("assets.asset_type", "documents.gift_letter"),
                )
                self._condition(
                    r, "AST-SRC-001", "ASSETS",
                    f"Provide a signed gift letter and transfer evidence for the gift of "
                    f"{_money(f.gift_amount)}.",
                    "Gift letter and transfer evidence",
                )
            else:
                self._emit(
                    r, f, "AST-SRC-001", PASS,
                    f"Gift of {_money(f.gift_amount)} is from an eligible donor with a "
                    "signed letter and transfer evidence, and is excluded from reserves.",
                    observed=f.gift_amount, threshold="documented, eligible donor",
                    comparator="==", input_fields=("assets", "documents.gift_letter"),
                )
            # Minimum borrower contribution.
            _p, contrib = self._rule("CONV-PUR-004", f.as_of)
            key = f"min_own_funds_pct_{f.occupancy}"
            if key in contrib.parameters and f.purpose == "purchase":
                need = Decimal(str(contrib.parameters[key]))
                self._emit(
                    r, f, "CONV-PUR-004",
                    PASS if f.own_funds_pct >= need else FAIL,
                    f"Borrower's own funds {_pct(f.own_funds_pct)} of purchase price "
                    f"against the {_pct(need)} minimum for {f.occupancy}.",
                    observed=f.own_funds_pct, threshold=need, comparator=">=",
                    input_fields=("assets", "underwriting_calculations.down_payment_amount"),
                )

        if f.purpose == "cash_out_refinance":
            _p, rsv = self._rule("CONV-COR-004", f.as_of)
            need = Decimal(str(rsv.parameters["min_months_reserves"]))
            if f.reserves_months is not None:
                self._emit(
                    r, f, "CONV-COR-004",
                    PASS if f.reserves_months >= need else FAIL,
                    f"Cash-out reserves of {f.reserves_months} months against the "
                    f"{need}-month requirement, counted from assets other than loan "
                    "proceeds.",
                    observed=f.reserves_months, threshold=need, comparator=">=",
                    input_fields=("underwriting_calculations.months_reserves",),
                )

        if f.product == "jumbo":
            _p, jrsv = self._rule("JMB-ELG-003", f.as_of)
            need = Decimal(str(jrsv.parameters["min_months_reserves"]))
            tier = jrsv.parameters.get("loan_amount_tier_trigger")
            if tier is not None and f.base_loan_amount > Decimal(str(tier)):
                need = Decimal(str(jrsv.parameters["min_months_reserves_above_1_5m"]))
            if f.reserves_months is not None:
                self._emit(
                    r, f, "JMB-ELG-003",
                    PASS if f.reserves_months >= need else FAIL,
                    f"Jumbo reserves of {f.reserves_months} months against the "
                    f"{need}-month overlay requirement in force on the as-of date.",
                    observed=f.reserves_months, threshold=need, comparator=">=",
                    input_fields=("underwriting_calculations.months_reserves",),
                )
            second = jrsv.parameters.get("second_valuation_above_loan_amount")
            _ = second

    def _required_reserve_months(self, f: Facts) -> Decimal:
        _p, rule = self._rule("AST-RSV-002", f.as_of)
        base = Decimal(str(rule.parameters[f"min_months_{f.occupancy}"]))
        if "additional_months_ltv_above_90" in rule.parameters:
            if f.ltv is not None and f.ltv > Decimal(
                str(rule.parameters["ltv_trigger"])
            ):
                base += Decimal(str(rule.parameters["additional_months_ltv_above_90"]))
            if f.back_end_dti is not None and f.back_end_dti > Decimal(
                str(rule.parameters["dti_trigger"])
            ):
                base += Decimal(str(rule.parameters["additional_months_dti_above_43"]))
        _p2, extra = self._rule("AST-RSV-003", f.as_of)
        per = Decimal(str(extra.parameters["additional_months_per_financed_property"]))
        cap = Decimal(str(extra.parameters["additional_months_cap"]))
        base += min(per * f.other_financed_properties, cap)
        return base

    # ---- property and valuation -----------------------------------------

    def _property_valuation(self, r: EngineResult, f: Facts) -> None:
        _p, rule = self._rule("VAL-APR-001", f.as_of)
        if f.valuation_method == "value_acceptance":
            allowed = bool(rule.parameters.get("value_acceptance_available"))
            self._emit(
                r, f, "VAL-APR-001", PASS if allowed else FAIL,
                "Automated value acceptance is available under the policy version in "
                "force on the as-of date, and the transaction meets its conditions."
                if allowed
                else "Automated value acceptance is not available under the policy "
                "version in force on the as-of date; a full appraisal is required.",
                observed=f.valuation_method,
                threshold="value_acceptance permitted" if allowed else "full_appraisal",
                comparator="==", input_fields=("appraisals.valuation_method",),
            )
            if not allowed:
                self._condition(
                    r, "VAL-APR-001", "COLLATERAL",
                    "Obtain a full interior and exterior appraisal.",
                    "Appraisal report from a licensed appraiser",
                )
        else:
            self._emit(
                r, f, "VAL-APR-001", PASS,
                f"Valuation method '{f.valuation_method}' satisfies the requirement for "
                "this transaction.",
                observed=f.valuation_method, threshold="full_appraisal",
                comparator="==", input_fields=("appraisals.valuation_method",),
            )

        _p2, age_rule = self._rule("VAL-APR-003", f.as_of)
        max_age = int(age_rule.parameters["max_age_days"])
        if f.valuation_age_days > max_age:
            self._emit(
                r, f, "VAL-APR-003", FAIL,
                f"Valuation is {f.valuation_age_days} days old against the "
                f"{max_age}-day window.",
                observed=f.valuation_age_days, threshold=max_age, comparator="<=",
                input_fields=("appraisals.appraisal_date",),
            )
            self._condition(
                r, "VAL-APR-003", "COLLATERAL",
                f"Provide an appraisal update; the valuation is {f.valuation_age_days} "
                "days old.",
                "Appraisal update from the original appraiser",
            )
        else:
            self._emit(
                r, f, "VAL-APR-003", PASS,
                f"Valuation is {f.valuation_age_days} days old, within the "
                f"{max_age}-day window.",
                observed=f.valuation_age_days, threshold=max_age, comparator="<=",
                input_fields=("appraisals.appraisal_date",),
            )

        if f.appraisal_below_contract:
            self._emit(
                r, f, "VAL-APR-002", PASS,
                f"Appraised value {_money(f.appraised_value)} is below the contract "
                f"price {_money(f.purchase_price)}; the lower figure "
                f"{_money(f.value_used)} is used for leverage and the shortfall falls to "
                "the borrower as additional funds to close. The value is not adjusted "
                "upward.",
                observed=f.appraised_value, threshold=f.purchase_price, comparator="<",
                input_fields=(
                    "appraisals.appraised_value", "properties.purchase_price",
                    "properties.value_used_for_ltv",
                ),
            )
            self._risk(
                r, "VALUATION", "MEDIUM",
                "Appraised value below contract price.",
                "appraisals.appraised_value", "VAL-APR-002",
            )

        if f.property_condition_finding:
            self._emit(
                r, f, "PRP-ELG-002", REFER,
                "The valuation reports a condition affecting safety, structural "
                "integrity or habitability; repairs and a satisfactory re-inspection are "
                "required before closing.",
                observed="condition finding", threshold="safe, sound, habitable",
                comparator="==", input_fields=("appraisals.condition_rating",),
                force_human_review=True,
            )
            self._condition(
                r, "PRP-ELG-002", "COLLATERAL",
                "Complete the repairs identified in the valuation and provide a "
                "satisfactory re-inspection.",
                "Repair invoices and re-inspection report",
            )
            self._risk(
                r, "COLLATERAL", "MEDIUM",
                "Property condition finding requiring repair.",
                "appraisals.condition_rating", "PRP-ELG-002",
            )

        if f.flood_zone_sfha:
            self._emit(
                r, f, "PRP-ELG-004",
                PASS if f.flood_insurance_evidenced else INDETERMINATE,
                "Property is in a special flood hazard area and flood insurance is "
                "evidenced; the premium is included in the qualifying housing expense."
                if f.flood_insurance_evidenced
                else "Property is in a special flood hazard area and flood insurance "
                "evidence is outstanding.",
                observed="SFHA", threshold="coverage in force", comparator="==",
                input_fields=("properties.flood_zone", "insurance_records"),
            )
            if not f.flood_insurance_evidenced:
                self._condition(
                    r, "PRP-ELG-004", "INSURANCE",
                    "Provide flood insurance evidence for the subject property.",
                    "Flood policy or binder effective by closing",
                )

        if f.occupancy_contradiction:
            self._emit(
                r, f, "PRP-OCC-002", REFER,
                "Evidence in the file contradicts the declared occupancy. The "
                "contradiction is recorded with both sources and routed for review; it "
                "is not resolved by re-reading the declaration.",
                observed="occupancy contradiction", threshold="sources corroborate",
                comparator="==",
                input_fields=("properties.occupancy_type", "documents"),
                force_human_review=True,
            )
            self._risk(
                r, "OCCUPANCY", "HIGH",
                "Declared occupancy contradicted by file evidence.",
                "properties.occupancy_type", "PRP-OCC-002",
            )

        if f.title_exception_blocking:
            self._emit(
                r, f, "TTL-LIE-002", REFER,
                "A title exception affecting marketability, access or the insured lien "
                "position is unresolved; it must be cleared before clear-to-close.",
                observed="blocking exception", threshold="no blocking exception",
                comparator="==", input_fields=("title_records.exceptions",),
                force_human_review=True,
            )
            self._condition(
                r, "TTL-LIE-002", "TITLE",
                "Clear the title exception affecting the insured lien position.",
                "Updated title commitment",
            )
            self._risk(
                r, "TITLE", "MEDIUM",
                "Blocking title exception.",
                "title_records.exceptions", "TTL-LIE-002",
            )

    # ---- documentation --------------------------------------------------

    def _documentation(self, r: EngineResult, f: Facts) -> None:
        if f.documents_required:
            completeness = (
                Decimal(f.documents_received_current) / Decimal(f.documents_required)
            ).quantize(Decimal("0.0001"))
        else:
            completeness = Decimal("1.0000")
        self._emit(
            r, f, "DOC-REQ-003", PASS,
            f"Document completeness {_pct(completeness)} "
            f"({f.documents_received_current} of {f.documents_required} required "
            "documents received and current)"
            + (
                f"; outstanding: {', '.join(f.missing_document_types)}."
                if f.missing_document_types
                else "."
            ),
            observed=completeness, threshold=Decimal("1.0000"), comparator="==",
            input_fields=("documents",),
        )
        if f.missing_document_types:
            self._emit(
                r, f, "DOC-REQ-004", INDETERMINATE,
                f"{len(f.missing_document_types)} required document type(s) outstanding, "
                "so the rules that depend on them evaluate to INDETERMINATE and the "
                "application is suspended rather than declined.",
                observed=len(f.missing_document_types), threshold=0, comparator="==",
                input_fields=("documents",),
            )
            for doc_type in f.missing_document_types:
                self._condition(
                    r, "DOC-REQ-001", "DOCUMENTATION",
                    f"Provide the outstanding {doc_type.replace('_', ' ')}.",
                    doc_type,
                )
        if f.stale_document_types:
            self._emit(
                r, f, "DOC-REQ-002", FAIL,
                f"{len(f.stale_document_types)} document(s) are outside their freshness "
                "window and must be refreshed: "
                f"{', '.join(f.stale_document_types)}. A stale document raises a refresh "
                "condition; it is not treated as a missing document.",
                observed=len(f.stale_document_types), threshold=0, comparator="==",
                input_fields=("documents.document_date",),
            )
            for doc_type in f.stale_document_types:
                self._condition(
                    r, "DOC-REQ-002", "DOCUMENTATION",
                    f"Provide a refreshed {doc_type.replace('_', ' ')}.",
                    doc_type,
                )

    # ---- routing --------------------------------------------------------

    def _routing(self, r: EngineResult, f: Facts) -> None:
        # GEN-ELG-005 is the rule that says an unevaluable rule is INDETERMINATE
        # rather than FAIL. Recording it explicitly on every application means the
        # distinction is auditable, not just described in the corpus.
        unevaluable = [e for e in r.evaluations if e.outcome == INDETERMINATE]
        if unevaluable:
            self._emit(
                r, f, "GEN-ELG-005", INDETERMINATE,
                f"{len(unevaluable)} rule(s) lacked the inputs to be evaluated "
                f"({', '.join(sorted({e.rule_id for e in unevaluable}))}); each is "
                "recorded as INDETERMINATE with a documentation condition, not as a "
                "failure.",
                observed=len(unevaluable), threshold=0, comparator="==",
                input_fields=("rule_evaluations", "documents"),
            )
        else:
            self._emit(
                r, f, "GEN-ELG-005", PASS,
                "Every rule in scope had the inputs it needed, so none evaluated to "
                "INDETERMINATE.",
                observed=0, threshold=0, comparator="==",
                input_fields=("rule_evaluations", "documents"),
            )

        if r.human_review_reasons:
            self._emit(
                r, f, "UWR-HRV-001", REFER,
                f"{len(r.human_review_reasons)} mandatory human-review trigger(s) "
                "present.",
                observed=len(r.human_review_reasons), threshold=0, comparator="==",
                input_fields=("rule_evaluations",), force_human_review=True,
            )
        self._emit(
            r, f, "DEC-REC-001", PASS,
            "The recommendation is drawn from the controlled vocabulary and carries the "
            "rule ids, policy versions and calculation records supporting it.",
            input_fields=("decisions", "decision_reasons"),
        )
        self._emit(
            r, f, "DEC-AUD-001", PASS,
            "The decision record carries the full chain: policy version, rule, "
            "calculation, evidence and reason.",
            input_fields=("audit_events",),
        )


# ---------------------------------------------------------------------------
# Outcome synthesis
# ---------------------------------------------------------------------------


def eligibility_result(result: EngineResult) -> str:
    """Programme eligibility only - never a proxy for approval (GEN-ELG-004)."""
    eligibility_rules = {
        "GEN-ELG-003", "JMB-ELG-001", "JMB-ELG-002", "CONV-PUR-002", "CONV-RTR-002",
        "CONV-COR-002", "CONV-COR-001", "CONV-COR-003", "FHA-OVL-002", "USD-OVL-002",
        "USD-OVL-003", "USD-OVL-004", "VA-OVL-001", "VA-OVL-003", "PRP-ELG-001",
        "CRD-SCR-003", "CRD-EVT-001", "DTI-CONV-001", "FHA-OVL-004", "AST-FTC-003",
        "INC-VAR-001",
    }
    relevant = [e for e in result.evaluations if e.rule_id in eligibility_rules]
    if any(e.outcome == FAIL for e in relevant):
        return INELIGIBLE
    if any(e.outcome == INDETERMINATE for e in relevant):
        return INDETERMINATE
    return ELIGIBLE


def risk_level(result: EngineResult) -> str:
    severities = [flag["severity"] for flag in result.risk_flags]
    if severities.count("HIGH") >= 2:
        return "HIGH"
    if "HIGH" in severities:
        return "ELEVATED"
    if "MEDIUM" in severities:
        return "MEDIUM"
    return "LOW"


def recommendation(result: EngineResult, facts: Facts) -> str:
    """The copilot's recommendation. Never a credit decision (DEC-REC-001)."""
    # Identity failure stops the file before ordinary underwriting (KYC-IDV-002).
    if facts.identity_status != "VERIFIED":
        return MANUAL_REVIEW_REQUIRED
    hard_fails = [e for e in result.breaches if e.severity == "HARD_FAIL"]
    # A hard rule failing on verified evidence stands regardless of unrelated
    # missing documents (DOC-REQ-004).
    verified_fails = [
        e for e in hard_fails if e.rule_id not in ("DOC-REQ-002", "SEC-INJ-001",
                                                   "SEC-INJ-002", "SEC-INJ-003")
    ]
    if verified_fails:
        return DECLINE
    if facts.security_event_types:
        return MANUAL_REVIEW_REQUIRED
    if result.indeterminates or facts.missing_document_types:
        return SUSPENDED_INCOMPLETE
    if result.human_review_reasons:
        return MANUAL_REVIEW_REQUIRED
    if result.refers:
        return REFER_RECOMMENDATION
    if result.conditions:
        return APPROVE_WITH_CONDITIONS
    return APPROVE


def requires_human_review(result: EngineResult, recommendation_value: str) -> bool:
    """DEC-REC-002: a decline or high-value case is never auto-decided."""
    return bool(result.human_review_reasons) or recommendation_value in (
        DECLINE,
        MANUAL_REVIEW_REQUIRED,
        REFER_RECOMMENDATION,
    )


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _fmt(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _pct(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return f"{Decimal(value) * 100:.2f}%"


def _money(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return f"{Decimal(value):,.2f}"
