# Model Card — CredPilot Underwriting Copilot

**Audience:** anyone deciding whether to rely on this system, extend it, or deploy it.

**Version:** 1.0 · **Date:** 2026-09-21 · **Status:** pre-production, synthetic data only

---

## What this system is

CredPilot is an **agentic RAG underwriting copilot** for two lending products — residential mortgage and education loans. Given an application packet, it retrieves the lending policy that governs that file on its own as-of date, computes the affordability and leverage figures, applies the rules deterministically, screens for risk, and produces an underwriting **recommendation** with the policy rules and calculations that support it.

The most important thing to understand about it is where the language model sits, because it is not where people usually assume.

```
retrieval  →  calculation  →  rule engine  →  recommendation  →  narrative
└────────────────── deterministic ──────────────────────────┘    └── Gemini ──┘
```

Gemini writes the **rationale**. It does not retrieve, rank, filter, compute, compare against a threshold, or decide. By the time it is called, the outcome already exists and is handed to it as a fact. There is no code path by which its text changes the recommendation.

This is a design choice with consequences in both directions: the decision is reproducible and auditable and cannot be argued into by prompt injection, and equally the system cannot reason its way around a rule the way a human underwriter can.

---

## Models

| Role | Model | Where it runs | Why |
|---|---|---|---|
| **Narrative rationale** | Google Gemini (`gemini-flash-latest`) | hosted API | The only approved provider (REQ-036). `-latest` rather than a pinned name because `gemini-2.0-flash` and `gemini-2.5-flash` were retired mid-development and began returning 404; every report records which model actually answered. |
| **Embeddings** | `intfloat/e5-base-v2` (768-dim) | local | Benchmarked against three alternatives on both products; it beat the expected starting model. Local, so retrieval never leaves the machine and costs nothing per query. |
| **Reranking** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | local | Measured gain over fusion alone. |
| **Lexical retrieval** | BM25 (`rank-bm25`) | local | Policy text is dense with exact identifiers — `DTI-CONV-001`, `HCLTV`, `I-94` — that embeddings recover unreliably. |
| **Evaluation judge** | Gemini, via DeepEval | hosted API | Evaluation only. Never part of a decision. |

**No Claude. No OpenAI. No hosted embedding or reranking service.** Enforced by `tests/rag/test_stack_boundaries.py`, which scans every runtime module's imports and the dependency manifest.

### Generation settings

`temperature=0` — a rationale that changes between runs cannot be reconciled with the trace that produced it.

`thinking_level="low"` — Gemini flash reasons before answering and bills the reasoning as output, where it never appears in the text. How much it spends is allocated dynamically by how hard it judges the task, so the figure is a property of the prompt rather than of the model: a two-sentence probe drew **388 of 419** output tokens as reasoning, while the actual narrative prompt — long, fully specified, decision already made — draws **none**, with output tokens matching the visible text. `thinking_budget=0` is accepted and effectively ignored; `thinking_level` does move it where the model chooses to think at all. `reasoning_tokens` is reported as its own line in `reports/golden_signals.json` so the figure is visible either way.

---

## Data

**Entirely synthetic. No real applicant data of any kind.**

| | Mortgage | Education |
|---|---|---|
| Policy documents | 42, six policies at two versions | 12 |
| Rules | ~203 | 72 |
| Chunks indexed | 329 | ~100 |
| Applications | 75 | 200 |
| Golden evaluation cases | 75 | 20 |
| Collection | `credpilot_mortgage_policies` | `credpilot_education_policies` |

Product isolation is **structural rather than a filter**: two separate Chroma collections, resolved before retrieval runs. There is no combined collection to leak from, and `cross_product_contamination_rate` measures 0.00.

### Known data defects

Documented rather than absorbed into metrics (`docs/rag/DATA_QUALITY_FINDINGS.md`):

- 21 of 59 education golden citations are broken — 9 name rules that do not exist (`EDU-CERT-001`, `EDU-REFI-001`, `EDU-AGG-001`, `EDU-FRAUD-001`); 12 pair a real rule with the wrong policy.
- 5 education application packets are cp1252-encoded rather than UTF-8.
- `dti_pct` is stored as a fraction despite its name.
- Every education packet embeds the generator's own decision inline. It is **stripped at the packet boundary** before runtime sees it (`EMBEDDED_OUTCOME_FIELDS`); all 200 verified.

