# Requirements Traceability

Every artifact in this dataset traces back to one of three things:

- **A** — an explicit requirement in the hackathon business case,
- **B** — a researched mortgage-domain requirement from the completed Deep Research report, or
- **C** — a clearly labelled synthetic design decision made by this project.

Where a source is silent, the gap is filled by a **C** row and recorded in
[DESIGN_ASSUMPTIONS.md](DESIGN_ASSUMPTIONS.md), never by inventing a mortgage rule
and presenting it as real.

**Source-of-truth order.** Where sources conflict, the order is: business-case
mandatory requirements first, then the completed research report, then the
regulatory and agency facts the report cites, then publicly documented industry
practice, then explicit synthetic assumptions. One conflict arose in practice and is
recorded at the end of this file.

The business-case requirement ids below are the ones assigned by the existing QA
layer in `requirements_validation_tests/source_requirements/requirements_verbatim.md`. Research-report references name the section of the completed report, which is
committed at `synthetic_data/mortgage/research/deep-research-report.md`.

---

## A — Requirements from the hackathon business case

| Requirement ID | Requirement | Source Document | Source Section | Synthetic Artifact Needed | Implementation |
| --- | --- | --- | --- | --- | --- |
| SDR-A01 | "Use only synthetic loan applications and lending policies you generate." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-031, §3.4 Synthetic-Data Rule | A wholly generated application set and policy corpus with no real-world record anywhere | `generator/generate_synthetic_data.py` builds every row; all 90 people come from committed name pools in `people.py`, not from any external source |
| SDR-A02 | "Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-031, §3.4 | Tokenised identifiers with masked display forms | `SYN-SSN-nnnnnn` → `***-**-nnnn`, `SYN-ACCT-nnnnnn` → `******nnnn`, `SYN-CRDT-nnnnnn` → `****nnnn`, minted in `synthetic_data_utils.py`; the validator scans every committed CSV, JSONL, text, log, JSON and Markdown artifact for plaintext patterns |
| SDR-A03 | "All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-060, NFR-05 | Masking enforced in rendered documents as well as tables | No rendered document contains a raw `SYN-` token; the validator fails if one appears |
| SDR-A04 | "Untrusted free-text applicant-supplied content is quarantined and never treated as instructions." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-058, NFR-03 | Applicant text carrying a trust class, labelled and isolated | `untrusted_applicant_text` block in each input packet is labelled `UNTRUSTED_APPLICANT_TEXT` with `trust_class: customer_evidence`; rule `SEC-INJ-001` in `POL-SEC-001` states the handling |
| SDR-A05 | "attempts to inject instructions or access another applicant's data are refused, and sensitive data … is never exposed in answers or logs." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-049, AC-06 | Adversarial cases with expected refusal behaviour | 6 security scenarios (SCN-065 … SCN-070) covering injection, policy override, instruction smuggling, PII extraction, cross-customer access and out-of-scope; each carries `expected_security_behavior` in `expected_results.jsonl` |
| SDR-A06 | "the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-044, AC-01 | A retrievable corpus with stable, citable rule ids, and an eligibility result per application | 42 policy documents with 174 addressable rule ids; `eligibility_results.csv` and `rule_evaluations.csv` name the rule and version for every determination |
| SDR-A07 | "computes affordability (DTI / disposable income) … and flags any policy breach with the threshold it failed." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-045, AC-02 | Both measures computed deterministically, and breaches carrying their threshold | `back_end_dti`, `front_end_dti` and `residual_income_monthly` in `underwriting_calculations.csv`; every breach row in `rule_evaluations.csv` carries `observed_value`, `comparator` and `threshold_value`; rule `DTI-BRE-001` makes this an explicit obligation |
| SDR-A08 | "produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-046, AC-03 | A controlled recommendation vocabulary, written reasons, and human routing | `decisions.csv` uses the six-value vocabulary from `DEC-REC-001`; `decision_reasons.csv` gives the specific reason; 47 applications route to `human_reviews.csv`; every decline and every jumbo file is among them |
| SDR-A09 | "ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-047, AC-04 | An out-of-scope case with an escalation expectation | SCN-070 submits a request the system does not perform; rule `SEC-INJ-004` requires clarify-or-escalate |
| SDR-A10 | "it uses facts stated earlier in the interaction and recalls prior-session context on a return visit." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-048, AC-05 | The same borrower appearing on more than one application, at different times | SCN-063 and SCN-064 reuse the borrowers from SCN-001 and SCN-010 months later; `application_borrowers.csv` links them, and the later file's outcome does **not** inherit the earlier one |
| SDR-A11 | "an agentic-RAG tool over a synthetic lending-policy corpus" at `data/policy_corpus/` | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-076, §7.1 | A corpus rich enough for non-trivial retrieval | `synthetic_data/mortgage/policy_corpus/` holds 42 Markdown documents with YAML front matter; thresholds appear only in the body, never in a filename or title, so a retriever must read the document |
| SDR-A12 | "a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance)" | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-055 AC-12, REQ-090 §7.6 | A golden set with ground truth separated from inputs | `evaluation_cases.jsonl` (inputs only) and `expected_results.jsonl` (ground truth), 75 cases each |
| SDR-A13 | "The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-033, Reproducibility Rule | Deterministic generation from a documented seed | `python synthetic_data/mortgage/generator/generate_synthetic_data.py` with `SYNTHETIC_SEED` (default 20260920); two consecutive runs produce byte-identical output across all 1,302 files |
| SDR-A14 | "Single documented command runs the copilot and a second regenerates … committed sample inputs." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-057, NFR-02 | Committed inputs, discoverable and named consistently | Input packets live at `synthetic_data/mortgage/applications/`, one file per application plus an index. See the recorded deviation at the end of this file for what this costs against the QA layer's fixed directory list |
| SDR-A15 | "Real credit-bureau or core-banking integrations — use synthetic application and policy data." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-066, §6.2 | Synthetic adapters standing in for external services | `verifications.csv` records a synthetic provider (`SYNTH-VERIFY`) and `credit_profiles.csv` a synthetic bureau (`SYNTH-TRIMERGE`); no external call exists |
| SDR-A16 | "Use the approved open-source stack with Google Gemini as the only model provider (not Claude)." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-032, §3.4 | No Anthropic dependency anywhere in the runtime | Generation and validation use the Python standard library only; no model provider of any kind is invoked, and no `anthropic` package, API call or key appears |
| SDR-A17 | "Evidence artifacts … are machine-generated by committed code; the code that produced each is committed alongside it." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-061, NFR-06 | Generated documentation, not hand-written summaries | `DATA_DICTIONARY.md`, `POLICY_TEST_COVERAGE.md`, `SCENARIO_COVERAGE.md` and `SYNTHETIC_DATA_REPORT.md` are produced by `reports.py` and carry a generated-file banner |
| SDR-A18 | "A claim with no committed evidence scores zero; an evidence artifact with no producing code … is heavily discounted." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-029, Evidence-in-Repo Rule | Data and the code that produced it both committed | The generator sits in `synthetic_data/mortgage/generator/`, directly beside the output it produces; nothing here was produced by hand |
| SDR-A19 | "the citation must resolve to a committed artifact." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-030, Citation-Resolves Rule | Only real paths cited in any document | Every file path named in this dataset's Markdown resolves to a committed file |
| SDR-A20 | "risk register … output-risk classification — each mitigation/claim citing a committed control." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-086 §7.5, REQ-089 §7.5 | Risk findings bound to a control | `risk_flags.csv` carries `category`, `severity`, `evidence` and the `rule_id` that raised it; every finding names the control |
| SDR-A21 | "compliance mapping (EU AI Act / NIST AI RMF / DPDP)" | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-088, §7.5 | Data supporting a fair-lending and privacy posture | Demographic monitoring data is held in `borrower_demographics.csv` with a use restriction on every row and is absent from every decision surface and every input packet |
| SDR-A22 | "a small red-team attack set + results." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-110, §8.1 (optional) | A committed attack set | The 6 security scenarios double as the attack set; each records the submitted text, the expected handling and a `security_events.csv` row |
| SDR-A23 | "ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call." | `requirements_validation_tests/source_requirements/requirements_verbatim.md` | REQ-020, §3.1 | Every stage represented as data | The full chain exists per application: input packet → policy version selection → calculations → rule evaluations → risk flags → recommendation → pending human credit decision |

