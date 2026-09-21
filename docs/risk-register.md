# CredPilot — Risk Register

**System:** CredPilot underwriting copilot — multi-product agentic RAG over mortgage and education lending policy.
**Scope of this register:** the retrieval, reasoning and recommendation subsystem in this repository. It does not cover the origination platform CredPilot would sit inside, the servicing system, or the production data pipeline, none of which exist here.
**Status:** pre-production. Every figure below was measured against synthetic data, on a single machine, with no production traffic behind it.
**Last reviewed:** 2026-09-21.

Categories are OWASP Top 10 for LLM Applications (2025) and the NIST AI RMF 1.0 functions (GOVERN / MAP / MEASURE / MANAGE).

Likelihood and impact are scored **Low / Medium / High** for this system as built, not for the general class of risk. Residual risk is what remains *after* the stated mitigation, and is deliberately not zero anywhere.

---

## How to read the residual column

A residual of **Low** means the control is implemented, tested, and the test runs in CI. A residual of **Medium** means the control exists but has a known gap named in the row. A residual of **High** means the risk is accepted and not yet controlled — there are three of those, and they are listed first so they are not buried.

---

## Accepted, uncontrolled risks

| # | Risk | Category | L | I | Mitigation in place | Residual | Owner |
|---|------|----------|---|---|---------------------|----------|-------|
| R-01 | **The golden data is synthetic and internally generated.** Every accuracy figure in `reports/eval_report.json` measures agreement with a generator that wrote both the applications and the expected answers. A systematic error shared by the generator and the system would score as success. | MAP 2.3, LLM09 Misinformation | High | High | None available in this repository. The limitation is stated in `docs/model-card.md`, in the eval report payload, and here. No production decision should rest on these numbers. | **High** | Data Science |
| R-02 | **The LLM-as-judge shares a model family with the system under test.** DeepEval's faithfulness, hallucination and relevancy scores are produced by Gemini judging Gemini's own prose. A blind spot common to the family is invisible to this measurement. | MEASURE 2.5, LLM09 | High | Medium | Every judged figure has a deterministic counterpart computed by `src.narrative.verify_narrative`, which asks no model anything. Both are published side by side and the report states which to believe on disagreement. Does not remove the shared-blind-spot risk, only bounds it. | **High** | AI Evaluation |
| R-03 | **No human has reviewed the policy corpus for correctness.** The system faithfully applies rules whose substance was never validated by a credit officer. A wrong threshold in the corpus produces a confidently wrong, fully cited decision. | GOVERN 1.2, MAP 1.1 | Medium | High | Citations resolve to a specific rule, version and effective date, so a wrong answer is traceable to the rule that produced it. This makes the error auditable, not less likely. | **High** | Credit Policy |

---

## Prompt injection and untrusted input

| # | Risk | Category | L | I | Mitigation in place | Residual | Owner |
|---|------|----------|---|---|---------------------|----------|-------|
| R-04 | Applicant-supplied free text instructs the system to ignore policy, raise a threshold, or approve the file. | LLM01 Prompt Injection | High | High | `src.guardrails.sanitize` matches 13 patterns and detects all six adversarial packets committed in the corpus. Detected text sets `requires_human_review` and raises risk to HIGH. `src.context.isolate` renders applicant text **last**, inside a `<<<UNTRUSTED_APPLICANT_TEXT` fence, labelled as data. The decision is made by a deterministic rule engine that never reads the text at all, so a successful injection reaches the narrative and nothing else. | Low | Security |
| R-05 | A novel injection phrasing evades all 13 patterns. | LLM01 | Medium | Low | Pattern matching is the second line, not the first. The structural control is that no model participates in the decision: `recommendation_node` reads eligibility, risk and evidence, never applicant prose. An undetected injection can at most produce misleading narrative text on a file, and the narrative is checked against its evidence afterwards. | Low | Security |
| R-06 | Injected text persists in memory and influences a later session. | LLM01, LLM04 Data Poisoning | Medium | Medium | `ShortTermMemory` keeps the applicant trust class on every turn regardless of age — a fact "stated earlier" by an applicant is still applicant-supplied when recalled. `LongTermMemory` refuses to store `decision`, `policy`, `policy_rule`, `threshold` or `credit_score` at all, so the categories worth poisoning cannot be written. | Low | Security |
| R-07 | Injection reaches the system through a **retrieved policy document** rather than applicant text. | LLM01, LLM04 | Low | High | Not controlled by pattern matching — the corpus is trusted input. Controlled structurally: retrieved text is used to supply thresholds to a rule engine and citations to a narrative, and is never executed as instruction. A poisoned corpus is a corpus-integrity problem, addressed by R-16. | Medium | Security |

