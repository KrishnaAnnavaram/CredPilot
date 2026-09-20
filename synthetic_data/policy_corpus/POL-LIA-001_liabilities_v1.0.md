---
policy_id: POL-LIA-001
title: Liabilities and Debt Inclusion
version: 1.0
family: liabilities
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
priority: 45
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - LIA-INC-001
  - LIA-INC-002
  - LIA-INC-003
  - LIA-INC-004
  - LIA-INC-005
  - LIA-INC-006
synthetic: true
---

# Liabilities and Debt Inclusion

**POL-LIA-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Determines which obligations enter the debt-to-income numerator and at what payment amount. The answer is rarely 'the balance': what matters is the monthly payment, whether it will continue, and whether the evidence supports excluding it.

## 2. Scope

Applies to every programme. Every obligation is stored as its own record with its source and its inclusion decision; a single aggregated 'monthly debt' figure is not an acceptable representation.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Recurring monthly obligation.** A payment the borrower is contractually required to make each month that will continue after closing. A payment that ends within the near-term window below is treated separately.

## 4. Rules

### LIA-INC-001 — Every obligation is recorded individually with its inclusion decision

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Each obligation is stored with its creditor, type, balance, monthly payment, remaining term, evidence source and an explicit include or exclude decision citing the rule that produced it. Storing only a total makes the debt-to-income ratio unauditable, because no reviewer can determine which obligations were counted.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Liability/credit model' - store every obligation separately with its source and DTI treatment.

### LIA-INC-002 — Obligations ending within ten months may be excluded

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

An instalment obligation with ten or fewer payments remaining may be excluded from the debt-to-income calculation, provided the remaining term is evidenced and the payment is not so large that it materially affects the borrower's ability to accumulate funds to close. A lease payment is never excluded on this basis regardless of remaining term, because leases are typically renewed or replaced.

| Parameter | Value |
| --- | --- |
| `max_remaining_payments_for_exclusion` | 10 |
| `lease_excluded_from_this_rule` | yes |
| `materiality_guard` | payment above 5 percent of qualifying income |

**Acceptable evidence.** Statement or credit report field showing the remaining term.

### LIA-INC-003 — Revolving accounts use the stated minimum payment

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

A revolving account with an outstanding balance is included at its stated minimum payment. Where no minimum is stated, five percent of the outstanding balance is used. An account with a zero balance is excluded, but the available limit is still recorded because it affects the utilisation measure and the HCLTV calculation for a secured line.

| Parameter | Value |
| --- | --- |
| `fallback_minimum_payment_pct_of_balance` | 5% |
| `zero_balance_excluded` | yes |

**See also:** POL-CRD-003.

### LIA-INC-004 — Deferred and income-driven obligations

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

A deferred obligation, or one in forbearance, is included at the documented payment that will apply when repayment resumes. Where no such payment is documented, one percent of the outstanding balance is used. A documented income-driven payment is used at its stated amount even where that amount is zero, provided the plan documentation is current.

| Parameter | Value |
| --- | --- |
| `fallback_payment_pct_of_balance` | 1% |
| `income_driven_zero_payment_allowed` | yes |
| `plan_documentation_required` | yes |

**Acceptable evidence.** Servicer statement showing the scheduled payment; Current repayment-plan documentation.

### LIA-INC-005 — Obligations paid by another party

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

An obligation on which the borrower is liable but which another party has paid may be excluded where the most recent 12 months of payments from that party are evidenced and the borrower is not the primary obligor of record. Business obligations paid by the borrower's business follow the same test. The exclusion turns on evidence of who actually paid, not on who says they will.

| Parameter | Value |
| --- | --- |
| `required_months_of_third_party_payments` | 12 |

**Acceptable evidence.** 12 months of cancelled cheques or account statements from the paying party.

**Condition raised when unsatisfied.** Provide 12 months of payment evidence from the party paying obligation {liability_id}.

### LIA-INC-006 — Obligations found on the credit report but absent from the application

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

An obligation appearing on the credit report but not declared on the application is added to the liabilities and the debt-to-income ratio is recomputed. The omission itself is recorded as a data-quality finding. Where the recomputed ratio breaches the affordability limit, the file is routed for review rather than declined automatically, because the borrower has not yet had the opportunity to explain or dispute the tradeline.

**Condition raised when unsatisfied.** Confirm or dispute the undeclared obligation {liability_id} identified on the credit report.

**See also:** POL-DTI-001, POL-FRD-001.

## 5. Documentation requirements

- Credit report tradelines for every obligation.
- Statements evidencing remaining term where an exclusion is claimed.
- Third-party payment evidence where LIA-INC-005 is relied upon.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-DTI-001
- POL-CRD-001
- POL-CRD-002

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
