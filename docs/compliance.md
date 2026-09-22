# CredPilot — Regulatory Mapping

How this system addresses the obligations that apply to automated credit decisioning, and **where the evidence is**. Every row points at something in the repository that can be opened and checked; rows with no evidence say so plainly rather than claiming coverage.

**Audience:** compliance, legal and audit.

**Standing caveat for every row below.** This is a pre-production system running on synthetic data, on one machine, with no production traffic. Nothing here constitutes a compliance assessment of a deployed system, and several obligations — DPIA, registration, post-market monitoring, human-reviewer competence — can only be met by an operator, not by a repository. Those are marked **Operator obligation**.

---

## EU AI Act

Creditworthiness assessment of natural persons is **Annex III(5)(b)** — high-risk. The obligations below are the ones that fall on a provider building the system.

| Article | Obligation | How CredPilot addresses it | Evidence |
|---|---|---|---|
| **Art. 9** — Risk management system | Identify and mitigate risks across the lifecycle | 33-row register scoring likelihood, impact, mitigation and residual, with risks recorded as accepted or only partly controlled rather than quietly closed. Five rows (R-29 to R-33) cover the surface the conversational UI and the MCP server added: an injection typed directly at the system, an MCP client the host does not control, sampling moving generation off the approved provider, elicitation being used to ask for something it should not, and an external call that hangs. | [`docs/risk-register.md`](risk-register.md) |
| **Art. 10** — Data governance | Training/validation data relevant, representative, examined for bias | **Partially addressed.** Data is synthetic and internally generated; its defects are documented rather than hidden (21 of 59 education golden citations broken, 5 packets mis-encoded). No bias examination has been performed — see Gaps. | [`docs/rag/DATA_QUALITY_FINDINGS.md`](rag/DATA_QUALITY_FINDINGS.md) |
| **Art. 11** — Technical documentation | System description, architecture, performance, limitations | Architecture, requirements mapping, temporal retrieval design, ablation and benchmark results, failure analysis, runbook | [`docs/rag/`](rag/), [`docs/model-card.md`](model-card.md) |
| **Art. 12** — Record-keeping | Automatic logging of events over lifetime | Every agent action and tool call logged to `logs/agent_actions.jsonl` and `logs/tool_calls.jsonl` with actor, decision, application, product and detail; OpenTelemetry/OpenInference spans exportable to Phoenix | `src/observability/`, `scripts/export_traces.py` |
| **Art. 13** — Transparency to deployers | Deployers can interpret output and use it appropriately | Three-tier output classification stating what each tier means and what gates it; every recommendation carries resolvable citations and the formula version behind each figure | [`docs/output-risk.md`](output-risk.md) |
| **Art. 14** — Human oversight | Effective oversight by natural persons; ability to override | **Structural.** The system emits recommendations, never decisions. Declines, indeterminate results, HIGH risk, detected injection, unfaithful rationales, failed response validation and budget halts all route to `human_review`, and no graph edge carries a decline to `END`. The Supervisor adds two more paths to a person: a request that asks for an override, a decision change or a dispute is routed to `HUMAN_REVIEW` before any specialist runs, and a request the system cannot resolve after two clarification rounds goes to a person rather than being asked a third time. | `src/graph.py`, `src/supervisor.py`, [`docs/output-risk.md`](output-risk.md) |
| **Art. 15** — Accuracy, robustness, cybersecurity | Appropriate accuracy; resilience to error and manipulation | Macro-averaged accuracy, citation validity and grounding measured over both products' golden sets by an evaluation that enters the graph at its real entry point, so Supervisor routing accuracy is scored too. Injection resistance covering all six committed adversarial packets and the conversational surface. Three independent loop guards (in-state budget, LangGraph recursion limit, clarification-round cap). Every external call carries a deadline and a bounded retry count, and a failure comes back as a value so a node degrades rather than dying. | `reports/eval_report.json`, `src/guardrails/sanitize.py`, `src/resilience.py`, `tests/test_loops.py`, `tests/test_resilience.py` |
| **Art. 26** — Deployer obligations | Use per instructions, assign competent oversight, monitor | **Operator obligation.** Not satisfiable from this repository. | — |
| **Art. 27** — Fundamental rights impact assessment | FRIA before putting into service | **Operator obligation.** Required for a credit institution deploying this. Not performed. | — |
| **Art. 86** — Right to explanation | Explanation of the role of the system in a decision that adversely affects a person | Every recommendation carries the rules it relied on, each resolving to a policy, version and effective date; the rationale names them in prose; the deterministic faithfulness check confirms the prose did not invent any | `src/narrative.py`, `reports/eval_cases.jsonl` |

