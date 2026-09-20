"""
Policy definitions, part B: income and employment.

Documents 14-22 of the corpus. The income family is deliberately polymorphic:
income types are not interchangeable, and the research report is explicit that a
single `income_amount` field destroys the distinction between declared, verified and
qualifying values.
"""

from __future__ import annotations

from .policies import Policy, Rule
from .policy_defs_a import ALL_OCCUPANCY, ALL_PRODUCTS, RESEARCH, V1, V2


# ---------------------------------------------------------------------------
# 14 - Income general principles
# ---------------------------------------------------------------------------

POL_INC_001 = Policy(
    policy_id="POL-INC-001",
    title="Income General Principles and Qualifying Income",
    version="1.0",
    effective_date=V1,
    family="income-general",
    priority=48,
    product_scope=ALL_PRODUCTS,
    purpose="Establishes what qualifying income is, how it differs from declared and "
    "verified income, and the tests every income source must satisfy before any "
    "amount enters the affordability calculation.",
    scope_note="Applies to every income source in every programme. The source-specific "
    "documents POL-INC-002 through POL-INC-007 state how each type is calculated; this "
    "document states the tests they all share.",
    definitions=(
        (
            "Declared income",
            "The amount the applicant stated on the application. It is never used to "
            "qualify. It is retained so the file can show what changed on verification.",
        ),
        (
            "Verified income",
            "The amount authoritative evidence establishes. For a salaried borrower "
            "this is what the paystub, W-2 and employment verification jointly support.",
        ),
        (
            "Qualifying income",
            "The amount policy permits to be used, after history, trend and continuance "
            "tests are applied to the verified amount. Qualifying income is frequently "
            "lower than verified income and is never higher.",
        ),
        (
            "Continuance",
            "A reasonable expectation that the income will continue for at least the "
            "period stated in INC-GEN-003. Continuance is about the income, never about "
            "who receives it or where it comes from.",
        ),
    ),
    rules=(
        Rule(
            rule_id="INC-GEN-001",
            title="Declared, verified and qualifying amounts are stored separately",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PROCESS",
            statement=(
                "Each income source carries three amounts: declared, verified and "
                "qualifying, each with its own evidence reference and as-of date. "
                "Overwriting the three with a single figure is a data-model defect, "
                "because it makes it impossible to show which document supported which "
                "number or to detect that the application and the evidence disagreed."
            ),
            research_reference=(
                RESEARCH + ", 'Mortgage data, document, calculation, policy and lineage "
                "architecture' - declared, observed/verified and qualifying values must "
                "be preserved separately."
            ),
        ),
        Rule(
            rule_id="INC-GEN-002",
            title="Qualifying income must not exceed verified income",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "The qualifying amount for any source must be less than or equal to the "
                "verified amount for that source. A qualifying amount above the verified "
                "amount means the calculation used a figure the evidence does not "
                "support, and the affordability result derived from it is unusable."
            ),
            parameters={"invariant": "qualifying_amount <= verified_amount"},
        ),
        Rule(
            rule_id="INC-GEN-003",
            title="Continuance period",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Income may be used only where it is reasonably expected to continue "
                "for at least 36 months from the note date. Where evidence shows a "
                "defined end date inside that window - a fixed-term contract, a benefit "
                "with a stated expiry, a support order terminating on a known date - the "
                "income is excluded unless documented renewal or replacement evidence is "
                "provided. A source with no defined end date is presumed continuing."
            ),
            parameters={
                "continuance_months": 36,
                "defined_end_date_within_window": "exclude unless renewal evidenced",
            },
            evidence=("Award letters, contracts or orders showing any end date",),
        ),
        Rule(
            rule_id="INC-GEN-004",
            title="Income source is never a basis for discounting",
            source_category="REGULATORY",
            severity="HARD_FAIL",
            outcome_type="PROCESS",
            statement=(
                "Income may not be discounted or refused because of its source where "
                "that source is public assistance, retirement, disability or a "
                "protected characteristic of the recipient. Analysis is confined to the "
                "verifiable amount and its likely continuance. Applying a haircut to a "
                "benefit source that would not be applied to wage income of the same "
                "amount and stability is a fair-lending failure, not a conservative "
                "underwriting choice."
            ),
            research_reference=(
                RESEARCH + ", 'Income model' - ECOA prohibits discrimination based on "
                "receipt of public-assistance income; legitimate analysis is confined "
                "to amount and likely continuance."
            ),
            cross_refs=("POL-CRD-001", "POL-DEC-001"),
        ),
        Rule(
            rule_id="INC-GEN-005",
            title="Non-taxable income may be grossed up",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="CALCULATION",
            statement=(
                "Verified income that is not subject to federal income tax may be "
                "increased by 15 percent for qualifying purposes, provided the "
                "non-taxable status is documented. The adjustment is recorded as its own "
                "calculation step so the pre-adjustment amount remains visible. The "
                "adjustment is never applied to an amount whose tax status is assumed "
                "rather than evidenced."
            ),
            parameters={
                "gross_up_pct": 0.15,
                "documentation_required": "evidence of non-taxable status",
            },
            cross_refs=("POL-INC-007",),
        ),
        Rule(
            rule_id="INC-GEN-006",
            title="Conflicting income evidence is reconciled, never averaged away",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Where two sources of income evidence disagree by more than five "
                "percent of the lower figure, the discrepancy is recorded explicitly "
                "with both values and their document references, the lower verified "
                "figure is used pending resolution, and the file is routed for review. "
                "Silently averaging the two, or taking the higher, conceals the conflict "
                "that the reviewer needs to see."
            ),
            parameters={
                "materiality_threshold": 0.05,
                "interim_treatment": "use the lower verified figure",
                "record": "both values, both document ids, the computed variance",
            },
            requires_human_review=True,
            research_reference=(
                RESEARCH + ", 'Missing/conflicting data workflow' - reconcile pay "
                "frequency, YTD and employment verification, and use the verified "
                "qualifying amount."
            ),
            cross_refs=("POL-FRD-001", "POL-UWR-001"),
        ),
    ),
    documentation=(
        "Evidence for every income source, referenced by document id.",
        "The qualifying-income calculation record with its per-source components.",
    ),
    related_policies=("POL-DTI-001", "POL-EMP-001", "POL-DOC-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 15 - Salaried income
# ---------------------------------------------------------------------------

POL_INC_002 = Policy(
    policy_id="POL-INC-002",
    title="Salaried Income Qualification",
    version="1.0",
    effective_date=V1,
    family="income-salaried",
    priority=49,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how fixed annual salary is verified and converted into "
    "qualifying monthly income. Salary is the simplest income type and the one most "
    "applications rely on, which makes it the type where arithmetic errors are least "
    "likely to be noticed.",
    scope_note="Applies to borrowers paid a fixed annual salary by an employer they do "
    "not own. Ownership of 25 percent or more of the employing business makes the "
    "borrower self-employed under POL-INC-005 regardless of how the pay is described.",
    rules=(
        Rule(
            rule_id="INC-SAL-001",
            title="Conversion to monthly qualifying income",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "Fixed annual salary converts to monthly income by dividing the annual "
                "amount by 12. Where pay is stated per period, the conversion uses the "
                "period multiplier: weekly pay multiplied by 52 and divided by 12; "
                "bi-weekly pay multiplied by 26 and divided by 12; semi-monthly pay "
                "multiplied by 24 and divided by 12. Treating bi-weekly pay as though it "
                "were semi-monthly understates annual income by roughly four percent, "
                "which is the single most common arithmetic error in this category."
            ),
            parameters={
                "annual_divisor": 12,
                "weekly_multiplier": 52,
                "biweekly_multiplier": 26,
                "semimonthly_multiplier": 24,
                "monthly_multiplier": 12,
            },
            research_reference=(
                RESEARCH + ", 'Income model' - fixed salary is converted to monthly "
                "income; pay frequency is an explicit edge case."
            ),
        ),
        Rule(
            rule_id="INC-SAL-002",
            title="Required documentation",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Salaried income requires a paystub covering at least one full pay "
                "period within the freshness window, the most recent W-2, and an "
                "employment verification. Where a validated digital verification report "
                "covers employment and income, the paystub and W-2 requirement may be "
                "reduced - but a digital report never removes the obligation to resolve "
                "contradictory information it contains."
            ),
            parameters={
                "paystub_periods_required": 1,
                "w2_years_required": 1,
                "employment_verification_required": True,
                "digital_verification_reduces_documents": True,
            },
            evidence=(
                "Paystub showing pay period, gross pay for the period and year-to-date "
                "gross",
                "W-2 for the most recent year",
                "Written or verbal employment verification",
            ),
            condition_template=(
                "Provide a paystub dated within {freshness_days} days covering at least "
                "one full pay period."
            ),
            research_reference=(
                RESEARCH + ", 'Document catalog' - digital validation services can "
                "reduce document requirements without removing the obligation to address "
                "contradictory information."
            ),
            cross_refs=("POL-DOC-001", "POL-EMP-001"),
        ),
        Rule(
            rule_id="INC-SAL-003",
            title="Year-to-date earnings must reconcile with the stated salary",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Year-to-date gross on the most recent paystub, annualised over the "
                "elapsed pay periods, must reconcile with the stated annual salary within "
                "five percent. Where it does not, the difference is investigated before "
                "the income is used: the usual explanations are a mid-year raise, unpaid "
                "leave, a bonus included in year-to-date gross, or a paystub that does "
                "not belong to this borrower. The reconciliation is recorded whether or "
                "not it identifies a discrepancy."
            ),
            parameters={
                "tolerance": 0.05,
                "formula": "YTD gross / elapsed pay periods * periods per year",
            },
            requires_human_review=True,
            cross_refs=("POL-INC-001", "POL-FRD-001"),
        ),
        Rule(
            rule_id="INC-SAL-004",
            title="A documented raise may be used before it appears on a paystub",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "A salary increase effective within 60 days of the note date may be used "
                "at the increased rate where the employer documents the new rate and its "
                "effective date in writing. Until that evidence exists, the prior rate is "
                "used. An increase that has not yet taken effect and is not documented is "
                "not qualifying income, however confident the borrower is about it."
            ),
            parameters={
                "max_days_before_effective": 60,
                "documentation": "employer letter stating the new rate and effective date",
            },
            condition_template=(
                "Provide employer documentation of the salary increase and its effective "
                "date."
            ),
        ),
    ),
    documentation=(
        "Paystub, W-2 and employment verification as required by INC-SAL-002.",
        "The year-to-date reconciliation record required by INC-SAL-003.",
    ),
    related_policies=("POL-INC-001", "POL-EMP-001", "POL-DOC-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 16 - Hourly and variable-hour income
# ---------------------------------------------------------------------------

POL_INC_003 = Policy(
    policy_id="POL-INC-003",
    title="Hourly and Variable-Hour Income",
    version="1.0",
    effective_date=V1,
    family="income-hourly",
    priority=49,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how hourly earnings are qualified. The critical distinction is "
    "between hours that are guaranteed and hours that merely happened: only the former "
    "can be treated as fixed income.",
    scope_note="Applies to borrowers paid an hourly rate. Overtime and other premium "
    "earnings on top of base hours are governed by POL-INC-004.",
    definitions=(
        (
            "Guaranteed hours",
            "A weekly hour count the employer commits to in writing. An employment "
            "verification that reports hours actually worked is not evidence of "
            "guaranteed hours.",
        ),
    ),
    rules=(
        Rule(
            rule_id="INC-HRL-001",
            title="Guaranteed hours are qualified as fixed income",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "Where the employer confirms a guaranteed weekly hour count in writing, "
                "monthly income is the hourly rate multiplied by the guaranteed hours, "
                "multiplied by 52 and divided by 12. Hours above the guaranteed count are "
                "variable earnings and follow INC-HRL-002, not this rule."
            ),
            parameters={
                "formula": "rate * guaranteed weekly hours * 52 / 12",
                "guarantee_evidence_required": True,
            },
        ),
        Rule(
            rule_id="INC-HRL-002",
            title="Variable hours are averaged over history",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "Where hours are not guaranteed, qualifying income is the average of "
                "verified earnings over the most recent 24 months, or over 12 months "
                "where a 24-month history is unavailable and the shorter history is "
                "stable. The average is taken over the full period including any "
                "low-earning months; excluding weak periods from the average inflates the "
                "result and is not permitted."
            ),
            parameters={
                "preferred_history_months": 24,
                "minimum_history_months": 12,
                "averaging": "full period, no exclusions",
            },
            evidence=(
                "W-2 forms covering the averaging period",
                "Year-to-date paystub",
                "Employment verification reporting hours",
            ),
        ),
        Rule(
            rule_id="INC-HRL-003",
            title="Declining hours reduce the qualifying amount",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Where the current-period annualised rate is more than 10 percent below "
                "the historical average, the lower current figure is used rather than the "
                "average, and the file is routed for review. An average that is propped "
                "up by earnings the borrower is no longer achieving overstates capacity. "
                "A rising trend does not permit using an amount above the historical "
                "average."
            ),
            parameters={
                "decline_trigger": 0.10,
                "declining_treatment": "use the current annualised amount",
                "rising_treatment": "use the historical average, never the current peak",
            },
            requires_human_review=True,
            research_reference=(
                RESEARCH + ", 'Income model' - falling hours are the principal risk for "
                "variable hourly income."
            ),
        ),
        Rule(
            rule_id="INC-HRL-004",
            title="Seasonal employment",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Seasonal employment requires a two-year history in the same seasonal "
                "role or industry and evidence that the borrower is expected to be "
                "rehired. Qualifying income is the full-year average including the "
                "off-season, not the in-season rate. Qualifying a seasonal borrower on "
                "peak-season earnings produces a payment they cannot make for part of "
                "every year."
            ),
            parameters={
                "required_history_months": 24,
                "averaging_basis": "full calendar year including off-season",
            },
            evidence=("Employer statement of expected rehire", "Two years of W-2 forms"),
        ),
    ),
    documentation=(
        "Written confirmation of guaranteed hours where INC-HRL-001 is relied upon.",
        "W-2 forms and paystubs covering the averaging period.",
    ),
    related_policies=("POL-INC-004", "POL-EMP-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 17 - Bonus, overtime, commission and tip income (two versions)
# ---------------------------------------------------------------------------

_VAR_COMMON = (
    Rule(
        rule_id="INC-VAR-002",
        title="Averaging method",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="HARD_FAIL",
        outcome_type="CALCULATION",
        statement=(
            "Qualifying variable income is the total verified variable earnings over "
            "the qualifying history divided by the number of months in that history. "
            "Where the history spans two W-2 years plus a year-to-date period, all "
            "three are summed and divided by the total elapsed months. Partial months "
            "are counted as whole months only where the paystub's year-to-date field "
            "supports it."
        ),
        parameters={
            "formula": "total variable earnings over history / months in history"
        },
    ),
    Rule(
        rule_id="INC-VAR-003",
        title="Declining variable income",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="REFER",
        outcome_type="PASS_REFER_FAIL",
        statement=(
            "Where the current-year annualised variable earnings are more than 20 "
            "percent below the prior full year, the lower current figure is used and "
            "the file is routed for review with a written explanation of the decline. "
            "Where the decline exceeds 40 percent, the variable component is excluded "
            "from qualifying income entirely unless the underwriter documents why it "
            "should be retained."
        ),
        parameters={
            "refer_decline_trigger": 0.20,
            "exclude_decline_trigger": 0.40,
        },
        requires_human_review=True,
        condition_template=(
            "Provide a written explanation of the {decline_pct} decline in variable "
            "earnings and evidence of the expected forward level."
        ),
        research_reference=(
            RESEARCH + ", 'Income model' - volatile or declining variable income is the "
            "principal risk for this category."
        ),
    ),
    Rule(
        rule_id="INC-VAR-004",
        title="Commission income with significant unreimbursed expenses",
        source_category="SYNTHETIC_INTERNAL_POLICY",
        severity="CONDITIONAL",
        outcome_type="CALCULATION",
        statement=(
            "Where commission income represents more than 25 percent of the borrower's "
            "total income, tax-return evidence is obtained and documented unreimbursed "
            "business expenses are deducted from the qualifying amount. Using gross "
            "commission without the expense deduction overstates the income actually "
            "available to service debt."
        ),
        parameters={
            "commission_share_trigger": 0.25,
            "expense_treatment": "deduct documented unreimbursed business expenses",
        },
        evidence=("Tax returns covering the qualifying history",),
    ),
)

POL_INC_004_V1 = Policy(
    policy_id="POL-INC-004",
    title="Bonus, Overtime, Commission and Tip Income",
    version="1.0",
    effective_date=V1,
    expiration_date=V2,
    superseded_by="POL-INC-004 v2.0",
    family="income-variable",
    priority=49,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how earnings that vary period to period are qualified. These "
    "earnings are often the difference between a file that fits and one that does not, "
    "which is precisely why the history requirement matters.",
    scope_note="Applies to bonus, overtime, commission and tip earnings paid on top of "
    "a base wage or salary. Income from a business the borrower owns is governed by "
    "POL-INC-005 regardless of how it is labelled on a paystub.",
    rules=(
        Rule(
            rule_id="INC-VAR-001",
            title="Required earnings history",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Variable earnings require a 24-month history with the same employer or "
                "in the same line of work. Where 24 months are not available, the "
                "variable component is excluded from qualifying income. Published agency "
                "guidance for conventional conforming loans generally recommends a "
                "two-year history for this category while permitting shorter histories of "
                "at least 12 months with adequate positive factors; this version of the "
                "lender's policy does not adopt the shorter-history allowance."
            ),
            parameters={
                "required_history_months": 24,
                "shorter_history_allowed": False,
            },
            research_reference=(
                RESEARCH + ", 'Income model' - agency guidance generally recommends two "
                "years for bonus, commission, overtime and tip income while permitting "
                "at least 12 months with adequate positive factors."
            ),
        ),
    )
    + _VAR_COMMON,
    documentation=(
        "W-2 forms covering the full qualifying history.",
        "Year-to-date paystub separating base from variable earnings.",
        "Employment verification confirming the variable component is expected to "
        "continue.",
    ),
    related_policies=("POL-INC-002", "POL-INC-003", "POL-EMP-002"),
    version_note=(
        "Original standard: a firm 24-month history with no shorter-history allowance. "
        "Superseded on 2026-07-01."
    ),
)