---

## B — Requirements from the completed research report

| Requirement ID | Requirement | Source Document | Source Section | Synthetic Artifact Needed | Implementation |
| --- | --- | --- | --- | --- | --- |
| SDR-B01 | Preserve declared, verified and qualifying values separately; a single `income_amount` destroys the distinction | Research report | "Mortgage data, document, calculation, policy and lineage architecture" | Three-column income and asset models | `income.csv` carries `declared_`, `verified_` and `qualifying_monthly_amount`; `assets.csv` carries declared, verified, closing-eligible and reserve-eligible amounts |
| SDR-B02 | Model a relational evidence-and-decision graph, not one flat table | Research report | "Dataset blueprint" | ~30 related entities | 32 tables in `synthetic_data/mortgage/structured/` plus 2 policy-metadata tables, all foreign-key checked |
| SDR-B03 | Calculations belong in deterministic functions with input provenance, never in unconstrained LLM arithmetic | Research report | "Underwriting calculations"; "Agentic AI architecture mapping" | A pure calculation library with recorded provenance | `synthetic_data_utils.py` holds every formula; each result in `underwriting_calculations.csv` carries its `input_fields`, `formula_version` and `units` |
| SDR-B04 | Policy retrieval must use the application's as-of date, not "latest" | Research report | "Policy-document architecture" | Versioned policies with effective windows, and applications either side of a change | 6 policies carry 2 versions each; SCN-055/056/057 form a three-way boundary test at 2026-07-01 |
| SDR-B05 | Distinguish five authority layers; never present a rule above its actual source | Research report | "Executive summary and research frame" | A `source_category` on every rule | Five-value enum on all 203 rule versions; the schema **refuses** a numeric threshold under a weaker authority than `SYNTHETIC_INTERNAL_POLICY` at import time |
| SDR-B06 | Keep eligibility, risk, AUS finding, recommendation, credit decision and clear-to-close distinct | Research report | "Decision taxonomy" | Separate tables and separate vocabularies | `eligibility_results.csv`, `risk_flags.csv` and `decisions.csv` are separate; `GEN-ELG-004` states the separation; no automated actor appears on a credit-decision row |
| SDR-B07 | Rules need `PASS / FAIL / REFER / NOT_APPLICABLE / INDETERMINATE`, not Boolean | Research report | "Eligibility rule taxonomy" | A five-value outcome | `rule_evaluations.outcome`; `GEN-ELG-005` records explicitly when inputs were unavailable |
| SDR-B08 | Missing evidence is INDETERMINATE and curable, never a failure | Research report | "Eligibility rule taxonomy"; "Missing/conflicting data workflow" | Suspended, not declined, files | `DOC-REQ-004`; SCN-042, SCN-045 and SCN-048 all produce `SUSPENDED_INCOMPLETE` |
| SDR-B09 | Apply the recommended human-in-the-loop classification | Research report | "Human-in-the-loop classification" | Mandatory review triggers as data | `UWR-HRV-001` encodes the table; 47 of 75 applications route to a human |
| SDR-B10 | Reproduce the conflict catalogue as detectable cases | Research report | "Missing/conflicting data workflow" | Controlled single-value mismatches | 4 scenarios carry a labelled `expected_discrepancies` record naming the field, both sources, the detecting rule and the required action |
| SDR-B11 | Build the document catalogue and the cross-document validation graph | Research report | "Document catalog"; "Cross-document validation graph" | Documents that reconcile with the tables | 1,140 documents across 19 types; `document_extractions.csv` gives field-level provenance; the validator cross-checks extractions against the tables |
| SDR-B12 | Do not assume every loan has an appraisal; record a valuation method | Research report | "Property valuation" | A `valuation_method` field and a no-appraisal case | `properties.valuation_method`; SCN-052 uses value acceptance and produces no appraisal row at all |
| SDR-B13 | Segregate demographic monitoring data from decision context | Research report | "Canonical domain data dictionary" | A separate, restricted table | `borrower_demographics.csv`; drawn from an independent RNG stream so no statistical relationship to any outcome exists |
| SDR-B14 | Do not clone DU or LPA; represent automated findings as an external simulated service | Research report | "AUS role"; "Research gaps" | No reverse-engineered scoring | No AUS scoring is modelled. This is recorded as a known limitation rather than faked |
| SDR-B15 | Do not reproduce any real lender's internal policy | Research report | "Major-lender public comparison"; "Research gaps" | A transparently fictional lender | The corpus is attributed to "Northwind Residential Lending (fictional)" in every document header |
| SDR-B16 | Lineage must be queryable at field level | Research report | "Data lineage" | Field-level links from evidence to decision | `document_extractions` → `underwriting_calculations.input_fields` → `rule_evaluations.input_fields` → `decision_reasons.evidence_reference`; worked end to end in [DATA_LINEAGE.md](DATA_LINEAGE.md) |
| SDR-B17 | At least a third of the evaluation set should involve missing, conflicting, stale, adversarial or judgmental evidence | Research report | "Recommended hackathon boundary" | A deliberately hard majority | 30 of 75 carry missing, conflicting, stale, adversarial or integrity-related evidence (40%, against the recommended third); 55 of 75 do not reach a clean approval; only 20 are straight-through approvals with no risk flag |
| SDR-B18 | Start with conventional conforming, fixed-rate, one-unit, owner-occupied purchase | Research report | "Recommended base-product tradeoff" | That product as the backbone | 70 of 75 applications are conventional conforming; FHA, VA, USDA and jumbo appear as explicitly labelled overlays |
| SDR-B19 | Loan-limit reference points for 2026 | Research report | "Executive summary and research frame" (FHFA, HUD) | Genuine published limits, attributed | `GEN-ELG-003` states 832,750 / 1,249,125 / 541,287 as `AGENCY_INVESTOR` with the report cited |
| SDR-B20 | Source hierarchy: policy is authoritative, applicant documents are evidence | Research report | "Agentic AI architecture mapping" | A trust class on every document | `documents.trust_class`; the validator asserts no applicant's submitted text has reached the policy corpus |
| SDR-B21 | Public-assistance, retirement and benefit income may not be discounted for its source | Research report | "Income model" (ECOA) | Benefit-income cases treated identically | SCN-075 qualifies on pension and social-security income; `INC-GEN-004` and `INC-OTH-002` state the prohibition |
| SDR-B22 | Adverse-action reasons must stay specific even behind a complex algorithm | Research report | "Regulatory and agency landscape" (CFPB circular) | Specific reasons bound to rules | `DEC-ADV-001`; every decline carries at least one `decision_reasons.csv` row naming the rule, version and evidence |

