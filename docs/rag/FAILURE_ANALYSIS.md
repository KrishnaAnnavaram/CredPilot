# Failure analysis — real failures from real runs

Eight failures found while building and evaluating this subsystem. Each was
observed in a run, not imagined; each has the evidence that showed it, a root
cause, a fix, and the measurement before and after.

Four of them (F-1, F-2, F-7, F-8) would have shipped as silent correctness
bugs — F-8 as a wrongful decline. One (F-3)
hung the system completely. One (F-5) was an assumption this work started with
that measurement contradicted.

---

## F-1 — Overview chunks starved their own policy's rules

**Severity: high.** Correct rules were being excluded from evidence entirely.

### Observed

`eval/results/retrieval_eval_cases.jsonl`, first full run. Six authored cases
scored `rule_recall@5 = 0.00` despite the right policy being retrieved:

```
MTG-090  "Which monthly obligations have to be counted against the borrower?"
         expected  ['LIA-INC-001']
         retrieved ['LIA-INC-005', 'LIA-INC-002', 'INC-OTH-004', 'DTI-CALC-001']

MTG-010  "What affordability ceiling applies to this file?"   (as of 2026-06-25)
         expected  ['DTI-CONV-001']
         retrieved ['USD-OVL-004', 'VA-OVL-003', 'DTI-CALC-003', 'DTI-BRE-001']
```

### Diagnosis

Running MTG-090 with `top_k=25` and debug on showed the whole picture:

```
 1. POL-LIA-001 v1.0                      rr=-1.16   <- OVERVIEW chunk
 2. POL-LIA-001 v1.0 rule LIA-INC-005     rr=-2.46
 3. POL-LIA-001 v1.0 rule LIA-INC-002     rr=-2.74
 4. POL-INC-007 v1.0 rule INC-OTH-004     rr=-4.49
```

Three `POL-LIA-001` items had been admitted and the per-policy cap of 3 was
spent — on an overview chunk plus two incidental rules. `LIA-INC-001`, the rule
that answers the question, was ranked below them and never reached the result.

### Root cause

`_dedupe` counted every chunk against one per-policy budget. A document's
OVERVIEW chunk — its purpose, scope and version history — is *navigation*, and it
matches almost any question about that policy because it restates the policy's
subject. So it reliably outranked the specific rule and then consumed one of the
three slots that rule needed.

### Fix

[`src/rag/pipeline.py`](../../src/rag/pipeline.py) — overviews get their own small
budget (`dedupe.max_overview: 2`) and no longer count against `max_per_policy`.
They keep their rank, so "summarise POL-LIA-001" still works; they just cannot
displace the rules underneath them.

### Measured

| | macro rule Recall@5 | macro rule MRR@10 |
|---|---|---|
| Before | 0.9546 | 0.8803 | <!-- was -->
| After | **0.9687** | **0.8843** | <!-- was -->

Same funnel (25/15/20/15), same corpus, same cases. MTG-090 and MTG-010 both
pass. Regression test: `test_chunking.py` plus the authored eval set.

---

## F-2 — Presidio destroyed every citation in the audit trail

**Severity: high.** Every logged citation became unresolvable, which is exactly
what the Citation-Resolves Rule (REQ-030) forbids.

### Observed

`tests/rag/test_pii_logging.py::test_audit_detail_is_redacted` failed:

```
At index 0 diff:
  'POL-DTI-001 [REDACTED_US_DRIVER_LICENSE].0 rule DTI-CONV-001'
!= 'POL-DTI-001 v2.0 rule DTI-CONV-001'
```

`logs/agent_actions.jsonl` from a real CLI run confirmed it was not a test
artifact — every citation in every record was mangled the same way, and
`APP-000056` had become `APP-[REDACTED_US_DRIVER_LICENSE]`.

### Root cause

`redact_structure(..., use_presidio=True)` ran Presidio with `US_DRIVER_LICENSE`
and `US_PASSPORT` in its entity list. Both are deliberately loose recognizers —
they match generic alphanumeric runs, because driver's licence formats vary by
state. On this corpus they matched `v2.0` inside a version marker and `000056`
inside an application id.

