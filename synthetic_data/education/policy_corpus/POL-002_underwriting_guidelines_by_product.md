---
policy_id: POL-002
title: Underwriting Guidelines by Product
version: 1.0
effective_date: 2026-01-01
product_scope: [UG, GR, SP, INTL, REFI]
source_category: SYNTHETIC_INTERNAL_POLICY
synthetic: true
issuer: Edgemont Education Lending (fictional)
owner: Credit Policy Office
rule_ids: [EDU-UW-001, EDU-UW-002, EDU-UW-003, EDU-UW-004, EDU-UW-005]
---

# POL-002 -- Underwriting Guidelines by Product

## 1. Overview

This document defines product-specific underwriting parameters for all five Edgemont Education Lending loan programs. Each rule below supplements the master governance framework in POL-001 and must be applied in conjunction with the risk grading matrix (POL-003), cosigner policy (POL-004), income verification requirements (POL-005), and school eligibility criteria (POL-006).

---

## 2. Undergraduate Loans (UG)

**EDU-UW-001 -- Undergraduate Underwriting Criteria.**

| Parameter | Requirement |
|---|---|
| Minimum borrower age | 17 years at application (if under 18, cosigner is mandatory regardless of credit profile) |
| Credit score source | FICO 8 or FICO 9 from Equifax or TransUnion |
| Cosigner requirement | Required if borrower FICO < 700 or borrower has a THIN file (fewer than 3 tradelines or fewer than 24 months of credit history) or NO_FILE (no bureau record). Approximately 95% of UG borrowers require a cosigner. |
| Minimum loan amount | $1,000 per academic year |
| Maximum loan amount | $75,000 per academic year (aggregate lifetime cap: $200,000) |
| Enrollment status | At least half-time at an approved Title IV institution (see POL-006) |
| School certification | Required prior to disbursement; school must confirm enrollment status, cost of attendance, and other financial aid received |
| Disbursement | Funds disbursed directly to the school; any credit balance refunded to the borrower per school policy |
| Federal loan priority | Borrower must certify that federal loan options (Direct Subsidized/Unsubsidized) have been exhausted or considered before private loan origination |

When a cosigner is present, the decisioning engine evaluates the stronger of the borrower or cosigner credit profile for grading purposes, but both profiles must clear knockout checks (no active bankruptcy, no OFAC match).

---

## 3. Graduate Loans (GR)

**EDU-UW-002 -- Graduate Underwriting Criteria.**

| Parameter | Requirement |
|---|---|
| Borrower eligibility | Must be enrolled at least half-time in a graduate or professional degree program at an approved Title IV institution |
| Solo borrower FICO minimum | 660 |
| No-cosigner eligibility | FICO >= 700 AND DTI <= 40%. If either condition is not met, a cosigner is required. |
| Minimum loan amount | $5,000 per academic year |
| Maximum loan amount | $100,000 per academic year (aggregate lifetime cap: $350,000 including UG balances with Edgemont) |
| Federal cap awareness | Federal Direct Unsubsidized cap for graduate students is $20,500 per academic year. Edgemont's private loan may cover the gap between the federal cap and the certified cost of attendance minus other aid. |
| Employment / income | Not required for currently enrolled students. If the borrower is employed, income documentation strengthens the application but is not mandatory for GR applicants with FICO >= 720. |
| Residency | US citizen, permanent resident, or DACA recipient with valid SSN. Non-resident aliens must apply under the INTL product. |

Graduate borrowers who held a prior UG loan with Edgemont and maintained a perfect payment history receive a 0.25% loyalty rate discount, applied after risk-grade pricing (see POL-003).

---

## 4. Specialty / Professional Loans (SP)

**EDU-UW-003 -- Specialty Professional Underwriting Criteria.**

