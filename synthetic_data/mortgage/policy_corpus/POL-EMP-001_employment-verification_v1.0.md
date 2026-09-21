---
policy_id: POL-EMP-001
title: Employment Verification
version: 1.0
family: employment-verification
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
priority: 47
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - EMP-VER-001
  - EMP-VER-002
  - EMP-VER-003
  - EMP-VER-004
synthetic: true
---

# Employment Verification

**POL-EMP-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how employment is verified, when it must be re-verified, and how a verification that contradicts the application is handled.

## 2. Scope

Applies to every employed borrower. Self-employed borrowers verify the existence and operation of the business under POL-INC-005 instead.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### EMP-VER-001 — Independent verification is required

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Employment must be verified independently of documents the borrower supplied: a written verification obtained directly from the employer, a verbal verification recorded with the name and title of the person contacted, or a validated third-party verification report. A paystub supplied by the borrower is evidence of income; it is not independent verification of employment.

| Parameter | Value |
| --- | --- |
| `acceptable_methods` | written employer verification, recorded verbal verification, validated third-party report |
| `borrower_supplied_documents_sufficient` | no |

**Acceptable evidence.** Written verification of employment; Verbal verification record naming the contact and date; Third-party verification report.

**Condition raised when unsatisfied.** Obtain independent employment verification for {employer}.

### EMP-VER-002 — Re-verification before closing

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Employment is re-verified within ten business days of the note date. Where the re-verification shows the borrower is no longer employed, or shows materially different terms, the income calculation and the affordability result are re-run before closing proceeds. A file cleared to close on employment that has since ended is a control failure, not a timing inconvenience.

| Parameter | Value |
| --- | --- |
| `reverification_window_business_days` | 10 |

**Condition raised when unsatisfied.** Re-verify employment within ten business days of closing.

**See also:** POL-UWR-001.

### EMP-VER-003 — Verification that contradicts the application

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where the verification reports an employer name, job title, start date or compensation that differs materially from the application, the verified value governs, the discrepancy is recorded with both values and their sources, and the file is routed for review. A start date differing by more than 60 days, or an employer name that is similar but not identical, is treated as material.

| Parameter | Value |
| --- | --- |
| `material_start_date_variance_days` | 60 |
| `similar_but_not_identical_employer` | material |
| `governing_value` | the verified value |

**See also:** POL-FRD-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Missing/conflicting data workflow' - an application start date differing from the verification requires an authoritative timeline and a condition if unresolved.

### EMP-VER-004 — Verification freshness

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

An employment verification is valid for 60 days from its completion date for underwriting purposes, subject to the pre-closing re-verification in EMP-VER-002. A verification older than that is refreshed rather than relied upon.

| Parameter | Value |
| --- | --- |
| `max_age_days` | 60 |

**See also:** POL-DOC-001.

## 5. Documentation requirements

- The verification record itself, with method, date and the contact where verbal.
- The pre-closing re-verification record.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-INC-002
- POL-EMP-002
- POL-DOC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
