# CredPilot — engineering completion report

**System** Loan Origination & Underwriting Copilot · BC-AAIE-HACK-02
**Branch** `chore/unify-synthetic-data` · **Commits** `52aa9ba`, `e6a1ba8`
**Evaluation run** `9fff3fc1` · **Trace run** `4ac6f741`

Every figure below is read out of a committed artifact produced by committed
code. Where something could not be measured, this report says so and names the
blocker rather than substituting a plausible number.

---

## 1. Architecture implemented

```
    request ──▶ intake ──▶ input_guardrails ──▶ supervisor
                                                    │
      ┌──────────┬──────────┬───────────┬───────────┴──┬─────────────┐
   GENERAL    CLARIFY    MORTGAGE   EDUCATION_LOAN  HUMAN_REVIEW  OUT_OF_SCOPE
      │      interrupt()     │            │            │             │
      │      + resume (≤2)   ▼            ▼            │             │
      │              policy_retrieval  policy_retrieval │             │
      │                      ▼            ▼            │             │
      │                 eligibility   eligibility      │             │
      │                      ▼            ▼            │             │
      │                    risk         risk           │             │
      │                      ▼            ▼            │             │
      │              recommendation  recommendation    │             │
      │                      └──────┬─────┘            │             │
      │                          narrative ────────────┤             │
      └─────────────────────────────┴──────────────────┴─────────────┘
                                    ▼
                          final_response ──▶ output_guardrails ──▶ END
```

**20 nodes. Two product chains sharing none of them.**

* **Product isolation is topological.** Subgraph-as-node was tried first and
  rejected: LangGraph duplicates accumulating channels across the boundary, so
  one product's evidence turned up in the other's state. There is now no edge
  between the chains, so isolation does not depend on a runtime check being
  correct. The fresh-clone run shows it — `mortgage_agent → mortgage_policy_
  retrieval → mortgage_eligibility → …` and the education equivalent, with no
  shared node between them.
* **Supervisor** (`src/supervisor.py`) — six routes, deterministic-first (term
  lists, packet shape, identifier prefixes). The model fallback is off by
  default (`CREDPILOT_SUPERVISOR_MODEL=0`), so routing behaves identically with
  and without an API key and the unit tests spend nothing. Terms that do not
  discriminate — `cosigner`, `refinance`, `dti` — are held in a shared list and
  never used to pick a product.
* **Clarification and resume** — `interrupt()` / `Command(resume=…)` on the
  same thread, capped at `MAX_CLARIFICATION_ROUNDS = 2`, then a person.
* **MCP** — `mcp_server/` is an independently runnable FastMCP server;
  `src/mcp_host/client.py` is the host's client. Six capability families:
  11 tools, 10 resources, 6 prompts, elicitation (typed two-field schema, no
  free-text field, declines with no responder), sampling (served through Gemini
  only, refused from any other family), 4 roots. **Roots are not an
  authorization mechanism** and the server says so in its own response.
* **Retrieval** is unchanged in shape — BM25 + `intfloat/e5-base-v2` + Chroma,
  RRF fusion, cross-encoder rerank, effective-date filtering, citation
  resolution — plus one addition: `fetch_rules()`, a by-id lookup that skips the
  ranking funnel for rules the engine knows it needs. Temporal selection still
  applies to it.
* **HTTP surface** — [`src/api/`](../src/api/) is the API as a mountable
  `APIRouter`: the JSON and Server-Sent-Events endpoints and the streaming
  machinery, importable without a browser UI. [`src/web/`](../src/web/) is the
  application that includes that router and serves `index.html` and the static
  assets; `python -m src.web` runs it.
* **Identifiers cannot be mistaken for account numbers.** A span id is 16 hex
  characters and roughly one in 1,800 comes out all decimal digits, which is a
  valid card shape — so a committed trace export randomly acquired a string
  every payment-card scanner reported as an unmasked account number.
  `UnambiguousIdGenerator` in [`src/observability/tracing.py`](../src/observability/tracing.py)
  rejection-samples those, so the guarantee holds by construction rather than
  by luck.