The audit trail's whole purpose is that a reviewer can follow a citation to a
committed source document. Redacting the citation destroys that while protecting
nothing: a policy version number is not personal data.

### Fix

[`src/guardrails/redaction.py`](../../src/guardrails/redaction.py):

1. `US_DRIVER_LICENSE` and `US_PASSPORT` removed from `_PRESIDIO_ENTITIES`, with
   the reason recorded in the code. The deterministic patterns already cover the
   passport and I-94 references the corpora actually contain.
2. `_PROTECTED_IDENTIFIERS` — CredPilot's own grammar (policy ids, rule ids,
   application ids, version markers, record ids, trace and span ids) is skipped
   by every redaction pass, including the pattern layer.

### Measured

Real identifiers are still caught — `123-45-6789`, `4111 1111 1111 1111`,
`SYN-ACCT-000221`, emails, phone numbers all redact. Citations survive intact and
resolve. Regression tests: `test_redaction_never_mangles_an_identifier` (7
identifier shapes), `test_an_identifier_beside_a_secret_survives_while_the_secret_does_not`,
`test_logged_citations_still_resolve`.

---

## F-3 — the MCP server deadlocked on its first retrieval

**Severity: critical.** The MCP integration was completely non-functional.

### Observed

`tests/rag/test_mcp_rag_integration.py` never completed. A 600-second timeout
produced `.F` and then nothing. The smoke script showed the session opening fine
and then stopping dead:

```
[  4.5s] tools=['retrieve_policy', 'resolve_citation', 'list_policy_rules']
[09/21/26 02:53:57] INFO  Processing request of type CallToolRequest
                          ... nothing further, for 10 minutes
```

Sampling the server process twice, twenty seconds apart:

```
sample1 CPU=4.765625 WS=919MB Threads=26
sample2 CPU=4.765625 WS=919MB Threads=26
```

CPU identical to seven decimal places. The process was **blocked**, not slow.

### Root cause

On stdio transport, **stdout is the JSON-RPC channel**. The first
`retrieve_policy` call loads the embedding model, and `transformers` prints a
progress bar — `Loading weights: 0%| | 0/199 [00:00<?, ?it/s]` — to **stdout**.
That wrote non-JSON into the protocol stream. The client could not parse a frame,
never replied, and the server waited for a request that would never come.

Visible in the logs the whole time; it just does not look like a protocol error,
it looks like slowness.

### Fix

[`mcp_server/server.py`](../../mcp_server/server.py), three layers:

1. `HF_HUB_DISABLE_PROGRESS_BARS`, `TQDM_DISABLE`, `TRANSFORMERS_VERBOSITY=error`
   set **before** any import that reads them.
2. `warm_up()` loads the models at start-up, before `mcp.run()` takes stdout.
3. `@protocol_safe` redirects stdout to stderr for the duration of every tool and
   resource handler, so a library that prints in future cannot repeat this.

### Measured

| | Result |
|---|---|
| Before | indefinite hang on the first retrieval |
| After | session up in 4.5 s; **4 cross-product retrievals in 17.8 s total**, clean shutdown |

`pytest tests/rag/test_mcp_rag_integration.py` — 5 passed.

---

## F-4 — the evaluation was measuring the slot count, not the retriever

**Severity: medium.** It made the headline metric unreadable.

### Observed

First full evaluation: macro `policy_recall@5 = 0.7474` against a 0.95 target.
Split by case family:

| Family | policy Recall@5 | mean relevant policies |
|--------|-----------------|------------------------|
| authored | 0.9932 | 1.0 | <!-- was -->
| golden-application | 0.1279 (mortgage) | **15.7** | <!-- was -->

### Root cause

Recall@5 is bounded above by `5 / |relevant|`. A mortgage golden case asks one
broad question — *"assess this application"* — whose ground truth is every policy
governing the file, around sixteen of them. With `final_top_k = 6`, Recall@5
cannot exceed 0.32 however perfect the ranking is. Averaging the two families
together reported a retrieval problem where there was a measurement problem.

