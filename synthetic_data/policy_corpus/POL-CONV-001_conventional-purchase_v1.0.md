---
policy_id: POL-CONV-001
title: Conventional Conforming Purchase Eligibility
version: 1.0
family: conventional-purchase
effective_date: 2026-01-01
expiration_date: null
product_scope:
  - conventional_conforming
occupancy_scope:
  - primary_residence
  - second_home
  - investment
purpose_scope:
  - purchase
jurisdiction: US
source_category: SYNTHETIC_INTERNAL_POLICY
priority: 30
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - CONV-PUR-001
  - CONV-PUR-002
  - CONV-PUR-003
  - CONV-PUR-004
  - CONV-PUR-005
synthetic: true
---

# Conventional Conforming Purchase Eligibility

**POL-CONV-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines eligibility for the lender's core product: a conventional conforming, fixed-rate, one-to-four-unit purchase mortgage. This is the programme most applications are underwritten against, and the one whose leverage and occupancy rules the other product documents vary from.

## 2. Scope

Purchase transactions only. Refinances are governed by POL-CONV-002 and POL-CONV-003. Loan amounts above the applicable conforming limit are not eligible under this document and are routed to POL-JUMBO-001.

- **Products:** conventional_conforming
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase
- **Jurisdiction:** US

## 3. Definitions

**Conforming.** A loan whose amount is at or below the applicable one-unit conforming limit for the property's area, and which meets the other requirements of this document. 'Conforming' describes the execution, not the borrower.

**Value used for leverage.** For a purchase, the lower of the contract sales price and the appraised or otherwise accepted value. An appraisal that comes in below the contract price therefore raises the loan-to-value ratio; it does not change the price the borrower agreed to pay.

## 4. Rules

### CONV-PUR-001 — Eligible transaction characteristics

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

An eligible transaction under this document is a first-lien purchase of a one-to-four-unit residential property, on a fixed-rate fully-amortising note with a term of 120 to 360 months, where the borrower occupies the property as a primary residence, second home or declared investment property. Manufactured housing, properties above four units, and mixed commercial use are outside this document and require the collateral review in POL-PRP-001.

| Parameter | Value |
| --- | --- |
| `unit_count_min` | 1 |
| `unit_count_max` | 4 |
| `term_months_min` | 120 |
| `term_months_max` | 360 |
| `lien_position` | 1 |
| `amortisation` | fully amortising, fixed rate |

**See also:** POL-PRP-001, POL-PRP-002.

### CONV-PUR-002 — Maximum leverage by occupancy

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Loan-to-value is computed against the value used for leverage and must not exceed the limit for the declared occupancy. Combined loan-to-value, which adds every subordinate lien, is capped at the same figure as loan-to-value for second homes and investment property, and five percentage points higher for a primary residence to accommodate eligible community-second financing. These figures are this lender's own synthetic leverage matrix; they are not an agency matrix.

| Parameter | Value |
| --- | --- |
| `max_ltv_primary_residence` | 97% |
| `max_ltv_second_home` | 90% |
| `max_ltv_investment` | 85% |
| `max_cltv_primary_residence` | 1.02 |
| `max_cltv_second_home` | 90% |
| `max_cltv_investment` | 85% |

**Acceptable evidence.** Appraisal or accepted valuation; Executed purchase agreement.

**See also:** POL-VAL-001, POL-AST-002.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - purchase LTV uses the lower of sales price or appraised value; the thresholds themselves are synthetic.

### CONV-PUR-003 — Mortgage insurance is required above 80 percent leverage

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A loan with a loan-to-value ratio above 80 percent requires mortgage insurance, and the insurance premium must be included in the qualifying housing expense. Coverage is expressed as a monthly factor applied to the loan amount; the factor rises as leverage rises. Omitting the premium from the housing expense understates the debt-to-income ratio and is a calculation defect, not a rounding difference.

| Parameter | Value |
| --- | --- |
| `mi_required_above_ltv` | 80% |
| `annual_factor_ltv_80_to_85` | 0.32% |
| `annual_factor_ltv_85_to_90` | 0.52% |
| `annual_factor_ltv_90_to_95` | 0.78% |
| `annual_factor_ltv_above_95` | 0.94% |

**Condition raised when unsatisfied.** Provide evidence of mortgage insurance meeting the coverage required at {ltv_pct} loan-to-value.

**See also:** POL-DTI-001.

### CONV-PUR-004 — Minimum borrower contribution

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

On a primary residence the entire down payment may come from eligible gift funds. On a second home or investment property the borrower must contribute at least five percent of the purchase price from the borrower's own verified funds before gift funds are applied. Gift eligibility itself, including who may be a donor, is governed by POL-AST-004.

| Parameter | Value |
| --- | --- |
| `min_own_funds_pct_primary_residence` | 0.00 |
| `min_own_funds_pct_second_home` | 5% |
| `min_own_funds_pct_investment` | 5% |

**See also:** POL-AST-004.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Asset model' - agency gift eligibility differs by occupancy and purpose; the percentages here are synthetic.

### CONV-PUR-005 — Interested-party contributions are limited

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Seller and other interested-party credits toward the borrower's closing costs are limited by leverage. Credits above the limit are not disallowed outright: the excess is applied as a reduction to the sales price, which changes the value used for leverage and therefore requires the leverage calculation to be re-run.

| Parameter | Value |
| --- | --- |
| `max_ipc_pct_ltv_above_90` | 3% |
| `max_ipc_pct_ltv_75_to_90` | 6% |
| `max_ipc_pct_ltv_at_or_below_75` | 9% |
| `excess_treatment` | reduce sales price and recompute LTV |

**See also:** POL-AST-002.

## 5. Documentation requirements

- Executed purchase agreement including price, parties, concessions and dates.
- Appraisal or an accepted alternative valuation under POL-VAL-001.
- Evidence of mortgage insurance where CONV-PUR-003 requires it.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-GEN-001 for the programme limit and the decision vocabulary
- POL-DTI-001 for affordability
- POL-AST-002 for funds to close

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial product version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
