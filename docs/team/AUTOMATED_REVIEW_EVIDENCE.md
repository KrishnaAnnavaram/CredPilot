# Automated review — what the team runs, and what it produces

> **This is the team's own automated validation.** It is **not** the official
> Virtusa Hackathon review. `REQ-010` describes an automated review of the
> submitted repository against the 7-category / 100-mark Hackathon Rubric,
> performed by the evaluator. That rubric is **not in this repository**, has
> **not been run**, and nothing below is a substitute for it.
>
> `REQ-010` therefore stays open until the official evaluation actually happens.
> This document exists to show that the *deliverable* is built to be reviewed
> automatically — every claim is checkable by running a command.

Team: **Krishna Annavaram** and **Mahesh Rajendra**.

---

## Why this matters for an automated review

The requirement says the review is *"scored entirely from committed evidence in
the repository. No live demo judging."* That places a burden on the deliverable
rather than on the reviewer: every claim has to be checkable without anyone
demonstrating anything.

Two rules are enforced throughout, and both are machine-checked:

* **Evidence-in-Repo** — every committed measurement is produced by committed
  code, regenerable in one command.
* **Citation-Resolves** — every citation in every document resolves to a
  committed artifact. An artifact present in the working tree but *not committed*
  counts as missing.

---

## 1. Requirements validator — 112 requirements

```bash
python requirements_validation_tests/runners/run_all_tests.py
```

Grades the implementation against a **hash-locked** extract of the requirements
document. The baseline is checksummed, and validation **stops** if the baseline
changed — so a failing implementation cannot be made to pass by editing the
requirements.

| Produces | |
|---|---|
| [`requirements_validation_tests/reports/latest_test_report.json`](../../requirements_validation_tests/reports/latest_test_report.json) | Machine-readable, per-requirement, with collected evidence |
| [`requirements_validation_tests/reports/latest_test_report.md`](../../requirements_validation_tests/reports/latest_test_report.md) | Readable form |

**Current result:** 103 / 112 requirements, 98% weighted fit, IMPLEMENTATION
87/90. Exit code 1 — `final_status` reads FAIL by design, because three
unreachable checks are IMPLEMENTATION-class. See
[`final_gap_analysis.md`](../../requirements_validation_tests/reports/final_gap_analysis.md).

### Derived reports

```bash
python requirements_validation_tests/traceability/classify_failures.py
python requirements_validation_tests/traceability/build_source_matrix.py
python requirements_validation_tests/traceability/build_gap_analysis.py
python requirements_validation_tests/manual_evidence/build_checklist.py
```

The first of those asserts `passed + failed == total` and refuses to publish if
any failing test is unclassified — it has already blocked a report during this
project for exactly that reason.

---

## 2. Full test suite

```bash
python -m pytest -q
```

**970 tests, 970 passed, 0 failed, 0 skipped.** Roughly 25–40 minutes.

By area:

| Area | Tests | Area | Tests |
|---|---|---|---|
| RAG | 439 | Memory | 28 |
| Agent / supervisor / eval harness | 134 | Observability | 27 |
| Guardrails + output validation | 36 | API / web | 19 |
| MCP | 35 | Tool contracts | 15 |
| Routing | 33 | Loops | 10 |

---

## 3. Evidence regeneration

```bash
python scripts/regenerate_evidence.py
```

Regenerates every committed measurement from the current code in one pass:
indexes → funnel sweep → ablation → retrieval evaluation → trace export → agent
evaluation → golden signals → dashboard.

Each step's exit code is checked. On failure the script **names the stage,
returns non-zero, and stops** — a later step never runs on a failed upstream, and
no success message is printed after a traceback. This was verified by injecting a
failing step.

| Produces | |
|---|---|
| `traces/phoenix_spans.jsonl`, `traces/trace_summary.json` | Phoenix spans |
| `logs/tool_calls.jsonl`, `logs/agent_actions.jsonl`, `logs/mcp_transcript.jsonl` | Machine-generated logs |
| `reports/eval_report.json`, `reports/golden_signals.json` | Evaluation and operational signals |
| `reports/dashboard_data.csv`, `reports/dashboard.png` | Dashboard |
| `eval/results/retrieval_eval.json`, `eval/results/retrieval_ablation.json`, `eval/results/pipeline_sweep.json` | Retrieval evaluation, ablation, sweep |

---

## 4. Evidence-integrity verifiers

```bash
python scripts/verify_evidence_citations.py   # 6/6 citations resolve
python scripts/verify_doc_tables.py           # every transcribed table figure matches
python scripts/check_published_figures.py     # 19 headline metrics match measurements
```

All three exit 0. These are what stop a document quoting a number the result files
no longer support — they have caught real drift in this project, most recently 35
stale figures across four documents after a regeneration.

---

## 5. DeepEval — LLM-as-judge

```bash
python -m eval.agent.run_agent_eval --judge-all
```

DeepEval with **Google Gemini as the only judge** (`REQ-036` permits one
provider): faithfulness, hallucination, answer relevancy, plus deterministic
metrics — outcome accuracy, directional agreement, citation validity, citation
recall, human-review agreement, unsupported-claim rate.

**Current state — stated plainly:** every `judge_*` metric in
[`reports/eval_report.json`](../../reports/eval_report.json) is **`null`**. The
API key is well-formed and reaches Google, but every Gemini model returns
`402 RESOURCE_EXHAUSTED — "Your prepayment credits are depleted"`. The report
records:

> NO CASE WAS JUDGED. The judge was unreachable for this run, so every `judge_*`
> metric below is null. They are not zero and they are not carried over from an
> earlier run — they were not measured.

The 95-case deterministic evaluation ran in full and is unaffected.

### Requirements judge

```bash
python eval/requirements_judge.py
```

A second judge that grades each requirement against the evidence collected for
it. Same state: writes `null` and exits 3 rather than inventing a grade.

---

## 6. Secret scan and submission readiness

```bash
git ls-files | grep -E "^\.env$"                    # must return nothing
git ls-files -z | xargs -0 grep -lE "AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9]{20,}"
git status --porcelain                              # must be empty before pushing
```

`NFR-01` and `NFR-05` are covered by
[`tests/rag/test_security.py`](../../tests/rag/test_security.py) and
[`tests/rag/test_pii_logging.py`](../../tests/rag/test_pii_logging.py), which scan
every committed data and documentation file for identifier- and account-shaped
strings. Current result: **zero findings**.

---

## 7. One command for a reviewer in a hurry

```bash
python -m pytest -q
python requirements_validation_tests/runners/run_all_tests.py
python scripts/verify_evidence_citations.py
```

Tests, requirement grade, and proof that every cited artifact resolves.

---

## What this does **not** establish

| Requirement | Why it stays open |
|---|---|
| `REQ-010` | The **official** automated rubric review is the evaluator's event. The team validating its own work is not that event, and the rubric is not in this repository. |
| `REQ-012` | The per-team Excel report is the **reviewer's** output. [`reports/CredPilot_Internal_Peer_Review.xlsx`](../../reports/CredPilot_Internal_Peer_Review.xlsx) is internal preparation with the same five sheets, and is labelled as such. |
| `REQ-013` | Grade bands are applied by the **evaluator**. The bands are recorded; whether they were applied is not the team's fact to assert. |

No command in this document, run any number of times, changes any of the three.
