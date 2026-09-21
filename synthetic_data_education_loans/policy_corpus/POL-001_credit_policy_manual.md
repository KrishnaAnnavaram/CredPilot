---
policy_id: POL-001
title: Master Credit Policy and Governance
version: 1.0
effective_date: 2026-01-01
product_scope: [UG, GR, SP, INTL, REFI]
source_category: SYNTHETIC_INTERNAL_POLICY
synthetic: true
issuer: Edgemont Education Lending (fictional)
owner: Credit Policy Office
rule_ids: [EDU-GOV-001, EDU-GOV-002, EDU-GOV-003, EDU-GOV-004]
---

# POL-001 -- Master Credit Policy and Governance

## 1. Purpose and Scope

This document establishes the master credit policy framework for Edgemont Education Lending. It governs all private education loan products originated, serviced, or acquired by Edgemont, including Undergraduate (UG), Graduate (GR), Specialty/Professional (SP), International Student (INTL), and Refinance (REFI) programs. All subordinate policies, underwriting guidelines, pricing matrices, and operational procedures must conform to the principles and authority structure defined herein.

**EDU-GOV-001 -- Policy Scope and Applicability.** Every credit decision rendered by Edgemont Education Lending -- whether automated, assisted, or manual -- shall be governed by this master policy and its subordinate documents (POL-002 through POL-006 and any future addenda). No loan may be originated, modified, or refinanced outside this framework without an approved exception recorded in the Exception Ledger.

## 2. Decision Outcomes

All applications processed through Edgemont's decisioning engine must resolve to exactly one of four terminal outcomes. No application may remain in an indeterminate state beyond the service-level window (48 hours for automated decisions, 5 business days for manual review).

**EDU-GOV-002 -- Permitted Decision Outcomes.** The four permissible credit decision outcomes are:

| Outcome | Code | Definition |
|---|---|---|
| **APPROVE** | A | Application meets all product-specific underwriting criteria. Loan may proceed to disclosure, acceptance, and disbursement without further credit review. |
| **APPROVE_WITH_CONDITIONS** | AC | Application meets core eligibility but requires satisfaction of one or more stipulations (e.g., cosigner addition, additional documentation, school certification) before disbursement. Conditions must be itemized and communicated to the applicant within 2 business days. |
| **REFER** | R | Application falls outside automated decision boundaries and requires manual adjudication by a Senior Credit Analyst or the Credit Committee. Referral triggers must be documented with the specific rule or parameter that caused the referral. |
| **DECLINE** | D | Application fails one or more knockout criteria or falls below minimum thresholds after full evaluation. Adverse action notices must be issued in compliance with ECOA and FCRA within 30 days, specifying the principal reason(s) for denial. |

Outcomes must be logged with timestamps, the rule ID(s) that drove the decision, the identity of the decision-maker (system or human), and a hash reference to the policy version in effect at the time of adjudication.

## 3. Traceability and Audit Requirements

**EDU-GOV-003 -- Decision Traceability.** Every credit decision must maintain a complete audit trail that includes:

1. **Application snapshot**: A frozen copy of all applicant-supplied data, credit bureau pulls, and derived analytics captured at the moment of decisioning.
2. **Rule execution log**: An ordered list of every rule evaluated, including rule ID, input values, threshold values, and pass/fail result.
3. **Policy version reference**: The exact version hash of the policy corpus used. If any policy document was amended between application receipt and decision rendering, the later version governs unless the applicant was already issued a conditional approval under the prior version.
4. **Decision-maker identification**: For automated decisions, the engine version and model identifier. For manual decisions, the name, title, and employee ID of the adjudicator.
5. **Exception documentation**: If any rule was overridden, the exception record must include the overriding authority's identity, the business justification narrative (minimum 50 words), the risk mitigation plan, and the approval level exercised per the Exception Authority Matrix (Section 4).

Audit trail records must be retained for a minimum of seven (7) years from the date of final loan disposition (payoff, charge-off, or sale) in a tamper-evident data store.

## 4. Exception Authority Matrix

**EDU-GOV-004 -- Exception Authority Levels.** Exceptions to any underwriting rule defined in POL-002 through POL-006 may be granted only by authorized personnel at the appropriate level. The exception authority matrix is structured in three tiers based on the incremental credit exposure introduced by the exception:

| Level | Authority | Maximum Incremental Exposure | Scope of Override |
|---|---|---|---|
| **Level 1** | Senior Credit Analyst | Up to $10,000 | Single-parameter deviations where the applicant is within 5% of the threshold (e.g., FICO 695 against a 700 cutoff). Limited to one exception per application. |
| **Level 2** | Credit Committee (minimum 3 members) | Up to $25,000 | Multi-parameter deviations or single-parameter deviations exceeding the Level 1 tolerance band. May approve up to two concurrent exceptions per application. Committee vote must be unanimous. |
| **Level 3** | Chief Credit Officer (CCO) | Unlimited | Any exception not coverable under Level 1 or Level 2, including policy waivers for pilot programs, strategic partnerships, or extraordinary circumstances. CCO decisions must be reported to the Board Risk Committee within 10 business days. |

### Exception Guardrails

- No exception may override a regulatory knockout (e.g., SCRA protections, ability-to-repay requirements, adverse action notice obligations).
- Aggregate exception volume must not exceed 5% of total decisions in any rolling 90-day window. If the 5% threshold is breached, the Credit Policy Office must initiate a policy review within 15 business days to determine whether the underlying rule requires recalibration.
- All exceptions are subject to post-decision quality assurance sampling at a rate of no less than 20%.

## 5. Policy Maintenance

The Credit Policy Office is responsible for reviewing this master policy and all subordinate documents at least annually, or within 30 days of any material change in regulatory requirements, portfolio performance, or market conditions. Amendments require sign-off from the CCO and notification to the Board Risk Committee. Version history must be maintained in the policy management system with full diff records.

## 6. Effective Date

This policy is effective as of January 1, 2026, and supersedes all prior credit policy governance documents.