* **Resilience** (`src/resilience.py`) — a deadline and a bounded, jittered
  retry on every boundary call. A fault that will recur identically raises
  `NonRetryableError` and stops after one attempt. Failures come back as a
  `ToolFailure` **value**, so a node degrades and records the loss instead of
  raising inside a checkpoint.
* **Rule engine** — 21 deterministic families, 14 mortgage and 7 education.
  Every threshold is read out of retrieved policy text; none is hard-coded. A
  rule that was not retrieved returns `INDETERMINATE`, never `FAIL`.

## 2. Files created

**Runtime**

| Path | What it is |
|---|---|
| `src/supervisor.py` | Six routes, deterministic-first, checkpoint-safe decision object |
| `src/resilience.py` | Deadlines, bounded jittered retries, `ToolFailure` as a value |
| [`src/mcp_host/client.py`](../src/mcp_host/client.py) | CredPilot as MCP **host**: connect, discover, call, plus sampling / elicitation / roots callbacks |
| `mcp_server/capabilities.py` | The declared surface and `capability_report()` |
| [`src/rule_families/mortgage_ext.py`](../src/rule_families/mortgage_ext.py) | GEN-ELG, DOC-REQ, EMP-CNT, CRD-EVT, CRD-DLQ, AST-SRC, VAL-APR, JMB-ELG |
| [`src/rule_families/education_ext.py`](../src/rule_families/education_ext.py) | EDU-UW, EDU-RG, EDU-COS, EDU-INTL |
| `src/guardrails/validation.py` | The output guardrail, moved out of `graph.py` |
| [`src/api/routes.py`](../src/api/routes.py) | The HTTP API: JSON and SSE endpoints as a mountable router |
| [`src/web/app.py`](../src/web/app.py) and its `static/` assets | The application that mounts the API and serves the page |

**Evidence and verification**

| Path | What it is |
|---|---|
| `scripts/verify_evidence_citations.py` | Re-resolves every machine-evidence citation against the artifact it names |
| `scripts/capture_phoenix_screenshot.py` | Captures the Phoenix UI; refuses rather than writing a placeholder |
| [`docs/evidence/f14-intake-spans.jsonl`](evidence/f14-intake-spans.jsonl) | Frozen verbatim extract of the run F-14 cites |
| [`docs/assets/phoenix-traces.png`](assets/phoenix-traces.png) and [`web-ui-assessment.png`](assets/web-ui-assessment.png) | The two screenshots |
| `reports/phoenix_spans.csv` | Span-level data behind the dashboard |

**Tests** — `test_supervisor.py`, `test_conversation.py`, `test_mcp_capabilities.py`,
`test_resilience.py`, `test_rule_families.py`, `test_web_api.py`,
`test_observability_signals.py`, `test_evidence.py`, `test_output_validation.py`

## 3. Files modified

99 files in the first commit, 16 in the second. The substantial ones:

| File | Δ |
|---|---|
| `src/graph.py` | +1939 / −291 |
| `mcp_server/server.py` | +1094 / −77 |
| `docs/failure-analysis.md` | +644 / −11 |
| `scripts/build_golden_signals.py` | +586 / −217 |
| `README.md` | +275 / −88 |
| `src/cli.py` | +221 / −4 |
| `src/narrative.py` | +184 / −0 |
| `scripts/export_traces.py` | +170 / −1 |
| `eval/agent/run_agent_eval.py` | +163 / −6 |
| [`docs/rag/RUNBOOK.md`](rag/RUNBOOK.md) and [`REQUIREMENTS_MAPPING.md`](rag/REQUIREMENTS_MAPPING.md) | +393 / −82 |
| [`src/rules.py`](../src/rules.py), [`review_triggers.py`](../src/review_triggers.py), [`rag/pipeline.py`](../src/rag/pipeline.py), [`tools/rag_tool.py`](../src/tools/rag_tool.py) | +191 / −8 |
| [`src/guardrails/sanitize.py`](../src/guardrails/sanitize.py), [`redaction.py`](../src/guardrails/redaction.py) | +115 / −5 |
| [`src/observability/tracing.py`](../src/observability/tracing.py), [`tool_logging.py`](../src/observability/tool_logging.py) | +107 / −2 |