POL_INC_004_V2 = Policy(
    policy_id="POL-INC-004",
    title="Bonus, Overtime, Commission and Tip Income",
    version="2.0",
    effective_date=V2,
    supersedes="POL-INC-004 v1.0",
    family="income-variable",
    priority=49,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how earnings that vary period to period are qualified. These "
    "earnings are often the difference between a file that fits and one that does not, "
    "which is precisely why the history requirement matters.",
    scope_note="Applies to bonus, overtime, commission and tip earnings paid on top of "
    "a base wage or salary. Income from a business the borrower owns is governed by "
    "POL-INC-005 regardless of how it is labelled on a paystub.",
    rules=(
        Rule(
            rule_id="INC-VAR-001",
            title="Required earnings history, with a shorter-history allowance",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Variable earnings require a 24-month history with the same employer or "
                "in the same line of work. A history of at least 12 months may be used "
                "where the earnings are stable or rising and at least two positive "
                "factors from INC-VAR-005 are documented; in that case the qualifying "
                "amount is 75 percent of the 12-month average, and the file is routed "
                "for underwriter review. Version 1.0 of this policy excluded the variable "
                "component outright where 24 months were unavailable, so a borrower with "
                "14 months of stable commission qualifies on part of it under this "
                "version and on none of it under version 1.0."
            ),
            parameters={
                "required_history_months": 24,
                "shorter_history_allowed": True,
                "minimum_history_months": 12,
                "shorter_history_haircut": 0.75,
                "min_positive_factors": 2,
            },
            requires_human_review=True,
            research_reference=(
                RESEARCH + ", 'Income model' - agency guidance permits shorter histories "
                "of at least 12 months with adequate positive factors; the haircut is "
                "synthetic."
            ),
        ),
    )
    + _VAR_COMMON
    + (
        Rule(
            rule_id="INC-VAR-005",
            title="Positive factors supporting a shorter history",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PROCESS",
            statement=(
                "The positive factors recognised for INC-VAR-001 are: the variable "
                "component represents less than 25 percent of total qualifying income; "
                "the employer confirms the variable component is contractual rather than "
                "discretionary; the borrower has at least 24 months in the same line of "
                "work with a prior employer; and the earnings trend across the available "
                "history is flat or rising. Each factor relied upon is named in the "
                "decision record."
            ),
            parameters={
                "factor_max_variable_share": 0.25,
                "factor_contractual_confirmation": True,
                "factor_min_same_line_of_work_months": 24,
                "factor_trend": "flat or rising",
            },
            cross_refs=("POL-EMP-002",),
        ),
    ),
    documentation=(
        "W-2 forms covering the available history.",
        "Year-to-date paystub separating base from variable earnings.",
        "Named documentation for each positive factor relied upon.",
    ),
    related_policies=("POL-INC-002", "POL-INC-003", "POL-EMP-002"),
    version_note=(
        "Introduced the 12-month shorter-history allowance with a 75 percent haircut "
        "and the named positive-factor list INC-VAR-005."
    ),
)