---

## Intended use

**Intended.** Producing a first-pass underwriting recommendation with resolvable citations, for a human underwriter to review; surfacing the policy that governs a file on a given date; showing which rule and threshold a figure was tested against.

**Not intended.** Issuing a credit decision. Setting pricing. Replacing an underwriter. Operating on real applicant data in its current state. Any jurisdiction, product or policy corpus other than the two synthetic ones it was built against.

**Out of scope entirely.** Servicing, collections, fraud investigation, and any use of the output as an adverse-action notice — the system produces reason material, not a compliant notice.

---

## Performance

Measured end-to-end over both products' golden sets by `eval/agent/run_agent_eval.py`. The live figures are in **[`reports/eval_report.json`](../reports/eval_report.json)**, with per-case detail in `reports/eval_cases.jsonl` and the operational view in `reports/golden_signals.json`.

**All headline figures are macro-averaged across the two products.** Mortgage brings 75 cases to education's 20, so a pooled mean would be a mortgage score with a rounding error attached, and a total failure on education would barely move it.

### How to read the accuracy figures

Two are published, and the difference between them is not a rounding detail:

- `outcome_accuracy` — over cases whose expected outcome the system **can** express.
- `outcome_accuracy_all_cases` — over every case, including six that expect `APPROVE_WITH_CONDITIONS`, which `recommendation_node` cannot emit and therefore always misses.

Folding those six into `APPROVE` would score the system correct for an answer it is structurally incapable of giving. They are kept as their own class and counted as `cases_with_inexpressible_expectation`.

### Grounding is measured twice, deliberately

| | Method | Asks a model? |
|---|---|---|
| `narrative_faithfulness_deterministic` | `src.narrative.verify_narrative` extracts every citation and figure from the prose and checks each appears in the evidence supplied | No |
| `judge_faithfulness`, `judge_hallucination_rate`, `judge_answer_relevancy` | DeepEval, judged by Gemini | Yes |

**Where the two disagree, the deterministic one governs.** The judge shares a model family with the system it is grading.

The deterministic checks run on **every** case. The judged metrics run on a balanced sample — 20 per product, so education's 20 cases are all judged and neither product dominates — because DeepEval makes nine or ten model calls per case and judging all 95 triples the run for no change in what the numbers mean. `judged_cases` states the denominator, and `judge.sampled` records that a sample was taken.

One direction trap worth naming: DeepEval 4.x reports `HallucinationMetric` in the same direction as its other metrics — **1.0 means grounded**, 0.0 means contradicted. It previously reported the proportion of violations. The report therefore publishes `judge_hallucination_score` (raw, 1 is good) and derives `judge_hallucination_rate = 1 − score` (0 is good) beside it, because publishing the raw score under the name "hallucination rate" would invert it.

### One metric is mortgage-only, and deliberately so

`human_review_agreement` compares the system's `requires_human_review` flag against the golden set's. Mortgage records that flag explicitly in `decisions.csv`. The education golden set does not record it at all.

It would be easy to derive one — treat every `REFER` expectation as requiring review — but that would be inventing ground truth and then scoring against it. The metric is therefore reported for mortgage and `null` for education, and the macro average is taken over the products that actually have a value. A `null` that says "not recorded" is worth more than a number that says "assumed".

### What the committed run does and does not contain

The committed evaluation ran all 95 cases with narratives generated by
`gemini-flash-latest`, and the grounding figures are measured over those
narratives. The **text** of them is not in `reports/eval_cases.jsonl`: the field
that records it was added after this run, and the model quota was exhausted before
another could be completed. Each case record carries what the faithfulness verdict
rested on — the citations used and any unsupported citation or figure — so the
metric is auditable, but a reader cannot re-read the prose itself.

The two worked examples in `reports/assessments/` were regenerated after the quota
ran out and therefore carry the deterministic summary rather than a generated
rationale. They say so in the file: `available: false`, with the reason.

The next run closes both gaps without any change to the system.

### Targets

