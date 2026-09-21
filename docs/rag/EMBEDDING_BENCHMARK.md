# Embedding benchmark

Produced by [`eval/retrieval/benchmark_embeddings.py`](../../eval/retrieval/benchmark_embeddings.py).
Raw numbers: [`eval/results/embedding_benchmark.json`](../../eval/results/embedding_benchmark.json).

Four local Sentence-Transformers checkpoints, each used to build a complete
throwaway index over **both** corpora and then evaluated through the full
pipeline on 182 authored cases — 108 mortgage, 74 education. The reranker
(`cross-encoder/ms-marco-MiniLM-L-6-v2`), the chunking, the filters and the
fusion are identical across rows; only the embedding changes.

Everything runs locally. No hosted embedding endpoint is contacted.

---

## Results

Macro-averaged across the two products:

| Model | dim | rule R@1 | rule R@3 | rule R@5 | rule MRR@10 | rule nDCG@10 | policy R@5 | build | index | p50 ms |
|-------|-----|----------|----------|----------|-------------|--------------|------------|-------|-------|--------|
| BAAI/bge-small-en-v1.5 | 384 | 0.7924 | 0.9227 | 0.9640 | 0.8760 | 0.8964 | 0.9865 | **17.3 s** | **8.9 MB** | **490** |
| sentence-transformers/all-MiniLM-L6-v2 | 384 | 0.7924 | **0.9344** | 0.9663 | 0.8793 | 0.8993 | 0.9886 | **9.8 s** | **8.9 MB** | 496 |
| **intfloat/e5-base-v2** | 768 | **0.7972** | 0.9169 | **0.9756** | 0.8806 | **0.9015** | **0.9932** | 61.0 s | 9.7 MB | 509 |
| BAAI/bge-base-en-v1.5 | 768 | 0.7924 | 0.9193 | 0.9594 | 0.8740 | 0.8939 | 0.9865 | 57.8 s | 9.7 MB | 490 |

Per product:

| Model | mortgage rule R@5 | education rule R@5 | mortgage policy R@5 | education policy R@5 |
|-------|-------------------|--------------------|---------------------|----------------------|
| BAAI/bge-small-en-v1.5 | 0.9766 | 0.9514 | 1.0000 | 0.9730 |
| sentence-transformers/all-MiniLM-L6-v2 | 0.9673 | 0.9653 | 0.9907 | 0.9865 |
| **intfloat/e5-base-v2** | 0.9720 | **0.9792** | 1.0000 | 0.9865 |
| BAAI/bge-base-en-v1.5 | 0.9673 | 0.9514 | 1.0000 | 0.9730 |

Build time and index size are one-off costs. Query latency is dominated by the
reranker and is effectively identical across all four (490–509 ms p50).

---

## Selected: `intfloat/e5-base-v2`

**This work started on `BAAI/bge-small-en-v1.5` and the measurement moved it.**
The task brief named bge-small as the expected starting point and said not to
lock it in without evidence. The evidence puts e5-base-v2 ahead:

* **+0.0116 macro rule Recall@5** (0.9756 vs 0.9640) — the deciding metric
* **+0.0067 macro policy Recall@5** (0.9932 vs 0.9865) — the best of the four
* **+0.0048 macro rule Recall@1** — the only model to move the top slot at all
* at **the same query latency** (509 vs 490 ms p50, both dominated by reranking)

What it costs: 768 dimensions instead of 384, a 61-second index build instead of
17, and 9.7 MB of index instead of 8.9 MB. All one-off, all trivial at this
corpus size.

### How big is the margin, honestly

0.0116 over 182 cases is about **two cases**. That clears the 0.01 materiality
bar this project uses, and the direction is corroborated by e5 also winning
policy Recall@5 and Recall@1 — but it is a preference supported by a small
margin, not a decisive result. Two things follow:

* If index build time or memory ever matters, `all-MiniLM-L6-v2` at 0.9663 and a
  9.8-second build is a defensible fallback that costs under one point of recall.
