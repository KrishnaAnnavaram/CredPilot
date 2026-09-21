---
policy_id: POL-INC-005
title: "Self-Employment Income"
version: 1.0
family: income-self-employed
effective_date: 2026-01-01
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
supersedes: null
superseded_by: null
requires_human_review: true
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - INC-SEB-001
  - INC-SEB-002
  - INC-SEB-003
  - INC-SEB-004
  - INC-SEB-005
  - INC-SEB-006
synthetic: true
---

# Self-Employment Income

**POL-INC-005 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how income from a business the borrower owns is qualified. The governing idea is that self-employment income is a cash-flow analysis, not a revenue figure: what matters is what the business can sustainably distribute.

## 2. Scope

Applies where the borrower owns 25 percent or more of the business generating the income, regardless of whether the borrower receives a W-2 from it. Every application relying on self-employment income is reviewed by a human underwriter.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Self-employed.** Ownership of 25 percent or more of the business generating the income. A borrower who receives a W-2 from a business they own at or above this level is self-employed for underwriting purposes.

**Add-back.** A non-cash expense deducted on the return that is added back to cash flow, such as depreciation or depletion. Add-backs are itemised individually; an unexplained aggregate add-back is not acceptable.

## 4. Rules

### INC-SEB-001 — Ownership test determines the analysis method

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Ownership of 25 percent or more makes the borrower self-employed and requires the cash-flow analysis in this document. Below 25 percent the borrower is treated as an employee under POL-INC-002 or POL-INC-003. Ownership percentage is evidenced from the tax return or the business's own records, not from the application alone.

| Parameter | Value |
| --- | --- |
| `self_employment_ownership_threshold` | 25% |

**Acceptable evidence.** Tax return schedules showing ownership; Business records.

### INC-SEB-002 — Required history and returns

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

Two years of personal tax returns are required, together with business returns where the business files separately. One year may suffice where the business has operated for at least five years, the borrower has at least five years in the same line of work, and the current-year income is stable or rising. Published agency guidance likewise provides circumstances in which one year can be sufficient, which is why a blanket 'always require two years' rule would be wrong.

| Parameter | Value |
| --- | --- |
| `standard_years_required` | 2 |
| `reduced_years_allowed` | 1 |
| `reduced_min_business_years` | 5 |
| `reduced_min_line_of_work_years` | 5 |
| `reduced_trend_requirement` | stable or rising |

**Acceptable evidence.** Personal tax returns with all schedules; Business tax returns where separately filed; Evidence the business is currently operating.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Income model' - agency guidance provides circumstances in which one year may suffice, demonstrating why 'always require two tax returns' is an invalid universal rule.

### INC-SEB-003 — Cash-flow analysis, not revenue

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Qualifying income is the borrower's share of business cash flow: net profit, plus itemised non-cash add-backs, less any non-recurring income and less obligations the business does not demonstrably cover. Gross receipts are never qualifying income. Where the borrower's ownership is below 100 percent, only the borrower's share is used, and only where the borrower can demonstrate access to it.

| Parameter | Value |
| --- | --- |
| `basis` | net profit + itemised add-backs - non-recurring income |
| `ownership_proration` | yes |
| `gross_receipts_usable` | no |

### INC-SEB-004 — Declining business income

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where the most recent year's cash flow is more than 20 percent below the prior year, the most recent year alone is used rather than the two-year average, and the file is routed for review with an explanation of the decline. A declining business averaged with a strong prior year produces a qualifying figure the business is no longer generating.

| Parameter | Value |
| --- | --- |
| `decline_trigger` | 20% |
| `treatment` | use the most recent year only |

### INC-SEB-005 — Current-period evidence

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Where the most recent tax return is more than 120 days old at the note date, a current profit and loss statement and business account statements covering the intervening period are required. The current evidence is used to confirm the business is still operating at the level the returns showed, not to replace the return-based calculation.

| Parameter | Value |
| --- | --- |
| `trigger_return_age_days` | 120 |
| `current_evidence` | profit and loss statement plus business account statements |

**Condition raised when unsatisfied.** Provide a current profit and loss statement and business account statements covering the period since the most recent tax return.

**See also:** POL-DOC-001.

### INC-SEB-006 — Mandatory human review

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Every application relying on self-employment income is reviewed by a human underwriter before a recommendation is issued. Tax and cash-flow judgement is outside what an automated component may settle on its own, and the add-back decisions in particular require a reviewer who can see the whole return.

| Parameter | Value |
| --- | --- |
| `reason_code` | HR-SELF-EMPLOYED-COMPLEXITY |

**See also:** POL-UWR-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Human-in-the-loop classification' - self-employed complex returns are classified HUMAN REVIEW REQUIRED for the MVP.

## 5. Documentation requirements

- Personal and, where applicable, business tax returns with all schedules.
- Current profit and loss statement where INC-SEB-005 requires it.
- Evidence the business is currently operating.
- The itemised add-back worksheet supporting the cash-flow calculation.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-INC-001
- POL-UWR-001
- POL-DOC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
