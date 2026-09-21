---
policy_id: POL-INC-003
title: "Hourly and Variable-Hour Income"
version: 1.0
family: income-hourly
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
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - INC-HRL-001
  - INC-HRL-002
  - INC-HRL-003
  - INC-HRL-004
synthetic: true
---

# Hourly and Variable-Hour Income

**POL-INC-003 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how hourly earnings are qualified. The critical distinction is between hours that are guaranteed and hours that merely happened: only the former can be treated as fixed income.

## 2. Scope

Applies to borrowers paid an hourly rate. Overtime and other premium earnings on top of base hours are governed by POL-INC-004.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Guaranteed hours.** A weekly hour count the employer commits to in writing. An employment verification that reports hours actually worked is not evidence of guaranteed hours.

## 4. Rules

### INC-HRL-001 — Guaranteed hours are qualified as fixed income

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Where the employer confirms a guaranteed weekly hour count in writing, monthly income is the hourly rate multiplied by the guaranteed hours, multiplied by 52 and divided by 12. Hours above the guaranteed count are variable earnings and follow INC-HRL-002, not this rule.

| Parameter | Value |
| --- | --- |
| `formula` | rate * guaranteed weekly hours * 52 / 12 |
| `guarantee_evidence_required` | yes |

### INC-HRL-002 — Variable hours are averaged over history

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Where hours are not guaranteed, qualifying income is the average of verified earnings over the most recent 24 months, or over 12 months where a 24-month history is unavailable and the shorter history is stable. The average is taken over the full period including any low-earning months; excluding weak periods from the average inflates the result and is not permitted.

| Parameter | Value |
| --- | --- |
| `preferred_history_months` | 24 |
| `minimum_history_months` | 12 |
| `averaging` | full period, no exclusions |

**Acceptable evidence.** W-2 forms covering the averaging period; Year-to-date paystub; Employment verification reporting hours.

### INC-HRL-003 — Declining hours reduce the qualifying amount

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where the current-period annualised rate is more than 10 percent below the historical average, the lower current figure is used rather than the average, and the file is routed for review. An average that is propped up by earnings the borrower is no longer achieving overstates capacity. A rising trend does not permit using an amount above the historical average.

| Parameter | Value |
| --- | --- |
| `decline_trigger` | 10% |
| `declining_treatment` | use the current annualised amount |
| `rising_treatment` | use the historical average, never the current peak |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Income model' - falling hours are the principal risk for variable hourly income.

### INC-HRL-004 — Seasonal employment

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

Seasonal employment requires a two-year history in the same seasonal role or industry and evidence that the borrower is expected to be rehired. Qualifying income is the full-year average including the off-season, not the in-season rate. Qualifying a seasonal borrower on peak-season earnings produces a payment they cannot make for part of every year.

| Parameter | Value |
| --- | --- |
| `required_history_months` | 24 |
| `averaging_basis` | full calendar year including off-season |

**Acceptable evidence.** Employer statement of expected rehire; Two years of W-2 forms.

## 5. Documentation requirements

- Written confirmation of guaranteed hours where INC-HRL-001 is relied upon.
- W-2 forms and paystubs covering the averaging period.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-INC-004
- POL-EMP-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
