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
| REQ-035 | `Language / Agent Framework \| Python 3.11+ · LangGraph (MIT)` | §4 table | [src/graph.py](../../src/graph.py) | same graph, product-routed | `data/memory/credpilot_checkpoints.sqlite` | [test_langgraph_rag_integration.py](../../tests/rag/test_langgraph_rag_integration.py) | **MET** |
| REQ-036 | `LLM Provider \| Google Gemini (API) — the only approved provider; not Claude` | §4 table | [src/llm.py](../../src/llm.py) — one module, one provider; no LLM in the retrieval path | same | `reports/eval_report.json` records the answering model | [test_stack_boundaries.py](../../tests/rag/test_stack_boundaries.py) | **MET** |
| REQ-037 | `Interoperability \| MCP Python SDK (stdio) + langchain-mcp-adapters` | §4 table | [mcp_server/server.py](../../mcp_server/server.py) — 3 tools, 3 resources | same server, product-scoped tools | `logs/mcp_transcript.jsonl` | [test_mcp_rag_integration.py](../../tests/rag/test_mcp_rag_integration.py) | **MET** |
| REQ-039 | `Retrieval \| Chroma or FAISS + Sentence-Transformers (local)` | §4 table | `credpilot_mortgage_policies` | `credpilot_education_policies` | `data/vectorstore/index_manifest.json` | [test_index_build.py](../../tests/rag/test_index_build.py) | **MET** |
| REQ-044 (AC-01) | *"retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied"* | §5.1 | effective-date-aware; boundary triple passes | effective-date-aware; single version per policy | `eval/results/retrieval_eval.json` | [test_temporal_retrieval.py](../../tests/rag/test_temporal_retrieval.py) | **MET** |
| REQ-045 (AC-02) | *"computes affordability … and flags any policy breach with the threshold it failed"* | §5.1 | [src/calculations.py](../../src/calculations.py) + [src/rules.py](../../src/rules.py) | same modules, product-specific formulas | `reports/assessments/` | `test_the_breach_names_the_threshold_it_failed` | **MET** |
| REQ-046 (AC-03) | *"a decline or high-value case is routed for human review rather than auto-decided"* | §5.1 | `recommendation_node` + DEC-REC-002 | `recommendation_node` + EDU-GOV-002 | `logs/agent_actions.jsonl` | `test_a_decline_is_always_routed_to_a_human` | **MET** |
| REQ-047 (AC-04) | *"ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled"* | §5.1 | `PRODUCT_CLARIFICATION_REQUIRED`, `OUT_OF_SCOPE_REQUEST` | same | `eval/results/retrieval_eval_cases.jsonl` | [test_product_isolation.py](../../tests/rag/test_product_isolation.py), [test_security.py](../../tests/rag/test_security.py) | **MET** |
| REQ-049 (AC-06) | *"attempts to inject instructions or access another applicant's data are refused, and sensitive data … is never exposed in answers or logs"* | §5.1 | 6 committed adversarial cases, all detected | patterns apply to both corpora | `logs/tool_calls.jsonl` | [test_security.py](../../tests/rag/test_security.py), [test_pii_logging.py](../../tests/rag/test_pii_logging.py) | **MET** |
| REQ-050 (AC-07) | `logs/tool_calls.jsonl … written by committed logging middleware; tool names reconcile with the agent/MCP code` | §5.1 | [src/observability/tool_logging.py](../../src/observability/tool_logging.py) | same middleware | `logs/tool_calls.jsonl` | [test_rag_tool_contract.py](../../tests/rag/test_rag_tool_contract.py) | **MET** |
| REQ-076 | `Agentic-RAG tool \| src/tools/rag_tool.py + data/policy_corpus/ \| retrieval-in-the-loop over a synthetic lending-policy corpus` | §7.1 table | [src/tools/rag_tool.py](../../src/tools/rag_tool.py) | same tool, product-routed | `data/policy_corpus/corpus_registry.json` | [test_rag_tool_contract.py](../../tests/rag/test_rag_tool_contract.py) | **MET** — see deviation D1 |
| REQ-077 | `Phoenix instrumentation \| src/observability/tracing.py \| tracer wired into the run path (called, not just imported)` | §7.2 | 11 named spans across the retrieval path | same spans | `traces/phoenix_spans.jsonl` | [test_observability.py](../../tests/rag/test_observability.py) | **MET** |
| REQ-031 | *"Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext."* | §3.4 | [src/guardrails/redaction.py](../../src/guardrails/redaction.py) | same | `logs/*.jsonl` scanned | [test_pii_logging.py](../../tests/rag/test_pii_logging.py) | **MET** |
| REQ-030 | *"Citation-Resolves Rule … the citation must resolve to a committed artifact."* | §3.4 | `POL-DTI-001 v2.0 rule DTI-CONV-001` | `POL-002 EDU-UW-001` | `data/vectorstore/index_integrity.json` | [test_citations.py](../../tests/rag/test_citations.py) | **MET** — validity 1.00 |
| REQ-029 | *"Evidence-in-Repo Rule … an evidence artifact with no producing code … is heavily discounted."* | §3.4 | every artifact written by a committed script | same | `eval/results/`, `data/vectorstore/` | [test_index_build.py](../../tests/rag/test_index_build.py) | **MET** |
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
| REQ-099 | `Dashboard \| reports/dashboard.png + dashboard_data.csv` | one chart, both products | same | `reports/dashboard.png` | [build_dashboard.py](../../scripts/build_dashboard.py) | **MET** |
| REQ-046 (AC-03) | *"a decline or high-value case is routed for human review rather than auto-decided"* | `UWR-HRV-001` routing table, band read from the rule | `EDU-GOV-002` outcome vocabulary | `recommendation.review_triggers` | [test_review_triggers.py](../../tests/test_review_triggers.py) | **MET** |
| — | risk register | OWASP LLM Top 10 + NIST AI RMF, 26 rows | same | [docs/risk-register.md](../risk-register.md) | — | **MET** |
| — | model card | [docs/model-card.md](../model-card.md) | same | — | — | **MET** |
| — | compliance mapping | EU AI Act / NIST AI RMF / DPDP | same | [docs/compliance.md](../compliance.md) | — | **MET** |
| — | output risk tiers | three tiers with gating | same | [docs/output-risk.md](../output-risk.md) | — | **MET** |
| — | failure analysis | eight real failures with before/after | same | [docs/failure-analysis.md](../failure-analysis.md) | [test_documentation.py](../../tests/rag/test_documentation.py) | **MET** |

### Loop and cost control

Not a numbered requirement, but an agentic system without it is a liability.
Two independent guards, because they fail differently: an in-state
`step_budget` of 24 lets a node **halt cleanly with a reason a human can read**,
and LangGraph's `recursion_limit` of 40 is the external backstop for a cycle
that never reaches a node able to check anything. A normal run uses 7. Covered by
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

### D3 — Gemini is wired but unusable with the committed credential

**Requirement.** REQ-036 mandates Google Gemini as the only model provider.

**What exists.** `langchain-google-genai` is wired for the narrative node. The
credential in `.env` is an OAuth-style token (`AQ.Ab8…`) rather than a Gemini API
key (`AIza…`) and returns `401 UNAUTHENTICATED` from every model.

**Impact on this subsystem: none.** Retrieval, calculation and rule evaluation
are deterministic and contain no model call — by design, and because
`POL-DTI-001` DTI-CALC-002 forbids a model producing an underwriting figure.
Every number in `eval/results/` was produced without any LLM. The narrative
rationale and the DeepEval LLM-as-judge suite need a working key.

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

Current figures are whatever the committed `eval/results/*.json` say; this table
is refreshed from them by `eval/retrieval/run_retrieval_eval.py`.
