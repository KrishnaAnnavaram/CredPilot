# Runbook — building, running and evaluating retrieval

Everything below runs from the repository root with pip and Python. No Docker, no
database service, no hosted model endpoint.

---

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate            # Windows
source .venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
cp .env.example .env              # optional; see "What needs a key" below
```

Python 3.11+ is required.

**First run downloads models.** `intfloat/e5-base-v2` (~440 MB) and
`cross-encoder/ms-marco-MiniLM-L-6-v2` (~90 MB) come from the Hugging Face hub
once and are served from the local cache afterwards. Nothing is called over the
network at inference time.

---

## The one command

```bash
python scripts/build_policy_indexes.py
```

Builds both product indexes from the committed corpora, writes the manifests, and
runs the integrity checks. Expect:

```
EDUCATION_LOAN:
  source docs       12
  chunks            101  (rule 72 / section 18 / overview 11)
  policies / rules  12 / 72
  collection        credpilot_education_policies

MORTGAGE:
  source docs       42
  chunks            329  (rule 203 / section 84 / overview 42)
  policies / rules  36 / 174
  collection        credpilot_mortgage_policies

Integrity:
  education  docs 12/12 · rules 72/72 · chunks 101 · contamination 0.00 · citations resolvable 1.00
  mortgage   docs 42/42 · rules 174/174 · chunks 329 · contamination 0.00 · citations resolvable 1.00
  16/16 checks passed
```

Takes about 30 seconds on CPU. It **exits non-zero if any integrity check
fails**, so a broken index cannot be committed unnoticed.

Counts are measured from the corpus on disk, never hard-coded: add a policy
document and the numbers move.

Artifacts written:

| Path | What |
|------|------|
| `data/vectorstore/credpilot/` | the Chroma database, two collections |
| `data/vectorstore/lexical/bm25_*.json` | the BM25 indexes, one per product |
| `data/vectorstore/index_manifest.json` | models, counts, per-document SHA-256 |
| `data/vectorstore/index_integrity.json` | all 16 checks, pass/fail with detail |
| `data/policy_corpus/corpus_registry.json` | the corpus inventory |

---

## Running it

### Assess an application

```bash
python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json
python -m src.cli assess synthetic_data/education/applications/APP-2026-00001.json
```

The full graph: quarantine → domain routing → targeted policy retrieval →
deterministic calculation → rule evaluation → risk → recommendation, writing
`logs/tool_calls.jsonl` and `logs/agent_actions.jsonl` as it goes.

`--json` for machine output, `--output PATH` to save it, `--trace` to emit spans.

### The boundary triple

The case the corpus was built around — same 44% ratio, three outcomes:

```bash
for app in APP-000055 APP-000056 APP-000057; do
  python -m src.cli assess synthetic_data/mortgage/applications/$app.json
done
```

### Query retrieval directly

```bash
python -m src.cli retrieve "What is the maximum back-end DTI?" \
    --application-id APP-000056 --as-of-date 2026-07-08

python -m src.cli retrieve "Does this borrower require a cosigner?" \
    --application-id APP-2026-00001 --verbose
