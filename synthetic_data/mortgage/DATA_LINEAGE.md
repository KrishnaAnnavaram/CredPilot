# Data Lineage

How a number in this dataset can be traced back to the document it came from, and
forward to the decision it produced.

The research report sets the standard: a lineage record should answer more than
"DTI = 44%". It should answer *which* formula version, from *which* inputs, supported
by *which* evidence, against *which* policy rule version, producing *which* decision
reason. Every link in that chain is a column in this dataset.

---

## The four chains

### 1. Income → affordability → decision

```text
SOURCE EMPLOYMENT / INCOME DOCUMENT
  documents.document_id · paystub, W-2, verification of employment
        ↓  document_extractions.field_name = ytd_gross, annual_wages, employment_start_date
VERIFIED INCOME
  income.verified_monthly_amount        (what the evidence establishes)
        ↓  income.qualifying_rule_id → the policy rule that permits the amount
QUALIFYING MONTHLY INCOME
  underwriting_calculations.calculation_name = qualifying_monthly_income
  formula_version v1.0.0 · input_fields = income.qualifying_monthly_amount
        ↓  divides into
DTI
  underwriting_calculations.back_end_dti
  input_fields = total_monthly_debt | qualifying_monthly_income
        ↓  evaluated by
ELIGIBILITY
  rule_evaluations (DTI-CONV-001) → eligibility_results.result
        ↓  contributes to
RISK
  risk_flags.category = AFFORDABILITY · evidence = the calculation that produced it
        ↓  summarised as
RECOMMENDATION
  decisions.result → decision_reasons.reason_text, rule_id, policy_version
```

The declared amount never enters this chain. `income.declared_monthly_amount` is
retained so the file can show what the applicant said and how it differed, but
`INC-GEN-002` requires the qualifying amount to be less than or equal to the verified
amount, and the validator enforces that invariant on all 99 income rows.

### 2. Assets → funds to close → reserves

```text
ASSETS
  assets.asset_id · declared_balance, verified_balance
        ↓  AST-ELG-001 applies the category haircut
VERIFIED FUNDS
  assets.eligible_close_amount  and  assets.eligible_reserve_amount
  (two independent answers: usable at closing, and countable as a reserve)
        ↓  measured against
CASH TO CLOSE
  underwriting_calculations.cash_to_close
  input_fields = down_payment_amount | closing_costs | prepaids_and_escrow
                 | seller_credits | earnest_money_paid
        ↓  AST-FTC-004 draws non-reserve sources first, then reserve-eligible
           assets in ascending asset_id order
REMAINING ASSETS
  underwriting_calculations.post_close_reserves
        ↓  divided by the qualifying housing expense
RESERVES
  underwriting_calculations.months_reserves → rule_evaluations (AST-RSV-002)
```

Reserves are not a separate figure sitting beside the assets. They are what the draw
left behind, which is why the validator recomputes them by replaying the draw from
the asset rows alone rather than trusting the stored value.

### 3. Property → value → leverage

```text
PROPERTY
  properties.property_id · property_type, units, occupancy_type
        ↓
PURCHASE PRICE / APPRAISED VALUE
  properties.purchase_price  ·  appraisals.appraised_value
  (or no appraisal row at all, where valuation_method = value_acceptance)
        ↓  CONV-PUR-002: purchase uses the lower of the two;
           CONV-RTR-002 / CONV-COR-002: a refinance uses the value
VALUE USED FOR CALCULATION
  properties.value_used_for_ltv        (a distinct column, on purpose)
        ↓
LTV
  underwriting_calculations.ltv
  input_fields = loans.base_loan_amount | properties.value_used_for_ltv
        ↓
POLICY EVALUATION
  rule_evaluations (CONV-PUR-002 / CONV-COR-002 / JMB-ELG-002 / FHA-OVL-002 /
                    USD-OVL-003 / VA-OVL-002)
```

Leverage is measured against the **base** loan amount, not the note amount. Where a
programme premium is financed into the note — FHA, VA and USDA — the payment rises
but the leverage test does not, which is why `loans` carries both columns.

### 4. Policy version → rule → reason → audit

```text
POLICY VERSION
  policies.policy_id + version, selected by applications.underwriting_as_of_date
  (never by "latest" — GEN-ELG-002)
        ↓
APPLICABLE RULE
  policy_rules.rule_id at that version, with its parameters
        ↓
ELIGIBILITY / RISK RESULT
  rule_evaluations.outcome, observed_value, comparator, threshold_value
        ↓
DECISION REASON
  decision_reasons.reason_code, rule_id, policy_version, evidence_reference
        ↓
AUDIT RECORD
  audit_events: authorise → classify → select_policy_versions → extract →
                run_calculations → evaluate_rules → screen_risk →
                produce_recommendation → route_to_human_review
  all sharing one correlation_id
```

---

## Worked example: APP-000056

This is the second half of the policy-boundary pair. It is chosen because the
lineage is the entire point of the case: nothing about the borrower is unusual, and
the outcome turns on which version of one policy was in force.

**The file.** Application dated 2026-07-08. Conventional conforming purchase, primary
residence, single borrower BORR-000067, single salaried income.

