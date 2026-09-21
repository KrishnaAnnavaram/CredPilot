---
policy_id: POL-006
title: School Eligibility and Approved List
version: 1.0
effective_date: 2026-01-01
product_scope: [UG, GR, SP, INTL, REFI]
source_category: SYNTHETIC_INTERNAL_POLICY
synthetic: true
issuer: Edgemont Education Lending (fictional)
owner: Credit Policy Office
rule_ids: [EDU-SCH-001, EDU-SCH-002, EDU-SCH-003, EDU-SCH-004, EDU-SCH-005, EDU-SCH-006, EDU-SCH-007]
---

# POL-006 -- School Eligibility and Approved List

## 1. Purpose

This document establishes the criteria for school eligibility, the tiering methodology, ongoing monitoring and suspension triggers, and enrollment requirements for all Edgemont Education Lending products. School eligibility is a front-gate control: an application associated with a school not on the approved list is knocked out at intake before any credit evaluation is performed.

---

## 2. Approved List Requirement

**EDU-SCH-001 -- Approved School List as Intake Knockout.**

Every non-REFI application must identify a school that appears on Edgemont's Approved School List. If the school is not on the list, the application is rejected at intake with a status of INELIGIBLE_SCHOOL. This is not a credit decision and does not trigger adverse action notice requirements. REFI applications are exempt from this requirement because the borrower has already completed their program; however, the degree-granting institution must have been accredited at the time of graduation.

The Approved School List is maintained by the Credit Policy Office and updated quarterly based on the tiering criteria defined below.

---

## 3. School Tiering Criteria

**EDU-SCH-002 -- Tier Definitions.**

Schools on the approved list are assigned to one of four tiers based on three performance metrics sourced from the U.S. Department of Education College Scorecard, IPEDS, and internal Edgemont portfolio data. All three criteria must be met for a tier; if any metric falls into a lower tier, the school is assigned to the lowest qualifying tier.

| Tier | Cohort Default Rate (CDR) | Completion Rate | Median Post-Graduation Earnings |
|---|---|---|---|
| **Tier A** | <= 5% | >= 80% | >= $55,000 |
| **Tier B** | <= 10% | >= 65% | >= $40,000 |
| **Tier C** | <= 15% | >= 50% | >= $30,000 |
| **Tier D** | > 15% OR completion < 50% | < 50% possible | < $30,000 possible |

**Tier A** schools represent the lowest lending risk and qualify for the most favorable pricing (no school tier adjustment per POL-003) and the broadest product access, including the INTL no-cosigner pathway.

**Tier B** schools also receive no pricing adjustment and qualify for the INTL no-cosigner pathway, but are subject to annual enhanced monitoring reviews.

**Tier C** schools incur a +0.50% rate adjustment (POL-003, EDU-RG-002) and are excluded from the INTL no-cosigner pathway. Maximum loan amounts for Tier C schools are capped at 90% of the standard product maximum.

**Tier D** schools are classified as restricted. Lending to Tier D schools requires Credit Committee approval (Level 2 exception authority per POL-001) on a case-by-case basis. A +1.00% rate adjustment applies. Maximum loan amounts are capped at 75% of the standard product maximum. New INTL originations are not permitted at Tier D schools.

---

## 4. Title IV Requirement

**EDU-SCH-003 -- Title IV Participation for UG and GR.**

For the Undergraduate (UG) and Graduate (GR) products, the school must be a current participant in the Federal Title IV student aid program. Schools that have lost Title IV eligibility or have been placed on heightened cash monitoring (HCM2) by the Department of Education are automatically moved to Tier D or suspended, depending on the severity of the action.

SP loans also require Title IV participation unless the program is at a non-Title IV institution approved by a recognized programmatic accreditor (e.g., ABA for law, LCME for medicine). Such exceptions must be individually approved by the Credit Committee.

INTL and REFI products do not require Title IV participation, but the institution must hold recognized accreditation (regional or national accreditor recognized by the Department of Education, or an equivalent foreign accrediting body for international campuses).

---

## 5. Suspension Triggers

**EDU-SCH-004 -- Automatic Suspension Criteria.**

A school is automatically suspended from the Approved School List -- meaning no new applications are accepted -- if any of the following conditions are met:

1. **Cohort Default Rate exceeds 25%** in the most recently published 3-year CDR data from the Department of Education.
2. **Loss of accreditation** from the institution's primary accrediting body, whether voluntary withdrawal or involuntary revocation.
3. **Closure announcement**: The school announces a teach-out plan or cessation of operations.
4. **Federal enforcement action**: The school is subject to a limitation, suspension, or termination (LS&T) action by the Department of Education.

Suspension is effective immediately upon identification of the triggering event. Existing loans at suspended schools continue to be serviced per their original terms, but no new disbursements are made for applications in the pipeline unless the disbursement was approved before the suspension date.

Reinstatement from suspension requires a formal review by the Credit Committee demonstrating that the triggering condition has been resolved for at least 12 consecutive months.

---

## 6. School Certification Requirement

**EDU-SCH-005 -- School Certification for Non-REFI Products.**

For all non-REFI products (UG, GR, SP, INTL), the school must provide a signed school certification before loan proceeds are disbursed. The certification must confirm:

- The borrower's enrollment status (full-time or half-time as applicable)
- The certified cost of attendance for the relevant academic period
- Other financial aid the borrower is receiving (grants, scholarships, federal loans)
- The gap between cost of attendance and other aid (the maximum certifiable private loan amount)
- The borrower's expected graduation date

Edgemont will not disburse funds exceeding the certified gap amount. If the requested loan amount exceeds the gap, the loan amount is reduced to the certified gap. The borrower is notified of any reduction.

---

## 7. Enrollment Status Requirements

**EDU-SCH-006 -- Minimum Enrollment Status by Product.**

| Product | Minimum Enrollment Status |
|---|---|
| UG | Half-time (as defined by the institution, typically 6+ credit hours per semester) |
| GR | Half-time |
| SP | Half-time |
| INTL | **Full-time** (required by F-1/J-1 visa regulations; half-time is not permitted) |
| REFI | Not applicable (borrower has completed program) |

Enrollment status is verified through the school certification at origination and monitored via the National Student Clearinghouse during the life of the loan. If a borrower drops below the minimum enrollment status, the in-school deferment period ends and the grace period begins (typically 6 months before repayment commences).

---

## 8. International Schools

**EDU-SCH-007 -- International School Eligibility.**

Edgemont may lend to borrowers attending international schools (schools located outside the United States) under the following conditions:

1. The school must have an **articulation agreement** with a US-accredited institution, meaning credits earned are transferable and the degree is recognized by US employers and graduate programs.
2. The school must appear on the Approved School List with a designated tier. International schools are tiered using the same metrics where data is available; where CDR or Scorecard data is unavailable, the Credit Committee assigns a tier based on the partnering US institution's tier and independent outcome data.
3. Only the UG and GR products are available for international school attendance. SP, INTL, and REFI are not available for international campus enrollment.
4. Disbursement for international schools is made to the US partner institution, which coordinates fund transfer to the international campus. Direct disbursement to foreign institutions is not permitted.
5. Maximum loan amounts for international schools are capped at 80% of the applicable product maximum, regardless of school tier.

The Credit Policy Office maintains a separate International School Supplement to the Approved School List, reviewed semi-annually.
