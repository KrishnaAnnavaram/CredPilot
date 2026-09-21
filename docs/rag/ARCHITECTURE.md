# Retrieval architecture

CredPilot underwrites two independent lending products. Their AI infrastructure
is shared; their business knowledge is not. This document describes how that line
is drawn and why it is drawn where it is.

---

## 1. The shape

```
                            Supervisor
                                 |
                       Loan Domain Router          <- structured facts only
                        /                \
                 MORTGAGE              EDUCATION_LOAN
                        \                /
                         +------+-------+
                                |
                     Policy Retrieval Agent
                                |
                     retrieve_policy (RAG tool)
                                |
        +-----------------------+------------------------+
        |                                                |
  credpilot_mortgage_policies              credpilot_education_policies
  329 chunks · 42 documents                101 chunks · 12 documents
  174 rules · 6 versioned policies         72 rules · 1 version each
  synthetic_data/mortgage/policy_corpus/   synthetic_data/education/policy_corpus/
```

The two collections live in one local Chroma database at
`data/vectorstore/credpilot/`. They never share an index, and there is
deliberately no combined collection — `PolicyVectorStore` refuses to open one
named `credpilot_all_policies`.

**Product isolation happens before retrieval, not after.** The domain router
resolves the product from structured facts — an explicit domain, the graph
state, the application id's shape, or the packet's structure — and that decision
picks the collection. A mortgage query cannot return an education policy because
it never searches the education index, not because a metadata filter was applied
correctly. Measured: `cross_product_contamination_rate` = 0.0000.

When no structured fact settles the product, retrieval returns
`PRODUCT_CLARIFICATION_REQUIRED` and searches nothing. Searching both corpora and
letting the model pick is the failure mode this design exists to prevent.

---

## 2. The pipeline

```
  query (may contain untrusted applicant text)
        |
   [1] sanitize .................... strip imperatives; keep the topic
        |
   [2] resolve product domain ...... HARD: picks the collection
        |
   [3] applicability filter ........ HARD: effective-date window + governing version
        |
        +------------------+------------------+
        |                                     |
   [4] BM25 top 15                    [5] dense top 15
        |                                     |
        +------------------+------------------+
                           |
   [6] reciprocal rank fusion -> top 12
                           |
   [7] cross-encoder rerank -> top 10
                           |
   [8] temporal re-validation
                           |
   [9] scope affinity (SOFT) + deduplication
                           |
  [10] citation validation ......... unresolvable evidence is dropped
                           |
                   PolicyEvidence[] top 6
```

Every stage opens a named span (`rag.retrieve`, `bm25.search`, `chroma.search`,
`rrf.fusion`, `reranker.run`, `temporal.validate`, `citation.validate`, …), so a
Phoenix trace shows exactly where candidates were gained and lost.

**The widths are floors, not caps.** Every stage only ever *removes* candidates,
so a width narrower than the requested `top_k` truncates the answer silently —
a request for 15 used to come back with 4. Each width is therefore
`max(configured, top_k + slack)`, and the overview budget scales with `top_k` the
same way. At the default `top_k` of 6 the measured values still govern, unchanged.
Deduplication may still return fewer than requested when the candidate pool runs
out of distinct (policy, version, rule) units — that is the retriever reporting
honestly that there is no more distinct evidence, and the candidate counts on the
result show it.

**No language model participates in any stage.** Retrieval is deterministic: the
same query, corpus and as-of date produce the same evidence in the same order,
every run. That is what makes the evaluation reproducible (REQ-033) and what lets
`POL-DTI-001` DTI-CALC-002 be honoured — no model produces an underwriting figure
or a threshold.

Funnel widths are measured, not assumed; see
[RETRIEVAL_ABLATION.md](RETRIEVAL_ABLATION.md).

---

## 3. Chunking: the rule is the unit

The retrieval unit is a whole rule together with everything that makes it
applicable — its source category, severity, outcome, "applies when", body,
parameter table, acceptable evidence, exceptions and cross-references.

A fixed 500- or 1000-character window would routinely separate

> Back-end debt-to-income must not exceed 43 percent…

from

> | `max_back_end_dti` | 43% |

and a rule without its threshold is not evidence, it is a hint. Secondary
splitting fires only above 4200 characters, at paragraph boundaries, repeating
the parent heading into every part. **No rule in either corpus currently needs
it**, and [`test_chunking.py`](../../tests/rag/test_chunking.py) asserts that, so
if a future policy grows past the limit the split path is exercised deliberately
rather than discovered in production.

### The two corpora are genuinely different documents

| | Mortgage | Education |
|---|---|---|
| Rule marker | `### DTI-CONV-001 — Title` (own heading) | `**EDU-UW-001 -- Title.**` (bold, inline, body runs on) |
| Dash convention | em dash | `--` in POL-001..006, em dash in POL-007..012 |
| Product scope key | `product_scope` | `product_scope` *or* `products` |
| Versions | 6 policies × 2 versions, 2026-07-01 boundary | 1 version per policy |
| Expiry / supersession | published | not published |
| Per-rule severity | published | not published |
| Occupancy / purpose scope | published | not applicable |

Two parsers, one normalized `PolicyChunk`. Fields a product does not support are
`None` — never filled in to make the two look symmetrical.

### Chunk identity

```
MORTGAGE__POL-DTI-001__v2.0__DTI-CONV-001__000
EDUCATION__POL-002__v1.0__EDU-UW-001__000
EDUCATION__POL-001__v1.0__S05__000              (section with no rule)
MORTGAGE__POL-DTI-001__v2.0__OVERVIEW__000      (document overview)
```

