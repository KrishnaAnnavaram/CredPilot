"""
Policy definitions, part A: programme framework, product eligibility, credit,
liabilities and affordability.

Documents 01-13 of the corpus. See `policies.py` for the schema and for what each
`source_category` means. Rules that carry an enforced number are
SYNTHETIC_INTERNAL_POLICY unless the research report establishes the exact value as
a genuine public rule for the product and context.
"""

from __future__ import annotations

from datetime import date

from .policies import Policy, Rule

V1 = date(2026, 1, 1)
V2 = date(2026, 7, 1)

ALL_PRODUCTS = ("conventional_conforming", "jumbo", "fha", "va", "usda")
CONV = ("conventional_conforming",)
ALL_PURPOSES = ("purchase", "rate_term_refinance", "cash_out_refinance")
ALL_OCCUPANCY = ("primary_residence", "second_home", "investment")

RESEARCH = (
    "Completed research report, `synthetic_data/research/deep-research-report.md`"
)


# ---------------------------------------------------------------------------
# 01 - General mortgage eligibility framework
# ---------------------------------------------------------------------------

POL_GEN_001 = Policy(
    policy_id="POL-GEN-001",
    title="General Mortgage Eligibility and Programme Framework",
    version="1.0",
    effective_date=V1,
    family="general-eligibility",
    priority=10,
    product_scope=ALL_PRODUCTS,
    purpose="Establishes the authority layers, the decision vocabulary and the "
    "order of evaluation that every other policy in this corpus depends on. It is "
    "the document a retrieval agent should reach for when it needs to know what "
    "kind of statement it is looking at, rather than a specific threshold.",
    scope_note="Applies to every application in every programme. Where a "
    "programme-specific document states a different requirement, the "
    "programme-specific document governs for that programme only, and this document "
    "continues to govern the vocabulary and the order of evaluation.",
    definitions=(
        (
            "Authority layer",
            "Where a requirement comes from. Five layers are recognised: regulatory, "
            "agency or investor, publicly published lender guidance, common industry "
            "practice, and this lender's own synthetic internal policy. A requirement "
            "may never be presented at a higher layer than its actual source.",
        ),
        (
            "Declared, verified and qualifying value",
            "Three distinct values that must be preserved separately. Declared is what "
            "the applicant stated. Verified is what authoritative evidence established. "
            "Qualifying is the value underwriting is permitted to use. A borrower may "
            "declare 9,000 of monthly income, verify 8,700, and qualify on 8,250; "
            "overwriting all three with one figure destroys the audit trail.",
        ),
        (
            "As-of date",
            "The underwriting decision date used to select which policy version "
            "applies. It is not the date the question is asked.",
        ),
        (
            "Eligibility",
            "Whether the loan satisfies a defined programme rule set. Eligibility is "
            "never a synonym for approval.",
        ),
    ),
    rules=(
        Rule(
            rule_id="GEN-ELG-001",
            title="Order of evaluation",
            source_category="COMMON_INDUSTRY_PRACTICE",
            severity="ADVISORY",
            outcome_type="PROCESS",
            statement=(
                "Applications are evaluated in a fixed order: authorise access to the "
                "case; establish product, purpose, occupancy and the underwriting "
                "as-of date; retrieve the policy versions in force on that date; "
                "extract and verify evidence; detect conflicts between sources; run "
                "deterministic calculations; run deterministic eligibility rules; "
                "screen for risk; apply the human-review routing policy; and only then "
                "produce a recommendation with its citations. A component that "
                "produces a recommendation before the calculations have run has not "
                "followed this policy."
            ),
            research_reference=(
                RESEARCH + ", 'Agentic AI architecture mapping' - safe orchestration "
                "sequence."
            ),
            cross_refs=("POL-UWR-001", "POL-DEC-001"),
        ),
        Rule(
            rule_id="GEN-ELG-002",
            title="Applicable policy version is selected by as-of date",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The rule set applied to an application is the set of policy versions "
                "whose effective window contains the application's underwriting as-of "
                "date. Retrieving the most recently published version of a policy is a "
                "policy-selection defect whenever an earlier version was still in force "
                "on that date. A decision that cites a version not in force on the "
                "as-of date is not supportable and must be re-evaluated."
            ),
            parameters={
                "selection_basis": "underwriting_as_of_date",
                "fallback_when_before_first_version": "earliest published version, flagged",
            },
            evidence=("Policy front matter effective_date and expiration_date",),
            research_reference=(
                RESEARCH + ", 'Policy-document architecture' - the corpus must answer "
                "'what policy was applicable on the underwriting decision date?'."
            ),
            cross_refs=("POL-DOC-001",),
        ),
        Rule(
            rule_id="GEN-ELG-003",
            title="Loan amount must be within the programme's applicable limit",
            source_category="AGENCY_INVESTOR",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "A loan offered as conventional conforming must not exceed the "
                "applicable one-unit conforming limit for its area. For 2026 the "
                "published baseline one-unit conforming limit is 832,750 and the "
                "high-cost area ceiling is 1,249,125; the published 2026 FHA one-unit "
                "floor is 541,287 against the same high-cost ceiling. These are "
                "programme and geography reference points published by FHFA and HUD. "
                "They are not a generic maximum mortgage, and a loan above the "
                "conforming limit is not ineligible - it is simply not conforming, and "
                "must be executed under a different programme."
            ),
            parameters={
                "conforming_baseline_one_unit_2026": 832750,
                "high_cost_ceiling_one_unit_2026": 1249125,
                "fha_floor_one_unit_2026": 541287,
            },
            research_reference=(
                RESEARCH + ", 'Executive summary and research frame' - FHFA 2026 "
                "conforming limits and HUD 2026 FHA limits."
            ),
            cross_refs=("POL-CONV-001", "POL-JUMBO-001"),
        ),
        Rule(
            rule_id="GEN-ELG-004",
            title="Eligibility, risk, recommendation and credit decision are distinct",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PROCESS",
            statement=(
                "Five results must be recorded separately and must never be collapsed "
                "into one another: the eligibility determination against a programme "
                "rule set; the risk assessment; the copilot's underwriting "
                "recommendation; the authorised human credit decision; and the "
                "clear-to-close or funding decision. A loan can be programme-eligible "
                "and still be declined for creditworthiness; a strong borrower can be "
                "ineligible for one product configuration and eligible for another. An "
                "automated component may produce the first three. It may not produce "
                "the last two."
            ),
            parameters={
                "eligibility_values": "ELIGIBLE, INELIGIBLE, INDETERMINATE",
                "recommendation_values": (
                    "APPROVE_RECOMMENDATION, APPROVE_WITH_CONDITIONS, REFER, "
                    "MANUAL_REVIEW_REQUIRED, SUSPENDED_INCOMPLETE, DECLINE_RECOMMENDATION"
                ),
                "human_only_values": "CLEAR_TO_CLOSE, credit decision, funding decision",
            },
            research_reference=RESEARCH + ", 'Decision taxonomy'.",
            cross_refs=("POL-DEC-001", "POL-UWR-001"),
        ),
        Rule(
            rule_id="GEN-ELG-005",
            title="Missing evidence yields INDETERMINATE, not a negative result",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Every rule evaluates to exactly one of PASS, FAIL, REFER, "
                "NOT_APPLICABLE or INDETERMINATE. A rule whose inputs are missing or "
                "unverified evaluates to INDETERMINATE and raises a documentation "
                "condition. It does not evaluate to FAIL. Treating absent evidence as "
                "a failure converts a curable processing gap into an adverse outcome "
                "the file does not support."
            ),
            parameters={"outcomes": "PASS, FAIL, REFER, NOT_APPLICABLE, INDETERMINATE"},
            condition_template=(
                "Provide the evidence identified for rule {rule_id} so the rule can be "
                "evaluated."
            ),
            research_reference=(
                RESEARCH + ", 'Eligibility rule taxonomy' - INDETERMINATE is "
                "particularly important for missing evidence."
            ),
            cross_refs=("POL-DOC-001", "POL-UWR-001"),
        ),
        Rule(
            rule_id="GEN-ELG-006",
            title="Ability to repay must be established from verified information",
            source_category="REGULATORY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "A covered residential mortgage requires a reasonable, good-faith "
                "determination of the consumer's ability to repay, made from verified "
                "information about income or assets, obligations, and a measure such as "
                "debt-to-income or residual income. This is a regulatory obligation "
                "under TILA / Regulation Z and it sits above every product rule in this "
                "corpus: satisfying an investor's DTI matrix does not by itself "
                "discharge it."
            ),
            evidence=(
                "Verified income and asset records",
                "Verified obligation records",
                "The committed affordability calculation and its inputs",
            ),
            research_reference=(
                RESEARCH + ", 'Regulatory and agency landscape' - CFPB Regulation Z "
                "12 CFR 1026.43 ability-to-repay standards."
            ),
            cross_refs=("POL-DTI-001",),
        ),
    ),
    documentation=(
        "Every rule evaluation records the rule id, the policy version, the input "
        "values it consumed and the resulting outcome.",
        "Every decision records which rule evaluations supported it.",
    ),
    related_policies=(
        "POL-CONV-001 for the base conventional product",
        "POL-DEC-001 for decision and adverse-action handling",
        "POL-UWR-001 for conditions, manual review and exception authority",
    ),
    version_note="Initial framework version.",
)


# ---------------------------------------------------------------------------
# 02 - Conventional conforming purchase
# ---------------------------------------------------------------------------

