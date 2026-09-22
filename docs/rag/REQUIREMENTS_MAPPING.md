# Requirements mapping — retrieval subsystem

Every requirement in `requirements_validation_tests/source_requirements/requirements_verbatim.md`
that bears on retrieval, mapped to what implements it for **each** lending
product, the evidence it produced, and the test that checks it.

Two kinds of statement appear below, and they are not interchangeable:

* **REQUIREMENT** — the source document says it. `REQ-0xx` cites the verbatim
  requirement file.
* **DECISION** — an architecture choice this team made to meet a requirement
  well. BM25, reciprocal rank fusion, the choice of embedding checkpoint and the
  choice of reranker are all decisions. The source document mandates
  *"Chroma or FAISS + Sentence-Transformers (local)"* (REQ-039) and nothing
  further about how retrieval is built. Nothing below claims otherwise.

Every path is repo-relative and resolves in a clean checkout.

---

## 1. Mandatory requirements

| ID | Requirement (verbatim, abridged) | Source | Mortgage | Education | Evidence | Test | Status |
|----|----------------------------------|--------|----------|-----------|----------|------|--------|
| REQ-035 | `Language / Agent Framework \| Python 3.11+ · LangGraph (MIT)` | §4 table | [src/graph.py](../../src/graph.py) — 20 nodes, conditional edges, `interrupt()`/resume | its own chain, sharing no node with mortgage | `data/memory/credpilot_checkpoints.sqlite` | [test_routing.py](../../tests/test_routing.py), [test_langgraph_rag_integration.py](../../tests/rag/test_langgraph_rag_integration.py) | **MET** — see deviation D4 |
| REQ-036 | `LLM Provider \| Google Gemini (API) — the only approved provider; not Claude` | §4 table | [src/llm.py](../../src/llm.py) — one module, one provider; no LLM in the retrieval path | same | `reports/eval_report.json` records the answering model | [test_stack_boundaries.py](../../tests/rag/test_stack_boundaries.py) | **MET** |
| REQ-037 | `Interoperability \| MCP Python SDK (stdio) + langchain-mcp-adapters` | §4 table | [mcp_server/server.py](../../mcp_server/server.py) — 11 tools, 10 resources, 6 prompts; host and client in [src/mcp_host/](../../src/mcp_host/) | same server, product-scoped tools | `logs/mcp_transcript.jsonl` | [test_mcp_capabilities.py](../../tests/test_mcp_capabilities.py) (35 tests, real subprocess), [test_mcp_rag_integration.py](../../tests/rag/test_mcp_rag_integration.py) | **MET** — see deviation D5 |
| REQ-047 (AC-04) — routing | *"identifies each application's intent and handles it with the right capability"* | §5.1 | [src/supervisor.py](../../src/supervisor.py) — six routes, deterministic-first | same Supervisor, education chain | `reports/eval_report.json` → `supervisor_routing_accuracy` | [test_supervisor.py](../../tests/test_supervisor.py) (62 tests) | **MET** |
| REQ-047 (AC-04) — clarification | *"ambiguous … requests are clarified … not mishandled"* | §5.1 | `clarification_node` + LangGraph `interrupt()`, capped at 2 rounds | same | `traces/phoenix_spans.jsonl` → the `clarify` run | `test_an_ambiguous_request_pauses_and_resumes_on_the_same_thread` | **MET** |
| NFR-04 | *"async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions)"* | §5.2 | [src/resilience.py](../../src/resilience.py) + async MCP client | same | `degradations` on graph state; `reports/eval_report.json` → `runs_with_a_degraded_tool_call`; two deliberately malformed packets traced in `traces/trace_summary.json` under `kind: "malformed"` — one refused for its missing as-of date, one the dated control that proceeds | [test_resilience.py](../../tests/test_resilience.py) | **MET** |
| — | Web application, CLI preserved | — | [src/web/](../../src/web/) — FastAPI + SSE over the same compiled graph | same | — | [test_web_api.py](../../tests/test_web_api.py) | **MET** |
| REQ-039 | `Retrieval \| Chroma or FAISS + Sentence-Transformers (local)` | §4 table | `credpilot_mortgage_policies` | `credpilot_education_policies` | `data/vectorstore/index_manifest.json` | [test_index_build.py](../../tests/rag/test_index_build.py) | **MET** |
| REQ-044 (AC-01) | *"retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied"* | §5.1 | effective-date-aware; boundary triple passes | effective-date-aware; single version per policy | `eval/results/retrieval_eval.json` | [test_temporal_retrieval.py](../../tests/rag/test_temporal_retrieval.py) | **MET** |
| REQ-045 (AC-02) | *"computes affordability … and flags any policy breach with the threshold it failed"* | §5.1 | [src/calculations.py](../../src/calculations.py) + [src/rules.py](../../src/rules.py) | same modules, product-specific formulas | `reports/assessments/` | `test_the_breach_names_the_threshold_it_failed` | **MET** |
| REQ-046 (AC-03) | *"a decline or high-value case is routed for human review rather than auto-decided"* | §5.1 | `recommendation_node` + DEC-REC-002 | `recommendation_node` + EDU-GOV-002 | `logs/agent_actions.jsonl` | `test_a_decline_is_always_routed_to_a_human` | **MET** |
| REQ-047 (AC-04) | *"ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled"* | §5.1 | `PRODUCT_CLARIFICATION_REQUIRED`, `OUT_OF_SCOPE_REQUEST` | same | `eval/results/retrieval_eval_cases.jsonl` | [test_product_isolation.py](../../tests/rag/test_product_isolation.py), [test_security.py](../../tests/rag/test_security.py) | **MET** |
| REQ-049 (AC-06) | *"attempts to inject instructions or access another applicant's data are refused, and sensitive data … is never exposed in answers or logs"* | §5.1 | 6 committed adversarial cases, all detected | patterns apply to both corpora | `logs/tool_calls.jsonl` | [test_security.py](../../tests/rag/test_security.py), [test_pii_logging.py](../../tests/rag/test_pii_logging.py) | **MET** |
| REQ-050 (AC-07) | `logs/tool_calls.jsonl … written by committed logging middleware; tool names reconcile with the agent/MCP code` | §5.1 | [src/observability/tool_logging.py](../../src/observability/tool_logging.py) | same middleware | `logs/tool_calls.jsonl` | [test_rag_tool_contract.py](../../tests/rag/test_rag_tool_contract.py) | **MET** |
| REQ-076 | `Agentic-RAG tool \| src/tools/rag_tool.py + data/policy_corpus/ \| retrieval-in-the-loop over a synthetic lending-policy corpus` | §7.1 table | [src/tools/rag_tool.py](../../src/tools/rag_tool.py) | same tool, product-routed | `data/policy_corpus/corpus_registry.json` | [test_rag_tool_contract.py](../../tests/rag/test_rag_tool_contract.py) | **MET** — see deviation D1 |
| REQ-077 | `Phoenix instrumentation \| src/observability/tracing.py \| tracer wired into the run path (called, not just imported)` | §7.2 | 11 named spans across the retrieval path | same spans | `traces/phoenix_spans.jsonl` | [test_observability.py](../../tests/rag/test_observability.py) | **MET** |
| REQ-031 | *"Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext."* | §3.4 | [src/guardrails/redaction.py](../../src/guardrails/redaction.py) | same | `logs/tool_calls.jsonl` and `logs/agent_actions.jsonl` scanned | [test_pii_logging.py](../../tests/rag/test_pii_logging.py) | **MET** |
| REQ-030 | *"Citation-Resolves Rule … the citation must resolve to a committed artifact."* | §3.4 | `POL-DTI-001 v2.0 rule DTI-CONV-001` | `POL-002 EDU-UW-001` | `data/vectorstore/index_integrity.json` | [test_citations.py](../../tests/rag/test_citations.py) | **MET** — validity 1.00 |
| REQ-029 | *"Evidence-in-Repo Rule … an evidence artifact with no producing code … is heavily discounted."* | §3.4 | every artifact written by a committed script | same | `eval/results/retrieval_eval.json`, `data/vectorstore/index_manifest.json` | [test_index_build.py](../../tests/rag/test_index_build.py) | **MET** |
| REQ-033 | *"Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command"* | §3.4 | `scripts/build_policy_indexes.py` | same command builds both | [RUNBOOK.md](RUNBOOK.md) | [test_index_build.py](../../tests/rag/test_index_build.py) | **MET** |
| REQ-032 | *"Open-Source & Gemini-Only Rule … no Docker or external database service required"* | §3.4 | Chroma is an embedded library | same | `requirements.txt` | [test_stack_boundaries.py](../../tests/rag/test_stack_boundaries.py) | **MET** |
| REQ-066 | *"Use only synthetic loan applications and lending policies you generate."* | §6.1 | `synthetic_data/mortgage/` | `synthetic_data/education/` | corpus registry | [test_index_build.py](../../tests/rag/test_index_build.py) | **MET** |