## 4. Tests executed

```bash
python -m pytest tests/ -q --tb=short -p no:randomly      # the whole suite
python scripts/verify_evidence_citations.py               # cited artifacts still say it
python scripts/check_published_figures.py                 # quoted metrics match
python scripts/verify_doc_tables.py                       # transcribed tables match
python requirements_validation_tests/runners/run_all_tests.py   # all six suites
```

## 5. Test results

| Suite | Result |
|---|---|
| `pytest tests/` | **952 passed, 0 failed** |
| Evidence citations | **6 / 6 resolve** |
| Published figures | 19 quoted headline metrics, all match |
| Documentation tables | every transcribed figure matches its result file |
| Requirements validator (6 suites, 320 tests) | **101 / 112 requirements, 97% fit** — IMPLEMENTATION 85/90, ENGAGEMENT 12/18, OPTIONAL **4/4**. See §9 |
| Fresh clone | indexes rebuilt (16/16 integrity checks), both products assessed, all evidence present, 6/6 citations resolve |

Four failures were found and fixed during the final run, and each was worth
having:

* `test_pii_logging` — two Phoenix **span ids** that came out all digits and
  Visa-shaped. Fixed with a column-aware CSV scan, plus a test proving the
  exemption cannot be stretched.
* `test_eval_harness` — asserted `0 < affected` "because 0 means the check is
  broken". Education is now 0 because all seven families are implemented. The
  guard was replaced by one that withdraws a cited family and requires it to
  reappear, rather than forcing the measurement to under-report.
* `test_observability_signals` — F-14 cites spans the regenerated export no
  longer contains, because the fix works. Resolved against the live export ∪
  `docs/evidence/`.
* `test_resilience` — **the test was wrong, not the code.** `ConnectionError`
  is retryable with `max_attempts=2`, so one raise was retried and succeeded;
  recording a degradation would have reported a loss that did not happen. Split
  into a persistent fault (must degrade) and a transient one (must not).

## 6. Final DeepEval metrics

`reports/eval_report.json`, run `9fff3fc1`, DeepEval 4.2.3, 95 cases, **0
errors**, 0 halted.

| Metric | Macro | Mortgage (75) | Education (20) |
|---|---|---|---|
| supervisor_routing_accuracy | **1.0** | — | — |
| response_validation_pass_rate | **1.0** | — | — |
| citation_validity | **1.0** | 1.0 | 1.0 |
| citation_recall | 0.7095 | 0.7731 | 0.6458 |
| outcome_accuracy (expressible) | 0.6991 | 0.6761 | 0.7222 |
| outcome_accuracy_all_cases | 0.6450 | — | — |
| directional_agreement | 0.6766 | 0.6533 | 0.7000 |
| human_review_agreement | 0.6933 | 0.6933 | — |
| narrative_faithfulness_deterministic | **1.0** | — | — |
| unsupported_claim_rate | **0.0** | — | — |
| runs_with_a_degraded_tool_call | 0 | — | — |
| steps_taken_mean | 11.46 of a 32 budget | — | — |

**Judged metrics are `null`, not zero.** `judge_faithfulness`,
`judge_answer_relevancy`, `judge_hallucination_rate` and
`judge_hallucination_score` were not measured; `judged_cases` is 0. See §11.

Macro rather than pooled, because mortgage contributes 75 cases to education's
20 and a pooled mean would be a mortgage score wearing a system's name.

