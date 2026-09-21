---
policy_id: POL-007
title: Exception and Override Policy
lender: Edgemont Education Lending
products: [UG, GR, SP, INTL, REFI]
version: "2.0"
effective_date: 2025-01-15
last_reviewed: 2025-06-30
owner: Chief Credit Officer
classification: Internal – Confidential
rule_ids:
  - EDU-EXC-001
  - EDU-EXC-002
  - EDU-EXC-003
  - EDU-EXC-004
  - EDU-EXC-005
---

# POL-007: Exception and Override Policy

## 1. Purpose

This policy establishes the authority framework, documentation requirements, and governance controls for granting exceptions to Edgemont Education Lending's standard underwriting and eligibility criteria across all private education loan products (UG, GR, SP, INTL, REFI). Exceptions are deviations from published policy thresholds that are individually justified and approved by an authorized party. This policy exists to ensure that exception activity is transparent, controlled, auditable, and does not introduce undue risk to the portfolio.

## 2. Scope

This policy applies to every application where any single underwriting parameter falls outside the boundaries defined in POL-001 through POL-006, including but not limited to credit score floors, DTI ceilings, loan amount maximums, income requirements, and cosigner eligibility criteria.

## 3. Exception Documentation Requirements

**EDU-EXC-001 — Documentation Standard**

Every exception, regardless of tier, must be recorded in the loan origination system with the following fields before the loan may proceed to the next decisioning stage:

1. **Justification narrative** — a plain-language explanation of why the exception is warranted, referencing specific borrower circumstances.
2. **Compensating factors** — at least one measurable compensating factor must be cited (e.g., high residual income, substantial savings, strong employment history, low aggregate debt, cosigner with FICO >= 750).
3. **Approving authority** — the name, title, and approval tier of the individual or body granting the exception.
4. **Parameter(s) exceeded** — the specific rule ID(s) being overridden and the magnitude of deviation.
5. **Conditions imposed** — any additional conditions or mitigants required as part of the exception approval (e.g., reduced loan amount, additional documentation, enhanced monitoring).

Incomplete exception records shall cause the loan to be placed in PEND status until remediated.

## 4. Exception Authority Tiers

**EDU-EXC-002 — Level 1 Authority (Senior Underwriter)**

A Senior Underwriter may approve exceptions subject to ALL of the following constraints:

- DTI may exceed the product maximum by up to **2 percentage points** (e.g., if the UG ceiling is 43%, Level 1 may approve up to 45%).
- Loan amount may exceed the certified or program maximum by up to **$10,000**.
- Only a **single non-credit exception** may be granted per application (e.g., one documentation deficiency or one employment tenure shortfall — not both).
- The borrower's (or cosigner's) FICO score must still meet or exceed the published product minimum.
- Level 1 authority may not be used to override credit-score floors, enrollment verification failures, or any item listed in Section 5.

**EDU-EXC-003 — Level 2 Authority (Credit Committee)**

The Credit Committee (minimum three voting members, quorum required) may approve exceptions subject to ALL of the following constraints:

- DTI may exceed the product maximum by up to **5 percentage points**.
- Loan amount may exceed the certified or program maximum by up to **$25,000**.
- FICO score may be reduced to a floor of **600**, provided at least two compensating factors are documented.
- **Multiple exceptions** may be granted on the same application, provided each is individually justified.
- The Credit Committee must convene and vote; email or asynchronous polling is not permitted for Level 2 exceptions.
- All Level 2 decisions must be documented in committee minutes within two business days.

**EDU-EXC-004 — Level 3 Authority (Chief Credit Officer)**

The Chief Credit Officer (CCO) holds **unlimited exception authority** and may approve deviations beyond Level 2 thresholds. Level 3 exceptions are subject to the following governance requirements:

- The CCO must provide a written memorandum for each Level 3 exception.
- All Level 3 exceptions are reported to the Board Risk Committee quarterly.
- Level 3 exceptions on any single application exceeding $100,000 in aggregate deviation require concurrent notification to the Chief Risk Officer.

## 5. Non-Overridable Conditions

**EDU-EXC-005 — Absolute Prohibitions**

No exception, at any authority level, may be granted for the following conditions:

1. **OFAC hit** — any match on the Specially Designated Nationals (SDN) list or other OFAC-administered sanctions lists results in an immediate and final DECLINE (see POL-008, EDU-FRD-002).
2. **Enrollment fraud** — confirmed falsification of enrollment status, acceptance letters, or school certification documents results in DECLINE with referral to the fraud investigation unit.
3. **School suspension** — if the institution is suspended, terminated, or under heightened oversight by the Department of Education, no loans may be originated regardless of borrower qualifications.
4. **Regulatory prohibition** — any condition where origination would violate federal or state law, regulation, or a binding supervisory directive may not be overridden.

These prohibitions are absolute and are not subject to escalation.

## 6. Monitoring and Governance

The Credit Risk Analytics team shall calculate the **exception rate** — defined as the number of approved exceptions divided by total approved applications — on a quarterly basis, segmented by product and exception tier.

If the exception rate exceeds **10% of approved applications** in any calendar quarter for any product line, the following actions are triggered:

- Immediate notification to the CCO and Chief Risk Officer.
- A formal policy review must be initiated within 30 days to determine whether the underlying policy thresholds require recalibration.
- The review findings and any recommended changes must be presented to the Board Risk Committee.

## 7. Automated Systems Restriction

Automated decisioning engines, including any algorithmic or rules-based systems, **may not grant exceptions**. All exceptions require human review, judgment, and approval at the appropriate authority tier. Automated systems may flag applications as exception candidates and route them to the correct authority level, but the approval decision itself must be made by an authorized individual or committee.

## 8. Effective Date and Review Cycle

This policy is effective as of the date shown in the frontmatter and shall be reviewed at least annually or more frequently if triggered by the monitoring thresholds in Section 6.