| Parameter | Requirement |
|---|---|
| Eligible programs | Medical (MD/DO), Dental (DDS/DMD), Law (JD), and other professional doctorate programs approved by the Credit Committee on a case-by-case basis |
| Minimum loan amount | $10,000 per academic year |
| Maximum loan amount | $150,000 per academic year (aggregate lifetime cap: $500,000) |
| Federal cap awareness | Federal Direct Unsubsidized cap for health profession students can reach $50,000 per academic year (including Graduate PLUS availability). Edgemont's SP product covers costs above federal aid. |
| Projected income underwriting | Permitted under EDU-INC-007 (see POL-005). The decisioning engine may use projected post-graduation income derived from a signed offer letter or the program-specific median starting salary published by the institution or BLS data. Debt-to-projected-income ratio must not exceed 2.0. |
| Credit score minimum | 640 solo; cosigner may cure scores down to 580, below which the application is declined |
| DTI ceiling | 45% (current obligations; projected income DTI evaluated separately) |
| Deferment | In-school deferment plus 6-month grace period standard; residency/fellowship deferment available for up to 48 months for medical/dental graduates |

SP applicants in their final year of study who have secured a signed employment offer letter receive streamlined processing with a 24-hour decision SLA.

---

## 5. International Student Loans (INTL)

**EDU-UW-004 -- International Student Underwriting Criteria.**

| Parameter | Requirement |
|---|---|
| Visa eligibility | F-1 or J-1 visa holders currently enrolled or admitted to an approved US institution |
| Minimum loan amount | $5,000 per academic year |
| Maximum loan amount | $80,000 per academic year (aggregate lifetime cap: $250,000) |
| No-cosigner pathway | Available only for borrowers attending a Tier A or Tier B school (see POL-006) AND who have secured Optional Practical Training (OPT) authorization or equivalent AND can demonstrate at least 12 months of post-study work authorization remaining at the time of final disbursement |
| Cosigner requirement (standard) | US citizen or permanent resident cosigner required unless the no-cosigner pathway criteria above are fully satisfied |
| Enrollment status | Full-time enrollment required (half-time not permitted for INTL) |
| School certification | Required; school must additionally confirm valid immigration status and SEVIS compliance |
| Currency / disbursement | All loans denominated in USD and disbursed to the school. No direct-to-borrower disbursement for INTL. |
| Repayment start | Immediate interest-only payments required during enrollment; full P&I repayment begins 6 months after graduation or loss of student status |

INTL applicants from countries under OFAC sanctions are ineligible. Country-of-origin risk adjustments may apply per the internal Country Risk Register, maintained quarterly by the Risk Analytics team.

---

## 6. Refinance Loans (REFI)

**EDU-UW-005 -- Refinance Underwriting Criteria.**

| Parameter | Requirement |
|---|---|
| Borrower status | Must have completed a degree (associate's or higher) from an accredited institution |
| Eligible debts | Federal student loans, private student loans, or a combination. Parent PLUS loans eligible if borrower is the parent. |
| Minimum loan amount | $5,000 |
| Maximum loan amount | $300,000 |
| Minimum FICO | 640 (no cosigner pathway available for REFI) |
| Active default | Any borrower with an active default status on any tradeline is ineligible (knockout). Rehabilitated defaults with 12 months of clean payment history may be considered under Level 2 exception authority (see POL-001, EDU-GOV-004). |
| DTI ceiling | 45% post-refinance |
| Employment | Must be currently employed or have a signed offer letter with a start date within 90 days. Self-employed borrowers must meet the 24-month tenure requirement per POL-005. |
| Income verification | Mandatory for all REFI applicants (no income-waiver pathway). See POL-005 for accepted documentation. |
| Residual income | Minimum $800/month post-obligation residual income required. This is a hard fail for REFI; applications below this threshold are declined, not referred. |

REFI applicants consolidating federal loans must acknowledge the loss of federal protections (income-driven repayment, PSLF eligibility, federal forbearance/deferment) via a signed Federal Benefit Waiver Disclosure prior to closing.

---

## 7. Cross-Product Rules

The following rules apply across all products:

- **OFAC and sanctions screening**: Knockout for all products. No exceptions permitted.
- **Bankruptcy**: Active Chapter 7 or Chapter 13 bankruptcy is a knockout. Discharged bankruptcy must be at least 24 months old with re-established credit.
- **Fraud flags**: Any identity verification failure or fraud alert triggers an automatic REFER for manual review.
- **Stacking controls**: A borrower may hold concurrent loans across products but total Edgemont exposure must not exceed the applicable aggregate lifetime cap for the highest-limit product held.
