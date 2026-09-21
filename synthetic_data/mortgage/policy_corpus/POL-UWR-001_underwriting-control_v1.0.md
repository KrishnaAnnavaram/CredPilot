---
policy_id: POL-UWR-001
title: "Conditions, Manual Review and Exception Authority"
version: 1.0
family: underwriting-control
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
priority: 15
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - UWR-HRV-001
  - UWR-CND-001
  - UWR-CND-002
  - UWR-EXC-001
  - UWR-EXC-002
synthetic: true
---

# Conditions, Manual Review and Exception Authority

**POL-UWR-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines when a file must reach a human, how conditions are managed, and who may approve a departure from policy. This is the document that keeps the copilot inside its authority.

## 2. Scope

Applies to every application. The routing table in UWR-HRV-001 is mandatory: a file matching any trigger reaches a human regardless of how the rest of the file looks.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Condition.** An outstanding item that must be satisfied before the transaction can proceed. Conditions have an owner, a required evidence type and a status.

**Exception.** An approved departure from a stated policy requirement, granted by a named individual with the authority to grant it, recorded with its reasoning.

## 4. Rules

### UWR-HRV-001 — Mandatory human-review triggers

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A file reaches a human underwriter whenever any of the following is present: a decline recommendation; a jumbo or otherwise high-value exposure; self-employment income; any fraud or document-integrity indicator; an identity verification that is not clean; a conflict between evidence sources that the deterministic rules could not reconcile; an unsourced large deposit; an occupancy contradiction; a valuation or collateral finding; an automated-underwriting refer or caution result; a requested policy exception; an affordability result within two percentage points of its limit; or an application where a security event was raised. The list is a floor, not a ceiling: an underwriter may take any file.

| Parameter | Value |
| --- | --- |
| `borderline_band_pct_points` | 2 |
| `triggers` | decline, jumbo, self-employment, fraud indicator, identity not clean, unresolved conflict, unsourced deposit, occupancy contradiction, collateral finding, AUS refer or caution, exception request, borderline affordability, security event |

**See also:** POL-DEC-001, POL-SEC-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Human-in-the-loop classification' - the recommended synthetic control policy for which cases require human review.

### UWR-CND-001 — Condition lifecycle

- **Source category:** `COMMON_INDUSTRY_PRACTICE` · **Severity:** `CONDITIONAL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Every condition is created with a category, the text of what is required, the evidence that will satisfy it, an owner and a status of OPEN. It moves to CLEARED only when the evidence is received and accepted, or to WAIVED only under an approved exception. Clearing a condition may introduce new information, which requires the affected calculations and rules to be re-run - a cleared condition is not automatically a neutral event.

| Parameter | Value |
| --- | --- |
| `statuses` | OPEN, CLEARED, WAIVED |
| `clearance_triggers_recalculation` | yes |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Lifecycle controls and evidence' - new information can require recalculation and resubmission.

### UWR-CND-002 — Prior-to-close conditions gate the clear-to-close

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Clear-to-close requires every prior-to-close condition to be CLEARED or WAIVED under an approved exception, the pre-closing employment re-verification to be complete, insurance to be in force, and title to be clear of unresolved exceptions. Clear-to-close is recorded with the identity of the person who granted it and the timestamp; it is never produced by an automated component.

| Parameter | Value |
| --- | --- |
| `requires_all_ptc_cleared` | yes |
| `granted_by` | authorised human only |

**See also:** POL-TTL-001, POL-EMP-001.

### UWR-EXC-001 — Exception authority

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

An exception may be granted only by a named individual holding the authority level for that rule's severity, and never by the person who underwrote the file alone. An exception to an ADVISORY or CONDITIONAL rule requires underwriting-manager authority. An exception to a HARD_FAIL rule requires credit-committee authority. Regulatory rules may not be excepted at any level. Every exception records the rule, the reason, the compensating factors relied upon, the approver and the date.

| Parameter | Value |
| --- | --- |
| `advisory_and_conditional` | underwriting manager |
| `hard_fail` | credit committee |
| `regulatory` | no exception available |
| `self_approval_permitted` | no |

**See also:** POL-GEN-001.

### UWR-EXC-002 — An automated component may never grant an exception

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

No automated component may grant, recommend granting itself, or act as though an exception has been granted. It may identify that an exception would be required, assemble the compensating factors and route the request. A recommendation that assumes an exception not yet approved is a defect, not an optimistic forecast.

**See also:** POL-DEC-001, POL-SEC-001.

## 5. Documentation requirements

- The condition register with status history.
- The human-review record: reviewer, trigger, reasoning and outcome.
- The exception record where one was granted.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-DEC-001
- POL-FRD-001
- POL-DOC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
