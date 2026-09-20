---
policy_id: POL-AST-003
title: Reserve Requirements
version: 1.0
family: reserves
effective_date: 2026-01-01
expiration_date: 2026-07-01
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
priority: 54
supersedes: null
superseded_by: "POL-AST-003 v2.0"
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - AST-RSV-001
  - AST-RSV-004
  - AST-RSV-002
  - AST-RSV-003
synthetic: true
---

# Reserve Requirements

**POL-AST-003 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how many months of housing expense must remain available after closing. Reserves are the file's margin for the first payment shock, and the requirement rises with the risk of the rest of the file.

## 2. Scope

Applies to every programme. Product documents that state a higher reserve requirement - POL-CONV-003 and POL-JUMBO-001 - govern for their products.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### AST-RSV-001 — Reserve definition and measurement

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Reserves are the reserve-eligible assets remaining after the funds-to-close draw in AST-FTC-004, expressed as a number of months of the qualifying housing expense. The denominator is the full qualifying housing expense including mortgage insurance and association dues, not principal and interest alone. Using the smaller denominator overstates months of reserves by a wide margin on a high-leverage file.

| Parameter | Value |
| --- | --- |
| `formula` | reserve-eligible assets remaining after closing / qualifying PITIA |
| `denominator` | full qualifying housing expense |

**See also:** POL-AST-002, POL-DTI-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - reserves are conventionally expressed as months of qualifying PITIA remaining after required funds-to-close are deducted.

### AST-RSV-004 — Reserves in excess of the requirement are a compensating factor

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Reserves materially above the requirement are recorded as an available compensating factor for the affordability extension in POL-DTI-001 and for the manual-underwriting assessment. They do not cure a hard failure of leverage, credit seasoning or funds to close.

**See also:** POL-DTI-001, POL-UWR-001.

### AST-RSV-002 — Minimum reserve requirement

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

No reserves are required on a primary-residence conventional conforming transaction. Two months are required on a second home and six months on an investment property. Leverage and affordability do not change the requirement under this version.

| Parameter | Value |
| --- | --- |
| `min_months_primary_residence` | 0 |
| `min_months_second_home` | 2 |
| `min_months_investment` | 6 |
| `risk_based_adjustment` | none |

### AST-RSV-003 — Additional financed properties

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Where the borrower has other financed residential properties, an additional two months of the subject property's qualifying housing expense is required for each, up to a maximum of eight additional months. Multiple financed properties raise the probability that one of them generates a call on the borrower's liquidity.

| Parameter | Value |
| --- | --- |
| `additional_months_per_financed_property` | 2 |
| `additional_months_cap` | 8 |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - multiple financed properties can alter the reserve requirement.

## 5. Documentation requirements

- Asset evidence supporting the post-closing reserve figure.
- The reserve calculation showing the post-draw remaining balance.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-AST-001
- POL-AST-002
- POL-DTI-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Original standard: occupancy-based only, with no risk-based adjustment. Superseded on 2026-07-01. |
| (later) | from 2026-07-01 | This version is superseded by POL-AST-003 v2.0. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
