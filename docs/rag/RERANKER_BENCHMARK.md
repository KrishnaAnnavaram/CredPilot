# Reranker benchmark

Produced by [`eval/retrieval/benchmark_rerankers.py`](../../eval/retrieval/benchmark_rerankers.py).
Raw numbers: [`eval/results/reranker_benchmark.json`](../../eval/results/reranker_benchmark.json).

Three local cross-encoders against a no-reranker baseline, over 182 authored
evaluation cases — 108 mortgage, 74 education. The embedding
(`intfloat/e5-base-v2`) and the index are held fixed, so the only thing that
varies is the reranker.

Every candidate runs locally through `sentence-transformers`. No hosted reranking
service is contacted, and none was considered.

---

## Results

Macro-averaged across the two products:

| Reranker | rule R@5 | rule R@3 | rule MRR@10 | rule nDCG@10 | policy R@5 | p50 ms | p95 ms |
|----------|----------|----------|-------------|--------------|------------|--------|--------|
| *(none)* | 0.9640 | 0.9135 | 0.8435 | 0.8714 | 0.9932 | **40** | **44** |
| **ms-marco-MiniLM-L-6-v2** | **0.9826** | 0.9239 | 0.8876 | 0.9084 | **1.0000** | 481 | 513 |
| ms-marco-MiniLM-L-12-v2 | 0.9709 | 0.9226 | **0.8982** | **0.9122** | **1.0000** | 947 | 982 |
| BAAI/bge-reranker-base | 0.9564 | **0.9290** | 0.8665 | 0.8859 | **1.0000** | 2738 | 2793 |

Per product:

| Reranker | mortgage rule R@5 | education rule R@5 | mortgage policy R@1 | education policy R@1 |
|----------|-------------------|--------------------|---------------------|----------------------|
| *(none)* | 0.9766 | 0.9514 | 0.8565 | 0.7973 |
| **ms-marco-MiniLM-L-6-v2** | **0.9720** | **0.9931** | **0.9120** | 0.8514 |
| ms-marco-MiniLM-L-12-v2 | 0.9626 | 0.9792 | 0.9028 | **0.8649** |
| BAAI/bge-reranker-base | 0.9439 | 0.9688 | 0.8843 | 0.8108 |

---

## Selected: `cross-encoder/ms-marco-MiniLM-L-6-v2`

Both the most accurate on the deciding metric and the cheapest of the three.
There is no trade-off to make.

* **+0.0186 macro rule Recall@5** over no reranker (0.9640 → 0.9826)
* **+0.0117** over the next best candidate, L-12, at **half** its latency
* **+0.0441 macro rule MRR@10** over no reranker
* Takes macro policy Recall@5 to **1.0000** — every authored case surfaces the
  governing policy inside five results

---

## What the numbers say

### `bge-reranker-base` is now *worse than no reranker at all*

At 0.9564 it sits **below** the 0.9640 baseline, while costing 2.7 seconds of p50
latency. A 278-million-parameter reranker actively degrades retrieval here, and
charges 68× the baseline's latency to do it.

That is the sharpest instance of a pattern this project has now measured four
independent times:

| Where | Bigger option | Result |
|---|---|---|
| Candidate funnel | 60/60/60/50 vs 15/15/12/10 | worse (0.9593 vs 0.9826) |
| Reranker | bge-base 278 M vs MiniLM-L-6 23 M | worse (0.9564 vs 0.9826) |
| Reranker | MiniLM-L-12 33 M vs MiniLM-L-6 23 M | worse (0.9709 vs 0.9826) |
| Embedding | bge-base 768d vs bge-small 384d | worse (0.9594 vs 0.9640) |

A corpus of near-duplicate rules — six policies at two versions, many separated
by a single threshold — rewards precision about *which* rule, not general
semantic strength. Larger models are better at "is this about affordability" and
no better at "is this the 43% ceiling or the 45% one", so their extra capacity
buys extra plausible-but-wrong matches.

### A better embedding did part of the reranker's job

Under the previous embedding (`bge-small-en-v1.5`) the no-reranker baseline
scored 0.9315 and L-6 added **+0.0325**. Under e5-base-v2 the baseline is 0.9640
and L-6 adds **+0.0186** — the same reranker, doing meaningfully less work,
because the candidates arriving at it are already better ordered.

Worth saying plainly: reranking still clears the 0.01 materiality bar, but its
marginal value nearly halved when the retrieval underneath it improved. If the
embedding improves again, this decision is worth revisiting rather than assuming.

### The larger models win on ordering, not on finding

L-12 leads on MRR@10 (0.8982 vs 0.8876) and nDCG@10 (0.9122 vs 0.9084) while
losing 0.0117 of Recall@5. `bge-reranker-base` leads on Recall@**3** (0.9290)
while placing last on Recall@5. Both rank what they find more sharply and find
less.

For this system recall is what matters. An underwriting agent reads the whole
evidence list before applying a rule, so a correct rule at position 4 is fully
usable; a rule that never appears cannot be applied at all, and the deterministic
engine then reports INDETERMINATE and refers the file. `DECIDING` in the
benchmark encodes that priority — Recall@5 first, MRR and nDCG as tie-breakers.

### The baseline is strong enough to be a real option

Fusion alone now reaches 0.9640 rule recall and 0.9932 policy recall at **44 ms
p95** — a twelfth of L-6's latency. If this system ever needs to answer inside a
tight interactive budget, turning the reranker off costs 1.9 points of rule
recall rather than falling off a cliff. `--no-rerank` on `run_retrieval_eval.py`
measures that configuration on demand.

### Education gains, mortgage gives a little back

L-6 takes education from 0.9514 to **0.9931** (+0.0417) and mortgage from 0.9766
down to 0.9720 (−0.0046). The mortgage corpus is 3.3× larger with far more
near-duplicate rules, so reranking occasionally reorders two nearly identical
candidates the wrong way; the education corpus has more genuinely distinct rules
for a cross-encoder to separate.

Macro averaging is what makes the trade visible and acceptable: a 4-point gain on
one product against a half-point loss on the other.

---

## Method

* **Macro, not micro.** Mortgage contributes 108 cases to education's 74.
* **Index and embedding held fixed.** Only the reranker varies.
* **Authored cases only.** The golden-application family asks one broad question
  per file and is scored on coverage — see [../failure-analysis.md](../failure-analysis.md) F-4.
* **Materiality bar of 0.01**, applied by the script rather than by hand.
* **Re-run after the embedding changed.** This benchmark originally selected L-6
  under `bge-small-en-v1.5`. When the embedding benchmark moved the model, this
  was re-run rather than left describing a system that no longer existed — the
  selection held, and the margin changed enough to be worth reporting.

## Reproducing

```bash
python eval/retrieval/benchmark_rerankers.py
```

Roughly 40 minutes on CPU, most of it `bge-reranker-base`. Add
`--models cross-encoder/ms-marco-MiniLM-L-6-v2` to check a single candidate.
