---
policy_id: POL-DOC-001
title: "Documentation Requirements, Completeness and Freshness"
version: 1.0
family: documentation
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
priority: 60
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - DOC-REQ-001
  - DOC-REQ-002
  - DOC-REQ-003
  - DOC-REQ-004
  - DOC-REQ-005
  - DOC-REQ-006
synthetic: true
---

# Documentation Requirements, Completeness and Freshness

**POL-DOC-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines what must be in the file, how current it must be, and how an incomplete file is treated. Incompleteness is the most common state a real file is in, and treating it as a decline is the most common way to get it wrong.

## 2. Scope

Applies to every application. The freshness windows here are the defaults; a source-specific document that states a different window governs for its own evidence.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### DOC-REQ-001 — Baseline document set

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Every application requires a completed application form, identity evidence, a credit report, income evidence for every source relied upon, asset evidence for every asset relied upon, and a valuation. Purchase transactions additionally require the executed contract. Refinances additionally require payoff evidence. Documents required by a source-specific policy are additive to this set.

| Parameter | Value |
| --- | --- |
| `baseline` | application, identity, credit report, income evidence, asset evidence, valuation |
| `purchase_additional` | executed purchase contract |
| `refinance_additional` | payoff statement |

### DOC-REQ-002 — Default freshness windows

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Measured to the note date: a paystub is acceptable for 30 days from its pay-period end; asset statements for 60 days; a credit report for the window in POL-CRD-001; an employment verification for 60 days; a valuation for the window in POL-VAL-001; and a tax return for 120 days before current-period evidence is additionally required. A stale document raises a refresh condition; it is not treated as a missing document, because the difference matters to the borrower.

| Parameter | Value |
| --- | --- |
| `paystub_days` | 30 |
| `asset_statement_days` | 60 |
| `employment_verification_days` | 60 |
| `tax_return_days` | 120 |
| `measured_to` | note date |

**Condition raised when unsatisfied.** Provide a refreshed {document_type}; the current one is {age_days} days old.

**See also:** POL-CRD-001, POL-VAL-001, POL-INC-005.

### DOC-REQ-003 — Completeness is measured and reported

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Document completeness is the proportion of required documents that are received and not stale, computed against the requirement set for this application's product, purpose and income types. The figure is reported with the list of what is missing, never as a bare percentage.

| Parameter | Value |
| --- | --- |
| `formula` | received and current required documents / required documents |
| `report_with` | the itemised list of outstanding documents |

### DOC-REQ-004 — An incomplete file is suspended, not declined

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

Where required documents are outstanding, affected rules evaluate to INDETERMINATE and the application is routed as SUSPENDED_INCOMPLETE with an itemised condition list. A decline recommendation may not be issued on the basis of documents that were never requested. Where the file is complete enough to evaluate every hard rule and one of them fails on verified evidence, the failure stands regardless of unrelated missing documents.

| Parameter | Value |
| --- | --- |
| `routing` | SUSPENDED_INCOMPLETE |
| `decline_on_missing_documents` | no |

**See also:** POL-GEN-001, POL-DEC-001, POL-UWR-001.

### DOC-REQ-005 — Letters of explanation are not self-validating

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

A letter of explanation records the borrower's account of a gap, a deposit, an inquiry or a derogatory event. It is evidence of what the borrower says, not evidence that what they say is so. Where a rule requires corroboration, the letter alone does not satisfy it, and a file cleared solely on the strength of a letter has not met the rule.

| Parameter | Value |
| --- | --- |
| `corroboration_required_where_rule_states` | yes |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Document catalog' - a letter of explanation must be corroborated where required and is not self-validating.

### DOC-REQ-006 — Every extracted field keeps its provenance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

A value extracted from a document is stored with the document identifier, the field name, the extracted value and an extraction confidence. A calculation consuming an extracted value records which extraction it used. Without this, a reviewer cannot tell whether a qualifying income figure came from the paystub, the W-2 or the application.

| Parameter | Value |
| --- | --- |
| `required` | document_id, field_name, value, confidence |
| `calculation_links_to_extraction` | yes |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Data lineage' - lineage must remain queryable at field level.

## 5. Documentation requirements

- The requirement set computed for this application.
- The received-document inventory with dates and staleness.
- The outstanding-document condition list.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-UWR-001
- POL-FRD-001
- POL-DEC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
