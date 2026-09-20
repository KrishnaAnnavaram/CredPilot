---
policy_id: POL-EMP-002
title: "Employment Continuity, Gaps and Future Employment"
version: 1.0
family: employment-continuity
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
priority: 47
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - EMP-CNT-001
  - EMP-CNT-002
  - EMP-CNT-003
  - EMP-CNT-004
  - EMP-CNT-005
synthetic: true
---

# Employment Continuity, Gaps and Future Employment

**POL-EMP-002 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how much employment history is required, how gaps are treated, and when employment that has not yet begun may be used. A job change is not by itself a negative: what matters is whether the history supports an expectation of continuing income.

## 2. Scope

Applies to every employed borrower.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### EMP-CNT-001 — Two-year history requirement

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A 24-month employment history is required, and it may span several employers. Time in full-time education or military service in the same field counts toward the requirement where documented. Fewer than 24 months of combined history routes the file for review rather than failing it, because a shorter history with strong continuity can still support the income.

| Parameter | Value |
| --- | --- |
| `required_history_months` | 24 |
| `education_and_service_count` | yes |
| `shortfall_treatment` | refer, not fail |

**Acceptable evidence.** Employment history covering 24 months; Transcripts or service records.

### EMP-CNT-002 — Job change within the same field

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A change of employer within the same field, with no reduction in compensation, is acceptable without additional conditions once the borrower has completed at least one full pay period with the new employer. A change into a different field, or one involving a compensation structure change - salary to commission, for example - routes the file for review, because the prior history no longer predicts the new earnings.

| Parameter | Value |
| --- | --- |
| `min_pay_periods_with_new_employer` | 1 |
| `field_change` | refer |
| `compensation_structure_change` | refer |

**See also:** POL-INC-004.

### EMP-CNT-003 — Employment gaps

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A gap of 30 days or more in the 24-month history requires a written explanation. A gap of six months or more additionally requires the borrower to have been in the current position for at least six months before the income is used. Gaps are documented, not penalised: the purpose is to establish the current position's stability, not to score the borrower's past.

| Parameter | Value |
| --- | --- |
| `explanation_required_gap_days` | 30 |
| `extended_gap_months` | 6 |
| `min_current_tenure_after_extended_gap_months` | 6 |

**Condition raised when unsatisfied.** Provide a written explanation of the employment gap between {gap_start} and {gap_end}.

### EMP-CNT-004 — Employment that has not yet started

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Income from employment beginning after the note date may be used only where a non-contingent written offer states the position, the compensation and the start date; the start date falls within 90 days of the note date; and the borrower has verified reserves covering the housing expense and all obligations for the entire period between closing and the first payment from the new employer. The file is routed for review in every case.

| Parameter | Value |
| --- | --- |
| `max_days_to_start` | 90 |
| `offer_must_be_non_contingent` | yes |
| `reserves_must_cover_gap_period` | yes |

**Acceptable evidence.** Non-contingent written offer stating position, compensation and start date; Asset evidence covering the gap period.

**Condition raised when unsatisfied.** Provide the non-contingent offer letter and reserve evidence covering the period to {start_date}.

**See also:** POL-AST-003.

### EMP-CNT-005 — Tenure is computed deterministically

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Employment tenure is the whole number of months between the verified start date and the application date, computed by the committed calculation code. Where the application's stated start date differs from the verified start date, tenure is computed from the verified date and the difference is recorded under EMP-VER-003.

| Parameter | Value |
| --- | --- |
| `formula` | whole months from verified start date to application date |
| `source_date` | verified start date |

**See also:** POL-EMP-001.

## 5. Documentation requirements

- A 24-month employment history with dates for every position.
- Written explanations for gaps of 30 days or more.
- The offer letter and reserve evidence where EMP-CNT-004 applies.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-EMP-001
- POL-INC-004
- POL-AST-003

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