POL_CONV_001 = Policy(
    policy_id="POL-CONV-001",
    title="Conventional Conforming Purchase Eligibility",
    version="1.0",
    effective_date=V1,
    family="conventional-purchase",
    priority=30,
    product_scope=CONV,
    purpose_scope=("purchase",),
    purpose="Defines eligibility for the lender's core product: a conventional "
    "conforming, fixed-rate, one-to-four-unit purchase mortgage. This is the "
    "programme most applications are underwritten against, and the one whose "
    "leverage and occupancy rules the other product documents vary from.",
    scope_note="Purchase transactions only. Refinances are governed by POL-CONV-002 "
    "and POL-CONV-003. Loan amounts above the applicable conforming limit are not "
    "eligible under this document and are routed to POL-JUMBO-001.",
    definitions=(
        (
            "Conforming",
            "A loan whose amount is at or below the applicable one-unit conforming "
            "limit for the property's area, and which meets the other requirements of "
            "this document. 'Conforming' describes the execution, not the borrower.",
        ),
        (
            "Value used for leverage",
            "For a purchase, the lower of the contract sales price and the appraised "
            "or otherwise accepted value. An appraisal that comes in below the contract "
            "price therefore raises the loan-to-value ratio; it does not change the "
            "price the borrower agreed to pay.",
        ),
    ),
    rules=(
        Rule(
            rule_id="CONV-PUR-001",
            title="Eligible transaction characteristics",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "An eligible transaction under this document is a first-lien purchase "
                "of a one-to-four-unit residential property, on a fixed-rate "
                "fully-amortising note with a term of 120 to 360 months, where the "
                "borrower occupies the property as a primary residence, second home or "
                "declared investment property. Manufactured housing, properties above "
                "four units, and mixed commercial use are outside this document and "
                "require the collateral review in POL-PRP-001."
            ),
            parameters={
                "unit_count_min": 1,
                "unit_count_max": 4,
                "term_months_min": 120,
                "term_months_max": 360,
                "lien_position": 1,
                "amortisation": "fully amortising, fixed rate",
            },
            cross_refs=("POL-PRP-001", "POL-PRP-002"),
        ),
        Rule(
            rule_id="CONV-PUR-002",
            title="Maximum leverage by occupancy",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Loan-to-value is computed against the value used for leverage and must "
                "not exceed the limit for the declared occupancy. Combined "
                "loan-to-value, which adds every subordinate lien, is capped at the same "
                "figure as loan-to-value for second homes and investment property, and "
                "five percentage points higher for a primary residence to accommodate "
                "eligible community-second financing. These figures are this lender's "
                "own synthetic leverage matrix; they are not an agency matrix."
            ),
            parameters={
                "max_ltv_primary_residence": 0.97,
                "max_ltv_second_home": 0.90,
                "max_ltv_investment": 0.85,
                "max_cltv_primary_residence": 1.02,
                "max_cltv_second_home": 0.90,
                "max_cltv_investment": 0.85,
            },
            evidence=("Appraisal or accepted valuation", "Executed purchase agreement"),
            cross_refs=("POL-VAL-001", "POL-AST-002"),
            research_reference=(
                RESEARCH + ", 'Underwriting calculations' - purchase LTV uses the lower "
                "of sales price or appraised value; the thresholds themselves are "
                "synthetic."
            ),
        ),
        Rule(
            rule_id="CONV-PUR-003",
            title="Mortgage insurance is required above 80 percent leverage",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "A loan with a loan-to-value ratio above 80 percent requires mortgage "
                "insurance, and the insurance premium must be included in the qualifying "
                "housing expense. Coverage is expressed as a monthly factor applied to "
                "the loan amount; the factor rises as leverage rises. Omitting the "
                "premium from the housing expense understates the debt-to-income ratio "
                "and is a calculation defect, not a rounding difference."
            ),
            parameters={
                "mi_required_above_ltv": 0.80,
                "annual_factor_ltv_80_to_85": 0.0032,
                "annual_factor_ltv_85_to_90": 0.0052,
                "annual_factor_ltv_90_to_95": 0.0078,
                "annual_factor_ltv_above_95": 0.0094,
            },
            condition_template=(
                "Provide evidence of mortgage insurance meeting the coverage required "
                "at {ltv_pct} loan-to-value."
            ),
            cross_refs=("POL-DTI-001",),
        ),
        Rule(
            rule_id="CONV-PUR-004",
            title="Minimum borrower contribution",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "On a primary residence the entire down payment may come from eligible "
                "gift funds. On a second home or investment property the borrower must "
                "contribute at least five percent of the purchase price from the "
                "borrower's own verified funds before gift funds are applied. Gift "
                "eligibility itself, including who may be a donor, is governed by "
                "POL-AST-004."
            ),
            parameters={
                "min_own_funds_pct_primary_residence": 0.00,
                "min_own_funds_pct_second_home": 0.05,
                "min_own_funds_pct_investment": 0.05,
            },
            research_reference=(
                RESEARCH + ", 'Asset model' - agency gift eligibility differs by "
                "occupancy and purpose; the percentages here are synthetic."
            ),
            cross_refs=("POL-AST-004",),
        ),
        Rule(
            rule_id="CONV-PUR-005",
            title="Interested-party contributions are limited",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Seller and other interested-party credits toward the borrower's "
                "closing costs are limited by leverage. Credits above the limit are not "
                "disallowed outright: the excess is applied as a reduction to the sales "
                "price, which changes the value used for leverage and therefore requires "
                "the leverage calculation to be re-run."
            ),
            parameters={
                "max_ipc_pct_ltv_above_90": 0.03,
                "max_ipc_pct_ltv_75_to_90": 0.06,
                "max_ipc_pct_ltv_at_or_below_75": 0.09,
                "excess_treatment": "reduce sales price and recompute LTV",
            },
            cross_refs=("POL-AST-002",),
        ),
    ),
    documentation=(
        "Executed purchase agreement including price, parties, concessions and dates.",
        "Appraisal or an accepted alternative valuation under POL-VAL-001.",
        "Evidence of mortgage insurance where CONV-PUR-003 requires it.",
    ),
    related_policies=(
        "POL-GEN-001 for the programme limit and the decision vocabulary",
        "POL-DTI-001 for affordability",
        "POL-AST-002 for funds to close",
    ),
    version_note="Initial product version.",
)


# ---------------------------------------------------------------------------
# 03 - Conventional rate/term refinance
# ---------------------------------------------------------------------------

POL_CONV_002 = Policy(
    policy_id="POL-CONV-002",
    title="Conventional Rate and Term Refinance Eligibility",
    version="1.0",
    effective_date=V1,
    family="conventional-rate-term-refinance",
    priority=30,
    product_scope=CONV,
    purpose_scope=("rate_term_refinance",),
    purpose="Defines eligibility for a limited-cash-out refinance that replaces "
    "existing mortgage debt without meaningful equity extraction. The distinguishing "
    "feature of this product is the denominator used for leverage and the strict "
    "limit on cash returned to the borrower.",
    scope_note="Applies where the new loan pays off an existing first lien and, "
    "optionally, an eligible seasoned subordinate lien, and the borrower receives no "
    "more than the incidental cash permitted below. Any transaction exceeding that "
    "limit is a cash-out refinance under POL-CONV-003 regardless of how it was "
    "described at application.",
    definitions=(
        (
            "Value used for leverage on a refinance",
            "The appraised or otherwise accepted current value of the property. There "
            "is no sales price in a refinance, so the purchase convention of taking the "
            "lower of two figures does not apply.",
        ),
        (
            "Incidental cash",
            "Cash returned to the borrower at closing that arises from rounding the new "
            "loan amount and from escrow or prepaid adjustments, rather than from an "
            "intent to extract equity.",
        ),
    ),
    rules=(
        Rule(
            rule_id="CONV-RTR-001",
            title="Cash returned to the borrower is capped",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Cash returned to the borrower at closing must not exceed the lesser of "
                "one percent of the new loan amount or 2,000. A transaction that returns "
                "more than this is a cash-out refinance and must be re-underwritten "
                "under POL-CONV-003, which applies lower leverage limits and a different "
                "credit standard. Re-labelling the transaction without re-running the "
                "leverage and credit rules is a policy-selection defect."
            ),
            parameters={
                "max_incidental_cash_pct_of_loan": 0.01,
                "max_incidental_cash_amount": 2000,
                "reclassification_target": "POL-CONV-003",
            },
            cross_refs=("POL-CONV-003",),
        ),
        Rule(
            rule_id="CONV-RTR-002",
            title="Maximum leverage on a rate and term refinance",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Loan-to-value is computed against the current accepted value and must "
                "not exceed the occupancy limit below. Where an existing subordinate "
                "lien is to remain in place rather than be paid off, the combined "
                "loan-to-value test governs and the subordinate payment is included in "
                "the qualifying housing expense."
            ),
            parameters={
                "max_ltv_primary_residence": 0.95,
                "max_ltv_second_home": 0.90,
                "max_ltv_investment": 0.75,
                "max_cltv_primary_residence": 0.95,
            },
            research_reference=(
                RESEARCH + ", 'Underwriting calculations' - refinance LTV uses a "
                "different denominator from purchase; the thresholds are synthetic."
            ),
            cross_refs=("POL-VAL-001",),
        ),
        Rule(
            rule_id="CONV-RTR-003",
            title="Existing mortgage payment history",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "The mortgage being refinanced must show no payment 30 or more days "
                "past due in the most recent 12 months. A single 30-day late in that "
                "window routes the file to an underwriter rather than failing it, "
                "because the surrounding circumstances determine whether the history is "
                "acceptable. Two or more such lates in the window is a hard failure "
                "under this product."
            ),
            parameters={
                "lookback_months": 12,
                "lates_30d_refer_at": 1,
                "lates_30d_fail_at": 2,
            },
            evidence=("Credit report mortgage tradeline", "Mortgage payment history"),
            requires_human_review=True,
            cross_refs=("POL-CRD-003",),
        ),
        Rule(
            rule_id="CONV-RTR-004",
            title="Payoff figure must be evidenced",
            source_category="COMMON_INDUSTRY_PRACTICE",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "The new loan amount must be supported by a current payoff statement "
                "for each lien being retired. Where the payoff statement postdates the "
                "loan amount used in the calculations, the funds-to-close calculation "
                "must be re-run, because the difference falls to the borrower."
            ),
            evidence=("Payoff statement dated within the freshness window in POL-DOC-001",),
            condition_template="Provide a current payoff statement for lien {lien_id}.",
            cross_refs=("POL-AST-002", "POL-DOC-001"),
        ),
    ),
    documentation=(
        "Current payoff statement for each lien being retired.",
        "Evidence of the existing note terms where the benefit test is relied upon.",
        "Appraisal or accepted alternative valuation.",
    ),
    related_policies=("POL-CONV-003", "POL-VAL-001", "POL-CRD-003"),
    version_note="Initial product version.",
)