---

## 2. Architecture decisions (not requirements)

Each of these is a choice made to meet the requirements above well. None is
mandated by the source document, and each is justified by committed measurement.

| Decision | What it is | Why | Evidence |
|----------|-----------|-----|----------|
| **D-01** Chroma over FAISS | REQ-039 permits either | Chroma stores metadata alongside vectors, which the effective-date filter and the citation builder both need; FAISS would need a second store beside it | [src/rag/vectorstore.py](../../src/rag/vectorstore.py) |
| **D-02** One database, two collections | Not specified by REQ-039 | Product isolation becomes structural rather than a filter that has to be applied correctly every time | [test_product_isolation.py](../../tests/rag/test_product_isolation.py) |
| **D-03** `intfloat/e5-base-v2` | REQ-039 says "Sentence-Transformers (local)"; the checkpoint is ours | Benchmarked against 3 alternatives on both products; it beat the expected starting model | [EMBEDDING_BENCHMARK.md](EMBEDDING_BENCHMARK.md), `eval/results/embedding_benchmark.json` |
| **D-04** BM25 alongside dense | Not mentioned in the source document | Policy text is full of exact identifiers (`DTI-CONV-001`, `HCLTV`, `I-94`) that embeddings recover unreliably | [RETRIEVAL_ABLATION.md](RETRIEVAL_ABLATION.md) |
| **D-05** Reciprocal rank fusion | Not mentioned in the source document | A BM25 score and a cosine similarity are not on one scale; fusing ranks avoids inventing a calibration | [test_retrieval_components.py](../../tests/rag/test_retrieval_components.py) |
| **D-06** Local cross-encoder rerank | Not mentioned in the source document | Measured gain over fusion alone | [RERANKER_BENCHMARK.md](RERANKER_BENCHMARK.md), `eval/results/reranker_benchmark.json` |
| **D-07** Rule-level chunking | Not mentioned in the source document | A threshold separated from the rule that sets it is unusable evidence | [test_chunking.py](../../tests/rag/test_chunking.py) |
| **D-08** Narrow funnel (15/15/12/10) | Not mentioned in the source document | Measured: widening it *lowered* recall (0.9826 → 0.9593) and cost 4× latency | `eval/results/pipeline_sweep.json` |
| **D-09** No LLM query rewriting | Not mentioned in the source document | A deterministic synonym table already closes the terminology gap; an LLM in the retrieval path would make results non-reproducible (REQ-033) | [src/rag/expansion.py](../../src/rag/expansion.py) |

