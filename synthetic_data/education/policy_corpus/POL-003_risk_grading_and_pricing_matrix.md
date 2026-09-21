---
policy_id: POL-003
title: Risk Grading and Pricing Matrix
version: 1.0
effective_date: 2026-01-01
product_scope: [UG, GR, SP, INTL, REFI]
source_category: SYNTHETIC_INTERNAL_POLICY
synthetic: true
issuer: Edgemont Education Lending (fictional)
owner: Credit Policy Office
rule_ids: [EDU-RG-001, EDU-RG-002, EDU-RG-003, EDU-RG-004]
---

# POL-003 -- Risk Grading and Pricing Matrix

## 1. Purpose

This document defines the risk grade assignment methodology and the corresponding fixed and variable interest rate pricing for all Edgemont Education Lending products. Risk grades drive pricing, reserve allocation, and portfolio monitoring thresholds. Every approved or conditionally approved application must be assigned exactly one risk grade before rate disclosure.

---

## 2. Risk Grade Assignment

**EDU-RG-001 -- Grade Band Definitions.**

Risk grades are determined by the intersection of the applicant's FICO score (or cosigner FICO, whichever is used for decisioning per POL-002) and the calculated debt-to-income ratio (DTI) as defined in POL-005. Both conditions in a band must be satisfied; if the FICO qualifies for one band but the DTI qualifies for a lower band, the lower (worse) band governs.

| Grade | FICO Minimum | DTI Maximum | Fixed Rate (Base) |
|---|---|---|---|
| A1 | 780 | 25% | 4.99% |
| A2 | 760 | 30% | 5.49% |
| A3 | 740 | 35% | 5.99% |
| B1 | 720 | 38% | 6.49% |
| B2 | 700 | 40% | 6.99% |
| B3 | 680 | 42% | 7.49% |
| C1 | 660 | 43% | 7.99% |
| C2 | 650 | 44% | 8.49% |
| C3 | 640 | 45% | 8.99% |
| D1 | 620 | 46% | 9.99% |
| D2 | 600 | 48% | 10.99% |
| D3 | 580 | 50% | 11.99% |
| E1 | 560 | -- | DECLINE |
| E2 | 540 | -- | DECLINE |
| E3 | < 540 | -- | DECLINE |

Applicants whose FICO falls in the D3 band (580-599) are eligible for approval only with a qualified cosigner whose profile grades at C3 or above. If no cosigner is provided, the application must be declined.

Applicants whose FICO falls in the E1, E2, or E3 bands (below 580) are automatically declined. No cosigner cure is available for E-band applicants. This is a hard knockout with no exception pathway.

---

## 3. School Tier Adjustments

**EDU-RG-002 -- School Tier Rate Adjustments.**

After the base fixed rate is determined from the grade band table, a school tier adjustment is applied for non-REFI products. School tiers are defined in POL-006. REFI loans are not subject to school tier adjustments because the borrower has already graduated.

| School Tier | Rate Adjustment |
|---|---|
| Tier A | +0.00% (no adjustment) |
| Tier B | +0.00% (no adjustment) |
| Tier C | +0.50% |
| Tier D | +1.00% |

Schools not on the approved list are ineligible for lending; therefore, no adjustment beyond Tier D exists. Tier D schools are restricted-access and require Credit Committee approval (Level 2 exception per POL-001) before origination.

Example: A borrower graded B2 (base rate 6.99%) attending a Tier C school receives a final fixed rate of 7.49%.

---

## 4. Variable Rate Calculation

**EDU-RG-003 -- Variable Rate Derivation.**

Edgemont offers both fixed and variable rate options on all products except REFI (fixed-only). The variable rate is derived from the fixed rate as follows:

> **Variable Rate = Fixed Rate - 1.50%**, subject to a floor of **3.99%**.

The variable rate is indexed to the 1-Month SOFR (Secured Overnight Financing Rate) plus a margin. The margin is set such that the initial variable rate equals the formula above at the time of origination. Rate adjustments occur monthly on the first business day, with a per-adjustment cap of 1.00% and a lifetime cap of the original fixed rate + 3.00%.

| Grade | Fixed Rate | Variable Rate (Initial) |
|---|---|---|
| A1 | 4.99% | 3.99% (floor applies) |
| A2 | 5.49% | 3.99% (floor applies) |
| A3 | 5.99% | 4.49% |
| B1 | 6.49% | 4.99% |
| B2 | 6.99% | 5.49% |
| B3 | 7.49% | 5.99% |
| C1 | 7.99% | 6.49% |
| C2 | 8.49% | 6.99% |
| C3 | 8.99% | 7.49% |
| D1 | 9.99% | 8.49% |
| D2 | 10.99% | 9.49% |
| D3 | 11.99% | 10.49% |

Variable rate loans include a rate-change notification sent to the borrower at least 25 days before each adjustment takes effect, in compliance with Regulation Z.

---

## 5. Repayment Term Options and Term-Based Adjustments

**EDU-RG-004 -- Available Repayment Terms.**

Borrowers may select from the following repayment terms. The base rates in the grade band table assume a 10-year term. Term adjustments are applied as follows:

| Term (Years) | Rate Adjustment | Availability |
|---|---|---|
| 5 | -0.50% | All products |
| 7 | -0.25% | All products |
| 10 | +0.00% (base) | All products |
| 15 | +0.25% | GR, SP, REFI only |
| 20 | +0.50% | SP, REFI only |

UG and INTL loans are limited to 5-, 7-, or 10-year terms. The 15- and 20-year terms are available only for higher-balance programs where extended amortization materially improves affordability.

Example: A GR borrower graded A3 (base 5.99%) selecting a 15-year term at a Tier B school pays 5.99% + 0.00% (school) + 0.25% (term) = 6.24% fixed.

---

## 6. Rate Lock and Expiration

Approved rates are locked for 45 days from the date of the credit decision. If the loan has not been disbursed within the lock period, the application must be re-priced using the then-current matrix. Rate locks are non-transferable between products or borrowers.

## 7. Autopay and Loyalty Discounts

A 0.25% autopay discount is available on all products when the borrower enrolls in automatic debit from a checking or savings account. This discount is applied after all other adjustments and is revocable upon autopay cancellation. The GR loyalty discount (0.25% for prior UG borrowers with perfect payment history, per POL-002) stacks with the autopay discount for a maximum combined discount of 0.50%.

## 8. Annual Review

The pricing matrix is reviewed quarterly by the Asset-Liability Committee (ALCO) and may be adjusted based on funding costs, competitive positioning, and portfolio credit performance. Rate changes apply prospectively to new originations only; existing loans retain their locked rate.