## 7. Retrieval metrics

`eval/results/retrieval_eval.json` — **all targets met**.

| Metric | Value | Target |
|---|---|---|
| citation_validity | 1.0 | 1.0 |
| version_accuracy | 1.0 | 1.0 |
| wrong_version_rate | 0.0 | — |
| cross_product_contamination | 0.0 | 0.0 |
| routing_correct | 1.0 | — |
| policy_recall@5 | 1.0 | 0.95 |
| rule_recall@5 | 0.9826 | 0.90 |
| policy_mrr@10 | 0.9414 | — |
| rule_mrr@10 | 0.8876 | — |

Re-run under the current code to confirm `fetch_rules()` did not perturb
ranking: it did not. Index integrity 16/16 with per-document SHA-256 agreement.

## 8. Phoenix golden signals

`reports/golden_signals.json`, from **1,119 spans over 318 traces**. Latency in
milliseconds, operational figures from spans and quality figures from the
evaluation — each block states its source.

| Span kind | n | p50 | p95 | max |
|---|---|---|---|---|
| request (root) | 318 | 8.5 | 531.6 | 13,623.8 |
| thinking (model) | 11 | 1.0 | 2.0 | 1,990.5 |
| acting (graph nodes) | 211 | 1.0 | 76.6 | 523.1 |
| tool (tool boundary, MCP) | 185 | 7.7 | 550.7 | 13,623.8 |
| retrieval (pipeline stages) | 712 | 3.0 | 453.4 | 10,000.1 |

Tokens **0** across 11 model-call spans, with
`model_calls_recorded_no_tokens: true` recorded beside it — the calls did not
reach the provider, so every cost figure is $0.00 **by absence of measurement**
rather than because generation was free. Error span rate 0.0.

The export covers both products, all six Supervisor routes, and two
deliberately malformed packets, so NFR-04's degraded paths are traced rather
than asserted. Greetings and the injection attempt are recorded with **0
evidence chunks** — the claim "a greeting does not invoke RAG" is a trace
anyone can open.

Dashboard: `reports/dashboard.png` + `reports/dashboard_data.csv` (35 rows).
Phoenix UI: `docs/assets/phoenix-traces.png` — the `credpilot` project's span
table, 636 traces, P50 8.00 ms, P99 0.93 s.

## 9. AC-01 … AC-12

| # | Status | Implementation | Evidence |
|---|---|---|---|
| **AC-01** | **PASS** | effective-date-aware retrieval; every `RuleEvaluation` carries its citation | version_accuracy 1.0, wrong_version_rate 0.0; citation_validity 1.0 over 95 cases |
| **AC-02** | **PASS** | `src/calculations.py` + `src/rules.py`; thresholds read from retrieved text | every breach in `reports/eval_cases.jsonl` carries its threshold and citation |
| **AC-03** | **PASS** | `recommendation_node` + `src/review_triggers.py`; no edge carries a decline to END | `logs/agent_actions.jsonl`; the fresh-clone decline routed to `human_review` |
| **AC-04** | **PASS** | `src/supervisor.py`, six routes; `clarification_node` with interrupt/resume | supervisor_routing_accuracy **1.0**; the `clarify` trace asks and resumes; greeting and out-of-scope runs record 0 evidence |
| **AC-05** | **PASS** | `src/memory/` tiered store, thread-scoped conversation state | `logs/memory_test.log` — written in session 1, read back by a store built only from the file path in session 2 |
| **AC-06** | **PASS** | 15 injection patterns; `src/guardrails/redaction.py` | 6 adversarial packets detected; 9 typed attack phrasings caught and 10 legitimate questions left clean; injection turn routes to HUMAN_REVIEW with 0 evidence |
| **AC-07** | **PASS** | `src/observability/tool_logging.py`, `transport` field | `logs/tool_calls.jsonl` — 129 records, **0** under the retired `mcp:` prefix, every name resolving to a committed tool |
| **AC-08** | **PASS** | `docs/failure-analysis.md`, 20 failures | 4 carry machine evidence (F-11, F-14, F-17, F-20); `verify_evidence_citations.py` resolves **6/6** and runs as a test |
| **AC-09** | **PASS** | `build_golden_signals.py` reads spans, not the eval | `golden_signals.json` with the thinking/acting/tool split, `dashboard.png`, `dashboard_data.csv`, `phoenix_spans.csv`, `docs/assets/phoenix-traces.png` |
| **AC-10** | **PASS** | `input_guardrails_node` / `output_guardrails_node` on every path, refusals included | `logs/agent_actions.jsonl`, 209 records |
| **AC-11** | **PASS** | risk register (34 risks), model card, compliance mapping, output-risk | every mitigation names a file or a test; `check_published_figures.py` and `verify_doc_tables.py` run as tests |
| **AC-12** | **PARTIAL** | DeepEval 4.2.3 over all 95 cases; routing / loop-cascade / tool-contract tests all present and green | **judged hallucination and faithfulness could not be measured** — see §11.1 |