---

## 3. Stack boundaries

The runtime uses **no** Anthropic, Claude, OpenAI, Cohere, Voyage, Pinecone,
Weaviate, Qdrant, Milvus, Azure AI Search, OpenSearch or Elasticsearch, and no
hosted reranking service. Embeddings and reranking are local
`sentence-transformers` models; the vector store is embedded Chroma.

Gemini is the only model provider, and every call to it goes through
[src/llm.py](../../src/llm.py). There is exactly **one** such call in a normal
assessment — the narrative node, which explains a decision already made. Nothing
in retrieval, ranking, filtering, arithmetic or the verdict involves a model, so
the pipeline that produces the recommendation is deterministic end to end and the
evaluation is reproducible (REQ-033).

Enforced by [tests/rag/test_stack_boundaries.py](../../tests/rag/test_stack_boundaries.py),
which scans every runtime module's imports and the dependency manifest.

Claude Code was used as the development assistant for this work. No Claude model
is called at runtime and no `ANTHROPIC_API_KEY` is read.

---

## 3a. Agent, evaluation and governance

The rows above cover retrieval. These cover the graph that uses it, the
evaluation that measures it, and the documents that govern it.

| ID | Requirement (verbatim, abridged) | Mortgage | Education | Evidence | Test | Status |
|----|----------------------------------|----------|-----------|----------|------|--------|
| REQ-074 | tiered memory: short-term + long-term/semantic | [src/memory/](../../src/memory/) | same store, subject-scoped | `logs/memory_test.log` | [test_memory_persistence.py](../../tests/test_memory_persistence.py) | **MET** |
| REQ-075 | *"cross-session recall test with committed output log"* | written in one session, read by a store built only from the path | same | `logs/memory_test.log` | `test_memory_survives_a_new_store_on_the_same_file` | **MET** |
| REQ-080 | context engineering: write / select / compress / isolate | [src/context/](../../src/context/) | same | `context_record` on graph state | [test_context_engineering.py](../../tests/test_context_engineering.py) | **MET** |
| REQ-097 | `Evaluation report \| reports/eval_report.json + harness \| DeepEval … hallucination + faithfulness/relevance; LLM-as-judge` | 75 golden cases | 20 golden cases | `reports/eval_report.json`, `reports/eval_cases.jsonl` | [eval/agent/](../../eval/agent/) | **MET** |
| REQ-098 | `Golden signals \| reports/golden_signals.json \| latency, tokens in/out, cost estimate, accuracy, hallucination rate` | derived per product | derived per product | `reports/golden_signals.json` | [build_golden_signals.py](../../scripts/build_golden_signals.py) | **MET** |
| REQ-099 | Dashboard: `reports/dashboard.png` plus `reports/dashboard_data.csv`, with a Phoenix screenshot | one chart, both products | same | `reports/dashboard.png`, `reports/dashboard_data.csv`, `reports/phoenix_spans.csv`, [docs/assets/phoenix-traces.png](../assets/phoenix-traces.png) — the `credpilot` project's span table, 636 traces, P50 8.00 ms | [build_dashboard.py](../../scripts/build_dashboard.py), [capture_phoenix_screenshot.py](../../scripts/capture_phoenix_screenshot.py) | **MET** |
| REQ-046 (AC-03) | *"a decline or high-value case is routed for human review rather than auto-decided"* | `UWR-HRV-001` routing table, band read from the rule | `EDU-GOV-002` outcome vocabulary | `recommendation.review_triggers` | [test_review_triggers.py](../../tests/test_review_triggers.py) | **MET** |
| — | risk register | OWASP LLM Top 10 + NIST AI RMF, 33 rows | same | [docs/risk-register.md](../risk-register.md) | — | **MET** |
| — | model card | [docs/model-card.md](../model-card.md) | same | — | — | **MET** |
| — | compliance mapping | EU AI Act / NIST AI RMF / DPDP | same | [docs/compliance.md](../compliance.md) | — | **MET** |
| — | output risk tiers | three tiers with gating | same | [docs/output-risk.md](../output-risk.md) | — | **MET** |
| — | failure analysis | twenty real failures with before/after; four (F-11, F-14, F-17, F-20) cite machine evidence re-resolved by `scripts/verify_evidence_citations.py` | same | [docs/failure-analysis.md](../failure-analysis.md) | [test_documentation.py](../../tests/rag/test_documentation.py), [test_observability_signals.py](../../tests/test_observability_signals.py) | **MET** |

