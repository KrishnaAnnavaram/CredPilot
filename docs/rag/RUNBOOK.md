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

## Regenerating every committed artifact

REQ-033 asks for the system, its traces and its evaluation to be regenerable from
one documented command. This is it:

```bash
python scripts/regenerate_evidence.py
```

Eight steps, in order, each writing artifacts that are committed:

| Step | Writes | Needs a key |
|---|---|---|
| indexes | `data/vectorstore/`, manifests, integrity report | no |
| funnel sweep | `eval/results/pipeline_sweep.json` | no |
| ablation | `eval/results/ablation.json` | no |
| retrieval evaluation | `eval/results/retrieval_eval*.json(l)` | no |
| trace export | `traces/phoenix_spans.jsonl` | no |
| agent evaluation | `reports/eval_report.json`, `reports/eval_cases.jsonl` | **yes** |
| golden signals | `reports/golden_signals.json`, `reports/dashboard_data.csv` | no |
| dashboard | `reports/dashboard.png` | no |

The agent evaluation is **skipped with a message** when no `GOOGLE_API_KEY` is
set, rather than failing the run. Everything retrieval-side — which is most of
the committed evidence and all of the deterministic part — regenerates on a clean
checkout with no credential at all.

Useful flags: `--only indexes` to run one step, `--skip "agent evaluation"` to
leave the long one out deliberately.

The whole run takes a little over an hour with a key, or about ten minutes
without one.

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
[../failure-analysis.md](../failure-analysis.md) F-4 for why.

Useful flags: `--no-rerank` to isolate the reranker's contribution, `--no-golden`
for the authored set only, `--trace` to emit spans for the run.

### End to end, both products, with the LLM-as-judge

```bash
python -m eval.agent.run_agent_eval
```

**Needs `GOOGLE_API_KEY`.** Runs all 95 golden cases — 75 mortgage, 20 education —
through the whole graph, then scores the rationales with DeepEval using Gemini as
the judge.

Budget roughly **15 seconds** for an unjudged case and **50 seconds** for a judged
one. The committed run judges 20 per product and takes a little under an hour;
judging all 95 takes about three times that, because DeepEval makes nine or ten
model calls per case.

```bash
python -m eval.agent.run_agent_eval --judge-limit-per-product 20   # the committed run
```

Writes `reports/eval_report.json` and a per-case record at
`reports/eval_cases.jsonl`.

**Sampling the judge does not weaken the result.** The deterministic metrics —
outcome accuracy, citation validity and recall, and the grounding check in
`src.narrative.verify_narrative` — run on every case, and those are the ones that
govern where the two disagree. The judged metrics run on a balanced sample, taken
per product so neither dominates, and `judged_cases` states the denominator.

Useful flags while iterating:

```bash
python -m eval.agent.run_agent_eval --limit-per-product 5   # 10 cases, both products
python -m eval.agent.run_agent_eval --no-judge              # deterministic only, ~3x faster
python -m eval.agent.run_agent_eval --product education     # one product
```

`--limit-per-product` takes the first *n* of **each** product rather than the
first *n* overall. Mortgage has 75 cases to education's 20, so a flat limit would
leave a "both products" run that was almost entirely mortgage.

`--no-judge` still runs the deterministic grounding check
(`src.narrative.verify_narrative`), which needs no judge — only the DeepEval
metrics are skipped.

### Golden signals and the dashboard

```bash
python scripts/build_golden_signals.py
python scripts/build_dashboard.py
```

Both **re-derive** from the committed evaluation run rather than re-measuring, so
they are fast and cannot disagree with it. The first writes
`reports/golden_signals.json` and `reports/dashboard_data.csv`; the second draws
`reports/dashboard.png` from that CSV, so the picture and the numbers behind it
come from one source.

Run the evaluation first — both exit with a message if `reports/eval_report.json`
is missing.

### Re-deriving faithfulness after a change to the checker

```bash
python scripts/recheck_faithfulness.py            # updates reports/eval_report.json
python scripts/recheck_faithfulness.py --dry-run  # reports the figure, touches nothing
```

`narrative_faithfulness_deterministic` is produced during the run, so a fix to
:func:`src.narrative.verify_narrative` normally means re-running the evaluation.
This script gets the same answer without one, and **needs no model credential**.

It is exact rather than approximate, for a specific reason: the run records every
figure it flagged, and a fix that widens the supported set can only clear a flag,
never raise a new one. Each flagged figure is re-tested against a supported set
rebuilt from retrieval, the calculators and the rule engine — none of which
involve a model. Where a fix changes the figure *pattern* rather than the
supported set, that reasoning does not hold and the evaluation must be re-run.

The corrected figure replaces the one in `reports/eval_report.json`, and the
original is kept beside it as
`narrative_faithfulness_deterministic_as_measured`. `reports/faithfulness_recheck.json`
records which cases cleared, which did not, and why the re-derivation is sound.

### Reading the numbers

Three things to know before quoting anything from these reports:

1. **Every headline figure is macro-averaged across products.** A pooled mean
   would be a mortgage score with a rounding error attached.
2. **`hallucination_rate` is derived, not raw.** DeepEval 4.x reports
   `HallucinationMetric` in the same direction as its other metrics — 1.0 means
   grounded. The report publishes `judge_hallucination_score` (raw, 1 is good)
   and `judge_hallucination_rate = 1 - score` (0 is good) beside it.
3. **Grounding is measured twice.** `narrative_faithfulness_deterministic` asks
   no model anything; the `judge_*` figures do. Where they disagree, trust the
   deterministic one — the judge shares a model family with the system it grades.

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
> [../failure-analysis.md](../failure-analysis.md) F-3 is what happens otherwise.

---

## What needs a key, and what does not

| | Needs `GOOGLE_API_KEY` |
|---|---|
| Building the indexes | no |
| Retrieval, the CLI, the MCP server | no |
| Calculations and rule evaluation | no |
| The retrieval evaluation and all benchmarks | no |
| `pytest tests/` | no |
| Narrative rationale generation | **yes** |
| `eval/agent/run_agent_eval.py` and its DeepEval judge | **yes** |
| `scripts/build_golden_signals.py`, `scripts/build_dashboard.py` | no — they re-derive from the committed report |

Retrieval, calculation and rule evaluation are deterministic and contain no model
call — by design, and because `POL-DTI-001` DTI-CALC-002 forbids a model
producing an underwriting figure.

There is exactly **one** model call in a normal assessment: the narrative node,
which explains a decision already made. Without a key it degrades to a
deterministic summary and marks the result `available: false`; the file is still
assessed and still gets a recommendation.

Both `GOOGLE_API_KEY` and `GEMINI_API_KEY` are accepted, and the SDK is given
whichever is set.

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
