# CredPilot — Verbatim Source Requirements

**Source document:** `source_document/Loan_Origination_Underwriting_Copilot_Merged.docx`

**Document title as printed:** Agentic AI Engineer Pathway — Capstone Hackathon / Loan Origination & Underwriting Copilot

**Document subtitle as printed:** Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation

---

## HOW TO READ THIS FILE

This file is the **only** source of truth for the CredPilot requirements validation suite.

* Every `~~~text` block below is an **exact, character-for-character quotation** of the source document.
* Requirement IDs (`REQ-001`, `REQ-002`, ...) are **external metadata assigned by the QA layer**. They do not appear in the source document and they do not alter the source text in any way.
* `Source location`, `Source type`, `Requirement class` and `Category` are **external metadata** as well.
* Table rows are rendered as their cells joined by ` | ` in left-to-right column order. The **cell text itself is verbatim**. See `source_document/EXTRACTION_NOTE.md`.
* Nothing in the source document has been paraphrased, summarised, corrected, reworded, reordered or omitted.

**Requirement class** values (external metadata, used only for report grouping — never to weaken a test):

* `IMPLEMENTATION` — the statement constrains the CredPilot deliverable itself. Counts towards the mandatory pass/fail gate.
* `OPTIONAL` — the **source text itself** marks the item optional / bonus / good-to-have.
* `ENGAGEMENT` — the statement describes the engagement, the grading process or the evaluator's own behaviour rather than the CredPilot deliverable.

---

## REQ-001

- **Source location:** Document title block — banner line above the title (first line of the document)
- **Source type:** SENTENCE
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Agentic AI Engineer Pathway — Capstone Hackathon
~~~

## REQ-002

- **Source location:** Document title block — document title
- **Source type:** SENTENCE
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Loan Origination & Underwriting Copilot
~~~

## REQ-003

- **Source location:** Document title block — subtitle line beneath the title
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

## REQ-004

- **Source location:** Section 1. Project Identity — table row 1
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Business Case Title | Loan Origination & Underwriting Copilot
~~~

## REQ-005

- **Source location:** Section 1. Project Identity — table row 2
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Business Case ID | BC-AAIE-HACK-02
~~~

## REQ-006

- **Source location:** Section 1. Project Identity — table row 3
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Domain | Banking & Finance
~~~

## REQ-007

- **Source location:** Section 1. Project Identity — table row 4
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Project Type | Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon
~~~

## REQ-008

- **Source location:** Section 2. Engagement Overview — table row 1
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Duration | 20 hours
~~~

## REQ-009

- **Source location:** Section 2. Engagement Overview — table row 2
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Format | Team of 2–4
~~~

## REQ-010

- **Source location:** Section 2. Engagement Overview — table row 3
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

## REQ-011

- **Source location:** Section 2. Engagement Overview — table row 4
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

## REQ-012

- **Source location:** Section 2. Engagement Overview — table row 5
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

## REQ-013

- **Source location:** Section 2. Engagement Overview — table row 6
- **Source type:** TABLE_ROW
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

## REQ-014

- **Source location:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 1
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

## REQ-015

- **Source location:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 2
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Every claim is scored from committed evidence.
~~~

## REQ-016

- **Source location:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 1
- **Source type:** SENTENCE
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
What is not evaluated: the visual polish of any interface, generic unit-test volume, or which optional deployment path you use.
~~~

## REQ-017

- **Source location:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 2
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
Containerized/cloud deployment is out of scope for this cut.
~~~

## REQ-018

- **Source location:** Section 3.1 Problem — sentence 1
- **Source type:** SENTENCE
- **Requirement class:** ENGAGEMENT
- **Category:** underwriting

**Exact source text (verbatim):**

~~~text
A retail bank's loan officers spend most of an application on manual work: gathering the applicant's documents, checking eligibility against product policy, computing affordability, screening for risk flags, and drafting a decision rationale.
~~~

## REQ-019

