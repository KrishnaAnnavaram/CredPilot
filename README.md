# CredPilot

**Loan Origination & Underwriting Copilot** — a LangGraph multi-agent system that
ingests a loan application, retrieves the lending policy that governed it on the
day it was underwritten, computes affordability deterministically, screens risk,
and drafts an auditable recommendation with a human making the final call.

CredPilot underwrites **two independent lending products**: U.S. residential
mortgage and private education loans. Their AI infrastructure is shared; their
business knowledge is not.

---

## Quick start

```bash
python -m venv .venv
.venv/Scripts/activate                 # source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

python scripts/build_policy_indexes.py                                    # ~30 s
python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json
python -m src.cli assess synthetic_data/education/applications/APP-2026-00001.json
```

No Docker. No database service. No hosted model or vector endpoint. Building the
indexes, retrieval, the CLI, the retrieval evaluation and the tests need **no API
key** — they are deterministic and call no model.

One step does: the written rationale. Set `GOOGLE_API_KEY` in `.env` to enable it,
and the end-to-end evaluation with it:

```bash
python -m eval.agent.run_agent_eval      # 95 golden cases, both products, LLM-as-judge
python scripts/build_golden_signals.py   # latency, tokens, cost, accuracy, hallucination rate
python scripts/build_dashboard.py        # reports/dashboard.png
```

Full instructions: **[docs/rag/RUNBOOK.md](docs/rag/RUNBOOK.md)**.

---

## What it does, on one case

`APP-000056` and `APP-000057` are the same borrower profile, both computing to
exactly **44.00%** back-end debt-to-income, both underwritten on 2026-07-08:

```
APP-000056  back_end_dti 0.4400
            BREACH back_end_dti: 0.4400 <= 0.4300  [POL-DTI-001 v2.0 rule DTI-CONV-001]
            DECLINE_RECOMMENDATION — HUMAN REVIEW REQUIRED
              a decline recommendation is always routed to a human (DEC-REC-002)

APP-000057  back_end_dti 0.4400
            ceiling extended to 45.00% on 3 documented compensating factors:
              verified reserves of 61.1 months (>= 6.0)
              representative credit score 744 (>= 720)
              loan-to-value 72.00% (<= 75%)
            APPROVE_RECOMMENDATION
```

`APP-000055` is the same ratio again on 2026-06-25, where `POL-DTI-001` **v1.0**
still governs and allows 45% unconditionally — so it passes for a different
reason. Three files, one ratio, three outcomes, decided entirely by which policy
version retrieval returned and what each file documents.

Nothing in that is hardcoded. The 43%, the 45% extension, the two-factor minimum
and each factor's bar are all read out of the policy text the retriever returned;
remove the retrieved rule and the engine reports INDETERMINATE rather than
falling back to a number in the code.

---

## Where the model sits

Not where people usually assume.

```
retrieval  →  calculation  →  rule engine  →  recommendation  →  narrative
└────────────────── deterministic ──────────────────────────┘    └── Gemini ──┘
```

Gemini writes the **rationale**. It does not retrieve, rank, filter, compute,
compare against a threshold, or decide. By the time it is called the outcome
already exists and is handed to it as a fact, and there is no code path by which
its text changes the recommendation. Afterwards, every citation and figure in the
prose is checked back against the evidence it was given — deterministically, with
no model involved. A rationale that fails that check is kept, marked unfaithful,
and routed to a human.

---

## The pieces

| | Where | What |
|---|---|---|
| **LangGraph** | [`src/graph.py`](src/graph.py) | typed state, supervisor, loan-domain router, 4 workers, conditional edges, SQLite checkpointer |
| **Agentic-RAG tool** | [`src/tools/rag_tool.py`](src/tools/rag_tool.py) | hybrid product-isolated retrieval, retrieval-in-the-loop |
| **Retrieval subsystem** | [`src/rag/`](src/rag/) | parsers, chunking, embedding, Chroma, BM25, RRF, reranking, applicability, citations |
| **MCP server** | [`mcp_server/`](mcp_server/) | 3 tools + 3 resources over stdio, consumed via `langchain-mcp-adapters` |
| **Deterministic math** | [`src/calculations.py`](src/calculations.py) | every underwriting figure, per product |
| **Rule engine** | [`src/rules.py`](src/rules.py) | retrieved thresholds applied to computed figures |
| **Review triggers** | [`src/review_triggers.py`](src/review_triggers.py) | `UWR-HRV-001`, the mandatory human-review routing table |
| **Narrative** | [`src/narrative.py`](src/narrative.py) | the one Gemini call, checked against its own evidence afterwards |
| **Context engineering** | [`src/context/`](src/context/) | write, select, compress, isolate — untrusted text in its own compartment |
| **Tiered memory** | [`src/memory/`](src/memory/) | short-term window + long-term semantic recall, scoped per subject |
| **Guardrails** | [`src/guardrails/`](src/guardrails/) | injection detection, quarantine, PII redaction |
| **Observability** | [`src/observability/`](src/observability/) | Phoenix/OTel spans, tool-call log, audit trail |
| **Evaluation** | [`eval/retrieval/`](eval/retrieval/), [`eval/agent/`](eval/agent/) | retrieval metrics and benchmarks; end-to-end accuracy with DeepEval LLM-as-judge |
| **Tests** | [`tests/`](tests/) | parsers, isolation, temporal, security, contracts, rules, loops, memory, integration |

