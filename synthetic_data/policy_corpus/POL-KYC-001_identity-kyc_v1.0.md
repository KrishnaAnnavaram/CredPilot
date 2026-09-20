---
policy_id: POL-KYC-001
title: Identity Verification and Customer Identification
version: 1.0
family: identity-kyc
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
priority: 20
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - KYC-IDV-001
  - KYC-IDV-002
  - KYC-IDV-003
synthetic: true
---

# Identity Verification and Customer Identification

**POL-KYC-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how the applicant's identity is established. Identity is a precondition for everything else in the file: an unverified identity means the credit report, the income evidence and the assets have not been tied to anyone.

## 2. Scope

Applies to every applicant on every application, before any credit decision is reached.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### KYC-IDV-001 — Risk-based identity verification is required

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The lender must maintain risk-based procedures to verify each applicant's identity, collecting at minimum name, date of birth, address and an identification number, and forming a reasonable belief that it knows the applicant's identity. For lending, the customer relationship for these purposes is established when an enforceable relationship comes into being. The verification result, its method and its date are recorded.

| Parameter | Value |
| --- | --- |
| `minimum_elements` | name, date of birth, address, identification number |
| `outcome_values` | VERIFIED, REFERRED, FAILED |

**Acceptable evidence.** Identity verification result with method and provider; Government identification document or documentary equivalent.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Lifecycle controls and evidence' - banks need risk-based identity-verification procedures and a loan account is opened for CIP purposes when an enforceable relationship is established.

### KYC-IDV-002 — Identity mismatch stops the file

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Where identity cannot be verified, or where the identity elements in the file conflict - a name that differs from the identification document, a date of birth inconsistent with the credit file, an identification number associated with a different name - the application stops and is escalated to the financial-crime function. It does not proceed to ordinary underwriting while the discrepancy is open, and it is never automatically approved on the strength of the rest of the file.

| Parameter | Value |
| --- | --- |
| `on_mismatch` | STOP and escalate |
| `ordinary_underwriting_may_proceed` | no |
| `reason_code` | HR-IDENTITY-MISMATCH |

**See also:** POL-FRD-001, POL-UWR-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Human-in-the-loop classification' - identity that cannot be verified is a stop-and-escalate case, not ordinary auto-approval.

### KYC-IDV-003 — Identifiers are tokenised in every downstream system

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Taxpayer identification numbers, full financial account numbers, identification-document numbers and credit-file identifiers are stored as tokens and displayed masked. No downstream system, prompt, log or report receives them in plaintext. An underwriting component may need a credit score; it never needs a taxpayer identification number.

| Parameter | Value |
| --- | --- |
| `tokenised` | taxpayer id, account numbers, document numbers, credit ids |
| `display_form` | masked |
| `plaintext_in_logs` | no |

**See also:** POL-SEC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'AI redaction policy' - mask or tokenise identifiers and preserve stable surrogate keys so relationships remain testable.

## 5. Documentation requirements

- The identity verification record with method, provider, date and result.
- The escalation record where KYC-IDV-002 applies.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-FRD-001
- POL-SEC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