* If the query set grows, this is worth re-running. `--models` takes a subset, so
  re-checking two candidates is a ten-minute job.

---

## What the numbers say

### Bigger is not better here either

The two 768-dimension models bracket the field: e5-base-v2 is the best and
bge-base-en-v1.5 is the **worst**, below its own 384-dimension sibling
(0.9594 vs 0.9640). Capacity is not what separates these models on this corpus —
training objective is.

This is the third place the same pattern has appeared. A wider candidate funnel
made retrieval worse ([RETRIEVAL_ABLATION.md](RETRIEVAL_ABLATION.md)); a larger
cross-encoder made it worse ([RERANKER_BENCHMARK.md](RERANKER_BENCHMARK.md)); a
larger embedding from the same family makes it worse. A corpus of near-duplicate
rules — six policies at two versions, many separated by one threshold — rewards
precision about *which* rule, not general semantic strength.

### e5 wins at 5 and loses at 3

e5-base-v2 has the best Recall@5 (0.9756) and the **worst** Recall@3 (0.9169) of
the top three. `all-MiniLM-L6-v2` is the reverse: best at 3 (0.9344), third at 5.

e5 surfaces more of the right rules but ranks them slightly lower inside the top
three. For this system that trade is worth taking: the underwriting agent reads
the whole evidence list before applying a rule, so a correct rule at position 4 is
fully usable, whereas a rule that never appears cannot be applied at all and
leaves the deterministic engine reporting INDETERMINATE. `DECIDING` in the
benchmark encodes that priority — Recall@5 first.

Had this system shown a single citation to a user, Recall@3 would have been the
right metric and `all-MiniLM-L6-v2` the right model.

### The encoding convention is doing real work

Each family is used the way its authors published it, and the convention travels
with the model name rather than being a caller's responsibility:

| Model | Query | Passage |
|-------|-------|---------|
| e5-base-v2 | `query: ` | `passage: ` |
| bge-*-en-v1.5 | `Represent this sentence for searching relevant passages: ` | *(none)* |
| all-MiniLM-L6-v2 | *(none)* | *(none)* |

All four are normalized and scored with cosine distance. Getting a prefix wrong
costs recall silently — there is no error, just worse results — which is why
[`src/rag/embedding.py`](../../src/rag/embedding.py) owns the convention and
records it in the index manifest rather than leaving it to a caller.

### Education gains more than mortgage

e5's advantage is almost entirely on education (0.9792 vs bge-small's 0.9514,
+0.0278) while mortgage slightly regresses (0.9720 vs 0.9766, −0.0046). The
education corpus is a third the size with no versioned near-duplicates, so a
stronger general-purpose embedding has more room there; the mortgage corpus
rewards the exact-identifier matching that BM25 supplies regardless of embedding.

Macro averaging is what makes that visible. A case-weighted average would have
let mortgage's 108 cases bury a 2.8-point gain on the other product.

---

## Method

* **Both products, every candidate.** Each model builds a full index over both
  corpora into a temporary directory and is evaluated on both. A model chosen on
  mortgage alone would be chosen on 60% of the system.
* **Macro, not micro.** Mortgage has 3.3× the chunks and 1.5× the cases.
* **Identical pipeline.** Same chunking, filters, BM25, fusion, reranker,
  deduplication. Only the embedding varies.
* **Deterministic.** No sampling, no temperature — the differences between rows
  are real, not run-to-run noise. They may still be idiosyncratic to this query
  set, which is the caveat stated above.
* **Committed decision rule.** `DECIDING = (rule_recall@5, rule_mrr@10,
  policy_recall@5)`, applied by the script. The largest model is not chosen
  automatically and neither is the smallest.

## Reproducing

```bash
python eval/retrieval/benchmark_embeddings.py
```

Roughly 35 minutes on CPU — it builds four complete indexes. `--models` limits
the sweep; `--no-rerank` isolates the embedding from the reranker's contribution.

After changing the selected model, rebuild and re-measure everything from one
code state:

```bash
python scripts/regenerate_evidence.py
```
