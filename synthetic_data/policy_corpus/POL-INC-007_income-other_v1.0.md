---
policy_id: POL-INC-007
title: Other Qualifying Income
version: 1.0
family: income-other
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
  - INC-OTH-001
  - INC-OTH-002
  - INC-OTH-003
  - INC-OTH-004
  - INC-OTH-005
synthetic: true
---

# Other Qualifying Income

**POL-INC-007 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Covers retirement, pension, social-security and other benefit income, investment income, support payments and military allowances. These sources share one analytical question - will the amount continue - and one prohibition: the source itself is never a reason to discount the amount.

## 2. Scope

Applies to every income type not covered by POL-INC-002 through POL-INC-006.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### INC-OTH-001 — Retirement, pension and benefit income

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Retirement, pension, annuity, disability and social-security income qualify at the verified periodic amount where an award letter, benefit statement or account statement evidences the amount and, where applicable, its end date. Income with no stated end date is presumed to continue. Where the income is not subject to federal income tax and that status is documented, the gross-up in INC-GEN-005 applies.

| Parameter | Value |
| --- | --- |
| `evidence` | award letter, benefit statement or account statement |
| `no_end_date` | presumed continuing |

**Acceptable evidence.** Award letter or benefit statement; Recent deposit evidence.

**See also:** POL-INC-001.

### INC-OTH-002 — Benefit income is never discounted for its source

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Social-security, disability, public-assistance and retirement income are analysed on exactly the same basis as wage income: verified amount and likely continuance. Applying an additional haircut, a shorter continuance window or an extra documentation burden to these sources because of what they are is prohibited discrimination, not caution.

**See also:** POL-CRD-001, POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Income model' - a future AI must not penalise income simply because it comes from Social Security, retirement or another public-assistance source.

### INC-OTH-003 — Interest and dividend income

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Interest and dividend income qualify at the two-year average from tax returns, reduced proportionally for any of the generating assets that will be consumed to close the transaction. An asset cannot simultaneously fund the down payment and generate qualifying income; counting it twice is the characteristic error in this category.

| Parameter | Value |
| --- | --- |
| `averaging_years` | 2 |
| `reduce_for_consumed_assets` | yes |

**Acceptable evidence.** Tax returns; Account statements evidencing the holdings.

**See also:** POL-AST-001.

### INC-OTH-004 — Support payments the borrower chooses to disclose

- **Source category:** `REGULATORY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Alimony, child support and maintenance need not be disclosed unless the borrower chooses to rely on them for qualification. Where the borrower does rely on them, a legal order or agreement establishing the amount and its end date is required, together with evidence of receipt for the most recent six months. Income terminating within the continuance window in INC-GEN-003 is excluded.

| Parameter | Value |
| --- | --- |
| `required_receipt_months` | 6 |
| `disclosure` | at the borrower's election only |

**Acceptable evidence.** Court order or written agreement; Six months of receipt evidence.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Income model' and 'Regulatory and agency landscape' - Regulation B restricts requests about support obligations and the borrower's reliance is elective.

### INC-OTH-005 — Military pay and allowances

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Base military pay qualifies as salaried income. Housing and subsistence allowances qualify where the leave and earnings statement evidences them and they are expected to continue; they are commonly non-taxable, in which case INC-GEN-005 applies. Temporary or duty-specific allowances such as hazard or deployment pay are excluded, because they end when the duty ends.

| Parameter | Value |
| --- | --- |
| `base_pay` | qualify as salaried |
| `housing_and_subsistence` | qualify where evidenced and continuing |
| `temporary_duty_pay` | excluded |

**Acceptable evidence.** Leave and earnings statement; Employment verification.

**See also:** POL-VA-001, POL-INC-002.

## 5. Documentation requirements

- Award letters, benefit statements or orders for every source relied upon.
- Evidence of receipt for the period each rule requires.
- Documentation of non-taxable status where a gross-up is applied.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-INC-001
- POL-AST-001
- POL-VA-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
