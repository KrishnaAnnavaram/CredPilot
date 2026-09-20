---
policy_id: POL-VA-001
title: "VA-Style Programme Overlay"
version: 1.0
family: va-overlay
effective_date: 2026-01-01
expiration_date: null
product_scope:
  - va
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
  - VA-OVL-001
  - VA-OVL-002
  - VA-OVL-003
  - VA-OVL-004
synthetic: true
---

# VA-Style Programme Overlay

**POL-VA-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

A synthetic overlay for a guaranty-style programme for eligible service members and veterans, modelled on the structure of VA lending: an entitlement certificate, a residual-income test that sits alongside debt-to-income, occupancy requirements, and no monthly mortgage insurance.

## 2. Scope

Applies to applications under the synthetic guaranty programme. VA's own standards, and the fact that lenders may impose additional standards of their own, are described in VA's published guidance; this overlay is the lender-side standard only.

- **Products:** va
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### VA-OVL-001 — Programme eligibility rests on an entitlement certificate

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Programme eligibility is established by a certificate of eligibility evidencing entitlement, not by the lender's own assessment. A borrower must meet both the programme's standards and the lender's own credit and income standards; published VA guidance is explicit that lenders may impose additional standards. Satisfying the guaranty programme is therefore not equivalent to qualifying for the loan.

**Acceptable evidence.** Certificate of eligibility evidencing available entitlement.

**Condition raised when unsatisfied.** Provide a current certificate of eligibility.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Product taxonomy' - VA makes the investor versus lender distinction explicit.

### VA-OVL-002 — No down payment and no monthly mortgage insurance

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `ADVISORY` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Purchase transactions under this programme can commonly be made with no down payment and carry no monthly mortgage insurance. That structural feature is not a statement that every applicant qualifies: the residual-income and credit tests below still apply, and a funding fee may be financed into the loan amount.

| Parameter | Value |
| --- | --- |
| `min_down_payment_pct` | 0.00 |
| `max_ltv` | 1.00 |
| `monthly_mortgage_insurance` | no |
| `funding_fee_pct_financed` | 2.3% |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Product taxonomy' - VA purchase loans can often be made without a down payment and do not require PMI or MIP.

### VA-OVL-003 — Residual income test

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Monthly income remaining after the proposed housing expense and all recurring obligations must meet the residual-income floor for the household size. Back-end debt-to-income above 41 percent is permitted only where residual income exceeds that floor by at least 20 percent; below that cushion the guideline governs. This test therefore replaces the general affordability ceiling for this programme rather than sitting alongside it, and a file that every other programme would measure only as a ratio can fail here on the absolute amount left over. The figures are synthetic; the concept of a residual income standard is genuine to this kind of programme.

| Parameter | Value |
| --- | --- |
| `residual_income_floor_household_1` | 500 |
| `residual_income_floor_household_2` | 840 |
| `residual_income_floor_household_3` | 1,000 |
| `residual_income_floor_household_4_plus` | 1,180 |
| `max_back_end_dti_without_residual_cushion` | 41% |
| `residual_cushion_multiple_above_guideline` | 1.20 |

**See also:** POL-DTI-001.

### VA-OVL-004 — Occupancy certification

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The borrower must certify intent to occupy the property as a primary residence within 60 days of closing. Investment occupancy is not eligible under this programme, and an occupancy declaration that conflicts with other evidence in the file is escalated under POL-PRP-002 rather than resolved by the declaration alone.

| Parameter | Value |
| --- | --- |
| `occupancy_required` | primary_residence |
| `occupancy_deadline_days` | 60 |

**See also:** POL-PRP-002.

## 5. Documentation requirements

- Certificate of eligibility.
- Household-size evidence where the residual-income floor depends on it.
- Signed occupancy certification.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-DTI-001
- POL-PRP-002

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial overlay version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
