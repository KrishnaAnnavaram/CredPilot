---
policy_id: POL-INC-001
title: Income General Principles and Qualifying Income
version: 1.0
family: income-general
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
priority: 48
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - INC-GEN-001
  - INC-GEN-002
  - INC-GEN-003
  - INC-GEN-004
  - INC-GEN-005
  - INC-GEN-006
synthetic: true
---

# Income General Principles and Qualifying Income

**POL-INC-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Establishes what qualifying income is, how it differs from declared and verified income, and the tests every income source must satisfy before any amount enters the affordability calculation.

## 2. Scope

Applies to every income source in every programme. The source-specific documents POL-INC-002 through POL-INC-007 state how each type is calculated; this document states the tests they all share.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Declared income.** The amount the applicant stated on the application. It is never used to qualify. It is retained so the file can show what changed on verification.

**Verified income.** The amount authoritative evidence establishes. For a salaried borrower this is what the paystub, W-2 and employment verification jointly support.

**Qualifying income.** The amount policy permits to be used, after history, trend and continuance tests are applied to the verified amount. Qualifying income is frequently lower than verified income and is never higher.

**Continuance.** A reasonable expectation that the income will continue for at least the period stated in INC-GEN-003. Continuance is about the income, never about who receives it or where it comes from.

## 4. Rules

### INC-GEN-001 — Declared, verified and qualifying amounts are stored separately

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Each income source carries three amounts: declared, verified and qualifying, each with its own evidence reference and as-of date. Overwriting the three with a single figure is a data-model defect, because it makes it impossible to show which document supported which number or to detect that the application and the evidence disagreed.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Mortgage data, document, calculation, policy and lineage architecture' - declared, observed/verified and qualifying values must be preserved separately.

### INC-GEN-002 — Qualifying income must not exceed verified income

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The qualifying amount for any source must be less than or equal to the verified amount for that source. A qualifying amount above the verified amount means the calculation used a figure the evidence does not support, and the affordability result derived from it is unusable.

| Parameter | Value |
| --- | --- |
| `invariant` | qualifying_amount <= verified_amount |

### INC-GEN-003 — Continuance period

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

Income may be used only where it is reasonably expected to continue for at least 36 months from the note date. Where evidence shows a defined end date inside that window - a fixed-term contract, a benefit with a stated expiry, a support order terminating on a known date - the income is excluded unless documented renewal or replacement evidence is provided. A source with no defined end date is presumed continuing.

| Parameter | Value |
| --- | --- |
| `continuance_months` | 36 |
| `defined_end_date_within_window` | exclude unless renewal evidenced |

**Acceptable evidence.** Award letters, contracts or orders showing any end date.

### INC-GEN-004 — Income source is never a basis for discounting

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Income may not be discounted or refused because of its source where that source is public assistance, retirement, disability or a protected characteristic of the recipient. Analysis is confined to the verifiable amount and its likely continuance. Applying a haircut to a benefit source that would not be applied to wage income of the same amount and stability is a fair-lending failure, not a conservative underwriting choice.

**See also:** POL-CRD-001, POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Income model' - ECOA prohibits discrimination based on receipt of public-assistance income; legitimate analysis is confined to amount and likely continuance.

### INC-GEN-005 — Non-taxable income may be grossed up

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Verified income that is not subject to federal income tax may be increased by 15 percent for qualifying purposes, provided the non-taxable status is documented. The adjustment is recorded as its own calculation step so the pre-adjustment amount remains visible. The adjustment is never applied to an amount whose tax status is assumed rather than evidenced.

| Parameter | Value |
| --- | --- |
| `gross_up_pct` | 15% |
| `documentation_required` | evidence of non-taxable status |

**See also:** POL-INC-007.

### INC-GEN-006 — Conflicting income evidence is reconciled, never averaged away

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where two sources of income evidence disagree by more than five percent of the lower figure, the discrepancy is recorded explicitly with both values and their document references, the lower verified figure is used pending resolution, and the file is routed for review. Silently averaging the two, or taking the higher, conceals the conflict that the reviewer needs to see.

| Parameter | Value |
| --- | --- |
| `materiality_threshold` | 5% |
| `interim_treatment` | use the lower verified figure |
| `record` | both values, both document ids, the computed variance |

**See also:** POL-FRD-001, POL-UWR-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Missing/conflicting data workflow' - reconcile pay frequency, YTD and employment verification, and use the verified qualifying amount.

## 5. Documentation requirements

- Evidence for every income source, referenced by document id.
- The qualifying-income calculation record with its per-source components.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-DTI-001
- POL-EMP-001
- POL-DOC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
