---
policy_id: POL-USDA-001
title: "USDA-Style Rural Programme Overlay"
version: 1.0
family: usda-overlay
effective_date: 2026-01-01
expiration_date: null
product_scope:
  - usda
occupancy_scope:
  - primary_residence
purpose_scope:
  - purchase
  - rate_term_refinance
jurisdiction: US
source_category: SYNTHETIC_INTERNAL_POLICY
priority: 28
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - USD-OVL-001
  - USD-OVL-002
  - USD-OVL-003
  - USD-OVL-004
synthetic: true
---

# USDA-Style Rural Programme Overlay

**POL-USDA-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

A synthetic overlay for a guaranteed rural-housing programme modelled on the structure of a Section 502 guaranteed loan: property must be in an eligible area, household income must be within a programme limit, occupancy must be a primary residence, and the programme permits full financing.

## 2. Scope

Applies to applications under the synthetic rural programme. The authoritative source for real USDA guaranteed lending is USDA Rural Development's own programme guidance and handbook.

- **Products:** usda
- **Occupancy:** primary_residence
- **Loan purpose:** purchase, rate_term_refinance
- **Jurisdiction:** US

## 4. Rules

### USD-OVL-001 — Property and occupancy eligibility

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The property must be located in an area the programme designates as eligible and must be occupied by the borrower as a primary residence. Area eligibility is a programme determination keyed to the property address; it is not a judgement the underwriter or an automated component may make from the address alone.

**Acceptable evidence.** Programme area-eligibility determination for the property address.

**Condition raised when unsatisfied.** Obtain the programme area-eligibility determination for the subject property.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Product taxonomy' - USDA Section 502 Guaranteed serves eligible rural primary residences.

### USD-OVL-002 — Household income limit

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Adjusted household income must not exceed the programme limit for the area and household size. Household income here counts every adult member of the household, which is a broader measure than the qualifying income used for the debt-to-income calculation. The two measures serve different purposes and must both be recorded.

| Parameter | Value |
| --- | --- |
| `income_limit_household_1_to_4` | 121,500 |
| `income_limit_household_5_plus` | 160,400 |
| `income_basis` | adjusted household income, all adult members |

**See also:** POL-INC-001.

### USD-OVL-003 — Full financing and guarantee fees

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

The programme permits financing of the full accepted value, with an up-front guarantee fee financed into the loan and an annual fee collected monthly as part of the housing expense. The annual fee is included in the qualifying housing expense in the same way mortgage insurance is under CONV-PUR-003.

| Parameter | Value |
| --- | --- |
| `max_ltv` | 1.00 |
| `upfront_guarantee_fee_pct` | 1% |
| `annual_fee_pct_of_loan` | 0.35% |

**See also:** POL-DTI-001.

### USD-OVL-004 — Affordability ceiling

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Housing expense ratio must not exceed 34 percent and back-end debt-to-income must not exceed 44 percent. This programme is one of the few in this corpus where the housing ratio is a hard test rather than an advisory measure.

| Parameter | Value |
| --- | --- |
| `max_front_end_dti` | 34% |
| `max_back_end_dti` | 44% |

**See also:** POL-DTI-001.

## 5. Documentation requirements

- Programme area-eligibility determination.
- Household income documentation for every adult household member.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-DTI-001
- POL-INC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial overlay version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
