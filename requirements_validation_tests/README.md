# CredPilot — Independent Requirements Validation Suite

An external QA layer that checks a CredPilot implementation against the supplied requirements
document, and reports **PASS / FAIL plus a 0–100 fit score for every requirement**.

It is deliberately independent of CredPilot. It is not imported by the implementation, it does not
run the implementation's own test suite as if it were its own, and it never scans itself as
evidence.

```
Requirements Document
        ↓
Independent Requirements Tests      ← this folder
        ↓
CredPilot Implementation            ← --target
        ↓
Validation Execution
        ↓
PASS / FAIL / SCORE                 → reports/
```

---

## At a glance

| | |
| --- | --- |
| Source document | `source_document/Loan_Origination_Underwriting_Copilot_Merged.docx` |
| Requirement units extracted | **112** (`REQ-001` … `REQ-112`) |
| Test cases | **320** |
| Automated | **311** |
| Manual / non-automatable | **9** |
| Source requirements coverage | **100%** |
| Requirements with no test | **0** |

---

## Quick start

```bash
cd requirements_validation_tests

# Full validation run + report. --target defaults to the parent directory.
python runners/run_all_tests.py --target /path/to/CredPilot

# Same checks under pytest, one test per requirement test case.
python -m pytest -q --target /path/to/CredPilot

# A slice, while iterating on one area.
python runners/run_all_tests.py --suite governance
python runners/run_all_tests.py --requirement REQ-072 --requirement REQ-073

# Re-verify the verbatim baseline against the source document, character by character.
python traceability/verify_against_source.py
```

The target can also be given as `CREDPILOT_ROOT` in the environment, or as
`implementation_root` in `config/validation_config.json`. Precedence:
`--target` → `CREDPILOT_ROOT` → config → the suite's parent directory.

**Exit codes:** `0` all mandatory requirements passed · `1` at least one failed ·
`3` `REQUIREMENTS_BASELINE_MODIFIED` · `4` no test cases selected.

Requires Python 3.11+. The runner needs no third-party packages. `pytest` is needed only for the
pytest entry point, and `pandas`+`pyarrow` only to read a Parquet trace export — without them that
one check reports *why* it could not complete rather than passing on the file's existence.

---

## Layout

```
requirements_validation_tests/
├── README.md                          this file
├── BASELINE_REQUIREMENTS.md           baseline origin, guarantees and protection rules
├── bootstrap.py                       sys.path setup
├── conftest.py                        pytest wiring + baseline-hash gate
├── pytest.ini
│
├── source_document/
│   ├── Loan_Origination_Underwriting_Copilot_Merged.docx          the supplied document
│   ├── Loan_Origination_Underwriting_Copilot_Extracted_Text.docx  machine-readable cross-check
│   ├── EXTRACTION_NOTE.md             how the text was obtained, and its coverage map
│   └── pages/                         the 5 page images the .docx actually contains
│
├── source_requirements/
│   └── requirements_verbatim.md       THE SOURCE OF TRUTH (hashed)
│
├── traceability/
│   ├── build_traceability.py          regenerates everything derived
│   ├── verify_against_source.py       re-verifies the baseline against the document
│   ├── requirement_traceability_matrix.md / .json
│   ├── source_requirements_hash.txt   baseline SHA-256
│   └── coverage_audit.md              the independent second coverage pass
│
├── test_specs/<category>/             human-readable test specifications (generated)
│   affordability · auditability · eligibility · evaluation · functional · governance
│   integration · non_functional · observability · orchestration · policy · risk
│   security · underwriting · workflow
│
├── automated_tests/
│   ├── registry/                      THE TEST CASES - authoritative
│   │   ├── _helpers.py                the T() builder
│   │   ├── _shared_checks.py          composite checks
│   │   ├── _artifact_checks.py        checklist / evidence-format checks
│   │   ├── cases_core.py              REQ-001 .. REQ-043
│   │   ├── cases_acceptance.py        REQ-044 .. REQ-071
│   │   ├── cases_artifacts.py         REQ-072 .. REQ-095
│   │   └── cases_evidence.py          REQ-096 .. REQ-112
│   ├── _suite_runner.py               shared pytest plumbing
│   ├── static/ functional/ workflow/ integration/ governance/ api/
│
├── validators/
│   ├── requirement_loader.py          parses the verbatim baseline
│   ├── baseline_guard.py              hash verification
│   ├── evidence_validator.py          evidence primitives
│   ├── response_validator.py          runtime / black-box response validation
│   ├── requirement_validator.py       test model + PASS/FAIL + fit scoring
│   └── console.py
│
├── manual_evidence/
│   └── manual_attestations.json       human evidence channel; unattested ⇒ FAIL
│
├── config/validation_config.json      how to reach the implementation
└── reports/
    ├── latest_test_report.md
    └── latest_test_report.json
```

