---
policy_id: POL-CONV-002
title: Conventional Rate and Term Refinance Eligibility
version: 1.0
family: conventional-rate-term-refinance
effective_date: 2026-01-01
expiration_date: null
product_scope:
  - conventional_conforming
occupancy_scope:
  - primary_residence
  - second_home
  - investment
purpose_scope:
  - rate_term_refinance
jurisdiction: US
source_category: SYNTHETIC_INTERNAL_POLICY
priority: 30
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - CONV-RTR-001
  - CONV-RTR-002
  - CONV-RTR-003
  - CONV-RTR-004
synthetic: true
---

# Conventional Rate and Term Refinance Eligibility

**POL-CONV-002 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines eligibility for a limited-cash-out refinance that replaces existing mortgage debt without meaningful equity extraction. The distinguishing feature of this product is the denominator used for leverage and the strict limit on cash returned to the borrower.

## 2. Scope

Applies where the new loan pays off an existing first lien and, optionally, an eligible seasoned subordinate lien, and the borrower receives no more than the incidental cash permitted below. Any transaction exceeding that limit is a cash-out refinance under POL-CONV-003 regardless of how it was described at application.

- **Products:** conventional_conforming
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** rate_term_refinance
- **Jurisdiction:** US

## 3. Definitions

**Value used for leverage on a refinance.** The appraised or otherwise accepted current value of the property. There is no sales price in a refinance, so the purchase convention of taking the lower of two figures does not apply.

**Incidental cash.** Cash returned to the borrower at closing that arises from rounding the new loan amount and from escrow or prepaid adjustments, rather than from an intent to extract equity.

## 4. Rules

### CONV-RTR-001 — Cash returned to the borrower is capped

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Cash returned to the borrower at closing must not exceed the lesser of one percent of the new loan amount or 2,000. A transaction that returns more than this is a cash-out refinance and must be re-underwritten under POL-CONV-003, which applies lower leverage limits and a different credit standard. Re-labelling the transaction without re-running the leverage and credit rules is a policy-selection defect.

| Parameter | Value |
| --- | --- |
| `max_incidental_cash_pct_of_loan` | 1% |
| `max_incidental_cash_amount` | 2,000 |
| `reclassification_target` | POL-CONV-003 |

**See also:** POL-CONV-003.

### CONV-RTR-002 — Maximum leverage on a rate and term refinance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Loan-to-value is computed against the current accepted value and must not exceed the occupancy limit below. Where an existing subordinate lien is to remain in place rather than be paid off, the combined loan-to-value test governs and the subordinate payment is included in the qualifying housing expense.

| Parameter | Value |
| --- | --- |
| `max_ltv_primary_residence` | 95% |
| `max_ltv_second_home` | 90% |
| `max_ltv_investment` | 75% |
| `max_cltv_primary_residence` | 95% |

**See also:** POL-VAL-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - refinance LTV uses a different denominator from purchase; the thresholds are synthetic.

### CONV-RTR-003 — Existing mortgage payment history

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

The mortgage being refinanced must show no payment 30 or more days past due in the most recent 12 months. A single 30-day late in that window routes the file to an underwriter rather than failing it, because the surrounding circumstances determine whether the history is acceptable. Two or more such lates in the window is a hard failure under this product.

| Parameter | Value |
| --- | --- |
| `lookback_months` | 12 |
| `lates_30d_refer_at` | 1 |
| `lates_30d_fail_at` | 2 |

**Acceptable evidence.** Credit report mortgage tradeline; Mortgage payment history.

**See also:** POL-CRD-003.

### CONV-RTR-004 — Payoff figure must be evidenced

- **Source category:** `COMMON_INDUSTRY_PRACTICE` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The new loan amount must be supported by a current payoff statement for each lien being retired. Where the payoff statement postdates the loan amount used in the calculations, the funds-to-close calculation must be re-run, because the difference falls to the borrower.

**Acceptable evidence.** Payoff statement dated within the freshness window in POL-DOC-001.

**Condition raised when unsatisfied.** Provide a current payoff statement for lien {lien_id}.

**See also:** POL-AST-002, POL-DOC-001.

## 5. Documentation requirements

- Current payoff statement for each lien being retired.
- Evidence of the existing note terms where the benefit test is relied upon.
- Appraisal or accepted alternative valuation.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-CONV-003
- POL-VAL-001
- POL-CRD-003

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial product version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
