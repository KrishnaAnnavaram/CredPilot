---
policy_id: POL-FHA-001
title: "FHA-Style Programme Overlay"
version: 1.0
family: fha-overlay
effective_date: 2026-01-01
expiration_date: null
product_scope:
  - fha
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
priority: 28
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - FHA-OVL-001
  - FHA-OVL-002
  - FHA-OVL-003
  - FHA-OVL-004
synthetic: true
---

# FHA-Style Programme Overlay

**POL-FHA-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

A synthetic overlay for government-insured lending modelled on the structure of an FHA-style programme. It reproduces the shape of the programme - an up-front and an annual insurance premium, lower leverage tolerance for weaker credit, and a separate property standard - without restating any provision of HUD Handbook 4000.1, which is the authoritative source for real FHA lending.

## 2. Scope

Applies to applications submitted under the synthetic government programme. Where a rule here conflicts with the conventional documents, this overlay governs for these applications only.

- **Products:** fha
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### FHA-OVL-001 — Authority and what this document is not

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `ADVISORY` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

The authoritative source for real FHA single-family origination and underwriting is HUD's consolidated Single Family Housing Policy Handbook 4000.1. This document does not restate it, does not reproduce the TOTAL scorecard, and must never be cited as though it were HUD policy. Every numeric threshold below is this lender's synthetic overlay.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, source ledger entry 23 - HUD Handbook 4000.1, August 2026 update, is the authoritative FHA source.

### FHA-OVL-002 — Leverage by credit band

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Maximum loan-to-value is set by the representative credit score band. A score of 580 or above supports up to 96.5 percent; a score from 500 to 579 supports up to 90 percent; below 500 the programme is not available. The score bands are structural to this kind of programme; the exact figures here are synthetic.

| Parameter | Value |
| --- | --- |
| `max_ltv_score_580_plus` | 96.5% |
| `max_ltv_score_500_to_579` | 90% |
| `min_representative_score` | 500 |

**See also:** POL-CRD-001.

### FHA-OVL-003 — Insurance premiums enter the housing expense

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

An up-front insurance premium is financed into the loan amount and an annual premium is collected monthly. The monthly premium is part of the qualifying housing expense, and the financed up-front premium increases the loan amount used in the payment calculation but is excluded from the loan-to-value test, which is measured against the base loan amount.

| Parameter | Value |
| --- | --- |
| `upfront_premium_pct_of_base_loan` | 1.75% |
| `annual_premium_pct_of_loan` | 0.55% |
| `upfront_premium_financed` | yes |
| `ltv_measured_against` | base loan amount before financed premium |

**See also:** POL-DTI-001.

### FHA-OVL-004 — Affordability tolerance with compensating factors

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Back-end debt-to-income must not exceed 43 percent, extended to 50 percent where at least two documented compensating factors are present and recorded by name. The compensating factors recognised are: verified reserves of at least three months beyond the programme requirement; a residual income at or above 1,500 per month; no payment 30 or more days past due in 24 months; and a proposed housing payment no greater than the borrower's current housing payment.

| Parameter | Value |
| --- | --- |
| `max_back_end_dti` | 43% |
| `max_back_end_dti_with_factors` | 50% |
| `min_compensating_factors` | 2 |

**See also:** POL-DTI-001.

## 5. Documentation requirements

- Evidence of programme eligibility for the borrower and the property.
- Documentation of each compensating factor relied upon by FHA-OVL-004.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-DTI-001
- POL-CRD-001
- POL-PRP-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial overlay version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
