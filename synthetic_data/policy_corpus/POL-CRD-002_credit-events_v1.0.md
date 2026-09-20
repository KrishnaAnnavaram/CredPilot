---
policy_id: POL-CRD-002
title: Significant Derogatory Credit Events and Seasoning
version: 1.0
family: credit-events
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
priority: 42
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - CRD-EVT-001
  - CRD-EVT-002
  - CRD-EVT-003
  - CRD-EVT-004
synthetic: true
---

# Significant Derogatory Credit Events and Seasoning

**POL-CRD-002 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Governs how a bankruptcy, foreclosure, short sale, deed in lieu, charge-off or collection affects eligibility. The operative concept is seasoning: how much time has passed since the event concluded, measured from the correct anchor date for that event type.

## 2. Scope

Applies to every programme. The anchor date differs by event type, and using the wrong anchor is the most common error this document guards against.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Anchor date.** The date from which seasoning is measured. For a bankruptcy it is the discharge or dismissal date, not the filing date. For a foreclosure it is the completion or sale date, not the date of first delinquency. For a short sale or deed in lieu it is the date title transferred.

**Extenuating circumstances.** A documented non-recurring event beyond the borrower's control that directly caused the derogatory event, supported by independent evidence rather than by the borrower's account alone.

## 4. Rules

### CRD-EVT-001 — Seasoning periods by event type

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A significant derogatory event bars eligibility until the seasoning period below has elapsed, measured from the event's anchor date to the application date. Seasoning that has not yet elapsed is a hard failure for the programme, not a referral - but the borrower may be eligible for a different programme with a shorter period, and the file should say so rather than simply declining.

| Parameter | Value |
| --- | --- |
| `chapter_7_bankruptcy_months` | 48 |
| `chapter_13_bankruptcy_discharged_months` | 24 |
| `foreclosure_months` | 84 |
| `deed_in_lieu_months` | 48 |
| `short_sale_months` | 48 |
| `mortgage_charge_off_months` | 48 |
| `anchor_bankruptcy` | discharge or dismissal date |
| `anchor_foreclosure` | completion or sale date |
| `anchor_short_sale` | title transfer date |

**Acceptable evidence.** Court discharge or dismissal order; Trustee deed, settlement statement or equivalent completion evidence.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - derogatory seasoning depends on the event type and the correct anchor date; the periods here are synthetic.

### CRD-EVT-002 — Reduced seasoning with documented extenuating circumstances

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where extenuating circumstances are documented by independent evidence, the seasoning period for a foreclosure, deed in lieu or short sale is reduced to 36 months, and the file is routed to an underwriter to assess whether the evidence supports the claim. The reduction is never applied on the strength of a letter of explanation alone.

| Parameter | Value |
| --- | --- |
| `reduced_seasoning_months` | 36 |
| `requires_independent_evidence` | yes |
| `applies_to` | foreclosure, deed in lieu, short sale |

**Acceptable evidence.** Independent third-party evidence of the circumstance and its dates; Evidence that the circumstance has been resolved.

**See also:** POL-UWR-001.

### CRD-EVT-003 — Collections and charge-offs on non-mortgage debt

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Non-mortgage collection and charge-off accounts totalling more than 5,000 across the application must be paid off or brought into a documented payment plan before closing, and any plan payment is included in the debt-to-income calculation. Individual accounts below 500 are excluded from the total. Medical collections are excluded entirely from this test.

| Parameter | Value |
| --- | --- |
| `aggregate_threshold` | 5,000 |
| `individual_account_floor` | 500 |
| `medical_collections_excluded` | yes |

**Condition raised when unsatisfied.** Pay off or document a payment plan for non-mortgage collection and charge-off accounts totalling {collection_total}.

**See also:** POL-LIA-001.

### CRD-EVT-004 — Disputed tradelines

- **Source category:** `COMMON_INDUSTRY_PRACTICE` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A tradeline carrying a dispute indicator is not silently excluded from or included in the analysis. The underwriter records whether the disputed balance and payment are counted and why, because the same tradeline treated inconsistently between the debt-to-income calculation and the credit assessment produces two different pictures of the same file.

**Condition raised when unsatisfied.** Document the treatment of the disputed tradeline {tradeline_id} in both the credit assessment and the debt calculation.

**See also:** POL-LIA-001.

## 5. Documentation requirements

- Court or trustee documentation establishing the anchor date for each event.
- Independent evidence where extenuating circumstances are claimed.
- Payoff or payment-plan evidence for collections under CRD-EVT-003.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-CRD-001
- POL-CRD-003
- POL-LIA-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
