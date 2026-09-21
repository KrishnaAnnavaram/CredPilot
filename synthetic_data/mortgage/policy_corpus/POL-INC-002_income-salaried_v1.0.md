---
policy_id: POL-INC-002
title: Salaried Income Qualification
version: 1.0
family: income-salaried
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
priority: 49
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - INC-SAL-001
  - INC-SAL-002
  - INC-SAL-003
  - INC-SAL-004
synthetic: true
---

# Salaried Income Qualification

**POL-INC-002 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how fixed annual salary is verified and converted into qualifying monthly income. Salary is the simplest income type and the one most applications rely on, which makes it the type where arithmetic errors are least likely to be noticed.

## 2. Scope

Applies to borrowers paid a fixed annual salary by an employer they do not own. Ownership of 25 percent or more of the employing business makes the borrower self-employed under POL-INC-005 regardless of how the pay is described.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### INC-SAL-001 — Conversion to monthly qualifying income

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Fixed annual salary converts to monthly income by dividing the annual amount by 12. Where pay is stated per period, the conversion uses the period multiplier: weekly pay multiplied by 52 and divided by 12; bi-weekly pay multiplied by 26 and divided by 12; semi-monthly pay multiplied by 24 and divided by 12. Treating bi-weekly pay as though it were semi-monthly understates annual income by roughly four percent, which is the single most common arithmetic error in this category.

| Parameter | Value |
| --- | --- |
| `annual_divisor` | 12 |
| `weekly_multiplier` | 52 |
| `biweekly_multiplier` | 26 |
| `semimonthly_multiplier` | 24 |
| `monthly_multiplier` | 12 |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Income model' - fixed salary is converted to monthly income; pay frequency is an explicit edge case.

### INC-SAL-002 — Required documentation

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Salaried income requires a paystub covering at least one full pay period within the freshness window, the most recent W-2, and an employment verification. Where a validated digital verification report covers employment and income, the paystub and W-2 requirement may be reduced - but a digital report never removes the obligation to resolve contradictory information it contains.

| Parameter | Value |
| --- | --- |
| `paystub_periods_required` | 1 |
| `w2_years_required` | 1 |
| `employment_verification_required` | yes |
| `digital_verification_reduces_documents` | yes |

**Acceptable evidence.** Paystub showing pay period, gross pay for the period and year-to-date gross; W-2 for the most recent year; Written or verbal employment verification.

**Condition raised when unsatisfied.** Provide a paystub dated within {freshness_days} days covering at least one full pay period.

**See also:** POL-DOC-001, POL-EMP-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Document catalog' - digital validation services can reduce document requirements without removing the obligation to address contradictory information.

### INC-SAL-003 — Year-to-date earnings must reconcile with the stated salary

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

Year-to-date gross on the most recent paystub, annualised over the elapsed pay periods, must reconcile with the stated annual salary within five percent. Where it does not, the difference is investigated before the income is used: the usual explanations are a mid-year raise, unpaid leave, a bonus included in year-to-date gross, or a paystub that does not belong to this borrower. The reconciliation is recorded whether or not it identifies a discrepancy.

| Parameter | Value |
| --- | --- |
| `tolerance` | 5% |
| `formula` | YTD gross / elapsed pay periods * periods per year |

**See also:** POL-INC-001, POL-FRD-001.

### INC-SAL-004 — A documented raise may be used before it appears on a paystub

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A salary increase effective within 60 days of the note date may be used at the increased rate where the employer documents the new rate and its effective date in writing. Until that evidence exists, the prior rate is used. An increase that has not yet taken effect and is not documented is not qualifying income, however confident the borrower is about it.

| Parameter | Value |
| --- | --- |
| `max_days_before_effective` | 60 |
| `documentation` | employer letter stating the new rate and effective date |

**Condition raised when unsatisfied.** Provide employer documentation of the salary increase and its effective date.

## 5. Documentation requirements

- Paystub, W-2 and employment verification as required by INC-SAL-002.
- The year-to-date reconciliation record required by INC-SAL-003.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-INC-001
- POL-EMP-001
- POL-DOC-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
