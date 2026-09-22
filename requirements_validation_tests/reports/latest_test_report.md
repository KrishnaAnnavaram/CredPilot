# CredPilot Requirements Validation Report

Generated: 2026-09-22T04:04:36Z  
Implementation under validation: `E:\Virtusa Projects\CredPilot`  
Requirements baseline: `source_requirements/requirements_verbatim.md`  
Baseline SHA-256: `ed25ccf4473d3cf17daad29d0db50f18276f4ed219aba55d8188e01214adf917`  
Baseline integrity: **REQUIREMENTS_BASELINE_VERIFIED**  
Suites executed: api, functional, governance, integration, static, workflow  
Wall time: 126.68s

---

## Headline

```
CredPilot Requirements Validation Report

Total Requirements: 112
Tests Executed: 320
Requirements Passed: 85
Requirements Failed: 27
Requirement Coverage: 100.0%
Overall Requirement Fit: 91%

Final Status:
FAIL
```

## Breakdown by requirement class

| Class | Total | Passed | Failed | Gates final status |
| --- | --- | --- | --- | --- |
| IMPLEMENTATION | 90 | 71 | 19 | yes |
| OPTIONAL | 4 | 2 | 2 | no - the source text marks these optional / bonus / good-to-have |
| ENGAGEMENT | 18 | 12 | 6 | no - these describe the engagement or the evaluator, not the deliverable |

Automated tests executed: 311  |  Manual / non-automatable tests executed: 9

## Failed requirements (IMPLEMENTATION class)

| Requirement | Fit | Category | Reason |
| --- | --- | --- | --- |
| REQ-031 | 33 | security | 2 of 3 bound test(s) produced no satisfying evidence: REQ-031-T02, REQ-031-T03. |
| REQ-032 | 50 | integration | 2 of 4 bound test(s) produced no satisfying evidence: REQ-032-T02, REQ-032-T04. |
| REQ-034 | 67 | integration | 1 of 3 bound test(s) produced no satisfying evidence: REQ-034-T03. |
| REQ-035 | 67 | integration | 1 of 3 bound test(s) produced no satisfying evidence: REQ-035-T03. |
| REQ-036 | 50 | integration | 1 of 2 bound test(s) produced no satisfying evidence: REQ-036-T02. |
| REQ-038 | 50 | integration | 1 of 2 bound test(s) produced no satisfying evidence: REQ-038-T02. |
| REQ-042 | 67 | security | 1 of 3 bound test(s) produced no satisfying evidence: REQ-042-T01. |
| REQ-045 | 80 | affordability | 1 of 4 bound test(s) produced no satisfying evidence: REQ-045-T04. |
| REQ-046 | 89 | underwriting | 1 of 7 bound test(s) produced no satisfying evidence: REQ-046-T07. |
| REQ-049 | 71 | security | 1 of 4 bound test(s) produced no satisfying evidence: REQ-049-T03. |
| REQ-051 | 75 | observability | 1 of 2 bound test(s) produced no satisfying evidence: REQ-051-T02. |
| REQ-054 | 71 | governance | 1 of 5 bound test(s) produced no satisfying evidence: REQ-054-T05. |
| REQ-060 | 25 | security | 1 of 2 bound test(s) produced no satisfying evidence: REQ-060-T02. |
| REQ-066 | 50 | integration | 1 of 2 bound test(s) produced no satisfying evidence: REQ-066-T01. |
| REQ-071 | 50 | auditability | 1 of 2 bound test(s) produced no satisfying evidence: REQ-071-T02. |
| REQ-086 | 67 | risk | 1 of 3 bound test(s) produced no satisfying evidence: REQ-086-T03. |
| REQ-088 | 50 | governance | 1 of 3 bound test(s) produced no satisfying evidence: REQ-088-T03. |
| REQ-106 | 40 | governance | 1 of 2 bound test(s) produced no satisfying evidence: REQ-106-T02. |
| REQ-112 | 88 | governance | 1 of 6 bound test(s) produced no satisfying evidence: REQ-112-T03. |

## Failed requirements (OPTIONAL / ENGAGEMENT - not gating)

| Requirement | Class | Fit | Reason |
| --- | --- | --- | --- |
| REQ-008 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-008-T01. |
| REQ-009 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-009-T01. |
| REQ-010 | ENGAGEMENT | 50 | 1 of 2 bound test(s) produced no satisfying evidence: REQ-010-T02. |
| REQ-011 | ENGAGEMENT | 33 | 2 of 3 bound test(s) produced no satisfying evidence: REQ-011-T02, REQ-011-T03. |
| REQ-012 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-012-T01. |
| REQ-013 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-013-T01. |
| REQ-109 | OPTIONAL | 50 | 1 of 2 bound test(s) produced no satisfying evidence: REQ-109-T01. |
| REQ-110 | OPTIONAL | 67 | 1 of 3 bound test(s) produced no satisfying evidence: REQ-110-T01. |

## Fit score by category

| Category | Requirements | Passed | Mean fit |
| --- | --- | --- | --- |
| affordability | 1 | 0 | 80 |
| auditability | 11 | 10 | 95 |
| eligibility | 1 | 1 | 100 |
| evaluation | 6 | 6 | 100 |
| functional | 7 | 6 | 93 |
| governance | 23 | 13 | 71 |
| integration | 10 | 4 | 73 |
| non_functional | 8 | 8 | 100 |
| observability | 19 | 18 | 99 |
| orchestration | 6 | 6 | 100 |
| policy | 3 | 3 | 100 |
| risk | 2 | 1 | 84 |
| security | 11 | 6 | 78 |
| underwriting | 3 | 2 | 96 |
| workflow | 1 | 1 | 100 |

---

## Per-requirement result

Each entry carries the exact original requirement, its status, its fit score, the actual evidence collected, and a factual reason.

### REQ-001 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Document title block — banner line above the title (first line of the document)

**Requirement:**

~~~text
Agentic AI Engineer Pathway — Capstone Hackathon
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-001-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-001-T01: the pathway and capstone hackathon named in the banner line across implementation tree (105 files) (ALL: 2/2 satisfied)
[OK] README.md:3: > **Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon**
[OK] README.md:3: > **Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon**
```

### REQ-002 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Document title block — document title

**Requirement:**

~~~text
Loan Origination & Underwriting Copilot
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-002-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-002-T01: the document title declared in repository documentation across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] README.md:9: **Loan Origination & Underwriting Copilot** — a LangGraph multi-agent system that
```

### REQ-003 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Document title block — subtitle line beneath the title

**Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-003-T01, REQ-003-T02, REQ-003-T03, REQ-003-T04, REQ-003-T05, REQ-003-T06, REQ-003-T07, REQ-003-T08  
**Reason:** All 8 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-003-T01: business case ID and domain from the subtitle (ALL: 2/2 satisfied)
[OK] business case ID across implementation tree (1265 files) (ALL: 1/1 satisfied)
[OK] README.md:4: > Business Case **BC-AAIE-HACK-02** · Domain: **Banking & Finance**
[OK] domain across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] README.md:4: > Business Case **BC-AAIE-HACK-02** · Domain: **Banking & Finance**
[PASS] REQ-003-T02: Agentic Core (ALL: 2/2 satisfied)
[OK] File present: src/graph.py (exact path); size=105982 bytes
[OK] LangGraph declared as a dependency (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:16: langgraph==1.2.11
[PASS] REQ-003-T03: Directory present: src/context (exact path); 7 entries: __init__.py, __pycache__, assemble.py, compress.py, isolate.py, select.py, write.py
[PASS] REQ-003-T04: MCP (ALL: 2/2 satisfied)
[OK] Directory present: mcp_server (exact path); 5 entries: __init__.py, __pycache__, capabilities.py, client.py, server.py
[OK] the MCP Python SDK declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:26: mcp==1.30.0
[PASS] REQ-003-T05: Observability (ALL: 2/2 satisfied)
[OK] File present: src/observability/tracing.py (exact path); size=11075 bytes
[OK] arize-phoenix declared as a dependency (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:53: arize-phoenix==11.38.0
[PASS] REQ-003-T06: Cost Governance (ALL: 2/2 satisfied)
[OK] File present: reports/golden_signals.json (exact path); size=9605 bytes
[OK] File present: reports/dashboard_data.csv (exact path); size=1576 bytes
[PASS] REQ-003-T07: Security & Governance (ALL: 3/3 satisfied)
[OK] Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[OK] File present: docs/risk-register.md (exact path); size=24231 bytes
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[PASS] REQ-003-T08: Agent Evaluation (ALL: 2/2 satisfied)
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
[OK] File present: tests/test_routing.py (exact path); size=15913 bytes
```

### REQ-004 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 1

**Requirement:**

~~~text
Business Case Title | Loan Origination & Underwriting Copilot
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-004-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-004-T01: business case title declared in repository documentation across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] README.md:9: **Loan Origination & Underwriting Copilot** — a LangGraph multi-agent system that
```

### REQ-005 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 2

**Requirement:**

~~~text
Business Case ID | BC-AAIE-HACK-02
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-005-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-005-T01: business case ID declared in the repository across implementation tree (1265 files) (ALL: 1/1 satisfied)
[OK] README.md:4: > Business Case **BC-AAIE-HACK-02** · Domain: **Banking & Finance**
```

### REQ-006 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 3

**Requirement:**

~~~text
Domain | Banking & Finance
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-006-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-006-T01: domain declared in repository documentation across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] README.md:4: > Business Case **BC-AAIE-HACK-02** · Domain: **Banking & Finance**
```

### REQ-007 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 4

**Requirement:**

~~~text
Project Type | Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-007-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-007-T01: project type declared in repository documentation across implementation tree (105 files) (ALL: 2/2 satisfied)
[OK] README.md:3: > **Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon**
[OK] README.md:3: > **Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon**
```

### REQ-008 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 1

**Requirement:**

~~~text
Duration | 20 hours
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-008-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-008-T01.

**Evidence:**

```
[FAIL] REQ-008-T01: Attestation for REQ-008-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-009 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 2

**Requirement:**

~~~text
Format | Team of 2–4
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-009-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-009-T01.

**Evidence:**

```
[FAIL] REQ-009-T01: Attestation for REQ-009-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-010 - FAIL (50/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 3

**Requirement:**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-010-T01, REQ-010-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-010-T02.

**Evidence:**

```
[PASS] REQ-010-T01: E:\Virtusa Projects\CredPilot is a Git repository; git ls-files reports 1844 tracked files
[FAIL] REQ-010-T02: Attestation for REQ-010-T02 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-011 - FAIL (33/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 4

**Requirement:**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-011-T01, REQ-011-T02, REQ-011-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-011-T02, REQ-011-T03.

**Evidence:**

```
[PASS] REQ-011-T01: git remote -v:
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)
[FAIL] REQ-011-T02: No configured remote names GitLab, but the submission instruction names a Virtusa GitLab project. Remotes found:
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)
[FAIL] REQ-011-T03: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project' could be verified against an implementation.
```

### REQ-012 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 5

**Requirement:**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-012-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-012-T01.

**Evidence:**

```
[FAIL] REQ-012-T01: Attestation for REQ-012-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-013 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 6

**Requirement:**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-013-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-013-T01.

**Evidence:**

```
[FAIL] REQ-013-T01: Attestation for REQ-013-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-014 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 1

**Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-014-T01, REQ-014-T02, REQ-014-T03, REQ-014-T04, REQ-014-T05, REQ-014-T06, REQ-014-T07, REQ-014-T08, REQ-014-T09, REQ-014-T10  
**Reason:** All 10 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-014-T01: LangGraph multi-agent system (ALL: 2/2 satisfied)
[OK] File present: src/graph.py (exact path); size=105982 bytes
[OK] LangGraph declared as a dependency (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:16: langgraph==1.2.11
[PASS] REQ-014-T02: Directory present: src/context (exact path); 7 entries: __init__.py, __pycache__, assemble.py, compress.py, isolate.py, select.py, write.py
[PASS] REQ-014-T03: Directory present: src/memory (exact path); 5 entries: __init__.py, __pycache__, long_term.py, short_term.py, store.py
[PASS] REQ-014-T04: Directory present: mcp_server (exact path); 5 entries: __init__.py, __pycache__, capabilities.py, client.py, server.py
[PASS] REQ-014-T05: File present: src/tools/rag_tool.py (exact path); size=13791 bytes
[PASS] REQ-014-T06: Arize Phoenix observability (ALL: 2/2 satisfied)
[OK] File present: src/observability/tracing.py (exact path); size=11075 bytes
[OK] arize-phoenix declared as a dependency (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:53: arize-phoenix==11.38.0
[PASS] REQ-014-T07: cost and latency governance artifacts (ALL: 2/2 satisfied)
[OK] File present: reports/golden_signals.json (exact path); size=9605 bytes
[OK] cost/latency dashboard (ANY: 2/2 satisfied)
[OK] File present: reports/dashboard.png (exact path); size=206181 bytes
[OK] File present: reports/dashboard_data.csv (exact path); size=1576 bytes
[PASS] REQ-014-T08: guardrails and audit (ALL: 2/2 satisfied)
[OK] Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[OK] File present: logs/agent_actions.jsonl (exact path); size=463537 bytes
[PASS] REQ-014-T09: governance and compliance documentation (ALL: 4/4 satisfied)
[OK] File present: docs/risk-register.md (exact path); size=24231 bytes
[OK] File present: docs/model-card.md (exact path); size=25500 bytes
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[OK] File present: docs/output-risk.md (exact path); size=12473 bytes
[PASS] REQ-014-T10: agent-level evaluation and tests (ALL: 4/4 satisfied)
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
[OK] File present: tests/test_routing.py (exact path); size=15913 bytes
[OK] File present: tests/test_loops.py (exact path); size=8870 bytes
[OK] File present: tests/test_tool_contracts.py (exact path); size=8964 bytes
```

### REQ-015 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 2

**Requirement:**

~~~text
Every claim is scored from committed evidence.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-015-T01, REQ-015-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-015-T01: E:\Virtusa Projects\CredPilot is a Git repository; git ls-files reports 1844 tracked files
[PASS] REQ-015-T02: All 24 present named artifact(s) are committed: src/graph.py, logs/mcp_transcript.jsonl, tests/test_memory_persistence.py, logs/memory_test.log, src/tools/rag_tool.py, src/observability/tracing.py, traces/phoenix_spans.jsonl, logs/tool_calls.jsonl, docs/failure-analysis.md, reports/golden_signals.json, reports/dashboard.png, reports/dashboard_data.csv, logs/agent_actions.jsonl, .env.example, .gitignore, docs/risk-register.md, docs/model-card.md, docs/compliance.md, docs/output-risk.md, reports/eval_report.json, tests/test_routing.py, tests/test_loops.py, tests/test_tool_contracts.py, README.md
```

### REQ-016 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 1

**Requirement:**

~~~text
What is not evaluated: the visual polish of any interface, generic unit-test volume, or which optional deployment path you use.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-016-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-016-T01: Scanned 307 of 320 registered test cases (excluding the 2 exclusion-stating requirements and the absence-asserting NEGATIVE_TESTs, which must name a topic in order to exclude it): none would score interface visual polish, generic unit-test volume, or a particular optional deployment path.
```

### REQ-017 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 2

**Requirement:**

~~~text
Containerized/cloud deployment is out of scope for this cut.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-017-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-017-T01: README.md (436 lines) documents no docker / docker-compose / kubectl / helm command, so the run path does not depend on containerized or cloud deployment.
```

### REQ-018 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** underwriting  |  **Source:** Section 3.1 Problem — sentence 1

**Requirement:**

~~~text
A retail bank's loan officers spend most of an application on manual work: gathering the applicant's documents, checking eligibility against product policy, computing affordability, screening for risk flags, and drafting a decision rationale.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-018-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-018-T01: the five manual activities named in the problem statement across implementation tree (105 files) (ALL: 5/5 satisfied)
[OK] data/policy_corpus/README.md:4: CredPilot agentic-RAG tool retrieves from. The policy documents themselves
[OK] docs/compliance.md:77: - the outcome, eligibility status, risk level and review reasons — as facts
[OK] docs/failure-analysis.md:64: MTG-010  "What affordability ceiling applies to this file?"   (as of 2026-06-25)
[OK] docs/compliance.md:13: Creditworthiness assessment of natural persons is **Annex III(5)(b)** — high-risk. The obligations below are the ones that fall on a provider building the system.
[OK] docs/compliance.md:21: | **Art. 13** — Transparency to deployers | Deployers can interpret output and use it appropriately | Three-tier output classification stating what each tier means and what gates it; every recommendation carries resolvable citations and the formula version behind each figure | [`docs/output-risk.md`
```

### REQ-019 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** policy  |  **Source:** Section 3.1 Problem — sentence 2

**Requirement:**

~~~text
Rules are scattered across policy PDFs and change often, so decisions are inconsistent and slow.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-019-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-019-T01: policy retrieved from a corpus (ALL: 2/2 satisfied)
[OK] Directory present: data/policy_corpus (exact path); 2 entries: corpus_registry.json, README.md
[OK] File present: src/tools/rag_tool.py (exact path); size=13791 bytes
```

### REQ-020 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** underwriting  |  **Source:** Section 3.1 Problem — sentence 3

**Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-020-T01, REQ-020-T02, REQ-020-T03, REQ-020-T04, REQ-020-T05, REQ-020-T06  
**Reason:** All 6 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-020-T01: loan application ingestion (ALL: 2/2 satisfied)
[OK] committed loan application inputs: 7 committed input file(s): data/policy_corpus/corpus_registry.json, data/policy_corpus/README.md, data/vectorstore/index_integrity.json, data/vectorstore/index_manifest.json, data/vectorstore/lexical/bm25_education.json, data/vectorstore/lexical/bm25_mortgage.json, data/vectorstore/README.md
[OK] application handling in source across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:10: application and a question; the expected answer lives in the structured
[PASS] REQ-020-T02: current lending policy retrieval (ALL: 2/2 satisfied)
[OK] File present: src/tools/rag_tool.py (exact path); size=13791 bytes
[OK] Directory present: data/policy_corpus (exact path); 2 entries: corpus_registry.json, README.md
[PASS] REQ-020-T03: eligibility and affordability computation across implementation tree (147 files) (ALL: 2/2 satisfied)
[OK] eval/agent/dataset.py:11: outcome tables (``decisions.csv``, ``eligibility_results.csv``,
[OK] eval/agent/dataset.py:320: "DTI-CONV": "src/rules.py — affordability ceiling, with the compensating-factor extension",
[PASS] REQ-020-T04: risk screening in source across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:7: hand-written cases carrying ``expected_decision``, ``expected_risk_grade``,
[PASS] REQ-020-T05: auditable decision recommendation (ALL: 2/2 satisfied)
[OK] decision vocabulary in source across implementation tree (147 files) (ALL: 3/3 satisfied)
[OK] eval/agent/dataset.py:41: #: ``APPROVE_WITH_CONDITIONS`` is listed because the golden sets use it — six
[OK] eval/agent/dataset.py:43: #: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
[OK] eval/agent/dataset.py:43: #: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
[OK] File present: logs/agent_actions.jsonl (exact path); size=463537 bytes
[PASS] REQ-020-T06: human-in-the-loop final decision across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:63: "PENDING_HUMAN_REVIEW": REFER,
```

### REQ-021 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 3.2 Your Role — sentence 1

**Requirement:**

~~~text
Agentic AI Engineer.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-021-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-021-T01: the stated role named in documentation across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] README.md:3: > **Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon**
```

### REQ-022 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 3.2 Your Role — sentence 2

**Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-022-T01, REQ-022-T02, REQ-022-T03, REQ-022-T04, REQ-022-T05, REQ-022-T06, REQ-022-T07  
**Reason:** All 7 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-022-T01: LangGraph multi-agent copilot (ALL: 2/2 satisfied)
[OK] File present: src/graph.py (exact path); size=105982 bytes
[OK] LangGraph imported by the implementation (import analysis) (ALL: 1/1 satisfied)
[OK] src/graph.py:2424: from langgraph.checkpoint.sqlite import ...
[PASS] REQ-022-T02: Arize Phoenix instrumentation (ALL: 2/2 satisfied)
[OK] File present: src/observability/tracing.py (exact path); size=11075 bytes
[OK] Phoenix/openinference imported (import analysis) (ANY: 1/2 satisfied)
[OK] scripts/build_golden_signals.py:109: import phoenix
[NOT FOUND] module 'openinference' is never imported
[PASS] REQ-022-T03: File present: reports/golden_signals.json (exact path); size=9605 bytes
[PASS] REQ-022-T04: guardrails and audit trail (ALL: 2/2 satisfied)
[OK] Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[OK] File present: logs/agent_actions.jsonl (exact path); size=463537 bytes
[PASS] REQ-022-T05: risk and compliance documentation (ALL: 2/2 satisfied)
[OK] File present: docs/risk-register.md (exact path); size=24231 bytes
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[PASS] REQ-022-T06: agent-level evaluation and tests (ALL: 4/4 satisfied)
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
[OK] File present: tests/test_routing.py (exact path); size=15913 bytes
[OK] File present: tests/test_loops.py (exact path); size=8870 bytes
[OK] File present: tests/test_tool_contracts.py (exact path); size=8964 bytes
[PASS] REQ-022-T07: All 24 present named artifact(s) are committed: src/graph.py, logs/mcp_transcript.jsonl, tests/test_memory_persistence.py, logs/memory_test.log, src/tools/rag_tool.py, src/observability/tracing.py, traces/phoenix_spans.jsonl, logs/tool_calls.jsonl, docs/failure-analysis.md, reports/golden_signals.json, reports/dashboard.png, reports/dashboard_data.csv, logs/agent_actions.jsonl, .env.example, .gitignore, docs/risk-register.md, docs/model-card.md, docs/compliance.md, docs/output-risk.md, reports/eval_report.json, tests/test_routing.py, tests/test_loops.py, tests/test_tool_contracts.py, README.md
```

### REQ-023 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 3.3 Expected Solution — lead-in sentence

**Requirement:**

~~~text
A working, instrumented multi-agent application delivered as a Git repository that demonstrates:
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-023-T01, REQ-023-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-023-T01: E:\Virtusa Projects\CredPilot is a Git repository; git ls-files reports 1844 tracked files
[PASS] REQ-023-T02: working instrumented multi-agent application (ALL: 3/3 satisfied)
[OK] File present: src/graph.py (exact path); size=105982 bytes
[OK] File present: src/observability/tracing.py (exact path); size=11075 bytes
[OK] a committed trace export proving it ran (ANY: 1/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[OK] File present: traces/phoenix_spans.jsonl (exact path); size=501494 bytes
```

### REQ-024 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 3.3 Expected Solution — bullet 1

**Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-024-T01, REQ-024-T02, REQ-024-T03, REQ-024-T04, REQ-024-T05, REQ-024-T06  
**Reason:** All 6 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-024-T01: typed state definition across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:91: @dataclass
[PASS] REQ-024-T02: supervisor routing node across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:39: through intake, the input guardrail, the Supervisor, the product specialist,
[PASS] REQ-024-T03: the three named worker agents across implementation tree (147 files) (ALL: 3/3 satisfied)
[OK] src/context/select.py:4: policy questions. The eligibility agent needs the affordability and leverage
[OK] eval/agent/run_agent_eval.py:210: ``mortgage_policy_retrieval`` with a hand-built state, but ``intake`` — so
[OK] mcp_server/capabilities.py:82: "screen_risk_flags": "src.calculations.screen_risk — deterministic risk screen",
[PASS] REQ-024-T04: conditional routing wired into the graph (AST call analysis) (ALL: 1/1 satisfied)
[OK] src/graph.py contains a call to 'add_conditional_edges'
[PASS] REQ-024-T05: checkpointing (ALL: 2/2 satisfied)
[OK] checkpointer configured across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:218: ``run_id`` scopes the checkpoint thread to this evaluation run. Without it
[OK] graph compiled, which is where a checkpointer is attached (AST call analysis) (ALL: 1/1 satisfied)
[OK] mcp_server/server.py contains a call to '_re.compile'
[PASS] REQ-024-T06: structured output at the graph boundary across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] mcp_server/server.py:73: from pydantic import BaseModel, Field  # noqa: E402
```

### REQ-025 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 3.3 Expected Solution — bullet 2

**Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-025-T01, REQ-025-T02, REQ-025-T03, REQ-025-T04, REQ-025-T05, REQ-025-T06, REQ-025-T07  
**Reason:** All 7 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-025-T01: MCP surface in mcp_server (4 module(s)) (ALL: 2/2 satisfied)
[OK] >=2 MCP tools: 11 registered ['clarify_loan_product', 'compute_affordability', 'draft_with_sampling', 'get_policy_version', 'get_rule_dependencies', 'list_policy_rules', 'list_project_roots', 'resolve_citation', 'retrieve_policy', 'screen_risk_flags', 'validate_evidence']
[OK] >=1 MCP resource: 10 registered ['education_catalog', 'education_policies', 'education_rules', 'education_thresholds', 'index_manifest', 'mortgage_catalog', 'mortgage_policies', 'mortgage_rules', 'mortgage_thresholds', 'system_capabilities']
[PASS] REQ-025-T02: langchain-mcp-adapters consumption (ALL: 2/2 satisfied)
[OK] langchain-mcp-adapters declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:27: langchain-mcp-adapters>=0.3.0,<0.4
[OK] langchain_mcp_adapters imported (import analysis) (ALL: 1/1 satisfied)
[OK] mcp_server/client.py:67: from langchain_mcp_adapters.resources import ...
[PASS] REQ-025-T03: the four context operations across 'src/context' (6 files) (ALL: 4/4 satisfied)
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[PASS] REQ-025-T04: summarization in the context layer across 'src/context' (6 files) (ALL: 1/1 satisfied)
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[PASS] REQ-025-T05: quarantine of untrusted applicant-supplied text across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:342: "SEC-INJ": "src/guardrails/ + input_guardrails_node — injection detection and quarantine",
[PASS] REQ-025-T06: verified cross-session persistence (ALL: 3/3 satisfied)
[OK] Directory present: src/memory (exact path); 5 entries: __init__.py, __pycache__, long_term.py, short_term.py, store.py
[OK] File present: tests/test_memory_persistence.py (exact path); size=14984 bytes
[OK] File present: logs/memory_test.log (exact path); size=895 bytes
[PASS] REQ-025-T07: agentic-RAG over a synthetic lending-policy corpus (ALL: 2/2 satisfied)
[OK] File present: src/tools/rag_tool.py (exact path); size=13791 bytes
[OK] Directory present: data/policy_corpus (exact path); 2 entries: corpus_registry.json, README.md
```

### REQ-026 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 3.3 Expected Solution — bullet 3

**Requirement:**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-026-T01, REQ-026-T02, REQ-026-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-026-T01: committed Phoenix trace export (ALL: 2/2 satisfied)
[OK] trace export artifact (ANY: 1/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[OK] File present: traces/phoenix_spans.jsonl (exact path); size=501494 bytes
[OK] the export is committed (ANY: 1/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' to check for commitment
[OK] git ls-files lists 'traces/phoenix_spans.jsonl' -> artifact is committed
[PASS] REQ-026-T02: machine-generated tool-invocation log (ALL: 2/2 satisfied)
[OK] artifact present: logs/tool_calls.jsonl
[OK] producing code: scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[PASS] REQ-026-T03: evidence-linked failure-mode analysis (ALL: 2/2 satisfied)
[OK] File present: docs/failure-analysis.md (exact path); size=56777 bytes
[OK] Phoenix evidence links in docs/failure-analysis.md (exact path) (ANY: 2/2 satisfied)
[OK] docs/failure-analysis.md:677: A per-run id in the thread: `eval-{run_id}-{case_id}`, with `run_id` recorded in
[OK] docs/failure-analysis.md:40: machine-generated evidence directly: F-14 a Phoenix `trace_id` and `span_id`
```

### REQ-027 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 3.3 Expected Solution — bullet 4

**Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-027-T01, REQ-027-T02, REQ-027-T03, REQ-027-T04, REQ-027-T05, REQ-027-T06  
**Reason:** All 6 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-027-T01: File present: reports/golden_signals.json (exact path); size=9605 bytes
[PASS] REQ-027-T02: cost/latency dashboard (ALL: 2/2 satisfied)
[OK] File present: reports/dashboard.png (exact path); size=206181 bytes
[OK] File present: reports/dashboard_data.csv (exact path); size=1576 bytes
[PASS] REQ-027-T03: Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[PASS] REQ-027-T04: File present: logs/agent_actions.jsonl (exact path); size=463537 bytes
[PASS] REQ-027-T05: secrets hygiene (ALL: 2/2 satisfied)
[OK] File present: .env.example (exact path); size=2595 bytes
[OK] File present: .gitignore (exact path); size=1302 bytes
[PASS] REQ-027-T06: governance pack (ALL: 4/4 satisfied)
[OK] File present: docs/risk-register.md (exact path); size=24231 bytes
[OK] File present: docs/model-card.md (exact path); size=25500 bytes
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[OK] File present: docs/output-risk.md (exact path); size=12473 bytes
```

### REQ-028 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 3.3 Expected Solution — bullet 5

**Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-028-T01, REQ-028-T02, REQ-028-T03, REQ-028-T04, REQ-028-T05  
**Reason:** All 5 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-028-T01: LLM-as-judge and hallucination evaluation (ALL: 2/2 satisfied)
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
[OK] hallucination metric in the eval report at reports/eval_report.json (exact path) (ALL: 1/1 satisfied)
[OK] key matching /hallucinat/ present as 'judge_hallucination_rate'
[PASS] REQ-028-T02: File present: tests/test_routing.py (exact path); size=15913 bytes
[PASS] REQ-028-T03: File present: tests/test_loops.py (exact path); size=8870 bytes
[PASS] REQ-028-T04: File present: tests/test_tool_contracts.py (exact path); size=8964 bytes
[PASS] REQ-028-T05: local-run runbook (ALL: 2/2 satisfied)
[OK] File present: README.md (exact path); size=20794 bytes
[OK] a documented runnable command block in README.md (exact path) (ANY: 1/1 satisfied)
[OK] README.md:23: ```bash
```

### REQ-029 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 3.4 Applicable Rules — bullet 1 (Evidence-in-Repo Rule)

**Requirement:**

~~~text
Evidence-in-Repo Rule. Only committed artifacts are scored. A claim with no committed evidence scores zero; an evidence artifact with no producing code (a metric, trace or log a team could hand-write) is heavily discounted.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-029-T01, REQ-029-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-029-T01: All 24 present named artifact(s) are committed: src/graph.py, logs/mcp_transcript.jsonl, tests/test_memory_persistence.py, logs/memory_test.log, src/tools/rag_tool.py, src/observability/tracing.py, traces/phoenix_spans.jsonl, logs/tool_calls.jsonl, docs/failure-analysis.md, reports/golden_signals.json, reports/dashboard.png, reports/dashboard_data.csv, logs/agent_actions.jsonl, .env.example, .gitignore, docs/risk-register.md, docs/model-card.md, docs/compliance.md, docs/output-risk.md, reports/eval_report.json, tests/test_routing.py, tests/test_loops.py, tests/test_tool_contracts.py, README.md
[PASS] REQ-029-T02: producing code for 7 present evidence artifact(s) (ALL: 7/7 satisfied)
[OK] logs/tool_calls.jsonl <- produced by scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[OK] logs/agent_actions.jsonl <- produced by scripts/verify_evidence_citations.py:216: artifact="logs/agent_actions.jsonl",
[OK] logs/mcp_transcript.jsonl <- produced by mcp_server/server.py:122: The transcript at ``logs/mcp_transcript.jsonl`` is written from here, which
[OK] reports/golden_signals.json <- produced by scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[OK] reports/dashboard_data.csv <- produced by scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
[OK] reports/eval_report.json <- produced by eval/agent/run_agent_eval.py:72: REPORT_PATH = REPORTS / "eval_report.json"
[OK] logs/memory_test.log <- produced by src/memory/__init__.py:3: *"src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log |
```

### REQ-030 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 3.4 Applicable Rules — bullet 2 (Citation-Resolves Rule)

**Requirement:**

~~~text
Citation-Resolves Rule. Wherever a document cites evidence (a Phoenix run/span id, a log record, a control file), the citation must resolve to a committed artifact. Unresolvable citations are treated as missing.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-030-T01, REQ-030-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-030-T01: failure-analysis citations: all 37 citation(s) resolve to committed artifacts
reports/phoenix_spans.csv -> reports/phoenix_spans.csv
logs/tool_calls.jsonl -> logs/tool_calls.jsonl
logs/agent_actions.jsonl -> logs/agent_actions.jsonl
scripts/verify_evidence_citations.py -> scripts/verify_evidence_citations.py
eval/results/retrieval_eval_cases.jsonl -> eval/results/retrieval_eval_cases.jsonl
src/rag/pipeline.py -> src/rag/pipeline.py
test_chunking.py -> tests/rag/test_chunking.py
src/guardrails/redaction.py -> src/guardrails/redaction.py
tests/rag/test_mcp_rag_integration.py -> tests/rag/test_mcp_rag_integration.py
mcp_server/server.py -> mcp_server/server.py
pytest tests/rag/test_mcp_rag_integration.py -> tests/rag/test_mcp_rag_integration.py
rag/DATA_QUALITY_FINDINGS.md -> docs/rag/DATA_QUALITY_FINDINGS.md
eval/results/pipeline_sweep.json -> eval/results/pipeline_sweep.json
rag/RETRIEVAL_ABLATION.md -> docs/rag/RETRIEVAL_ABLATION.md
config/rag.yaml -> config/rag.yaml
[PASS] REQ-030-T02: governance pack citations resolve (ALL: 4/4 satisfied)
[OK] risk register citations: all 19 citation(s) resolve to committed artifacts
reports/eval_report.json -> reports/eval_report.json
docs/model-card.md -> docs/model-card.md
tests/test_supervisor.py -> tests/test_supervisor.py
tests/test_web_api.py -> tests/test_web_api.py
tests/test_mcp_capabilities.py -> tests/test_mcp_capabilities.py
src/llm.py -> src/llm.py
logs/mcp_transcript.jsonl -> logs/mcp_transcript.jsonl
mcp_server/capabilities.py -> mcp_server/capabilities.py
tests/rag/test_pii_logging.py -> tests/rag/test_pii_logging.py
index_manifest.json -> data/vectorstore/index_manifest.json
scripts/check_published_figures.py -> scripts/check_published_figures.py
scripts/verify_doc_tables.py -> scripts/verify_doc_tables.py
tests/test_rule_families.py -> tests/test_rule_families.py
tests/test_resilience.py -> tests/test_resilience.py
reports/golden_signals.json -> reports/golden_signals.json
[OK] model card citations: all 17 citation(s) resolve to committed artifacts
tests/rag/test_stack_boundaries.py -> tests/rag/test_stack_boundaries.py
reports/golden_signals.json -> reports/golden_signals.json
docs/rag/DATA_QUALITY_FINDINGS.md -> docs/rag/DATA_QUALITY_FINDINGS.md
eval/agent/run_agent_eval.py -> eval/agent/run_agent_eval.py
reports/eval_report.json -> reports/eval_report.json
reports/eval_cases.jsonl -> reports/eval_cases.jsonl
decisions.csv -> synthetic_data/mortgage/structured/decisions.csv
failure-analysis.md -> docs/failure-analysis.md
docs/output-risk.md -> docs/output-risk.md
scripts/build_policy_indexes.py -> scripts/build_policy_indexes.py
scripts/build_golden_signals.py -> scripts/build_golden_signals.py
scripts/build_dashboard.py -> scripts/build_dashboard.py
rag/RUNBOOK.md -> docs/rag/RUNBOOK.md
risk-register.md -> docs/risk-register.md
compliance.md -> docs/compliance.md
[OK] compliance mapping citations: all 31 citation(s) resolve to committed artifacts
risk-register.md -> docs/risk-register.md
rag/DATA_QUALITY_FINDINGS.md -> docs/rag/DATA_QUALITY_FINDINGS.md
model-card.md -> docs/model-card.md
logs/agent_actions.jsonl -> logs/agent_actions.jsonl
logs/tool_calls.jsonl -> logs/tool_calls.jsonl
scripts/export_traces.py -> scripts/export_traces.py
output-risk.md -> docs/output-risk.md
src/graph.py -> src/graph.py
src/supervisor.py -> src/supervisor.py
reports/eval_report.json -> reports/eval_report.json
src/guardrails/sanitize.py -> src/guardrails/sanitize.py
src/resilience.py -> src/resilience.py
tests/test_loops.py -> tests/test_loops.py
tests/test_resilience.py -> tests/test_resilience.py
src/narrative.py -> src/narrative.py
[OK] output-risk citations: all 2 citation(s) resolve to committed artifacts
src/supervisor.py -> src/supervisor.py
reports/eval_report.json -> reports/eval_report.json
```

### REQ-031 - FAIL (33/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 3.4 Applicable Rules — bullet 3 (Synthetic-Data Rule)

**Requirement:**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-031-T01, REQ-031-T02, REQ-031-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-031-T02, REQ-031-T03.

**Evidence:**

```
[PASS] REQ-031-T01: synthetic data declared for applications and policies across implementation tree (553 files) (ALL: 1/1 satisfied)
[OK] data/policy_corpus/corpus_registry.json:2: "description": "Machine-generated inventory of the lending-policy corpora CredPilot's vector and lexical indexes are built from. The policy documents themselves are committed under synthetic_data/<product>/policy_corpus/ and are not duplicated here.",
[FAIL] REQ-031-T02: unmasked payment-card numbers: prohibited content found (6 hit(s))
/\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b/ matched docs/rag/REQUIREMENTS_MAPPING.md:242: them were nDCG values: `"policy_ndcg@10": 0.4440973278132557` contains the
/\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b/ matched eval/retrieval/metrics.py:90: #: distinguish from a Visa number. `0.4440973278132557` contains
/\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b/ matched src/guardrails/redaction.py:219: # version of this pattern matched `4111111111111111` and stopped it being
/\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b/ matched tests/rag/test_pii_logging.py:89: "account_number": "4111111111111111",
/\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b/ matched tests/rag/test_security.py:138: result = sanitize_query("Check the file for SSN 123-45-6789 and account 4111111111111111")
/\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b/ matched traces/phoenix-live.jsonl:813: {"attributes.allowed": null, "attributes.application_id": null, "attributes.as_of_date": null, "attributes.available": null, "attributes.breaches": null, "attributes.candidates": null, "attributes.catalogue_size": null, "attributes.citation_count": null, "attributes.citations": null, "attributes.cit
[FAIL] REQ-031-T03: PII masking and leak-free logs (ALL: 1/2 satisfied)
[OK] masking implemented at scripts/export_traces.py:246: redaction_is_warm(
[NOT FOUND] 1 sensitive value(s) written in plaintext:
traces/phoenix-live.jsonl:813 matches /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b/
```

### REQ-032 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 3.4 Applicable Rules — bullet 4 (Open-Source & Gemini-Only Rule)

**Requirement:**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-032-T01, REQ-032-T02, REQ-032-T03, REQ-032-T04  
**Reason:** 2 of 4 bound test(s) produced no satisfying evidence: REQ-032-T02, REQ-032-T04.

**Evidence:**

```
[PASS] REQ-032-T01: Google Gemini as model provider (ALL: 2/2 satisfied)
[OK] a Google Gemini SDK declared (dependency manifests) (ANY: 2/3 satisfied)
[OK] requirements.txt:23: langchain-google-genai==4.4.0
[NOT FOUND] 'google-generativeai' not declared in any of: requirements.txt, pyproject.toml
[OK] requirements.txt:23: langchain-google-genai==4.4.0
[OK] Gemini referenced in the implementation across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/judges.py:1: """Gemini as the LLM-as-judge behind DeepEval.
[FAIL] REQ-032-T02: no Claude provider (ALL: 1/2 satisfied)
[NOT FOUND] Claude/Anthropic provider usage: prohibited content found (1 hit(s))
/anthropic/ matched tests/rag/test_stack_boundaries.py:9: call Claude, and must not read an ``ANTHROPIC_API_KEY``.
[OK] Claude/Anthropic dependency declaration: no prohibited pattern matched across 1160 scanned files
[PASS] REQ-032-T03: pip + Python toolchain (ALL: 2/2 satisfied)
[OK] a pip-installable dependency manifest (ANY: 2/2 satisfied)
[OK] File present: requirements.txt (exact path); size=3304 bytes
[OK] File present: pyproject.toml (exact path); size=399 bytes
[OK] documented pip install step in README.md (exact path) (ANY: 1/1 satisfied)
[OK] README.md:26: pip install -r requirements.txt
[FAIL] REQ-032-T04: no Docker or external DB service required (ALL: 1/2 satisfied)
[OK] container build/orchestration files: no file matches ['Dockerfile', 'docker-compose*.yml', 'docker-compose*.yaml', '*.dockerfile', 'compose.yaml', 'compose.yml'] across 1862 files
[NOT FOUND] external database service connection strings: prohibited content found (6 hit(s))
/\bpostgres(ql)?:/// matched docs/rag/REQUIREMENTS_MAPPING.md:263: | "external database service" (REQ-032, REQ-034) | the same file | Likewise: it contains `postgresql://`, `mysql://` in the list of markers it asserts are absent. |
/\bpostgres(ql)?:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
/\bmysql:/// matched docs/rag/REQUIREMENTS_MAPPING.md:263: | "external database service" (REQ-032, REQ-034) | the same file | Likewise: it contains `postgresql://`, `mysql://` in the list of markers it asserts are absent. |
/\bmysql:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
/\bmongodb(\+srv)?:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
/\bredis:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
```

### REQ-033 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 3.4 Applicable Rules — bullet 5 (Reproducibility Rule)

**Requirement:**

~~~text
Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-033-T01, REQ-033-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-033-T01: documented regeneration commands (ALL: 3/3 satisfied)
[OK] documented command to run the copilot: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[OK] documented command to regenerate the Phoenix traces: 'python scripts/export_traces.py' (from README.md (documented command))
[OK] documented command to regenerate the evaluation: 'python -m eval.agent.run_agent_eval --no-judge' (from README.md (documented command))
[PASS] REQ-033-T02: committed sample inputs: 7 committed input file(s): data/policy_corpus/corpus_registry.json, data/policy_corpus/README.md, data/vectorstore/index_integrity.json, data/vectorstore/index_manifest.json, data/vectorstore/lexical/bm25_education.json, data/vectorstore/lexical/bm25_mortgage.json, data/vectorstore/README.md
```

### REQ-034 - FAIL (67/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — lead-in paragraph

**Requirement:**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-034-T01, REQ-034-T02, REQ-034-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-034-T03.

**Evidence:**

```
[PASS] REQ-034-T01: Gemini is the only model provider (ALL: 2/2 satisfied)
[OK] a Google Gemini SDK declared (dependency manifests) (ANY: 2/3 satisfied)
[OK] requirements.txt:23: langchain-google-genai==4.4.0
[NOT FOUND] 'google-generativeai' not declared in any of: requirements.txt, pyproject.toml
[OK] requirements.txt:23: langchain-google-genai==4.4.0
[OK] a competing model-provider dependency: no prohibited pattern matched across 1160 scanned files
[PASS] REQ-034-T02: pip-installable manifest (ANY: 2/2 satisfied)
[OK] File present: requirements.txt (exact path); size=3304 bytes
[OK] File present: pyproject.toml (exact path); size=399 bytes
[FAIL] REQ-034-T03: no Docker or external DB service (ALL: 1/2 satisfied)
[OK] container build/orchestration files: no file matches ['Dockerfile', 'docker-compose*.yml', 'docker-compose*.yaml', 'compose.yaml', 'compose.yml'] across 1862 files
[NOT FOUND] external database service connection strings: prohibited content found (6 hit(s))
/\bpostgres(ql)?:/// matched docs/rag/REQUIREMENTS_MAPPING.md:263: | "external database service" (REQ-032, REQ-034) | the same file | Likewise: it contains `postgresql://`, `mysql://` in the list of markers it asserts are absent. |
/\bpostgres(ql)?:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
/\bmysql:/// matched docs/rag/REQUIREMENTS_MAPPING.md:263: | "external database service" (REQ-032, REQ-034) | the same file | Likewise: it contains `postgresql://`, `mysql://` in the list of markers it asserts are absent. |
/\bmysql:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
/\bmongodb(\+srv)?:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
/\bredis:/// matched tests/rag/test_stack_boundaries.py:139: for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
```

### REQ-035 - FAIL (67/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"

**Requirement:**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-035-T01, REQ-035-T02, REQ-035-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-035-T03.

**Evidence:**

```
[PASS] REQ-035-T01: Python >= 3.11 declared at pyproject.toml:5: requires-python = ">=3.11"
[PASS] REQ-035-T02: LangGraph agent framework (ALL: 2/2 satisfied)
[OK] langgraph declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:16: langgraph==1.2.11
[OK] langgraph imported (import analysis) (ALL: 1/1 satisfied)
[OK] src/graph.py:2424: from langgraph.checkpoint.sqlite import ...
[FAIL] REQ-035-T03: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence' could be verified against an implementation.
```

### REQ-036 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "LLM Provider"

**Requirement:**

~~~text
LLM Provider | Google Gemini (API) — the only approved provider; not Claude
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-036-T01, REQ-036-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-036-T02.

**Evidence:**

```
[PASS] REQ-036-T01: Gemini API usage (ALL: 2/2 satisfied)
[OK] a Google Gemini SDK declared (dependency manifests) (ANY: 2/3 satisfied)
[OK] requirements.txt:23: langchain-google-genai==4.4.0
[NOT FOUND] 'google-generativeai' not declared in any of: requirements.txt, pyproject.toml
[OK] requirements.txt:23: langchain-google-genai==4.4.0
[OK] Gemini model referenced across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/judges.py:1: """Gemini as the LLM-as-judge behind DeepEval.
[FAIL] REQ-036-T02: Claude/Anthropic usage: prohibited content found (1 hit(s))
/anthropic/ matched tests/rag/test_stack_boundaries.py:9: call Claude, and must not read an ``ANTHROPIC_API_KEY``.
```

### REQ-037 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "Interoperability"

**Requirement:**

~~~text
Interoperability | MCP Python SDK (stdio) + langchain-mcp-adapters
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-037-T01, REQ-037-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-037-T01: MCP Python SDK over stdio (ALL: 2/2 satisfied)
[OK] the MCP Python SDK declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:26: mcp==1.30.0
[OK] stdio transport configured across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:60: from src.console import use_utf8_stdio
[PASS] REQ-037-T02: langchain-mcp-adapters (ALL: 2/2 satisfied)
[OK] langchain-mcp-adapters declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:27: langchain-mcp-adapters>=0.3.0,<0.4
[OK] langchain_mcp_adapters imported (import analysis) (ALL: 1/1 satisfied)
[OK] mcp_server/client.py:67: from langchain_mcp_adapters.resources import ...
```

### REQ-038 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "Memory"

**Requirement:**

~~~text
Memory | langgraph-checkpoint-sqlite (SQLite file) + LangMem
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-038-T01, REQ-038-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-038-T02.

**Evidence:**

```
[PASS] REQ-038-T01: langgraph-checkpoint-sqlite (ALL: 2/2 satisfied)
[OK] langgraph-checkpoint-sqlite declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:17: langgraph-checkpoint-sqlite==3.1.1
[OK] SQLite checkpointer used across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/graph.py:2424: from langgraph.checkpoint.sqlite import SqliteSaver
[FAIL] REQ-038-T02: LangMem (ALL: 0/2 satisfied)
[NOT FOUND] langmem declared (dependency manifests) (ALL: 0/1 satisfied)
[NOT FOUND] 'langmem' not declared in any of: requirements.txt, pyproject.toml
[NOT FOUND] LangMem used across implementation tree (147 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /langmem/ in 147 files under implementation tree
```

### REQ-039 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** policy  |  **Source:** Section 4. Technology & Framework Stack — table row "Retrieval"

**Requirement:**

~~~text
Retrieval | Chroma or FAISS + Sentence-Transformers (local)
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-039-T01, REQ-039-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-039-T01: Chroma or FAISS (ANY: 1/2 satisfied)
[OK] Chroma (ALL: 2/2 satisfied)
[OK] chromadb declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:45: chromadb==1.5.9
[OK] Chroma used across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/retrieval/harness.py:40: vectorstore_path=workspace / "chroma",
[NOT FOUND] FAISS (ALL: 1/2 satisfied)
[NOT FOUND] faiss declared (dependency manifests) (ALL: 0/1 satisfied)
[NOT FOUND] 'faiss' not declared in any of: requirements.txt, pyproject.toml
[OK] FAISS used across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] tests/rag/test_documentation.py:199: "REQ-039",  # Chroma or FAISS + Sentence-Transformers
[PASS] REQ-039-T02: Sentence-Transformers (local) (ALL: 2/2 satisfied)
[OK] sentence-transformers declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:46: sentence-transformers==6.0.1
[OK] Sentence-Transformers used across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/rag/embedding.py:71: from sentence_transformers import SentenceTransformer
```

### REQ-040 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 4. Technology & Framework Stack — table row "Observability (mandated)"

**Requirement:**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-040-T01, REQ-040-T02, REQ-040-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-040-T01: Arize Phoenix (ALL: 2/2 satisfied)
[OK] arize-phoenix declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:53: arize-phoenix==11.38.0
[OK] phoenix imported (import analysis) (ALL: 1/1 satisfied)
[OK] scripts/build_golden_signals.py:109: import phoenix
[PASS] REQ-040-T02: OpenTelemetry / openinference (ALL: 2/2 satisfied)
[OK] openinference/OpenTelemetry declared (dependency manifests) (ANY: 2/2 satisfied)
[OK] requirements.txt:56: openinference-instrumentation-langchain==0.1.76
[OK] requirements.txt:57: opentelemetry-sdk==1.44.0
[OK] openinference/OpenTelemetry imported (import analysis) (ANY: 1/2 satisfied)
[NOT FOUND] module 'openinference' is never imported
[OK] scripts/export_traces.py:168: from opentelemetry import ...
[PASS] REQ-040-T03: local in-process Phoenix session across implementation tree (252 files) (ALL: 1/1 satisfied)
[OK] docs/rag/RUNBOOK.md:394: python -m phoenix.server.main serve       # terminal 1, UI on http://localhost:6006
```

### REQ-041 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 4. Technology & Framework Stack — table row "Evaluation"

**Requirement:**

~~~text
Evaluation | DeepEval (LLM-as-judge = Gemini) · pytest for agent tests
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-041-T01, REQ-041-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-041-T01: DeepEval with a Gemini judge (ALL: 3/3 satisfied)
[OK] deepeval declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:80: deepeval==4.2.3
[OK] DeepEval used across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/judges.py:1: """Gemini as the LLM-as-judge behind DeepEval.
[OK] Gemini configured as the judge model across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/judges.py:1: """Gemini as the LLM-as-judge behind DeepEval.
[PASS] REQ-041-T02: pytest for agent tests (ALL: 2/2 satisfied)
[OK] pytest declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:72: pytest==9.0.2
[OK] File present: tests/test_routing.py (exact path); size=15913 bytes
```

### REQ-042 - FAIL (67/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 4. Technology & Framework Stack — table row "Security"

**Requirement:**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-042-T01, REQ-042-T02, REQ-042-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-042-T01.

**Evidence:**

```
[FAIL] REQ-042-T01: Guardrails-AI or LLM Guard (ANY: 0/2 satisfied)
[NOT FOUND] guardrails-ai declared (dependency manifests) (ALL: 0/1 satisfied)
[NOT FOUND] 'guardrails-ai' not declared in any of: requirements.txt, pyproject.toml
[NOT FOUND] llm-guard declared (dependency manifests) (ALL: 0/1 satisfied)
[NOT FOUND] 'llm-guard' not declared in any of: requirements.txt, pyproject.toml
[PASS] REQ-042-T02: Presidio for PII (ALL: 2/2 satisfied)
[OK] presidio declared (dependency manifests) (ANY: 2/3 satisfied)
[OK] requirements.txt:61: presidio-analyzer==2.2.361
[NOT FOUND] 'presidio_analyzer' not declared in any of: requirements.txt, pyproject.toml
[OK] requirements.txt:61: presidio-analyzer==2.2.361
[OK] Presidio used across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/guardrails/redaction.py:8: Deterministic regex redaction runs first and always. Microsoft Presidio, when
[PASS] REQ-042-T03: python-dotenv (ALL: 2/2 satisfied)
[OK] python-dotenv declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:63: python-dotenv==1.2.2
[OK] dotenv used across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/config.py:5: python-dotenv (see ``.env.example``).
```

### REQ-043 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 4. Technology & Framework Stack — table row "Interface" (continuation table)

**Requirement:**

~~~text
Interface | CLI (required) · FastAPI streaming (optional / bonus)
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-043-T01, REQ-043-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-043-T01: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in eval/agent/run_agent_eval.py
[OK] CLI invocation documented: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[PASS] REQ-043-T02: FastAPI streaming (optional / bonus): not present at or near 'src/api'. The source text marks this surface optional / bonus and explicitly not required, so its absence satisfies the interface requirement.
```

### REQ-044 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** eligibility  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-01

**Requirement:**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-044-T01, REQ-044-T02, REQ-044-T03, REQ-044-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-044-T01: eligibility determination in observable output (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json') (ALL: 1/1 satisfied)
[OK] /eligib/ matched observable output: 'eligib'
--- observable output (last lines) ---
Policy evidence (61 chunks, 61 distinct citations, all resolve: True)
  POL-AST-001 v1.0
  POL-AST-002 v1.0
  POL-AST-002 v1.0 rule AST-FTC-001
  POL-AST-002 v1.0 rule AST-FTC-003
  POL-AST-002 v1.0 rule AST-FTC-004
  POL-AST-002 v1.0 rule AST-FTC-005
  POL-AST-002 v1.0 section 5
  POL-AST-003 v2.0 rule AST-RSV-001
  POL-AST-003 v2.0 rule AST-RSV-002
  POL-AST-003 v2.0 rule AST-RSV-003
  POL-AST-003 v2.0 rule AST-RSV-005
  POL-AST-003 v2.0 section 5
  ... and 49 more

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/199 [00:00<?, ?it/s]
Loading weights:  15%|█▌        | 30/199 [00:00<00:00, 282.86it/s]
Loading weights:  30%|██▉       | 59/199 [00:00<00:00, 271.07it/s]
Loading weights: 100%|██████████| 199/199 [00:00<00:00, 815.21it/s]

Loading weights:   0%|          | 0/105 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 105/105 [00:00<00:00, 2891.60it/s]
Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
[PASS] REQ-044-T02: policy rule citation in observable output (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json') (ALL: 2/2 satisfied)
[OK] /polic(y|ies)/ matched observable output: 'policy'
[OK] /rule|clause|section|citation|cite/ matched observable output: 'rule'
--- observable output (last lines) ---
Policy evidence (61 chunks, 61 distinct citations, all resolve: True)
  POL-AST-001 v1.0
  POL-AST-002 v1.0
  POL-AST-002 v1.0 rule AST-FTC-001
  POL-AST-002 v1.0 rule AST-FTC-003
  POL-AST-002 v1.0 rule AST-FTC-004
  POL-AST-002 v1.0 rule AST-FTC-005
  POL-AST-002 v1.0 section 5
  POL-AST-003 v2.0 rule AST-RSV-001
  POL-AST-003 v2.0 rule AST-RSV-002
  POL-AST-003 v2.0 rule AST-RSV-003
  POL-AST-003 v2.0 rule AST-RSV-005
  POL-AST-003 v2.0 section 5
  ... and 49 more

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/199 [00:00<?, ?it/s]
Loading weights:  25%|██▍       | 49/199 [00:00<00:00, 489.49it/s]
Loading weights:  49%|████▉     | 98/199 [00:00<00:00, 435.07it/s]
Loading weights: 100%|██████████| 199/199 [00:00<00:00, 892.17it/s]

Loading weights:   0%|          | 0/105 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 105/105 [00:00<00:00, 3956.39it/s]
Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
[PASS] REQ-044-T03: current lending policy retrieval (ALL: 2/2 satisfied)
[OK] File present: src/tools/rag_tool.py (exact path); size=13791 bytes
[OK] Directory present: data/policy_corpus (exact path); 2 entries: corpus_registry.json, README.md
[PASS] REQ-044-T04: committed synthetic loan applications: 7 committed input file(s): data/policy_corpus/corpus_registry.json, data/policy_corpus/README.md, data/vectorstore/index_integrity.json, data/vectorstore/index_manifest.json, data/vectorstore/lexical/bm25_education.json, data/vectorstore/lexical/bm25_mortgage.json, data/vectorstore/README.md
```

### REQ-045 - FAIL (80/100)

**Class:** IMPLEMENTATION  |  **Category:** affordability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-02

**Requirement:**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Status:** FAIL  
**Fit Score:** 80  
**Tests:** REQ-045-T01, REQ-045-T02, REQ-045-T03, REQ-045-T04  
**Reason:** 1 of 4 bound test(s) produced no satisfying evidence: REQ-045-T04.

**Evidence:**

```
[PASS] REQ-045-T01: DTI / disposable-income computation across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:320: "DTI-CONV": "src/rules.py — affordability ceiling, with the compensating-factor extension",
[PASS] REQ-045-T02: affordability figure in observable output (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json') (ALL: 1/1 satisfied)
[OK] /afford|\bDTI\b|disposable/ matched observable output: 'afford'
--- observable output (last lines) ---
Policy evidence (61 chunks, 61 distinct citations, all resolve: True)
  POL-AST-001 v1.0
  POL-AST-002 v1.0
  POL-AST-002 v1.0 rule AST-FTC-001
  POL-AST-002 v1.0 rule AST-FTC-003
  POL-AST-002 v1.0 rule AST-FTC-004
  POL-AST-002 v1.0 rule AST-FTC-005
  POL-AST-002 v1.0 section 5
  POL-AST-003 v2.0 rule AST-RSV-001
  POL-AST-003 v2.0 rule AST-RSV-002
  POL-AST-003 v2.0 rule AST-RSV-003
  POL-AST-003 v2.0 rule AST-RSV-005
  POL-AST-003 v2.0 section 5
  ... and 49 more

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/199 [00:00<?, ?it/s]
Loading weights:  18%|█▊        | 35/199 [00:00<00:00, 313.85it/s]
Loading weights:  54%|█████▍    | 107/199 [00:00<00:00, 539.52it/s]
Loading weights: 100%|██████████| 199/199 [00:00<00:00, 928.53it/s]

Loading weights:   0%|          | 0/105 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 105/105 [00:00<00:00, 2209.93it/s]
Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
[PASS] REQ-045-T03: threshold-bearing policy breach flag across implementation tree (147 files) (ALL: 2/2 satisfied)
[OK] eval/agent/dataset.py:316: #: reader, but no code compares them against a threshold.
[OK] eval/agent/dataset.py:158: asked, and scoring against it would penalise the system for failing to
[FAIL] REQ-045-T04: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the numeric DTI or disposable-income threshold that constitutes a policy breach' could be verified against an implementation.
```

### REQ-046 - FAIL (89/100)

**Class:** IMPLEMENTATION  |  **Category:** underwriting  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-03

**Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Status:** FAIL  
**Fit Score:** 89  
**Tests:** REQ-046-T01, REQ-046-T02, REQ-046-T03, REQ-046-T04, REQ-046-T05, REQ-046-T06, REQ-046-T07  
**Reason:** 1 of 7 bound test(s) produced no satisfying evidence: REQ-046-T07.

**Evidence:**

```
[PASS] REQ-046-T01: Decision vocabulary present in observable output: ['decline'] (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json')
[PASS] REQ-046-T02: the approve / refer / decline outcomes across implementation tree (147 files) (ALL: 3/3 satisfied)
[OK] eval/agent/dataset.py:41: #: ``APPROVE_WITH_CONDITIONS`` is listed because the golden sets use it — six
[OK] eval/agent/dataset.py:43: #: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
[OK] eval/agent/dataset.py:43: #: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
[PASS] REQ-046-T03: written rationale in observable output (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json') (ALL: 1/1 satisfied)
[OK] /rationale|reason|justification|because|explanation/ matched observable output: 'Rationale'
--- observable output (last lines) ---
Policy evidence (61 chunks, 61 distinct citations, all resolve: True)
  POL-AST-001 v1.0
  POL-AST-002 v1.0
  POL-AST-002 v1.0 rule AST-FTC-001
  POL-AST-002 v1.0 rule AST-FTC-003
  POL-AST-002 v1.0 rule AST-FTC-004
  POL-AST-002 v1.0 rule AST-FTC-005
  POL-AST-002 v1.0 section 5
  POL-AST-003 v2.0 rule AST-RSV-001
  POL-AST-003 v2.0 rule AST-RSV-002
  POL-AST-003 v2.0 rule AST-RSV-003
  POL-AST-003 v2.0 rule AST-RSV-005
  POL-AST-003 v2.0 section 5
  ... and 49 more

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

Loading weights:   0%|          | 0/199 [00:00<?, ?it/s]
Loading weights:  15%|█▌        | 30/199 [00:00<00:00, 271.82it/s]
Loading weights:  37%|███▋      | 73/199 [00:00<00:00, 360.12it/s]
Loading weights: 100%|██████████| 199/199 [00:00<00:00, 754.93it/s]

Loading weights:   0%|          | 0/105 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 105/105 [00:00<00:00, 2428.18it/s]
Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
[PASS] REQ-046-T04: decline handling across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:43: #: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
[PASS] REQ-046-T05: high-value case routing across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/review_triggers.py:257: add("high_value_exposure", "a jumbo transaction is a mandatory human-review trigger")
[PASS] REQ-046-T06: human-review route across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:63: "PENDING_HUMAN_REVIEW": REFER,
[FAIL] REQ-046-T07: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the loan value above which a case counts as a high-value case' could be verified against an implementation.
```

### REQ-047 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** workflow  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-04

**Requirement:**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-047-T01, REQ-047-T02, REQ-047-T03, REQ-047-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-047-T01: intent identification across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/calculations.py:335: occupancy_intent = (packet.get("subject_property") or {}).get("occupancy_intent")
[PASS] REQ-047-T02: intent-to-capability dispatch across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] mcp_server/capabilities.py:6: * the ``credpilot://system/capabilities`` resource, which is how a client sees
[PASS] REQ-047-T03: clarification of ambiguous requests across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] mcp_server/capabilities.py:93: "clarify_loan_product": "MCP elicitation — ask the client for the one missing "
[PASS] REQ-047-T04: out-of-scope escalation across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:99: unsupported_citations: list[str] = field(default_factory=list)
```

### REQ-048 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-05

**Requirement:**

~~~text
AC-05 | The copilot maintains context — it uses facts stated earlier in the interaction and recalls prior-session context on a return visit.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-048-T01, REQ-048-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-048-T01: within-interaction context (ALL: 2/2 satisfied)
[OK] Directory present: src/memory (exact path); 5 entries: __init__.py, __pycache__, long_term.py, short_term.py, store.py
[OK] short-term conversational context across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:329: "EMP-CNT": "src/rule_families/mortgage_ext.py — two-year history (refer, not "
[PASS] REQ-048-T02: cross-session recall (ALL: 3/3 satisfied)
[OK] File present: tests/test_memory_persistence.py (exact path); size=14984 bytes
[OK] File present: logs/memory_test.log (exact path); size=895 bytes
[OK] session-keyed persistence across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:218: ``run_id`` scopes the checkpoint thread to this evaluation run. Without it
```

### REQ-049 - FAIL (71/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-06

**Requirement:**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

**Status:** FAIL  
**Fit Score:** 71  
**Tests:** REQ-049-T01, REQ-049-T02, REQ-049-T03, REQ-049-T04  
**Reason:** 1 of 4 bound test(s) produced no satisfying evidence: REQ-049-T03.

**Evidence:**

```
[PASS] REQ-049-T01: prompt-injection refusal across implementation tree (147 files) (ALL: 2/2 satisfied)
[OK] eval/agent/dataset.py:342: "SEC-INJ": "src/guardrails/ + input_guardrails_node — injection detection and quarantine",
[OK] eval/agent/run_agent_eval.py:538: f"   Refusing to publish a run labelled 'every case judged' "
[PASS] REQ-049-T02: per-applicant data access control across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:172: # carries no applicant identifiers; tests/rag/test_pii_logging.py
[FAIL] REQ-049-T03: PII masking and leak-free logs (ALL: 1/2 satisfied)
[OK] masking implemented at scripts/export_traces.py:246: redaction_is_warm(
[NOT FOUND] 1 sensitive value(s) written in plaintext:
traces/phoenix-live.jsonl:813 matches /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b/
[PASS] REQ-049-T04: output-side masking before answers are emitted across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:171: # without re-running the model. It is built from redacted context and
```

### REQ-050 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-07

**Requirement:**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-050-T01, REQ-050-T02, REQ-050-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-050-T01: tool-invocation log per-call fields (ALL: 8/8 satisfied)
[OK] logs/tool_calls.jsonl: 430 tool-call record(s)
[OK] field 'timestamp' present as ['timestamp']
[OK] field 'agent/node' present as ['agent']
[OK] field 'tool_name' present as ['tool_name']
[OK] field 'args' present as ['args']
[OK] field 'result' present as ['result']
[OK] field 'latency_ms' present as ['latency_ms']
[OK] field 'status' present as ['status']
[PASS] REQ-050-T02: committed logging middleware that writes the tool-invocation log (ALL: 2/2 satisfied)
[OK] artifact present: logs/tool_calls.jsonl
[OK] producing code: scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[PASS] REQ-050-T03: All 12 tool name(s) in logs/tool_calls.jsonl reconcile with source:
clarify_loan_product -> mcp_server/capabilities.py
compute_affordability -> mcp_server/capabilities.py
draft_with_sampling -> mcp_server/capabilities.py
fetch_policy_rules -> scripts/verify_evidence_citations.py
get_policy_version -> mcp_server/capabilities.py
get_rule_dependencies -> mcp_server/capabilities.py
list_policy_rules -> mcp_server/capabilities.py
list_project_roots -> mcp_server/capabilities.py
resolve_citation -> mcp_server/capabilities.py
retrieve_policy -> mcp_server/capabilities.py
screen_risk_flags -> mcp_server/capabilities.py
validate_evidence -> mcp_server/capabilities.py
```

### REQ-051 - FAIL (75/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-08

**Requirement:**

~~~text
AC-08 | docs/failure-analysis.md documents ≥ 3 real failures from your own runs, each citing the Phoenix run_id + span_id (or a tool-log record) that shows it, plus root cause and fix.
~~~

**Status:** FAIL  
**Fit Score:** 75  
**Tests:** REQ-051-T01, REQ-051-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-051-T02.

**Evidence:**

```
[PASS] REQ-051-T01: failure-mode analysis docs/failure-analysis.md (ALL: 5/5 satisfied)
[OK] 106 documented failure section(s) (>= 3)
[OK] 1 distinct run_id and 1 distinct span_id citation(s)
[OK] 3 failure(s) carry an evidence citation (>= 3)
[OK] 21 root-cause statement(s)
[OK] 29 fix statement(s)
[FAIL] REQ-051-T02: 4 unresolvable citation(s) across 105 document(s) (treated as missing per the Citation-Resolves Rule):
docs/rag/REQUIREMENTS_MAPPING.md cites 'assets/phoenix-traces.png' -> present but uncommitted
docs/rag/REQUIREMENTS_MAPPING.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
README.md cites 'docs/assets/phoenix-traces.png' -> present but uncommitted
README.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
```

### REQ-052 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-09

**Requirement:**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-052-T01, REQ-052-T02, REQ-052-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-052-T01: golden-signals report reports/golden_signals.json (ALL: 7/7 satisfied)
[OK] latency for the thinking span type: present in reports/golden_signals.json
[OK] latency for the acting span type: present in reports/golden_signals.json
[OK] latency for the tool span type: present in reports/golden_signals.json
[OK] tokens in/out: present in reports/golden_signals.json
[OK] cost estimate: present in reports/golden_signals.json
[OK] accuracy from the eval: present in reports/golden_signals.json
[OK] hallucination rate from the eval: present in reports/golden_signals.json
[PASS] REQ-052-T02: Phoenix-derived golden-signals report (ALL: 2/2 satisfied)
[OK] artifact present: reports/golden_signals.json
[OK] producing code: scripts/build_golden_signals.py:112: frame = client.get_spans_dataframe(project_name="credpilot")
[PASS] REQ-052-T03: cost/latency dashboard screenshot AND its underlying data file (ALL: 2/2 satisfied)
[OK] reports/dashboard.png: valid PNG, 206181 bytes
[OK] reports/dashboard_data.csv: 35 data row(s), header='group,metric,value,target,unit,source'
```

### REQ-053 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-10

**Requirement:**

~~~text
AC-10 | Input/output guardrails wired into the agent's I/O path, and a machine-generated audit trail of agent actions (logs/agent_actions.jsonl).
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-053-T01, REQ-053-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-053-T01: input/output guardrails wired into the I/O path (ALL: 5/5 satisfied)
[OK] guardrail package src/guardrails with 4 module(s)
[OK] input guardrail: src/guardrails/sanitize.py
[OK] output guardrail: src/guardrails/__init__.py
[OK] blocks or sanitizes: src/guardrails/__init__.py
[OK] wired into the I/O path: eval/agent/dataset.py references the guardrail layer
[PASS] REQ-053-T02: machine-generated audit trail (ALL: 7/7 satisfied)
[OK] logs/agent_actions.jsonl: 831 audit record(s)
[OK] field 'actor' present
[OK] field 'action' present
[OK] field 'tool' present
[OK] field 'decision' present
[OK] field 'timestamp' present
[OK] audit middleware writes it: scripts/verify_evidence_citations.py
```

### REQ-054 - FAIL (71/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-11

**Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Status:** FAIL  
**Fit Score:** 71  
**Tests:** REQ-054-T01, REQ-054-T02, REQ-054-T03, REQ-054-T04, REQ-054-T05  
**Reason:** 1 of 5 bound test(s) produced no satisfying evidence: REQ-054-T05.

**Evidence:**

```
[PASS] REQ-054-T01: File present: docs/risk-register.md (exact path); size=24231 bytes
[PASS] REQ-054-T02: File present: docs/model-card.md (exact path); size=25500 bytes
[PASS] REQ-054-T03: compliance mapping at docs/compliance.md (ALL: 3/3 satisfied)
[OK] EU AI Act obligations: docs/compliance.md:11: EU AI Act
[OK] NIST AI RMF obligations: docs/compliance.md:30: NIST AI RMF
[OK] DPDP obligations: docs/compliance.md:52: DPDP
[PASS] REQ-054-T04: File present: docs/output-risk.md (exact path); size=12473 bytes
[FAIL] REQ-054-T05: 4 unresolvable citation(s) across 105 document(s) (treated as missing per the Citation-Resolves Rule):
docs/rag/REQUIREMENTS_MAPPING.md cites 'assets/phoenix-traces.png' -> present but uncommitted
docs/rag/REQUIREMENTS_MAPPING.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
README.md cites 'docs/assets/phoenix-traces.png' -> present but uncommitted
README.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
```

### REQ-055 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-12

**Requirement:**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-055-T01, REQ-055-T02, REQ-055-T03, REQ-055-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-055-T01: agent evaluation report (ALL: 6/6 satisfied)
[OK] hallucination metric: present in reports/eval_report.json
[OK] faithfulness metric: present in reports/eval_report.json
[OK] answer-relevance metric: present in reports/eval_report.json
[OK] a golden set of cases: present in reports/eval_report.json
[OK] evaluation harness: eval/agent/run_agent_eval.py
[OK] the harness uses DeepEval (or an equivalent LLM-as-judge)
[PASS] REQ-055-T02: routing-logic test at tests/test_routing.py (ALL: 3/3 satisfied)
[OK] tests/test_routing.py defines 22 test function(s): ['test_each_supervisor_route_has_its_own_target', 'test_an_unrecognized_route_asks_rather_than_guesses', 'test_a_halted_run_goes_to_a_human_whatever_it_was_routed_to', 'test_an_unresolved_product_routes_to_human_review', 'test_a_resolved_product_routes_to_its_own_retrieval_node', 'test_retrieval_with_no_evidence_routes_to_human_review', 'test_retrieval_with_evidence_routes_to_its_own_eligibility_node', 'test_a_policy_question_skips_the_assessment_nodes']
[OK] tests/test_routing.py contains assertions
[OK] routes to the right worker: matched 'Rout'
[PASS] REQ-055-T03: loop/cascade guard test at tests/test_loops.py (ALL: 3/3 satisfied)
[OK] tests/test_loops.py defines 10 test function(s): ['test_a_fresh_run_has_budget', 'test_an_exhausted_run_is_detected', 'test_a_missing_budget_falls_back_to_the_default', 'test_the_budget_leaves_headroom_over_a_real_run', 'test_a_runaway_loop_is_stopped_by_the_step_budget', 'test_the_halt_reason_names_the_node_and_the_budget', 'test_the_recursion_limit_stops_a_loop_the_budget_cannot_see', 'test_the_real_graph_carries_the_recursion_limit']
[OK] tests/test_loops.py contains assertions
[OK] max-steps / recursion-limit guard: matched 'max-step'
[PASS] REQ-055-T04: tool-contract test at tests/test_tool_contracts.py (ALL: 4/4 satisfied)
[OK] tests/test_tool_contracts.py defines 15 test function(s): ['test_the_input_schema_is_declared', 'test_the_input_schema_rejects_an_unknown_field', 'test_the_input_schema_requires_a_query', 'test_the_output_schema_is_typed', 'test_the_output_shape_matches_the_contract', 'test_an_unresolvable_product_is_a_status_not_an_exception', 'test_no_applicable_policy_is_distinguishable_from_an_empty_answer', 'test_an_unknown_product_domain_raises_with_a_usable_message']
[OK] tests/test_tool_contracts.py contains assertions
[OK] input/output schema assertion: matched 'contract'
[OK] an error path: matched 'error'
```

### REQ-056 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-01

**Requirement:**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-056-T01, REQ-056-T02, REQ-056-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-056-T01: No committed secret matched 6 credential patterns across 1734 scanned files.
[PASS] REQ-056-T02: secrets hygiene (ALL: 3/3 satisfied)
[OK] .gitignore ignores .env: '.env'
[OK] .env.example present as the committed env-var template
[OK] no .env file is committed
[PASS] REQ-056-T03: environment-variable configuration across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] mcp_server/server.py:65: os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
```

### REQ-057 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-02

**Requirement:**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-057-T01, REQ-057-T02, REQ-057-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-057-T01: single documented command plus a regeneration command (ALL: 3/3 satisfied)
[OK] single documented run command: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[OK] second documented command regenerates traces: 'python scripts/export_traces.py'
[OK] documented command regenerates the evaluation: 'python -m eval.agent.run_agent_eval --no-judge'
[PASS] REQ-057-T02: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in eval/agent/run_agent_eval.py
[OK] CLI invocation documented: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[PASS] REQ-057-T03: committed sample inputs: 7 committed input file(s): data/policy_corpus/corpus_registry.json, data/policy_corpus/README.md, data/vectorstore/index_integrity.json, data/vectorstore/index_manifest.json, data/vectorstore/lexical/bm25_education.json, data/vectorstore/lexical/bm25_mortgage.json, data/vectorstore/README.md
```

### REQ-058 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-03

**Requirement:**

~~~text
NFR-03 | Untrusted free-text applicant-supplied content is quarantined and never treated as instructions.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-058-T01, REQ-058-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-058-T01: quarantine of untrusted applicant-supplied content across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:342: "SEC-INJ": "src/guardrails/ + input_guardrails_node — injection detection and quarantine",
[PASS] REQ-058-T02: untrusted content marked as data, not instructions across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:342: "SEC-INJ": "src/guardrails/ + input_guardrails_node — injection detection and quarantine",
```

### REQ-059 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-04

**Requirement:**

~~~text
NFR-04 | Agent pipeline uses async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions).
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-059-T01, REQ-059-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-059-T01: async tool/model invocation (ALL: 2/2 satisfied)
[OK] 49 async definition(s):
eval/agent/judges.py:91: async def a_generate
mcp_server/client.py:54: async def open_session
mcp_server/client.py:65: async def load_surface
mcp_server/client.py:78: async def load_mcp_policy_tools
mcp_server/server.py:653: async def clarify_loan_product
mcp_server/server.py:740: async def draft_with_sampling
mcp_server/server.py:829: async def list_project_roots
src/mcp_host/client.py:729: async def open_client
src/mcp_host/client.py:250: async def __aenter__
src/mcp_host/client.py:254: async def __aexit__
[OK] 55 await expression(s), so the async path is actually used
[PASS] REQ-059-T02: graceful degradation on tool/model failure (ALL: 4/4 satisfied)
[OK] timeouts: scripts/capture_phoenix_screenshot.py:50: def _phoenix_is_up(base: str, timeout: float = 5.0) -> tuple[bool, str]:
[OK] retries: src/graph.py:1318: """One retrieval, with a deadline and bounded retries (NFR-04).
[OK] exit conditions: eval/retrieval/dataset.py:131: break
[OK] failure handling around tool/model calls: eval/agent/judges.py:114: except Exception:  # noqa: BLE001 - fall through to the salvage attempt
```

### REQ-060 - FAIL (25/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-05

**Requirement:**

~~~text
NFR-05 | All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext.
~~~

**Status:** FAIL  
**Fit Score:** 25  
**Tests:** REQ-060-T01, REQ-060-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-060-T02.

**Evidence:**

```
[PASS] REQ-060-T01: synthetic data declaration across implementation tree (553 files) (ALL: 1/1 satisfied)
[OK] data/policy_corpus/corpus_registry.json:2: "description": "Machine-generated inventory of the lending-policy corpora CredPilot's vector and lexical indexes are built from. The policy documents themselves are committed under synthetic_data/<product>/policy_corpus/ and are not duplicated here.",
[FAIL] REQ-060-T02: PII masking and leak-free logs (ALL: 1/2 satisfied)
[OK] masking implemented at scripts/export_traces.py:246: redaction_is_warm(
[NOT FOUND] 1 sensitive value(s) written in plaintext:
traces/phoenix-live.jsonl:813 matches /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b/
```

### REQ-061 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-06

**Requirement:**

~~~text
NFR-06 | Evidence artifacts (traces, logs, reports) are machine-generated by committed code; the code that produced each is committed alongside it.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-061-T01, REQ-061-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-061-T01: producing code for 7 present evidence artifact(s) (ALL: 7/7 satisfied)
[OK] logs/tool_calls.jsonl <- produced by scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[OK] logs/agent_actions.jsonl <- produced by scripts/verify_evidence_citations.py:216: artifact="logs/agent_actions.jsonl",
[OK] logs/mcp_transcript.jsonl <- produced by mcp_server/server.py:122: The transcript at ``logs/mcp_transcript.jsonl`` is written from here, which
[OK] reports/golden_signals.json <- produced by scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[OK] reports/dashboard_data.csv <- produced by scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
[OK] reports/eval_report.json <- produced by eval/agent/run_agent_eval.py:72: REPORT_PATH = REPORTS / "eval_report.json"
[OK] logs/memory_test.log <- produced by src/memory/__init__.py:3: *"src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log |
[PASS] REQ-061-T02: artifact and its producer both committed (ALL: 2/2 satisfied)
[OK] producing code for 7 present evidence artifact(s) (ALL: 7/7 satisfied)
[OK] logs/tool_calls.jsonl <- produced by scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[OK] logs/agent_actions.jsonl <- produced by scripts/verify_evidence_citations.py:216: artifact="logs/agent_actions.jsonl",
[OK] logs/mcp_transcript.jsonl <- produced by mcp_server/server.py:122: The transcript at ``logs/mcp_transcript.jsonl`` is written from here, which
[OK] reports/golden_signals.json <- produced by scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[OK] reports/dashboard_data.csv <- produced by scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
[OK] reports/eval_report.json <- produced by eval/agent/run_agent_eval.py:72: REPORT_PATH = REPORTS / "eval_report.json"
[OK] logs/memory_test.log <- produced by src/memory/__init__.py:3: *"src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log |
[OK] All 24 present named artifact(s) are committed: src/graph.py, logs/mcp_transcript.jsonl, tests/test_memory_persistence.py, logs/memory_test.log, src/tools/rag_tool.py, src/observability/tracing.py, traces/phoenix_spans.jsonl, logs/tool_calls.jsonl, docs/failure-analysis.md, reports/golden_signals.json, reports/dashboard.png, reports/dashboard_data.csv, logs/agent_actions.jsonl, .env.example, .gitignore, docs/risk-register.md, docs/model-card.md, docs/compliance.md, docs/output-risk.md, reports/eval_report.json, tests/test_routing.py, tests/test_loops.py, tests/test_tool_contracts.py, README.md
```

### REQ-062 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 6.1 In Scope — bullet 1

**Requirement:**

~~~text
The LangGraph multi-agent copilot (foundation) plus its full observability, cost-governance, security, governance and evaluation surface.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-062-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-062-T01: the full in-scope surface (ALL: 6/6 satisfied)
[OK] File present: src/graph.py (exact path); size=105982 bytes
[OK] File present: src/observability/tracing.py (exact path); size=11075 bytes
[OK] File present: reports/golden_signals.json (exact path); size=9605 bytes
[OK] Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
```

### REQ-063 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 6.1 In Scope — bullet 2

**Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-063-T01, REQ-063-T02, REQ-063-T03, REQ-063-T04, REQ-063-T05  
**Reason:** All 5 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-063-T01: Phoenix tracing (ALL: 2/2 satisfied)
[OK] File present: src/observability/tracing.py (exact path); size=11075 bytes
[OK] a trace export (ANY: 1/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[OK] File present: traces/phoenix_spans.jsonl (exact path); size=501494 bytes
[PASS] REQ-063-T02: golden signals and cost/latency governance (ALL: 2/2 satisfied)
[OK] File present: reports/golden_signals.json (exact path); size=9605 bytes
[OK] File present: reports/dashboard_data.csv (exact path); size=1576 bytes
[PASS] REQ-063-T03: guardrails, audit and secrets hygiene (ALL: 3/3 satisfied)
[OK] Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[OK] File present: logs/agent_actions.jsonl (exact path); size=536468 bytes
[OK] File present: .env.example (exact path); size=2595 bytes
[PASS] REQ-063-T04: governance and compliance docs (ALL: 4/4 satisfied)
[OK] File present: docs/risk-register.md (exact path); size=24231 bytes
[OK] File present: docs/model-card.md (exact path); size=25500 bytes
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[OK] File present: docs/output-risk.md (exact path); size=12473 bytes
[PASS] REQ-063-T05: agent-level evaluation and tests (ALL: 4/4 satisfied)
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
[OK] File present: tests/test_routing.py (exact path); size=15913 bytes
[OK] File present: tests/test_loops.py (exact path); size=8870 bytes
[OK] File present: tests/test_tool_contracts.py (exact path); size=8964 bytes
```

### REQ-064 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 6.1 In Scope — bullet 3

**Requirement:**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-064-T01, REQ-064-T02, REQ-064-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-064-T01: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in eval/agent/run_agent_eval.py
[OK] CLI invocation documented: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[PASS] REQ-064-T02: the CLI invoking the graph across implementation tree (147 files) (ALL: 2/2 satisfied)
[OK] eval/agent/dataset.py:43: #: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
[OK] eval/agent/dataset.py:12: ``decision_reasons.csv``) that :mod:`src.application_context` forbids runtime
[PASS] REQ-064-T03: single documented command plus a regeneration command (ALL: 3/3 satisfied)
[OK] single documented run command: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[OK] second documented command regenerates traces: 'python scripts/export_traces.py'
[OK] documented command regenerates the evaluation: 'python -m eval.agent.run_agent_eval --no-judge'
```

### REQ-065 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 1

**Requirement:**

~~~text
Containerized / cloud deployment (Docker, Rancher, k8s) — deferred; do not spend hackathon time on it.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-065-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-065-T01: Docker / Rancher / k8s deployment artifacts: no file matches ['Dockerfile', '*.dockerfile', 'docker-compose*.yml', 'docker-compose*.yaml', 'compose.yaml', 'compose.yml', '*.k8s.yaml', 'Chart.yaml', 'rancher*.yml'] across 1862 files
```

### REQ-066 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 2

**Requirement:**

~~~text
Real credit-bureau or core-banking integrations — use synthetic application and policy data.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-066-T01, REQ-066-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-066-T01.

**Evidence:**

```
[FAIL] REQ-066-T01: real credit-bureau or core-banking integrations: prohibited content found (3 hit(s))
/experian|equifax|transunion|cibil|creditbureau|credit[_\- ]bureau[_\- ]api/ matched synthetic_data/mortgage/generator/synth/people.py:6: with no network access and no extra dependency - which is what the Reproducibility
/experian|equifax|transunion|cibil|creditbureau|credit[_\- ]bureau[_\- ]api/ matched tests/rag/test_documentation.py:195: "REQ-033",  # Reproducibility
/experian|equifax|transunion|cibil|creditbureau|credit[_\- ]bureau[_\- ]api/ matched tests/test_context_engineering.py:193: """Reproducibility (REQ-033): a compressed prompt must be the same every run."""
[PASS] REQ-066-T02: synthetic application and policy data (ALL: 2/2 satisfied)
[OK] Directory present: data/policy_corpus (exact path); 2 entries: corpus_registry.json, README.md
[OK] committed synthetic application data: 7 committed input file(s): data/policy_corpus/corpus_registry.json, data/policy_corpus/README.md, data/vectorstore/index_integrity.json, data/vectorstore/index_manifest.json, data/vectorstore/lexical/bm25_education.json, data/vectorstore/lexical/bm25_mortgage.json, data/vectorstore/README.md
```

### REQ-067 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** non_functional  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 3

**Requirement:**

~~~text
Front-end visual polish; generic unit-test volume for its own sake.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-067-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-067-T01: front-end build tooling: no file matches ['package.json', 'webpack.config.js', 'vite.config.*', 'tailwind.config.*', 'next.config.*', 'angular.json'] across 1862 files
```

### REQ-068 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 4

**Requirement:**

~~~text
Advanced OAuth flows and live secrets-rotation infrastructure (document the approach instead).
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-068-T01, REQ-068-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-068-T01: advanced OAuth flows and live secrets-rotation infrastructure: no prohibited pattern matched across 147 scanned files
[PASS] REQ-068-T02: the documented approach to OAuth and secrets rotation across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] docs/rag/RUNBOOK.md:576: <https://aistudio.google.com/apikey>. An OAuth access token (starting `AQ.`) is
```

### REQ-069 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 1

**Requirement:**

~~~text
This is the checklist your submission is scored against.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-069-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-069-T01: All 25 checklist artifacts are referenced by the 320 registered test cases, so this suite scores the stated checklist.
```

### REQ-070 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 2

**Requirement:**

~~~text
Each artifact must be present at (or near) the path shown and contain what is listed.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-070-T01, REQ-070-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-070-T01: every artifact named by the checklist is present at (or near) its path (ALL: 24/24 satisfied)
[OK] src/graph.py -> src/graph.py
[OK] logs/mcp_transcript.jsonl -> logs/mcp_transcript.jsonl
[OK] tests/test_memory_persistence.py -> tests/test_memory_persistence.py
[OK] logs/memory_test.log -> logs/memory_test.log
[OK] src/tools/rag_tool.py -> src/tools/rag_tool.py
[OK] src/observability/tracing.py -> src/observability/tracing.py
[OK] logs/tool_calls.jsonl -> logs/tool_calls.jsonl
[OK] docs/failure-analysis.md -> docs/failure-analysis.md
[OK] reports/golden_signals.json -> reports/golden_signals.json
[OK] reports/dashboard.png -> reports/dashboard.png
[OK] reports/dashboard_data.csv -> reports/dashboard_data.csv
[OK] logs/agent_actions.jsonl -> logs/agent_actions.jsonl
[OK] .env.example -> .env.example
[OK] .gitignore -> .gitignore
[OK] docs/risk-register.md -> docs/risk-register.md
[OK] docs/model-card.md -> docs/model-card.md
[OK] docs/compliance.md -> docs/compliance.md
[OK] docs/output-risk.md -> docs/output-risk.md
[OK] reports/eval_report.json -> reports/eval_report.json
[OK] tests/test_routing.py -> tests/test_routing.py
[OK] tests/test_loops.py -> tests/test_loops.py
[OK] tests/test_tool_contracts.py -> tests/test_tool_contracts.py
[OK] README.md -> README.md
[OK] traces/phoenix_spans.parquet or traces/phoenix_spans.jsonl -> traces/phoenix_spans.jsonl
[PASS] REQ-070-T02: content of 24 present checklist artifact(s) (ALL: 24/24 satisfied)
[OK] src/graph.py: 105982 bytes of content
[OK] logs/mcp_transcript.jsonl: 110 valid JSON record(s)
[OK] tests/test_memory_persistence.py: 14984 bytes of content
[OK] logs/memory_test.log: 895 bytes of content
[OK] src/tools/rag_tool.py: 13791 bytes of content
[OK] src/observability/tracing.py: 11075 bytes of content
[OK] traces/phoenix_spans.jsonl: 1119 valid JSON record(s)
[OK] logs/tool_calls.jsonl: 430 valid JSON record(s)
[OK] docs/failure-analysis.md: 56777 bytes of content
[OK] reports/golden_signals.json: valid JSON, 9605 bytes
[OK] reports/dashboard.png: 206181 bytes of content
[OK] reports/dashboard_data.csv: 1576 bytes of content
[OK] logs/agent_actions.jsonl: 831 valid JSON record(s)
[OK] .env.example: 2595 bytes of content
[OK] .gitignore: 1302 bytes of content
[OK] docs/risk-register.md: 24231 bytes of content
[OK] docs/model-card.md: 25500 bytes of content
[OK] docs/compliance.md: 13627 bytes of content
[OK] docs/output-risk.md: 12473 bytes of content
[OK] reports/eval_report.json: valid JSON, 10334 bytes
[OK] tests/test_routing.py: 15913 bytes of content
[OK] tests/test_loops.py: 8870 bytes of content
[OK] tests/test_tool_contracts.py: 8964 bytes of content
[OK] README.md: 20794 bytes of content
```

### REQ-071 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 3

**Requirement:**

~~~text
Remember the Evidence-in-Repo and Citation-Resolves rules: outputs must be produced by committed code, and every citation must resolve to a committed artifact.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-071-T01, REQ-071-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-071-T02.

**Evidence:**

```
[PASS] REQ-071-T01: producing code for 7 present evidence artifact(s) (ALL: 7/7 satisfied)
[OK] logs/tool_calls.jsonl <- produced by scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[OK] logs/agent_actions.jsonl <- produced by scripts/verify_evidence_citations.py:216: artifact="logs/agent_actions.jsonl",
[OK] logs/mcp_transcript.jsonl <- produced by mcp_server/server.py:122: The transcript at ``logs/mcp_transcript.jsonl`` is written from here, which
[OK] reports/golden_signals.json <- produced by scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[OK] reports/dashboard_data.csv <- produced by scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
[OK] reports/eval_report.json <- produced by eval/agent/run_agent_eval.py:72: REPORT_PATH = REPORTS / "eval_report.json"
[OK] logs/memory_test.log <- produced by src/memory/__init__.py:3: *"src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log |
[FAIL] REQ-071-T02: 4 unresolvable citation(s) across 105 document(s) (treated as missing per the Citation-Resolves Rule):
docs/rag/REQUIREMENTS_MAPPING.md cites 'assets/phoenix-traces.png' -> present but uncommitted
docs/rag/REQUIREMENTS_MAPPING.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
README.md cites 'docs/assets/phoenix-traces.png' -> present but uncommitted
README.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
```

### REQ-072 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 7.1 Agentic System — Foundation — table row "LangGraph graph"

**Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-072-T01, REQ-072-T02, REQ-072-T03, REQ-072-T04, REQ-072-T05, REQ-072-T06  
**Reason:** All 6 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-072-T01: File present: src/graph.py (exact path); size=105982 bytes
[PASS] REQ-072-T02: typed graph state across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:91: @dataclass
[PASS] REQ-072-T03: supervisor + >=3 worker agents (graph at src/graph.py) (ALL: 2/2 satisfied)
[OK] supervisor present (eval/agent/run_agent_eval.py: supervisor)
[OK] >=3 worker agents present:
eligibility-and-affordability agent -> src/graph.py
policy-retrieval agent -> eval/agent/run_agent_eval.py
risk-screening agent -> mcp_server/capabilities.py
[PASS] REQ-072-T04: conditional edges added to the graph (AST call analysis) (ALL: 1/1 satisfied)
[OK] src/graph.py contains a call to 'add_conditional_edges'
[PASS] REQ-072-T05: checkpointer (ALL: 2/2 satisfied)
[OK] checkpointer referenced across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/run_agent_eval.py:218: ``run_id`` scopes the checkpoint thread to this evaluation run. Without it
[OK] a checkpointer implementation (ANY: 1/2 satisfied)
[OK] SQLite checkpointer across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/graph.py:2424: from langgraph.checkpoint.sqlite import SqliteSaver
[NOT FOUND] checkpointer class across implementation tree (147 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /MemorySaver|BaseCheckpointSaver/ in 147 files under implementation tree
[PASS] REQ-072-T06: structured output at node boundaries across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/graph.py:2454: return packet_state(
```

### REQ-073 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 7.1 Agentic System — Foundation — table row "MCP server"

**Requirement:**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-073-T01, REQ-073-T02, REQ-073-T03, REQ-073-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-073-T01: Directory present: mcp_server (exact path); 5 entries: __init__.py, __pycache__, capabilities.py, client.py, server.py
[PASS] REQ-073-T02: MCP surface in mcp_server (4 module(s)) (ALL: 2/2 satisfied)
[OK] >=2 MCP tools: 11 registered ['clarify_loan_product', 'compute_affordability', 'draft_with_sampling', 'get_policy_version', 'get_rule_dependencies', 'list_policy_rules', 'list_project_roots', 'resolve_citation', 'retrieve_policy', 'screen_risk_flags', 'validate_evidence']
[OK] >=1 MCP resource: 10 registered ['education_catalog', 'education_policies', 'education_rules', 'education_thresholds', 'index_manifest', 'mortgage_catalog', 'mortgage_policies', 'mortgage_rules', 'mortgage_thresholds', 'system_capabilities']
[PASS] REQ-073-T03: consumed via langchain-mcp-adapters (ALL: 2/2 satisfied)
[OK] langchain-mcp-adapters declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:27: langchain-mcp-adapters>=0.3.0,<0.4
[OK] langchain_mcp_adapters imported (import analysis) (ALL: 1/1 satisfied)
[OK] mcp_server/client.py:67: from langchain_mcp_adapters.resources import ...
[PASS] REQ-073-T04: committed MCP tool-call transcript (ALL: 2/2 satisfied)
[OK] logs/mcp_transcript.jsonl: 110 transcript record(s)
[OK] logs/mcp_transcript.jsonl is committed
```

### REQ-074 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 7.1 Agentic System — Foundation — table row "Context engineering"

**Requirement:**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-074-T01, REQ-074-T02, REQ-074-T03, REQ-074-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-074-T01: Directory present: src/context (exact path); 7 entries: __init__.py, __pycache__, assemble.py, compress.py, isolate.py, select.py, write.py
[PASS] REQ-074-T02: the four named context operations across 'src/context' (6 files) (ALL: 4/4 satisfied)
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[PASS] REQ-074-T03: summarization middleware across 'src/context' (6 files) (ALL: 1/1 satisfied)
[OK] src/context/__init__.py:3: *"src/context/ | write/select/compress/isolate; summarization middleware;
[PASS] REQ-074-T04: quarantine of untrusted text across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:342: "SEC-INJ": "src/guardrails/ + input_guardrails_node — injection detection and quarantine",
```

### REQ-075 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 7.1 Agentic System — Foundation — table row "Tiered memory"

**Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-075-T01, REQ-075-T02, REQ-075-T03, REQ-075-T04, REQ-075-T05  
**Reason:** All 5 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-075-T01: Directory present: src/memory (exact path); 5 entries: __init__.py, __pycache__, long_term.py, short_term.py, store.py
[PASS] REQ-075-T02: File present: tests/test_memory_persistence.py (exact path); size=14984 bytes
[PASS] REQ-075-T03: committed memory test output log (ALL: 2/2 satisfied)
[OK] File present: logs/memory_test.log (exact path); size=895 bytes
[OK] git ls-files lists 'logs/memory_test.log' -> artifact is committed
[PASS] REQ-075-T04: short + long/semantic memory (ALL: 2/2 satisfied)
[OK] short-term memory tier across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/memory/__init__.py:9: * **Short-term** (:mod:`~src.memory.short_term`) — what happened in *this*
[OK] long/semantic memory tier across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/retrieval/ablation.py:74: def _dense_search(self, domain, query_vector, top_k, allowed_ids):
[PASS] REQ-075-T05: cross-session recall test at tests/test_memory_persistence.py (ALL: 3/3 satisfied)
[OK] tests/test_memory_persistence.py defines 19 test function(s): ['test_short_term_holds_facts_stated_earlier', 'test_short_term_is_bounded', 'test_an_applicant_turn_stays_untrusted_however_old', 'test_short_term_redacts_on_write', 'test_short_term_round_trips_through_the_checkpointer_shape', 'test_long_term_refuses_to_store_a_decision', 'test_long_term_refuses_to_cache_policy', 'test_long_term_refuses_an_unknown_kind']
[OK] tests/test_memory_persistence.py contains assertions
[OK] cross-session recall subject: matched 'session'
```

### REQ-076 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** policy  |  **Source:** Section 7.1 Agentic System — Foundation — table row "Agentic-RAG tool"

**Requirement:**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-076-T01, REQ-076-T02, REQ-076-T03, REQ-076-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-076-T01: File present: src/tools/rag_tool.py (exact path); size=13791 bytes
[PASS] REQ-076-T02: Directory present: data/policy_corpus (exact path); 2 entries: corpus_registry.json, README.md
[PASS] REQ-076-T03: retrieval-in-the-loop (ALL: 2/2 satisfied)
[OK] the RAG capability exposed as an agent tool across 'src/tools' (2 files) (ALL: 1/1 satisfied)
[OK] src/tools/rag_tool.py:1: """The agentic-RAG tool.
[OK] retrieval invoked by the tool across 'src/tools' (2 files) (ALL: 1/1 satisfied)
[OK] src/tools/rag_tool.py:3: This is the tool the Policy Retrieval Agent calls when it needs policy evidence.
[PASS] REQ-076-T04: the corpus declared synthetic across implementation tree (1712 files) (ALL: 1/1 satisfied)
[OK] data/policy_corpus/corpus_registry.json:2: "description": "Machine-generated inventory of the lending-policy corpora CredPilot's vector and lexical indexes are built from. The policy documents themselves are committed under synthetic_data/<product>/policy_corpus/ and are not duplicated here.",
```

### REQ-077 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Phoenix instrumentation"

**Requirement:**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-077-T01, REQ-077-T02, REQ-077-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-077-T01: File present: src/observability/tracing.py (exact path); size=11075 bytes
[PASS] REQ-077-T02: the tracer actually invoked (AST call analysis) (ANY: 1/5 satisfied)
[OK] src/observability/tracing.py contains a call to 'register'
[NOT FOUND] no call to 'instrument' in 147 Python file(s)
[NOT FOUND] no call to 'LangChainInstrumentor' in 147 Python file(s)
[NOT FOUND] no call to 'launch_app' in 147 Python file(s)
[NOT FOUND] no call to 'tracer_provider' in 147 Python file(s)
[PASS] REQ-077-T03: the run path referencing the tracing module across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/retrieval/run_retrieval_eval.py:50: from src.observability.tracing import configure_tracing, flush_traces  # noqa: E402
```

### REQ-078 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Trace export"

**Requirement:**

~~~text
Trace export | traces/phoenix_spans.parquet (or .jsonl) | ≥1 full run; spans across multiple agents + every tool call; latencies present
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-078-T01, REQ-078-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-078-T01: trace export artifact (ANY: 1/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[OK] File present: traces/phoenix_spans.jsonl (exact path); size=501494 bytes
[PASS] REQ-078-T02: trace export traces/phoenix_spans.jsonl (ALL: 3/3 satisfied)
[OK] 1119 span(s) exported from at least one full run
[OK] spans span multiple components: ['agent.education', 'agent.eligibility', 'agent.final_response', 'agent.human_review', 'agent.mortgage', 'agent.recommendation', 'agent.risk', 'bm25.search', 'chroma.search', 'citation.validate', 'domain.resolve', 'embedding.query']
[OK] latency evidence present via key(s) ['latency_ms', 'start_time', 'end_time']
```

### REQ-079 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Tool-invocation log"

**Requirement:**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-079-T01, REQ-079-T02, REQ-079-T03, REQ-079-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-079-T01: File present: logs/tool_calls.jsonl (exact path); size=422236 bytes
[PASS] REQ-079-T02: tool-invocation log per-call fields (ALL: 8/8 satisfied)
[OK] logs/tool_calls.jsonl: 430 tool-call record(s)
[OK] field 'timestamp' present as ['timestamp']
[OK] field 'agent/node' present as ['agent']
[OK] field 'tool_name' present as ['tool_name']
[OK] field 'args' present as ['args']
[OK] field 'result' present as ['result']
[OK] field 'latency_ms' present as ['latency_ms']
[OK] field 'status' present as ['status']
[PASS] REQ-079-T03: machine-generated tool-invocation log (ALL: 2/2 satisfied)
[OK] artifact present: logs/tool_calls.jsonl
[OK] producing code: scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[PASS] REQ-079-T04: All 12 tool name(s) in logs/tool_calls.jsonl reconcile with source:
clarify_loan_product -> mcp_server/capabilities.py
compute_affordability -> mcp_server/capabilities.py
draft_with_sampling -> mcp_server/capabilities.py
fetch_policy_rules -> scripts/verify_evidence_citations.py
get_policy_version -> mcp_server/capabilities.py
get_rule_dependencies -> mcp_server/capabilities.py
list_policy_rules -> mcp_server/capabilities.py
list_project_roots -> mcp_server/capabilities.py
resolve_citation -> mcp_server/capabilities.py
retrieve_policy -> mcp_server/capabilities.py
screen_risk_flags -> mcp_server/capabilities.py
validate_evidence -> mcp_server/capabilities.py
```

### REQ-080 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Failure-mode analysis"

**Requirement:**

~~~text
Failure-mode analysis | docs/failure-analysis.md | ≥3 real failures, EACH citing Phoenix run_id + span_id (or tool-log record) + root cause + fix
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-080-T01, REQ-080-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-080-T01: File present: docs/failure-analysis.md (exact path); size=56777 bytes
[PASS] REQ-080-T02: failure-mode analysis docs/failure-analysis.md (ALL: 5/5 satisfied)
[OK] 106 documented failure section(s) (>= 3)
[OK] 1 distinct run_id and 1 distinct span_id citation(s)
[OK] 3 failure(s) carry an evidence citation (>= 3)
[OK] 21 root-cause statement(s)
[OK] 29 fix statement(s)
```

### REQ-081 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.3 Performance & Cost Governance — table row "Golden-signals report"

**Requirement:**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-081-T01, REQ-081-T02, REQ-081-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-081-T01: File present: reports/golden_signals.json (exact path); size=9605 bytes
[PASS] REQ-081-T02: the report's producing script (ALL: 2/2 satisfied)
[OK] artifact present: reports/golden_signals.json
[OK] producing code: scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[PASS] REQ-081-T03: golden-signals report reports/golden_signals.json (ALL: 7/7 satisfied)
[OK] latency for the thinking span type: present in reports/golden_signals.json
[OK] latency for the acting span type: present in reports/golden_signals.json
[OK] latency for the tool span type: present in reports/golden_signals.json
[OK] tokens in/out: present in reports/golden_signals.json
[OK] cost estimate: present in reports/golden_signals.json
[OK] accuracy from the eval: present in reports/golden_signals.json
[OK] hallucination rate from the eval: present in reports/golden_signals.json
```

### REQ-082 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.3 Performance & Cost Governance — table row "Cost/latency dashboard"

**Requirement:**

~~~text
Cost/latency dashboard | reports/dashboard.png + reports/dashboard_data.csv | Phoenix latency/cost/token dashboard screenshot AND the underlying data file it was drawn from
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-082-T01, REQ-082-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-082-T01: cost/latency dashboard screenshot AND its underlying data file (ALL: 2/2 satisfied)
[OK] reports/dashboard.png: valid PNG, 206181 bytes
[OK] reports/dashboard_data.csv: 35 data row(s), header='group,metric,value,target,unit,source'
[PASS] REQ-082-T02: the dashboard data export (ALL: 2/2 satisfied)
[OK] artifact present: reports/dashboard_data.csv
[OK] producing code: scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
```

### REQ-083 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 7.4 Security & Guardrails — table row "Guardrail code"

**Requirement:**

~~~text
Guardrail code | src/guardrails/ | input/output guardrails wired into the agent's I/O path (blocks/sanitizes)
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-083-T01, REQ-083-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-083-T01: Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[PASS] REQ-083-T02: input/output guardrails wired into the I/O path (ALL: 5/5 satisfied)
[OK] guardrail package src/guardrails with 4 module(s)
[OK] input guardrail: src/guardrails/sanitize.py
[OK] output guardrail: src/guardrails/__init__.py
[OK] blocks or sanitizes: src/guardrails/__init__.py
[OK] wired into the I/O path: eval/agent/dataset.py references the guardrail layer
```

### REQ-084 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 7.4 Security & Guardrails — table row "Audit trail"

**Requirement:**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-084-T01, REQ-084-T02, REQ-084-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-084-T01: File present: logs/agent_actions.jsonl (exact path); size=536468 bytes
[PASS] REQ-084-T02: machine-generated audit trail (ALL: 7/7 satisfied)
[OK] logs/agent_actions.jsonl: 831 audit record(s)
[OK] field 'actor' present
[OK] field 'action' present
[OK] field 'tool' present
[OK] field 'decision' present
[OK] field 'timestamp' present
[OK] audit middleware writes it: scripts/verify_evidence_citations.py
[PASS] REQ-084-T03: audit middleware invoked on agent actions across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/verify_evidence_citations.py:217: claim="the undated application is refused as an audited outcome",
```

### REQ-085 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 7.4 Security & Guardrails — table row "Secrets hygiene"

**Requirement:**

~~~text
Secrets hygiene | .env.example, .gitignore | env-var config; .gitignore covers .env; no secrets committed anywhere
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-085-T01, REQ-085-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-085-T01: secrets hygiene (ALL: 3/3 satisfied)
[OK] .gitignore ignores .env: '.env'
[OK] .env.example present as the committed env-var template
[OK] no .env file is committed
[PASS] REQ-085-T02: No committed secret matched 6 credential patterns across 1734 scanned files.
```

### REQ-086 - FAIL (67/100)

**Class:** IMPLEMENTATION  |  **Category:** risk  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Risk register"

**Requirement:**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-086-T01, REQ-086-T02, REQ-086-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-086-T03.

**Evidence:**

```
[PASS] REQ-086-T01: File present: docs/risk-register.md (exact path); size=24231 bytes
[PASS] REQ-086-T02: risk register columns at docs/risk-register.md (ALL: 7/7 satisfied)
[OK] risk: docs/risk-register.md:1: Risk
[OK] category (OWASP/NIST): docs/risk-register.md:8: OWASP
[OK] likelihood: docs/risk-register.md:10: Likelihood
[OK] impact: docs/risk-register.md:10: impact
[OK] mitigation: docs/risk-register.md:10: mitigat
[OK] residual risk: docs/risk-register.md:10: Residual
[OK] owner: docs/risk-register.md:22: Owner
[FAIL] REQ-086-T03: 4 unresolvable citation(s) across 105 document(s) (treated as missing per the Citation-Resolves Rule):
docs/rag/REQUIREMENTS_MAPPING.md cites 'assets/phoenix-traces.png' -> present but uncommitted
docs/rag/REQUIREMENTS_MAPPING.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
README.md cites 'docs/assets/phoenix-traces.png' -> present but uncommitted
README.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
```

### REQ-087 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Model / system card"

**Requirement:**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-087-T01, REQ-087-T02, REQ-087-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-087-T01: File present: docs/model-card.md (exact path); size=25500 bytes
[PASS] REQ-087-T02: model card contents at docs/model-card.md (ALL: 6/6 satisfied)
[OK] model (Gemini): docs/model-card.md:17: Gemini
[OK] data (synthetic): docs/model-card.md:5: synthetic
[OK] intended use: docs/model-card.md:85: Intended use
[OK] limitations: docs/model-card.md:210: Limitation
[OK] known failure modes: docs/model-card.md:241: failure mode
[OK] out-of-scope: docs/model-card.md:91: Out of scope
[PASS] REQ-087-T03: citation of failure-analysis.md in docs/model-card.md (exact path) (ALL: 1/1 satisfied)
[OK] docs/model-card.md:243: Twenty real failures found while building this, each with evidence, root cause, fix and before/after measurement, in **[`docs/failure-analysis.md`](failure-analysis.md)**. The ones that bear on trusting the output:
```

### REQ-088 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Compliance mapping"

**Requirement:**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-088-T01, REQ-088-T02, REQ-088-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-088-T03.

**Evidence:**

```
[PASS] REQ-088-T01: File present: docs/compliance.md (exact path); size=13627 bytes
[PASS] REQ-088-T02: compliance frameworks at docs/compliance.md (ALL: 3/3 satisfied)
[OK] EU AI Act: docs/compliance.md:11: EU AI Act
[OK] NIST AI RMF: docs/compliance.md:30: NIST AI RMF
[OK] DPDP: docs/compliance.md:52: DPDP
[FAIL] REQ-088-T03: obligation -> how addressed -> evidence artifact (ALL: 1/2 satisfied)
[OK] compliance mapping columns at docs/compliance.md (ALL: 2/2 satisfied)
[OK] how addressed: docs/compliance.md:17: mitigation
[OK] evidence artifact: docs/compliance.md:3: evidence
[NOT FOUND] 4 unresolvable citation(s) across 105 document(s) (treated as missing per the Citation-Resolves Rule):
docs/rag/REQUIREMENTS_MAPPING.md cites 'assets/phoenix-traces.png' -> present but uncommitted
docs/rag/REQUIREMENTS_MAPPING.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
README.md cites 'docs/assets/phoenix-traces.png' -> present but uncommitted
README.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
```

### REQ-089 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** risk  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Output-risk classification"

**Requirement:**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-089-T01, REQ-089-T02, REQ-089-T03, REQ-089-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-089-T01: File present: docs/output-risk.md (exact path); size=12473 bytes
[PASS] REQ-089-T02: output-risk tiers at docs/output-risk.md (ALL: 3/3 satisfied)
[OK] low tier: docs/output-risk.md:15: Low
[OK] medium tier: docs/output-risk.md:16: Medium
[OK] high tier: docs/output-risk.md:17: High
[PASS] REQ-089-T03: high-risk gating at docs/output-risk.md (ALL: 2/2 satisfied)
[OK] high-risk gating: docs/output-risk.md:5: gate
[OK] human-in-loop or refusal: docs/output-risk.md:42: refus
[PASS] REQ-089-T04: output-risk sample at docs/output-risk.md (ALL: 1/1 satisfied)
[OK] a sample: docs/output-risk.md:5: sample
```

### REQ-090 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Evaluation report"

**Requirement:**

~~~text
Evaluation report | reports/eval_report.json + harness | DeepEval (or equiv) over a golden set: hallucination + faithfulness/relevance; LLM-as-judge
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-090-T01, REQ-090-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-090-T01: File present: reports/eval_report.json (exact path); size=10334 bytes
[PASS] REQ-090-T02: agent evaluation report (ALL: 6/6 satisfied)
[OK] hallucination metric: present in reports/eval_report.json
[OK] faithfulness metric: present in reports/eval_report.json
[OK] answer-relevance metric: present in reports/eval_report.json
[OK] a golden set of cases: present in reports/eval_report.json
[OK] evaluation harness: eval/agent/run_agent_eval.py
[OK] the harness uses DeepEval (or an equivalent LLM-as-judge)
```

### REQ-091 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Routing-logic test"

**Requirement:**

~~~text
Routing-logic test | tests/test_routing.py | asserts conditional edges route the right worker for given states
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-091-T01, REQ-091-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-091-T01: File present: tests/test_routing.py (exact path); size=15913 bytes
[PASS] REQ-091-T02: routing-logic assertions at tests/test_routing.py (ALL: 4/4 satisfied)
[OK] tests/test_routing.py defines 22 test function(s): ['test_each_supervisor_route_has_its_own_target', 'test_an_unrecognized_route_asks_rather_than_guesses', 'test_a_halted_run_goes_to_a_human_whatever_it_was_routed_to', 'test_an_unresolved_product_routes_to_human_review', 'test_a_resolved_product_routes_to_its_own_retrieval_node', 'test_retrieval_with_no_evidence_routes_to_human_review', 'test_retrieval_with_evidence_routes_to_its_own_eligibility_node', 'test_a_policy_question_skips_the_assessment_nodes']
[OK] tests/test_routing.py contains assertions
[OK] the routing subject: matched 'Rout'
[OK] a given state: matched 'state'
```

### REQ-092 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Loop/cascade guard"

**Requirement:**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-092-T01, REQ-092-T02, REQ-092-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-092-T01: File present: tests/test_loops.py (exact path); size=8870 bytes
[PASS] REQ-092-T02: loop/cascade guard assertions at tests/test_loops.py (ALL: 4/4 satisfied)
[OK] tests/test_loops.py defines 10 test function(s): ['test_a_fresh_run_has_budget', 'test_an_exhausted_run_is_detected', 'test_a_missing_budget_falls_back_to_the_default', 'test_the_budget_leaves_headroom_over_a_real_run', 'test_a_runaway_loop_is_stopped_by_the_step_budget', 'test_the_halt_reason_names_the_node_and_the_budget', 'test_the_recursion_limit_stops_a_loop_the_budget_cannot_see', 'test_the_real_graph_carries_the_recursion_limit']
[OK] tests/test_loops.py contains assertions
[OK] max-steps / recursion limit: matched 'max-step'
[OK] stopping a runaway loop: matched 'limit'
[PASS] REQ-092-T03: a configured step or recursion limit across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/build_golden_signals.py:524: "recursion_limit": 60,
```

### REQ-093 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Tool-contract test"

**Requirement:**

~~~text
Tool-contract test | tests/test_tool_contracts.py | asserts each tool's input/output schema + one error path
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-093-T01, REQ-093-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-093-T01: File present: tests/test_tool_contracts.py (exact path); size=8964 bytes
[PASS] REQ-093-T02: tool-contract assertions at tests/test_tool_contracts.py (ALL: 4/4 satisfied)
[OK] tests/test_tool_contracts.py defines 15 test function(s): ['test_the_input_schema_is_declared', 'test_the_input_schema_rejects_an_unknown_field', 'test_the_input_schema_requires_a_query', 'test_the_output_schema_is_typed', 'test_the_output_shape_matches_the_contract', 'test_an_unresolvable_product_is_a_status_not_an_exception', 'test_no_applicable_policy_is_distinguishable_from_an_empty_answer', 'test_an_unknown_product_domain_raises_with_a_usable_message']
[OK] tests/test_tool_contracts.py contains assertions
[OK] input/output schema: matched 'contract'
[OK] one error path: matched 'error'
```

### REQ-094 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 7.7 Engineering & Delivery — table row "Local-run runbook"

**Requirement:**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-094-T01, REQ-094-T02, REQ-094-T03, REQ-094-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-094-T01: File present: README.md (exact path); size=20794 bytes
[PASS] REQ-094-T02: single documented command plus a regeneration command (ALL: 3/3 satisfied)
[OK] single documented run command: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[OK] second documented command regenerates traces: 'python scripts/export_traces.py'
[OK] documented command regenerates the evaluation: 'python -m eval.agent.run_agent_eval --no-judge'
[PASS] REQ-094-T03: runbook sample inputs: 7 committed input file(s): data/policy_corpus/corpus_registry.json, data/policy_corpus/README.md, data/vectorstore/index_integrity.json, data/vectorstore/index_manifest.json, data/vectorstore/lexical/bm25_education.json, data/vectorstore/lexical/bm25_mortgage.json, data/vectorstore/README.md
[PASS] REQ-094-T04: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in eval/agent/run_agent_eval.py
[OK] CLI invocation documented: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
```

### REQ-095 - PASS (100/100)

**Class:** OPTIONAL  |  **Category:** functional  |  **Source:** Section 7.7 Engineering & Delivery — table row "Bonus"

**Requirement:**

~~~text
Bonus | src/api/ (FastAPI streaming) | OPTIONAL: async FastAPI streaming endpoint — extra credit, not required
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-095-T01, REQ-095-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-095-T01: FastAPI streaming endpoint (OPTIONAL, not required): not present at or near 'src/api'. The source text marks this surface optional / bonus and explicitly not required, so its absence satisfies the interface requirement.
[PASS] REQ-095-T02: async FastAPI streaming endpoint, or the surface is absent (ANY: 1/2 satisfied)
[NOT FOUND] async FastAPI streaming endpoint (ALL: 1/3 satisfied)
[NOT FOUND] No directory at or near 'src/api' under E:\Virtusa Projects\CredPilot
[OK] fastapi declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:33: fastapi==0.141.1
[NOT FOUND] Cannot check 'async streaming endpoint': no directory at or near 'src/api'
[OK] FastAPI streaming endpoint (OPTIONAL, not required): not present at or near 'src/api'. The source text marks this surface optional / bonus and explicitly not required, so its absence satisfies the interface requirement.
```

### REQ-096 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 1

**Requirement:**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-096-T01, REQ-096-T02, REQ-096-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-096-T01: producing code for 7 present evidence artifact(s) (ALL: 7/7 satisfied)
[OK] logs/tool_calls.jsonl <- produced by scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[OK] logs/agent_actions.jsonl <- produced by scripts/verify_evidence_citations.py:216: artifact="logs/agent_actions.jsonl",
[OK] logs/mcp_transcript.jsonl <- produced by mcp_server/server.py:122: The transcript at ``logs/mcp_transcript.jsonl`` is written from here, which
[OK] reports/golden_signals.json <- produced by scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[OK] reports/dashboard_data.csv <- produced by scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
[OK] reports/eval_report.json <- produced by eval/agent/run_agent_eval.py:72: REPORT_PATH = REPORTS / "eval_report.json"
[OK] logs/memory_test.log <- produced by src/memory/__init__.py:3: *"src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log |
[PASS] REQ-096-T02: All 24 present named artifact(s) are committed: src/graph.py, logs/mcp_transcript.jsonl, tests/test_memory_persistence.py, logs/memory_test.log, src/tools/rag_tool.py, src/observability/tracing.py, traces/phoenix_spans.jsonl, logs/tool_calls.jsonl, docs/failure-analysis.md, reports/golden_signals.json, reports/dashboard.png, reports/dashboard_data.csv, logs/agent_actions.jsonl, .env.example, .gitignore, docs/risk-register.md, docs/model-card.md, docs/compliance.md, docs/output-risk.md, reports/eval_report.json, tests/test_routing.py, tests/test_loops.py, tests/test_tool_contracts.py, README.md
[PASS] REQ-096-T03: artifacts in their stated formats (ALL: 8/8 satisfied)
[OK] Phoenix trace export as Parquet or JSONL of OTel spans (ANY: 1/2 satisfied)
[NOT FOUND] No artifact at or near 'traces/phoenix_spans.parquet'
[OK] JSONL trace export at traces/phoenix_spans.jsonl (exact path) (ALL: 2/2 satisfied)
[OK] traces/phoenix_spans.jsonl parsed: 1119 JSON object(s)
[OK] record count 1119 >= 1
[OK] tool-invocation log as JSONL at logs/tool_calls.jsonl (exact path) (ALL: 2/2 satisfied)
[OK] logs/tool_calls.jsonl parsed: 430 JSON object(s)
[OK] record count 430 >= 1
[OK] File present: docs/failure-analysis.md (exact path); size=56777 bytes
[OK] golden-signals report as JSON in reports/golden_signals.json (exact path) (ALL: 1/1 satisfied)
[OK] reports/golden_signals.json:1: {
[OK] dashboard as PNG at reports/dashboard.png (exact path) (ALL: 2/2 satisfied)
[OK] reports/dashboard.png size=206181 bytes (>= 1)
[OK] file signature b'\x89PNG\r\n\x1a\n' matches expected b'\x89PNG\r\n\x1a\n'
[OK] dashboard data as CSV: reports/dashboard_data.csv (exact path) header=['group', 'metric', 'value', 'target', 'unit', 'source'] with 35 data rows
[OK] audit trail as JSONL at logs/agent_actions.jsonl (exact path) (ALL: 2/2 satisfied)
[OK] logs/agent_actions.jsonl parsed: 831 JSON object(s)
[OK] record count 831 >= 1
[OK] evaluation report as JSON in reports/eval_report.json (exact path) (ALL: 1/1 satisfied)
[OK] reports/eval_report.json:1: {
```

### REQ-097 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 2

**Requirement:**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-097-T01, REQ-097-T02, REQ-097-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-097-T01: observability as generated files (ALL: 2/2 satisfied)
[OK] a trace export (ANY: 1/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[OK] File present: traces/phoenix_spans.jsonl (exact path); size=501494 bytes
[OK] generated tool-invocation log (ALL: 2/2 satisfied)
[OK] artifact present: logs/tool_calls.jsonl
[OK] producing code: scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[PASS] REQ-097-T02: cost governance as generated files (ALL: 2/2 satisfied)
[OK] generated golden-signals report (ALL: 2/2 satisfied)
[OK] artifact present: reports/golden_signals.json
[OK] producing code: scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[OK] generated dashboard data (ALL: 2/2 satisfied)
[OK] artifact present: reports/dashboard_data.csv
[OK] producing code: scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
[PASS] REQ-097-T03: slide decks substituted for generated evidence: no file matches ['*.pptx', '*.ppt', '*.key', '*.odp'] across 1862 files
```

### REQ-098 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 3

**Requirement:**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-098-T01, REQ-098-T02, REQ-098-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-098-T01: arize-phoenix and openinference-instrumentation-langchain (ALL: 2/2 satisfied)
[OK] arize-phoenix declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:53: arize-phoenix==11.38.0
[OK] openinference-instrumentation-langchain declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:56: openinference-instrumentation-langchain==0.1.76
[PASS] REQ-098-T02: the local Phoenix UI endpoint across implementation tree (254 files) (ALL: 1/1 satisfied)
[OK] docs/rag/RUNBOOK.md:394: python -m phoenix.server.main serve       # terminal 1, UI on http://localhost:6006
[PASS] REQ-098-T03: Phoenix as the single evidence source (ALL: 2/2 satisfied)
[OK] golden signals derived from Phoenix spans (ALL: 2/2 satisfied)
[OK] artifact present: reports/golden_signals.json
[OK] producing code: scripts/build_golden_signals.py:112: frame = client.get_spans_dataframe(project_name="credpilot")
[OK] dashboard data derived from Phoenix spans (ALL: 2/2 satisfied)
[OK] artifact present: reports/dashboard_data.csv
[OK] producing code: scripts/build_golden_signals.py:112: frame = client.get_spans_dataframe(project_name="credpilot")
```

### REQ-099 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Phoenix trace export"

**Requirement:**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-099-T01, REQ-099-T02, REQ-099-T03, REQ-099-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-099-T01: Parquet or JSONL of OTel spans (ANY: 1/2 satisfied)
[NOT FOUND] No artifact at or near 'traces/phoenix_spans.parquet'
[OK] JSONL span export at traces/phoenix_spans.jsonl (exact path) (ALL: 2/2 satisfied)
[OK] traces/phoenix_spans.jsonl parsed: 1119 JSON object(s)
[OK] record count 1119 >= 1
[PASS] REQ-099-T02: openinference-instrumentation-langchain tracing (ALL: 2/2 satisfied)
[OK] openinference-instrumentation-langchain declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:56: openinference-instrumentation-langchain==0.1.76
[OK] openinference instrumentation activated across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/observability/tracing.py:149: """Wire the Phoenix/OpenInference tracer into this process.
[PASS] REQ-099-T03: the stated export method (ALL: 2/2 satisfied)
[OK] px.Client().get_spans_dataframe() across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/build_golden_signals.py:112: frame = client.get_spans_dataframe(project_name="credpilot")
[OK] the span dataframe exported to file across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/build_golden_signals.py:113: return json.loads(frame.to_json(orient="records"))
[PASS] REQ-099-T04: trace export traces/phoenix_spans.jsonl (ALL: 3/3 satisfied)
[OK] 1119 span(s) exported from at least one full run
[OK] spans span multiple components: ['agent.education', 'agent.eligibility', 'agent.final_response', 'agent.human_review', 'agent.mortgage', 'agent.recommendation', 'agent.risk', 'bm25.search', 'chroma.search', 'citation.validate', 'domain.resolve', 'embedding.query']
[OK] latency evidence present via key(s) ['latency_ms', 'start_time', 'end_time']
```

### REQ-100 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Tool-invocation log"

**Requirement:**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-100-T01, REQ-100-T02, REQ-100-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-100-T01: one JSON object per tool call at logs/tool_calls.jsonl (exact path) (ALL: 2/2 satisfied)
[OK] logs/tool_calls.jsonl parsed: 430 JSON object(s)
[OK] record count 430 >= 1
[PASS] REQ-100-T02: tool-invocation log per-call fields (ALL: 8/8 satisfied)
[OK] logs/tool_calls.jsonl: 430 tool-call record(s)
[OK] field 'timestamp' present as ['timestamp']
[OK] field 'agent/node' present as ['agent']
[OK] field 'tool_name' present as ['tool_name']
[OK] field 'args' present as ['args']
[OK] field 'result' present as ['result']
[OK] field 'latency_ms' present as ['latency_ms']
[OK] field 'status' present as ['status']
[PASS] REQ-100-T03: a logging wrapper/decorator (ALL: 2/2 satisfied)
[OK] a logging wrapper or decorator across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] mcp_server/server.py:111: @functools.wraps(fn)
[OK] appending to logs/tool_calls.jsonl across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
```

### REQ-101 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Failure-mode analysis"

**Requirement:**

~~~text
Failure-mode analysis | Markdown | Open your Phoenix traces, pick ≥ 3 real failures, write each up citing its run_id + span_id, with root cause and the fix.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-101-T01, REQ-101-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-101-T01: Markdown failure-mode analysis (ALL: 2/2 satisfied)
[OK] File present: docs/failure-analysis.md (exact path); size=56777 bytes
[OK] git ls-files lists 'docs/failure-analysis.md' -> artifact is committed
[PASS] REQ-101-T02: failure-mode analysis docs/failure-analysis.md (ALL: 5/5 satisfied)
[OK] 106 documented failure section(s) (>= 3)
[OK] 1 distinct run_id and 1 distinct span_id citation(s)
[OK] 3 failure(s) carry an evidence citation (>= 3)
[OK] 21 root-cause statement(s)
[OK] 29 fix statement(s)
```

### REQ-102 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Golden-signals report"

**Requirement:**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-102-T01, REQ-102-T02, REQ-102-T03, REQ-102-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-102-T01: valid JSON report in reports/golden_signals.json (exact path) (ALL: 1/1 satisfied)
[OK] reports/golden_signals.json:1: {
[PASS] REQ-102-T02: golden-signals derivation (ALL: 5/5 satisfied)
[OK] p50 latency present
[OK] p95 latency present
[OK] producing script: scripts/build_golden_signals.py
[OK] the producing script reads the Phoenix spans via get_spans_dataframe()
[OK] cost is computed from tokens and a price
[PASS] REQ-102-T03: golden-signals report reports/golden_signals.json (ALL: 7/7 satisfied)
[OK] latency for the thinking span type: present in reports/golden_signals.json
[OK] latency for the acting span type: present in reports/golden_signals.json
[OK] latency for the tool span type: present in reports/golden_signals.json
[OK] tokens in/out: present in reports/golden_signals.json
[OK] cost estimate: present in reports/golden_signals.json
[OK] accuracy from the eval: present in reports/golden_signals.json
[OK] hallucination rate from the eval: present in reports/golden_signals.json
[PASS] REQ-102-T04: accuracy and hallucination imported from the eval report (ALL: 2/2 satisfied)
[OK] golden-signals report reports/golden_signals.json (ALL: 7/7 satisfied)
[OK] latency for the thinking span type: present in reports/golden_signals.json
[OK] latency for the acting span type: present in reports/golden_signals.json
[OK] latency for the tool span type: present in reports/golden_signals.json
[OK] tokens in/out: present in reports/golden_signals.json
[OK] cost estimate: present in reports/golden_signals.json
[OK] accuracy from the eval: present in reports/golden_signals.json
[OK] hallucination rate from the eval: present in reports/golden_signals.json
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
```

### REQ-103 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Cost/latency dashboard"

**Requirement:**

~~~text
Cost/latency dashboard | PNG + CSV | Phoenix UI (localhost:6006) shows latency / cost / token dashboards — screenshot one; export the data with get_spans_dataframe().to_csv('reports/dashboard_data.csv').
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-103-T01, REQ-103-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-103-T01: cost/latency dashboard screenshot AND its underlying data file (ALL: 2/2 satisfied)
[OK] reports/dashboard.png: valid PNG, 206181 bytes
[OK] reports/dashboard_data.csv: 35 data row(s), header='group,metric,value,target,unit,source'
[PASS] REQ-103-T02: the stated CSV export method (ALL: 3/3 satisfied)
[OK] the Phoenix spans dataframe across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/build_golden_signals.py:112: frame = client.get_spans_dataframe(project_name="credpilot")
[OK] the to_csv export across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/build_golden_signals.py:629: frame.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
[OK] the dashboard data target path across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
```

### REQ-104 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 8. Producing the Evidence — table row "Guardrail code"

**Requirement:**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-104-T01, REQ-104-T02, REQ-104-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-104-T01: guardrail Python module (ALL: 2/2 satisfied)
[OK] Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[OK] Python definitions in the guardrail module across 'src/guardrails' (4 files) (ALL: 1/1 satisfied)
[OK] src/guardrails/redaction.py:134: def _presidio_analyzer():
[PASS] REQ-104-T02: validators or policy functions wrapping input and output (ALL: 2/2 satisfied)
[OK] Guardrails-AI, LLM Guard, or policy functions (ANY: 1/3 satisfied)
[NOT FOUND] guardrails-ai declared (dependency manifests) (ALL: 0/1 satisfied)
[NOT FOUND] 'guardrails-ai' not declared in any of: requirements.txt, pyproject.toml
[NOT FOUND] llm-guard declared (dependency manifests) (ALL: 0/1 satisfied)
[NOT FOUND] 'llm-guard' not declared in any of: requirements.txt, pyproject.toml
[OK] policy/validator functions across 'src/guardrails' (4 files) (ALL: 1/1 satisfied)
[OK] src/guardrails/validation.py:45: def validate_response(
[OK] input/output guardrails wired into the I/O path (ALL: 5/5 satisfied)
[OK] guardrail package src/guardrails with 4 module(s)
[OK] input guardrail: src/guardrails/sanitize.py
[OK] output guardrail: src/guardrails/__init__.py
[OK] blocks or sanitizes: src/guardrails/__init__.py
[OK] wired into the I/O path: eval/agent/dataset.py references the guardrail layer
[PASS] REQ-104-T03: wired into the graph's I/O nodes (ALL: 2/2 satisfied)
[OK] input/output guardrails wired into the I/O path (ALL: 5/5 satisfied)
[OK] guardrail package src/guardrails with 4 module(s)
[OK] input guardrail: src/guardrails/sanitize.py
[OK] output guardrail: src/guardrails/__init__.py
[OK] blocks or sanitizes: src/guardrails/__init__.py
[OK] wired into the I/O path: eval/agent/dataset.py references the guardrail layer
[OK] the graph referencing the guardrail layer across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] eval/agent/dataset.py:342: "SEC-INJ": "src/guardrails/ + input_guardrails_node — injection detection and quarantine",
```

### REQ-105 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 8. Producing the Evidence — table row "Audit trail"

**Requirement:**

~~~text
Audit trail | JSONL | Audit middleware that appends {actor, action, tool, decision, timestamp} for each consequential action to logs/agent_actions.jsonl.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-105-T01, REQ-105-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-105-T01: audit trail as JSONL at logs/agent_actions.jsonl (exact path) (ALL: 2/2 satisfied)
[OK] logs/agent_actions.jsonl parsed: 831 JSON object(s)
[OK] record count 831 >= 1
[PASS] REQ-105-T02: machine-generated audit trail (ALL: 7/7 satisfied)
[OK] logs/agent_actions.jsonl: 831 audit record(s)
[OK] field 'actor' present
[OK] field 'action' present
[OK] field 'tool' present
[OK] field 'decision' present
[OK] field 'timestamp' present
[OK] audit middleware writes it: scripts/verify_evidence_citations.py
```

### REQ-106 - FAIL (40/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 8. Producing the Evidence — table row "Governance pack" (continuation table)

**Requirement:**

~~~text
Governance pack | Markdown | risk-register.md, model-card.md, compliance.md, output-risk.md — each entry cites the committed control/artifact it refers to.
~~~

**Status:** FAIL  
**Fit Score:** 40  
**Tests:** REQ-106-T01, REQ-106-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-106-T02.

**Evidence:**

```
[PASS] REQ-106-T01: the four governance Markdown documents (ALL: 4/4 satisfied)
[OK] File present: docs/risk-register.md (exact path); size=24231 bytes
[OK] File present: docs/model-card.md (exact path); size=25500 bytes
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[OK] File present: docs/output-risk.md (exact path); size=12473 bytes
[FAIL] REQ-106-T02: 4 unresolvable citation(s) across 105 document(s) (treated as missing per the Citation-Resolves Rule):
docs/rag/REQUIREMENTS_MAPPING.md cites 'assets/phoenix-traces.png' -> present but uncommitted
docs/rag/REQUIREMENTS_MAPPING.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
README.md cites 'docs/assets/phoenix-traces.png' -> present but uncommitted
README.md cites 'scripts/capture_phoenix_screenshot.py' -> present but uncommitted
```

### REQ-107 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 8. Producing the Evidence — table row "Evaluation report" (continuation table)

**Requirement:**

~~~text
Evaluation report | JSON | A DeepEval run over your golden set (hallucination, faithfulness, answer-relevance) that writes reports/eval_report.json, plus the harness.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-107-T01, REQ-107-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-107-T01: valid JSON evaluation report in reports/eval_report.json (exact path) (ALL: 1/1 satisfied)
[OK] reports/eval_report.json:1: {
[PASS] REQ-107-T02: agent evaluation report (ALL: 6/6 satisfied)
[OK] hallucination metric: present in reports/eval_report.json
[OK] faithfulness metric: present in reports/eval_report.json
[OK] answer-relevance metric: present in reports/eval_report.json
[OK] a golden set of cases: present in reports/eval_report.json
[OK] evaluation harness: eval/agent/run_agent_eval.py
[OK] the harness uses DeepEval (or an equivalent LLM-as-judge)
```

### REQ-108 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 8. Producing the Evidence — table row "Agent tests" (continuation table)

**Requirement:**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-108-T01, REQ-108-T02, REQ-108-T03, REQ-108-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-108-T01: the three pytest files (ALL: 3/3 satisfied)
[OK] File present: tests/test_routing.py (exact path); size=15913 bytes
[OK] File present: tests/test_loops.py (exact path); size=8870 bytes
[OK] File present: tests/test_tool_contracts.py (exact path); size=8964 bytes
[PASS] REQ-108-T02: routing test at tests/test_routing.py (ALL: 3/3 satisfied)
[OK] tests/test_routing.py defines 22 test function(s): ['test_each_supervisor_route_has_its_own_target', 'test_an_unrecognized_route_asks_rather_than_guesses', 'test_a_halted_run_goes_to_a_human_whatever_it_was_routed_to', 'test_an_unresolved_product_routes_to_human_review', 'test_a_resolved_product_routes_to_its_own_retrieval_node', 'test_retrieval_with_no_evidence_routes_to_human_review', 'test_retrieval_with_evidence_routes_to_its_own_eligibility_node', 'test_a_policy_question_skips_the_assessment_nodes']
[OK] tests/test_routing.py contains assertions
[OK] routing subject: matched 'Rout'
[PASS] REQ-108-T03: loops test at tests/test_loops.py (ALL: 3/3 satisfied)
[OK] tests/test_loops.py defines 10 test function(s): ['test_a_fresh_run_has_budget', 'test_an_exhausted_run_is_detected', 'test_a_missing_budget_falls_back_to_the_default', 'test_the_budget_leaves_headroom_over_a_real_run', 'test_a_runaway_loop_is_stopped_by_the_step_budget', 'test_the_halt_reason_names_the_node_and_the_budget', 'test_the_recursion_limit_stops_a_loop_the_budget_cannot_see', 'test_the_real_graph_carries_the_recursion_limit']
[OK] tests/test_loops.py contains assertions
[OK] recursion/step limit subject: matched 'step'
[PASS] REQ-108-T04: tool-contract test at tests/test_tool_contracts.py (ALL: 4/4 satisfied)
[OK] tests/test_tool_contracts.py defines 15 test function(s): ['test_the_input_schema_is_declared', 'test_the_input_schema_rejects_an_unknown_field', 'test_the_input_schema_requires_a_query', 'test_the_output_schema_is_typed', 'test_the_output_shape_matches_the_contract', 'test_an_unresolvable_product_is_a_status_not_an_exception', 'test_no_applicable_policy_is_distinguishable_from_an_empty_answer', 'test_an_unknown_product_domain_raises_with_a_usable_message']
[OK] tests/test_tool_contracts.py contains assertions
[OK] I/O schema: matched 'contract'
[OK] error path: matched 'error'
```

### REQ-109 - FAIL (50/100)

**Class:** OPTIONAL  |  **Category:** functional  |  **Source:** Section 8.1 Good-to-Have — bullet 1

**Requirement:**

~~~text
FastAPI streaming endpoint; a demonstrated local run (screenshot/log).
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-109-T01, REQ-109-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-109-T01.

**Evidence:**

```
[FAIL] REQ-109-T01: FastAPI streaming endpoint (ALL: 1/3 satisfied)
[NOT FOUND] No directory at or near 'src/api' under E:\Virtusa Projects\CredPilot
[OK] fastapi declared (dependency manifests) (ALL: 1/1 satisfied)
[OK] requirements.txt:33: fastapi==0.141.1
[NOT FOUND] Cannot check 'an async streaming endpoint': no directory at or near 'src/api'
[PASS] REQ-109-T02: a demonstrated local run (ANY: 1/2 satisfied)
[OK] a committed run log of the streaming endpoint across implementation tree (1265 files) (ALL: 1/1 satisfied)
[OK] docs/rag/ARCHITECTURE.md:291: | [`src/web/`](../../src/web/) | FastAPI + one static page over the same compiled graph |
[NOT FOUND] No file at or near 'docs/api-run.png' under E:\Virtusa Projects\CredPilot
```

### REQ-110 - FAIL (67/100)

**Class:** OPTIONAL  |  **Category:** security  |  **Source:** Section 8.1 Good-to-Have — bullet 2

**Requirement:**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-110-T01, REQ-110-T02, REQ-110-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-110-T01.

**Evidence:**

```
[FAIL] REQ-110-T01: Presidio PII-redaction middleware (ALL: 2/3 satisfied)
[OK] presidio declared (dependency manifests) (ANY: 2/3 satisfied)
[OK] requirements.txt:61: presidio-analyzer==2.2.361
[NOT FOUND] 'presidio_analyzer' not declared in any of: requirements.txt, pyproject.toml
[OK] requirements.txt:61: presidio-analyzer==2.2.361
[OK] Presidio used in the redaction path across implementation tree (147 files) (ALL: 1/1 satisfied)
[OK] src/guardrails/redaction.py:8: Deterministic regex redaction runs first and always. Microsoft Presidio, when
[NOT FOUND] PII masking and leak-free logs (ALL: 1/2 satisfied)
[OK] masking implemented at scripts/export_traces.py:246: redaction_is_warm(
[NOT FOUND] 1 sensitive value(s) written in plaintext:
traces/phoenix-live.jsonl:813 matches /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b/
[PASS] REQ-110-T02: a before/after redaction sample across implementation tree (1565 files) (ALL: 1/1 satisfied)
[OK] docs/failure-analysis.md:5: cause, a fix, and the measurement before and after.
[PASS] REQ-110-T03: red-team attack set and results (ALL: 2/2 satisfied)
[OK] a red-team attack set across implementation tree (606 files) (ALL: 1/1 satisfied)
[OK] docs/compliance.md:23: | **Art. 15** — Accuracy, robustness, cybersecurity | Appropriate accuracy; resilience to error and manipulation | Macro-averaged accuracy, citation validity and grounding measured over both products' golden sets by an evaluation that enters the graph at its real entry point, so Supervisor routing a
[OK] the attack results across implementation tree (459 files) (ALL: 1/1 satisfied)
[OK] data/vectorstore/index_integrity.json:9: "status": "PASS"
```

### REQ-111 - PASS (100/100)

**Class:** OPTIONAL  |  **Category:** observability  |  **Source:** Section 8.1 Good-to-Have — bullet 3

**Requirement:**

~~~text
An optimization note showing a measured before/after latency or cost improvement (two Phoenix-derived reports).
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-111-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-111-T01: optimization note backed by two Phoenix-derived reports (ALL: 3/3 satisfied)
[OK] the optimization note across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] docs/failure-analysis.md:5: cause, a fix, and the measurement before and after.
[OK] the measured dimension across implementation tree (105 files) (ALL: 1/1 satisfied)
[OK] docs/failure-analysis.md:27: old assumption that had always been true until then*: a latency cost that only
[OK] 2 Phoenix-derived report(s) available for a before/after comparison: reports/dashboard_data.csv, reports/golden_signals.json
```

### REQ-112 - FAIL (88/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 8.1 Good-to-Have — closing italic paragraph (final paragraph of the document)

**Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Status:** FAIL  
**Fit Score:** 88  
**Tests:** REQ-112-T01, REQ-112-T02, REQ-112-T03, REQ-112-T04, REQ-112-T05, REQ-112-T06  
**Reason:** 1 of 6 bound test(s) produced no satisfying evidence: REQ-112-T03.

**Evidence:**

```
[PASS] REQ-112-T01: observable lending decision (ALL: 2/2 satisfied)
[OK] a trace export (ANY: 1/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[OK] File present: traces/phoenix_spans.jsonl (exact path); size=501494 bytes
[OK] File present: logs/tool_calls.jsonl (exact path); size=422236 bytes
[PASS] REQ-112-T02: cost governance (ALL: 2/2 satisfied)
[OK] File present: reports/golden_signals.json (exact path); size=9605 bytes
[OK] File present: reports/dashboard_data.csv (exact path); size=1576 bytes
[FAIL] REQ-112-T03: security (ALL: 2/3 satisfied)
[OK] Directory present: src/guardrails (exact path); 5 entries: __init__.py, __pycache__, redaction.py, sanitize.py, validation.py
[OK] File present: .env.example (exact path); size=2595 bytes
[NOT FOUND] PII masking and leak-free logs (ALL: 1/2 satisfied)
[OK] masking implemented at scripts/export_traces.py:246: redaction_is_warm(
[NOT FOUND] 1 sensitive value(s) written in plaintext:
traces/phoenix-live.jsonl:813 matches /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b/
[PASS] REQ-112-T04: compliance (ALL: 4/4 satisfied)
[OK] File present: docs/compliance.md (exact path); size=13627 bytes
[OK] File present: docs/risk-register.md (exact path); size=24231 bytes
[OK] File present: docs/model-card.md (exact path); size=25500 bytes
[OK] File present: docs/output-risk.md (exact path); size=12473 bytes
[PASS] REQ-112-T05: continuous evaluation (ALL: 4/4 satisfied)
[OK] File present: reports/eval_report.json (exact path); size=10334 bytes
[OK] File present: tests/test_routing.py (exact path); size=15913 bytes
[OK] File present: tests/test_loops.py (exact path); size=8870 bytes
[OK] File present: tests/test_tool_contracts.py (exact path); size=8964 bytes
[PASS] REQ-112-T06: committed, regenerable evidence (ALL: 3/3 satisfied)
[OK] All 24 present named artifact(s) are committed: src/graph.py, logs/mcp_transcript.jsonl, tests/test_memory_persistence.py, logs/memory_test.log, src/tools/rag_tool.py, src/observability/tracing.py, traces/phoenix_spans.jsonl, logs/tool_calls.jsonl, docs/failure-analysis.md, reports/golden_signals.json, reports/dashboard.png, reports/dashboard_data.csv, logs/agent_actions.jsonl, .env.example, .gitignore, docs/risk-register.md, docs/model-card.md, docs/compliance.md, docs/output-risk.md, reports/eval_report.json, tests/test_routing.py, tests/test_loops.py, tests/test_tool_contracts.py, README.md
[OK] producing code for 7 present evidence artifact(s) (ALL: 7/7 satisfied)
[OK] logs/tool_calls.jsonl <- produced by scripts/verify_evidence_citations.py:209: artifact="logs/tool_calls.jsonl",
[OK] logs/agent_actions.jsonl <- produced by scripts/verify_evidence_citations.py:216: artifact="logs/agent_actions.jsonl",
[OK] logs/mcp_transcript.jsonl <- produced by mcp_server/server.py:122: The transcript at ``logs/mcp_transcript.jsonl`` is written from here, which
[OK] reports/golden_signals.json <- produced by scripts/build_golden_signals.py:1: """Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.
[OK] reports/dashboard_data.csv <- produced by scripts/build_dashboard.py:3: REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.
[OK] reports/eval_report.json <- produced by eval/agent/run_agent_eval.py:72: REPORT_PATH = REPORTS / "eval_report.json"
[OK] logs/memory_test.log <- produced by src/memory/__init__.py:3: *"src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log |
[OK] single documented command plus a regeneration command (ALL: 3/3 satisfied)
[OK] single documented run command: 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json' (from README.md (documented command))
[OK] second documented command regenerates traces: 'python scripts/export_traces.py'
[OK] documented command regenerates the evaluation: 'python -m eval.agent.run_agent_eval --no-judge'
```

---

## How to read this report

* **PASS** means the implementation provided sufficient verifiable evidence that the original requirement is satisfied.
* **FAIL** means it did not. Partial implementation stays FAIL even where the fit score is high.
* **Fit Score** is the weighted percentage of that requirement's tests that passed: 100 = fully satisfied with evidence; 75-99 = substantial but one or more explicit parts incomplete; 50-74 = partially implemented; 1-49 = minimal; 0 = absent.
* `UNSPECIFIED_BY_REQUIREMENT` in an evidence line means the source document fixes no value to test against. That is a specification gap recorded honestly, not an implementation defect, and no threshold was invented to fill it.

Do not edit the expectations in this suite to turn a FAIL into a PASS. The requirements define the expected behaviour; the implementation does not.