# ---------------------------------------------------------------------------
# 18 - Self-employment
# ---------------------------------------------------------------------------

POL_INC_005 = Policy(
    policy_id="POL-INC-005",
    title="Self-Employment Income",
    version="1.0",
    effective_date=V1,
    family="income-self-employed",
    priority=49,
    product_scope=ALL_PRODUCTS,
    requires_human_review=True,
    purpose="Defines how income from a business the borrower owns is qualified. The "
    "governing idea is that self-employment income is a cash-flow analysis, not a "
    "revenue figure: what matters is what the business can sustainably distribute.",
    scope_note="Applies where the borrower owns 25 percent or more of the business "
    "generating the income, regardless of whether the borrower receives a W-2 from it. "
    "Every application relying on self-employment income is reviewed by a human "
    "underwriter.",
    definitions=(
        (
            "Self-employed",
            "Ownership of 25 percent or more of the business generating the income. A "
            "borrower who receives a W-2 from a business they own at or above this level "
            "is self-employed for underwriting purposes.",
        ),
        (
            "Add-back",
            "A non-cash expense deducted on the return that is added back to cash flow, "
            "such as depreciation or depletion. Add-backs are itemised individually; an "
            "unexplained aggregate add-back is not acceptable.",
        ),
    ),
    rules=(
        Rule(
            rule_id="INC-SEB-001",
            title="Ownership test determines the analysis method",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="PASS_FAIL",
            statement=(
                "Ownership of 25 percent or more makes the borrower self-employed and "
                "requires the cash-flow analysis in this document. Below 25 percent the "
                "borrower is treated as an employee under POL-INC-002 or POL-INC-003. "
                "Ownership percentage is evidenced from the tax return or the business's "
                "own records, not from the application alone."
            ),
            parameters={"self_employment_ownership_threshold": 0.25},
            evidence=("Tax return schedules showing ownership", "Business records"),
        ),
        Rule(
            rule_id="INC-SEB-002",
            title="Required history and returns",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Two years of personal tax returns are required, together with business "
                "returns where the business files separately. One year may suffice where "
                "the business has operated for at least five years, the borrower has at "
                "least five years in the same line of work, and the current-year income "
                "is stable or rising. Published agency guidance likewise provides "
                "circumstances in which one year can be sufficient, which is why a blanket "
                "'always require two years' rule would be wrong."
            ),
            parameters={
                "standard_years_required": 2,
                "reduced_years_allowed": 1,
                "reduced_min_business_years": 5,
                "reduced_min_line_of_work_years": 5,
                "reduced_trend_requirement": "stable or rising",
            },
            evidence=(
                "Personal tax returns with all schedules",
                "Business tax returns where separately filed",
                "Evidence the business is currently operating",
            ),
            research_reference=(
                RESEARCH + ", 'Income model' - agency guidance provides circumstances in "
                "which one year may suffice, demonstrating why 'always require two tax "
                "returns' is an invalid universal rule."
            ),
        ),
        Rule(
            rule_id="INC-SEB-003",
            title="Cash-flow analysis, not revenue",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "Qualifying income is the borrower's share of business cash flow: net "
                "profit, plus itemised non-cash add-backs, less any non-recurring income "
                "and less obligations the business does not demonstrably cover. Gross "
                "receipts are never qualifying income. Where the borrower's ownership is "
                "below 100 percent, only the borrower's share is used, and only where the "
                "borrower can demonstrate access to it."
            ),
            parameters={
                "basis": "net profit + itemised add-backs - non-recurring income",
                "ownership_proration": True,
                "gross_receipts_usable": False,
            },
        ),
        Rule(
            rule_id="INC-SEB-004",
            title="Declining business income",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Where the most recent year's cash flow is more than 20 percent below "
                "the prior year, the most recent year alone is used rather than the "
                "two-year average, and the file is routed for review with an "
                "explanation of the decline. A declining business averaged with a strong "
                "prior year produces a qualifying figure the business is no longer "
                "generating."
            ),
            parameters={
                "decline_trigger": 0.20,
                "treatment": "use the most recent year only",
            },
            requires_human_review=True,
        ),
        Rule(
            rule_id="INC-SEB-005",
            title="Current-period evidence",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Where the most recent tax return is more than 120 days old at the note "
                "date, a current profit and loss statement and business account "
                "statements covering the intervening period are required. The current "
                "evidence is used to confirm the business is still operating at the level "
                "the returns showed, not to replace the return-based calculation."
            ),
            parameters={
                "trigger_return_age_days": 120,
                "current_evidence": "profit and loss statement plus business account statements",
            },
            condition_template=(
                "Provide a current profit and loss statement and business account "
                "statements covering the period since the most recent tax return."
            ),
            cross_refs=("POL-DOC-001",),
        ),
        Rule(
            rule_id="INC-SEB-006",
            title="Mandatory human review",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PROCESS",
            statement=(
                "Every application relying on self-employment income is reviewed by a "
                "human underwriter before a recommendation is issued. Tax and cash-flow "
                "judgement is outside what an automated component may settle on its own, "
                "and the add-back decisions in particular require a reviewer who can see "
                "the whole return."
            ),
            requires_human_review=True,
            parameters={"reason_code": "HR-SELF-EMPLOYED-COMPLEXITY"},
            research_reference=(
                RESEARCH + ", 'Human-in-the-loop classification' - self-employed complex "
                "returns are classified HUMAN REVIEW REQUIRED for the MVP."
            ),
            cross_refs=("POL-UWR-001",),
        ),
    ),
    documentation=(
        "Personal and, where applicable, business tax returns with all schedules.",
        "Current profit and loss statement where INC-SEB-005 requires it.",
        "Evidence the business is currently operating.",
        "The itemised add-back worksheet supporting the cash-flow calculation.",
    ),
    related_policies=("POL-INC-001", "POL-UWR-001", "POL-DOC-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 19 - Rental income
# ---------------------------------------------------------------------------

POL_INC_006 = Policy(
    policy_id="POL-INC-006",
    title="Rental Income",
    version="1.0",
    effective_date=V1,
    family="income-rental",
    priority=49,
    product_scope=ALL_PRODUCTS,
    occupancy_scope=ALL_OCCUPANCY,
    purpose="Defines how rent from an investment property or from additional units of "
    "the subject property is qualified. Rental income is the only income type in this "
    "corpus that can be negative, and the negative case is the one most often handled "
    "incorrectly.",
    scope_note="Applies to rent from property the borrower owns, whether the subject "
    "property or another. Rent from a property being sold before closing is excluded "
    "entirely.",
    rules=(
        Rule(
            rule_id="INC-RNT-001",
            title="Vacancy factor",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "Gross rent is reduced by a 25 percent vacancy and maintenance factor "
                "before any other adjustment. The factor applies whether or not the "
                "property is currently tenanted, because it represents expected vacancy "
                "and upkeep across the holding period rather than current occupancy."
            ),
            parameters={"vacancy_factor": 0.25, "applies_when_tenanted": True},
        ),
        Rule(
            rule_id="INC-RNT-002",
            title="Net rental income and negative rent",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "Net rental income is gross rent after the vacancy factor, less the "
                "property's full housing expense including its mortgage payment, taxes, "
                "insurance and association dues. A positive result is added to qualifying "
                "income. A negative result is added to monthly obligations as a "
                "liability - it is never recorded as zero income. Discarding a negative "
                "result understates the borrower's obligations and is a calculation "
                "defect."
            ),
            parameters={
                "formula": "gross rent * (1 - vacancy factor) - property PITIA",
                "negative_treatment": "add the absolute value to monthly obligations",
            },
            cross_refs=("POL-LIA-001", "POL-DTI-001"),
        ),
        Rule(
            rule_id="INC-RNT-003",
            title="Evidence hierarchy",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Where the property appears on the borrower's most recent tax return, "
                "the return governs the rental calculation. Where it does not - a "
                "recently acquired property, or one recently placed in service - a "
                "current executed lease plus the valuation's rent schedule may be used. A "
                "lease alone, with no supporting valuation evidence, is not sufficient "
                "for a property that has never appeared on a return."
            ),
            parameters={
                "primary_evidence": "most recent tax return schedule",
                "alternative_evidence": "executed lease plus appraisal rent schedule",
                "lease_alone_sufficient": False,
            },
            evidence=(
                "Tax return rental schedule",
                "Executed lease agreement",
                "Appraisal comparable rent schedule",
            ),
            condition_template=(
                "Provide the tax return schedule or an executed lease with the "
                "valuation's rent schedule for property {property_id}."
            ),
            research_reference=(
                RESEARCH + ", 'Income model' - rental evidence is tax returns, lease, "
                "appraisal or rental analysis depending on the case; unsupported leases "
                "and related-party arrangements are the principal risks."
            ),
        ),
        Rule(
            rule_id="INC-RNT-004",
            title="Related-party leases",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "A lease with a party related to the borrower requires evidence that "
                "the rent is at market - normally the valuation's comparable rent "
                "schedule - and routes the file for review. Rent materially above market "
                "on a related-party lease is treated as unsupported and reduced to the "
                "market figure."
            ),
            parameters={"treatment_above_market": "reduce to the market rent figure"},
            requires_human_review=True,
            cross_refs=("POL-FRD-001",),
        ),
    ),
    documentation=(
        "Tax return rental schedules for every owned rental property.",
        "Executed leases where relied upon.",
        "Valuation rent schedule for the subject property where additional units exist.",
    ),
    related_policies=("POL-LIA-001", "POL-DTI-001", "POL-VAL-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 20 - Other qualifying income
# ---------------------------------------------------------------------------

POL_INC_007 = Policy(
    policy_id="POL-INC-007",
    title="Other Qualifying Income",
    version="1.0",
    effective_date=V1,
    family="income-other",
    priority=49,
    product_scope=ALL_PRODUCTS,
    purpose="Covers retirement, pension, social-security and other benefit income, "
    "investment income, support payments and military allowances. These sources share "
    "one analytical question - will the amount continue - and one prohibition: the "
    "source itself is never a reason to discount the amount.",
    scope_note="Applies to every income type not covered by POL-INC-002 through "
    "POL-INC-006.",
    rules=(
        Rule(
            rule_id="INC-OTH-001",
            title="Retirement, pension and benefit income",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Retirement, pension, annuity, disability and social-security income "
                "qualify at the verified periodic amount where an award letter, benefit "
                "statement or account statement evidences the amount and, where "
                "applicable, its end date. Income with no stated end date is presumed to "
                "continue. Where the income is not subject to federal income tax and that "
                "status is documented, the gross-up in INC-GEN-005 applies."
            ),
            parameters={
                "evidence": "award letter, benefit statement or account statement",
                "no_end_date": "presumed continuing",
            },
            evidence=("Award letter or benefit statement", "Recent deposit evidence"),
            cross_refs=("POL-INC-001",),
        ),
        Rule(
            rule_id="INC-OTH-002",
            title="Benefit income is never discounted for its source",
            source_category="REGULATORY",
            severity="HARD_FAIL",
            outcome_type="PROCESS",
            statement=(
                "Social-security, disability, public-assistance and retirement income "
                "are analysed on exactly the same basis as wage income: verified amount "
                "and likely continuance. Applying an additional haircut, a shorter "
                "continuance window or an extra documentation burden to these sources "
                "because of what they are is prohibited discrimination, not caution."
            ),
            research_reference=(
                RESEARCH + ", 'Income model' - a future AI must not penalise income "
                "simply because it comes from Social Security, retirement or another "
                "public-assistance source."
            ),
            cross_refs=("POL-CRD-001", "POL-DEC-001"),
        ),
        Rule(
            rule_id="INC-OTH-003",
            title="Interest and dividend income",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="CALCULATION",
            statement=(
                "Interest and dividend income qualify at the two-year average from tax "
                "returns, reduced proportionally for any of the generating assets that "
                "will be consumed to close the transaction. An asset cannot simultaneously "
                "fund the down payment and generate qualifying income; counting it twice "
                "is the characteristic error in this category."
            ),
            parameters={
                "averaging_years": 2,
                "reduce_for_consumed_assets": True,
            },
            evidence=("Tax returns", "Account statements evidencing the holdings"),
            cross_refs=("POL-AST-001",),
        ),
        Rule(
            rule_id="INC-OTH-004",
            title="Support payments the borrower chooses to disclose",
            source_category="REGULATORY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Alimony, child support and maintenance need not be disclosed unless the "
                "borrower chooses to rely on them for qualification. Where the borrower "
                "does rely on them, a legal order or agreement establishing the amount "
                "and its end date is required, together with evidence of receipt for the "
                "most recent six months. Income terminating within the continuance window "
                "in INC-GEN-003 is excluded."
            ),
            parameters={
                "required_receipt_months": 6,
                "disclosure": "at the borrower's election only",
            },
            evidence=("Court order or written agreement", "Six months of receipt evidence"),
            research_reference=(
                RESEARCH + ", 'Income model' and 'Regulatory and agency landscape' - "
                "Regulation B restricts requests about support obligations and the "
                "borrower's reliance is elective."
            ),
        ),
        Rule(
            rule_id="INC-OTH-005",
            title="Military pay and allowances",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="CALCULATION",
            statement=(
                "Base military pay qualifies as salaried income. Housing and subsistence "
                "allowances qualify where the leave and earnings statement evidences them "
                "and they are expected to continue; they are commonly non-taxable, in "
                "which case INC-GEN-005 applies. Temporary or duty-specific allowances "
                "such as hazard or deployment pay are excluded, because they end when the "
                "duty ends."
            ),
            parameters={
                "base_pay": "qualify as salaried",
                "housing_and_subsistence": "qualify where evidenced and continuing",
                "temporary_duty_pay": "excluded",
            },
            evidence=("Leave and earnings statement", "Employment verification"),
            cross_refs=("POL-VA-001", "POL-INC-002"),
        ),
    ),
    documentation=(
        "Award letters, benefit statements or orders for every source relied upon.",
        "Evidence of receipt for the period each rule requires.",
        "Documentation of non-taxable status where a gross-up is applied.",
    ),
    related_policies=("POL-INC-001", "POL-AST-001", "POL-VA-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 21 - Employment verification
# ---------------------------------------------------------------------------

POL_EMP_001 = Policy(
    policy_id="POL-EMP-001",
    title="Employment Verification",
    version="1.0",
    effective_date=V1,
    family="employment-verification",
    priority=47,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how employment is verified, when it must be re-verified, and how "
    "a verification that contradicts the application is handled.",
    scope_note="Applies to every employed borrower. Self-employed borrowers verify the "
    "existence and operation of the business under POL-INC-005 instead.",
    rules=(
        Rule(
            rule_id="EMP-VER-001",
            title="Independent verification is required",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Employment must be verified independently of documents the borrower "
                "supplied: a written verification obtained directly from the employer, a "
                "verbal verification recorded with the name and title of the person "
                "contacted, or a validated third-party verification report. A paystub "
                "supplied by the borrower is evidence of income; it is not independent "
                "verification of employment."
            ),
            parameters={
                "acceptable_methods": (
                    "written employer verification, recorded verbal verification, "
                    "validated third-party report"
                ),
                "borrower_supplied_documents_sufficient": False,
            },
            evidence=(
                "Written verification of employment",
                "Verbal verification record naming the contact and date",
                "Third-party verification report",
            ),
            condition_template="Obtain independent employment verification for {employer}.",
        ),
        Rule(
            rule_id="EMP-VER-002",
            title="Re-verification before closing",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "Employment is re-verified within ten business days of the note date. "
                "Where the re-verification shows the borrower is no longer employed, or "
                "shows materially different terms, the income calculation and the "
                "affordability result are re-run before closing proceeds. A file cleared "
                "to close on employment that has since ended is a control failure, not a "
                "timing inconvenience."
            ),
            parameters={"reverification_window_business_days": 10},
            condition_template="Re-verify employment within ten business days of closing.",
            cross_refs=("POL-UWR-001",),
        ),
        Rule(
            rule_id="EMP-VER-003",
            title="Verification that contradicts the application",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="REFER",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Where the verification reports an employer name, job title, start date "
                "or compensation that differs materially from the application, the "
                "verified value governs, the discrepancy is recorded with both values and "
                "their sources, and the file is routed for review. A start date differing "
                "by more than 60 days, or an employer name that is similar but not "
                "identical, is treated as material."
            ),
            parameters={
                "material_start_date_variance_days": 60,
                "similar_but_not_identical_employer": "material",
                "governing_value": "the verified value",
            },
            requires_human_review=True,
            research_reference=(
                RESEARCH + ", 'Missing/conflicting data workflow' - an application start "
                "date differing from the verification requires an authoritative timeline "
                "and a condition if unresolved."
            ),
            cross_refs=("POL-FRD-001",),
        ),
        Rule(
            rule_id="EMP-VER-004",
            title="Verification freshness",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "An employment verification is valid for 60 days from its completion "
                "date for underwriting purposes, subject to the pre-closing "
                "re-verification in EMP-VER-002. A verification older than that is "
                "refreshed rather than relied upon."
            ),
            parameters={"max_age_days": 60},
            cross_refs=("POL-DOC-001",),
        ),
    ),
    documentation=(
        "The verification record itself, with method, date and the contact where verbal.",
        "The pre-closing re-verification record.",
    ),
    related_policies=("POL-INC-002", "POL-EMP-002", "POL-DOC-001"),
    version_note="Initial version.",
)