---

## NIST AI RMF 1.0

| Function | Subcategory | How addressed | Evidence |
|---|---|---|---|
| **GOVERN 1.1** | Legal requirements understood and managed | Decision authority bounded in code: the vocabulary is `*_RECOMMENDATION`, and `POL-DEC-001` DEC-REC-002 forces every decline to a human | `src/graph.py` |
| **GOVERN 1.2** | Trustworthiness characteristics integrated | Named in the register with owners; residual risk stated per row | [`docs/risk-register.md`](risk-register.md) |
| **GOVERN 4.2** | Risks documented and communicated | Data-quality defects published as findings and excluded from metrics rather than absorbed into them | [`docs/rag/DATA_QUALITY_FINDINGS.md`](rag/DATA_QUALITY_FINDINGS.md) |
| **GOVERN 6.1** | Third-party risks addressed | One approved provider (Gemini), one module through which every model call passes, the answering model recorded in every report | `src/llm.py` |
| **MAP 1.1** | Context established | Two lending products, their corpora, their rule vocabularies and their separate golden sets | [`docs/rag/ARCHITECTURE.md`](rag/ARCHITECTURE.md) |
| **MAP 2.3** | Scientific integrity of the AI system | **Limitation disclosed, not solved.** The data is synthetic and self-generated; agreement with the generator is not correctness. R-01, residual High. | [`docs/risk-register.md`](risk-register.md), [`docs/model-card.md`](model-card.md) |
| **MAP 5.1** | Likelihood and magnitude of impact | Three output tiers with impact reasoning and per-tier gating | [`docs/output-risk.md`](output-risk.md) |
| **MEASURE 2.1** | Test sets not leaked into the system | Two-sided boundary: `OUTCOME_TABLES` raises on access for mortgage; `EMBEDDED_OUTCOME_FIELDS` strips the decision education packets carry inline. All 200 education packets verified stripped. | `src/application_context.py`, `tests/rag/test_no_golden_leakage.py` |
| **MEASURE 2.3** | Performance measured against requirements | Macro-averaged across products so the larger product cannot mask the smaller; inexpressible outcomes reported separately rather than folded in | `reports/eval_report.json` |
| **MEASURE 2.5** | Validity under expected conditions | Deterministic and LLM-judged grounding published side by side, with the shared-model-family caveat stated in the report payload itself | `eval/agent/`, `reports/eval_report.json` |
| **MEASURE 2.7** | Security and resilience evaluated | Injection detection across all six committed adversarial packets; PII scan over every committed artifact fails the build on a hit | `tests/rag/test_pii_logging.py`, `src/guardrails/` |
| **MEASURE 2.11** | Fairness and bias evaluated | **Not performed.** See Gaps. | — |
| **MEASURE 4.2** | Measurement results documented and current | Published figures re-derived from committed results by scripts that run as tests, so documentation cannot silently drift. Evidence *citations* are checked separately and for a different failure: the artifacts they point into are regenerated, so a citation can stop resolving without any figure changing (R-34) | `scripts/check_published_figures.py`, `scripts/verify_doc_tables.py`, `scripts/verify_evidence_citations.py` |
| **MANAGE 2.3** | Mechanisms to sustain value under failure | Narrative degrades to a deterministic summary on provider outage; retrieval, indexing, rules, tests and retrieval evaluation need no model at all | `src/narrative.py` |
| **MANAGE 4.1** | Post-deployment monitoring | **Partial.** Traces, action logs and golden signals exist; no production monitoring, drift detection or alerting. Operator obligation. | `reports/golden_signals.json` |

---

## India DPDP Act 2023

