---
policy_id: POL-TTL-001
title: "Title, Lien Position and Property Insurance"
version: 1.0
family: title-and-insurance
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
priority: 58
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - TTL-LIE-001
  - TTL-LIE-002
  - TTL-INS-001
  - TTL-INS-002
synthetic: true
---

# Title, Lien Position and Property Insurance

**POL-TTL-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines what must be true about ownership, lien priority and insurance before funds are released. These are closing controls: they rarely change the credit decision and they routinely stop a closing.

## 2. Scope

Applies to every application from the point a title commitment is obtained through funding.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### TTL-LIE-001 — Required lien position

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The security instrument must hold first-lien position, with an acceptable title policy insuring that position. Any lien that would take priority - unpaid property taxes, a mechanic's lien, a recorded judgment, a prior mortgage not being paid off - must be cleared or subordinated before funding. Acceptable title and the required lien priority are conditions of the loan, not documentation formalities.

| Parameter | Value |
| --- | --- |
| `required_position` | 1 |

**Acceptable evidence.** Title commitment; Payoff or release evidence for prior liens.

**Condition raised when unsatisfied.** Clear or subordinate title exception {exception_id}.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Lifecycle controls and evidence' - agency requirements include acceptable title and the required lien priority.

### TTL-LIE-002 — Title exceptions

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Exceptions are classified on receipt. Standard exceptions such as utility easements and recorded subdivision restrictions are acceptable without action. Exceptions affecting marketability, access or the insured lien position require clearance. An unresolved exception in the second category at the point of clear-to-close is a hard stop regardless of the strength of the credit file.

| Parameter | Value |
| --- | --- |
| `acceptable_without_action` | utility easements, subdivision restrictions |
| `requires_clearance` | marketability, access, lien position |

### TTL-INS-001 — Hazard insurance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Hazard insurance must be in force at closing with coverage at least equal to the lesser of the loan amount or the estimated replacement cost of the improvements, with the lender named as mortgagee and the policy effective on or before the closing date. The annual premium divided by 12 enters the qualifying housing expense. A binder effective after the closing date leaves the collateral uninsured on day one.

| Parameter | Value |
| --- | --- |
| `min_coverage` | lesser of loan amount or replacement cost |
| `effective_by` | closing date |
| `mortgagee_clause_required` | yes |

**Acceptable evidence.** Policy or binder showing coverage, effective date and mortgagee.

**Condition raised when unsatisfied.** Provide evidence of hazard insurance effective by closing.

**See also:** POL-DTI-001.

### TTL-INS-002 — Vesting must match the borrowers

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Title vesting at closing must match the borrowers on the note. Where a non-borrowing party will hold title, the party must execute the security instrument, and the arrangement is recorded. A vesting mismatch discovered after funding cannot be corrected by agreement alone.

**Condition raised when unsatisfied.** Reconcile the title vesting with the borrowers on the note.

## 5. Documentation requirements

- Title commitment with every exception listed.
- Hazard insurance policy or binder with the mortgagee clause.
- Flood insurance evidence where POL-PRP-001 requires it.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-PRP-001
- POL-UWR-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