### Loop and cost control

Not a numbered requirement, but an agentic system without it is a liability.
Two independent guards, because they fail differently: an in-state
`step_budget` of 32 lets a node **halt cleanly with a reason a human can read**,
and LangGraph's `recursion_limit` of 60 is the external backstop for a cycle
that never reaches a node able to check anything. A third bound caps the one cycle the graph contains: clarification is allowed two rounds before the thread goes to a person. A normal assessment uses 11 and a clarified conversation 13. Covered by
[tests/test_loops.py](../../tests/test_loops.py).

---

## 4. Deviations

### D1 — `data/policy_corpus/` holds the registry, not copies of the documents

**Requirement.** REQ-076 names `src/tools/rag_tool.py + data/policy_corpus/`.
REQ-070 qualifies this: *"Each artifact must be present at (or near) the path
shown."*

**What exists.** `src/tools/rag_tool.py` is at the exact path. The policy
documents are committed at `synthetic_data/mortgage/policy_corpus/` (42 files)
and `synthetic_data/education/policy_corpus/` (12 files) — the layout the
existing synthetic-data foundation established, with one folder per lending
product because the two corpora use incompatible identifier taxonomies and ship
separate generators, schemas and golden sets.

`data/policy_corpus/` holds
[`corpus_registry.json`](../../data/policy_corpus/corpus_registry.json) and a
README: the machine-generated inventory of every source document the indexes were
built from, with product, policy id, version, effective window, declared rule
ids, SHA-256 and canonical path.

