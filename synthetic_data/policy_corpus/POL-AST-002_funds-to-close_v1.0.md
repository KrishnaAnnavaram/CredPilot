---
policy_id: POL-AST-002
title: Funds to Close and the Settlement Calculation
version: 1.0
family: funds-to-close
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
priority: 53
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - AST-FTC-001
  - AST-FTC-002
  - AST-FTC-003
  - AST-FTC-004
  - AST-FTC-005
synthetic: true
---

# Funds to Close and the Settlement Calculation

**POL-AST-002 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines the deterministic settlement calculation: what the borrower must bring, what reduces it, and what happens when eligible funds fall short.

## 2. Scope

Applies to every application. The calculation differs between purchase and refinance only in its components; the arithmetic and the sufficiency test are the same.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### AST-FTC-001 — The funds-to-close calculation

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Required funds to close are the down payment, plus borrower-paid closing costs, plus prepaid items and escrow deposits, plus any lien payoff not financed by the new loan, less seller and interested-party credits, less lender credits, less earnest money already on deposit, less cash-out proceeds received. Each component is stored individually; a single net figure with no components cannot be reconciled against the settlement statement.

| Parameter | Value |
| --- | --- |
| `formula` | down payment + closing costs + prepaids + payoff - seller credits - lender credits - earnest money - cash-out proceeds |
| `component_storage_required` | yes |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - cash to close is a deterministic settlement calculation that must reconcile to the disclosures.

### AST-FTC-002 — Synthetic closing-cost and prepaid basis

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

For this synthetic environment, borrower-paid closing costs are estimated as a fixed origination component plus a percentage of the loan amount, and prepaid items as a number of months of property tax and hazard insurance escrow plus per-diem interest. Real settlement costs vary by jurisdiction, settlement agent and transaction; these figures exist so the arithmetic is reproducible, not because they are market rates.

| Parameter | Value |
| --- | --- |
| `origination_fixed_component` | 1,850 |
| `third_party_cost_pct_of_loan` | 1.25% |
| `tax_escrow_months` | 3 |
| `hazard_escrow_months` | 2 |
| `prepaid_interest_days` | 15 |

**See also:** POL-DEC-001.

### AST-FTC-003 — Sufficiency test

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Eligible funds available for closing must be at least the required funds to close. A shortfall is a deterministic arithmetic failure, not a judgement: no compensating factor cures it. The file may still proceed where the borrower documents additional eligible assets, an increased seller credit within the interested-party limit, or a reduced loan amount - each of which changes an input and requires the calculation to be re-run.

| Parameter | Value |
| --- | --- |
| `test` | funds_to_close_available >= funds_to_close_required |
| `shortfall_curable_by` | additional eligible assets, increased permitted credits, reduced loan amount |

**See also:** POL-AST-001, POL-CONV-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Human-in-the-loop classification' - a mathematical funds-to-close shortfall with no permissible cure is a hard policy failure.

### AST-FTC-004 — Draw order and its effect on reserves

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Closing funds are drawn first from sources that are not reserve-eligible - gift funds, earnest money already deposited, sale proceeds - and only then from reserve-eligible liquid assets, in ascending asset-identifier order. The draw is recorded asset by asset, so the reserve calculation can show exactly which assets remained. Reserves are what is left after this draw; they are not a separate pool of money.

| Parameter | Value |
| --- | --- |
| `tier_one` | non-reserve-eligible sources |
| `tier_two` | reserve-eligible assets, ascending asset_id |
| `record` | per-asset draw amounts |

**See also:** POL-AST-003.

### AST-FTC-005 — Earnest money must be sourced like any other funds

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

An earnest-money deposit reduces the funds the borrower must bring to settlement, but only where the deposit is evidenced as having cleared the borrower's own verified account. A deposit credited on the contract with no corresponding withdrawal from a verified account is not a credit; it is an unsourced payment.

| Parameter | Value |
| --- | --- |
| `evidence_required` | cleared withdrawal from a verified account |

**Acceptable evidence.** Account statement showing the earnest-money withdrawal; Contract or escrow receipt showing the deposit.

**Condition raised when unsatisfied.** Evidence the source of the earnest-money deposit of {amount}.

**See also:** POL-AST-004.

## 5. Documentation requirements

- The itemised funds-to-close calculation with every component.
- Evidence of earnest money clearing a verified account.
- Evidence of seller and lender credits from the contract or lender records.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-AST-001
- POL-AST-003
- POL-CONV-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