| Metric | Target | Source |
|---|---|---|
| `citation_validity` | 1.00 | REQ-030, the Citation-Resolves Rule |
| `cross_product_contamination_rate` | 0.00 | product isolation requirement |
| `hallucination_rate` | 0.00 | REQ-097 |

Met or missed, the measurement is published as measured.

### Cost and latency

Roughly one Gemini call per assessment. The deterministic pipeline — retrieval, calculation, rules — is the faster half and does not vary with a provider; the single model call dominates the tail. Per-assessment token and cost figures are in `reports/golden_signals.json`, estimated from published per-million rates and labelled as an estimate rather than a billing record.

---

## Limitations

Ordered by how much they should affect your confidence.

1. **The data is synthetic and internally generated.** Every accuracy figure measures agreement with a generator that wrote both the applications and the expected answers. A systematic error shared by the generator and the system would score as success. This is the single largest limitation and no amount of further engineering inside this repository closes it. (`R-01`)

2. **The judge shares a model family with the system under test.** (`R-02`)

3. **No credit professional has validated the policy corpus.** The system applies its rules faithfully; whether those rules say the right things is unverified. A wrong threshold produces a confidently wrong, fully cited decision. (`R-03`)

4. **The rule engine evaluates a minority of the declared rule families, and that caps accuracy.** Mortgage declares 26 families; the engine applies four, the guardrails a fifth and the routing table a sixth. Education is thinner still. Published per product in `reports/eval_report.json` under `rule_coverage`:

   | | golden cases | needing a rule family the engine does not implement |
   |---|---|---|
   | Mortgage | 75 | **33 (44%)** |
   | Education | 20 | **17 (85%)** |

   **Retrieval is not the gap.** Both corpora are indexed in full, and rules in the unimplemented families are retrieved, ranked and cited exactly like the others — an underwriter reading the output sees them. What is missing is code comparing them against a threshold. A case whose golden outcome turns on one cannot be scored correct except by coincidence, which makes this the ceiling on `outcome_accuracy` rather than an excuse for it, and the first thing to extend. The dominant residual error is **under-referral**: the system approves a file the policy says a human must see.

5. **No fairness or disparate-impact testing has been performed.** The mortgage corpus has a `borrower_demographics` table and it sits on the outcome denylist — correct for decisioning, and it also means no bias analysis exists. NIST MEASURE 2.11 and EU AI Act Art. 10 are not met.

6. **`APPROVE_WITH_CONDITIONS` cannot be expressed.** Six golden cases expect it. Those files land as a refer, which is the safe direction but not the right answer.

7. **Three of the thirteen `UWR-HRV-001` review triggers cannot be evaluated** — no automated-underwriting result, exception-request field or valuation finding exists in any committed table. They are reported as `unevaluable` rather than silently passing. The list was five until the structured inputs were checked properly; an unsourced large deposit and an evidence conflict both turned out to be recorded, and are now evaluated.

8. **The model provider can change underneath the system.** Already observed: two model names were retired mid-development. Recording which model answered converts a silent behaviour change into a visible one; it does not prevent it.

9. **Education has only one version of each policy**, so temporal version selection is exercised in depth on mortgage only.

---

## Known failure modes

Thirteen real failures found while building this, each with evidence, root cause, fix and before/after measurement, in **[`docs/failure-analysis.md`](failure-analysis.md)**. The ones that bear on trusting the output:

| | Failure | Why it mattered |
|---|---|---|
| **F-8** | **Wrongful decline.** `DTI-CONV-003` was not retrieved, so the engine read "0 of 2 compensating factors documented" and declined a file it should have referred. | Missing evidence was being treated as evidence of ineligibility — the most consequential failure mode a system like this has. Fixed twice over: the retrieval agent now follows rule references it cannot resolve, and the engine returns `INDETERMINATE` rather than `FAIL` on absent evidence (`GEN-ELG-005`). |
| **F-1** | Overview chunks starved their own policy's rules out of the evidence slate. | Correct rules were excluded entirely. Fixed with a separate overview budget; rule recall@5 0.9546 → 0.9687. |
| **F-2** | PII redaction destroyed citations — `POL-DTI-001 [REDACTED_US_DRIVER_LICENSE].0 rule DTI-CONV-001`. | A safety control breaking the auditability another control depends on. |
| **F-7** | The retrieval funnel silently truncated: `top_k=15` returned 4. | Silent under-delivery, not an error. Fixed with width floors. |
| **F-4** | The evaluation was measuring slot count rather than ranking quality. | The measurement, not the system, was wrong — which is worse, because it hides everything else. |

