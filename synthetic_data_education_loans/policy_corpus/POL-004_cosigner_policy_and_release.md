---
policy_id: POL-004
title: Cosigner Policy and Release Criteria
version: 1.0
effective_date: 2026-01-01
product_scope: [UG, GR, SP, INTL, REFI]
source_category: SYNTHETIC_INTERNAL_POLICY
synthetic: true
issuer: Edgemont Education Lending (fictional)
owner: Credit Policy Office
rule_ids: [EDU-COS-001, EDU-COS-002, EDU-COS-003, EDU-COS-004, EDU-COS-005]
---

# POL-004 -- Cosigner Policy and Release Criteria

## 1. Purpose

This document defines the eligibility requirements for cosigners, the obligations imposed on cosigners, the regulatory disclosures required, and the criteria under which a cosigner may be released from liability. Cosigner requirements are a central component of Edgemont Education Lending's credit risk framework, particularly for the Undergraduate (UG) and International Student (INTL) products where the primary borrower frequently lacks sufficient credit history or income.

---

## 2. Cosigner Eligibility

**EDU-COS-001 -- Cosigner Qualification Requirements.**

A cosigner must satisfy all of the following criteria at the time of application:

| Criterion | Requirement |
|---|---|
| Citizenship / residency | Must be a US citizen (US_CITIZEN) or lawful permanent resident (PERM_RESIDENT). DACA recipients, visa holders, and non-resident aliens are not eligible to serve as cosigners. |
| Minimum age | 21 years old at the time of application |
| FICO score | Minimum 650 (FICO 8 or FICO 9 from Equifax or TransUnion) |
| Bankruptcy status | No active Chapter 7 or Chapter 13 filing. Discharged bankruptcy must be at least 24 months old with re-established credit (minimum 2 active tradelines in good standing). |
| OFAC / sanctions | Must clear OFAC and sanctions screening. A match is a knockout with no exception. |
| Relationship to borrower | No restriction. The cosigner need not be a relative of the borrower. Institutional or corporate cosigners are not permitted. |

If the cosigner fails any knockout criterion, the cosigner is rejected, and the borrower may substitute a different eligible cosigner or, if applicable, pursue a no-cosigner pathway under the relevant product rules in POL-002.

---

## 3. Cosigner DTI Ceiling

**EDU-COS-002 -- Cosigner Debt-to-Income Limit.**

The cosigner's debt-to-income ratio, calculated per the methodology in POL-005 (EDU-INC-002), must not exceed **50%** inclusive of the proposed loan obligation. This ceiling is higher than the borrower DTI ceilings (40%-45% depending on product) because the cosigner's obligation is contingent and typically layered on top of their existing debt structure.

If the cosigner's DTI exceeds 50% after including the proposed loan payment, the application outcome is REFER for manual review. The Credit Committee may approve exceptions up to 55% DTI under Level 2 authority (POL-001, EDU-GOV-004) if the cosigner demonstrates substantial liquid reserves (at least 12 months of combined loan payments in verified savings or investment accounts).

When both borrower and cosigner have verifiable income, the risk grade is assigned using the stronger FICO of the two, but DTI is evaluated independently for each party against their respective ceilings. Both must pass.

---

## 4. Regulatory Disclosure -- Reg Z Cosigner Notice

**EDU-COS-003 -- Cosigner Notice Requirement.**

In compliance with Regulation Z (12 CFR 1026.36), Edgemont must provide the cosigner with a clear and conspicuous written notice before the first disbursement of loan proceeds. The notice must include:

1. A statement that the cosigner is equally responsible for repayment of the full loan amount, including principal, interest, and any fees.
2. A description of the circumstances under which the lender may pursue collection against the cosigner, including default, delinquency, and acceleration.
3. Information about the cosigner release program, including the general criteria and the earliest point at which the cosigner may apply for release.
4. A statement that the cosigner's credit report will reflect the loan obligation and that delinquency or default by the primary borrower will negatively affect the cosigner's credit.

The cosigner must acknowledge receipt of this notice by signature (wet or electronic) prior to disbursement. Failure to obtain the signed acknowledgment is a compliance knockout; the loan may not be funded until the acknowledgment is on file.

---

## 5. Cosigner Release Program

**EDU-COS-004 -- Cosigner Release Eligibility Criteria.**

A cosigner may apply for release from liability after the primary borrower satisfies all of the following conditions:

| Criterion | Requirement |
|---|---|
| On-time payments | Minimum **24 consecutive** scheduled principal-and-interest payments made on time (within the 15-day grace period). Payments made during in-school deferment or grace periods do not count toward this requirement. |
| Borrower FICO | >= 680 at the time of the release evaluation (new credit pull required) |
| Borrower DTI | <= 43% at the time of the release evaluation, calculated using current verified income and all outstanding obligations |
| Delinquency history | No delinquency of 30 days or more on the subject loan or any other tradeline in the **12 months** preceding the release request |
| Loan status | Loan must be in active repayment status (not in deferment, forbearance, or modification) |

The release evaluation is performed by the servicing team using a standardized checklist. If all criteria are met, the cosigner is released within 30 business days, and both the borrower and the cosigner receive written confirmation. The cosigner's obligation is removed from their credit report within one reporting cycle.

If the borrower does not meet the release criteria, the request is denied with a written explanation identifying which criteria were not satisfied. The borrower may reapply after 6 months.

### Automatic Release Notification

Edgemont's servicing system automatically generates a notification to the borrower and cosigner when the 24th consecutive on-time payment is made, informing them that the borrower may now be eligible for cosigner release and inviting them to initiate the process. This notification does not guarantee approval; the remaining criteria (FICO, DTI, delinquency) must still be verified.

---

## 6. UG Cosigner Prevalence

**EDU-COS-005 -- UG Cosigner Requirement Expectation.**

Under the Undergraduate product, a cosigner is required whenever the borrower's FICO score is below 700 or the borrower's credit file is classified as NO_FILE (no bureau record found) or THIN (fewer than 3 tradelines or fewer than 24 months of credit history). Given the demographic profile of undergraduate borrowers (typically ages 17-22 with limited credit history), approximately **95%** of UG applications require a cosigner.

For product planning and capital allocation purposes, underwriting models must assume a 95% cosigner attachment rate for UG originations. Portfolio analytics should track actual cosigner attachment rates monthly and flag deviations greater than 3 percentage points from the expected rate for investigation.

The cosigner's credit profile is the primary driver of risk grading for most UG loans. When a cosigner is present, the higher FICO of the borrower and cosigner is used for grade assignment per POL-003, but in practice the cosigner's score is almost always the operative score for UG.

---

## 7. Death or Disability of Cosigner

In the event of the cosigner's death or total and permanent disability, the cosigner's obligation is discharged upon receipt of a certified death certificate or qualifying disability documentation. The loan continues under the primary borrower's sole obligation. The borrower's credit profile is re-evaluated within 60 days; if the borrower no longer meets standalone underwriting criteria, the loan is placed on enhanced monitoring but is not accelerated or called due solely because of cosigner discharge.
