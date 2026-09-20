---
policy_id: POL-PRP-002
title: Occupancy Classification and Verification
version: 1.0
family: occupancy
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
priority: 56
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - PRP-OCC-001
  - PRP-OCC-002
  - PRP-OCC-003
synthetic: true
---

# Occupancy Classification and Verification

**POL-PRP-002 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how declared occupancy is classified and what happens when the file's evidence contradicts the declaration. Occupancy drives leverage, reserves and pricing, which is precisely why it is misrepresented.

## 2. Scope

Applies to every application. Occupancy is a declaration by the borrower that the file's evidence either corroborates or contradicts.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### PRP-OCC-001 — Occupancy classes

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Three classes are recognised. A primary residence is occupied by the borrower as their principal home and must be occupied within 60 days of closing. A second home is occupied by the borrower for part of the year, is suitable for year-round use, is not subject to a rental or management agreement, and must be a reasonable distance from the primary residence. An investment property is held to generate rent. The declared class determines which leverage and reserve rules apply.

| Parameter | Value |
| --- | --- |
| `primary_occupancy_deadline_days` | 60 |
| `second_home_rental_agreement_permitted` | no |
| `second_home_min_distance_miles` | 50 |

### PRP-OCC-002 — Contradicting evidence routes the file for review

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where evidence in the file contradicts the declared occupancy, the file is routed for review and the contradiction is recorded with both sources. Indicators include a subject property implausibly distant from the borrower's employment for a declared primary residence, an existing lease on the subject property, a mailing address that differs from the subject after the declared occupancy date, and a valuation reporting the property as tenant-occupied. No single indicator is conclusive, and none may be resolved by re-reading the declaration.

| Parameter | Value |
| --- | --- |
| `distance_indicator_miles` | 100 |
| `resolution` | underwriter review, not re-reading the declaration |

**See also:** POL-FRD-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Risk taxonomy' - occupancy fraud is detected by cross-source and address analysis and represented as a contradiction.

### PRP-OCC-003 — Occupancy misrepresentation is a fraud finding, not a pricing question

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where the review concludes the declared occupancy is not the intended occupancy, the finding is recorded as a material misrepresentation and escalated under POL-FRD-001. It is not resolved by silently re-classifying the loan into the correct occupancy and re-pricing it, because that would leave a known misrepresentation undocumented in the file.

**See also:** POL-FRD-001, POL-UWR-001.

## 5. Documentation requirements

- Signed occupancy declaration.
- Evidence corroborating occupancy where PRP-OCC-002 indicators are present.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-PRP-001
- POL-FRD-001
- POL-CONV-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
