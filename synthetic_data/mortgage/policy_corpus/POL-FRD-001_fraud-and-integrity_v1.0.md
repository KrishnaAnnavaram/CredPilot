---
policy_id: POL-FRD-001
title: Fraud Indicators and Document Integrity
version: 1.0
family: fraud-and-integrity
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
priority: 22
supersedes: null
superseded_by: null
requires_human_review: true
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - FRD-IND-001
  - FRD-IND-002
  - FRD-IND-003
  - FRD-IND-004
synthetic: true
---

# Fraud Indicators and Document Integrity

**POL-FRD-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how misrepresentation is detected and what happens when it is suspected. Fraud in this corpus is never a field the file asserts; it is a conclusion drawn from evidence that does not agree with itself.

## 2. Scope

Applies to every application. Every finding under this document requires human review, and no automated component may clear a finding it raised.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Indicator.** An observation that evidence is inconsistent. An indicator is not a finding of fraud, and recording one is not an accusation.

## 4. Rules

### FRD-IND-001 — Indicators arise from cross-source inconsistency

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Indicators are raised where independent sources disagree in ways that have no innocent arithmetic explanation: year-to-date earnings that cannot be produced by the stated rate and elapsed periods; an employer name that nearly matches another source but is not identical; a deposit exactly matching a claimed gift with no corresponding donor withdrawal; a contract price differing from the application; a valuation naming an owner the title does not; or the same document instance appearing on more than one application. Each indicator records the two sources it arose from, so a reviewer can evaluate the evidence rather than a score.

| Parameter | Value |
| --- | --- |
| `evidence_link_required` | yes |
| `score_without_evidence_permitted` | no |

**See also:** POL-INC-001, POL-EMP-001, POL-AST-004.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Cross-document validation graph' - the strongest fraud cases arise from inconsistent evidence rather than from an arbitrary fraud flag; the OCC identifies false application information, inflated appraisals and identity theft among mortgage-fraud concerns.

### FRD-IND-002 — Document tampering

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A document showing signs of alteration - internal totals that do not sum, inconsistent formatting within a single field, a period that does not match the issuer's stated cycle, or metadata inconsistent with the stated issuer - is quarantined and the file is escalated. The document is not used for qualification while the finding is open, and it is not simply replaced with a fresh copy from the same source without the escalation being recorded.

| Parameter | Value |
| --- | --- |
| `on_detection` | quarantine the document and escalate |
| `use_for_qualification_while_open` | no |
| `reason_code` | HR-DOCUMENT-INTEGRITY |

**See also:** POL-DOC-001, POL-UWR-001.

### FRD-IND-003 — An automated component may not clear its own finding

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Any indicator raised under this document is cleared only by an authorised human reviewer, whose identity, reasoning and date are recorded. An automated component may gather evidence, present the comparison and recommend a disposition. It may not close the finding, and a file carrying an open finding may not reach a clear-to-close state.

**See also:** POL-UWR-001, POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Human-in-the-loop classification' - suspected document manipulation requires human or fraud review because the AI should not clear itself.

### FRD-IND-004 — An indicator is not by itself an adverse-action reason

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Where an application is declined following a fraud review, the reasons communicated must be the specific, accurate principal reasons for the decision. 'Fraud indicator raised' is not a reason; the specific factual basis the reviewer relied upon is. This obligation does not weaken because the indicator was produced by an algorithm.

**See also:** POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Regulatory and agency landscape' - the CFPB has stated that adverse-action requirements do not disappear because a creditor uses a complex algorithm.

## 5. Documentation requirements

- For every indicator: the two sources, the specific inconsistency and the computed variance.
- The reviewer's disposition with identity, reasoning and date.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-KYC-001
- POL-DOC-001
- POL-UWR-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
