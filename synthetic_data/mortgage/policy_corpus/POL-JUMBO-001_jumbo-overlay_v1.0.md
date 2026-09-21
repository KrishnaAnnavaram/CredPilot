---
policy_id: POL-JUMBO-001
title: "Jumbo and High-Value Mortgage Overlay"
version: 1.0
family: jumbo-overlay
effective_date: 2026-01-01
expiration_date: 2026-07-01
product_scope:
  - jumbo
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
priority: 25
supersedes: null
superseded_by: "POL-JUMBO-001 v2.0"
requires_human_review: true
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - JMB-ELG-001
  - JMB-ELG-004
  - JMB-ELG-002
  - JMB-ELG-003
synthetic: true
---

# Jumbo and High-Value Mortgage Overlay

**POL-JUMBO-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

A fictional investor overlay for loan amounts above the applicable conforming limit. Real jumbo underwriting criteria are proprietary to the lenders and private investors that set them; nothing in this document should be read as describing any real institution's jumbo policy.

## 2. Scope

Applies to first-lien transactions above the conforming limit, in addition to - not instead of - the credit, income, asset and property documents. Where this overlay is stricter, the overlay governs.

- **Products:** jumbo
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### JMB-ELG-001 — Definition of a jumbo transaction

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A transaction is jumbo under this document when the first-lien loan amount exceeds the applicable conforming limit recorded in GEN-ELG-003. A jumbo loan is not a conventional conforming loan with a larger number; it is a separate execution with its own leverage, reserve and review requirements, and it is never eligible for the conforming leverage matrix in POL-CONV-001.

| Parameter | Value |
| --- | --- |
| `trigger` | loan amount above the applicable conforming limit |

**See also:** POL-GEN-001, POL-CONV-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Product taxonomy' - jumbo criteria are dominated by proprietary lender and investor overlays that are not public, so this entire document is a fictional overlay.

### JMB-ELG-004 — Every jumbo file is reviewed by a human underwriter

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

No jumbo application may reach a recommendation without human underwriting review, irrespective of how strong the file appears. The reason is explicit: real jumbo criteria are set by private investor overlays that are not publicly documented, so an automated component working from this synthetic overlay cannot be assumed to have applied the criteria a real investor would apply. The copilot may prepare the review package; it may not clear the file.

| Parameter | Value |
| --- | --- |
| `human_review` | mandatory |
| `reason_code` | HR-JUMBO-EXPOSURE |

**See also:** POL-UWR-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Human-in-the-loop classification' - jumbo exposure is classified HUMAN REVIEW REQUIRED because internal overlays are not publicly known.

### JMB-ELG-002 — Leverage and credit floor

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Loan-to-value must not exceed 80 percent on a primary residence and 75 percent on any other occupancy, and the representative credit score must be at least 700.

| Parameter | Value |
| --- | --- |
| `max_ltv_primary_residence` | 80% |
| `max_ltv_other_occupancy` | 75% |
| `min_representative_score` | 700 |

### JMB-ELG-003 — Reserve and documentation requirement

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

At least six months of the qualifying housing expense must remain available after closing, and every income source must be supported by full documentation. Reduced-documentation treatment is not available under this overlay.

| Parameter | Value |
| --- | --- |
| `min_months_reserves` | 6 |
| `documentation_level` | full |

**See also:** POL-AST-003, POL-DOC-001.

## 5. Documentation requirements

- Full documentation of every income source, with no reduced-documentation alternatives.
- Asset evidence covering both funds to close and the reserve requirement.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-CONV-001
- POL-UWR-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Original overlay. Superseded on 2026-07-01 by version 2.0, which tightens leverage and reserves and adds a second-appraisal trigger. |
| (later) | from 2026-07-01 | This version is superseded by POL-JUMBO-001 v2.0. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
