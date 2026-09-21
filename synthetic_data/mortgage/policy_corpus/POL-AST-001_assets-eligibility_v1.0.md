---
policy_id: POL-AST-001
title: Assets and Eligible Funds
version: 1.0
family: assets-eligibility
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
priority: 52
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - AST-ELG-001
  - AST-ELG-002
  - AST-ELG-003
  - AST-ELG-004
synthetic: true
---

# Assets and Eligible Funds

**POL-AST-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Determines which assets count, at what amount, and for which purpose. An asset has two independent eligibility questions - can it be used to close, and can it be counted as a reserve - and the answers are frequently different.

## 2. Scope

Applies to every asset on every application. Each asset carries a declared balance, a verified balance, an amount eligible for closing and an amount eligible for reserves; the four are stored separately.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Eligible for closing.** The portion of a verified asset the borrower can actually liquidate and bring to settlement. Retirement funds subject to a withdrawal restriction are commonly reserve-eligible but not closing-eligible.

**Liquidity haircut.** A reduction applied to an asset's verified balance to reflect the cost or uncertainty of converting it to cash. The haircut is applied once and is recorded as its own calculation step.

## 4. Rules

### AST-ELG-001 — Asset categories and their haircuts

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Verified balances are adjusted by category before use. Deposit accounts count in full. Publicly traded securities count at 80 percent of verified value for both closing and reserves. Vested retirement assets count at 60 percent, and only where the plan permits withdrawal or a loan; where it does not, the asset is reserve-eligible only. Gift funds count in full for closing and are never reserve-eligible. Cryptocurrency and other non-custodial holdings are excluded entirely unless converted to a verified deposit account before the funds-to-close calculation.

| Parameter | Value |
| --- | --- |
| `checking_savings_money_market_factor` | 1.00 |
| `certificate_of_deposit_factor` | 1.00 |
| `securities_factor` | 80% |
| `retirement_factor` | 60% |
| `gift_funds_factor` | 1.00 |
| `gift_reserve_eligible` | no |
| `crypto_eligible` | no |

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Asset model' - assets require declared, verified, closing-eligible, reserve-eligible and haircut values separately; the factors here are synthetic.

### AST-ELG-002 — Ownership and access

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

An asset counts only where a borrower on the application is an owner of the account. Where an account is held jointly with a non-borrower, the full balance may be used if the non-borrower provides written access consent; otherwise the borrower's proportional share is used. A business account may be used only where the borrower's access to the funds is evidenced and the withdrawal does not impair the business's operation.

| Parameter | Value |
| --- | --- |
| `joint_with_non_borrower_default` | proportional share |
| `joint_with_written_consent` | full balance |
| `business_account_requires_access_evidence` | yes |

**Acceptable evidence.** Account statement showing ownership; Written access consent.

**Condition raised when unsatisfied.** Evidence ownership of and access to account {asset_id}.

### AST-ELG-003 — Verified balance governs over declared balance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Where a verified balance is lower than the declared balance, the verified figure is used and the funds-to-close and reserve calculations are re-run against it. The difference is recorded as a data-quality finding. Where the verified balance is materially higher than declared, the increase is investigated under AST-SRC-002 before being used, because unexplained growth is itself a source-of-funds question.

| Parameter | Value |
| --- | --- |
| `governing_value` | verified balance |
| `unexplained_increase_trigger` | review under AST-SRC-002 |

**See also:** POL-AST-004, POL-AST-002.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Missing/conflicting data workflow' - where the bank balance is lower than declared assets, use the verified eligible balance and recalculate funds and reserves.

### AST-ELG-004 — Asset verification freshness

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Asset evidence must be dated within 60 days of the note date and must cover at least two consecutive monthly statement periods where source-of-funds review applies. A single statement shows a balance; two show whether that balance is the borrower's or arrived last week.

| Parameter | Value |
| --- | --- |
| `max_age_days` | 60 |
| `statement_periods_required` | 2 |

**Condition raised when unsatisfied.** Provide asset statements for the two most recent periods.

**See also:** POL-DOC-001, POL-AST-004.

## 5. Documentation requirements

- Account statements or a validated asset-verification report for every asset.
- Written access consent for joint accounts with a non-borrower.
- Plan documentation where retirement assets are relied upon for closing.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-AST-002
- POL-AST-003
- POL-AST-004

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