# ---------------------------------------------------------------------------
# 04 - Cash-out refinance
# ---------------------------------------------------------------------------

POL_CONV_003 = Policy(
    policy_id="POL-CONV-003",
    title="Cash-Out Refinance Eligibility",
    version="1.0",
    effective_date=V1,
    family="cash-out-refinance",
    priority=30,
    product_scope=CONV,
    purpose_scope=("cash_out_refinance",),
    purpose="Defines eligibility where the borrower extracts equity. Because the "
    "borrower's equity position falls at closing rather than rising, this product "
    "applies lower leverage limits, a higher credit floor and a reserve requirement "
    "that the rate and term product does not.",
    scope_note="Applies to any refinance returning more cash to the borrower than "
    "CONV-RTR-001 permits, and to any refinance paying off a subordinate lien that "
    "was not itself used to acquire the property.",
    definitions=(
        (
            "Seasoning",
            "The elapsed time since the borrower acquired the property or since the "
            "most recent cash-out refinance of it, measured to the application date.",
        ),
    ),
    rules=(
        Rule(
            rule_id="CONV-COR-001",
            title="Ownership seasoning",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The borrower must have held title to the property for at least six "
                "months before the application date, and at least 12 months must have "
                "elapsed since any prior cash-out refinance of the same property. "
                "Inherited property and property awarded by a court order are exempt "
                "from the six-month test on documentation of the transfer."
            ),
            parameters={
                "min_ownership_months": 6,
                "min_months_since_prior_cash_out": 12,
            },
            exception=(
                "Inheritance or a legal award transfers the seasoning clock to the "
                "prior owner's acquisition date when the transfer is documented."
            ),
            evidence=("Title evidence showing the acquisition date",),
            cross_refs=("POL-TTL-001",),
        ),
        Rule(
            rule_id="CONV-COR-002",
            title="Maximum leverage on a cash-out refinance",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Loan-to-value on a cash-out refinance must not exceed the occupancy "
                "limit below, measured against the current accepted value. These limits "
                "sit materially below the equivalent purchase limits because equity is "
                "leaving the transaction."
            ),
            parameters={
                "max_ltv_primary_residence": 0.80,
                "max_ltv_second_home": 0.75,
                "max_ltv_investment": 0.70,
                "max_cltv_primary_residence": 0.80,
            },
            cross_refs=("POL-VAL-001",),
        ),
        Rule(
            rule_id="CONV-COR-003",
            title="Elevated credit floor",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The representative credit score for a cash-out refinance must be at "
                "least 680, or at least 700 where loan-to-value exceeds 75 percent. "
                "This floor sits above the general credit floor in POL-CRD-001 and "
                "governs where the two differ."
            ),
            parameters={
                "min_representative_score": 680,
                "min_representative_score_ltv_above_75": 700,
                "ltv_trigger": 0.75,
            },
            cross_refs=("POL-CRD-001",),
        ),
        Rule(
            rule_id="CONV-COR-004",
            title="Reserve requirement",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "At least six months of the qualifying housing expense must remain "
                "available as reserves after closing. Cash proceeds from the "
                "transaction itself may not be counted toward this requirement, because "
                "counting the loan's own proceeds as the borrower's reserves would make "
                "the test circular."
            ),
            parameters={
                "min_months_reserves": 6,
                "proceeds_countable_as_reserves": False,
            },
            condition_template=(
                "Evidence reserves of at least {required_months} months of the "
                "qualifying housing expense from assets other than loan proceeds."
            ),
            cross_refs=("POL-AST-003",),
        ),
        Rule(
            rule_id="CONV-COR-005",
            title="Stated use of proceeds",
            source_category="COMMON_INDUSTRY_PRACTICE",
            severity="ADVISORY",
            outcome_type="PROCESS",
            statement=(
                "The borrower's stated use of proceeds is recorded for the file. It is "
                "context for the underwriter, not an eligibility test: a permissible use "
                "does not cure a leverage or credit failure, and an unusual use is not "
                "by itself a basis for an adverse outcome. Where the stated use "
                "contradicts other evidence in the file, the contradiction is a "
                "data-quality matter under POL-FRD-001."
            ),
            cross_refs=("POL-FRD-001",),
        ),
    ),
    documentation=(
        "Title evidence establishing the acquisition date.",
        "Payoff statements for every lien being retired.",
        "Asset evidence supporting the post-closing reserve requirement.",
    ),
    related_policies=("POL-CONV-002", "POL-AST-003", "POL-CRD-001"),
    version_note="Initial product version.",
)


# ---------------------------------------------------------------------------
# 05 - Jumbo overlay (two versions)
# ---------------------------------------------------------------------------

_JUMBO_RULES_COMMON = (
    Rule(
        rule_id="JMB-ELG-001",
        title="Definition of a jumbo transaction",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="HARD_FAIL",
        outcome_type="PASS_FAIL",
        statement=(
            "A transaction is jumbo under this document when the first-lien loan "
            "amount exceeds the applicable conforming limit recorded in GEN-ELG-003. "
            "A jumbo loan is not a conventional conforming loan with a larger number; "
            "it is a separate execution with its own leverage, reserve and review "
            "requirements, and it is never eligible for the conforming leverage matrix "
            "in POL-CONV-001."
        ),
        parameters={"trigger": "loan amount above the applicable conforming limit"},
        cross_refs=("POL-GEN-001", "POL-CONV-001"),
        research_reference=(
            RESEARCH + ", 'Product taxonomy' - jumbo criteria are dominated by "
            "proprietary lender and investor overlays that are not public, so this "
            "entire document is a fictional overlay."
        ),
    ),
    Rule(
        rule_id="JMB-ELG-004",
        title="Every jumbo file is reviewed by a human underwriter",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="REFER",
        outcome_type="PROCESS",
        statement=(
            "No jumbo application may reach a recommendation without human "
            "underwriting review, irrespective of how strong the file appears. The "
            "reason is explicit: real jumbo criteria are set by private investor "
            "overlays that are not publicly documented, so an automated component "
            "working from this synthetic overlay cannot be assumed to have applied the "
            "criteria a real investor would apply. The copilot may prepare the review "
            "package; it may not clear the file."
        ),
        requires_human_review=True,
        parameters={"human_review": "mandatory", "reason_code": "HR-JUMBO-EXPOSURE"},
        research_reference=(
            RESEARCH + ", 'Human-in-the-loop classification' - jumbo exposure is "
            "classified HUMAN REVIEW REQUIRED because internal overlays are not "
            "publicly known."
        ),
        cross_refs=("POL-UWR-001",),
    ),
)

POL_JUMBO_001_V1 = Policy(
    policy_id="POL-JUMBO-001",
    title="Jumbo and High-Value Mortgage Overlay",
    version="1.0",
    effective_date=V1,
    expiration_date=V2,
    superseded_by="POL-JUMBO-001 v2.0",
    family="jumbo-overlay",
    priority=25,
    product_scope=("jumbo",),
    requires_human_review=True,
    purpose="A fictional investor overlay for loan amounts above the applicable "
    "conforming limit. Real jumbo underwriting criteria are proprietary to the "
    "lenders and private investors that set them; nothing in this document should be "
    "read as describing any real institution's jumbo policy.",
    scope_note="Applies to first-lien transactions above the conforming limit, in "
    "addition to - not instead of - the credit, income, asset and property documents. "
    "Where this overlay is stricter, the overlay governs.",
    rules=_JUMBO_RULES_COMMON
    + (
        Rule(
            rule_id="JMB-ELG-002",
            title="Leverage and credit floor",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Loan-to-value must not exceed 80 percent on a primary residence and "
                "75 percent on any other occupancy, and the representative credit score "
                "must be at least 700."
            ),
            parameters={
                "max_ltv_primary_residence": 0.80,
                "max_ltv_other_occupancy": 0.75,
                "min_representative_score": 700,
            },
        ),
        Rule(
            rule_id="JMB-ELG-003",
            title="Reserve and documentation requirement",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "At least six months of the qualifying housing expense must remain "
                "available after closing, and every income source must be supported by "
                "full documentation. Reduced-documentation treatment is not available "
                "under this overlay."
            ),
            parameters={"min_months_reserves": 6, "documentation_level": "full"},
            cross_refs=("POL-AST-003", "POL-DOC-001"),
        ),
    ),
    documentation=(
        "Full documentation of every income source, with no reduced-documentation "
        "alternatives.",
        "Asset evidence covering both funds to close and the reserve requirement.",
    ),
    related_policies=("POL-CONV-001", "POL-UWR-001"),
    version_note=(
        "Original overlay. Superseded on 2026-07-01 by version 2.0, which tightens "
        "leverage and reserves and adds a second-appraisal trigger."
    ),
)