- **Source location:** Section 3.1 Problem — sentence 2
- **Source type:** SENTENCE
- **Requirement class:** ENGAGEMENT
- **Category:** policy

**Exact source text (verbatim):**

~~~text
Rules are scattered across policy PDFs and change often, so decisions are inconsistent and slow.
~~~

## REQ-020

- **Source location:** Section 3.1 Problem — sentence 3
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** underwriting

**Exact source text (verbatim):**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

## REQ-021

- **Source location:** Section 3.2 Your Role — sentence 1
- **Source type:** SENTENCE
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Agentic AI Engineer.
~~~

## REQ-022

- **Source location:** Section 3.2 Your Role — sentence 2
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** orchestration

**Exact source text (verbatim):**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

## REQ-023

- **Source location:** Section 3.3 Expected Solution — lead-in sentence
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
A working, instrumented multi-agent application delivered as a Git repository that demonstrates:
~~~

## REQ-024

- **Source location:** Section 3.3 Expected Solution — bullet 1
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** orchestration

**Exact source text (verbatim):**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

## REQ-025

- **Source location:** Section 3.3 Expected Solution — bullet 2
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

## REQ-026

- **Source location:** Section 3.3 Expected Solution — bullet 3
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

## REQ-027

- **Source location:** Section 3.3 Expected Solution — bullet 4
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

## REQ-028

- **Source location:** Section 3.3 Expected Solution — bullet 5
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** evaluation

**Exact source text (verbatim):**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

## REQ-029

- **Source location:** Section 3.4 Applicable Rules — bullet 1 (Evidence-in-Repo Rule)
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Evidence-in-Repo Rule. Only committed artifacts are scored. A claim with no committed evidence scores zero; an evidence artifact with no producing code (a metric, trace or log a team could hand-write) is heavily discounted.
~~~

## REQ-030

- **Source location:** Section 3.4 Applicable Rules — bullet 2 (Citation-Resolves Rule)
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Citation-Resolves Rule. Wherever a document cites evidence (a Phoenix run/span id, a log record, a control file), the citation must resolve to a committed artifact. Unresolvable citations are treated as missing.
~~~

## REQ-031

- **Source location:** Section 3.4 Applicable Rules — bullet 3 (Synthetic-Data Rule)
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

## REQ-032

- **Source location:** Section 3.4 Applicable Rules — bullet 4 (Open-Source & Gemini-Only Rule)
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

## REQ-033

- **Source location:** Section 3.4 Applicable Rules — bullet 5 (Reproducibility Rule)
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs.
~~~

## REQ-034

- **Source location:** Section 4. Technology & Framework Stack — lead-in paragraph
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

## REQ-035

- **Source location:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

## REQ-036

- **Source location:** Section 4. Technology & Framework Stack — table row "LLM Provider"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
LLM Provider | Google Gemini (API) — the only approved provider; not Claude
~~~

## REQ-037

- **Source location:** Section 4. Technology & Framework Stack — table row "Interoperability"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
Interoperability | MCP Python SDK (stdio) + langchain-mcp-adapters
~~~

## REQ-038

- **Source location:** Section 4. Technology & Framework Stack — table row "Memory"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
Memory | langgraph-checkpoint-sqlite (SQLite file) + LangMem
~~~

## REQ-039

- **Source location:** Section 4. Technology & Framework Stack — table row "Retrieval"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** policy

**Exact source text (verbatim):**

~~~text
Retrieval | Chroma or FAISS + Sentence-Transformers (local)
~~~

## REQ-040

- **Source location:** Section 4. Technology & Framework Stack — table row "Observability (mandated)"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

## REQ-041

- **Source location:** Section 4. Technology & Framework Stack — table row "Evaluation"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** evaluation

**Exact source text (verbatim):**

~~~text
Evaluation | DeepEval (LLM-as-judge = Gemini) · pytest for agent tests
~~~

## REQ-042

- **Source location:** Section 4. Technology & Framework Stack — table row "Security"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

## REQ-043

