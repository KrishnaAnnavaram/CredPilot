---
policy_id: POL-VAL-001
title: Appraisal and Valuation
version: 2.0
family: valuation
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
priority: 57
supersedes: "POL-VAL-001 v1.0"
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - VAL-APR-002
  - VAL-APR-004
  - VAL-APR-001
  - VAL-APR-003
  - VAL-APR-005
synthetic: true
---

# Appraisal and Valuation

**POL-VAL-001 · version 2.0 · effective 2026-07-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how the property's value is established, what form of valuation is acceptable, and how a valuation that disagrees with the transaction is handled.

## 2. Scope

Applies to every application. Not every transaction requires a full appraisal report, which is why the valuation method is recorded as a field rather than assumed.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Valuation method.** How the accepted value was established: a full interior and exterior appraisal, an exterior-only appraisal, a property-data report, or an automated value acceptance offer. The method is recorded on every application, because assuming every loan has an appraisal report is wrong.

**Value acceptance.** An offer from the automated underwriting system to accept a stated value without a traditional appraisal. Eligibility and exclusions apply and the offer controls: the lender does not decide unilaterally to waive an appraisal.

## 4. Rules

### VAL-APR-002 — Appraised value below contract price

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Where the appraised value is below the contract price on a purchase, the lower figure becomes the value used for leverage and the loan-to-value ratio is recomputed. The shortfall between price and value falls to the borrower as additional funds to close unless the price is renegotiated. The appraised value is never adjusted upward to preserve the loan amount, and a second appraisal is not ordered merely because the first was inconvenient.

| Parameter | Value |
| --- | --- |
| `value_used` | lower of contract price and appraised value |
| `shortfall_treatment` | additional borrower funds or renegotiated price |
| `upward_adjustment_permitted` | no |

**See also:** POL-AST-002, POL-CONV-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Missing/conflicting data workflow' - an appraisal lower than the purchase price means recalculating LTV and cash requirement, not changing the value.

### VAL-APR-004 — Appraiser independence

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

The valuation must be obtained through a process that keeps the appraiser independent of the transaction's production side. No party compensated on the transaction closing may select, influence or pressure the appraiser, and a valuation may not be ordered a second time solely because the first did not support the desired value. Applicants are entitled to a copy of the valuation the lender obtained.

**See also:** POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Regulatory and agency landscape' - Regulation Z valuation requirements and Regulation B appraisal-copy obligations.

### VAL-APR-001 — Required valuation method, with value acceptance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A full interior and exterior appraisal is required unless the automated underwriting system returns a value acceptance offer for the transaction. Value acceptance is available only on a one-unit primary residence or second home, at loan-to-value of 80 percent or less, where the transaction is not a cash-out refinance and the property is not in a disaster-affected area. Version 1.0 of this policy made a full appraisal mandatory on every purchase, so an eligible transaction underwritten before 2026-07-01 still requires the report.

| Parameter | Value |
| --- | --- |
| `value_acceptance_available` | yes |
| `value_acceptance_max_ltv` | 80% |
| `value_acceptance_max_units` | 1 |
| `value_acceptance_excluded_purposes` | cash_out_refinance |
| `value_acceptance_excluded_occupancy` | investment |

**Acceptable evidence.** Appraisal report, or the automated value-acceptance offer record.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Property valuation' - for eligible transactions the agency automated system can offer value acceptance and the offer controls; the eligibility conditions here are synthetic.

### VAL-APR-003 — Valuation age

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A valuation is acceptable for 120 days from its effective date. Beyond that, an appraisal update from the original appraiser is required; beyond 240 days a new valuation is required. A value-acceptance offer expires with the automated underwriting casefile it was issued against.

| Parameter | Value |
| --- | --- |
| `max_age_days` | 120 |
| `update_window_days` | 240 |
| `value_acceptance_expiry` | with the casefile that issued it |

**Condition raised when unsatisfied.** Provide an appraisal update; the valuation is {age_days} days old.

**See also:** POL-DOC-001.

### VAL-APR-005 — Valuation data standard and metadata

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `ADVISORY` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Appraisal data is exchanged using the industry appraisal dataset standard. The standard is versioned and the version in use changes over time - the successor dataset entered broad production in January 2026 and becomes mandatory for applicable new agency submissions on 2 November 2026. The dataset version is therefore recorded on every valuation record, so a file underwritten under one version remains interpretable after the mandate date.

| Parameter | Value |
| --- | --- |
| `dataset_version_recorded` | yes |
| `successor_mandate_date` | 2026-11-02 |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Property valuation' - UAD 3.6 entered broad production in January 2026 and is scheduled to become mandatory on 2 November 2026, so policy metadata must support both eras.

## 5. Documentation requirements

- The valuation report or the value-acceptance record, with its method and dataset version.
- Evidence the applicant received a copy of the valuation.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-PRP-001
- POL-CONV-001
- POL-AST-002

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| (prior) | before 2026-07-01 | Superseded by this version. Prior version identifier: POL-VAL-001 v1.0. |
| 2.0 | 2026-07-01 | Introduced automated value acceptance with eligibility conditions, and added the valuation dataset-version rule VAL-APR-005. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