Applies if CredPilot processes the personal data of data principals in India.

| Section | Obligation | How addressed | Evidence |
|---|---|---|---|
| **S. 4 / 6** | Lawful basis and consent | **Operator obligation.** Consent capture belongs to the origination platform, not this subsystem. | — |
| **S. 8(3)** | Accuracy where data is used to make a decision | Figures computed deterministically with a stated formula version; thresholds retrieved with an effective date; absent evidence returns `INDETERMINATE` rather than a negative finding | `src/calculations.py`, `src/rules.py` |
| **S. 8(4)** | Reasonable security safeguards | Redaction at every write boundary (Presidio + regex); applicant text quarantined and compartmentalised as untrusted; no secret written to any artifact; local embeddings, no external embedding calls | `src/guardrails/redaction.py`, `src/context/isolate.py` |
| **S. 8(5)** | Erasure when purpose is served | `LongTermMemory.forget(subject_id)` erases everything held for one data principal as a single operation, verified not to touch another's | `src/memory/long_term.py`, `tests/test_memory_persistence.py` |
| **S. 8(6)** | Breach notification | **Operator obligation.** | — |
| **S. 11** | Right to access information about processing | Every recommendation is reconstructable from logged actions, retrieved evidence and the checkpointed state | `logs/`, `data/memory/credpilot_checkpoints.sqlite` |
| **S. 12** | Right to correction | Memory is keyed and upserted, so a corrected fact replaces the earlier one across sessions rather than accumulating beside it | `tests/test_memory_persistence.py` |
| **S. 16** | Cross-border transfer | **Disclosed, not resolved.** Narrative generation calls Gemini, a hosted service. Data is synthetic here; with real applicant data this becomes a transfer decision for the operator. R-10. | [`docs/risk-register.md`](risk-register.md) |

---

## Data minimisation in the model prompt

Worth stating explicitly, because it is the question most often asked of a RAG system handling credit files: **the raw application packet is never sent to the model.**

The single model call in a normal run is the narrative node. Its prompt is assembled by `src.context.build_context` and contains:

- computed ratios and amounts, with their formula version
- the retrieved policy evidence that was selected for the role
- the outcome, eligibility status, risk level and review reasons — as facts
- applicant free text, if any, redacted and fenced as untrusted data

It does not contain taxpayer identifiers, account numbers, the borrower's address, employer details, or the document set. Everything crossing that boundary has passed `redact_text`.

---

## Gaps

Stated rather than implied, because a compliance map that lists only what is covered is misleading.

1. **The rule engine implements a minority of the declared rule families.** Mortgage declares 26; the engine applies four, the guardrails a fifth, the routing table a sixth. 33 of 75 mortgage and 17 of 20 education golden cases turn on a family it does not implement, and the residual error runs toward **under-referral** — approving files the policy routes to a human. This is an Art. 15 (accuracy) and Art. 14 (human oversight) limitation, published per product as `rule_coverage` in `reports/eval_report.json` rather than absorbed into the accuracy figure. Retrieval is not the gap: the unimplemented rules are retrieved and cited, so a reviewer reading the output sees them.

2. **No fairness or disparate-impact testing.** The mortgage corpus has a `borrower_demographics` table, and it is on the `OUTCOME_TABLES` denylist — runtime code cannot read it, which is correct for decisioning and also means no bias analysis has been run. MEASURE 2.11 and Art. 10 are not met. This is the largest gap in the register.
3. **No DPIA or FRIA.** Operator obligations; not performable from a repository.
4. **No production monitoring or drift detection.** Golden signals are a point-in-time measurement, not a monitor.
5. **The policy corpus has not been validated by a credit professional.** The system applies its rules faithfully; whether those rules are right is unverified (R-03, residual High).
6. **Accuracy figures measure agreement with a synthetic generator**, not correctness (R-01, residual High).
7. **Human-reviewer competence and override logging are not implemented here.** The graph routes to `human_review` and terminates; what a human then does is outside this subsystem.

---

**Last reviewed:** 2026-09-21. Re-review on any change to the policy corpus, the model provider, the guardrails or the evaluation harness.