---

## Sensitive data

| # | Risk | Category | L | I | Mitigation in place | Residual | Owner |
|---|------|----------|---|---|---------------------|----------|-------|
| R-08 | Taxpayer identifiers, bank accounts or credit identifiers written to logs, traces or committed artifacts. | LLM02 Sensitive Information Disclosure | Medium | High | `src.guardrails.redaction` applies Presidio plus regex at every write boundary: agent action logs, tool-call logs, memory writes, trace export. `tests/rag/test_pii_logging.py` scans every committed artifact for identifier patterns and fails the build on a hit. | Low | Security |
| R-09 | Redaction destroys the citations it was meant to leave alone — `POL-DTI-001 v2.0` read as a driver's licence number. | LLM02 (control failure) | Medium | Medium | Observed and fixed: `US_DRIVER_LICENSE` and `US_PASSPORT` recognisers are disabled, and `_PROTECTED_IDENTIFIERS` exempts policy ids, rule ids, versions and UUIDs before Presidio runs. Regression covered by test. | Low | Security |
| R-10 | Applicant data sent to Google as part of a Gemini call. | LLM02, GOVERN 6.1 | High | Medium | Unavoidable given a hosted provider, and **bounded**: the only model call in a normal run is the narrative node. Its prompt carries computed ratios, the outcome, and retrieved policy text — not the raw packet. All names and identifiers in it have passed redaction. Data is synthetic throughout this repository; with real applicant data this row becomes a data-residency decision that is not ours to make here. | Medium | Legal / DPO |
| R-11 | Secrets committed to the repository. | LLM03 Supply Chain | Low | High | `GOOGLE_API_KEY` is read from `.env`, which is git-ignored. No key is written to any report, log or trace. | Low | Engineering |

---

## Decision integrity