## 10. NFR-01 … NFR-06

| # | Status | Evidence |
|---|---|---|
| **NFR-01** | **PASS** | `.env` gitignored (`.gitignore:2`) and untracked; a scan of every tracked file for `AIza…`, `sk-…`, `ghp_…` and PEM headers returns nothing; `.env.example` committed |
| **NFR-02** | **PASS** | `python -m src.web` / `python -m src.cli assess …`; `python scripts/regenerate_evidence.py` regenerates traces and the evaluation from one code state; `synthetic_data/` holds both products' inputs |
| **NFR-03** | **PASS** | `quarantine()` at intake; applicant text rendered last inside a labelled fence and never read by the rule engine |
| **NFR-04** | **PASS** | `src/resilience.py`; two malformed packets traced under `kind: "malformed"` — the undated one refused with a reason, the dated control assessed; transient vs persistent faults asserted in both directions |
| **NFR-05** | **PASS** | [`tests/rag/test_pii_logging.py`](../tests/rag/test_pii_logging.py) scans every committed data and documentation file under `logs/`, `traces/`, `reports/` and `eval/results/` — JSON, JSON Lines, CSV, logs and Markdown alike |
| **NFR-06** | **PASS** | every artifact names its producer — `golden_signals.json` carries `generated_by`; the screenshot has `capture_phoenix_screenshot.py`; the frozen extract has `docs/evidence/README.md` |

### Requirements validator

All six suites, 320 tests: **101 of 112 requirements pass, 97% overall fit** —
IMPLEMENTATION 85/90, ENGAGEMENT 12/18, OPTIONAL **4/4**. The run began this
work at 86% on a two-suite partial run and moved 86 → 91 → 94 → 97 as the
findings below were worked through.

**`final_status` reads FAIL, and it always will.** That is not a residual
defect list; it is the validator's design. Requirements whose source text
fixes no value to verify against are registered through a helper whose
`pass_condition` is the literal string *"Not reachable: the document supplies
nothing to verify against."* Four tests use it, and three of those — REQ-035,
REQ-045, REQ-046 — are IMPLEMENTATION class. Since final status is gated on
IMPLEMENTATION being complete, **the maximum reachable IMPLEMENTATION score is
87/90**, and no amount of implementation work changes that.

The 11 remaining, by what would actually be needed:

| Count | Requirements | Blocker |
|---|---|---|
| 4 | REQ-011, REQ-035, REQ-045, REQ-046 | Unreachable by design — the validator's own helper never passes |
| 5 | REQ-008, REQ-009, REQ-010, REQ-012, REQ-013 | A human signature on facts about the engagement: duration, team size, review mode, the Excel report, the grade bands. Prepared for signing in `requirements_validation_tests/manual_evidence/manual_attestations.json`, with the verbatim source text and what would count as evidence for each; the three fields the validator reads are deliberately blank |
| 1 | REQ-011 | No GitLab remote is configured. Adding one that does not exist would be a fabrication |
| 2 | REQ-038, REQ-042 | LangMem and Guardrails-AI / LLM Guard are named in the stack table and not used — deviations D8 and D6, kept deliberately |

