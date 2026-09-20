---
policy_id: POL-GEN-001
title: General Mortgage Eligibility and Programme Framework
version: 1.0
family: general-eligibility
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
priority: 10
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - GEN-ELG-001
  - GEN-ELG-002
  - GEN-ELG-003
  - GEN-ELG-004
  - GEN-ELG-005
  - GEN-ELG-006
synthetic: true
---

# General Mortgage Eligibility and Programme Framework

**POL-GEN-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Establishes the authority layers, the decision vocabulary and the order of evaluation that every other policy in this corpus depends on. It is the document a retrieval agent should reach for when it needs to know what kind of statement it is looking at, rather than a specific threshold.

## 2. Scope

Applies to every application in every programme. Where a programme-specific document states a different requirement, the programme-specific document governs for that programme only, and this document continues to govern the vocabulary and the order of evaluation.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Authority layer.** Where a requirement comes from. Five layers are recognised: regulatory, agency or investor, publicly published lender guidance, common industry practice, and this lender's own synthetic internal policy. A requirement may never be presented at a higher layer than its actual source.

**Declared, verified and qualifying value.** Three distinct values that must be preserved separately. Declared is what the applicant stated. Verified is what authoritative evidence established. Qualifying is the value underwriting is permitted to use. A borrower may declare 9,000 of monthly income, verify 8,700, and qualify on 8,250; overwriting all three with one figure destroys the audit trail.

**As-of date.** The underwriting decision date used to select which policy version applies. It is not the date the question is asked.

**Eligibility.** Whether the loan satisfies a defined programme rule set. Eligibility is never a synonym for approval.

## 4. Rules

### GEN-ELG-001 — Order of evaluation

- **Source category:** `COMMON_INDUSTRY_PRACTICE` · **Severity:** `ADVISORY` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Applications are evaluated in a fixed order: authorise access to the case; establish product, purpose, occupancy and the underwriting as-of date; retrieve the policy versions in force on that date; extract and verify evidence; detect conflicts between sources; run deterministic calculations; run deterministic eligibility rules; screen for risk; apply the human-review routing policy; and only then produce a recommendation with its citations. A component that produces a recommendation before the calculations have run has not followed this policy.

**See also:** POL-UWR-001, POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Agentic AI architecture mapping' - safe orchestration sequence.

### GEN-ELG-002 — Applicable policy version is selected by as-of date

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The rule set applied to an application is the set of policy versions whose effective window contains the application's underwriting as-of date. Retrieving the most recently published version of a policy is a policy-selection defect whenever an earlier version was still in force on that date. A decision that cites a version not in force on the as-of date is not supportable and must be re-evaluated.

| Parameter | Value |
| --- | --- |
| `selection_basis` | underwriting_as_of_date |
| `fallback_when_before_first_version` | earliest published version, flagged |

**Acceptable evidence.** Policy front matter effective_date and expiration_date.

**See also:** POL-DOC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Policy-document architecture' - the corpus must answer 'what policy was applicable on the underwriting decision date?'.

### GEN-ELG-003 — Loan amount must be within the programme's applicable limit

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A loan offered as conventional conforming must not exceed the applicable one-unit conforming limit for its area. For 2026 the published baseline one-unit conforming limit is 832,750 and the high-cost area ceiling is 1,249,125; the published 2026 FHA one-unit floor is 541,287 against the same high-cost ceiling. These are programme and geography reference points published by FHFA and HUD. They are not a generic maximum mortgage, and a loan above the conforming limit is not ineligible - it is simply not conforming, and must be executed under a different programme.

| Parameter | Value |
| --- | --- |
| `conforming_baseline_one_unit_2026` | 832,750 |
| `high_cost_ceiling_one_unit_2026` | 1,249,125 |
| `fha_floor_one_unit_2026` | 541,287 |

**See also:** POL-CONV-001, POL-JUMBO-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Executive summary and research frame' - FHFA 2026 conforming limits and HUD 2026 FHA limits.

### GEN-ELG-004 — Eligibility, risk, recommendation and credit decision are distinct

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Five results must be recorded separately and must never be collapsed into one another: the eligibility determination against a programme rule set; the risk assessment; the copilot's underwriting recommendation; the authorised human credit decision; and the clear-to-close or funding decision. A loan can be programme-eligible and still be declined for creditworthiness; a strong borrower can be ineligible for one product configuration and eligible for another. An automated component may produce the first three. It may not produce the last two.

| Parameter | Value |
| --- | --- |
| `eligibility_values` | ELIGIBLE, INELIGIBLE, INDETERMINATE |
| `recommendation_values` | APPROVE_RECOMMENDATION, APPROVE_WITH_CONDITIONS, REFER, MANUAL_REVIEW_REQUIRED, SUSPENDED_INCOMPLETE, DECLINE_RECOMMENDATION |
| `human_only_values` | CLEAR_TO_CLOSE, credit decision, funding decision |

**See also:** POL-DEC-001, POL-UWR-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Decision taxonomy'.

### GEN-ELG-005 — Missing evidence yields INDETERMINATE, not a negative result

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

Every rule evaluates to exactly one of PASS, FAIL, REFER, NOT_APPLICABLE or INDETERMINATE. A rule whose inputs are missing or unverified evaluates to INDETERMINATE and raises a documentation condition. It does not evaluate to FAIL. Treating absent evidence as a failure converts a curable processing gap into an adverse outcome the file does not support.

| Parameter | Value |
| --- | --- |
| `outcomes` | PASS, FAIL, REFER, NOT_APPLICABLE, INDETERMINATE |

**Condition raised when unsatisfied.** Provide the evidence identified for rule {rule_id} so the rule can be evaluated.

**See also:** POL-DOC-001, POL-UWR-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Eligibility rule taxonomy' - INDETERMINATE is particularly important for missing evidence.

### GEN-ELG-006 — Ability to repay must be established from verified information

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A covered residential mortgage requires a reasonable, good-faith determination of the consumer's ability to repay, made from verified information about income or assets, obligations, and a measure such as debt-to-income or residual income. This is a regulatory obligation under TILA / Regulation Z and it sits above every product rule in this corpus: satisfying an investor's DTI matrix does not by itself discharge it.

**Acceptable evidence.** Verified income and asset records; Verified obligation records; The committed affordability calculation and its inputs.

**See also:** POL-DTI-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Regulatory and agency landscape' - CFPB Regulation Z 12 CFR 1026.43 ability-to-repay standards.

## 5. Documentation requirements

- Every rule evaluation records the rule id, the policy version, the input values it consumed and the resulting outcome.
- Every decision records which rule evaluations supported it.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-CONV-001 for the base conventional product
- POL-DEC-001 for decision and adverse-action handling
- POL-UWR-001 for conditions, manual review and exception authority

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial framework version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
