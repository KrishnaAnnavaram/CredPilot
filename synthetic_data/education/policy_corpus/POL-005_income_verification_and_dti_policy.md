---
policy_id: POL-005
title: Income Verification and DTI Policy
version: 1.0
effective_date: 2026-01-01
product_scope: [UG, GR, SP, INTL, REFI]
source_category: SYNTHETIC_INTERNAL_POLICY
synthetic: true
issuer: Edgemont Education Lending (fictional)
owner: Credit Policy Office
rule_ids: [EDU-INC-001, EDU-INC-002, EDU-INC-003, EDU-INC-004, EDU-INC-005, EDU-INC-006, EDU-INC-007]
---

# POL-005 -- Income Verification and DTI Policy

## 1. Purpose

This document defines accepted methods for verifying borrower and cosigner income, the formula for calculating debt-to-income (DTI) ratios, product-specific DTI ceilings, residual income requirements, and special provisions for self-employed and projected-income applicants. Income and DTI analysis are critical components of Edgemont Education Lending's ability-to-repay assessment.

---

## 2. Accepted Verification Methods

**EDU-INC-001 -- Income Documentation Standards.**

The following documentation methods are accepted for verifying gross income. At least one primary document is required; supplementary documents may be requested at the underwriter's discretion.

| Method | Code | Requirements | Applicability |
|---|---|---|---|
| Paystub | PAYSTUB | Most recent paystub dated within **30 days** of application. Must show employer name, pay period, gross earnings (YTD and current period), and deductions. | All products, W2 employees |
| W-2 | W2 | Most recent tax year W-2. If the application is submitted between January 1 and March 31, the prior-prior year W-2 is also acceptable pending current-year issuance. | All products, W2 employees |
| Tax return | TAX_RETURN | Most recent **2 years** of federal tax returns (Form 1040 with all schedules). Required for self-employed borrowers. IRS Form 4506-C transcript request must be executed for verification. | Self-employed applicants; all products |
| Bank statement | BANK_STATEMENT | Most recent **90 days** (3 consecutive months) of bank statements from the primary deposit account. Used to corroborate income when paystubs or W-2s show irregular patterns. | Supplementary for all products; primary for gig/freelance workers with TAX_RETURN |
| Verification of Employment | VOE | Direct verification from the employer via phone, email, or third-party verification service (e.g., The Work Number). Must confirm title, start date, employment status, and base compensation. | All products; mandatory for REFI if PAYSTUB is older than 30 days |

If documentation is inconsistent (e.g., paystub income differs from W-2 by more than 15%), the lower figure is used unless the borrower provides a written explanation with supporting evidence (promotion letter, commission structure documentation).

---

## 3. DTI Calculation

**EDU-INC-002 -- Debt-to-Income Ratio Formula.**

The debt-to-income ratio is calculated as follows:

> **DTI = Monthly Debt Service / (Gross Annual Income / 12)**

**Monthly Debt Service** includes:
- Proposed Edgemont loan payment (fully amortizing P&I at the quoted rate and term)
- All installment loan payments reported on the credit bureau (auto loans, personal loans, existing student loans)
- Minimum monthly payments on revolving credit (credit cards, HELOCs)
- Mortgage or rent payment (if mortgage, use PITIA; if rent, use stated rent verified against lease or bank statements)
- Child support and alimony obligations (if court-ordered)
- Any other recurring obligations disclosed by the applicant

**Excluded from Monthly Debt Service**: utility bills, insurance premiums not escrowed into mortgage, cell phone bills, subscriptions, and non-recourse deferred student loans currently in an approved income-driven repayment plan showing a $0 payment (these are included at $0 per bureau reporting).

**Gross Annual Income** is the verified pre-tax income from all sources, including base salary, regular overtime (averaged over 12 months), commissions (averaged over 24 months with documentation), bonuses (averaged over 24 months), rental income (net of expenses per Schedule E), and investment income (dividends and interest, averaged over 24 months).

---

## 4. Product-Specific DTI Ceilings

**EDU-INC-003 -- Maximum DTI by Product.**