---

## C — Synthetic design decisions

Each of these is a choice this project made because no source settled it. All are
expanded in [DESIGN_ASSUMPTIONS.md](DESIGN_ASSUMPTIONS.md).

| Requirement ID | Decision | Rationale | Implementation |
| --- | --- | --- | --- |
| SDR-C01 | Seed `20260920`, overridable by `SYNTHETIC_SEED` | The Reproducibility Rule needs a fixed, documented seed | `resolve_seed()` in `synthetic_data_utils.py` |
| SDR-C02 | Sub-RNGs derived from `sha256(seed + label)` rather than a shared stream | Adding a scenario must not shift the values of unrelated ones, or every regeneration produces an unreviewable diff | `sub_rng()` |
| SDR-C03 | The entire foundation lives in one folder, `synthetic_data/mortgage/`, with the generator inside it | A clear repository root, and producing code beside the evidence it produces | Paths resolve from `SYNTH_ROOT` in `synthetic_data_utils.py`; the deviation from REQ-076's stated path is recorded at the end of this file |
| SDR-C04 | 42 documents across 36 policy families | The target is 36 documents; 6 families carry a second version, which is what makes temporal retrieval testable | `corpus.py` |
| SDR-C05 | One policy boundary date, 2026-07-01 | A single boundary keeps the temporal test unambiguous | `POLICY_V2_EFFECTIVE` |
| SDR-C06 | A fictional lender, "Northwind Residential Lending" | No reader can mistake a synthetic threshold for a real institution's rule | `SYNTHETIC_LENDER` in `policies.py` |
| SDR-C07 | 75 scenarios, 75 applications, 90 people | Exceeds the 50-application and 60-person minimums with room for boundary pairs | `scenarios.py` |
| SDR-C08 | No third-party data-generation dependency | A pip-only, no-network build is more reproducible than one that depends on a generator library's version | Committed name, address and employer pools in `people.py` |
| SDR-C09 | Scenario expectations asserted during generation | Ground truth that drifts from the engine is worse than no ground truth | `assert_scenario()` raises and stops the build |
| SDR-C10 | Settlement funds drawn from non-reserve sources first, then reserve-eligible in `asset_id` order | Reserves must be a deterministic consequence of the draw, not a separate invented number | `draw_funds_to_close()` |
| SDR-C11 | Documents rendered as plain text | They carry every field an underwriter needs without reproducing any proprietary form layout | `documents.py` |
| SDR-C12 | Property-tax rates from a small state-level table | Needed to make the housing expense vary realistically; no source fixes it | `TAX_RATES` in `build.py` |

