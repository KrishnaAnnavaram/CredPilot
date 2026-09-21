---
policy_id: POL-INC-006
title: Rental Income
version: 1.0
family: income-rental
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
  - INC-RNT-001
  - INC-RNT-002
  - INC-RNT-003
  - INC-RNT-004
synthetic: true
---

# Rental Income

**POL-INC-006 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how rent from an investment property or from additional units of the subject property is qualified. Rental income is the only income type in this corpus that can be negative, and the negative case is the one most often handled incorrectly.

## 2. Scope

Applies to rent from property the borrower owns, whether the subject property or another. Rent from a property being sold before closing is excluded entirely.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### INC-RNT-001 — Vacancy factor

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Gross rent is reduced by a 25 percent vacancy and maintenance factor before any other adjustment. The factor applies whether or not the property is currently tenanted, because it represents expected vacancy and upkeep across the holding period rather than current occupancy.

| Parameter | Value |
| --- | --- |
| `vacancy_factor` | 25% |
| `applies_when_tenanted` | yes |

### INC-RNT-002 — Net rental income and negative rent

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Net rental income is gross rent after the vacancy factor, less the property's full housing expense including its mortgage payment, taxes, insurance and association dues. A positive result is added to qualifying income. A negative result is added to monthly obligations as a liability - it is never recorded as zero income. Discarding a negative result understates the borrower's obligations and is a calculation defect.

| Parameter | Value |
| --- | --- |
| `formula` | gross rent * (1 - vacancy factor) - property PITIA |
| `negative_treatment` | add the absolute value to monthly obligations |

**See also:** POL-LIA-001, POL-DTI-001.

### INC-RNT-003 — Evidence hierarchy

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Where the property appears on the borrower's most recent tax return, the return governs the rental calculation. Where it does not - a recently acquired property, or one recently placed in service - a current executed lease plus the valuation's rent schedule may be used. A lease alone, with no supporting valuation evidence, is not sufficient for a property that has never appeared on a return.

| Parameter | Value |
| --- | --- |
| `primary_evidence` | most recent tax return schedule |
| `alternative_evidence` | executed lease plus appraisal rent schedule |
| `lease_alone_sufficient` | no |

**Acceptable evidence.** Tax return rental schedule; Executed lease agreement; Appraisal comparable rent schedule.

**Condition raised when unsatisfied.** Provide the tax return schedule or an executed lease with the valuation's rent schedule for property {property_id}.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Income model' - rental evidence is tax returns, lease, appraisal or rental analysis depending on the case; unsupported leases and related-party arrangements are the principal risks.

### INC-RNT-004 — Related-party leases

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A lease with a party related to the borrower requires evidence that the rent is at market - normally the valuation's comparable rent schedule - and routes the file for review. Rent materially above market on a related-party lease is treated as unsupported and reduced to the market figure.

| Parameter | Value |
| --- | --- |
| `treatment_above_market` | reduce to the market rent figure |

**See also:** POL-FRD-001.

## 5. Documentation requirements

- Tax return rental schedules for every owned rental property.
- Executed leases where relied upon.
- Valuation rent schedule for the subject property where additional units exist.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-LIA-001
- POL-DTI-001
- POL-VAL-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
