# CredPilot retrieval subsystem

Multi-product agentic RAG over two isolated synthetic lending-policy corpora.

| | Mortgage | Education |
|---|---|---|
| Policy documents | 42 | 12 |
| Rules | 203 (174 distinct ids across versions) | 72 |
| Indexed chunks | 329 | 101 |
| Chroma collection | `credpilot_mortgage_policies` | `credpilot_education_policies` |
| Versioned policies | 6, boundary 2026-07-01 | none (one version each) |
| Applications | 75 | 200 |
| Golden cases | 75 | 20 |

---

## Start here

```bash
pip install -r requirements.txt
python scripts/build_policy_indexes.py
python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json
```

Full instructions: **[RUNBOOK.md](RUNBOOK.md)**.

---

## Documents

| | |
|---|---|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | how it is built and why — product isolation, chunking, the pipeline, the module map |
| **[REQUIREMENTS_MAPPING.md](REQUIREMENTS_MAPPING.md)** | every retrieval requirement → implementation → evidence → test, per product; requirements separated from architecture decisions; deviations stated |
| **[TEMPORAL_RETRIEVAL.md](TEMPORAL_RETRIEVAL.md)** | effective-date-aware version selection, the boundary triple, the education limitation |
| **[RETRIEVAL_ABLATION.md](RETRIEVAL_ABLATION.md)** | what each layer is measurably worth, including the layers that are worth nothing |
| **[EMBEDDING_BENCHMARK.md](EMBEDDING_BENCHMARK.md)** | four local checkpoints, both products, and the choice |
| **[RERANKER_BENCHMARK.md](RERANKER_BENCHMARK.md)** | three cross-encoders against a no-reranker baseline |
| **[../failure-analysis.md](../failure-analysis.md)** | twenty real failures with evidence, root cause, fix and before/after; F-11, F-14, F-17 and F-20 cite a run id, a Phoenix span or a tool-log record, re-resolved by `scripts/verify_evidence_citations.py` |
| **[DATA_QUALITY_FINDINGS.md](DATA_QUALITY_FINDINGS.md)** | defects found in the committed datasets and how each is handled |
| **[RUNBOOK.md](RUNBOOK.md)** | build, run, evaluate, trace, troubleshoot |

---

## The three properties this is built around

### Product isolation is structural, not a filter

A mortgage query cannot return an education policy because it never searches the
education index. The domain router resolves the product from structured facts
*before* retrieval and that decision picks the collection. Where the product
cannot be resolved, retrieval returns `PRODUCT_CLARIFICATION_REQUIRED` and
searches nothing.

`cross_product_contamination_rate` = **0.0000**, measured over every indexed
chunk and over cross-product bait queries in both directions.

### The version that governed, not the newest one

`POL-DTI-001` allows 45% at v1.0 and 43% at v2.0. A file at 44% passes on
2026-06-25 and breaches on 2026-07-08. Retrieval selects by underwriting as-of
date; a single retrieval never returns two versions of one policy.

12/12 versioned-policy checks correct, `version_accuracy` **1.0000**,
`wrong_version_rate` **0.0000**.

### Every citation resolves, or it is not evidence

Resolution is checked against the corpus — the file is opened and the rule id
found in it — not against the index that produced the citation. Evidence whose
citation does not resolve is dropped before it reaches an agent.

`citation_validity` = **1.0000** over all 430 indexed chunks and over every
evaluation run.

---

## Measured position

Authored evaluation set, 182 cases, macro-averaged across products:

| Metric | Target | Measured |
|--------|--------|----------|
| `policy_recall@5` | ≥ 0.95 | **0.9932** |
| `rule_recall@5` | ≥ 0.90 | **0.9756** |
| `rule_mrr@10` | — | 0.8859 |
| `rule_ndcg@10` | — | 0.9084 |
| `citation_validity` | 1.00 | **1.0000** |
| `cross_product_contamination` | 0.00 | **0.0000** |
| `version_accuracy` (mortgage) | 1.00 | **1.0000** |
| `no_result` | — | **0.0000** |
| Prompt-injection policy override | 0.00 | **0.0000** (6 committed adversarial packets) |
| p50 / p95 latency | — | ~465 / ~517 ms |

Targets are engineering goals this team set, not claims about the source
requirements — see [REQUIREMENTS_MAPPING.md](REQUIREMENTS_MAPPING.md) §2.

Raw numbers: [`eval/results/`](../../eval/results/).

---

## What is deliberately not here

* **No LLM in the retrieval path.** Retrieval, calculation and rule evaluation
  are deterministic end to end. Gemini explains a computed figure; it never
  produces one (`POL-DTI-001` DTI-CALC-002).
* **No LLM query rewriting.** A committed synonym table closes the terminology
  gap this corpus has. An LLM in the retrieval path would make the evaluation
  non-reproducible.
* **No MMR.** Deduplication by (policy, version, rule) already removes the
  redundancy it would target.
* **No hosted anything.** Embeddings and reranking are local
  `sentence-transformers` models; the vector store is embedded Chroma. Enforced
  by [`test_stack_boundaries.py`](../../tests/rag/test_stack_boundaries.py).