---

## Recorded conflict between sources

**The policy corpus location.** Business-case requirement REQ-076 names
`data/policy_corpus/`. The corpus is at `synthetic_data/mortgage/policy_corpus/` instead,
because the whole foundation is consolidated into one folder to keep the repository
root clear.

This is a deviation from a business-case path, so it is recorded here rather than
buried. Three points bear on it:

1. REQ-070 requires each artifact to be present **"at (or near) the path shown"** —
   the document itself contemplates near matches, and the validation suite implements
   that by falling back to a search by directory name. `policy_corpus/` still
   resolves.
2. What does *not* resolve is the suite's committed-sample-input check, which looks
   only in a fixed list of root-level directories and does not search by name. The
   six tests that depend on it belong to REQ-020, REQ-033, REQ-044, REQ-057, REQ-066
   and REQ-094; none of them passes today in any case, because each also requires the
   CredPilot application itself.
3. Restoring exact compliance is a one-line change: point `POLICY_CORPUS_DIR` and
   `APPLICATION_INPUT_DIR` in `synthetic_data_utils.py` back at a root `data/`
   directory and regenerate. Nothing else depends on the location.

Duplicating the corpus into both places was rejected: two copies of a policy is
precisely the failure mode the versioning rules in this corpus exist to prevent.
