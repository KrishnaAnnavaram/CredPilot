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
| `data/vectorstore/lexical/bm25_mortgage.json`, `data/vectorstore/lexical/bm25_education.json` | the BM25 indexes, one per product |
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
| ablation | `eval/results/retrieval_ablation.json` | no |
| retrieval evaluation | `eval/results/retrieval_eval*.json(l)` | no |
| trace export | `traces/phoenix_spans.jsonl`, `traces/trace_summary.json` | no |
| agent evaluation | `reports/eval_report.json`, `reports/eval_cases.jsonl` | for the **judged** metrics only |
| golden signals | `reports/golden_signals.json`, `reports/dashboard_data.csv` | no |
| dashboard | `reports/dashboard.png` | no |

**The agent evaluation always runs.** It gates on whether the model *answers*,
not on whether a key is present — those are different questions, and the
difference mattered here: the committed key is well-formed and reaches the
service, and returns `402 RESOURCE_EXHAUSTED` from every model. On a
"is there a key" test the step ran, the judge failed case by case, and the run
produced a report with null judged metrics under a command that promised judged
ones.

So when the model does not answer, the step runs with `--no-judge` and says so.
Every deterministic metric refreshes; every `judge_*` figure is `null` with the
reason recorded. Nothing is skipped and nothing is invented.

Useful flags: `--only indexes` to run one step, `--skip "agent evaluation"` to
leave the long one out deliberately.

The whole run takes about three hours with a working judge, an hour and a half
deterministic-only, or ten minutes with `--skip "agent evaluation"`.

---

## Running it

### The web UI

```bash
python -m src.web                  # http://127.0.0.1:8000
python -m src.web --port 9000 --reload
```

FastAPI plus one static page. It reaches the **same compiled graph** the CLI
reaches — there is no second router and no second rule engine behind it — and
streams each node as it runs, so a twenty-second assessment shows which agent is
working rather than spinning.

Submit a committed application from the right-hand panel, or ask a question in
the box. An ambiguous question pauses the thread and the page asks; answering it
resumes the same thread. The **Evidence view** at the bottom of the sidebar shows
the route, the agents that ran, the retrieval breakdown, the validation result
and the guardrail findings. It never shows chain of thought, because there is
none to show: the model writes prose after the decision exists.

### Assess an application

```bash
python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json
python -m src.cli assess synthetic_data/education/applications/APP-2026-00001.json
```

The full graph: intake → input guardrails → Supervisor → the product specialist
→ targeted policy retrieval → deterministic calculation → rule evaluation → risk
→ recommendation → narrative → response validation → output guardrails, writing
`logs/tool_calls.jsonl` and `logs/agent_actions.jsonl` as it goes.

`--json` for machine output, `--output PATH` to save it, `--trace` to emit spans.

### Ask a question

```bash
python -m src.cli ask "What is the maximum back-end DTI on a jumbo mortgage?"
python -m src.cli ask "When is a cosigner required on a student loan?" --verbose
python -m src.cli ask "hello"
```

The same graph, with no application attached. `--verbose` prints the nodes that
ran and the routing reason.

A question that names no product is clarified rather than guessed:

```bash
$ python -m src.cli ask "I need help with my loan"
  [route CLARIFY · deterministic]
  Is this about a **home mortgage** or a **private education (student) loan**? …
  Re-run with --answer to resume this thread:
    python -m src.cli ask "I need help with my loan" --thread-id ask-1a2b3c4d --answer "mortgage"
```

`--answer` resolves it in one run; `--thread-id` resumes a thread later.

### Hold a conversation

```bash
python -m src.cli chat
```

An interactive thread on one checkpoint. Clarification, resume and product
carry-forward work exactly as they do in the web UI — a follow-up in a thread
already scoped to mortgage stays on mortgage without being asked again.

### The boundary triple

The case the corpus was built around — same 44% ratio, three outcomes:

```bash
for app in APP-000055 APP-000056 APP-000057; do
  python -m src.cli assess "synthetic_data/mortgage/applications/${app}.json"
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
python -m eval.agent.run_agent_eval --judge-all      # the final, committed run
python -m eval.agent.run_agent_eval --no-judge       # deterministic only, no key
```

Runs all 95 golden cases — 75 mortgage, 20 education — through the **whole
graph, from its real entry point**. Every case therefore exercises intake, the
input guardrail, the Supervisor's routing decision, the product specialist,
retrieval, the rule engine, the recommendation, the narrative, the response
validator and the output guardrail. An evaluation that entered at an internal
node would be measuring a path no user can take, and Supervisor routing — the
component most able to send a file to the wrong corpus — would be scored by
nothing. `supervisor_routing_accuracy` exists because of this.