POL_JUMBO_001_V2 = Policy(
    policy_id="POL-JUMBO-001",
    title="Jumbo and High-Value Mortgage Overlay",
    version="2.0",
    effective_date=V2,
    supersedes="POL-JUMBO-001 v1.0",
    family="jumbo-overlay",
    priority=25,
    product_scope=("jumbo",),
    requires_human_review=True,
    purpose="A fictional investor overlay for loan amounts above the applicable "
    "conforming limit. Real jumbo underwriting criteria are proprietary to the "
    "lenders and private investors that set them; nothing in this document should be "
    "read as describing any real institution's jumbo policy.",
    scope_note="Applies to first-lien transactions above the conforming limit, in "
    "addition to - not instead of - the credit, income, asset and property documents. "
    "Where this overlay is stricter, the overlay governs.",
    rules=_JUMBO_RULES_COMMON
    + (
        Rule(
            rule_id="JMB-ELG-002",
            title="Leverage and credit floor",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Loan-to-value must not exceed 75 percent on a primary residence and "
                "70 percent on any other occupancy, and the representative credit score "
                "must be at least 720. Version 1.0 of this overlay permitted 80 percent "
                "and a 700 score; applications with an underwriting as-of date before "
                "2026-07-01 are still evaluated against those figures."
            ),
            parameters={
                "max_ltv_primary_residence": 0.75,
                "max_ltv_other_occupancy": 0.70,
                "min_representative_score": 720,
            },
        ),
        Rule(
            rule_id="JMB-ELG-003",
            title="Reserve and documentation requirement",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "At least nine months of the qualifying housing expense must remain "
                "available after closing, rising to 12 months where the loan amount "
                "exceeds 1,500,000. Every income source requires full documentation."
            ),
            parameters={
                "min_months_reserves": 9,
                "min_months_reserves_above_1_5m": 12,
                "loan_amount_tier_trigger": 1500000,
                "documentation_level": "full",
            },
            cross_refs=("POL-AST-003", "POL-DOC-001"),
        ),
        Rule(
            rule_id="JMB-ELG-005",
            title="Second valuation above a loan amount threshold",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "A loan amount above 1,500,000 requires a second independent valuation "
                "or a field review of the first. Where the two valuations differ by more "
                "than five percent, the lower value is used for leverage and the file is "
                "routed for collateral review."
            ),
            parameters={
                "second_valuation_above_loan_amount": 1500000,
                "variance_tolerance": 0.05,
                "resolution": "use the lower value and route for collateral review",
            },
            requires_human_review=True,
            cross_refs=("POL-VAL-001",),
        ),
    ),
    documentation=(
        "Full documentation of every income source.",
        "Asset evidence covering funds to close and the increased reserve requirement.",
        "A second valuation or field review where JMB-ELG-005 requires it.",
    ),
    related_policies=("POL-CONV-001", "POL-UWR-001", "POL-VAL-001"),
    version_note=(
        "Tightened leverage from 80 to 75 percent on a primary residence, raised the "
        "credit floor from 700 to 720, raised reserves from six to nine months and "
        "introduced the second-valuation trigger JMB-ELG-005."
    ),
)


# ---------------------------------------------------------------------------
# 06-08 - Government programme overlays
# ---------------------------------------------------------------------------

POL_FHA_001 = Policy(
    policy_id="POL-FHA-001",
    title="FHA-Style Programme Overlay",
    version="1.0",
    effective_date=V1,
    family="fha-overlay",
    priority=28,
    product_scope=("fha",),
    purpose="A synthetic overlay for government-insured lending modelled on the "
    "structure of an FHA-style programme. It reproduces the shape of the programme - "
    "an up-front and an annual insurance premium, lower leverage tolerance for weaker "
    "credit, and a separate property standard - without restating any provision of "
    "HUD Handbook 4000.1, which is the authoritative source for real FHA lending.",
    scope_note="Applies to applications submitted under the synthetic government "
    "programme. Where a rule here conflicts with the conventional documents, this "
    "overlay governs for these applications only.",
    rules=(
        Rule(
            rule_id="FHA-OVL-001",
            title="Authority and what this document is not",
            source_category="AGENCY_INVESTOR",
            severity="ADVISORY",
            outcome_type="PROCESS",
            statement=(
                "The authoritative source for real FHA single-family origination and "
                "underwriting is HUD's consolidated Single Family Housing Policy "
                "Handbook 4000.1. This document does not restate it, does not reproduce "
                "the TOTAL scorecard, and must never be cited as though it were HUD "
                "policy. Every numeric threshold below is this lender's synthetic "
                "overlay."
            ),
            research_reference=(
                RESEARCH + ", source ledger entry 23 - HUD Handbook 4000.1, August 2026 "
                "update, is the authoritative FHA source."
            ),
        ),
        Rule(
            rule_id="FHA-OVL-002",
            title="Leverage by credit band",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Maximum loan-to-value is set by the representative credit score band. "
                "A score of 580 or above supports up to 96.5 percent; a score from 500 "
                "to 579 supports up to 90 percent; below 500 the programme is not "
                "available. The score bands are structural to this kind of programme; "
                "the exact figures here are synthetic."
            ),
            parameters={
                "max_ltv_score_580_plus": 0.965,
                "max_ltv_score_500_to_579": 0.90,
                "min_representative_score": 500,
            },
            cross_refs=("POL-CRD-001",),
        ),
        Rule(
            rule_id="FHA-OVL-003",
            title="Insurance premiums enter the housing expense",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="CALCULATION",
            statement=(
                "An up-front insurance premium is financed into the loan amount and an "
                "annual premium is collected monthly. The monthly premium is part of the "
                "qualifying housing expense, and the financed up-front premium increases "
                "the loan amount used in the payment calculation but is excluded from "
                "the loan-to-value test, which is measured against the base loan amount."
            ),
            parameters={
                "upfront_premium_pct_of_base_loan": 0.0175,
                "annual_premium_pct_of_loan": 0.0055,
                "upfront_premium_financed": True,
                "ltv_measured_against": "base loan amount before financed premium",
            },
            cross_refs=("POL-DTI-001",),
        ),
        Rule(
            rule_id="FHA-OVL-004",
            title="Affordability tolerance with compensating factors",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Back-end debt-to-income must not exceed 43 percent, extended to 50 "
                "percent where at least two documented compensating factors are present "
                "and recorded by name. The compensating factors recognised are: verified "
                "reserves of at least three months beyond the programme requirement; a "
                "residual income at or above 1,500 per month; no payment 30 or more days "
                "past due in 24 months; and a proposed housing payment no greater than "
                "the borrower's current housing payment."
            ),
            parameters={
                "max_back_end_dti": 0.43,
                "max_back_end_dti_with_factors": 0.50,
                "min_compensating_factors": 2,
            },
            cross_refs=("POL-DTI-001",),
        ),
    ),
    documentation=(
        "Evidence of programme eligibility for the borrower and the property.",
        "Documentation of each compensating factor relied upon by FHA-OVL-004.",
    ),
    related_policies=("POL-DTI-001", "POL-CRD-001", "POL-PRP-001"),
    version_note="Initial overlay version.",
)


POL_VA_001 = Policy(
    policy_id="POL-VA-001",
    title="VA-Style Programme Overlay",
    version="1.0",
    effective_date=V1,
    family="va-overlay",
    priority=28,
    product_scope=("va",),
    purpose="A synthetic overlay for a guaranty-style programme for eligible "
    "service members and veterans, modelled on the structure of VA lending: an "
    "entitlement certificate, a residual-income test that sits alongside "
    "debt-to-income, occupancy requirements, and no monthly mortgage insurance.",
    scope_note="Applies to applications under the synthetic guaranty programme. VA's "
    "own standards, and the fact that lenders may impose additional standards of "
    "their own, are described in VA's published guidance; this overlay is the "
    "lender-side standard only.",
    rules=(
        Rule(
            rule_id="VA-OVL-001",
            title="Programme eligibility rests on an entitlement certificate",
            source_category="AGENCY_INVESTOR",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Programme eligibility is established by a certificate of eligibility "
                "evidencing entitlement, not by the lender's own assessment. A borrower "
                "must meet both the programme's standards and the lender's own credit "
                "and income standards; published VA guidance is explicit that lenders "
                "may impose additional standards. Satisfying the guaranty programme is "
                "therefore not equivalent to qualifying for the loan."
            ),
            evidence=("Certificate of eligibility evidencing available entitlement",),
            research_reference=(
                RESEARCH + ", 'Product taxonomy' - VA makes the investor versus lender "
                "distinction explicit."
            ),
            condition_template="Provide a current certificate of eligibility.",
        ),
        Rule(
            rule_id="VA-OVL-002",
            title="No down payment and no monthly mortgage insurance",
            source_category="AGENCY_INVESTOR",
            severity="ADVISORY",
            outcome_type="PROCESS",
            statement=(
                "Purchase transactions under this programme can commonly be made with "
                "no down payment and carry no monthly mortgage insurance. That structural "
                "feature is not a statement that every applicant qualifies: the "
                "residual-income and credit tests below still apply, and a funding fee "
                "may be financed into the loan amount."
            ),
            parameters={
                "min_down_payment_pct": 0.00,
                "max_ltv": 1.00,
                "monthly_mortgage_insurance": False,
                "funding_fee_pct_financed": 0.023,
            },
            research_reference=(
                RESEARCH + ", 'Product taxonomy' - VA purchase loans can often be made "
                "without a down payment and do not require PMI or MIP."
            ),
        ),
        Rule(
            rule_id="VA-OVL-003",
            title="Residual income test",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Monthly income remaining after the proposed housing expense and all "
                "recurring obligations must meet the residual-income floor for the "
                "household size. Back-end debt-to-income above 41 percent is permitted "
                "only where residual income exceeds that floor by at least 20 percent; "
                "below that cushion the guideline governs. This test therefore replaces "
                "the general affordability ceiling for this programme rather than sitting "
                "alongside it, and a file that every other programme would measure only "
                "as a ratio can fail here on the absolute amount left over. The figures "
                "are synthetic; the concept of a residual income standard is genuine to "
                "this kind of programme."
            ),
            parameters={
                "residual_income_floor_household_1": 500,
                "residual_income_floor_household_2": 840,
                "residual_income_floor_household_3": 1000,
                "residual_income_floor_household_4_plus": 1180,
                "max_back_end_dti_without_residual_cushion": 0.41,
                "residual_cushion_multiple_above_guideline": 1.20,
            },
            cross_refs=("POL-DTI-001",),
        ),
        Rule(
            rule_id="VA-OVL-004",
            title="Occupancy certification",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The borrower must certify intent to occupy the property as a primary "
                "residence within 60 days of closing. Investment occupancy is not "
                "eligible under this programme, and an occupancy declaration that "
                "conflicts with other evidence in the file is escalated under "
                "POL-PRP-002 rather than resolved by the declaration alone."
            ),
            parameters={
                "occupancy_required": "primary_residence",
                "occupancy_deadline_days": 60,
            },
            cross_refs=("POL-PRP-002",),
        ),
    ),
    documentation=(
        "Certificate of eligibility.",
        "Household-size evidence where the residual-income floor depends on it.",
        "Signed occupancy certification.",
    ),
    related_policies=("POL-DTI-001", "POL-PRP-002"),
    version_note="Initial overlay version.",
)