- **Source location:** Section 4. Technology & Framework Stack — table row "Interface" (continuation table)
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** functional

**Exact source text (verbatim):**

~~~text
Interface | CLI (required) · FastAPI streaming (optional / bonus)
~~~

## REQ-044

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-01
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** eligibility

**Exact source text (verbatim):**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

## REQ-045

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-02
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** affordability

**Exact source text (verbatim):**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

## REQ-046

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-03
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** underwriting

**Exact source text (verbatim):**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

## REQ-047

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-04
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** workflow

**Exact source text (verbatim):**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

## REQ-048

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-05
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** functional

**Exact source text (verbatim):**

~~~text
AC-05 | The copilot maintains context — it uses facts stated earlier in the interaction and recalls prior-session context on a return visit.
~~~

## REQ-049

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-06
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

## REQ-050

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-07
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

## REQ-051

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-08
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
AC-08 | docs/failure-analysis.md documents ≥ 3 real failures from your own runs, each citing the Phoenix run_id + span_id (or a tool-log record) that shows it, plus root cause and fix.
~~~

## REQ-052

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-09
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

## REQ-053

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-10
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
AC-10 | Input/output guardrails wired into the agent's I/O path, and a machine-generated audit trail of agent actions (logs/agent_actions.jsonl).
~~~

## REQ-054

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-11
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

## REQ-055

- **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-12
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** evaluation

**Exact source text (verbatim):**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

## REQ-056

- **Source location:** Section 5.2 Non-Functional Requirements — table row NFR-01
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

## REQ-057

- **Source location:** Section 5.2 Non-Functional Requirements — table row NFR-02
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

## REQ-058

- **Source location:** Section 5.2 Non-Functional Requirements — table row NFR-03
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
NFR-03 | Untrusted free-text applicant-supplied content is quarantined and never treated as instructions.
~~~

## REQ-059

- **Source location:** Section 5.2 Non-Functional Requirements — table row NFR-04
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
NFR-04 | Agent pipeline uses async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions).
~~~

## REQ-060

- **Source location:** Section 5.2 Non-Functional Requirements — table row NFR-05
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
NFR-05 | All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext.
~~~

## REQ-061

- **Source location:** Section 5.2 Non-Functional Requirements — table row NFR-06
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
NFR-06 | Evidence artifacts (traces, logs, reports) are machine-generated by committed code; the code that produced each is committed alongside it.
~~~

## REQ-062

- **Source location:** Section 6.1 In Scope — bullet 1
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** orchestration

**Exact source text (verbatim):**

~~~text
The LangGraph multi-agent copilot (foundation) plus its full observability, cost-governance, security, governance and evaluation surface.
~~~

## REQ-063

- **Source location:** Section 6.1 In Scope — bullet 2
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

## REQ-064

- **Source location:** Section 6.1 In Scope — bullet 3
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** functional

**Exact source text (verbatim):**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

## REQ-065

- **Source location:** Section 6.2 Out of Scope (this cut) — bullet 1
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
Containerized / cloud deployment (Docker, Rancher, k8s) — deferred; do not spend hackathon time on it.
~~~

## REQ-066

- **Source location:** Section 6.2 Out of Scope (this cut) — bullet 2
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
Real credit-bureau or core-banking integrations — use synthetic application and policy data.
~~~

## REQ-067

- **Source location:** Section 6.2 Out of Scope (this cut) — bullet 3
- **Source type:** BULLET
- **Requirement class:** ENGAGEMENT
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
Front-end visual polish; generic unit-test volume for its own sake.
~~~

## REQ-068

- **Source location:** Section 6.2 Out of Scope (this cut) — bullet 4
- **Source type:** BULLET
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
Advanced OAuth flows and live secrets-rotation infrastructure (document the approach instead).
~~~

## REQ-069

- **Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 1
- **Source type:** SENTENCE
- **Requirement class:** ENGAGEMENT
- **Category:** governance

**Exact source text (verbatim):**