**Step 1 — evidence to verified income.**

| Link | Value |
| --- | --- |
| `documents` | a paystub, a W-2 and a verification of employment |
| `document_extractions.ytd_gross` | annualises to the stated salary within tolerance, so `INC-SAL-003` passes |
| `income.verified_monthly_amount` | `12,591.67` |
| `income.qualifying_rule_id` | `INC-SAL-001` — annual salary divided by 12 |

**Step 2 — housing expense.** `underwriting_calculations.housing_expense_pitia` =
`3,902.92`, built from five inputs it names explicitly:

| Component | Value | Source column |
| --- | --- | --- |
| Principal and interest | 2,775.86 | `loans.principal_and_interest` (432,400 at 6.65% over 360 months) |
| Property tax | 708.92 | `properties.annual_property_tax` ÷ 12 |
| Hazard insurance | 137.08 | `properties.annual_hazard_premium` ÷ 12 |
| Association dues | 0.00 | `properties.monthly_hoa` |
| Mortgage insurance | 281.06 | `loans.monthly_mortgage_insurance` — required because LTV is 92% |

That last line is the one most easily dropped. Omitting it would understate the ratio
by 2.2 percentage points and flip this file's outcome, which is why `CONV-PUR-003`
states that the premium belongs in the housing expense and why the validator rebuilds
the figure from its components rather than reading it.

**Step 3 — obligations.** Four liabilities, each with its own row and inclusion rule:

| Obligation | Monthly | Balance |
| --- | ---: | ---: |
| Auto loan | 556.72 | 23,253.24 |
| Student loan | 425.73 | 31,237.66 |
| Revolving credit card | 392.98 | 13,099.33 |
| Instalment personal | 261.98 | 8,485.86 |

`total_monthly_debt` = 3,902.92 + 1,637.41 = **5,540.33**.

**Step 4 — the ratio.** 5,540.33 ÷ 12,591.67 = **0.4400**, recorded with
`formula_version v1.0.0` and `input_fields = total_monthly_debt |
qualifying_monthly_income`.

**Step 5 — policy selection.** The as-of date is 2026-07-08. `POL-DTI-001` has two
versions: v1.0 effective 2026-01-01 and expiring 2026-07-01, and v2.0 effective
2026-07-01. The as-of date falls in the second window, so v2.0 applies.

**Step 6 — evaluation.**

```
rule_id          DTI-CONV-001
policy_id        POL-DTI-001      policy_version 2.0      effective 2026-07-01
outcome          FAIL
observed_value   0.4400    comparator <=    threshold_value 0.43
reason           Back-end debt-to-income 44.00% against the applicable limit of
                 43.00%. The extension to 45.00% was not available: 0 documented
                 compensating factor(s) against the 2 required. The affordability
                 limit is breached.
```

**Step 7 — decision and reason.** `decisions` records
`DECLINE_RECOMMENDATION` by an `AUTOMATED_COMPONENT` at the
`underwriting_recommendation` stage, and a second row at the `credit_decision` stage
holding `PENDING_HUMAN_REVIEW` with `actor_type = HUMAN`. The copilot does not make
the credit decision; `human_reviews` records the queue and the authorised role.

`decision_reasons` carries reason code `RSN-DTICONV001`, naming the rule, the policy
version, and the evidence reference — the two calculations the ratio came from.

### Why the pair matters

| Application | As-of date | DTI | Policy version | Threshold | Outcome |
| --- | --- | ---: | --- | ---: | --- |
| APP-000055 | 2026-06-25 | 0.4400 | POL-DTI-001 v1.0 | 0.45 | PASS → routed to a human as borderline |
| APP-000056 | 2026-07-08 | 0.4400 | POL-DTI-001 v2.0 | 0.43 | **FAIL** → decline recommendation |
| APP-000057 | 2026-07-08 | 0.4400 | POL-DTI-001 v2.0 | 0.45 | PASS — the compensating-factor extension applied |

Identical ratios; three different results. The first two differ only by date. The
second and third differ only by whether the file carried two documented compensating
factors. A retrieval component that fetches the newest version of a policy gets
APP-000055 wrong; one that ignores the extension conditions gets APP-000057 wrong.

---

## Querying the lineage

The chains above are joins, not prose. A few that answer real questions:

**Which document supported this income figure?**

```
income → (application_id, borrower_id)
      → documents (document_type in paystub, w2, employment_verification)
      → document_extractions (field_name = ytd_gross, annual_wages)
```

**Which rule version produced this reason, and was it the right one?**

```
decision_reasons.rule_id + policy_version
      → rule_evaluations (same application_id, same rule_id)
      → policies (policy_id, version, effective_date, expiration_date)
      → compare against applications.underwriting_as_of_date
```

The validator runs exactly this last comparison across all 1,827 evaluations. Any
evaluation citing a version that was not in force on its application's as-of date is
a failure, not a warning.

**What did the system actually do, in order?**

```
audit_events where application_id = ? order by sequence
```

Every application carries a contiguous sequence under a single `correlation_id`,
beginning with authorisation and ending with the recommendation — and, where policy
required it, with the routing to a human.