POL_USDA_001 = Policy(
    policy_id="POL-USDA-001",
    title="USDA-Style Rural Programme Overlay",
    version="1.0",
    effective_date=V1,
    family="usda-overlay",
    priority=28,
    product_scope=("usda",),
    occupancy_scope=("primary_residence",),
    purpose_scope=("purchase", "rate_term_refinance"),
    purpose="A synthetic overlay for a guaranteed rural-housing programme modelled "
    "on the structure of a Section 502 guaranteed loan: property must be in an "
    "eligible area, household income must be within a programme limit, occupancy must "
    "be a primary residence, and the programme permits full financing.",
    scope_note="Applies to applications under the synthetic rural programme. The "
    "authoritative source for real USDA guaranteed lending is USDA Rural "
    "Development's own programme guidance and handbook.",
    rules=(
        Rule(
            rule_id="USD-OVL-001",
            title="Property and occupancy eligibility",
            source_category="AGENCY_INVESTOR",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The property must be located in an area the programme designates as "
                "eligible and must be occupied by the borrower as a primary residence. "
                "Area eligibility is a programme determination keyed to the property "
                "address; it is not a judgement the underwriter or an automated "
                "component may make from the address alone."
            ),
            evidence=("Programme area-eligibility determination for the property address",),
            condition_template=(
                "Obtain the programme area-eligibility determination for the subject "
                "property."
            ),
            research_reference=(
                RESEARCH + ", 'Product taxonomy' - USDA Section 502 Guaranteed serves "
                "eligible rural primary residences."
            ),
        ),
        Rule(
            rule_id="USD-OVL-002",
            title="Household income limit",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Adjusted household income must not exceed the programme limit for the "
                "area and household size. Household income here counts every adult "
                "member of the household, which is a broader measure than the qualifying "
                "income used for the debt-to-income calculation. The two measures serve "
                "different purposes and must both be recorded."
            ),
            parameters={
                "income_limit_household_1_to_4": 121500,
                "income_limit_household_5_plus": 160400,
                "income_basis": "adjusted household income, all adult members",
            },
            cross_refs=("POL-INC-001",),
        ),
        Rule(
            rule_id="USD-OVL-003",
            title="Full financing and guarantee fees",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="ADVISORY",
            outcome_type="CALCULATION",
            statement=(
                "The programme permits financing of the full accepted value, with an "
                "up-front guarantee fee financed into the loan and an annual fee "
                "collected monthly as part of the housing expense. The annual fee is "
                "included in the qualifying housing expense in the same way mortgage "
                "insurance is under CONV-PUR-003."
            ),
            parameters={
                "max_ltv": 1.00,
                "upfront_guarantee_fee_pct": 0.01,
                "annual_fee_pct_of_loan": 0.0035,
            },
            cross_refs=("POL-DTI-001",),
        ),
        Rule(
            rule_id="USD-OVL-004",
            title="Affordability ceiling",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Housing expense ratio must not exceed 34 percent and back-end "
                "debt-to-income must not exceed 44 percent. This programme is one of the "
                "few in this corpus where the housing ratio is a hard test rather than an "
                "advisory measure."
            ),
            parameters={"max_front_end_dti": 0.34, "max_back_end_dti": 0.44},
            cross_refs=("POL-DTI-001",),
        ),
    ),
    documentation=(
        "Programme area-eligibility determination.",
        "Household income documentation for every adult household member.",
    ),
    related_policies=("POL-DTI-001", "POL-INC-001"),
    version_note="Initial overlay version.",
)


# ---------------------------------------------------------------------------
# 09 - Credit assessment (two versions)
# ---------------------------------------------------------------------------

_CRD_COMMON = (
    Rule(
        rule_id="CRD-SCR-001",
        title="A credit report must be obtained for a permissible purpose",
        source_category="REGULATORY",
        severity="HARD_FAIL",
        outcome_type="PASS_FAIL",
        statement=(
            "A consumer report may be obtained only for a permissible purpose under "
            "the Fair Credit Reporting Act, and where an adverse action is based in "
            "whole or in part on information in that report, the notice obligations "
            "that attach to it apply. The credit report's provider, identifier and "
            "date must be recorded; a score with no report metadata behind it is not "
            "usable evidence."
        ),
        evidence=(
            "Consumer report with provider, report identifier and report date",
            "Borrower authorisation on file",
        ),
        research_reference=(
            RESEARCH + ", 'Regulatory and agency landscape' - FCRA permissible "
            "purpose and adverse-action duties."
        ),
        cross_refs=("POL-DEC-001",),
    ),
    Rule(
        rule_id="CRD-SCR-002",
        title="Representative score methodology",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="HARD_FAIL",
        outcome_type="CALCULATION",
        statement=(
            "For one borrower, the representative score is the middle of three "
            "scores, or the lower of two, or the single score where only one is "
            "available. For an application with more than one borrower, the "
            "application's representative score is the lowest of the borrowers' "
            "representative scores. The score model must be recorded alongside the "
            "value: a score without its model is not comparable to a threshold."
        ),
        parameters={
            "single_borrower": "middle of three, lower of two, otherwise the one",
            "multi_borrower": "lowest borrower representative score",
            "model_metadata_required": True,
        },
        research_reference=(
            RESEARCH + ", 'Liability/credit model' - representative-score methodology "
            "must be preserved; agency casefiles do not apply a single published "
            "minimum in the same way manual underwriting does."
        ),
    ),
    Rule(
        rule_id="CRD-SCR-005",
        title="Thin or absent credit history is not a failure",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="REFER",
        outcome_type="PASS_REFER_FAIL",
        statement=(
            "A borrower with fewer than three scoreable tradelines, or with no "
            "usable score, is routed for manual credit review with alternative "
            "credit evidence. Absence of credit history is not the same as adverse "
            "credit history, and must not be scored as though it were."
        ),
        parameters={"min_scoreable_tradelines_for_score_path": 3},
        evidence=(
            "Alternative credit references such as rent, utility or insurance payment "
            "history",
        ),
        requires_human_review=True,
        cross_refs=("POL-UWR-001",),
    ),
    Rule(
        rule_id="CRD-SCR-006",
        title="Prohibited-basis characteristics are never credit factors",
        source_category="REGULATORY",
        severity="HARD_FAIL",
        outcome_type="PROCESS",
        statement=(
            "Race, colour, religion, national origin, sex, marital status, age and "
            "the receipt of public assistance income may never be used as a factor in "
            "assessing creditworthiness, eligibility, affordability or the decision. "
            "Demographic information collected for statutory monitoring is held "
            "separately from the underwriting record and must not be supplied to any "
            "component that produces an eligibility, risk or recommendation output. "
            "Income from a public-assistance or retirement source is analysed for "
            "amount and likely continuance like any other income, never discounted "
            "for its source."
        ),
        parameters={
            "prohibited_factors": (
                "race, colour, religion, national origin, sex, marital status, age, "
                "receipt of public assistance"
            ),
            "monitoring_data_storage": "segregated from underwriting features",
        },
        research_reference=(
            RESEARCH + ", 'Regulatory and agency landscape' and 'Income model' - ECOA "
            "/ Regulation B 12 CFR 1002.6 evaluation rules and the prohibition on "
            "discounting public-assistance income."
        ),
        cross_refs=("POL-SEC-001", "POL-DEC-001"),
    ),
)

POL_CRD_001_V1 = Policy(
    policy_id="POL-CRD-001",
    title="Credit Assessment and Representative Score",
    version="1.0",
    effective_date=V1,
    expiration_date=V2,
    superseded_by="POL-CRD-001 v2.0",
    family="credit-assessment",
    priority=40,
    product_scope=ALL_PRODUCTS,
    purpose="Establishes how credit evidence is obtained, how a representative score "
    "is derived from it, and what minimum credit standard applies. It is the document "
    "a retrieval agent needs when the question is about score thresholds rather than "
    "about a specific derogatory event.",
    scope_note="Applies to every programme. Where a product document states a higher "
    "credit floor - as POL-CONV-003 and POL-JUMBO-001 do - the product floor governs.",
    rules=_CRD_COMMON
    + (
        Rule(
            rule_id="CRD-SCR-003",
            title="Minimum representative score",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The representative score must be at least 620 for a conventional "
                "conforming transaction, regardless of leverage. Government programme "
                "overlays set their own floors and govern for their own programmes."
            ),
            parameters={
                "min_representative_score_conventional": 620,
                "leverage_adjustment": "none",
            },
        ),
        Rule(
            rule_id="CRD-SCR-004",
            title="Credit report freshness",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "The credit report must be no older than 120 days on the note date. A "
                "report older than that is refreshed rather than extrapolated, because "
                "new obligations appearing after the report date change the "
                "debt-to-income calculation."
            ),
            parameters={"max_report_age_days": 120},
            condition_template="Obtain a refreshed credit report before closing.",
            cross_refs=("POL-DOC-001",),
        ),
    ),
    documentation=(
        "Consumer report with provider, identifier, date and every available score "
        "with its model.",
        "Borrower authorisation for the credit inquiry.",
    ),
    related_policies=("POL-CRD-002", "POL-CRD-003", "POL-LIA-001"),
    version_note=(
        "Original credit standard: a flat 620 floor for conventional transactions. "
        "Superseded on 2026-07-01."
    ),
)