| # | Risk | Category | L | I | Mitigation in place | Residual | Owner |
|---|------|----------|---|---|---------------------|----------|-------|
| R-12 | A language model produces an underwriting figure — DTI, LTV, reserves — and it is wrong. | LLM09 Misinformation | Low | High | Structurally impossible in the current graph. Every figure comes from `src.calculations`; the model receives them already computed with their formula version. `POL-DTI-001` DTI-CALC-002 forbids the alternative. | Low | Engineering |
| R-13 | The narrative cites a rule that does not support what it claims, or quotes a figure from nowhere. | LLM09, LLM05 Improper Output Handling | Medium | High | `src.narrative.verify_narrative` checks every citation and every figure in the generated prose against the evidence that was supplied, deterministically, after generation. A rationale that fails is **kept, marked unfaithful, and routed to a human** — not silently dropped, which would hide the failure, and not shipped unmarked, which would be worse. | Low | AI Evaluation |
| R-14 | Evidence from the wrong product reaches a decision — education policy applied to a mortgage. | LLM08 Vector and Embedding Weaknesses | Low | High | Product isolation is structural, not a filter: separate Chroma collections (`credpilot_mortgage_policies`, `credpilot_education_policies`) resolved before retrieval runs. There is no combined collection to leak from. `cross_product_contamination_rate` is measured at **0.00**. Where the product cannot be resolved the graph escalates rather than searching both. | Low | Retrieval |
| R-15 | A superseded policy version is applied to a file whose as-of date predates the change. | LLM09, MEASURE 2.11 | Medium | High | Effective-date windows are evaluated before ranking, and the latest *eligible* version is selected per the file's as-of date. The `APP-000055/56/57` boundary triple exercises both sides of a version change and the day it lands. | Low | Retrieval |
| R-16 | The indexed corpus drifts from the committed policy documents. | LLM04 Data Poisoning, MANAGE 4.1 | Medium | High | `index_manifest.json` records a content hash per source document; `src.rag.integrity` runs 16 checks including hash agreement, and `scripts/check_published_figures.py` plus `scripts/verify_doc_tables.py` run as tests so a documented figure cannot silently diverge from the measured one. | Low | Retrieval |
| R-27 | **The rule engine evaluates a minority of the declared rule families, so files the policy says a human must see are approved instead.** Measured: 33 of 75 mortgage and 17 of 20 education golden cases turn on a family the engine does not implement, and the dominant residual error is under-referral. | LLM06 Excessive Agency, MEASURE 2.3 | High | High | Partially controlled, and the gap is published rather than absorbed: `rule_coverage` in `reports/eval_report.json` states the ceiling per product. Retrieval is not the gap — the unimplemented rules are retrieved and cited, so an underwriter reading the output sees them. A blanket gate (refuse to auto-approve while any retrieved HARD_FAIL rule went unevaluated) was measured and rejected: 17–22 such rules are retrieved on every file including ones that correctly approve, so it would refer 100% of applications. The real fix is implementing the families, which is the first extension this system needs. | **High** | Credit Policy / Engineering |
| R-17 | Missing evidence is treated as evidence of ineligibility, producing a wrongful decline. | LLM09, GOVERN 1.1 | Medium | High | Found in testing as failure F-8: `DTI-CONV-003` was not retrieved, the engine read "0 of 2 compensating factors documented" and declined `APP-000057`. Fixed twice over — the retrieval agent now follows rule references it cannot resolve (up to 6), and the rule engine returns `INDETERMINATE` rather than `FAIL` on absent evidence, which routes to referral. `GEN-ELG-005` states the principle. | Low | Engineering |

---

## Agency and consumption

| # | Risk | Category | L | I | Mitigation in place | Residual | Owner |
|---|------|----------|---|---|---------------------|----------|-------|
| R-18 | The system issues a binding credit decision without a human. | LLM06 Excessive Agency, GOVERN 1.1 | Low | High | The system produces a **recommendation**, never a decision — the outcome vocabulary is `APPROVE_RECOMMENDATION` / `REFER_RECOMMENDATION` / `DECLINE_RECOMMENDATION`. A decline is always routed to a human (`POL-DEC-001` DEC-REC-002), as is any indeterminate result, any HIGH risk level, and any file where applicant text attempted instruction. | Low | Credit Policy |
| R-19 | An agent loop runs unbounded against one file, spending without reaching a decision. | LLM10 Unbounded Consumption | Low | Medium | Two independent guards, because they fail differently. An in-state `step_budget` of 24 lets a node see the budget running out and **halt cleanly with a reason a human can read**; LangGraph's `recursion_limit` of 40 is the external backstop for a cycle that never reaches a node able to check anything. A normal run uses 7. | Low | Engineering |
| R-20 | Reasoning tokens inflate cost invisibly — billed as output, never present in the text. | LLM10 | Medium | Low | Measured rather than assumed, and the measurement belongs to the prompt rather than the model: a short under-specified probe drew 388 of 419 output tokens as reasoning, while the actual narrative prompt — long, fully specified, decision already made — draws **zero**, output matching visible text. `thinking_budget=0` is accepted and ignored; `thinking_level="low"` is set and does move it where the model thinks at all. `reasoning_tokens` is reported as its own line in `usage_of()` and `reports/golden_signals.json`, so a future prompt change that starts drawing reasoning shows up as a figure rather than as a bill. | Low | Engineering |
| R-28 | **The checkpoint store grows without bound.** Every node writes its state, including the full retrieved evidence, and nothing prunes. Observed directly: `credpilot_checkpoints.sqlite` reached **537 MB** after a day of evaluation runs — roughly 400 assessments. | LLM10 Unbounded Consumption, MANAGE 2.3 | High | Medium | **Not controlled.** The directory is git-ignored so nothing is committed, and a single assessment is unaffected, but at this rate a production deployment fills a disk in weeks and the failure arrives as a write error mid-assessment rather than as a warning. A retention policy on the checkpointer — prune completed threads past a window — is the fix and is not written. | **Medium** | Engineering |
| R-21 | Tool errors or provider outages fail a file rather than degrading it. | MANAGE 2.3 | Medium | Medium | The narrative node degrades to a deterministic summary when Gemini is unreachable and marks the result `available: false`; a recommendation without prose is still a recommendation. Retrieval, indexing, the rule engine, the tests and the retrieval evaluation need no model at all and run unchanged. | Low | Engineering |