Budget roughly **25 seconds** for an unjudged mortgage case, **20** for
education, and **50+** for a judged one. A `--no-judge` run over all 95 takes
about forty minutes; `--judge-all` takes about three times that, because
DeepEval makes nine or ten model calls per case.

**`--judge-all` fails rather than degrading.** If the judge is unreachable it
exits non-zero and writes nothing, because a report labelled "every case judged"
that judged none is worse than no report. Use `--no-judge` deliberately instead,
and the report will say `judge.available: false` with the reason and leave every
`judge_*` figure `null` — not zero, and not carried over from an earlier run.

Writes `reports/eval_report.json` and a per-case record at
`reports/eval_cases.jsonl`.

**Sampling the judge does not weaken the deterministic result.** Outcome
accuracy, routing accuracy, citation validity and recall, response validation
and the grounding check in `src.narrative.verify_narrative` run on every case,
and those are the ones that govern where the two disagree. With
`--judge-limit-per-product` the judged metrics run on a balanced sample, taken
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
python scripts/export_traces.py          # 1. the spans
python -m eval.agent.run_agent_eval      # 2. the quality figures
python scripts/build_golden_signals.py   # 3. combine them
python scripts/build_dashboard.py        # 4. draw it
```

**Two sources, deliberately not one.**

*Operational* figures — latency and its **thinking / acting / tool / retrieval**
split, tokens, cost — are computed from **Phoenix spans**, read from
`traces/phoenix_spans.jsonl` or from a running instance with `--phoenix`. They
are not re-derived from the evaluation's own case file, and that is the point of
the requirement: a harness measures itself with a stopwatch around its own loop
and cannot see inside a run. It can report that an assessment took twenty
seconds; only the traces can say that four of them were the cross-encoder. A
split invented from a total would be a fabrication dressed as telemetry.

*Quality* figures — accuracy, hallucination rate, citation validity — are
imported from `reports/eval_report.json`, which is where they are measured.
Nothing in the script recomputes them.

Every block in the output states its `source`, and every row of
`dashboard_data.csv` carries a `source` column reading `phoenix` or `eval`, so
the two can never be confused for one another.

`build_golden_signals.py` exits non-zero if there are no spans — latency is
Phoenix-derived by requirement, so it will not silently produce a report
without them. `build_dashboard.py` draws `reports/dashboard.png` from the CSV,
so the picture and the numbers behind it come from one file.

Each span declares its own kind as a `credpilot.span_kind` attribute rather than
being classified by name in the aggregator, so a node added later is classified
by whoever adds it — see `tests/test_observability_signals.py`, which asserts
that every named span has a declared kind.

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
```

The full suite loads the embedding and reranker models and spawns the MCP server
as a subprocess several times; allow 60–90 minutes on CPU, and do not run two
copies at once — they contend for the same cores and both slow to a crawl.
`-m "not slow"` runs the parser, chunking, fusion, guardrail, supervisor,
resilience and rule-family tests in a couple of minutes.

By what they cover:

```bash
python -m pytest tests/test_supervisor.py -q            # routing, 62 tests, no model
python -m pytest tests/test_routing.py -q               # edges + the compiled graph
python -m pytest tests/test_rule_families.py -q         # the 17 rule families
python -m pytest tests/test_resilience.py -q            # NFR-04
python -m pytest tests/test_mcp_capabilities.py -q      # all six MCP families
python -m pytest tests/test_web_api.py -q               # the HTTP surface
python -m pytest tests/test_observability_signals.py -q # spans, signals, audit trail
python -m pytest tests/test_loops.py -q                 # loop and cascade guards
python -m pytest tests/test_tool_contracts.py -q        # tool contracts
python -m pytest tests/test_evidence.py -q             # every cited artifact still resolves
python -m pytest tests/test_memory_persistence.py -q    # cross-session recall
python -m pytest tests/rag/test_product_isolation.py -q
python -m pytest tests/rag/test_temporal_retrieval.py -q
```

**No unit test spends a model token.** The Supervisor's deterministic classifier
is the contract and its model fallback is off by default; `test_supervisor.py`
patches the model path to fail loudly if anything reaches it.

---

## The MCP server

CredPilot is the **host**. `src/mcp_host/client.py` is the client it owns, and
`mcp_server/` is a separate process reached over stdio.

```bash
python -m src.cli mcp              # connect, discover, print the surface
python -m src.cli mcp --json       # the same as JSON
python mcp_server/server.py        # run the server on its own
```

`python -m src.cli mcp` prints what the server advertises — 11 tools, 10
resources, 6 prompts, and the negotiated protocol revision. It takes about
thirty seconds, because the server loads two sentence-transformer models before
it answers.

From code, through the host's own client:

