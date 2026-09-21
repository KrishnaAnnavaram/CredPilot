---
policy_id: POL-008
title: Fraud, Identity Verification, and Anti-Money Laundering Policy
lender: Edgemont Education Lending
products: [UG, GR, SP, INTL, REFI]
version: "2.0"
effective_date: 2025-01-15
last_reviewed: 2025-06-30
owner: Chief Compliance Officer
classification: Internal – Confidential
rule_ids:
  - EDU-FRD-001
  - EDU-FRD-002
  - EDU-FRD-003
  - EDU-FRD-004
  - EDU-FRD-005
  - EDU-FRD-006
  - EDU-FRD-007
  - EDU-FRD-008
---

# POL-008: Fraud, Identity Verification, and Anti-Money Laundering Policy

## 1. Purpose

This policy defines the fraud prevention, identity verification (KYC/CIP), sanctions screening, and anti-money laundering (AML) controls that Edgemont Education Lending applies to all private education loan products (UG, GR, SP, INTL, REFI). These controls are designed to comply with the USA PATRIOT Act, the Bank Secrecy Act (BSA), OFAC regulations, and applicable state requirements while protecting the institution from financial crime and reputational harm.

## 2. KYC and Customer Identification Program (CIP)

**EDU-FRD-001 — Identity Verification Requirements**

Every applicant (borrower and cosigner, if applicable) must satisfy the following Customer Identification Program requirements before a credit decision may be rendered:

1. **Valid government-issued photo identification** — acceptable forms include a U.S. driver's license, state-issued ID card, U.S. passport, U.S. military ID, or for INTL applicants a valid foreign passport. The document must be unexpired at the time of application.
2. **SSN or ITIN verification** — the applicant's Social Security Number or Individual Taxpayer Identification Number must be verified against authoritative sources (e.g., SSA records, credit bureau header data). A mismatch or inability to verify results in a REFER_MANUAL disposition for further investigation.
3. **Date of birth and legal name** — must match across the photo ID, credit report header, and application data.
4. **Physical or mailing address** — at least one verifiable address must be on file. For INTL borrowers, the U.S. school address is acceptable during enrollment.

Failure to satisfy CIP requirements results in application suspension until documentation deficiencies are resolved, with a maximum cure period of 30 calendar days before automatic withdrawal.

## 3. OFAC and Sanctions Screening

**EDU-FRD-002 — Mandatory OFAC Screening**

All applicants, cosigners, and related parties must be screened against the Office of Foreign Assets Control Specially Designated Nationals (SDN) list, the Sectoral Sanctions Identifications (SSI) list, and all other OFAC-administered sanctions programs at the following points:

- At application submission.
- At loan disbursement.
- At any borrower name or address change post-origination.

Any confirmed OFAC match results in an **immediate DECLINE**. This determination is final and **no exception may be granted** at any authority level (see POL-007, EDU-EXC-005). Potential matches that are not confirmed (e.g., common name hits) must be escalated to the BSA/AML Officer for resolution within two business days.

## 4. Device and Session Risk

**EDU-FRD-003 — Device Risk Assessment**

All digital applications are evaluated using a device fingerprinting and risk-scoring service. The device risk score ranges from 0 (low risk) to 100 (high risk).

- Device risk score **<= 80**: application proceeds through standard decisioning.
- Device risk score **> 80**: application is flagged for **mandatory manual review** by the Fraud Operations team before a credit decision may be issued. Reviewers must document the disposition rationale.

Indicators contributing to elevated device risk include use of VPN or proxy services, virtual machines, device spoofing, rooted or jailbroken devices, and geographic anomalies relative to the applicant's stated location.

## 5. Synthetic Identity Detection

**EDU-FRD-004 — Synthetic Identity Score Threshold**

Edgemont Education Lending employs a synthetic identity detection model that assigns a score from 0 to 100, where higher scores indicate greater probability of a fabricated or manipulated identity.

- Synthetic identity score **<= 70**: application proceeds normally.
- Synthetic identity score **> 70**: application disposition is set to **REFER_MANUAL**. The Fraud Operations team must conduct enhanced due diligence, which may include requesting additional documentation, performing out-of-band verification (e.g., phone call to employer or school), or requesting an in-person identity confirmation.

## 6. Enrollment Fraud

**EDU-FRD-005 — Enrollment Verification and Fraud**

Enrollment status is verified via the National Student Clearinghouse or direct school certification. Confirmed enrollment fraud — including but not limited to fabricated acceptance letters, falsified enrollment certifications, or misrepresentation of attendance status — results in:

- Immediate **DECLINE** of the application.
- Referral to the Fraud Investigation Unit for further review and potential filing of a Suspicious Activity Report (SAR).
- The applicant is flagged in the internal fraud database to prevent future applications.

This is a non-overridable condition (see POL-007, EDU-EXC-005).

## 7. Address Verification

**EDU-FRD-006 — Address Mismatch Handling**

When the applicant's stated address does not match the address(es) on file with credit bureaus or other verification sources, the application receives a **REVIEW flag**. Address mismatch alone does **not** result in automatic decline. The underwriter or fraud analyst must evaluate the discrepancy considering common explanations such as recent relocation, campus housing, or use of a family address. The resolution must be documented in the loan file.

## 8. Application Velocity Controls

**EDU-FRD-007 — Velocity Limits**

To detect application stacking and potential fraud rings, the following velocity thresholds are monitored:

- More than **3 applications** originating from the **same device fingerprint** within a rolling **30-day period** trigger a mandatory fraud review.
- More than **3 applications** originating from the **same IP address** within a rolling **30-day period** trigger a mandatory fraud review.
- More than **2 applications** submitted under the **same SSN/ITIN** within a rolling **90-day period** trigger a mandatory fraud review (excluding status inquiries or amendments to an existing application).

Applications flagged for velocity violations are held in PEND status until the Fraud Operations team clears them or recommends DECLINE.

## 9. Anti-Money Laundering and Suspicious Activity

**EDU-FRD-008 — AML Monitoring and Reporting**

Edgemont Education Lending complies with all BSA/AML requirements:

1. **Currency Transaction Reports (CTRs)** — any cash transaction or series of related cash transactions totaling **$10,000 or more** in a single business day must be reported via CTR to FinCEN. While education loans are predominantly non-cash, any cash equivalents (e.g., money orders, cashier's checks) presented for payoff or prepayment are subject to this threshold.
2. **Suspicious Activity Reports (SARs)** — any transaction or pattern of transactions that the institution knows, suspects, or has reason to suspect involves funds derived from illegal activity, is designed to evade BSA reporting requirements, or lacks a lawful purpose must be reported via SAR to FinCEN. Filing must occur within 30 calendar days of the initial detection of facts triggering the suspicion.
3. Suspicious patterns include but are not limited to: rapid payoff followed by new application, structuring of payments to avoid reporting thresholds, use of multiple identities linked to common contact information, and loan proceeds redirected to third parties unrelated to educational expenses.

The BSA/AML Officer is responsible for program oversight, staff training, independent testing, and regulatory examination coordination.

## 10. Effective Date

This policy is effective as of the date in the frontmatter and is reviewed at least annually or upon regulatory change.