The same run showed `policy_mrr@10 = 1.0000` and `policy_hit@5 = 1.0000` on that
family: the top result was always a governing policy.

### Fix

`eval/retrieval/` now scores the two families separately and on their own terms.
The authored family — targeted questions, 1–2 relevant policies — carries the
Recall@5 targets. The golden-application family reports `coverage@k` (recall
normalized by `min(|relevant|, k)`) at a larger `top_k`, and is never used to
claim a Recall target was met.

### Measured

Authored family, macro: `policy_recall@5` **0.9932**, `rule_recall@5` **0.9546**
→ 0.9687 after F-1. Both targets met, and honestly stated.

**What this did not fix, and is not pretending to:** education
golden-application `policy_hit@5` is 0.6842. Some of that is
[F-1 in DATA_QUALITY_FINDINGS.md](DATA_QUALITY_FINDINGS.md) — 36% of those
citations are defective — but not all of it. Broad whole-file questions retrieve
genuinely less well than targeted ones. The architectural answer is the one the
graph already implements: ask several targeted questions per application rather
than one broad one.

---

## F-5 — a wider candidate funnel made retrieval worse

**Severity: low as a bug, high as a corrected assumption.**

### Observed

This work began with 25 dense / 25 lexical / 20 fused / 15 reranked, on the
intuition that more candidates give the reranker more to work with.
[`eval/results/pipeline_sweep.json`](../../eval/results/pipeline_sweep.json)
contradicted it:

| dense/lex/fuse/rerank | macro rule R@5 | p95 ms |
|---|---|---|
| 15 / 15 / 12 / 10 | **0.9709** | **498** | <!-- was -->
| 25 / 25 / 20 / 15 | 0.9687 | 829 | <!-- was -->
| 30 / 30 / 30 / 20 | 0.9687 | 1168 | <!-- was -->
| 40 / 40 / 40 / 25 | 0.9640 | 1436 | <!-- was -->
| 50 / 50 / 50 / 35 | 0.9640 | 1777 | <!-- was -->
| 60 / 60 / 60 / 50 | 0.9640 | 2033 | <!-- was -->

*(Figures as measured at the time, under `bge-small-en-v1.5`. The current table
is in [RETRIEVAL_ABLATION.md](RETRIEVAL_ABLATION.md); under `e5-base-v2` the
effect is larger still — 0.9826 against 0.9593 for every wider configuration.)*

Recall falls monotonically as the funnel widens, and p95 latency quadruples.

### Root cause

Every additional candidate is another chance for the cross-encoder to score a
plausible-but-wrong rule above the correct one. On a corpus this dense with
near-duplicate rules — six policies at two versions, many rules differing by a
single threshold — the reranker's error rate grows with candidate count faster
than its recall does.

### Fix

`config/rag.yaml` set to the measured optimum, 15/15/12/10, with the sweep cited
in a comment so the next person does not re-derive the intuition.

A second defect surfaced while making the change: `rerank_top_k` was a hard cap,
so a caller asking for `top_k=15` could only ever receive 10 results.
`src/rag/pipeline.py` now reranks `max(rerank_top_k, top_k)` candidates.

### Measured

macro rule Recall@5 0.9687 → **0.9709**, p95 829 ms → **498 ms**. Better on both
axes. <!-- was -->

---

## F-6 — the education parser silently found no rules in POL-001

**Severity: high.** Four rules would have been missing from the index.

### Observed

The first education parse run raised rather than silently succeeding:

```
PolicyParseError: front matter declares rules absent from the body:
['EDU-GOV-001', 'EDU-GOV-002', 'EDU-GOV-003', 'EDU-GOV-004']
```

### Root cause

The rule-marker pattern was anchored to end-of-line:

```python
r"^\*\*(EDU-[A-Z]+-\d+)\s*[—–-]{1,2}\s*(.+?)\.?\*\*\s*$"
```

`POL-002` writes its markers on their own line, so the survey that produced the
pattern looked right. `POL-001` runs the rule body on from the closing `**` on
the same line:

```
**EDU-GOV-001 -- Policy Scope and Applicability.** Every credit decision …
```

The `$` anchor never matched, and the document contributed no rule chunks.