**Why not copy the documents.** Two copies of every lending policy means two
content hashes to keep in step. The provenance chain from a citation to a
committed source file is checked by hash
([test_index_build.py](../../tests/rag/test_index_build.py)); duplicating the
corpus would let that chain drift silently, which is the failure the Citation-
Resolves Rule (REQ-030) exists to prevent.

**Assessment.** The requirement's substance — a synthetic lending-policy corpus,
committed, that the RAG tool retrieves over — is met in full and is larger than
the checklist implies (two corpora, 54 documents, 275 rules). The deviation is in
where the bytes live. It is flagged here rather than papered over.

### D2 — the education corpus has no policy versions to select between

**Requirement.** REQ-044 (AC-01) requires the *current* applicable policy.

**What exists.** Mortgage publishes six policies at two versions each with a
2026-07-01 boundary; retrieval selects by underwriting as-of date and the
boundary triple `APP-000055` / `APP-000056` / `APP-000057` proves it. Education
publishes one version per document with an effective date and no expiry or
supersession chain.

**What was done.** Effective-date filtering is applied to education too — a
2024 as-of date correctly returns `NO_APPLICABLE_POLICY` rather than the newest
document. Version selection has nothing to select between. No fake version
history was added to make the two products look symmetrical.
See [TEMPORAL_RETRIEVAL.md](TEMPORAL_RETRIEVAL.md).

### D3 — Gemini is wired, and the committed credential has no quota

**Requirement.** REQ-036 mandates Google Gemini as the only model provider.

**What exists.** `langchain-google-genai` is wired for the narrative node, the
policy-answer path, the optional Supervisor fallback and the DeepEval judge. The
key in `.env` is a correctly-formed Gemini API key and reaches the service; it
returns **`402 RESOURCE_EXHAUSTED — "Your prepayment credits are depleted"`**
from every model tried (`gemini-flash-latest`, `gemini-3.5-flash`,
`gemini-pro-latest`, `gemini-flash-lite-latest`).

**Impact, stated precisely rather than waved at.**

*Unaffected.* Retrieval, calculation, rule evaluation, routing, guardrails, MCP,
the graph, the web UI and every deterministic metric contain no model call — by
design, and because `POL-DTI-001` DTI-CALC-002 forbids a model producing an
underwriting figure. Every number in `eval/results/` and every deterministic
figure in `reports/eval_report.json` was produced without any LLM.

