---
policy_id: POL-INC-004
title: "Bonus, Overtime, Commission and Tip Income"
version: 2.0
family: income-variable
effective_date: 2026-07-01
expiration_date: null
product_scope:
  - conventional_conforming
  - jumbo
  - fha
  - va
  - usda
occupancy_scope:
  - primary_residence
  - second_home
  - investment
purpose_scope:
  - purchase
  - rate_term_refinance
  - cash_out_refinance
jurisdiction: US
source_category: SYNTHETIC_INTERNAL_POLICY
priority: 49
supersedes: "POL-INC-004 v1.0"
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - INC-VAR-001
  - INC-VAR-002
  - INC-VAR-003
  - INC-VAR-004
  - INC-VAR-005
synthetic: true
---

# Bonus, Overtime, Commission and Tip Income

**POL-INC-004 · version 2.0 · effective 2026-07-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how earnings that vary period to period are qualified. These earnings are often the difference between a file that fits and one that does not, which is precisely why the history requirement matters.

## 2. Scope

Applies to bonus, overtime, commission and tip earnings paid on top of a base wage or salary. Income from a business the borrower owns is governed by POL-INC-005 regardless of how it is labelled on a paystub.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### INC-VAR-001 — Required earnings history, with a shorter-history allowance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Variable earnings require a 24-month history with the same employer or in the same line of work. A history of at least 12 months may be used where the earnings are stable or rising and at least two positive factors from INC-VAR-005 are documented; in that case the qualifying amount is 75 percent of the 12-month average, and the file is routed for underwriter review. Version 1.0 of this policy excluded the variable component outright where 24 months were unavailable, so a borrower with 14 months of stable commission qualifies on part of it under this version and on none of it under version 1.0.

| Parameter | Value |
| --- | --- |
| `required_history_months` | 24 |
| `shorter_history_allowed` | yes |
| `minimum_history_months` | 12 |
| `shorter_history_haircut` | 75% |
| `min_positive_factors` | 2 |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Income model' - agency guidance permits shorter histories of at least 12 months with adequate positive factors; the haircut is synthetic.

### INC-VAR-002 — Averaging method

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Qualifying variable income is the total verified variable earnings over the qualifying history divided by the number of months in that history. Where the history spans two W-2 years plus a year-to-date period, all three are summed and divided by the total elapsed months. Partial months are counted as whole months only where the paystub's year-to-date field supports it.

| Parameter | Value |
| --- | --- |
| `formula` | total variable earnings over history / months in history |

### INC-VAR-003 — Declining variable income

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where the current-year annualised variable earnings are more than 20 percent below the prior full year, the lower current figure is used and the file is routed for review with a written explanation of the decline. Where the decline exceeds 40 percent, the variable component is excluded from qualifying income entirely unless the underwriter documents why it should be retained.

| Parameter | Value |
| --- | --- |
| `refer_decline_trigger` | 20% |
| `exclude_decline_trigger` | 40% |

**Condition raised when unsatisfied.** Provide a written explanation of the {decline_pct} decline in variable earnings and evidence of the expected forward level.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Income model' - volatile or declining variable income is the principal risk for this category.

### INC-VAR-004 — Commission income with significant unreimbursed expenses

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Where commission income represents more than 25 percent of the borrower's total income, tax-return evidence is obtained and documented unreimbursed business expenses are deducted from the qualifying amount. Using gross commission without the expense deduction overstates the income actually available to service debt.

| Parameter | Value |
| --- | --- |
| `commission_share_trigger` | 25% |
| `expense_treatment` | deduct documented unreimbursed business expenses |

**Acceptable evidence.** Tax returns covering the qualifying history.

### INC-VAR-005 — Positive factors supporting a shorter history

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

The positive factors recognised for INC-VAR-001 are: the variable component represents less than 25 percent of total qualifying income; the employer confirms the variable component is contractual rather than discretionary; the borrower has at least 24 months in the same line of work with a prior employer; and the earnings trend across the available history is flat or rising. Each factor relied upon is named in the decision record.

| Parameter | Value |
| --- | --- |
| `factor_max_variable_share` | 25% |
| `factor_contractual_confirmation` | yes |
| `factor_min_same_line_of_work_months` | 24 |
| `factor_trend` | flat or rising |

**See also:** POL-EMP-002.

## 5. Documentation requirements

- W-2 forms covering the available history.
- Year-to-date paystub separating base from variable earnings.
- Named documentation for each positive factor relied upon.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-INC-002
- POL-INC-003
- POL-EMP-002

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| (prior) | before 2026-07-01 | Superseded by this version. Prior version identifier: POL-INC-004 v1.0. |
| 2.0 | 2026-07-01 | Introduced the 12-month shorter-history allowance with a 75 percent haircut and the named positive-factor list INC-VAR-005. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