| Product | Maximum DTI | Breach Action |
|---|---|---|
| UG | 45% | REFER if cosigner DTI also exceeds ceiling; otherwise cosigner DTI governs |
| GR | 43% | REFER for manual review |
| SP | 45% | REFER for manual review; projected-income DTI evaluated separately |
| INTL | 40% | REFER for manual review |
| REFI | 45% | DECLINE if residual income also fails; REFER if residual income passes |

These ceilings apply to the DTI calculated at the time of decisioning. If a borrower's DTI exceeds the ceiling by no more than 2 percentage points, the application may be approved under Level 1 exception authority (POL-001, EDU-GOV-004) if compensating factors are present (e.g., substantial liquid reserves, high FICO, stable employment tenure exceeding 5 years).

---

## 5. Residual Income Requirement

**EDU-INC-004 -- Post-Obligation Residual Income.**

Residual income is calculated as:

> **Residual Income = (Gross Annual Income / 12) - Monthly Debt Service**

The minimum residual income threshold is **$800 per month**.

| Product | Residual Income Below $800 Action |
|---|---|
| UG | REFER for manual review |
| GR | REFER for manual review |
| SP | REFER for manual review |
| INTL | REFER for manual review |
| REFI | **DECLINE** (hard fail; no exception pathway) |

For REFI, the $800 residual income floor is a hard knockout. The rationale is that refinance borrowers are post-graduation and fully employed; insufficient residual income indicates an unacceptable ability-to-repay risk. For in-school products (UG, GR, SP, INTL), the REFER disposition acknowledges that the borrower's income is expected to increase upon graduation.

---

## 6. Self-Employment Income Rules

**EDU-INC-005 -- Self-Employed Borrower Income Calculation.**

Self-employed borrowers (defined as individuals who own 25% or more of a business or who file Schedule C, Schedule K-1, or Form 1120-S) must provide 2 years of federal tax returns. Income is calculated as follows:

1. Extract net self-employment income from Schedule C (sole proprietor), Schedule K-1 (partnership/S-corp), or Form 1120-S for each of the two most recent tax years.
2. Add back documented non-cash deductions (depreciation, amortization) if the underlying assets are not being liquidated.
3. Calculate the **2-year average** of adjusted net self-employment income.
4. If income has **declined by more than 20%** from Year 1 to Year 2, use the **lower year** (Year 2) as the qualifying income rather than the average. This rule protects against using a blended figure that overstates the borrower's current earning capacity.

**EDU-INC-006 -- Employment Tenure Minimums.**

| Employment Type | Minimum Tenure |
|---|---|
| W-2 employee | 6 months with current employer (start date verified via VOE or paystub) |
| Self-employed | 24 months of continuous self-employment, verified by 2 years of tax returns showing Schedule C or K-1 income |

Borrowers who have been with their current W-2 employer for fewer than 6 months but have at least 24 months of continuous employment history in the same field (verified via resume and prior VOE) may be approved under Level 1 exception authority.

---

## 7. Projected Income Underwriting (SP Only)

**EDU-INC-007 -- Projected Income for Specialty Professional Loans.**

The Specialty Professional (SP) product permits underwriting based on projected post-graduation income when the borrower is currently enrolled and does not yet have full-time professional employment. This provision recognizes the high earning potential and strong employment outcomes of medical, dental, and law graduates.

**Eligible projected income sources:**

1. **Signed offer letter**: A bona fide employment offer letter specifying base salary, employer name, and anticipated start date. The start date must be within 12 months of the expected graduation date.
2. **Program median income**: The median starting salary for graduates of the borrower's specific program as reported by the institution's career services office or, if unavailable, the Bureau of Labor Statistics (BLS) Occupational Employment Statistics for the relevant SOC code. The figure used must be no more than 24 months old.

**Debt-to-projected-income ratio**: The total outstanding education debt (all lenders, including the proposed Edgemont loan) divided by the projected annual income must not exceed **2.0**. This is evaluated as a supplemental metric alongside the standard DTI calculation. If the borrower has current income, both the standard DTI and the debt-to-projected-income ratio must be within limits.

Projected income is available only for the SP product. UG, GR, INTL, and REFI applicants must use actual verified income.