```

### See what is indexed

```bash
python -m src.cli corpus
```

---

## Evaluating

### Retrieval quality, both products

```bash
python eval/retrieval/run_retrieval_eval.py
```

~6 minutes. Writes `eval/results/retrieval_eval.json` and a per-case record at
`eval/results/retrieval_eval_cases.jsonl`. Reports the authored and
golden-application families separately — see the note in
[FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md) F-4 for why.

Useful flags: `--no-rerank` to isolate the reranker's contribution, `--no-golden`
for the authored set only, `--trace` to emit spans for the run.

### Model selection

```bash
python eval/retrieval/benchmark_embeddings.py   # ~35 min, builds 4 throwaway indexes
python eval/retrieval/benchmark_rerankers.py    # ~25 min, index held fixed
```

Write `eval/results/embedding_benchmark.json` and
`eval/results/reranker_benchmark.json`. The models in `config/rag.yaml` must be
justified by these.

### Pipeline shape

```bash
python eval/retrieval/ablation.py         # ~12 min, six configurations
python eval/retrieval/sweep_pipeline.py   # ~25 min, six funnel widths
```

---

## Observability

Tracing is **off** unless asked for — Phoenix's exporter targets a local
collector, and wiring it up implicitly means every call retries a connection to
something nobody started.

### Spans without a collector

```bash
python scripts/export_traces.py
```

Runs seven applications across both products with an in-process span recorder and
writes `traces/phoenix_spans.jsonl` plus `traces/trace_summary.json`.

### Spans into a running Phoenix

```bash
python -m phoenix.server.main serve       # terminal 1, UI on http://localhost:6006
export CREDPILOT_TRACING=1                # $env:CREDPILOT_TRACING=1 on Windows
python scripts/export_traces.py --phoenix # terminal 2
```

---

## Tests

```bash
python -m pytest tests/ -q                       # everything
python -m pytest tests/ -q -m "not slow"         # fast subset, no model loads
python -m pytest tests/rag/test_product_isolation.py -q
python -m pytest tests/rag/test_temporal_retrieval.py -q
```

The full suite loads the embedding and reranker models and spawns the MCP server
as a subprocess several times; allow 60–90 minutes on CPU. `-m "not slow"` runs
the parser, chunking, fusion, guardrail and boundary tests in under a minute.

---

## The MCP server

```bash
python mcp_server/server.py        # stdio; normally launched by a client
```

Consumed through `langchain-mcp-adapters`:

```python
import asyncio
from mcp_server.client import open_session, load_surface

async def main():
    async with open_session() as session:
        surface = await load_surface(session)
        tool = next(t for t in surface.tools if t.name == "retrieve_policy")
        print(await tool.ainvoke({
            "query": "What is the maximum back-end DTI?",
            "application_id": "APP-000056",
            "as_of_date": "2026-07-08",
        }))

asyncio.run(main())
```

Writes `logs/mcp_transcript.jsonl`.

> **Anything the server prints to stdout corrupts the JSON-RPC stream.** The
> server disables progress bars, warms the models before `mcp.run()`, and wraps
> every handler in `@protocol_safe`. Keep that in place when adding a handler —
> [FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md) F-3 is what happens otherwise.

---

## What needs a key, and what does not

| | Needs `GEMINI_API_KEY` |
|---|---|
| Building the indexes | no |
| Retrieval, the CLI, the MCP server | no |
| Calculations and rule evaluation | no |
| The retrieval evaluation and all benchmarks | no |
| `pytest tests/` | no |
| Narrative rationale generation | **yes** |
| The DeepEval LLM-as-judge suite | **yes** |

Retrieval, calculation and rule evaluation are deterministic and contain no model
call — by design, and because `POL-DTI-001` DTI-CALC-002 forbids a model
producing an underwriting figure.

A Gemini API key starts with `AIza` and comes from
<https://aistudio.google.com/apikey>. An OAuth access token (starting `AQ.`) is
not an API key and returns `401 UNAUTHENTICATED`.

---

## Rebuilding after a policy changes

Every build is a full rebuild — each collection is dropped and recreated — so a
stale embedding cannot survive an edit:

```bash
python scripts/build_policy_indexes.py
```

To confirm the index still matches the corpus without rebuilding:

```bash
python -c "import sys; sys.path.insert(0,'.'); \
from src.rag.integrity import validate_indexes; \
r = validate_indexes(); print(r.as_dict()['status']); \
[print(c.name, c.detail) for c in r.failures]"
```

The hash check catches an edited policy: `stale_documents` becomes non-zero.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `lexical index missing at …` | indexes not built | `python scripts/build_policy_indexes.py` |
| `no index manifest at …` | same | same |
| `PRODUCT_CLARIFICATION_REQUIRED` | no application id and no explicit domain | pass `--application-id` or `--product-domain` |
| `NO_APPLICABLE_POLICY` | the as-of date precedes every policy | check `--as-of-date`; mortgage starts 2026-01-01, education 2025-01-15 |
| `stale_documents > 0` | a policy changed since the build | rebuild |
| MCP client hangs | a handler wrote to stdout | wrap it in `@protocol_safe` |
| `401 UNAUTHENTICATED` from Gemini | OAuth token rather than an API key | use a key starting `AIza` |
| Very slow first call | model download or cold load | expected once; subsequent runs use the cache |