**Authoritative vs. derived.** Only two things are authoritative: `requirements_verbatim.md` (the
requirement text) and `automated_tests/registry/` (the test cases). The traceability matrix, the
`test_specs/` documents, the coverage audit and the manual-attestation template are all **generated**
— regenerate with `python traceability/build_traceability.py` rather than hand-editing them.

---

## How grading works

**Per test.** A test passes only when its check returns concrete evidence: a resolved path, a matched
line with line number, a record count, a `git ls-files` entry, or captured process output. A check
that finds nothing returns a factual "not found" and fails. A check that raises fails.

**Per requirement.**

* **PASS** — every test bound to the requirement passed. The implementation provided sufficient
  verifiable evidence that the original requirement is satisfied.
* **FAIL** — it did not.
* **Fit score** — the weighted percentage of that requirement's tests that passed:

  | Score | Meaning |
  | --- | --- |
  | 100 | fully satisfied with evidence |
  | 75–99 | substantial implementation, one or more explicit parts incomplete |
  | 50–74 | partially implemented |
  | 1–49 | minimal implementation related to the requirement |
  | 0 | absent, or no evidence |

  A high fit score never promotes a FAIL to a PASS. Partial implementation stays FAIL.

**Per project.** `Final Status` is `PASS` only when every `IMPLEMENTATION`-class requirement passes.
`OPTIONAL` and `ENGAGEMENT` requirements are executed, scored and reported in their own section —
see [`BASELINE_REQUIREMENTS.md`](BASELINE_REQUIREMENTS.md) for why that grouping exists and why it
does not weaken anything.

---

## Verification approach

**Black-box first.** The Section 5.1 acceptance criteria that describe observable behaviour are
driven through the CLI the document requires (`Interface | CLI (required)`), and the copilot's own
output is inspected. The run command is **discovered** from the implementation's `README.md` —
because the document requires a "single documented command" and a "Local-run runbook | README.md".
If no command can be discovered, those checks FAIL and say so. That is the correct verdict for the
runbook requirement; it is never substituted with a guessed command.

**Static inspection where the requirement is structural.** Architecture, configuration, source
structure, security controls and governance are checked by AST analysis and content inspection —
never by importing implementation code.

Verification types in use: `RUNTIME_TEST`, `API_TEST`, `INTEGRATION_TEST`, `WORKFLOW_TEST`,
`STATIC_TEST`, `CONFIGURATION_TEST`, `DOCUMENTATION_TEST`, `ARCHITECTURE_TEST`, `SECURITY_TEST`,
`GOVERNANCE_TEST`, `OBSERVABILITY_TEST`, `AUDITABILITY_TEST`, `DATA_VALIDATION_TEST`,
`OUTPUT_VALIDATION_TEST`, `NEGATIVE_TEST`, `BOUNDARY_TEST`.

**Runtime execution.** Enabled by default, and it does execute the target's own documented command
inside the target directory. Set `runtime.enabled` to `false` in `config/validation_config.json` to
disable it; the affected checks then report FAIL with the reason, rather than passing silently.

---

## Guardrails on the suite itself

* **Baseline hash gate.** Verified before every run. A mismatch stops validation with
  `REQUIREMENTS_BASELINE_MODIFIED`.
* **Registry invariants.** Enforced at import: unique well-formed test IDs, every test bound to a
  real requirement, the ID prefix matching that requirement, and every requirement covered.
* **Self-exclusion.** `requirements_validation_tests/` is on the scanner's excluded-directory list,
  so the suite can never satisfy a requirement with its own files.
* **Two self-checks.** `REQ-016-T01` asserts the suite does not score what the document excludes
  from evaluation; `REQ-069-T01` asserts every artifact on the document's checklist is actually
  covered by a test.
* **Requirement text is never stored twice.** It is read from the hashed baseline at run time.
* **The transcription is independently verified.** `traceability/verify_against_source.py` compares
  every requirement against the machine-readable rendering of the document, character by character,
  and re-verifies the six split paragraphs by reconstruction. See
  [`source_document/EXTRACTION_NOTE.md`](source_document/EXTRACTION_NOTE.md).

---

## Adding or changing tests

Add the case to the right `automated_tests/registry/cases_*.py`, then run
`python traceability/build_traceability.py`. The matrix, the specs and the coverage audit follow
automatically; the registry's import-time invariants will reject a malformed or unbound test.

New tests must derive strictly from the source text of the requirement they bind to. If the document
does not specify a value, use `unspecified_T(...)` and record `UNSPECIFIED_BY_REQUIREMENT` — do not
invent a threshold.

**Do not weaken a test to make the implementation pass.** That is the one change this suite exists
to prevent.
