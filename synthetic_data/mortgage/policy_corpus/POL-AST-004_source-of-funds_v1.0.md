---
policy_id: POL-AST-004
title: "Gifts, Grants and Source of Funds"
version: 1.0
family: source-of-funds
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
priority: 55
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - AST-SRC-001
  - AST-SRC-002
  - AST-SRC-003
  - AST-SRC-004
synthetic: true
---

# Gifts, Grants and Source of Funds

**POL-AST-004 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Governs where the borrower's funds came from. The concern is not generosity but obligation: money that must be repaid is a liability, and money with no traceable source cannot be verified as the borrower's at all.

## 2. Scope

Applies to every source of funds used for closing or counted as reserves.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 3. Definitions

**Large deposit.** A single deposit, or a set of related deposits, exceeding the threshold in AST-SRC-002 that is not identifiable as payroll or another established recurring source.

## 4. Rules

### AST-SRC-001 — Gift eligibility and documentation

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A gift may be provided by a relative, a legal partner, a fiancé or a documented employer programme. It may not be provided by any party with an interest in the transaction - the seller, the builder, the agent or the lender - because such a contribution is an interested-party contribution and is governed by CONV-PUR-005 instead. Gifts are not permitted on investment-property transactions. A gift requires a signed letter stating the amount, the donor, the relationship and that no repayment is expected, plus evidence of the transfer.

| Parameter | Value |
| --- | --- |
| `eligible_donors` | relative, legal partner, fiancé, employer programme |
| `prohibited_donors` | seller, builder, agent, lender, any interested party |
| `investment_property_gifts` | no |
| `reserve_eligible` | no |

**Acceptable evidence.** Signed gift letter with amount, donor, relationship and no-repayment statement; Evidence of the transfer into the borrower's verified account.

**Condition raised when unsatisfied.** Provide a signed gift letter and transfer evidence for the gift of {amount} from {donor}.

**See also:** POL-CONV-001.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Asset model' - agency gift eligibility differs by occupancy and purpose, and gifts are generally not permitted on investment-property transactions.

### AST-SRC-002 — Large deposits require a documented source

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A deposit exceeding 50 percent of the borrower's qualifying monthly income, and not identifiable as payroll or another established recurring source, must be sourced with documentary evidence. Until it is sourced, the deposit amount is deducted from eligible assets and the funds-to-close and reserve calculations are re-run without it. An unsourced deposit is not counted and then flagged; it is excluded and then the consequences are reported.

| Parameter | Value |
| --- | --- |
| `threshold_pct_of_qualifying_monthly_income` | 50% |
| `interim_treatment` | exclude from eligible assets and recompute |
| `excluded_from_test` | payroll and established recurring credits |

**Acceptable evidence.** Documentation identifying the origin of the funds; Evidence the funds are not borrowed.

**Condition raised when unsatisfied.** Document the source of the deposit of {amount} on {deposit_date} and confirm the funds are not borrowed.

**See also:** POL-FRD-001, POL-AST-002.

**Basis.** Completed research report, `synthetic_data/mortgage/research/deep-research-report.md`, 'Missing/conflicting data workflow' - a large deposit with no source is conditioned and risk-flagged, and is not automatically counted.

### AST-SRC-003 — Borrowed funds

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Funds borrowed against an asset the borrower owns may be used where the loan is secured by that asset and the repayment obligation is added to the debt-to-income calculation. Unsecured borrowed funds - a personal loan, a cash advance, an undocumented transfer from a third party - are not eligible for closing or reserves under any circumstances.

| Parameter | Value |
| --- | --- |
| `secured_borrowing_eligible` | yes |
| `unsecured_borrowing_eligible` | no |
| `payment_enters_dti` | yes |

**Acceptable evidence.** Loan agreement showing the security; Evidence of the pledged asset.

**See also:** POL-LIA-001.

### AST-SRC-004 — Grants and employer assistance

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A grant or employer assistance programme may fund closing where the programme documentation confirms the terms and states whether repayment is required. Where any repayment obligation exists, including a forgivable amount that becomes repayable on an early sale, the obligation is recorded as a liability and any monthly payment enters the debt-to-income calculation.

| Parameter | Value |
| --- | --- |
| `repayable_component_treated_as` | liability |
| `reserve_eligible` | no |

**Acceptable evidence.** Programme award documentation stating the repayment terms.

## 5. Documentation requirements

- Gift letters and transfer evidence for every gift.
- Source documentation for every large deposit identified.
- Programme documentation for grants and employer assistance.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-AST-001
- POL-AST-002
- POL-FRD-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
