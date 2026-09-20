---
policy_id: POL-DTI-001
title: "Affordability, Debt-to-Income and Disposable Income"
version: 2.0
family: affordability-dti
effective_date: 2026-07-01
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
priority: 50
supersedes: "POL-DTI-001 v1.0"
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - DTI-CALC-001
  - DTI-CALC-002
  - DTI-CALC-003
  - DTI-CONV-001
  - DTI-CONV-002
  - DTI-CONV-003
  - DTI-BRE-001
  - DTI-BRE-002
synthetic: true
---

# Affordability, Debt-to-Income and Disposable Income

**POL-DTI-001 · version 2.0 · effective 2026-07-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines how affordability is measured and what limit applies. This is the document behind acceptance criterion AC-02: it is where a breach gets the threshold it failed.

## 2. Scope

Applies to every programme. Where a government overlay states its own affordability ceiling, the overlay governs for that programme, and this document continues to govern the definitions and the calculation method.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### DTI-CALC-001 — Definition and components of the affordability measures

- **Source category:** `AGENCY_INVESTOR` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Back-end debt-to-income is total monthly obligations divided by the stable monthly income used to qualify. Total monthly obligations are the qualifying housing expense plus every recurring obligation POL-LIA-001 marked for inclusion. The qualifying housing expense is principal, interest, property taxes, hazard insurance, association dues, mortgage or guarantee insurance, flood insurance where required, and any subordinate lien payment. The housing ratio uses the same numerator components restricted to the housing expense. Published agency guidance for conventional conforming loans sold to a government-sponsored enterprise defines the ratio this way and, in its current form, generally limits manually underwritten loans to 36 percent with specified circumstances allowing up to 45 percent, while automated-underwriting casefiles may permit up to 50 percent. Those are that agency's figures for its own programme. They are not universal mortgage thresholds, and they are not the limit this lender enforces - see DTI-CONV-001 for that.

| Parameter | Value |
| --- | --- |
| `back_end_formula` | total monthly obligations / qualifying monthly income |
| `front_end_formula` | qualifying housing expense / qualifying monthly income |
| `zero_income_result` | INDETERMINATE, never zero or infinite |

**See also:** POL-LIA-001, POL-INC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - Fannie Mae Selling Guide B3-6-02 defines DTI and states the manual and automated limits as agency-specific current guidelines, not universal thresholds.

### DTI-CALC-002 — Affordability is computed deterministically, never estimated

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Every affordability figure is produced by the committed calculation code with its inputs and formula version recorded. No affordability value may originate from a language model's arithmetic. A model may explain a computed ratio; it may not compute one, and a ratio appearing in a narrative that does not match the calculation record is a defect in the narrative.

| Parameter | Value |
| --- | --- |
| `rounding` | ratios to four decimal places, money to cents, half-up |
| `provenance_required` | input field ids and formula version |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Agentic AI architecture mapping' - the LLM must not be trusted to perform DTI, LTV, amortisation or date arithmetic.

### DTI-CALC-003 — Disposable income is reported alongside the ratio

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Monthly disposable income - qualifying monthly income less total monthly obligations - is computed and reported with every affordability assessment. Two files with the same ratio can have very different absolute capacity, and the residual figure is what the residual-income tests in the government overlays consume.

| Parameter | Value |
| --- | --- |
| `formula` | qualifying monthly income - total monthly obligations |

**See also:** POL-VA-001.

### DTI-CONV-001 — Maximum back-end debt-to-income, with a compensating-factor extension

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Back-end debt-to-income must not exceed 43 percent for a conventional conforming transaction. The ceiling extends to 45 percent where at least two compensating factors from DTI-CONV-003 are documented and named in the file. Version 1.0 of this policy allowed 45 percent unconditionally; an application whose underwriting as-of date falls before 2026-07-01 is still measured against that unconditional 45 percent. A file computing at 44 percent with no compensating factors therefore passes under version 1.0 and breaches under this version, which is exactly the distinction a policy-retrieval component has to get right.

| Parameter | Value |
| --- | --- |
| `max_back_end_dti` | 43% |
| `max_back_end_dti_with_factors` | 45% |
| `min_compensating_factors` | 2 |

### DTI-CONV-002 — Housing ratio is advisory

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

The housing ratio is computed and recorded for every application but is not itself a pass or fail test on conventional transactions. A housing ratio above 38 percent is noted in the risk summary. The USDA overlay is the exception: there the housing ratio is a hard test.

| Parameter | Value |
| --- | --- |
| `risk_note_threshold` | 38% |
| `hard_test` | no |

**See also:** POL-USDA-001.

### DTI-CONV-003 — Recognised compensating factors

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Only the following are recognised as compensating factors for the extension in DTI-CONV-001, and each must be documented and named explicitly in the decision record: verified post-closing reserves of at least six months of the qualifying housing expense; a representative credit score at or above 720; a proposed housing payment no greater than 105 percent of the borrower's documented current housing payment; verified continuous employment with the same employer for at least 60 months; and a loan-to-value at or below 75 percent. A factor that is asserted but not documented does not count, and the extension is not available on cash-out refinances or under the jumbo overlay.

| Parameter | Value |
| --- | --- |
| `factor_reserves_months` | 6 |
| `factor_min_credit_score` | 720 |
| `factor_max_payment_shock` | 5% |
| `factor_min_employment_months` | 60 |
| `factor_max_ltv` | 75% |
| `excluded_products` | cash_out_refinance, jumbo |

**Acceptable evidence.** Documentation of each factor claimed, cited by name.

**See also:** POL-AST-003, POL-CRD-001.

### DTI-BRE-001 — A breach is reported with the threshold it failed

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Where an affordability limit is breached, the finding must state the computed value, the threshold that was exceeded, the rule id and policy version that set it, and the inputs that produced the computed value. A breach reported without its threshold is not actionable: the borrower cannot tell how far away they are, and the reviewer cannot tell whether the right limit was applied.

| Parameter | Value |
| --- | --- |
| `required_fields` | computed_value, threshold_value, rule_id, policy_version, input_field_ids |

**See also:** POL-DEC-001.

### DTI-BRE-002 — Payment shock is recorded where a prior housing payment exists

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `ADVISORY` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

Where the borrower has a current housing payment, the proportional increase to the proposed payment is computed and recorded. A borrower with no prior housing payment has no meaningful denominator and the measure is recorded as not applicable rather than as zero. Payment shock is a risk indicator that can support a referral; it is not a threshold test.

| Parameter | Value |
| --- | --- |
| `formula` | (proposed PITIA - current housing payment) / current housing payment |
| `no_prior_payment` | not applicable |
| `risk_note_threshold` | 50% |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Underwriting calculations' - payment shock is a common risk indicator, not a universal hard threshold.

## 5. Documentation requirements

- The calculation record for every affordability figure, with inputs and formula version.
- Evidence supporting every income and obligation component.
- Named documentation for each compensating factor relied upon.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-INC-001
- POL-LIA-001
- POL-GEN-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| (prior) | before 2026-07-01 | Superseded by this version. Prior version identifier: POL-DTI-001 v1.0. |
| 2.0 | 2026-07-01 | Reduced the unconditional back-end ceiling from 45 to 43 percent and introduced the documented compensating-factor extension to 45 percent (DTI-CONV-003). |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