~~~text
This is the checklist your submission is scored against.
~~~

## REQ-070

- **Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 2
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Each artifact must be present at (or near) the path shown and contain what is listed.
~~~

## REQ-071

- **Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 3
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Remember the Evidence-in-Repo and Citation-Resolves rules: outputs must be produced by committed code, and every citation must resolve to a committed artifact.
~~~

## REQ-072

- **Source location:** Section 7.1 Agentic System — Foundation — table row "LangGraph graph"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** orchestration

**Exact source text (verbatim):**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

## REQ-073

- **Source location:** Section 7.1 Agentic System — Foundation — table row "MCP server"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

## REQ-074

- **Source location:** Section 7.1 Agentic System — Foundation — table row "Context engineering"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** functional

**Exact source text (verbatim):**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

## REQ-075

- **Source location:** Section 7.1 Agentic System — Foundation — table row "Tiered memory"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** functional

**Exact source text (verbatim):**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

## REQ-076

- **Source location:** Section 7.1 Agentic System — Foundation — table row "Agentic-RAG tool"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** policy

**Exact source text (verbatim):**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

## REQ-077

- **Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Phoenix instrumentation"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

## REQ-078

- **Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Trace export"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Trace export | traces/phoenix_spans.parquet (or .jsonl) | ≥1 full run; spans across multiple agents + every tool call; latencies present
~~~

## REQ-079

- **Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Tool-invocation log"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

## REQ-080

- **Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Failure-mode analysis"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Failure-mode analysis | docs/failure-analysis.md | ≥3 real failures, EACH citing Phoenix run_id + span_id (or tool-log record) + root cause + fix
~~~

## REQ-081

- **Source location:** Section 7.3 Performance & Cost Governance — table row "Golden-signals report"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

## REQ-082

- **Source location:** Section 7.3 Performance & Cost Governance — table row "Cost/latency dashboard"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Cost/latency dashboard | reports/dashboard.png + reports/dashboard_data.csv | Phoenix latency/cost/token dashboard screenshot AND the underlying data file it was drawn from
~~~

## REQ-083

- **Source location:** Section 7.4 Security & Guardrails — table row "Guardrail code"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
Guardrail code | src/guardrails/ | input/output guardrails wired into the agent's I/O path (blocks/sanitizes)
~~~

## REQ-084

- **Source location:** Section 7.4 Security & Guardrails — table row "Audit trail"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

## REQ-085

- **Source location:** Section 7.4 Security & Guardrails — table row "Secrets hygiene"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
Secrets hygiene | .env.example, .gitignore | env-var config; .gitignore covers .env; no secrets committed anywhere
~~~

## REQ-086

- **Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Risk register"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** risk

**Exact source text (verbatim):**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

## REQ-087

- **Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Model / system card"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

## REQ-088

- **Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Compliance mapping"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

## REQ-089

- **Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Output-risk classification"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** risk

**Exact source text (verbatim):**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

## REQ-090

- **Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Evaluation report"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** evaluation

**Exact source text (verbatim):**

~~~text
Evaluation report | reports/eval_report.json + harness | DeepEval (or equiv) over a golden set: hallucination + faithfulness/relevance; LLM-as-judge
~~~

## REQ-091

- **Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Routing-logic test"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** orchestration

**Exact source text (verbatim):**

~~~text
Routing-logic test | tests/test_routing.py | asserts conditional edges route the right worker for given states
~~~

## REQ-092

- **Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Loop/cascade guard"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** orchestration

**Exact source text (verbatim):**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

## REQ-093

- **Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Tool-contract test"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** integration

**Exact source text (verbatim):**

~~~text
Tool-contract test | tests/test_tool_contracts.py | asserts each tool's input/output schema + one error path
~~~

## REQ-094

- **Source location:** Section 7.7 Engineering & Delivery — table row "Local-run runbook"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** non_functional

**Exact source text (verbatim):**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

## REQ-095