POL_CRD_001_V2 = Policy(
    policy_id="POL-CRD-001",
    title="Credit Assessment and Representative Score",
    version="2.0",
    effective_date=V2,
    supersedes="POL-CRD-001 v1.0",
    family="credit-assessment",
    priority=40,
    product_scope=ALL_PRODUCTS,
    purpose="Establishes how credit evidence is obtained, how a representative score "
    "is derived from it, and what minimum credit standard applies. It is the document "
    "a retrieval agent needs when the question is about score thresholds rather than "
    "about a specific derogatory event.",
    scope_note="Applies to every programme. Where a product document states a higher "
    "credit floor - as POL-CONV-003 and POL-JUMBO-001 do - the product floor governs.",
    rules=_CRD_COMMON
    + (
        Rule(
            rule_id="CRD-SCR-003",
            title="Minimum representative score, graduated by leverage",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The minimum representative score for a conventional conforming "
                "transaction is graduated by loan-to-value: 620 at or below 90 percent, "
                "and 640 above 90 percent. Version 1.0 of this policy applied a flat 620 "
                "floor at every leverage level; an application whose underwriting as-of "
                "date falls before 2026-07-01 is still measured against that flat floor. "
                "A borrower at 660 with 95 percent leverage therefore passes under "
                "either version, while a borrower at 630 with 95 percent leverage passes "
                "under version 1.0 and fails under this one."
            ),
            parameters={
                "min_representative_score_ltv_at_or_below_90": 620,
                "min_representative_score_ltv_above_90": 640,
                "ltv_band_boundary": 0.90,
            },
        ),
        Rule(
            rule_id="CRD-SCR-004",
            title="Credit report freshness",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "The credit report must be no older than 90 days on the note date, "
                "reduced from 120 days in version 1.0. A report older than that is "
                "refreshed rather than extrapolated, because new obligations appearing "
                "after the report date change the debt-to-income calculation."
            ),
            parameters={"max_report_age_days": 90},
            condition_template="Obtain a refreshed credit report before closing.",
            cross_refs=("POL-DOC-001",),
        ),
        Rule(
            rule_id="CRD-SCR-007",
            title="Recent inquiries must be addressed, not scored",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Four or more credit inquiries in the 90 days before the report date "
                "require a written explanation identifying whether any resulted in new "
                "debt, and any new debt identified is added to the liabilities and the "
                "debt-to-income ratio is recomputed. Inquiry count is never itself a "
                "basis for an adverse outcome; rate-shopping for a single purpose "
                "commonly produces several inquiries."
            ),
            parameters={"inquiry_lookback_days": 90, "inquiry_count_trigger": 4},
            condition_template=(
                "Provide a written explanation for the {inquiry_count} credit inquiries "
                "in the {lookback_days} days before the report date, stating whether any "
                "resulted in new debt."
            ),
            cross_refs=("POL-LIA-001",),
        ),
    ),
    documentation=(
        "Consumer report with provider, identifier, date and every available score "
        "with its model.",
        "Borrower authorisation for the credit inquiry.",
        "Written explanation of recent inquiries where CRD-SCR-007 requires one.",
    ),
    related_policies=("POL-CRD-002", "POL-CRD-003", "POL-LIA-001"),
    version_note=(
        "Graduated the score floor by leverage (620 at or below 90 percent LTV, 640 "
        "above), shortened report freshness from 120 to 90 days, and added the "
        "recent-inquiry rule CRD-SCR-007."
    ),
)


# ---------------------------------------------------------------------------
# 10 - Significant derogatory credit events
# ---------------------------------------------------------------------------