Deterministic: same corpus plus same code yields the same ids every run. The key
is the rule id, not a content hash, so an editorial fix to a rule's prose does not
churn every downstream id.

### Nothing is dropped

Sections carrying no rule — reason-code dictionaries, review cycles, cross-product
rules — become section-level chunks rather than being discarded for lacking an id.
Both parsers are checked for full line coverage of their source documents.

---

## 4. Temporal retrieval

A mortgage file at 44% back-end DTI **passes** on 2026-06-25 and **breaches** on
2026-07-08. Same ratio, same borrower profile, different governing version.
Retrieving the newest document would silently flip the decision, so version
selection is a hard filter:

1. **Effective window** — `effective_date <= as_of <= expiration_date`
   (open-ended when no expiry is published).
2. **Latest eligible version per policy id** — everything older is `SUPERSEDED`
   and removed.

A single retrieval never mixes two versions of one policy. An as-of date before
any policy existed returns `NO_APPLICABLE_POLICY`, not the oldest document.

Product scope (`product_scope`, `purpose_scope`, `occupancy_scope`) is a **soft**
ranking boost, not a filter: scope metadata is incomplete across the corpus and
hard-filtering on it would drop overlays that govern every programme.

Details and the education limitation: [TEMPORAL_RETRIEVAL.md](TEMPORAL_RETRIEVAL.md).

---

## 5. Citations

Every piece of evidence carries a citation, and a citation that does not resolve
to a committed source document is dropped before it becomes evidence. Resolution
is checked against **the corpus** — the file is opened and the rule id found in
it — not against the index that produced the citation, so a bug in indexing
cannot certify its own output.

Each product keeps its own convention, matching its golden set:

* mortgage — `POL-DTI-001 v2.0 rule DTI-CONV-001`
* education — `POL-002 EDU-UW-001`

A chunk with no rule cites its section; a chunk with neither cites the document.
A rule id is never invented. Measured validity: **1.0000**.

---

## 6. Where the corpus lives

The policy documents are committed under
`synthetic_data/<product>/policy_corpus/`. `data/policy_corpus/` holds the
machine-generated **registry** — every source document with its product, policy
id, version, effective window, rule ids, SHA-256 and canonical path — rather than
a second copy of the documents. One copy means one hash, and the provenance chain
from a citation back to a committed file cannot drift. Recorded as deviation D1
in [REQUIREMENTS_MAPPING.md](REQUIREMENTS_MAPPING.md).

---

## 7. What is deliberately kept apart

| Kept apart | Why |
|---|---|
| Policy knowledge / application evidence | The policy index holds policy only. No applicant record is in it, so there is nothing for a cross-customer query to leak. |
| Runtime / golden sets | No runtime module imports or reads either `golden_set/`. Only `eval/retrieval/dataset.py` does. |
| Inputs / outcomes | `src/application_context.py` reads the structured extract's *input* tables and **raises** on the tables holding computed ratios, rule evaluations, eligibility results or decisions. |
| Retrieval / arithmetic | `src/calculations.py` produces figures; the retriever produces thresholds; `src/rules.py` applies one to the other. |
| Applicant text / control | Untrusted text may influence what is searched for. It can reach nothing else. |

---

## 8. Module map

| Module | Responsibility |
|--------|----------------|
| [`src/domain.py`](../../src/domain.py) | `LendingProductDomain`, deterministic product resolution |
| [`src/config.py`](../../src/config.py) | typed config from `config/rag.yaml` |
| [`src/rag/models.py`](../../src/rag/models.py) | `PolicyChunk`, `PolicyRetrievalRequest`, `PolicyEvidence`, statuses |
| [`src/rag/parsers/`](../../src/rag/parsers/) | `BasePolicyParser` → mortgage / education |
| [`src/rag/embedding.py`](../../src/rag/embedding.py) | local Sentence-Transformers, per-family conventions |
| [`src/rag/vectorstore.py`](../../src/rag/vectorstore.py) | Chroma, one collection per product |
| [`src/rag/lexical.py`](../../src/rag/lexical.py) | BM25, identifier-preserving tokenizer |
| [`src/rag/fusion.py`](../../src/rag/fusion.py) | reciprocal rank fusion |
| [`src/rag/rerank.py`](../../src/rag/rerank.py) | local cross-encoder |
| [`src/rag/applicability.py`](../../src/rag/applicability.py) | effective-date and version selection |
| [`src/rag/expansion.py`](../../src/rag/expansion.py) | deterministic synonym expansion |
| [`src/rag/citations.py`](../../src/rag/citations.py) | citation construction and resolution |
| [`src/rag/pipeline.py`](../../src/rag/pipeline.py) | the retriever |
| [`src/rag/indexer.py`](../../src/rag/indexer.py) | deterministic index build + manifest |
| [`src/rag/integrity.py`](../../src/rag/integrity.py) | index integrity validation |
| [`src/tools/rag_tool.py`](../../src/tools/rag_tool.py) | the agentic-RAG tool |
| [`src/rules.py`](../../src/rules.py) | rule engine — retrieved thresholds applied |
| [`src/calculations.py`](../../src/calculations.py) | deterministic underwriting figures |
| [`src/graph.py`](../../src/graph.py) | the LangGraph |
| [`mcp_server/`](../../mcp_server/) | MCP server and adapter client |