### Why it was caught rather than shipped

The parser cross-checks front-matter `rule_ids` against the markers it found and
**raises** on a mismatch. Without that check, `POL-001` would have indexed as four
section chunks with no rule ids, no rule-level citations, and no error — and the
first sign would have been an evaluation case failing for reasons nobody could
explain.

### Fix

Pattern changed to `r"^\*\*(EDU-[A-Z]+-\d+)\s*[—–-]{1,2}\s*([^*]+?)\.?\*\*"` —
the marker opens a line but need not end it.

### Measured

| | Education rules indexed |
|---|---|
| Before | 68 / 72 (POL-001 contributed 0) |
| After | **72 / 72** |

Regression test: `test_inline_bold_rule_markers_are_found`, plus
`test_every_declared_rule_becomes_a_chunk` over all 12 documents.

---

---

## F-7 — the funnel silently truncated any request larger than it was wide

**Severity: high.** It made the golden-application evaluation measure the wrong
thing, on top of F-4.

### Observed

A test written to check that an unresolvable citation gets backfilled rather than
dropped failed for an unrelated reason: asking for `top_k=15` returned **4**
results.

```
top_k=15  ->  4 results
  1  POL-SEC-001 v1.0
  2  POL-GEN-001 v1.0 rule GEN-ELG-002
  3  POL-DEC-001 v1.0
  4  POL-GEN-001 v1.0 rule GEN-ELG-001
```

Instrumenting the stages showed 18 candidates reaching deduplication and 4
leaving it.

### Root cause

Two independent caps, both tuned for the default `top_k` of 6 and both applied
unconditionally:

1. **`fusion_top_k: 12`.** The funnel widths chosen by the sweep are correct at
   `top_k=6`. At `top_k=15` fusion discarded everything past the twelfth
   candidate before the reranker ever saw it.
