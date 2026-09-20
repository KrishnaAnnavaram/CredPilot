---
policy_id: POL-DEC-001
title: "Decisioning, Recommendations and Adverse-Action Handling"
version: 1.0
family: decisioning
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
priority: 12
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - DEC-REC-001
  - DEC-REC-002
  - DEC-ADV-001
  - DEC-ADV-002
  - DEC-ADV-003
  - DEC-AUD-001
synthetic: true
---

# Decisioning, Recommendations and Adverse-Action Handling

**POL-DEC-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines what the copilot may output, what only a human may output, and what must be communicated when an application is not approved.

## 2. Scope

Applies to every application at every decision point.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### DEC-REC-001 — Permitted copilot outputs

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

The copilot may output an eligibility determination, a risk assessment, a condition list and an underwriting recommendation drawn from the controlled vocabulary: APPROVE_RECOMMENDATION, APPROVE_WITH_CONDITIONS, REFER, MANUAL_REVIEW_REQUIRED, SUSPENDED_INCOMPLETE or DECLINE_RECOMMENDATION. It may not output a credit decision, a clear-to-close or a funding instruction. Every recommendation carries the rule ids, policy versions and calculation records that support it.

| Parameter | Value |
| --- | --- |
| `recommendation_vocabulary` | APPROVE_RECOMMENDATION, APPROVE_WITH_CONDITIONS, REFER, MANUAL_REVIEW_REQUIRED, SUSPENDED_INCOMPLETE, DECLINE_RECOMMENDATION |
| `human_only` | credit decision, clear-to-close, funding |
| `citations_required` | yes |

**See also:** POL-GEN-001, POL-UWR-001.

### DEC-REC-002 — A decline recommendation is always routed to a human

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PROCESS`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A decline recommendation, and any high-value exposure, is routed for human review rather than auto-decided. The copilot prepares the file and the reasoning; the authorised decision maker decides. This is the control that keeps an automated component from issuing an adverse outcome on its own authority.

| Parameter | Value |
| --- | --- |
| `auto_decision_permitted` | no |

**See also:** POL-UWR-001.

### DEC-ADV-001 — Adverse-action reasons must be specific and accurate

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Where an application is denied or approved on materially different terms, the applicant is entitled to a statement of the specific principal reasons for the action. The reasons must be the actual reasons the decision logic relied upon, not a generic category selected for convenience. This obligation applies with equal force where the decision involved a complex algorithm, and it is not satisfied by stating that a model produced a score.

| Parameter | Value |
| --- | --- |
| `reason_source` | the actual decision logic, traced to rule evaluations |
| `generic_reasons_permitted` | no |
| `algorithm_exemption` | no |

**See also:** POL-FRD-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Regulatory and agency landscape' - the CFPB has stated that ECOA / Regulation B adverse-action requirements do not disappear because a creditor uses a complex algorithm.

### DEC-ADV-002 — Reasons based on a consumer report carry additional notice duties

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Where the adverse action is based in whole or in part on information in a consumer report, the notice obligations attaching to that use apply in addition to the statement of reasons. The decision record must therefore identify whether consumer-report information contributed to the outcome.

| Parameter | Value |
| --- | --- |
| `record_required` | whether a consumer report contributed |

**See also:** POL-CRD-001.

### DEC-ADV-003 — Prohibited bases may never appear in a reason

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

No decision reason may reference, or be derived from, a prohibited basis or from demographic monitoring information. Where a reason would need to reference such a characteristic to be accurate, the decision itself is unsupportable and must be reconsidered rather than re-worded.

**See also:** POL-CRD-001, POL-SEC-001.

### DEC-AUD-001 — Every decision is auditable end to end

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

A decision record must permit a reviewer to reconstruct, without access to the original system: which policy versions applied and why those versions; which rules were evaluated and with what inputs; which calculations produced those inputs and from which evidence; which risk findings were open; who decided; and when. A decision that cannot be reconstructed to that level has not been documented, however confident its narrative sounds.

| Parameter | Value |
| --- | --- |
| `reconstructable_without_source_system` | yes |
| `required_chain` | policy version -> rule -> calculation -> evidence -> decision reason |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Data lineage' - the lineage record must answer more than the number; it must carry formula version, inputs, evidence and the policy rule version applied.

## 5. Documentation requirements

- The decision record with its full supporting chain.
- The statement of specific reasons for any adverse action.
- The human decision maker's identity and timestamp.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-GEN-001
- POL-UWR-001
- POL-CRD-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
