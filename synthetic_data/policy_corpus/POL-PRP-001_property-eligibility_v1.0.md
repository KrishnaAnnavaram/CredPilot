---
policy_id: POL-PRP-001
title: Property Eligibility
version: 1.0
family: property-eligibility
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
priority: 56
supersedes: null
superseded_by: null
requires_human_review: false
issuer: Northwind Residential Lending (fictional)
owner: Credit Policy Office
rule_ids:
  - PRP-ELG-001
  - PRP-ELG-002
  - PRP-ELG-003
  - PRP-ELG-004
synthetic: true
---

# Property Eligibility

**POL-PRP-001 · version 1.0 · effective 2026-01-01**

> This is a **synthetic lending policy** written for the CredPilot hackathon and attributed to Northwind Residential Lending (fictional). It is not the policy of any real lender, and no proprietary automated-underwriting logic is reproduced in it. Each rule below declares its own `source_category`; only rules marked `SYNTHETIC_INTERNAL_POLICY` invent a number.

## 1. Purpose

Defines what collateral the lender will accept. Property eligibility is assessed independently of the borrower: a strong borrower does not make an ineligible property eligible.

## 2. Scope

Applies to the subject property on every application.

- **Products:** conventional_conforming, jumbo, fha, va, usda
- **Occupancy:** primary_residence, second_home, investment
- **Loan purpose:** purchase, rate_term_refinance, cash_out_refinance
- **Jurisdiction:** US

## 4. Rules

### PRP-ELG-001 — Eligible property types

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `HARD_FAIL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

Eligible property types are the detached single-family residence, the attached single-family residence or townhouse, the approved condominium unit, the planned-unit-development unit, and the two-to-four-unit residential property. Manufactured housing, co-operative units, properties with more than four units, working farms, and properties whose commercial use exceeds 25 percent of the floor area are not eligible under this document.

| Parameter | Value |
| --- | --- |
| `max_units` | 4 |
| `max_commercial_floor_area_pct` | 25% |
| `ineligible_types` | manufactured housing, co-operative, 5+ units, working farm |

**Acceptable evidence.** Appraisal property description; Purchase contract.

### PRP-ELG-002 — Condition and habitability

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

The property must be safe, sound and habitable at closing. A valuation reporting deferred maintenance that affects safety, structural integrity or habitability raises a repair condition that must be satisfied and re-inspected before closing. A condition rating at the lower end of the valuation's scale routes the file for collateral review rather than failing it outright.

| Parameter | Value |
| --- | --- |
| `repair_condition_triggers` | safety, structural integrity or habitability findings |
| `reinspection_required` | yes |

**Condition raised when unsatisfied.** Complete the repairs identified in the valuation and provide a satisfactory re-inspection.

**See also:** POL-VAL-001.

### PRP-ELG-003 — Condominium project eligibility

- **Source category:** `SYNTHETIC_INTERNAL_POLICY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_REFER_FAIL`
- **Human review:** required when this rule is triggered.

**Applies when.** All applications within this document's scope.

A condominium unit requires a project review confirming that the association is financially sound, that owner occupancy is at least 50 percent for a non-primary-residence transaction, that no single entity owns more than 20 percent of the units, and that there is no pending litigation affecting the structure or safety of the project. Project issues are project-level findings; they are recorded against the project and not as a fault of the applicant.

| Parameter | Value |
| --- | --- |
| `min_owner_occupancy_non_primary` | 50% |
| `max_single_entity_ownership` | 20% |
| `structural_litigation` | ineligible pending resolution |

**Acceptable evidence.** Project questionnaire; Association financial statements.

**Condition raised when unsatisfied.** Provide a completed project review for {project_name}.

### PRP-ELG-004 — Flood zone and required coverage

- **Source category:** `REGULATORY` · **Severity:** `CONDITIONAL` · **Outcome:** `PASS_FAIL`

**Applies when.** All applications within this document's scope.

A flood-zone determination is obtained for every property. Where the property is in a special flood hazard area, flood insurance meeting the applicable federal and investor requirements must be in force at closing, and its premium is included in the qualifying housing expense. A determination is required even where the outcome is that no coverage is needed, because the absence of a determination is itself a finding.

| Parameter | Value |
| --- | --- |
| `determination_required` | yes |
| `coverage_required_in_sfha` | yes |
| `premium_enters_housing_expense` | yes |

**Acceptable evidence.** Flood-zone determination; Flood policy or binder where required.

**Condition raised when unsatisfied.** Provide flood insurance evidence for the subject property.

**See also:** POL-TTL-001, POL-DTI-001.

**Basis.** Completed research report, `synthetic_data/research/deep-research-report.md`, 'Lifecycle controls and evidence' - flood and hazard insurance requirements are federal and investor obligations.

## 5. Documentation requirements

- Valuation describing the property type, units, condition and characteristics.
- Project review for condominium units.
- Flood-zone determination for every property.

## 6. Exceptions and escalation

Any departure from this document requires a documented exception approved under POL-UWR-001. An exception is never granted by an automated component.

## 7. Related policies

- POL-VAL-001
- POL-PRP-002
- POL-TTL-001

## 8. Version history

| Version | Effective | Note |
| --- | --- | --- |
| 1.0 | 2026-01-01 | Initial version. |

An application is evaluated against the version whose effective window contains the application's underwriting as-of date. Retrieving the newest version of a policy is not the same as retrieving the applicable one.