# ---------------------------------------------------------------------------
# 22 - Employment continuity
# ---------------------------------------------------------------------------

POL_EMP_002 = Policy(
    policy_id="POL-EMP-002",
    title="Employment Continuity, Gaps and Future Employment",
    version="1.0",
    effective_date=V1,
    family="employment-continuity",
    priority=47,
    product_scope=ALL_PRODUCTS,
    purpose="Defines how much employment history is required, how gaps are treated, "
    "and when employment that has not yet begun may be used. A job change is not by "
    "itself a negative: what matters is whether the history supports an expectation of "
    "continuing income.",
    scope_note="Applies to every employed borrower.",
    rules=(
        Rule(
            rule_id="EMP-CNT-001",
            title="Two-year history requirement",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "A 24-month employment history is required, and it may span several "
                "employers. Time in full-time education or military service in the same "
                "field counts toward the requirement where documented. Fewer than 24 "
                "months of combined history routes the file for review rather than "
                "failing it, because a shorter history with strong continuity can still "
                "support the income."
            ),
            parameters={
                "required_history_months": 24,
                "education_and_service_count": True,
                "shortfall_treatment": "refer, not fail",
            },
            requires_human_review=True,
            evidence=("Employment history covering 24 months", "Transcripts or service records"),
        ),
        Rule(
            rule_id="EMP-CNT-002",
            title="Job change within the same field",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "A change of employer within the same field, with no reduction in "
                "compensation, is acceptable without additional conditions once the "
                "borrower has completed at least one full pay period with the new "
                "employer. A change into a different field, or one involving a "
                "compensation structure change - salary to commission, for example - "
                "routes the file for review, because the prior history no longer predicts "
                "the new earnings."
            ),
            parameters={
                "min_pay_periods_with_new_employer": 1,
                "field_change": "refer",
                "compensation_structure_change": "refer",
            },
            requires_human_review=True,
            cross_refs=("POL-INC-004",),
        ),
        Rule(
            rule_id="EMP-CNT-003",
            title="Employment gaps",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_FAIL",
            statement=(
                "A gap of 30 days or more in the 24-month history requires a written "
                "explanation. A gap of six months or more additionally requires the "
                "borrower to have been in the current position for at least six months "
                "before the income is used. Gaps are documented, not penalised: the "
                "purpose is to establish the current position's stability, not to score "
                "the borrower's past."
            ),
            parameters={
                "explanation_required_gap_days": 30,
                "extended_gap_months": 6,
                "min_current_tenure_after_extended_gap_months": 6,
            },
            condition_template=(
                "Provide a written explanation of the employment gap between "
                "{gap_start} and {gap_end}."
            ),
        ),
        Rule(
            rule_id="EMP-CNT-004",
            title="Employment that has not yet started",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="CONDITIONAL",
            outcome_type="PASS_REFER_FAIL",
            statement=(
                "Income from employment beginning after the note date may be used only "
                "where a non-contingent written offer states the position, the "
                "compensation and the start date; the start date falls within 90 days of "
                "the note date; and the borrower has verified reserves covering the "
                "housing expense and all obligations for the entire period between "
                "closing and the first payment from the new employer. The file is routed "
                "for review in every case."
            ),
            parameters={
                "max_days_to_start": 90,
                "offer_must_be_non_contingent": True,
                "reserves_must_cover_gap_period": True,
            },
            requires_human_review=True,
            evidence=(
                "Non-contingent written offer stating position, compensation and start date",
                "Asset evidence covering the gap period",
            ),
            condition_template=(
                "Provide the non-contingent offer letter and reserve evidence covering "
                "the period to {start_date}."
            ),
            cross_refs=("POL-AST-003",),
        ),
        Rule(
            rule_id="EMP-CNT-005",
            title="Tenure is computed deterministically",
            source_category="SYNTHETIC_INTERNAL_POLICY",
            severity="HARD_FAIL",
            outcome_type="CALCULATION",
            statement=(
                "Employment tenure is the whole number of months between the verified "
                "start date and the application date, computed by the committed "
                "calculation code. Where the application's stated start date differs from "
                "the verified start date, tenure is computed from the verified date and "
                "the difference is recorded under EMP-VER-003."
            ),
            parameters={
                "formula": "whole months from verified start date to application date",
                "source_date": "verified start date",
            },
            cross_refs=("POL-EMP-001",),
        ),
    ),
    documentation=(
        "A 24-month employment history with dates for every position.",
        "Written explanations for gaps of 30 days or more.",
        "The offer letter and reserve evidence where EMP-CNT-004 applies.",
    ),
    related_policies=("POL-EMP-001", "POL-INC-004", "POL-AST-003"),
    version_note="Initial version.",
)


PART_B_POLICIES = (
    POL_INC_001,
    POL_INC_002,
    POL_INC_003,
    POL_INC_004_V1,
    POL_INC_004_V2,
    POL_INC_005,
    POL_INC_006,
    POL_INC_007,
    POL_EMP_001,
    POL_EMP_002,
)