Nothing here is an unexplained gap. Ten of the eleven are either impossible
from inside the repository or a documented, argued deviation; the eleventh is
waiting on a signature.

## 11. Remaining limitations

**11.1 No judged evaluation.** `GOOGLE_API_KEY` is well-formed and reaches
Google, which answers `402 RESOURCE_EXHAUSTED — "Your prepayment credits are
depleted"` for every model including `gemini-pro-latest` and
`gemini-flash-latest`. What was done instead of guessing: every `judge_*`
metric is `null` rather than 0; `judged_cases` is 0; `--judge-all` **exits
non-zero and writes nothing** rather than publishing a report labelled "every
case judged" that judged none; all 95 narratives are the deterministic
fallback, counted as `narratives_deterministic_fallback: 95` beside
`narratives_model_generated: 0`; and two deterministic counterparts are
published in place of the judge —
`narrative_faithfulness_deterministic: 1.0` and `unsupported_claim_rate: 0.0`,
computed by checking every claim in a narrative against the evidence it cites,
with no model involved. AC-12 is **PARTIAL** because the requirement names
hallucination and faithfulness *from a judge*, and a deterministic substitute
is a different measurement, not the same one.

**11.2 Outcome accuracy is 0.6991, and the reason is measured.** 15 of 75
mortgage cases turn on a rule family with no code evaluating it against a
threshold. Those rules are retrieved, ranked and cited; the comparison is what
is missing. `rule_coverage` in the eval report names the affected share. This
is the ceiling the accuracy figure sits under and the first thing to extend.

**11.3 Nine education golden citations name a rule that does not exist** in the
corpus — a golden-set defect recorded in `docs/rag/DATA_QUALITY_FINDINGS.md`,
counted separately so it is not charged against retrieval.

**11.4 Accuracy measures agreement with a synthetic generator** (R-01), not
correctness. A systematic error shared by the generator and the system would
score as success. No production decision should rest on these numbers.

**11.5 The checkpoint store grows without bound** (R-28): 793 MB across 622
threads and 7,864 rows, about 1.3 MB per run, with no retention policy. Linear
in runs, so a deployment fills a disk in weeks and the failure arrives as a
write error mid-assessment.

**11.6 Six golden cases expect `APPROVE_WITH_CONDITIONS`**, which
`recommendation_node` cannot emit (R-24). Reported as
`outcome_accuracy_all_cases` beside `outcome_accuracy` rather than folded in.

**11.7 LangMem (D8) and Guardrails-AI / LLM Guard (D6) are named in the stack
table and not used.** The memory and guardrail layers are built here, for
reasons recorded in `docs/rag/REQUIREMENTS_MAPPING.md`. Both are PARTIAL, not
met.

**11.8 The fresh-clone check does not prove a clean-machine `pip install`.** It
proves the committed tree is complete and self-contained — a clone with nothing
but what git tracks builds its indexes and assesses both products, with no
reliance on an untracked file or an absolute path. Dependency resolution is
checked separately with `pip install --dry-run`, because installing torch and
transformers into a throwaway venv tests PyPI rather than this repository.

**11.9 Two structural changes were made late, and both were triggered by the
validator.** `src/api/` was split out of `src/web/`, and the OpenTelemetry id
generator was replaced. Each stands on its own — a mountable API, and
identifiers that cannot be confused with account numbers — but neither would
have been done this week without a check failing first. Both are covered by
tests and by a working run of the whole system; they are recorded here because
a reader deciding how much to trust them should know what prompted them.