```python
import asyncio
from src.mcp_host import open_client

async def main():
    async with open_client() as client:
        print(client.capabilities.tool_names)

        result = await client.call_tool("retrieve_policy", {
            "query": "What is the maximum back-end DTI?",
            "application_id": "APP-000056",
            "as_of_date": "2026-07-08",
        })
        print(result.ok, result.payload["evidence_count"])

        # Which version governed on a date, rather than which is newest.
        version = await client.call_tool("get_policy_version", {
            "product_domain": "MORTGAGE",
            "policy_id": "POL-DTI-001",
            "as_of_date": "2026-06-25",
        })
        print(version.payload["governing_version"])       # -> 1.0

        catalogue = await client.read_resource("credpilot://system/capabilities")
        prompt = await client.get_prompt("underwriting_rationale", {
            "product_domain": "MORTGAGE", "outcome": "APPROVE_RECOMMENDATION",
            "figures_json": "{}", "evidence_json": "[]",
        })

asyncio.run(main())
```

Every call returns an `MCPCallResult` whose `ok` says which it was — a timeout,
an unknown tool or an unreachable server is a **value**, not an exception,
because a graph node has to produce a state update either way.

Also consumable through `langchain-mcp-adapters`, which
`tests/rag/test_mcp_rag_integration.py` exercises:

```python
from mcp_server.client import open_session, load_surface
```

Writes `logs/mcp_transcript.jsonl`.

### The six capability families

| Family | Try it |
|---|---|
| Tools | `call_tool("compute_affordability", {"application_id": "APP-000056"})` |
| Resources | `read_resource("credpilot://thresholds/mortgage")` |
| Prompts | `get_prompt("human_review_summary", {...})` |
| Elicitation | `call_tool("clarify_loan_product", {"user_request": "help with my loan"})` — set `client.elicitation_responder` to answer it |
| Sampling | `call_tool("draft_with_sampling", {"instruction": "..."})` — served through Gemini, refused from any other model |
| Roots | `call_tool("list_project_roots", {})` — a four-directory allowlist |

```bash
python -m pytest tests/test_mcp_capabilities.py -q    # all six, real subprocess
```

> **Anything the server prints to stdout corrupts the JSON-RPC stream.** The
> server disables progress bars, warms the models before `mcp.run()`, and wraps
> every handler in `@protocol_safe`. Keep that in place when adding a handler —
> [../failure-analysis.md](../failure-analysis.md) F-3 is what happens otherwise.

---

## What needs a key, and what does not

| | Needs a working `GOOGLE_API_KEY` |
|---|---|
| Building the indexes | no |
| Retrieval, the CLI, the web UI, the MCP server | no |
| **Supervisor routing and clarification** | no |
| Calculations and rule evaluation | no |
| Guardrails, memory, context engineering | no |
| The retrieval evaluation and all benchmarks | no |
| `pytest tests/` | no — and no test spends a token |
| `scripts/export_traces.py` | no |
| `scripts/build_golden_signals.py`, `scripts/build_dashboard.py` | no |
| `run_agent_eval --no-judge` | no |
| Narrative rationale and policy-answer generation | **yes** — degrades if absent |
| `run_agent_eval --judge-all` and its DeepEval metrics | **yes** — refuses if absent |

Retrieval, calculation, rule evaluation and **routing** are deterministic and
contain no model call — by design, and because `POL-DTI-001` DTI-CALC-002
forbids a model producing an underwriting figure. The Supervisor's model
fallback is opt-in (`CREDPILOT_SUPERVISOR_MODEL=1`) and off by default, so
routing behaves identically with and without a key.

There is exactly **one** model call in a normal assessment: the narrative node,
which explains a decision already made. Without a key it degrades to a
deterministic summary and marks the result `available: false`; the file is still
assessed and still gets a recommendation. A policy question degrades to quoting
the governing rules.

### A key that is present but has no quota

Worth distinguishing, because it is the state this repository is in and because
"has a key" is the wrong thing to test for. The committed key is correctly
formed and reaches the service; every model returns
`402 RESOURCE_EXHAUSTED — "Your prepayment credits are depleted"`.

Everything in the "no" column above runs unchanged. What changes:

* narratives and policy answers use their fallbacks, marked `available: false`
  with the reason;
* `--judge-all` **exits non-zero and writes nothing**, rather than publishing a
  report labelled "every case judged" that judged none;
* `--no-judge` runs normally and the report records `judge.available: false`
  with the reason, leaving every `judge_*` figure `null` — not zero;
* `golden_signals.json` sets `model_calls_recorded_no_tokens: true` and states
  that $0.00 is an absence of measurement, not an efficiency result;
* `regenerate_evidence.py` detects it and runs the evaluation deterministic-only
  rather than producing a half-judged report.

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
