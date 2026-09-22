<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python synthetic_data/mortgage/generator/generate_synthetic_data.py -->

# CredPilot Synthetic Data Report

Generated with `SYNTHETIC_SEED=20260920`. Every figure below is counted from the committed files at generation time.

## 1. Source documents read

| Document | Role |
| --- | --- |
| `synthetic_data/mortgage/research/deep-research-report.md` | The completed Deep Research mortgage-domain report. Primary design authority for the data model, calculations, policy architecture, scenario matrix and human-review classification. |
| `requirements_validation_tests/source_requirements/requirements_verbatim.md` | The 112 verbatim requirements extracted from the business case, hash-verified. Highest authority on what must exist. |
| `requirements_validation_tests/source_document/EXTRACTION_NOTE.md` | Provenance of the requirements extraction. |
| `requirements_validation_tests/BASELINE_REQUIREMENTS.md` | The integrity contract around the baseline. |
| `requirements_validation_tests/traceability/requirement_traceability_matrix.md` | Existing requirement-to-test mapping, read to avoid contradicting the QA layer's expectations. |
| The 15 files under `test_specs/` | What the validation suite will check, including the paths and PII patterns it enforces. |

## 2. Research report used

`synthetic_data/mortgage/research/deep-research-report.md` is a completed research report, not a research prompt. It contains findings, a source ledger of 41 prioritised references, a canonical data dictionary, a calculation specification with worked examples, a policy-family architecture, a scenario matrix and a human-in-the-loop classification. The dataset blueprint in its final section is the primary guide for the entity model built here.

Three of its worked examples were used as acceptance tests for the calculation library: LTV of 80% from a 400,000 loan against min(500,000, 510,000); CLTV of 85% adding a 25,000 subordinate lien; and 10.39 months of reserves from 40,000 against a 3,850 housing expense. All three reproduce exactly.

## 3. Requirements identified

See `synthetic_data/mortgage/REQUIREMENTS_TRACEABILITY.md` for the full table. Every artifact traces to an explicit business-case requirement, a researched mortgage-domain requirement, or a labelled synthetic design decision.

## 4. Design assumptions

See `synthetic_data/mortgage/DESIGN_ASSUMPTIONS.md`. Every assumption is recorded there with its basis and its consequence; none is resolved silently.

## 5-22. Dataset contents

| # | Measure | Count |
| ---: | --- | ---: |
| 5 | Synthetic borrower profiles | 90 |
| 6 | Co-borrower participations | 17 |
| 7 | Mortgage applications | 75 |
| 8 | Product families represented | 5 |
| 9 | Properties | 75 |
| 10 | Employment records | 181 |
| 11 | Income records | 99 |
| 12 | Asset records | 296 |
| 13 | Liability records | 300 |
| 14 | Credit records (profiles + tradelines + events) | 396 |
| 15 | Applicant documents | 1140 |
| 16 | Policy documents | 42 |
| 17 | Policy rule versions | 203 |
| 18 | Policies carrying more than one version | 6 |
| 19 | Risk scenarios (total in the catalogue) | 75 |
| 20 | Human-review cases | 47 |
| 21 | Security / adversarial cases | 6 |
| 22 | Evaluation / golden-set cases | 75 |

Product spread: `conventional_conforming` x70, `fha` x1, `jumbo` x2, `usda` x1, `va` x1.

Versioned policies: `POL-AST-003` (2 versions), `POL-CRD-001` (2 versions), `POL-DTI-001` (2 versions), `POL-INC-004` (2 versions), `POL-JUMBO-001` (2 versions), `POL-VAL-001` (2 versions).

Returning applicants (appearing on more than one application): 2.

## 23-24. Validation

Run `python synthetic_data/mortgage/generator/validate_synthetic_data.py`. The validator executes 39 checks across structure, integrity, dates, financial recomputation, policy, traceability, documents, privacy, governance, security, coverage and evaluation. It exits non-zero on any violation and names the offending rows.

The financial checks re-derive their values from the raw inputs rather than comparing a stored figure to itself: amortisation is recomputed from the note terms, the housing expense is rebuilt from its components, income is summed from the income rows, the settlement figure is rebuilt from its components and the reserve figure is produced by replaying the asset draw.

