---
policy_id: POL-CONV-003
title: "Cash-Out Refinance Eligibility"
version: 1.0
family: cash-out-refinance
effective_date: 2026-01-01
expiration_date: null
product_scope:
  - conventional_conforming
occupancy_scope:
  - primary_residence
  - second_home
  - investment
purpose_scope:
  - cash_out_refinance
jurisdiction: US
source_category: SYNTHETIC_INTERNAL_POLICY
priority: 30
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - CONV-COR-001
  - CONV-COR-002
  - CONV-COR-003
  - CONV-COR-004
  - CONV-COR-005
synthetic: true
---

# Cash-Out Refinance Eligibility

**POL-CONV-003 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines eligibility where the borrower extracts equity. Because the borrower's equity position falls at closing rather than rising, this product applies lower leverage limits, a higher credit floor and a reserve requirement that the rate and term product does not.

## 2. Scope

Applies to any refinance returning more cash to the borrower than CONV-RTR-001 permits, and to any refinance paying off a subordinate lien that was not itself used to acquire the property.

- **Products:** conventional_conforming
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Seasoning.** The elapsed time since the borrower acquired the property or since the most recent cash-out refinance of it, measured to the application date.

## 4. Rules

### CONV-COR-001 — Ownership seasoning

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The borrower must have held title to the property for at least six months before the application date, and at least 12 months must have elapsed since any prior cash-out refinance of the same property. Inherited property and property awarded by a court order are exempt from the six-month test on documentation of the transfer.

| Parameter | Value |
| --- | --- |
| `min_ownership_months` | 6 |
| `min_months_since_prior_cash_out` | 12 |

**Acceptable evidence.** Title evidence showing the acquisition date.

**Exception.** Inheritance or a legal award transfers the seasoning clock to the prior owner's acquisition date when the transfer is documented.

**See also:** POL-TTL-001.

### CONV-COR-002 — Maximum leverage on a cash-out refinance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Loan-to-value on a cash-out refinance must not exceed the occupancy limit below, measured against the current accepted value. These limits sit materially below the equivalent purchase limits because equity is leaving the transaction.

| Parameter | Value |
| --- | --- |
| `max_ltv_primary_residence` | 80% |
| `max_ltv_second_home` | 75% |
| `max_ltv_investment` | 70% |
| `max_cltv_primary_residence` | 80% |

**See also:** POL-VAL-001.

### CONV-COR-003 — Elevated credit floor

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The representative credit score for a cash-out refinance must be at least 680, or at least 700 where loan-to-value exceeds 75 percent. This floor sits above the general credit floor in POL-CRD-001 and governs where the two differ.

| Parameter | Value |
| --- | --- |
| `min_representative_score` | 680 |
| `min_representative_score_ltv_above_75` | 700 |
| `ltv_trigger` | 75% |

**See also:** POL-CRD-001.

### CONV-COR-004 — Reserve requirement

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

At least six months of the qualifying housing expense must remain available as reserves after closing. Cash proceeds from the transaction itself may not be counted toward this requirement, because counting the loan's own proceeds as the borrower's reserves would make the test circular.

| Parameter | Value |
| --- | --- |
| `min_months_reserves` | 6 |
| `proceeds_countable_as_reserves` | no |

**Condition raised when unsatisfied.** Evidence reserves of at least {required_months} months of the qualifying housing expense from assets other than loan proceeds.

**See also:** POL-AST-003.

### CONV-COR-005 — Stated use of proceeds

- **Source category:** `COMMON_INDUSTRY_PRACTICE` · **Severity:** `ADVISORY` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

The borrower's stated use of proceeds is recorded for the file. It is context for the underwriter, not an eligibility test: a permissible use does not cure a leverage or credit failure, and an unusual use is not by itself a basis for an adverse outcome. Where the stated use contradicts other evidence in the file, the contradiction is a data-quality matter under POL-FRD-001.

**See also:** POL-FRD-001.

## 5. Documentation requirements

- Title evidence establishing the acquisition date.
- Payoff statements for every lien being retired.
- Asset evidence supporting the post-closing reserve requirement.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-CONV-002
- POL-AST-003
- POL-CRD-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial product version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