Five further defects were found by running the whole system end to end against both golden sets for the first time — which is the only thing that would have found any of them — and all five are fixed (F-9 to F-13):

| | Failure | Why it mattered |
|---|---|---|
| **F-10** | **Every refinance was declined** for the whole lien payoff as cash. `AST-FTC-001` says "any lien payoff *not financed by the new loan*"; the qualifier was dropped. One file was declined for a $289,234 shortfall it did not have. | Wrongful declines at volume. Purchases were unaffected, which is why spot checks missed it. |
| **F-11** | **The evaluation replayed its previous run.** A fixed checkpoint thread meant a 13-second case returned in 0.2 seconds with no retrieval, reporting a verdict reached before the rule engine was fixed. | A bug in the instrument, not the system — worse, because the numbers stayed plausible. |
| **F-12** | **All 200 education packets carried the generator's decision** — outcome, risk grade, approved amount — into runtime state. | Label leakage. The outcome boundary had been built for mortgage, where outcomes live in separate tables. |
| **F-9** | **Reserves were counted before the money left the account**, contradicting `AST-RSV-001`. One file reported 40.7 months where the truth was 9.6. | Every reserve figure in the system was overstated. |
| **F-13** | **The eligibility engine evaluated only DTI.** A file could clear its DTI ceiling and be approved with a failing credit score, no reserves and a six-figure cash shortfall. | Three knockout rules added, each version-aware across the 2026-07-01 boundary. |

---

## Ethical and safety considerations

**Human oversight is structural, not advisory.** Declines, indeterminate results, HIGH risk, detected injection attempts, unfaithful rationales and budget halts all route to `human_review`. No graph edge carries a decline to `END`. See `docs/output-risk.md`.

**Applicant text is data, never instruction.** It is quarantined at intake, kept in its own compartment, rendered last inside a labelled fence, and never read by the rule engine at all. Thirteen injection patterns detect all six committed adversarial packets, but the structural control is that a successful injection reaches only the narrative — and the narrative is checked against its evidence afterwards.

**Memory refuses to hold what it should not.** A prior decision is not evidence for a new application; policy is retrieved with an effective date rather than cached; a credit figure goes stale silently. `LongTermMemory` refuses all of them by kind. Recall is scoped to one subject, and `forget()` erases a data principal completely in one operation.

**Missing evidence never becomes a negative result.** `GEN-ELG-005`, learned the hard way via F-8.

---

## Reproducing this

```bash
python scripts/build_policy_indexes.py        # build both products' indexes
python -m eval.retrieval.run_retrieval_eval   # retrieval metrics (no model needed)
python -m eval.agent.run_agent_eval           # end-to-end + LLM-as-judge (needs GOOGLE_API_KEY)
python scripts/build_golden_signals.py        # operational signals
python scripts/build_dashboard.py             # the chart
pytest -m "not slow"                          # the suite
```

Retrieval, the indexes, the tests and the retrieval evaluation need **no** model credential and run unchanged without one. Only the narrative and the judge require Gemini.

Full operational detail in [`docs/rag/RUNBOOK.md`](rag/RUNBOOK.md).

---

## Governance

| Document | What it covers |
|---|---|
| [`docs/risk-register.md`](risk-register.md) | 28 risks, OWASP LLM Top 10 + NIST AI RMF, with residual risk stated per row |
| [`docs/compliance.md`](compliance.md) | EU AI Act, NIST AI RMF, India DPDP — what is addressed, where the evidence is, and what is not met |
| [`docs/output-risk.md`](output-risk.md) | Three output tiers and what gates each |
| [`docs/failure-analysis.md`](failure-analysis.md) | Eight real failures with before/after |

---

**Contact.** This is a portfolio/reference implementation. Issues and questions via the repository: `KrishnaAnnavaram/CredPilot`.