POL_CRD_002 = Policy(
    policy_id="POL-CRD-002",
    title="Significant Derogatory Credit Events and Seasoning",
    version="1.0",
    effective_date=V1,
    family="credit-events",
    priority=42,
    product_scope=ALL_PRODUCTS,
    purpose="Governs how a bankruptcy, foreclosure, short sale, deed in lieu, "
    "charge-off or collection affects eligibility. The operative concept is "
    "seasoning: how much time has passed since the event concluded, measured from the "
    "correct anchor date for that event type.",
    scope_note="Applies to every programme. The anchor date differs by event type, "
    "and using the wrong anchor is the most common error this document guards against.",
    definitions=(
        (
            "Anchor date",
            "The date from which seasoning is measured. For a bankruptcy it is the "
            "discharge or dismissal date, not the filing date. For a foreclosure it is "
            "the completion or sale date, not the date of first delinquency. For a short "
            "sale or deed in lieu it is the date title transferred.",
        ),
        (
            "Extenuating circumstances",
            "A documented non-recurring event beyond the borrower's control that "
            "directly caused the derogatory event, supported by independent evidence "
            "rather than by the borrower's account alone.",
        ),
    ),
    rules=(
        Rule(
            rule_id="CRD-EVT-001",
            title="Seasoning periods by event type",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "A significant derogatory event bars eligibility until the seasoning "
                "period below has elapsed, measured from the event's anchor date to the "
                "application date. Seasoning that has not yet elapsed is a hard failure "
                "for the programme, not a referral - but the borrower may be eligible "
                "for a different programme with a shorter period, and the file should "
                "say so rather than simply declining."
            ),
            parameters={
                "chapter_7_bankruptcy_months": 48,
                "chapter_13_bankruptcy_discharged_months": 24,
                "foreclosure_months": 84,
                "deed_in_lieu_months": 48,
                "short_sale_months": 48,
                "mortgage_charge_off_months": 48,
                "anchor_bankruptcy": "discharge or dismissal date",
                "anchor_foreclosure": "completion or sale date",
                "anchor_short_sale": "title transfer date",
            },
            evidence=(
                "Court discharge or dismissal order",
                "Trustee deed, settlement statement or equivalent completion evidence",
            ),
            research_reference=(
                RESEARCH + ", 'Underwriting calculations' - derogatory seasoning depends "
                "on the event type and the correct anchor date; the periods here are "
                "synthetic."
            ),
        ),
        Rule(
            rule_id="CRD-EVT-002",
            title="Reduced seasoning with documented extenuating circumstances",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Where extenuating circumstances are documented by independent "
                "evidence, the seasoning period for a foreclosure, deed in lieu or short "
                "sale is reduced to 36 months, and the file is routed to an underwriter "
                "to assess whether the evidence supports the claim. The reduction is "
                "never applied on the strength of a letter of explanation alone."
            ),
            parameters={
                "reduced_seasoning_months": 36,
                "requires_independent_evidence": True,
                "applies_to": "foreclosure, deed in lieu, short sale",
            },
            evidence=(
                "Independent third-party evidence of the circumstance and its dates",
                "Evidence that the circumstance has been resolved",
            ),
            requires_human_review=True,
            cross_refs=("POL-UWR-001",),
        ),
        Rule(
            rule_id="CRD-EVT-003",
            title="Collections and charge-offs on non-mortgage debt",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Non-mortgage collection and charge-off accounts totalling more than "
                "5,000 across the application must be paid off or brought into a "
                "documented payment plan before closing, and any plan payment is "
                "included in the debt-to-income calculation. Individual accounts below "
                "500 are excluded from the total. Medical collections are excluded "
                "entirely from this test."
            ),
            parameters={
                "aggregate_threshold": 5000,
                "individual_account_floor": 500,
                "medical_collections_excluded": True,
            },
            condition_template=(
                "Pay off or document a payment plan for non-mortgage collection and "
                "charge-off accounts totalling {collection_total}."
            ),
            cross_refs=("POL-LIA-001",),
        ),
        Rule(
            rule_id="CRD-EVT-004",
            title="Disputed tradelines",
            source_category="COMMON_INDUSTRY_PRACTICE",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "A tradeline carrying a dispute indicator is not silently excluded from "
                "or included in the analysis. The underwriter records whether the "
                "disputed balance and payment are counted and why, because the same "
                "tradeline treated inconsistently between the debt-to-income calculation "
                "and the credit assessment produces two different pictures of the same "
                "file."
            ),
            requires_human_review=True,
            condition_template=(
                "Document the treatment of the disputed tradeline {tradeline_id} in both "
                "the credit assessment and the debt calculation."
            ),
            cross_refs=("POL-LIA-001",),
        ),
    ),
    documentation=(
        "Court or trustee documentation establishing the anchor date for each event.",
        "Independent evidence where extenuating circumstances are claimed.",
        "Payoff or payment-plan evidence for collections under CRD-EVT-003.",
    ),
    related_policies=("POL-CRD-001", "POL-CRD-003", "POL-LIA-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 11 - Delinquency and payment history
# ---------------------------------------------------------------------------

POL_CRD_003 = Policy(
    policy_id="POL-CRD-003",
    title="Delinquency and Payment History Treatment",
    version="1.0",
    effective_date=V1,
    family="delinquency-treatment",
    priority=43,
    product_scope=ALL_PRODUCTS,
    purpose="Governs how late payments short of a significant derogatory event are "
    "weighed. The distinction that matters is between housing-related delinquency and "
    "other delinquency, and between an isolated late and a pattern.",
    scope_note="Applies to every programme. Events that qualify as significant "
    "derogatory events are handled by POL-CRD-002 instead.",
    rules=(
        Rule(
            rule_id="CRD-DLQ-001",
            title="Housing payment history is weighed separately",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Any payment 60 or more days past due on a mortgage or rental obligation "
                "in the most recent 12 months is a hard failure. A single 30-day late on "
                "a housing obligation in that window routes the file for underwriter "
                "review. Housing history carries more weight than other history because "
                "it is the closest available analogue to the obligation being underwritten."
            ),
            parameters={
                "housing_lookback_months": 12,
                "housing_30d_refer_at": 1,
                "housing_60d_fail_at": 1,
            },
            evidence=(
                "Credit report housing tradeline",
                "Cancelled cheques or a verification of rent where no tradeline exists",
            ),
            requires_human_review=True,
        ),
        Rule(
            rule_id="CRD-DLQ-002",
            title="Non-housing delinquency pattern",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Three or more accounts showing a payment 30 or more days past due in "
                "the most recent 24 months, or any account 90 or more days past due in "
                "that window, routes the file for underwriter review with a written "
                "explanation. An isolated 30-day late on a single non-housing account is "
                "recorded and passed."
            ),
            parameters={
                "lookback_months": 24,
                "accounts_30d_refer_at": 3,
                "any_90d_refer": True,
            },
            condition_template=(
                "Provide a written explanation of the delinquencies reported in the last "
                "{lookback_months} months."
            ),
        ),
        Rule(
            rule_id="CRD-DLQ-003",
            title="Credit utilisation is context, not a threshold test",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="ADVISORY",
            outcome_type="CALCULATION",
            statement=(
                "Revolving utilisation is computed as total revolving balances divided "
                "by total revolving limits, excluding accounts with no stated limit. It "
                "is recorded as a risk indicator and may support a referral alongside "
                "other findings, but high utilisation alone is not a policy breach and "
                "must not be reported as one. Utilisation above 80 percent is noted in "
                "the risk summary."
            ),
            parameters={
                "excludes": "accounts with no stated limit and closed accounts",
                "risk_note_threshold": 0.80,
            },
            research_reference=(
                RESEARCH + ", 'Underwriting calculations' - credit utilisation is a "
                "common-practice risk indicator, with the no-limit exclusion."
            ),
        ),
        Rule(
            rule_id="CRD-DLQ-004",
            title="Recent payment behaviour outweighs distant behaviour",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="ADVISORY",
            outcome_type="PROCESS",
            statement=(
                "Where a file shows deteriorating recent behaviour against a clean older "
                "history, the recent behaviour governs the referral decision. Where it "
                "shows improving behaviour against an adverse older history, the "
                "improvement is recorded as a compensating factor available to "
                "POL-DTI-001. Neither direction is inferred from the score alone."
            ),
            cross_refs=("POL-DTI-001",),
        ),
    ),
    documentation=(
        "Credit report payment history for every open account.",
        "Verification of rent where housing history is not on the credit report.",
        "Written explanations required by CRD-DLQ-002.",
    ),
    related_policies=("POL-CRD-001", "POL-CRD-002"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 12 - Liabilities
# ---------------------------------------------------------------------------

POL_LIA_001 = Policy(
    policy_id="POL-LIA-001",
    title="Liabilities and Debt Inclusion",
    version="1.0",
    effective_date=V1,
    family="liabilities",
    priority=45,
    product_scope=ALL_PRODUCTS,
    purpose="Determines which obligations enter the debt-to-income numerator and at "
    "what payment amount. The answer is rarely 'the balance': what matters is the "
    "monthly payment, whether it will continue, and whether the evidence supports "
    "excluding it.",
    scope_note="Applies to every programme. Every obligation is stored as its own "
    "record with its source and its inclusion decision; a single aggregated "
    "'monthly debt' figure is not an acceptable representation.",
    definitions=(
        (
            "Recurring monthly obligation",
            "A payment the borrower is contractually required to make each month that "
            "will continue after closing. A payment that ends within the near-term "
            "window below is treated separately.",
        ),
    ),
    rules=(
        Rule(
            rule_id="LIA-INC-001",
            title="Every obligation is recorded individually with its inclusion decision",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PROCESS",
            statement=(
                "Each obligation is stored with its creditor, type, balance, monthly "
                "payment, remaining term, evidence source and an explicit include or "
                "exclude decision citing the rule that produced it. Storing only a total "
                "makes the debt-to-income ratio unauditable, because no reviewer can "
                "determine which obligations were counted."
            ),
            research_reference=(
                RESEARCH + ", 'Liability/credit model' - store every obligation "
                "separately with its source and DTI treatment."
            ),
        ),
        Rule(
            rule_id="LIA-INC-002",
            title="Obligations ending within ten months may be excluded",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "An instalment obligation with ten or fewer payments remaining may be "
                "excluded from the debt-to-income calculation, provided the remaining "
                "term is evidenced and the payment is not so large that it materially "
                "affects the borrower's ability to accumulate funds to close. A lease "
                "payment is never excluded on this basis regardless of remaining term, "
                "because leases are typically renewed or replaced."
            ),
            parameters={
                "max_remaining_payments_for_exclusion": 10,
                "lease_excluded_from_this_rule": True,
                "materiality_guard": "payment above 5 percent of qualifying income",
            },
            evidence=("Statement or credit report field showing the remaining term",),
        ),
        Rule(
            rule_id="LIA-INC-003",
            title="Revolving accounts use the stated minimum payment",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "A revolving account with an outstanding balance is included at its "
                "stated minimum payment. Where no minimum is stated, five percent of the "
                "outstanding balance is used. An account with a zero balance is excluded, "
                "but the available limit is still recorded because it affects the "
                "utilisation measure and the HCLTV calculation for a secured line."
            ),
            parameters={
                "fallback_minimum_payment_pct_of_balance": 0.05,
                "zero_balance_excluded": True,
            },
            cross_refs=("POL-CRD-003",),
        ),
        Rule(
            rule_id="LIA-INC-004",
            title="Deferred and income-driven obligations",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="CALCULATION",
            statement=(
                "A deferred obligation, or one in forbearance, is included at the "
                "documented payment that will apply when repayment resumes. Where no "
                "such payment is documented, one percent of the outstanding balance is "
                "used. A documented income-driven payment is used at its stated amount "
                "even where that amount is zero, provided the plan documentation is "
                "current."
            ),
            parameters={
                "fallback_payment_pct_of_balance": 0.01,
                "income_driven_zero_payment_allowed": True,
                "plan_documentation_required": True,
            },
            evidence=(
                "Servicer statement showing the scheduled payment",
                "Current repayment-plan documentation",
            ),
        ),
        Rule(
            rule_id="LIA-INC-005",
            title="Obligations paid by another party",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "An obligation on which the borrower is liable but which another party "
                "has paid may be excluded where the most recent 12 months of payments "
                "from that party are evidenced and the borrower is not the primary "
                "obligor of record. Business obligations paid by the borrower's business "
                "follow the same test. The exclusion turns on evidence of who actually "
                "paid, not on who says they will."
            ),
            parameters={"required_months_of_third_party_payments": 12},
            evidence=(
                "12 months of cancelled cheques or account statements from the paying "
                "party",
            ),
            condition_template=(
                "Provide 12 months of payment evidence from the party paying obligation "
                "{liability_id}."
            ),
        ),
        Rule(
            rule_id="LIA-INC-006",
            title="Obligations found on the credit report but absent from the application",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "An obligation appearing on the credit report but not declared on the "
                "application is added to the liabilities and the debt-to-income ratio is "
                "recomputed. The omission itself is recorded as a data-quality finding. "
                "Where the recomputed ratio breaches the affordability limit, the file is "
                "routed for review rather than declined automatically, because the "
                "borrower has not yet had the opportunity to explain or dispute the "
                "tradeline."
            ),
            requires_human_review=True,
            condition_template=(
                "Confirm or dispute the undeclared obligation {liability_id} identified "
                "on the credit report."
            ),
            cross_refs=("POL-DTI-001", "POL-FRD-001"),
        ),
    ),
    documentation=(
        "Credit report tradelines for every obligation.",
        "Statements evidencing remaining term where an exclusion is claimed.",
        "Third-party payment evidence where LIA-INC-005 is relied upon.",
    ),
    related_policies=("POL-DTI-001", "POL-CRD-001", "POL-CRD-002"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 13 - Affordability / DTI (two versions)
# ---------------------------------------------------------------------------

_DTI_COMMON_HEAD = (
    Rule(
        rule_id="DTI-CALC-001",
        title="Definition and components of the affordability measures",
        source_category="AGENCY_INVESTOR",
        severity="HARD_FAIL",
        outcome_type="CALCULATION",
        statement=(
            "Back-end debt-to-income is total monthly obligations divided by the "
            "stable monthly income used to qualify. Total monthly obligations are the "
            "qualifying housing expense plus every recurring obligation POL-LIA-001 "
            "marked for inclusion. The qualifying housing expense is principal, "
            "interest, property taxes, hazard insurance, association dues, mortgage or "
            "guarantee insurance, flood insurance where required, and any subordinate "
            "lien payment. The housing ratio uses the same numerator components "
            "restricted to the housing expense. Published agency guidance for "
            "conventional conforming loans sold to a government-sponsored enterprise "
            "defines the ratio this way and, in its current form, generally limits "
            "manually underwritten loans to 36 percent with specified circumstances "
            "allowing up to 45 percent, while automated-underwriting casefiles may "
            "permit up to 50 percent. Those are that agency's figures for its own "
            "programme. They are not universal mortgage thresholds, and they are not "
            "the limit this lender enforces - see DTI-CONV-001 for that."
        ),
        parameters={
            "back_end_formula": "total monthly obligations / qualifying monthly income",
            "front_end_formula": "qualifying housing expense / qualifying monthly income",
            "zero_income_result": "INDETERMINATE, never zero or infinite",
        },
        research_reference=(
            RESEARCH + ", 'Underwriting calculations' - Fannie Mae Selling Guide "
            "B3-6-02 defines DTI and states the manual and automated limits as "
            "agency-specific current guidelines, not universal thresholds."
        ),
        cross_refs=("POL-LIA-001", "POL-INC-001"),
    ),
    Rule(
        rule_id="DTI-CALC-002",
        title="Affordability is computed deterministically, never estimated",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="HARD_FAIL",
        outcome_type="PROCESS",
        statement=(
            "Every affordability figure is produced by the committed calculation code "
            "with its inputs and formula version recorded. No affordability value may "
            "originate from a language model's arithmetic. A model may explain a "
            "computed ratio; it may not compute one, and a ratio appearing in a "
            "narrative that does not match the calculation record is a defect in the "
            "narrative."
        ),
        parameters={
            "rounding": "ratios to four decimal places, money to cents, half-up",
            "provenance_required": "input field ids and formula version",
        },
        research_reference=(
            RESEARCH + ", 'Agentic AI architecture mapping' - the LLM must not be "
            "trusted to perform DTI, LTV, amortisation or date arithmetic."
        ),
    ),
    Rule(
        rule_id="DTI-CALC-003",
        title="Disposable income is reported alongside the ratio",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="ADVISORY",
        outcome_type="CALCULATION",
        statement=(
            "Monthly disposable income - qualifying monthly income less total monthly "
            "obligations - is computed and reported with every affordability "
            "assessment. Two files with the same ratio can have very different "
            "absolute capacity, and the residual figure is what the "
            "residual-income tests in the government overlays consume."
        ),
        parameters={
            "formula": "qualifying monthly income - total monthly obligations"
        },
        cross_refs=("POL-VA-001",),
    ),
)

_DTI_COMMON_TAIL = (
    Rule(
        rule_id="DTI-BRE-001",
        title="A breach is reported with the threshold it failed",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="HARD_FAIL",
        outcome_type="PROCESS",
        statement=(
            "Where an affordability limit is breached, the finding must state the "
            "computed value, the threshold that was exceeded, the rule id and policy "
            "version that set it, and the inputs that produced the computed value. A "
            "breach reported without its threshold is not actionable: the borrower "
            "cannot tell how far away they are, and the reviewer cannot tell whether "
            "the right limit was applied."
        ),
        parameters={
            "required_fields": (
                "computed_value, threshold_value, rule_id, policy_version, input_field_ids"
            )
        },
        cross_refs=("POL-DEC-001",),
    ),
    Rule(
        rule_id="DTI-BRE-002",
        title="Payment shock is recorded where a prior housing payment exists",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="ADVISORY",
        outcome_type="CALCULATION",
        statement=(
            "Where the borrower has a current housing payment, the proportional "
            "increase to the proposed payment is computed and recorded. A borrower with "
            "no prior housing payment has no meaningful denominator and the measure is "
            "recorded as not applicable rather than as zero. Payment shock is a risk "
            "indicator that can support a referral; it is not a threshold test."
        ),
        parameters={
            "formula": "(proposed PITIA - current housing payment) / current housing payment",
            "no_prior_payment": "not applicable",
            "risk_note_threshold": 0.50,
        },
        research_reference=(
            RESEARCH + ", 'Underwriting calculations' - payment shock is a common risk "
            "indicator, not a universal hard threshold."
        ),
    ),
)

POL_DTI_001_V1 = Policy(
    policy_id="POL-DTI-001",
    title="Affordability, Debt-to-Income and Disposable Income",
    version="1.0",
    effective_date=V1,
    expiration_date=V2,
    superseded_by="POL-DTI-001 v2.0",
    family="affordability-dti",
    priority=50,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how affordability is measured and what limit applies. This is "
    "the document behind acceptance criterion AC-02: it is where a breach gets the "
    "threshold it failed.",
    scope_note="Applies to every programme. Where a government overlay states its own "
    "affordability ceiling, the overlay governs for that programme, and this document "
    "continues to govern the definitions and the calculation method.",
    rules=_DTI_COMMON_HEAD
    + (
        Rule(
            rule_id="DTI-CONV-001",
            title="Maximum back-end debt-to-income",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Back-end debt-to-income must not exceed 45 percent for a conventional "
                "conforming transaction at any leverage level. This is the lender's own "
                "limit; it is not an agency limit and it is not a regulatory limit."
            ),
            parameters={
                "max_back_end_dti": 0.45,
                "compensating_factor_extension": "none under this version",
            },
        ),
        Rule(
            rule_id="DTI-CONV-002",
            title="Housing ratio is advisory",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="ADVISORY",
            outcome_type="CALCULATION",
            statement=(
                "The housing ratio is computed and recorded for every application but "
                "is not itself a pass or fail test on conventional transactions. A "
                "housing ratio above 38 percent is noted in the risk summary. The USDA "
                "overlay is the exception: there the housing ratio is a hard test."
            ),
            parameters={"risk_note_threshold": 0.38, "hard_test": False},
            cross_refs=("POL-USDA-001",),
        ),
    )
    + _DTI_COMMON_TAIL,
    documentation=(
        "The calculation record for every affordability figure, with inputs and "
        "formula version.",
        "Evidence supporting every income and obligation component.",
    ),
    related_policies=("POL-INC-001", "POL-LIA-001", "POL-GEN-001"),
    version_note=(
        "Original affordability standard: a flat 45 percent back-end ceiling with no "
        "compensating-factor structure. Superseded on 2026-07-01."
    ),
)