*Degraded, visibly.* The narrative falls back to the deterministic summary and
marks itself `available: false` with the reason attached. A policy answer falls
back to quoting the governing rules. Neither is silent.

*Not measurable at all.* The DeepEval judged metrics — faithfulness,
hallucination, answer relevancy. They are reported as `null` with
`judge.available: false` and the reason, never as zero and never carried over
from an earlier run. `--judge-all` refuses to produce a report at all in this
state rather than publishing one labelled "every case judged" that judged none.

*Also not measurable.* Token counts and cost. `reports/golden_signals.json`
records `model_calls_recorded_no_tokens: true` and says that $0.00 is an absence
of measurement rather than an efficiency result.

**What this changes about reading the evidence.** Any judged figure still
present in a committed report is from an earlier run against an earlier
architecture and is labelled with its own `generated_at_utc` and `run_id`. The
deterministic figures are current.

### D4 — product isolation is enforced by graph topology, not by a condition

**Requirement.** REQ-047 (AC-04) and the product-isolation requirement.

**What exists.** The compiled graph contains two complete product chains —
`mortgage_agent → mortgage_policy_retrieval → mortgage_eligibility →
mortgage_risk → mortgage_recommendation`, and the same five for education —
generated from shared factories and sharing **no node**. The Supervisor routes
to one of the two entry points and nothing connects them.

**Why not one shared chain with a domain check.** A shared worker guarded by
`if domain is MORTGAGE` is only as correct as that condition stays, and it has
to stay correct in five places. Two chains cannot be got wrong: there is no
sequence of routing decisions that reaches education retrieval from a mortgage
node, because no such edge exists.
[`test_no_edge_crosses_between_the_two_products`](../../tests/test_routing.py)
asserts it against the compiled graph rather than against intent.

**Cost of the deviation.** Ten nodes where five would do, and a longer node list
in every trace. Worth it.

### D7 — two validator findings that are false positives, and what happened to the rest

`requirements_validation_tests` scans committed files for prohibited content by
regex. Two of its remaining hits are matches on text that says the opposite of
what the scanner concluded. They are recorded here rather than worked around, because a
finding nobody explains gets re-investigated by the next reader.

**Three more were dropped from this table once the thing they described
changed.** One was REQ-109, the FastAPI streaming endpoint the validator looks
for at `src/api/`. The note here used to argue that renaming a package to
match an assumption the source document does not make would be the wrong
reason to rename it — which was a fair argument against a *rename*, and not an
argument against the **split** that was done instead: `src/api/` is now the
HTTP API as a mountable `APIRouter`, and `src/web/` the application that
serves it alongside the page. The API can be mounted without a browser UI,
which is worth having on its own.

**The other two were dropped once the check they came from was
rewritten.** They were the provider and database-service hits inside
`tests/rag/test_stack_boundaries.py`, and the note here used to say they were
unavoidable because a test that forbids a thing has to name it. That was true
of a deny-list and is not true in general: the file is now an **allow-list** —
every third-party import must be in `APPROVED_RUNTIME_PACKAGES`, every
environment read in `APPROVED_CREDENTIALS` or `APPROVED_ENVIRONMENT`, every URL
scheme in `APPROVED_URL_SCHEMES` — which is strictly stronger, because it also
catches a provider nobody thought to ban. It names nothing prohibited, so the
hits went away as a side effect rather than as the goal.

**A further finding was investigated and turned out to be a real defect**,
which is the reason this section does not say "six". An earlier revision of this document
dismissed 81 "unmasked payment card numbers" as the same kind of shape
collision and noted that the ones in
`eval/results/retrieval_eval_cases.jsonl` "predate this work". Seventy-nine of
them were nDCG values. A `policy_ndcg@10` of `0.444097…`, printed to full
precision, ends in sixteen digits beginning with a 4 — and a decimal point is
a word boundary, so a payment-card detector reads those digits as a Visa
number. Roughly every other 17-significant-digit float in `[0, 1)` does this.
(The literal is not reproduced here; writing a card-shaped run into the
repository to explain why not to would be self-defeating.)