---

## Evaluation and governance

| # | Risk | Category | L | I | Mitigation in place | Residual | Owner |
|---|------|----------|---|---|---------------------|----------|-------|
| R-22 | Runtime code reads the golden set or an outcome table, and the evaluation measures copying. | MEASURE 2.1 | Medium | High | Enforced in two halves because the two products leak differently. Mortgage outcomes live in structured tables behind an `OUTCOME_TABLES` denylist that raises on access. Education packets embed the decision **inside the submitted JSON**, where no table guard could see it — `EMBEDDED_OUTCOME_FIELDS` strips it at the packet boundary and records what was withheld. All 200 education packets verified stripped; `tests/rag/test_no_golden_leakage.py` covers both halves. | Low | AI Evaluation |
| R-23 | A published figure in the documentation drifts from what the code actually measures. | MEASURE 4.2 | Medium | Medium | `scripts/check_published_figures.py` and `scripts/verify_doc_tables.py` re-derive every published table from the committed results and run as part of the test suite. | Low | AI Evaluation |
| R-24 | The system is scored correct for an outcome it cannot express. | MEASURE 2.3 | Medium | Low | Six golden cases expect `APPROVE_WITH_CONDITIONS`, which `recommendation_node` cannot emit. Rather than folding these into `APPROVE`, the eval keeps the class separate, reports `outcome_accuracy` over expressible cases and `outcome_accuracy_all_cases` over all of them, and names the gap. | Low | AI Evaluation |
| R-25 | Model or provider changes underneath the system without notice. | LLM03 Supply Chain, MANAGE 4.1 | High | Medium | Already observed: `gemini-2.0-flash` and `gemini-2.5-flash` were retired and began returning 404 during development. Pinned model names rot, so `gemini-flash-latest` is used and **the model that actually answered is recorded in every report**. This converts a silent behaviour change into a visible one; it does not prevent it. | Medium | Engineering |
| R-26 | Known data-quality defects in the corpus are quietly absorbed into metrics. | MEASURE 2.1, GOVERN 4.2 | High | Medium | Documented and excluded rather than absorbed: 21 of 59 education golden citations are broken (9 name rules that do not exist; 12 pair a real rule with the wrong policy), 5 education packets are cp1252 rather than UTF-8, `dti_pct` is a fraction despite its name. All recorded in `docs/rag/DATA_QUALITY_FINDINGS.md`. Fixing the source data is out of scope for this repository. | Medium | Data Science |

---

## Summary

| Residual | Count | Rows |
|---|---|---|
| High | 4 | R-01, R-02, R-03, R-27 |
| Medium | 5 | R-07, R-10, R-25, R-26, R-28 |
| Low | 19 | the remainder |

Three of the four High rows share a cause: **this system has been verified against itself.** The data is synthetic, the judge is the same model family as the generator of the prose it grades, and no credit professional has checked that the policy corpus says the right things. No amount of further engineering inside this repository will close them.

The fourth, R-27, is different in kind and is the one that *is* closable here. The engine applies a minority of the rules the corpus declares, and the resulting error runs in the under-referral direction — approving files the policy routes to a human. It is stated as High because a control that is documented but unimplemented offers no protection, and because unlike the other three it will not be fixed by better data or an independent judge. It will be fixed by writing the rules.

All four should be the first items any production readiness review takes up.

**Review cadence:** on any change to the policy corpus, the model or provider, the guardrail patterns, or the evaluation harness; and quarterly otherwise.