POL_DTI_001_V2 = Policy(
    policy_id="POL-DTI-001",
    title="Affordability, Debt-to-Income and Disposable Income",
    version="2.0",
    effective_date=V2,
    supersedes="POL-DTI-001 v1.0",
    family="affordability-dti",
    priority=50,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how affordability is measured and what limit applies. This is "
    "the document behind acceptance criterion AC-02: it is where a breach gets the "
    "threshold it failed.",
    scope_note="Applies to every programme. Where a government overlay states its own "
    "affordability ceiling, the overlay governs for that programme, and this document "
    "continues to govern the definitions and the calculation method.",
    rules=_DTI_COMMON_HEAD
    + (
        Rule(
            rule_id="DTI-CONV-001",
            title="Maximum back-end debt-to-income, with a compensating-factor extension",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Back-end debt-to-income must not exceed 43 percent for a conventional "
                "conforming transaction. The ceiling extends to 45 percent where at "
                "least two compensating factors from DTI-CONV-003 are documented and "
                "named in the file. Version 1.0 of this policy allowed 45 percent "
                "unconditionally; an application whose underwriting as-of date falls "
                "before 2026-07-01 is still measured against that unconditional 45 "
                "percent. A file computing at 44 percent with no compensating factors "
                "therefore passes under version 1.0 and breaches under this version, "
                "which is exactly the distinction a policy-retrieval component has to "
                "get right."
            ),
            parameters={
                "max_back_end_dti": 0.43,
                "max_back_end_dti_with_factors": 0.45,
                "min_compensating_factors": 2,
            },
        ),
        Rule(
            rule_id="DTI-CONV-002",
            title="Housing ratio is advisory",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="ADVISORY",
            outcome_type="CALCULATION",
            statement=(
                "The housing ratio is computed and recorded for every application but "
                "is not itself a pass or fail test on conventional transactions. A "
                "housing ratio above 38 percent is noted in the risk summary. The USDA "
                "overlay is the exception: there the housing ratio is a hard test."
            ),
            parameters={"risk_note_threshold": 0.38, "hard_test": False},
            cross_refs=("POL-USDA-001",),
        ),
        Rule(
            rule_id="DTI-CONV-003",
            title="Recognised compensating factors",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PROCESS",
            statement=(
                "Only the following are recognised as compensating factors for the "
                "extension in DTI-CONV-001, and each must be documented and named "
                "explicitly in the decision record: verified post-closing reserves of at "
                "least six months of the qualifying housing expense; a representative "
                "credit score at or above 720; a proposed housing payment no greater "
                "than 105 percent of the borrower's documented current housing payment; "
                "verified continuous employment with the same employer for at least 60 "
                "months; and a loan-to-value at or below 75 percent. A factor that is "
                "asserted but not documented does not count, and the extension is not "
                "available on cash-out refinances or under the jumbo overlay."
            ),
            parameters={
                "factor_reserves_months": 6,
                "factor_min_credit_score": 720,
                "factor_max_payment_shock": 0.05,
                "factor_min_employment_months": 60,
                "factor_max_ltv": 0.75,
                "excluded_products": "cash_out_refinance, jumbo",
            },
            evidence=("Documentation of each factor claimed, cited by name",),
            cross_refs=("POL-AST-003", "POL-CRD-001"),
        ),
    )
    + _DTI_COMMON_TAIL,
    documentation=(
        "The calculation record for every affordability figure, with inputs and "
        "formula version.",
        "Evidence supporting every income and obligation component.",
        "Named documentation for each compensating factor relied upon.",
    ),
    related_policies=("POL-INC-001", "POL-LIA-001", "POL-GEN-001"),
    version_note=(
        "Reduced the unconditional back-end ceiling from 45 to 43 percent and "
        "introduced the documented compensating-factor extension to 45 percent "
        "(DTI-CONV-003)."
    ),
)


PART_A_POLICIES = (
    POL_GEN_001,
    POL_CONV_001,
    POL_CONV_002,
    POL_CONV_003,
    POL_JUMBO_001_V1,
    POL_JUMBO_001_V2,
    POL_FHA_001,
    POL_VA_001,
    POL_USDA_001,
    POL_CRD_001_V1,
    POL_CRD_001_V2,
    POL_CRD_002,
    POL_CRD_003,
    POL_LIA_001,
    POL_DTI_001_V1,
    POL_DTI_001_V2,
)