That was fixable at the source and is fixed — `round_for_serialization` in
[`eval/retrieval/metrics.py`](../../eval/retrieval/metrics.py) rounds per-case
floats on the way to disk, in both evaluation harnesses. Aggregation still sees
full precision, so no published figure moved; every aggregate in this repo was
already rounded to four places, so the per-case files were the inconsistent
ones. `tests/rag/test_pii_logging.py` now fails if an over-precise float comes
back.

The lesson is worth keeping next to the table below: a scan reporting eighty
false positives is a scan nobody reads, and a real leak would have been sitting
in the middle of them. Dismissing a class of finding wholesale is how that
happens.

| Finding | What actually matched | Why it is a false positive |
|---|---|---|
| "real credit-bureau integration" (REQ-066) | the word **"Reprodu*cibil*ity"** | The bureau pattern includes `cibil` — an Indian credit bureau — and it matches inside that word. Three hits, all in comments about the Reproducibility Rule. |
| "unmasked payment-card number" (REQ-031) | a Phoenix **span id** | Span ids are 16 hex characters; about one in 1,800 comes out all digits, and a 16-digit run beginning with 4 is indistinguishable by shape from a Visa number. `traces/phoenix_spans.jsonl` contained one. CredPilot's own redaction handles this positionally — a value under a `span_id` key is a span id — but a byte-level scan of the file cannot. |

Neither is fixable without weakening a real control or falsifying an artifact. The two remaining payment-card hits are span ids, in
`traces/phoenix_spans.jsonl` and its CSV projection; CredPilot's own scan
handles those by column and by key — see `scan_csv` and `_ID_FIELD_VALUE` in
[`src/guardrails/redaction.py`](../../src/guardrails/redaction.py) — but an
independent byte-level scan of the file cannot, and should not be asked to.

### D8 — memory is built here, not LangMem

**Requirement.** REQ-038, §4 Technology & Framework Stack, Memory row:
`langgraph-checkpoint-sqlite (SQLite file) + LangMem`.

**What exists.** `langgraph-checkpoint-sqlite` is used as named — `SqliteSaver`
is the graph's checkpointer, and `data/memory/credpilot_checkpoints.sqlite` is
what it writes. **LangMem is not installed**, and the tiered memory is
implemented in [`src/memory/`](../../src/memory/).

**Status: PARTIAL.** One of the two named components is present. Recorded as a
deviation rather than reported as met.

**Why.** The memory this system needs is mostly a set of *refusals*, and they
are domain rules rather than storage behaviour:

* a prior decision is not evidence for a new application, so it is refused by
  kind rather than stored and ranked;
* policy is retrieved with an effective date rather than remembered, because a
  remembered threshold is a threshold that has silently expired;
* a credit figure goes stale on a clock, and the staleness is the point.

A general memory library stores and recalls well; what it cannot do is know
that `POL-DTI-001 v1.0` stopped governing on 2026-07-01. Recall is also scoped
to one subject and `forget()` erases a data principal completely in one
operation, which is a DPDP obligation rather than a memory feature.

Cross-session recall is demonstrated rather than asserted:
`logs/memory_test.log` is written by `tests/test_memory_persistence.py`, which
writes in one session and reads back in a second store built only from the
file path.

### D6 — the guardrails are built here, not Guardrails-AI or LLM Guard

**Requirement.** REQ-042, §4 Technology & Framework Stack, Security row:
`Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv`.

**What exists.** Presidio and python-dotenv are used as named. **Neither
Guardrails-AI nor LLM Guard is installed**, and the input/output guardrails are
implemented in [`src/guardrails/`](../../src/guardrails/).

**Status: PARTIAL.** Two of the three named components are present; the first is
not. Recorded as a deviation rather than reported as met.