2. **`dedupe.max_overview: 2`.** Added to fix [F-1](#f-1--overview-chunks-starved-their-own-policys-rules).
   A broad question — *"which policies govern this application?"* — matches
   document overviews more closely than any individual rule, so the candidate
   pool was mostly overviews and the cap of 2 truncated the result to 4.

Every stage in the pipeline only removes candidates. Any stage narrower than the
requested size is therefore a silent cap, and nothing in the response said so.

**This affected the evaluation.** The golden-application family runs at
`top_k=15` precisely because a mortgage file is governed by ~16 policies. It was
being answered with at most ~12, and often far fewer — so part of the weak
golden-application coverage reported under F-4 was this bug, not retrieval.

### Fix

[`src/rag/pipeline.py`](../../src/rag/pipeline.py):

* every stage width becomes `max(configured, top_k + slack)`,
* the overview budget becomes `max(configured, top_k // 2)`.

At `top_k=6` both resolve to the measured values and nothing changes, which
[`test_the_default_top_k_is_unaffected_by_the_width_floors`](../../tests/rag/test_rag_tool_contract.py)
pins.

### Measured

| | `top_k=15` results |
|---|---|
| Before | 4 |
| After | **11** |

Eleven rather than fifteen because deduplication then runs out of distinct
(policy, version, rule) units for that query — the retriever correctly reporting
that there is no more distinct evidence, which is visible in the candidate counts
and is a different thing from a silent cap.

The F-1 regression cases still pass: `LIA-INC-001` and `DTI-CONV-001` are both
still retrieved at `top_k=6`.

Regression tests: `test_a_large_top_k_is_not_capped_by_the_configured_funnel`,
`test_the_default_top_k_is_unaffected_by_the_width_floors`, and
`test_an_unresolvable_citation_is_replaced_not_dropped` — the test that found it.

---

## F-8 — a rule was applied without the rule it depends on, and declined a file

**Severity: critical.** It produced a confident, wrong, adverse decision.

### Observed

Changing the embedding to `intfloat/e5-base-v2` ([EMBEDDING_BENCHMARK.md](EMBEDDING_BENCHMARK.md))
and re-running the boundary triple:

```
APP-000055  thr 0.45  ELIGIBLE     APPROVE_RECOMMENDATION   factors=0
APP-000056  thr 0.43  INELIGIBLE   DECLINE_RECOMMENDATION   factors=0
APP-000057  thr 0.43  INELIGIBLE   DECLINE_RECOMMENDATION   factors=0   <-- wrong
```

`APP-000057` documents three compensating factors and must be **approved**. The
evaluation detail read:

```
ceiling 43.00% from POL-DTI-001 v2.0 rule DTI-CONV-001;
extension to 45.00% unavailable — 0 of 2 required factors documented
```

### Root cause

`DTI-CONV-001` grants its extension on *"at least two compensating factors from
DTI-CONV-003"*. `DTI-CONV-003` is the rule that defines what counts as a factor
and what each one's bar is.

Under the previous embedding, the broad affordability question happened to
retrieve both rules. Under e5 it retrieved `DTI-CONV-001`, `DTI-CALC-001` and
`DTI-CONV-002` — but not `DTI-CONV-003`.

With no factor definitions in hand, `_documented_factors` could match nothing and
returned an empty list. The engine then reported **"0 of 2 factors documented"** —
a statement it had no basis for. It did not know that no factors were documented;
it did not know what a factor was. The difference between those two produced a
decline on a file that qualifies.

The bug was latent the whole time and surfaced only because a model change
shuffled the candidate ranking. Any change to chunking, fusion or the corpus
could have triggered it just as easily.

### Fix

Two layers, because either alone leaves a hole.

**1. The agent follows its own references.** The Policy Retrieval Agent now scans
the evidence from its first pass for rule ids it does not hold and issues one
targeted retrieval per dependency — `src/graph.py`, `referenced_rules()` plus a
second pass bounded by `MAX_DEPENDENCY_FOLLOWS`. This is retrieval-in-the-loop in
the literal sense: the first answer raises a question and the agent asks it,
rather than deciding without it. Exact-id lookup is what the lexical layer is
best at, so the follow-up is reliable.

**2. The rule engine refuses to guess.** Where `DTI-CONV-001` publishes an
extension and `DTI-CONV-003` is absent, `src/rules.py` returns **INDETERMINATE**
with a detail naming the missing rule — never FAIL. `POL-GEN-001` GEN-ELG-005 is
explicit that missing evidence yields INDETERMINATE and never a negative result,
and declining someone because retrieval missed a rule is precisely the outcome
that forbids.

### Measured

| | `APP-000055` | `APP-000056` | `APP-000057` |
|---|---|---|---|
| Before | APPROVE ✓ | DECLINE ✓ | **DECLINE ✗** |
| Engine fix alone | APPROVE ✓ | REFER *(indeterminate)* | REFER *(indeterminate)* |
| Both fixes | APPROVE ✓ | **DECLINE ✓** | **APPROVE ✓** |

With both fixes the triple is correct *and* better-grounded than before:
`APP-000056` now shows **1** documented factor rather than 0 — it has one, and
needs two — which is only knowable because `DTI-CONV-003` is now retrieved.

Dependency following fires on all three files (1, 4 and 4 follow-up retrievals).

Regression tests: [`test_dependency_following.py`](../../tests/rag/test_dependency_following.py),
13 cases covering reference detection, the engine's refusal, the bound on
following, and all three boundary files end to end.

### A note on how this was nearly missed twice

The reference-detection regex initially matched nothing. The pattern *looked*
right in the file and compiled without error — but shell escaping had turned each
intended `\b` word boundary into a literal **backspace character** (`0x08`),
invisible in every editor and in `git diff`. `cat -A` showed it as `^H`. The
pattern now uses lookarounds and character classes with no backslashes at all,
which sidesteps the escaping layers entirely and is more precise around
hyphenated identifiers than `\b` is.

---

## Reproducing

```bash
python scripts/build_policy_indexes.py        # integrity: 16/16
python eval/retrieval/run_retrieval_eval.py   # per-family metrics
python eval/retrieval/sweep_pipeline.py       # the F-5 table
python scripts/regenerate_evidence.py         # all of the above, one code state
python -m pytest tests/ -q                    # every regression test above
```
