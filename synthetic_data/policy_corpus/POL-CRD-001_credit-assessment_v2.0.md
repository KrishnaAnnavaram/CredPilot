---
policy_id: POL-CRD-001
title: Credit Assessment and Representative Score
version: 2.0
family: credit-assessment
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
priority: 40
supersedes: "POL-CRD-001 v1.0"
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - CRD-SCR-001
  - CRD-SCR-002
  - CRD-SCR-005
  - CRD-SCR-006
  - CRD-SCR-003
  - CRD-SCR-004
  - CRD-SCR-007
synthetic: true
---

# Credit Assessment and Representative Score

**POL-CRD-001 · version 2.0 · effective 2026-07-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Establishes how credit evidence is obtained, how a representative score is derived from it, and what minimum credit standard applies. It is the document a retrieval agent needs when the question is about score thresholds rather than about a specific derogatory event.

## 2. Scope

Applies to every programme. Where a product document states a higher credit floor - as POL-CONV-003 and POL-JUMBO-001 do - the product floor governs.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### CRD-SCR-001 — A credit report must be obtained for a permissible purpose

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A consumer report may be obtained only for a permissible purpose under the Fair Credit Reporting Act, and where an adverse action is based in whole or in part on information in that report, the notice obligations that attach to it apply. The credit report's provider, identifier and date must be recorded; a score with no report metadata behind it is not usable evidence.

**Acceptable evidence.** Consumer report with provider, report identifier and report date; Borrower authorisation on file.

**See also:** POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Regulatory and agency landscape' - FCRA permissible purpose and adverse-action duties.

### CRD-SCR-002 — Representative score methodology

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `CALCULATION`

**Applies when.** All applications within this document's scope.

For one borrower, the representative score is the middle of three scores, or the lower of two, or the single score where only one is available. For an application with more than one borrower, the application's representative score is the lowest of the borrowers' representative scores. The score model must be recorded alongside the value: a score without its model is not comparable to a threshold.

| Parameter | Value |
| --- | --- |
| `single_borrower` | middle of three, lower of two, otherwise the one |
| `multi_borrower` | lowest borrower representative score |
| `model_metadata_required` | yes |

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Liability/credit model' - representative-score methodology must be preserved; agency casefiles do not apply a single published minimum in the same way manual underwriting does.

### CRD-SCR-005 — Thin or absent credit history is not a failure

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `REFER` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A borrower with fewer than three scoreable tradelines, or with no usable score, is routed for manual credit review with alternative credit evidence. Absence of credit history is not the same as adverse credit history, and must not be scored as though it were.

| Parameter | Value |
| --- | --- |
| `min_scoreable_tradelines_for_score_path` | 3 |

**Acceptable evidence.** Alternative credit references such as rent, utility or insurance payment history.

**See also:** POL-UWR-001.

### CRD-SCR-006 — Prohibited-basis characteristics are never credit factors

- **Source category:** `REGULATORY` · **Severity:** `HARD_FAIL` · **Outcome:** `PROCESS`

**Applies when.** All applications within this document's scope.

Race, colour, religion, national origin, sex, marital status, age and the receipt of public assistance income may never be used as a factor in assessing creditworthiness, eligibility, affordability or the decision. Demographic information collected for statutory monitoring is held separately from the underwriting record and must not be supplied to any component that produces an eligibility, risk or recommendation output. Income from a public-assistance or retirement source is analysed for amount and likely continuance like any other income, never discounted for its source.

| Parameter | Value |
| --- | --- |
| `prohibited_factors` | race, colour, religion, national origin, sex, marital status, age, receipt of public assistance |
| `monitoring_data_storage` | segregated from underwriting features |

**See also:** POL-SEC-001, POL-DEC-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Regulatory and agency landscape' and 'Income model' - ECOA / Regulation B 12 CFR 1002.6 evaluation rules and the prohibition on discounting public-assistance income.

### CRD-SCR-003 — Minimum representative score, graduated by leverage

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The minimum representative score for a conventional conforming transaction is graduated by loan-to-value: 620 at or below 90 percent, and 640 above 90 percent. Version 1.0 of this policy applied a flat 620 floor at every leverage level; an application whose underwriting as-of date falls before 2026-07-01 is still measured against that flat floor. A borrower at 660 with 95 percent leverage therefore passes under either version, while a borrower at 630 with 95 percent leverage passes under version 1.0 and fails under this one.

| Parameter | Value |
| --- | --- |
| `min_representative_score_ltv_at_or_below_90` | 620 |
| `min_representative_score_ltv_above_90` | 640 |
| `ltv_band_boundary` | 90% |

### CRD-SCR-004 — Credit report freshness

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

The credit report must be no older than 90 days on the note date, reduced from 120 days in version 1.0. A report older than that is refreshed rather than extrapolated, because new obligations appearing after the report date change the debt-to-income calculation.

| Parameter | Value |
| --- | --- |
| `max_report_age_days` | 90 |

**Condition raised when unsatisfied.** Obtain a refreshed credit report before closing.

**See also:** POL-DOC-001.

### CRD-SCR-007 — Recent inquiries must be addressed, not scored

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`

**Applies when.** All applications within this document's scope.

Four or more credit inquiries in the 90 days before the report date require a written explanation identifying whether any resulted in new debt, and any new debt identified is added to the liabilities and the debt-to-income ratio is recomputed. Inquiry count is never itself a basis for an adverse outcome; rate-shopping for a single purpose commonly produces several inquiries.

| Parameter | Value |
| --- | --- |
| `inquiry_lookback_days` | 90 |
| `inquiry_count_trigger` | 4 |

**Condition raised when unsatisfied.** Provide a written explanation for the {inquiry_count} credit inquiries in the {lookback_days} days before the report date, stating whether any resulted in new debt.

**See also:** POL-LIA-001.

## 5. Documentation requirements

- Consumer report with provider, identifier, date and every available score with its model.
- Borrower authorisation for the credit inquiry.
- Written explanation of recent inquiries where CRD-SCR-007 requires one.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-CRD-002
- POL-CRD-003
- POL-LIA-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| (prior) | before 2026-07-01 | Superseded by this version. Prior version identifier: POL-CRD-001 v1.0. |
| 2.0 | 2026-07-01 | Graduated the score floor by leverage (620 at or below 90 percent LTV, 640 above), shortened report freshness from 120 to 90 days, and added the recent-inquiry rule CRD-SCR-007. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