**Why.** Both libraries are general-purpose scanners over free text. What
CredPilot's guardrails do is mostly not that:

* the injection patterns are matched against a *known corpus* and are tuned on
  six committed adversarial packets plus the conversational surface — a generic
  scanner has no knowledge of `POL-SEC-001` or of which phrasings this corpus
  actually contains;
* `_PROTECTED_IDENTIFIERS` exempts CredPilot's own citation grammar from
  redaction, which is the fix for F-2 and which no general scanner could know to
  do. It is precisely the thing a generic library got wrong when Presidio's
  loose recognisers destroyed every citation in the audit trail;
* the output guardrail enforces *human-review routing* and validates figures
  against the calculation record, neither of which is text scanning at all.

Adding a heavyweight dependency to satisfy the row, while continuing to rely on
the code that actually does the work, would make the manifest say something the
system does not do. The honest position is this row.

**What a reviewer should check instead.** That the *substance* is there:
`tests/rag/test_security.py`, `tests/rag/test_pii_logging.py` and
`tests/test_supervisor.py` cover 15 injection patterns, cross-applicant and
bulk-access refusal, PII redaction at every write boundary, and the
committed-artifact scan.

### D5 — the requested MCP capability set exceeds what the source document asks for

**Requirement.** REQ-037 and §7.1 ask for *"≥ 2 tools + 1 resource; consumed via
langchain-mcp-adapters; committed tool-call transcript."*

**What exists.** Eleven tools, ten resources, six prompts, and all six MCP
capability families — tools, resources, prompts, elicitation, sampling and
roots — implemented and tested against a real server subprocess.

**Why the extra.** Requested explicitly for this build. The two compatibility
families are labelled as such rather than presented as load-bearing: CredPilot
does **not** depend on MCP sampling for generation (it would put the model
provider outside the host's control, and REQ-036 makes the provider a
requirement), and roots are **not** an authorization mechanism. Both say so in
`mcp_server/capabilities.py`, in the `credpilot://system/capabilities` resource,
and in their own responses.

---

## 5. Measured position

From `data/vectorstore/index_integrity.json` and `eval/results/retrieval_eval.json`:

| Metric | Target | Mortgage | Education | Macro |
|--------|--------|----------|-----------|-------|
| Source documents indexed | all | 42 / 42 | 12 / 12 | — |
| Declared rules indexed | all | 174 / 174 | 72 / 72 | — |
| `cross_product_contamination_rate` | 0.00 | 0.0000 | 0.0000 | **0.0000** |
| `citation_validity` | 1.00 | 1.0000 | 1.0000 | **1.0000** |
| `policy_recall@5` (authored) | ≥ 0.95 | 1.0000 | 1.0000 | **1.0000** |
| `rule_recall@5` (authored) | ≥ 0.90 | 0.9720 | 0.9931 | **0.9826** |
| `rule_mrr@10` (authored) | — | 0.8905 | 0.8847 | 0.8876 |
| `version_accuracy` (mortgage) | 1.00 | 1.0000 | n/a | **1.0000** |
| `wrong_version_rate` (mortgage) | 0.00 | 0.0000 | n/a | **0.0000** |
| `no_result` | — | 0.0000 | 0.0000 | **0.0000** |
| `routing_correct` | 1.00 | 1.0000 | 1.0000 | **1.0000** |
| Temporal-boundary accuracy | 1.00 | 6 policies × 2 dates | n/a | **1.0000** |
| Prompt-injection policy override | 0.00 | 0 / 6 succeeded | 0 / 2 succeeded | **0.0000** |

Models in force: embedding `intfloat/e5-base-v2`, reranker
`cross-encoder/ms-marco-MiniLM-L-6-v2`, both selected by the benchmarks in
`eval/results/`.

Current figures are whatever the committed result files under [`eval/results/`](../../eval/results/) say — chiefly `eval/results/retrieval_eval.json`; this table
is refreshed from them by `eval/retrieval/run_retrieval_eval.py`.