---

## Data

Entirely synthetic, generated by committed code from fixed seeds. No record is
real and no policy is any real lender's policy.

| | Mortgage | Education |
|---|---|---|
| Applications | 75 | 200 |
| Policy documents | 42 (6 at two versions) | 12 |
| Rules | 203 | 72 |
| Applicant documents | 1,140 | 18 |
| Golden cases | 75 | 20 |

See [`synthetic_data/README.md`](synthetic_data/README.md).

---

## Measured

| Metric | Target | Measured |
|--------|--------|----------|
| Source documents indexed | all | 42/42 · 12/12 |
| Declared rules indexed | all | 174/174 · 72/72 |
| `cross_product_contamination_rate` | 0.00 | **0.0000** |
| `citation_validity` | 1.00 | **1.0000** |
| `policy_recall@5` (macro, authored) | ≥ 0.95 | **1.0000** |
| `rule_recall@5` (macro, authored) | ≥ 0.90 | **0.9826** |
| Temporal-version accuracy | 1.00 | **1.0000** |
| Prompt-injection policy override | 0.00 | **0.0000** |

### End to end, both products' golden sets

95 cases run through the whole graph, macro-averaged across products. Judged
metrics cover a balanced sample of 20 per product; the deterministic ones cover
every case.

| Metric | Target | Measured |
|--------|--------|----------|
| `citation_validity` | 1.00 | **1.0000** |
| `judge_answer_relevancy` | — | **1.0000** |
| `judge_faithfulness` | — | **0.9841** |
| `narrative_faithfulness_deterministic` | — | **0.9750** |
| `hallucination_rate` (judged) | 0.00 | **0.0074** |
| `outcome_accuracy` | — | **0.6987** |
| `directional_agreement` | — | **0.6950** |
| `citation_recall` | — | **0.6030** |
| Runs completed without error | 95/95 | **95/95** |
| Cost per assessment | — | $0.0026 |
| Latency p50 / p95 | — | 18.0s / 28.0s |

Split by product, the same measure reads 0.6197 for mortgage over 75 cases and
0.7778 for education over 20. The macro figure above is their unweighted mean —
pooling them would make it a mortgage score with a rounding error attached.

**Read `outcome_accuracy` against `rule_coverage` in the same report.** The rule
engine evaluates a minority of the declared rule families, and 33 of 75 mortgage
and 17 of 20 education cases turn on one it does not implement — that is the
ceiling on the figure, not an excuse for it. Retrieval is not the gap: those rules
are retrieved and cited, they are simply never compared against a threshold.

The hallucination rate misses its 0.00 target and is published as measured.
`narrative_faithfulness_deterministic` is a conservative lower bound re-derived by
`scripts/recheck_faithfulness.py`; the figure the run itself produced is kept
beside it in the report.

Raw numbers in [`eval/results/`](eval/results/) and
[`data/vectorstore/index_integrity.json`](data/vectorstore/index_integrity.json),
all produced by committed scripts.

End-to-end decision accuracy, grounding and cost — over both products' golden
sets, macro-averaged, with DeepEval as LLM-as-judge — are in
[`reports/eval_report.json`](reports/eval_report.json),
[`reports/golden_signals.json`](reports/golden_signals.json) and
[`reports/dashboard.png`](reports/dashboard.png).

Two caveats travel with every accuracy figure and are repeated wherever they are
published: the data is synthetic and self-generated, so agreement with the
generator is not correctness; and the LLM judge shares a model family with the
system it grades. Every judged figure has a deterministic counterpart, and where
they disagree the deterministic one governs.

---

## Documentation

* **[docs/rag/README.md](docs/rag/README.md)** — the retrieval subsystem
* **[docs/rag/RUNBOOK.md](docs/rag/RUNBOOK.md)** — build, run, evaluate, trace
* **[docs/rag/ARCHITECTURE.md](docs/rag/ARCHITECTURE.md)** — how and why
* **[docs/rag/REQUIREMENTS_MAPPING.md](docs/rag/REQUIREMENTS_MAPPING.md)** — requirements → evidence → tests, with deviations stated
* **[docs/failure-analysis.md](docs/failure-analysis.md)** — eight real failures, with evidence and before/after
* **[docs/rag/DATA_QUALITY_FINDINGS.md](docs/rag/DATA_QUALITY_FINDINGS.md)** — defects found in the datasets
* **[docs/model-card.md](docs/model-card.md)** — models, data, intended use, limitations, failure modes
* **[docs/risk-register.md](docs/risk-register.md)** — 28 risks against OWASP LLM Top 10 and NIST AI RMF, with residual risk stated
* **[docs/compliance.md](docs/compliance.md)** — EU AI Act, NIST AI RMF, DPDP: what is addressed, where the evidence is, and what is not met
* **[docs/output-risk.md](docs/output-risk.md)** — three output tiers and what gates each

---

## Stack

Python 3.11+ · LangGraph · Google Gemini (the only model provider) · MCP Python
SDK + `langchain-mcp-adapters` · Chroma + local Sentence-Transformers · Arize
Phoenix + OpenTelemetry/OpenInference · Presidio · pytest.

Everything installs with pip. Claude Code was used as the development assistant;
no Claude model is called at runtime and no `ANTHROPIC_API_KEY` is read —
enforced by [`tests/rag/test_stack_boundaries.py`](tests/rag/test_stack_boundaries.py).