- **Source location:** Section 7.7 Engineering & Delivery — table row "Bonus"
- **Source type:** TABLE_ROW
- **Requirement class:** OPTIONAL
- **Category:** functional

**Exact source text (verbatim):**

~~~text
Bonus | src/api/ (FastAPI streaming) | OPTIONAL: async FastAPI streaming endpoint — extra credit, not required
~~~

## REQ-096

- **Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 1
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

## REQ-097

- **Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 2
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

## REQ-098

- **Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 3
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

## REQ-099

- **Source location:** Section 8. Producing the Evidence — table row "Phoenix trace export"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

## REQ-100

- **Source location:** Section 8. Producing the Evidence — table row "Tool-invocation log"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

## REQ-101

- **Source location:** Section 8. Producing the Evidence — table row "Failure-mode analysis"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Failure-mode analysis | Markdown | Open your Phoenix traces, pick ≥ 3 real failures, write each up citing its run_id + span_id, with root cause and the fix.
~~~

## REQ-102

- **Source location:** Section 8. Producing the Evidence — table row "Golden-signals report"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

## REQ-103

- **Source location:** Section 8. Producing the Evidence — table row "Cost/latency dashboard"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** observability

**Exact source text (verbatim):**

~~~text
Cost/latency dashboard | PNG + CSV | Phoenix UI (localhost:6006) shows latency / cost / token dashboards — screenshot one; export the data with get_spans_dataframe().to_csv('reports/dashboard_data.csv').
~~~

## REQ-104

- **Source location:** Section 8. Producing the Evidence — table row "Guardrail code"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** security

**Exact source text (verbatim):**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

## REQ-105

- **Source location:** Section 8. Producing the Evidence — table row "Audit trail"
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** auditability

**Exact source text (verbatim):**

~~~text
Audit trail | JSONL | Audit middleware that appends {actor, action, tool, decision, timestamp} for each consequential action to logs/agent_actions.jsonl.
~~~

## REQ-106

- **Source location:** Section 8. Producing the Evidence — table row "Governance pack" (continuation table)
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
Governance pack | Markdown | risk-register.md, model-card.md, compliance.md, output-risk.md — each entry cites the committed control/artifact it refers to.
~~~

## REQ-107

- **Source location:** Section 8. Producing the Evidence — table row "Evaluation report" (continuation table)
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** evaluation

**Exact source text (verbatim):**

~~~text
Evaluation report | JSON | A DeepEval run over your golden set (hallucination, faithfulness, answer-relevance) that writes reports/eval_report.json, plus the harness.
~~~

## REQ-108

- **Source location:** Section 8. Producing the Evidence — table row "Agent tests" (continuation table)
- **Source type:** TABLE_ROW
- **Requirement class:** IMPLEMENTATION
- **Category:** evaluation

**Exact source text (verbatim):**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

## REQ-109

- **Source location:** Section 8.1 Good-to-Have — bullet 1
- **Source type:** BULLET
- **Requirement class:** OPTIONAL
- **Category:** functional

**Exact source text (verbatim):**

~~~text
FastAPI streaming endpoint; a demonstrated local run (screenshot/log).
~~~

## REQ-110

- **Source location:** Section 8.1 Good-to-Have — bullet 2
- **Source type:** BULLET
- **Requirement class:** OPTIONAL
- **Category:** security

**Exact source text (verbatim):**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

## REQ-111

- **Source location:** Section 8.1 Good-to-Have — bullet 3
- **Source type:** BULLET
- **Requirement class:** OPTIONAL
- **Category:** observability

**Exact source text (verbatim):**

~~~text
An optimization note showing a measured before/after latency or cost improvement (two Phoenix-derived reports).
~~~

## REQ-112

- **Source location:** Section 8.1 Good-to-Have — closing italic paragraph (final paragraph of the document)
- **Source type:** SENTENCE
- **Requirement class:** IMPLEMENTATION
- **Category:** governance

**Exact source text (verbatim):**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

---

**END OF VERBATIM SOURCE REQUIREMENTS — 112 requirement units extracted.**
