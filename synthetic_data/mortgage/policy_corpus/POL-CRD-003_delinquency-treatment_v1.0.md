---
policy_id: POL-CRD-003
title: Delinquency and Payment History Treatment
version: 1.0
family: delinquency-treatment
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
priority: 43
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - CRD-DLQ-001
  - CRD-DLQ-002
  - CRD-DLQ-003
  - CRD-DLQ-004
synthetic: true
---

# Delinquency and Payment History Treatment

**POL-CRD-003 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Governs how late payments short of a significant derogatory event are weighed. The distinction that matters is between housing-related delinquency and other delinquency, and between an isolated late and a pattern.

## 2. Scope

Applies to every programme. Events that qualify as significant derogatory events are handled by POL-CRD-002 instead.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### CRD-DLQ-001 — Housing payment history is weighed separately

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Any payment 60 or more days past due on a mortgage or rental obligation in the most recent 12 months is a hard failure. A single 30-day late on a housing obligation in that window routes the file for underwriter review. Housing history carries more weight than other history because it is the closest available analogue to the obligation being underwritten.

| Parameter | Value |
| --- | --- |
| `housing_lookback_months` | 12 |
| `housing_30d_refer_at` | 1 |
| `housing_60d_fail_at` | 1 |

**Acceptable evidence.** Credit report housing tradeline; Cancelled cheques or a verification of rent where no tradeline exists.

### CRD-DLQ-002 — Non-housing delinquency pattern

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

Three or more accounts showing a payment 30 or more days past due in the most recent 24 months, or any account 90 or more days past due in that window, routes the file for underwriter review with a written explanation. An isolated 30-day late on a single non-housing account is recorded and passed.

| Parameter | Value |
| --- | --- |
| `lookback_months` | 24 |
| `accounts_30d_refer_at` | 3 |
| `any_90d_refer` | yes |

**Condition raised when unsatisfied.** Provide a written explanation of the delinquencies reported in the last {lookback_months} months.

### CRD-DLQ-003 — Credit utilisation is context, not a threshold test

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Revolving utilisation is computed as total revolving balances divided by total revolving limits, excluding accounts with no stated limit. It is recorded as a risk indicator and may support a referral alongside other findings, but high utilisation alone is not a policy breach and must not be reported as one. Utilisation above 80 percent is noted in the risk summary.

| Parameter | Value |
| --- | --- |
| `excludes` | accounts with no stated limit and closed accounts |
| `risk_note_threshold` | 80% |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Underwriting calculations' - credit utilisation is a common-practice risk indicator, with the no-limit exclusion.

### CRD-DLQ-004 — Recent payment behaviour outweighs distant behaviour

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Where a file shows deteriorating recent behaviour against a clean older history, the recent behaviour governs the referral decision. Where it shows improving behaviour against an adverse older history, the improvement is recorded as a compensating factor available to POL-DTI-001. Neither direction is inferred from the score alone.

**See also:** POL-DTI-001.

## 5. Documentation requirements

- Credit report payment history for every open account.
- Verification of rent where housing history is not on the credit report.
- Written explanations required by CRD-DLQ-002.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-CRD-001
- POL-CRD-002

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