**Validation failures at the time of writing: none.** The validator was also negative-tested by corrupting a liability payment and unmasking an identifier; it detected both.

## 25. Policy coverage

32 of 36 policy families are exercised by at least one application. See `synthetic_data/mortgage/POLICY_TEST_COVERAGE.md` for the rule-level matrix, including which rules have positive, boundary and negative cases.

## 26. Scenario coverage

See `synthetic_data/mortgage/SCENARIO_COVERAGE.md`. Every recommendation value in the controlled vocabulary is produced by at least one scenario, and all six security attack types are represented.

## 27. Known limitations

- **The synthetic automated-underwriting service is a placeholder.** The research report is explicit that DU and LPA risk models are proprietary and must not be reverse-engineered. This dataset therefore models the *shape* of an automated finding - a recommendation category and a message set - and does not attempt the underlying scoring. No `aus_submissions` table is populated.
- **Disclosure timing is modelled as policy text, not as data.** Loan Estimate and Closing Disclosure obligations appear in the corpus but no disclosure event rows are generated, because the underwriting MVP does not reach them.
- **Closing and servicing are out of scope.** The schema preserves the handoff point but no closing_events or servicing rows exist.
- **One property per application.** Multiple financed properties are modelled as a count that drives the reserve requirement, not as separate property rows.
- **Income history is summarised, not enumerated.** Variable-income scenarios carry a history length and a trend rather than month-by-month rows.
- **Geography is coarse.** Property-tax rates vary by state from a small committed table; there is no county or municipality granularity.
- **The document corpus is plain text.** Documents carry the fields an underwriter needs but are not PDFs or images, so optical extraction and image-level tampering detection cannot be exercised against them.

## 28. Research areas not publicly available

The research report names these as gaps, and this dataset does not paper over them:

- Detailed internal underwriting policies, scorecards, fraud models, pricing models, overlays, exception matrices and approval authorities of any named lender. Public lender pages establish products and consumer-facing process only. **No real lender's internal policy is reproduced anywhere in this corpus.**
- The statistical decision algorithms behind Desktop Underwriter and Loan Product Advisor. Recommendation categories are public; the models are not.
- Complete jumbo criteria, which are set by private investor overlays. This is why `POL-JUMBO-001` is explicitly a fictional overlay and why every jumbo file in the dataset routes to a human.

## 29. Synthetic assumptions

Of 203 rule versions in the corpus, 172 are labelled `SYNTHETIC_INTERNAL_POLICY`, 17 `REGULATORY`, 9 `AGENCY_INVESTOR` and 5 `COMMON_INDUSTRY_PRACTICE`.

Every numeric threshold that drives a pass or fail outcome is `SYNTHETIC_INTERNAL_POLICY` unless the research report establishes the exact value as a genuine public rule for that product and context. The schema enforces this: a rule carrying a numeric parameter under a weaker authority label raises an error at import time rather than reaching the corpus.

The three exceptions, where a genuine published figure is used and attributed, are the 2026 conforming and FHA loan limits in `GEN-ELG-003`, the agency DTI framework stated in `DTI-CALC-001`, and the regulatory obligations in the `REGULATORY` rules. In each case the rule states the public framework and a separate synthetic rule carries the number this lender actually enforces.

## 30. Commands to regenerate everything

```bash
# Generate. Deterministic: the same seed produces byte-identical output.
SYNTHETIC_SEED=20260920 python synthetic_data/mortgage/generator/generate_synthetic_data.py

# Validate. Exits non-zero on any violation.
python synthetic_data/mortgage/generator/validate_synthetic_data.py
```

On Windows PowerShell:

```powershell
$env:SYNTHETIC_SEED = '20260920'
python synthetic_data/mortgage/generator/generate_synthetic_data.py
python synthetic_data/mortgage/generator/validate_synthetic_data.py
```

The seed defaults to 20260920, so both commands work with no environment variable set. Generation takes a few seconds and rewrites every artifact under `data/` and `synthetic_data/mortgage/`.
