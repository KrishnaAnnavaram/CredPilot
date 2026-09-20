<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot - Requirement Traceability Matrix

Generated: 2026-09-20T05:48:35Z  
Source document: `source_document/Loan_Origination_Underwriting_Copilot_Merged.docx`  
Requirements baseline: `source_requirements/requirements_verbatim.md`  
Baseline SHA-256: `ed25ccf4473d3cf17daad29d0db50f18276f4ed219aba55d8188e01214adf917`

## Summary

| Metric | Value |
| --- | --- |
| Total requirements | 112 |
| Total test cases | 320 |
| Requirements with >= 1 test | 112 |
| Requirements with no test | 0 |
| Source requirements coverage | 100.0% |

`Status` is `NOT_RUN` until `runners/run_all_tests.py` executes against an implementation. Running the suite rewrites `reports/latest_test_report.md` and `reports/latest_test_report.json`; this matrix records the mapping, not the outcome.

## Index

| Requirement | Class | Category | Source location | Tests | Verification |
| --- | --- | --- | --- | --- | --- |
| [REQ-001](#req-001) | ENGAGEMENT | governance | Document title block — banner line above the title (first line of the document) | 1 | DOCUMENTATION_TEST |
| [REQ-002](#req-002) | ENGAGEMENT | governance | Document title block — document title | 1 | DOCUMENTATION_TEST |
| [REQ-003](#req-003) | IMPLEMENTATION | governance | Document title block — subtitle line beneath the title | 8 | ARCHITECTURE_TEST, DOCUMENTATION_TEST, GOVERNANCE_TEST, INTEGRATION_TEST, OBSERVABILITY_TEST |
| [REQ-004](#req-004) | ENGAGEMENT | governance | Section 1. Project Identity — table row 1 | 1 | DOCUMENTATION_TEST |
| [REQ-005](#req-005) | ENGAGEMENT | governance | Section 1. Project Identity — table row 2 | 1 | DOCUMENTATION_TEST |
| [REQ-006](#req-006) | ENGAGEMENT | governance | Section 1. Project Identity — table row 3 | 1 | DOCUMENTATION_TEST |
| [REQ-007](#req-007) | ENGAGEMENT | governance | Section 1. Project Identity — table row 4 | 1 | DOCUMENTATION_TEST |
| [REQ-008](#req-008) | ENGAGEMENT | governance | Section 2. Engagement Overview — table row 1 | 1 | GOVERNANCE_TEST |
| [REQ-009](#req-009) | ENGAGEMENT | governance | Section 2. Engagement Overview — table row 2 | 1 | GOVERNANCE_TEST |
| [REQ-010](#req-010) | ENGAGEMENT | governance | Section 2. Engagement Overview — table row 3 | 2 | GOVERNANCE_TEST |
| [REQ-011](#req-011) | ENGAGEMENT | governance | Section 2. Engagement Overview — table row 4 | 3 | GOVERNANCE_TEST |
| [REQ-012](#req-012) | ENGAGEMENT | governance | Section 2. Engagement Overview — table row 5 | 1 | GOVERNANCE_TEST |
| [REQ-013](#req-013) | ENGAGEMENT | governance | Section 2. Engagement Overview — table row 6 | 1 | GOVERNANCE_TEST |
| [REQ-014](#req-014) | IMPLEMENTATION | governance | Section 2. Engagement Overview — paragraph "What is evaluated", sentence 1 | 10 | ARCHITECTURE_TEST, GOVERNANCE_TEST, INTEGRATION_TEST, OBSERVABILITY_TEST, SECURITY_TEST |
| [REQ-015](#req-015) | IMPLEMENTATION | auditability | Section 2. Engagement Overview — paragraph "What is evaluated", sentence 2 | 2 | AUDITABILITY_TEST |
| [REQ-016](#req-016) | ENGAGEMENT | governance | Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 1 | 1 | GOVERNANCE_TEST |
| [REQ-017](#req-017) | IMPLEMENTATION | non_functional | Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 2 | 1 | NEGATIVE_TEST |
| [REQ-018](#req-018) | ENGAGEMENT | underwriting | Section 3.1 Problem — sentence 1 | 1 | DOCUMENTATION_TEST |
| [REQ-019](#req-019) | ENGAGEMENT | policy | Section 3.1 Problem — sentence 2 | 1 | ARCHITECTURE_TEST |
| [REQ-020](#req-020) | IMPLEMENTATION | underwriting | Section 3.1 Problem — sentence 3 | 6 | AUDITABILITY_TEST, INTEGRATION_TEST, STATIC_TEST, WORKFLOW_TEST |
| [REQ-021](#req-021) | ENGAGEMENT | governance | Section 3.2 Your Role — sentence 1 | 1 | DOCUMENTATION_TEST |
| [REQ-022](#req-022) | IMPLEMENTATION | orchestration | Section 3.2 Your Role — sentence 2 | 7 | ARCHITECTURE_TEST, AUDITABILITY_TEST, GOVERNANCE_TEST, INTEGRATION_TEST, OBSERVABILITY_TEST, SECURITY_TEST |
| [REQ-023](#req-023) | IMPLEMENTATION | non_functional | Section 3.3 Expected Solution — lead-in sentence | 2 | ARCHITECTURE_TEST, AUDITABILITY_TEST |
| [REQ-024](#req-024) | IMPLEMENTATION | orchestration | Section 3.3 Expected Solution — bullet 1 | 6 | ARCHITECTURE_TEST, OUTPUT_VALIDATION_TEST |
| [REQ-025](#req-025) | IMPLEMENTATION | integration | Section 3.3 Expected Solution — bullet 2 | 7 | ARCHITECTURE_TEST, INTEGRATION_TEST, SECURITY_TEST |
| [REQ-026](#req-026) | IMPLEMENTATION | observability | Section 3.3 Expected Solution — bullet 3 | 3 | OBSERVABILITY_TEST |
| [REQ-027](#req-027) | IMPLEMENTATION | governance | Section 3.3 Expected Solution — bullet 4 | 6 | AUDITABILITY_TEST, GOVERNANCE_TEST, OBSERVABILITY_TEST, SECURITY_TEST |
| [REQ-028](#req-028) | IMPLEMENTATION | evaluation | Section 3.3 Expected Solution — bullet 5 | 5 | DOCUMENTATION_TEST, INTEGRATION_TEST |
| [REQ-029](#req-029) | IMPLEMENTATION | auditability | Section 3.4 Applicable Rules — bullet 1 (Evidence-in-Repo Rule) | 2 | AUDITABILITY_TEST |
| [REQ-030](#req-030) | IMPLEMENTATION | auditability | Section 3.4 Applicable Rules — bullet 2 (Citation-Resolves Rule) | 2 | AUDITABILITY_TEST |
| [REQ-031](#req-031) | IMPLEMENTATION | security | Section 3.4 Applicable Rules — bullet 3 (Synthetic-Data Rule) | 3 | DATA_VALIDATION_TEST, NEGATIVE_TEST, SECURITY_TEST |
| [REQ-032](#req-032) | IMPLEMENTATION | integration | Section 3.4 Applicable Rules — bullet 4 (Open-Source & Gemini-Only Rule) | 4 | CONFIGURATION_TEST, INTEGRATION_TEST, NEGATIVE_TEST |
| [REQ-033](#req-033) | IMPLEMENTATION | non_functional | Section 3.4 Applicable Rules — bullet 5 (Reproducibility Rule) | 2 | CONFIGURATION_TEST, DOCUMENTATION_TEST |
| [REQ-034](#req-034) | IMPLEMENTATION | integration | Section 4. Technology & Framework Stack — lead-in paragraph | 3 | CONFIGURATION_TEST, NEGATIVE_TEST |
| [REQ-035](#req-035) | IMPLEMENTATION | integration | Section 4. Technology & Framework Stack — table row "Language / Agent Framework" | 3 | CONFIGURATION_TEST, GOVERNANCE_TEST |
| [REQ-036](#req-036) | IMPLEMENTATION | integration | Section 4. Technology & Framework Stack — table row "LLM Provider" | 2 | INTEGRATION_TEST, NEGATIVE_TEST |
| [REQ-037](#req-037) | IMPLEMENTATION | integration | Section 4. Technology & Framework Stack — table row "Interoperability" | 2 | INTEGRATION_TEST |
| [REQ-038](#req-038) | IMPLEMENTATION | integration | Section 4. Technology & Framework Stack — table row "Memory" | 2 | INTEGRATION_TEST |
| [REQ-039](#req-039) | IMPLEMENTATION | policy | Section 4. Technology & Framework Stack — table row "Retrieval" | 2 | INTEGRATION_TEST |
| [REQ-040](#req-040) | IMPLEMENTATION | observability | Section 4. Technology & Framework Stack — table row "Observability (mandated)" | 3 | OBSERVABILITY_TEST |
| [REQ-041](#req-041) | IMPLEMENTATION | evaluation | Section 4. Technology & Framework Stack — table row "Evaluation" | 2 | CONFIGURATION_TEST, INTEGRATION_TEST |
| [REQ-042](#req-042) | IMPLEMENTATION | security | Section 4. Technology & Framework Stack — table row "Security" | 3 | SECURITY_TEST |
| [REQ-043](#req-043) | IMPLEMENTATION | functional | Section 4. Technology & Framework Stack — table row "Interface" (continuation table) | 2 | ARCHITECTURE_TEST, CONFIGURATION_TEST |
| [REQ-044](#req-044) | IMPLEMENTATION | eligibility | Section 5.1 Functional Acceptance Criteria — table row AC-01 | 4 | DATA_VALIDATION_TEST, INTEGRATION_TEST, OUTPUT_VALIDATION_TEST, RUNTIME_TEST |
| [REQ-045](#req-045) | IMPLEMENTATION | affordability | Section 5.1 Functional Acceptance Criteria — table row AC-02 | 4 | BOUNDARY_TEST, RUNTIME_TEST, STATIC_TEST |
| [REQ-046](#req-046) | IMPLEMENTATION | underwriting | Section 5.1 Functional Acceptance Criteria — table row AC-03 | 7 | BOUNDARY_TEST, OUTPUT_VALIDATION_TEST, RUNTIME_TEST, STATIC_TEST, WORKFLOW_TEST |
| [REQ-047](#req-047) | IMPLEMENTATION | workflow | Section 5.1 Functional Acceptance Criteria — table row AC-04 | 4 | STATIC_TEST, WORKFLOW_TEST |
| [REQ-048](#req-048) | IMPLEMENTATION | functional | Section 5.1 Functional Acceptance Criteria — table row AC-05 | 2 | INTEGRATION_TEST |
| [REQ-049](#req-049) | IMPLEMENTATION | security | Section 5.1 Functional Acceptance Criteria — table row AC-06 | 4 | NEGATIVE_TEST, SECURITY_TEST |
| [REQ-050](#req-050) | IMPLEMENTATION | observability | Section 5.1 Functional Acceptance Criteria — table row AC-07 | 3 | AUDITABILITY_TEST, OBSERVABILITY_TEST |
| [REQ-051](#req-051) | IMPLEMENTATION | observability | Section 5.1 Functional Acceptance Criteria — table row AC-08 | 2 | AUDITABILITY_TEST, OBSERVABILITY_TEST |
| [REQ-052](#req-052) | IMPLEMENTATION | observability | Section 5.1 Functional Acceptance Criteria — table row AC-09 | 3 | OBSERVABILITY_TEST |
| [REQ-053](#req-053) | IMPLEMENTATION | auditability | Section 5.1 Functional Acceptance Criteria — table row AC-10 | 2 | AUDITABILITY_TEST, SECURITY_TEST |
| [REQ-054](#req-054) | IMPLEMENTATION | governance | Section 5.1 Functional Acceptance Criteria — table row AC-11 | 5 | AUDITABILITY_TEST, GOVERNANCE_TEST |
| [REQ-055](#req-055) | IMPLEMENTATION | evaluation | Section 5.1 Functional Acceptance Criteria — table row AC-12 | 4 | INTEGRATION_TEST |
| [REQ-056](#req-056) | IMPLEMENTATION | security | Section 5.2 Non-Functional Requirements — table row NFR-01 | 3 | CONFIGURATION_TEST, SECURITY_TEST |
| [REQ-057](#req-057) | IMPLEMENTATION | non_functional | Section 5.2 Non-Functional Requirements — table row NFR-02 | 3 | CONFIGURATION_TEST, DOCUMENTATION_TEST, RUNTIME_TEST |
| [REQ-058](#req-058) | IMPLEMENTATION | security | Section 5.2 Non-Functional Requirements — table row NFR-03 | 2 | SECURITY_TEST |
| [REQ-059](#req-059) | IMPLEMENTATION | non_functional | Section 5.2 Non-Functional Requirements — table row NFR-04 | 2 | ARCHITECTURE_TEST |
| [REQ-060](#req-060) | IMPLEMENTATION | security | Section 5.2 Non-Functional Requirements — table row NFR-05 | 2 | DATA_VALIDATION_TEST, SECURITY_TEST |
| [REQ-061](#req-061) | IMPLEMENTATION | auditability | Section 5.2 Non-Functional Requirements — table row NFR-06 | 2 | AUDITABILITY_TEST |
| [REQ-062](#req-062) | IMPLEMENTATION | orchestration | Section 6.1 In Scope — bullet 1 | 1 | ARCHITECTURE_TEST |
| [REQ-063](#req-063) | IMPLEMENTATION | observability | Section 6.1 In Scope — bullet 2 | 5 | GOVERNANCE_TEST, INTEGRATION_TEST, OBSERVABILITY_TEST, SECURITY_TEST |
| [REQ-064](#req-064) | IMPLEMENTATION | functional | Section 6.1 In Scope — bullet 3 | 3 | CONFIGURATION_TEST, DOCUMENTATION_TEST, INTEGRATION_TEST |
| [REQ-065](#req-065) | IMPLEMENTATION | non_functional | Section 6.2 Out of Scope (this cut) — bullet 1 | 1 | NEGATIVE_TEST |
| [REQ-066](#req-066) | IMPLEMENTATION | integration | Section 6.2 Out of Scope (this cut) — bullet 2 | 2 | DATA_VALIDATION_TEST, NEGATIVE_TEST |
| [REQ-067](#req-067) | ENGAGEMENT | non_functional | Section 6.2 Out of Scope (this cut) — bullet 3 | 1 | NEGATIVE_TEST |
| [REQ-068](#req-068) | IMPLEMENTATION | security | Section 6.2 Out of Scope (this cut) — bullet 4 | 2 | DOCUMENTATION_TEST, NEGATIVE_TEST |
| [REQ-069](#req-069) | ENGAGEMENT | governance | Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 1 | 1 | GOVERNANCE_TEST |
| [REQ-070](#req-070) | IMPLEMENTATION | auditability | Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 2 | 2 | DATA_VALIDATION_TEST, STATIC_TEST |
| [REQ-071](#req-071) | IMPLEMENTATION | auditability | Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 3 | 2 | AUDITABILITY_TEST |
| [REQ-072](#req-072) | IMPLEMENTATION | orchestration | Section 7.1 Agentic System — Foundation — table row "LangGraph graph" | 6 | ARCHITECTURE_TEST, OUTPUT_VALIDATION_TEST, STATIC_TEST |
| [REQ-073](#req-073) | IMPLEMENTATION | integration | Section 7.1 Agentic System — Foundation — table row "MCP server" | 4 | AUDITABILITY_TEST, INTEGRATION_TEST, STATIC_TEST |
| [REQ-074](#req-074) | IMPLEMENTATION | functional | Section 7.1 Agentic System — Foundation — table row "Context engineering" | 4 | ARCHITECTURE_TEST, SECURITY_TEST, STATIC_TEST |
| [REQ-075](#req-075) | IMPLEMENTATION | functional | Section 7.1 Agentic System — Foundation — table row "Tiered memory" | 5 | ARCHITECTURE_TEST, AUDITABILITY_TEST, INTEGRATION_TEST, STATIC_TEST |
| [REQ-076](#req-076) | IMPLEMENTATION | policy | Section 7.1 Agentic System — Foundation — table row "Agentic-RAG tool" | 4 | DATA_VALIDATION_TEST, INTEGRATION_TEST, STATIC_TEST |
| [REQ-077](#req-077) | IMPLEMENTATION | observability | Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Phoenix instrumentation" | 3 | OBSERVABILITY_TEST, STATIC_TEST |
| [REQ-078](#req-078) | IMPLEMENTATION | observability | Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Trace export" | 2 | OBSERVABILITY_TEST, STATIC_TEST |
| [REQ-079](#req-079) | IMPLEMENTATION | observability | Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Tool-invocation log" | 4 | AUDITABILITY_TEST, OBSERVABILITY_TEST, STATIC_TEST |
| [REQ-080](#req-080) | IMPLEMENTATION | observability | Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Failure-mode analysis" | 2 | OBSERVABILITY_TEST, STATIC_TEST |
| [REQ-081](#req-081) | IMPLEMENTATION | observability | Section 7.3 Performance & Cost Governance — table row "Golden-signals report" | 3 | AUDITABILITY_TEST, OBSERVABILITY_TEST, STATIC_TEST |
| [REQ-082](#req-082) | IMPLEMENTATION | observability | Section 7.3 Performance & Cost Governance — table row "Cost/latency dashboard" | 2 | AUDITABILITY_TEST, OBSERVABILITY_TEST |
| [REQ-083](#req-083) | IMPLEMENTATION | security | Section 7.4 Security & Guardrails — table row "Guardrail code" | 2 | SECURITY_TEST, STATIC_TEST |
| [REQ-084](#req-084) | IMPLEMENTATION | auditability | Section 7.4 Security & Guardrails — table row "Audit trail" | 3 | AUDITABILITY_TEST, STATIC_TEST |
| [REQ-085](#req-085) | IMPLEMENTATION | security | Section 7.4 Security & Guardrails — table row "Secrets hygiene" | 2 | CONFIGURATION_TEST, SECURITY_TEST |
| [REQ-086](#req-086) | IMPLEMENTATION | risk | Section 7.5 Governance & Compliance (citation-gated) — table row "Risk register" | 3 | AUDITABILITY_TEST, GOVERNANCE_TEST, STATIC_TEST |
| [REQ-087](#req-087) | IMPLEMENTATION | governance | Section 7.5 Governance & Compliance (citation-gated) — table row "Model / system card" | 3 | AUDITABILITY_TEST, GOVERNANCE_TEST, STATIC_TEST |
| [REQ-088](#req-088) | IMPLEMENTATION | governance | Section 7.5 Governance & Compliance (citation-gated) — table row "Compliance mapping" | 3 | AUDITABILITY_TEST, GOVERNANCE_TEST, STATIC_TEST |
| [REQ-089](#req-089) | IMPLEMENTATION | risk | Section 7.5 Governance & Compliance (citation-gated) — table row "Output-risk classification" | 4 | GOVERNANCE_TEST, STATIC_TEST |
| [REQ-090](#req-090) | IMPLEMENTATION | evaluation | Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Evaluation report" | 2 | INTEGRATION_TEST, STATIC_TEST |
| [REQ-091](#req-091) | IMPLEMENTATION | orchestration | Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Routing-logic test" | 2 | INTEGRATION_TEST, STATIC_TEST |
| [REQ-092](#req-092) | IMPLEMENTATION | orchestration | Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Loop/cascade guard" | 3 | ARCHITECTURE_TEST, INTEGRATION_TEST, STATIC_TEST |
| [REQ-093](#req-093) | IMPLEMENTATION | integration | Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Tool-contract test" | 2 | INTEGRATION_TEST, STATIC_TEST |
| [REQ-094](#req-094) | IMPLEMENTATION | non_functional | Section 7.7 Engineering & Delivery — table row "Local-run runbook" | 4 | CONFIGURATION_TEST, DOCUMENTATION_TEST, RUNTIME_TEST, STATIC_TEST |
| [REQ-095](#req-095) | OPTIONAL | functional | Section 7.7 Engineering & Delivery — table row "Bonus" | 2 | API_TEST, ARCHITECTURE_TEST |
| [REQ-096](#req-096) | IMPLEMENTATION | auditability | Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 1 | 3 | AUDITABILITY_TEST, DATA_VALIDATION_TEST |
| [REQ-097](#req-097) | IMPLEMENTATION | auditability | Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 2 | 3 | NEGATIVE_TEST, OBSERVABILITY_TEST |
| [REQ-098](#req-098) | IMPLEMENTATION | observability | Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 3 | 3 | CONFIGURATION_TEST, OBSERVABILITY_TEST |
| [REQ-099](#req-099) | IMPLEMENTATION | observability | Section 8. Producing the Evidence — table row "Phoenix trace export" | 4 | AUDITABILITY_TEST, DATA_VALIDATION_TEST, OBSERVABILITY_TEST |
| [REQ-100](#req-100) | IMPLEMENTATION | observability | Section 8. Producing the Evidence — table row "Tool-invocation log" | 3 | ARCHITECTURE_TEST, DATA_VALIDATION_TEST |
| [REQ-101](#req-101) | IMPLEMENTATION | observability | Section 8. Producing the Evidence — table row "Failure-mode analysis" | 2 | DATA_VALIDATION_TEST, OBSERVABILITY_TEST |
| [REQ-102](#req-102) | IMPLEMENTATION | observability | Section 8. Producing the Evidence — table row "Golden-signals report" | 4 | DATA_VALIDATION_TEST, OBSERVABILITY_TEST |
| [REQ-103](#req-103) | IMPLEMENTATION | observability | Section 8. Producing the Evidence — table row "Cost/latency dashboard" | 2 | AUDITABILITY_TEST, DATA_VALIDATION_TEST |
| [REQ-104](#req-104) | IMPLEMENTATION | security | Section 8. Producing the Evidence — table row "Guardrail code" | 3 | ARCHITECTURE_TEST, SECURITY_TEST, STATIC_TEST |
| [REQ-105](#req-105) | IMPLEMENTATION | auditability | Section 8. Producing the Evidence — table row "Audit trail" | 2 | AUDITABILITY_TEST, DATA_VALIDATION_TEST |
| [REQ-106](#req-106) | IMPLEMENTATION | governance | Section 8. Producing the Evidence — table row "Governance pack" (continuation table) | 2 | AUDITABILITY_TEST, GOVERNANCE_TEST |
| [REQ-107](#req-107) | IMPLEMENTATION | evaluation | Section 8. Producing the Evidence — table row "Evaluation report" (continuation table) | 2 | DATA_VALIDATION_TEST, INTEGRATION_TEST |
| [REQ-108](#req-108) | IMPLEMENTATION | evaluation | Section 8. Producing the Evidence — table row "Agent tests" (continuation table) | 4 | INTEGRATION_TEST, STATIC_TEST |
| [REQ-109](#req-109) | OPTIONAL | functional | Section 8.1 Good-to-Have — bullet 1 | 2 | API_TEST, DOCUMENTATION_TEST |
| [REQ-110](#req-110) | OPTIONAL | security | Section 8.1 Good-to-Have — bullet 2 | 3 | DOCUMENTATION_TEST, SECURITY_TEST |
| [REQ-111](#req-111) | OPTIONAL | observability | Section 8.1 Good-to-Have — bullet 3 | 1 | OBSERVABILITY_TEST |
| [REQ-112](#req-112) | IMPLEMENTATION | governance | Section 8.1 Good-to-Have — closing italic paragraph (final paragraph of the document) | 6 | AUDITABILITY_TEST, GOVERNANCE_TEST, INTEGRATION_TEST, OBSERVABILITY_TEST, SECURITY_TEST |

---

## Requirement detail

### REQ-001

**Source location:** Document title block — banner line above the title (first line of the document)  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Agentic AI Engineer Pathway — Capstone Hackathon
~~~

**Tests:** REQ-001-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- File paths and line numbers for both matched fragments.

**Current status:** NOT_RUN

### REQ-002

**Source location:** Document title block — document title  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Loan Origination & Underwriting Copilot
~~~

**Tests:** REQ-002-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- File path and line number of the matched title.

**Current status:** NOT_RUN

### REQ-003

**Source location:** Document title block — subtitle line beneath the title  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Tests:** REQ-003-T01, REQ-003-T02, REQ-003-T03, REQ-003-T04, REQ-003-T05, REQ-003-T06, REQ-003-T07, REQ-003-T08  
**Verification method:** ARCHITECTURE_TEST + DOCUMENTATION_TEST + GOVERNANCE_TEST + INTEGRATION_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 8  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-004

**Source location:** Section 1. Project Identity — table row 1  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Business Case Title | Loan Origination & Underwriting Copilot
~~~

**Tests:** REQ-004-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- File path and line number of the matched title.

**Current status:** NOT_RUN

### REQ-005

**Source location:** Section 1. Project Identity — table row 2  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Business Case ID | BC-AAIE-HACK-02
~~~

**Tests:** REQ-005-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- File path and line number of the matched ID.

**Current status:** NOT_RUN

### REQ-006

**Source location:** Section 1. Project Identity — table row 3  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Domain | Banking & Finance
~~~

**Tests:** REQ-006-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- File path and line number of the matched domain statement.

**Current status:** NOT_RUN

### REQ-007

**Source location:** Section 1. Project Identity — table row 4  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Project Type | Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon
~~~

**Tests:** REQ-007-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- File paths and line numbers for both matched fragments.

**Current status:** NOT_RUN

### REQ-008

**Source location:** Section 2. Engagement Overview — table row 1  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Duration | 20 hours
~~~

**Tests:** REQ-008-T01  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 0  |  **Manual/static tests:** 1  |  **Total weight:** 1

**Implementation evidence required:**

- A completed attestation record for REQ-008-T01 naming 'the 20-hour engagement duration', its attester and date.

**Current status:** NOT_RUN

### REQ-009

**Source location:** Section 2. Engagement Overview — table row 2  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Format | Team of 2–4
~~~

**Tests:** REQ-009-T01  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 0  |  **Manual/static tests:** 1  |  **Total weight:** 1

**Implementation evidence required:**

- A completed attestation record for REQ-009-T01 naming 'a team of 2-4 people', its attester and date.

**Current status:** NOT_RUN

### REQ-010

**Source location:** Section 2. Engagement Overview — table row 3  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**Tests:** REQ-010-T01, REQ-010-T02  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 1  |  **Total weight:** 2

**Implementation evidence required:**

- A completed attestation record for REQ-010-T02 naming 'an automated review against the Hackathon Rubric (7 categories / 100 marks), with no live demo judging', its attester and date.
- git ls-files output count.

**Current status:** NOT_RUN

### REQ-011

**Source location:** Section 2. Engagement Overview — table row 4  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Tests:** REQ-011-T01, REQ-011-T02, REQ-011-T03  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 1  |  **Total weight:** 3

**Implementation evidence required:**

- The 'git remote -v' output.
- The exact source text of REQ-011, showing it fixes no testable value for 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project'.
- The matching remote URL.

**Current status:** NOT_RUN

### REQ-012

**Source location:** Section 2. Engagement Overview — table row 5  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

**Tests:** REQ-012-T01  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 0  |  **Manual/static tests:** 1  |  **Total weight:** 1

**Implementation evidence required:**

- A completed attestation record for REQ-012-T01 naming 'a per-team Excel report containing the Summary, Categories, Scorecard, Detailed and Improvement sections', its attester and date.

**Current status:** NOT_RUN

### REQ-013

**Source location:** Section 2. Engagement Overview — table row 6  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

**Tests:** REQ-013-T01  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 0  |  **Manual/static tests:** 1  |  **Total weight:** 1

**Implementation evidence required:**

- A completed attestation record for REQ-013-T01 naming 'the grade bands Pass >= 60 and Not Yet Passed < 60', its attester and date.

**Current status:** NOT_RUN

### REQ-014

**Source location:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 1  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Tests:** REQ-014-T01, REQ-014-T02, REQ-014-T03, REQ-014-T04, REQ-014-T05, REQ-014-T06, REQ-014-T07, REQ-014-T08, REQ-014-T09, REQ-014-T10  
**Verification method:** ARCHITECTURE_TEST + GOVERNANCE_TEST + INTEGRATION_TEST + OBSERVABILITY_TEST + SECURITY_TEST  
**Automatable tests:** 10  |  **Manual/static tests:** 0  |  **Total weight:** 10

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-015

**Source location:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 2  
**Source type:** SENTENCE  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Every claim is scored from committed evidence.
~~~

**Tests:** REQ-015-T01, REQ-015-T02  
**Verification method:** AUDITABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- For each artifact: its path and its presence or absence in 'git ls-files'.

**Current status:** NOT_RUN

### REQ-016

**Source location:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 1  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
What is not evaluated: the visual polish of any interface, generic unit-test volume, or which optional deployment path you use.
~~~

**Tests:** REQ-016-T01  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- The registry scan result, listing any offending test IDs.

**Current status:** NOT_RUN

### REQ-017

**Source location:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 2  
**Source type:** SENTENCE  
**Requirement category:** non_functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Containerized/cloud deployment is out of scope for this cut.
~~~

**Tests:** REQ-017-T01  
**Verification method:** NEGATIVE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- The README lines searched, and any container command found.

**Current status:** NOT_RUN

### REQ-018

**Source location:** Section 3.1 Problem — sentence 1  
**Source type:** SENTENCE  
**Requirement category:** underwriting  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
A retail bank's loan officers spend most of an application on manual work: gathering the applicant's documents, checking eligibility against product policy, computing affordability, screening for risk flags, and drafting a decision rationale.
~~~

**Tests:** REQ-018-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-019

**Source location:** Section 3.1 Problem — sentence 2  
**Source type:** SENTENCE  
**Requirement category:** policy  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Rules are scattered across policy PDFs and change often, so decisions are inconsistent and slow.
~~~

**Tests:** REQ-019-T01  
**Verification method:** ARCHITECTURE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-020

**Source location:** Section 3.1 Problem — sentence 3  
**Source type:** SENTENCE  
**Requirement category:** underwriting  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Tests:** REQ-020-T01, REQ-020-T02, REQ-020-T03, REQ-020-T04, REQ-020-T05, REQ-020-T06  
**Verification method:** AUDITABILITY_TEST + INTEGRATION_TEST + STATIC_TEST + WORKFLOW_TEST  
**Automatable tests:** 6  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-021

**Source location:** Section 3.2 Your Role — sentence 1  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Agentic AI Engineer.
~~~

**Tests:** REQ-021-T01  
**Verification method:** DOCUMENTATION_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-022

**Source location:** Section 3.2 Your Role — sentence 2  
**Source type:** SENTENCE  
**Requirement category:** orchestration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Tests:** REQ-022-T01, REQ-022-T02, REQ-022-T03, REQ-022-T04, REQ-022-T05, REQ-022-T06, REQ-022-T07  
**Verification method:** ARCHITECTURE_TEST + AUDITABILITY_TEST + GOVERNANCE_TEST + INTEGRATION_TEST + OBSERVABILITY_TEST + SECURITY_TEST  
**Automatable tests:** 7  |  **Manual/static tests:** 0  |  **Total weight:** 7

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-023

**Source location:** Section 3.3 Expected Solution — lead-in sentence  
**Source type:** SENTENCE  
**Requirement category:** non_functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
A working, instrumented multi-agent application delivered as a Git repository that demonstrates:
~~~

**Tests:** REQ-023-T01, REQ-023-T02  
**Verification method:** ARCHITECTURE_TEST + AUDITABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-024

**Source location:** Section 3.3 Expected Solution — bullet 1  
**Source type:** BULLET  
**Requirement category:** orchestration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Tests:** REQ-024-T01, REQ-024-T02, REQ-024-T03, REQ-024-T04, REQ-024-T05, REQ-024-T06  
**Verification method:** ARCHITECTURE_TEST + OUTPUT_VALIDATION_TEST  
**Automatable tests:** 6  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-025

**Source location:** Section 3.3 Expected Solution — bullet 2  
**Source type:** BULLET  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Tests:** REQ-025-T01, REQ-025-T02, REQ-025-T03, REQ-025-T04, REQ-025-T05, REQ-025-T06, REQ-025-T07  
**Verification method:** ARCHITECTURE_TEST + INTEGRATION_TEST + SECURITY_TEST  
**Automatable tests:** 7  |  **Manual/static tests:** 0  |  **Total weight:** 7

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The registered tool and resource names found in the MCP server sources.

**Current status:** NOT_RUN

### REQ-026

**Source location:** Section 3.3 Expected Solution — bullet 3  
**Source type:** BULLET  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

**Tests:** REQ-026-T01, REQ-026-T02, REQ-026-T03  
**Verification method:** OBSERVABILITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-027

**Source location:** Section 3.3 Expected Solution — bullet 4  
**Source type:** BULLET  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Tests:** REQ-027-T01, REQ-027-T02, REQ-027-T03, REQ-027-T04, REQ-027-T05, REQ-027-T06  
**Verification method:** AUDITABILITY_TEST + GOVERNANCE_TEST + OBSERVABILITY_TEST + SECURITY_TEST  
**Automatable tests:** 6  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-028

**Source location:** Section 3.3 Expected Solution — bullet 5  
**Source type:** BULLET  
**Requirement category:** evaluation  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Tests:** REQ-028-T01, REQ-028-T02, REQ-028-T03, REQ-028-T04, REQ-028-T05  
**Verification method:** DOCUMENTATION_TEST + INTEGRATION_TEST  
**Automatable tests:** 5  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-029

**Source location:** Section 3.4 Applicable Rules — bullet 1 (Evidence-in-Repo Rule)  
**Source type:** BULLET  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Evidence-in-Repo Rule. Only committed artifacts are scored. A claim with no committed evidence scores zero; an evidence artifact with no producing code (a metric, trace or log a team could hand-write) is heavily discounted.
~~~

**Tests:** REQ-029-T01, REQ-029-T02  
**Verification method:** AUDITABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- For each artifact: the producing source file and line, or a statement that none exists.

**Current status:** NOT_RUN

### REQ-030

**Source location:** Section 3.4 Applicable Rules — bullet 2 (Citation-Resolves Rule)  
**Source type:** BULLET  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Citation-Resolves Rule. Wherever a document cites evidence (a Phoenix run/span id, a log record, a control file), the citation must resolve to a committed artifact. Unresolvable citations are treated as missing.
~~~

**Tests:** REQ-030-T01, REQ-030-T02  
**Verification method:** AUDITABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-031

**Source location:** Section 3.4 Applicable Rules — bullet 3 (Synthetic-Data Rule)  
**Source type:** BULLET  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

**Tests:** REQ-031-T01, REQ-031-T02, REQ-031-T03  
**Verification method:** DATA_VALIDATION_TEST + NEGATIVE_TEST + SECURITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The scanned file count, and any matching file and line.

**Current status:** NOT_RUN

### REQ-032

**Source location:** Section 3.4 Applicable Rules — bullet 4 (Open-Source & Gemini-Only Rule)  
**Source type:** BULLET  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

**Tests:** REQ-032-T01, REQ-032-T02, REQ-032-T03, REQ-032-T04  
**Verification method:** CONFIGURATION_TEST + INTEGRATION_TEST + NEGATIVE_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- Scanned file count, and any offending file and line.

**Current status:** NOT_RUN

### REQ-033

**Source location:** Section 3.4 Applicable Rules — bullet 5 (Reproducibility Rule)  
**Source type:** BULLET  
**Requirement category:** non_functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs.
~~~

**Tests:** REQ-033-T01, REQ-033-T02  
**Verification method:** CONFIGURATION_TEST + DOCUMENTATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The documented command lines found in README.md.

**Current status:** NOT_RUN

### REQ-034

**Source location:** Section 4. Technology & Framework Stack — lead-in paragraph  
**Source type:** SENTENCE  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

**Tests:** REQ-034-T01, REQ-034-T02, REQ-034-T03  
**Verification method:** CONFIGURATION_TEST + NEGATIVE_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-035

**Source location:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"  
**Source type:** TABLE_ROW  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**Tests:** REQ-035-T01, REQ-035-T02, REQ-035-T03  
**Verification method:** CONFIGURATION_TEST + GOVERNANCE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 1  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The exact source text of REQ-035, showing it fixes no testable value for 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence'.

**Current status:** NOT_RUN

### REQ-036

**Source location:** Section 4. Technology & Framework Stack — table row "LLM Provider"  
**Source type:** TABLE_ROW  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
LLM Provider | Google Gemini (API) — the only approved provider; not Claude
~~~

**Tests:** REQ-036-T01, REQ-036-T02  
**Verification method:** INTEGRATION_TEST + NEGATIVE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-037

**Source location:** Section 4. Technology & Framework Stack — table row "Interoperability"  
**Source type:** TABLE_ROW  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Interoperability | MCP Python SDK (stdio) + langchain-mcp-adapters
~~~

**Tests:** REQ-037-T01, REQ-037-T02  
**Verification method:** INTEGRATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-038

**Source location:** Section 4. Technology & Framework Stack — table row "Memory"  
**Source type:** TABLE_ROW  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Memory | langgraph-checkpoint-sqlite (SQLite file) + LangMem
~~~

**Tests:** REQ-038-T01, REQ-038-T02  
**Verification method:** INTEGRATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-039

**Source location:** Section 4. Technology & Framework Stack — table row "Retrieval"  
**Source type:** TABLE_ROW  
**Requirement category:** policy  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Retrieval | Chroma or FAISS + Sentence-Transformers (local)
~~~

**Tests:** REQ-039-T01, REQ-039-T02  
**Verification method:** INTEGRATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-040

**Source location:** Section 4. Technology & Framework Stack — table row "Observability (mandated)"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

**Tests:** REQ-040-T01, REQ-040-T02, REQ-040-T03  
**Verification method:** OBSERVABILITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-041

**Source location:** Section 4. Technology & Framework Stack — table row "Evaluation"  
**Source type:** TABLE_ROW  
**Requirement category:** evaluation  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Evaluation | DeepEval (LLM-as-judge = Gemini) · pytest for agent tests
~~~

**Tests:** REQ-041-T01, REQ-041-T02  
**Verification method:** CONFIGURATION_TEST + INTEGRATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-042

**Source location:** Section 4. Technology & Framework Stack — table row "Security"  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

**Tests:** REQ-042-T01, REQ-042-T02, REQ-042-T03  
**Verification method:** SECURITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-043

**Source location:** Section 4. Technology & Framework Stack — table row "Interface" (continuation table)  
**Source type:** TABLE_ROW  
**Requirement category:** functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Interface | CLI (required) · FastAPI streaming (optional / bonus)
~~~

**Tests:** REQ-043-T01, REQ-043-T02  
**Verification method:** ARCHITECTURE_TEST + CONFIGURATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Presence or absence of the optional API surface.
- The CLI entry point location and the documented invocation.

**Current status:** NOT_RUN

### REQ-044

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-01  
**Source type:** TABLE_ROW  
**Requirement category:** eligibility  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

**Tests:** REQ-044-T01, REQ-044-T02, REQ-044-T03, REQ-044-T04  
**Verification method:** DATA_VALIDATION_TEST + INTEGRATION_TEST + OUTPUT_VALIDATION_TEST + RUNTIME_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The executed command and the matched output text.
- The matched policy-rule citation in the observable output.

**Current status:** NOT_RUN

### REQ-045

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-02  
**Source type:** TABLE_ROW  
**Requirement category:** affordability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Tests:** REQ-045-T01, REQ-045-T02, REQ-045-T03, REQ-045-T04  
**Verification method:** BOUNDARY_TEST + RUNTIME_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 1  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The exact source text of REQ-045, showing it fixes no testable value for 'the numeric DTI or disposable-income threshold that constitutes a policy breach'.

**Current status:** NOT_RUN

### REQ-046

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-03  
**Source type:** TABLE_ROW  
**Requirement category:** underwriting  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Tests:** REQ-046-T01, REQ-046-T02, REQ-046-T03, REQ-046-T04, REQ-046-T05, REQ-046-T06, REQ-046-T07  
**Verification method:** BOUNDARY_TEST + OUTPUT_VALIDATION_TEST + RUNTIME_TEST + STATIC_TEST + WORKFLOW_TEST  
**Automatable tests:** 6  |  **Manual/static tests:** 1  |  **Total weight:** 9

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The exact source text of REQ-046, showing it fixes no testable value for 'the loan value above which a case counts as a high-value case'.

**Current status:** NOT_RUN

### REQ-047

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-04  
**Source type:** TABLE_ROW  
**Requirement category:** workflow  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

**Tests:** REQ-047-T01, REQ-047-T02, REQ-047-T03, REQ-047-T04  
**Verification method:** STATIC_TEST + WORKFLOW_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-048

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-05  
**Source type:** TABLE_ROW  
**Requirement category:** functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-05 | The copilot maintains context — it uses facts stated earlier in the interaction and recalls prior-session context on a return visit.
~~~

**Tests:** REQ-048-T01, REQ-048-T02  
**Verification method:** INTEGRATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-049

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-06  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

**Tests:** REQ-049-T01, REQ-049-T02, REQ-049-T03, REQ-049-T04  
**Verification method:** NEGATIVE_TEST + SECURITY_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 7

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-050

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-07  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

**Tests:** REQ-050-T01, REQ-050-T02, REQ-050-T03  
**Verification method:** AUDITABILITY_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-051

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-08  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-08 | docs/failure-analysis.md documents ≥ 3 real failures from your own runs, each citing the Phoenix run_id + span_id (or a tool-log record) that shows it, plus root cause and fix.
~~~

**Tests:** REQ-051-T01, REQ-051-T02  
**Verification method:** AUDITABILITY_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-052

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-09  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

**Tests:** REQ-052-T01, REQ-052-T02, REQ-052-T03  
**Verification method:** OBSERVABILITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-053

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-10  
**Source type:** TABLE_ROW  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-10 | Input/output guardrails wired into the agent's I/O path, and a machine-generated audit trail of agent actions (logs/agent_actions.jsonl).
~~~

**Tests:** REQ-053-T01, REQ-053-T02  
**Verification method:** AUDITABILITY_TEST + SECURITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-054

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-11  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Tests:** REQ-054-T01, REQ-054-T02, REQ-054-T03, REQ-054-T04, REQ-054-T05  
**Verification method:** AUDITABILITY_TEST + GOVERNANCE_TEST  
**Automatable tests:** 5  |  **Manual/static tests:** 0  |  **Total weight:** 7

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-055

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-12  
**Source type:** TABLE_ROW  
**Requirement category:** evaluation  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

**Tests:** REQ-055-T01, REQ-055-T02, REQ-055-T03, REQ-055-T04  
**Verification method:** INTEGRATION_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-056

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-01  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

**Tests:** REQ-056-T01, REQ-056-T02, REQ-056-T03  
**Verification method:** CONFIGURATION_TEST + SECURITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-057

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-02  
**Source type:** TABLE_ROW  
**Requirement category:** non_functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

**Tests:** REQ-057-T01, REQ-057-T02, REQ-057-T03  
**Verification method:** CONFIGURATION_TEST + DOCUMENTATION_TEST + RUNTIME_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-058

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-03  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
NFR-03 | Untrusted free-text applicant-supplied content is quarantined and never treated as instructions.
~~~

**Tests:** REQ-058-T01, REQ-058-T02  
**Verification method:** SECURITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-059

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-04  
**Source type:** TABLE_ROW  
**Requirement category:** non_functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
NFR-04 | Agent pipeline uses async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions).
~~~

**Tests:** REQ-059-T01, REQ-059-T02  
**Verification method:** ARCHITECTURE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-060

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-05  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
NFR-05 | All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext.
~~~

**Tests:** REQ-060-T01, REQ-060-T02  
**Verification method:** DATA_VALIDATION_TEST + SECURITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-061

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-06  
**Source type:** TABLE_ROW  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
NFR-06 | Evidence artifacts (traces, logs, reports) are machine-generated by committed code; the code that produced each is committed alongside it.
~~~

**Tests:** REQ-061-T01, REQ-061-T02  
**Verification method:** AUDITABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-062

**Source location:** Section 6.1 In Scope — bullet 1  
**Source type:** BULLET  
**Requirement category:** orchestration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
The LangGraph multi-agent copilot (foundation) plus its full observability, cost-governance, security, governance and evaluation surface.
~~~

**Tests:** REQ-062-T01  
**Verification method:** ARCHITECTURE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-063

**Source location:** Section 6.1 In Scope — bullet 2  
**Source type:** BULLET  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Tests:** REQ-063-T01, REQ-063-T02, REQ-063-T03, REQ-063-T04, REQ-063-T05  
**Verification method:** GOVERNANCE_TEST + INTEGRATION_TEST + OBSERVABILITY_TEST + SECURITY_TEST  
**Automatable tests:** 5  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-064

**Source location:** Section 6.1 In Scope — bullet 3  
**Source type:** BULLET  
**Requirement category:** functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

**Tests:** REQ-064-T01, REQ-064-T02, REQ-064-T03  
**Verification method:** CONFIGURATION_TEST + DOCUMENTATION_TEST + INTEGRATION_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-065

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 1  
**Source type:** BULLET  
**Requirement category:** non_functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Containerized / cloud deployment (Docker, Rancher, k8s) — deferred; do not spend hackathon time on it.
~~~

**Tests:** REQ-065-T01  
**Verification method:** NEGATIVE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-066

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 2  
**Source type:** BULLET  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Real credit-bureau or core-banking integrations — use synthetic application and policy data.
~~~

**Tests:** REQ-066-T01, REQ-066-T02  
**Verification method:** DATA_VALIDATION_TEST + NEGATIVE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-067

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 3  
**Source type:** BULLET  
**Requirement category:** non_functional  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
Front-end visual polish; generic unit-test volume for its own sake.
~~~

**Tests:** REQ-067-T01  
**Verification method:** NEGATIVE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-068

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 4  
**Source type:** BULLET  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Advanced OAuth flows and live secrets-rotation infrastructure (document the approach instead).
~~~

**Tests:** REQ-068-T01, REQ-068-T02  
**Verification method:** DOCUMENTATION_TEST + NEGATIVE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-069

**Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 1  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** ENGAGEMENT

**Exact requirement (verbatim, unaltered):**

~~~text
This is the checklist your submission is scored against.
~~~

**Tests:** REQ-069-T01  
**Verification method:** GOVERNANCE_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-070

**Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 2  
**Source type:** SENTENCE  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Each artifact must be present at (or near) the path shown and contain what is listed.
~~~

**Tests:** REQ-070-T01, REQ-070-T02  
**Verification method:** DATA_VALIDATION_TEST + STATIC_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-071

**Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 3  
**Source type:** SENTENCE  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Remember the Evidence-in-Repo and Citation-Resolves rules: outputs must be produced by committed code, and every citation must resolve to a committed artifact.
~~~

**Tests:** REQ-071-T01, REQ-071-T02  
**Verification method:** AUDITABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-072

**Source location:** Section 7.1 Agentic System — Foundation — table row "LangGraph graph"  
**Source type:** TABLE_ROW  
**Requirement category:** orchestration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Tests:** REQ-072-T01, REQ-072-T02, REQ-072-T03, REQ-072-T04, REQ-072-T05, REQ-072-T06  
**Verification method:** ARCHITECTURE_TEST + OUTPUT_VALIDATION_TEST + STATIC_TEST  
**Automatable tests:** 6  |  **Manual/static tests:** 0  |  **Total weight:** 10

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The supervisor location and the located worker agents.

**Current status:** NOT_RUN

### REQ-073

**Source location:** Section 7.1 Agentic System — Foundation — table row "MCP server"  
**Source type:** TABLE_ROW  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

**Tests:** REQ-073-T01, REQ-073-T02, REQ-073-T03, REQ-073-T04  
**Verification method:** AUDITABILITY_TEST + INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The registered tool and resource names.

**Current status:** NOT_RUN

### REQ-074

**Source location:** Section 7.1 Agentic System — Foundation — table row "Context engineering"  
**Source type:** TABLE_ROW  
**Requirement category:** functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

**Tests:** REQ-074-T01, REQ-074-T02, REQ-074-T03, REQ-074-T04  
**Verification method:** ARCHITECTURE_TEST + SECURITY_TEST + STATIC_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-075

**Source location:** Section 7.1 Agentic System — Foundation — table row "Tiered memory"  
**Source type:** TABLE_ROW  
**Requirement category:** functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Tests:** REQ-075-T01, REQ-075-T02, REQ-075-T03, REQ-075-T04, REQ-075-T05  
**Verification method:** ARCHITECTURE_TEST + AUDITABILITY_TEST + INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 5  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-076

**Source location:** Section 7.1 Agentic System — Foundation — table row "Agentic-RAG tool"  
**Source type:** TABLE_ROW  
**Requirement category:** policy  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

**Tests:** REQ-076-T01, REQ-076-T02, REQ-076-T03, REQ-076-T04  
**Verification method:** DATA_VALIDATION_TEST + INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-077

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Phoenix instrumentation"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

**Tests:** REQ-077-T01, REQ-077-T02, REQ-077-T03  
**Verification method:** OBSERVABILITY_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- The AST call site that activates the tracer.

**Current status:** NOT_RUN

### REQ-078

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Trace export"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Trace export | traces/phoenix_spans.parquet (or .jsonl) | ≥1 full run; spans across multiple agents + every tool call; latencies present
~~~

**Tests:** REQ-078-T01, REQ-078-T02  
**Verification method:** OBSERVABILITY_TEST + STATIC_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- Span count, distinct span names, and the latency column or key.

**Current status:** NOT_RUN

### REQ-079

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Tool-invocation log"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

**Tests:** REQ-079-T01, REQ-079-T02, REQ-079-T03, REQ-079-T04  
**Verification method:** AUDITABILITY_TEST + OBSERVABILITY_TEST + STATIC_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-080

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Failure-mode analysis"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Failure-mode analysis | docs/failure-analysis.md | ≥3 real failures, EACH citing Phoenix run_id + span_id (or tool-log record) + root cause + fix
~~~

**Tests:** REQ-080-T01, REQ-080-T02  
**Verification method:** OBSERVABILITY_TEST + STATIC_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-081

**Source location:** Section 7.3 Performance & Cost Governance — table row "Golden-signals report"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

**Tests:** REQ-081-T01, REQ-081-T02, REQ-081-T03  
**Verification method:** AUDITABILITY_TEST + OBSERVABILITY_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-082

**Source location:** Section 7.3 Performance & Cost Governance — table row "Cost/latency dashboard"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Cost/latency dashboard | reports/dashboard.png + reports/dashboard_data.csv | Phoenix latency/cost/token dashboard screenshot AND the underlying data file it was drawn from
~~~

**Tests:** REQ-082-T01, REQ-082-T02  
**Verification method:** AUDITABILITY_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-083

**Source location:** Section 7.4 Security & Guardrails — table row "Guardrail code"  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Guardrail code | src/guardrails/ | input/output guardrails wired into the agent's I/O path (blocks/sanitizes)
~~~

**Tests:** REQ-083-T01, REQ-083-T02  
**Verification method:** SECURITY_TEST + STATIC_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-084

**Source location:** Section 7.4 Security & Guardrails — table row "Audit trail"  
**Source type:** TABLE_ROW  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

**Tests:** REQ-084-T01, REQ-084-T02, REQ-084-T03  
**Verification method:** AUDITABILITY_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-085

**Source location:** Section 7.4 Security & Guardrails — table row "Secrets hygiene"  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Secrets hygiene | .env.example, .gitignore | env-var config; .gitignore covers .env; no secrets committed anywhere
~~~

**Tests:** REQ-085-T01, REQ-085-T02  
**Verification method:** CONFIGURATION_TEST + SECURITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-086

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Risk register"  
**Source type:** TABLE_ROW  
**Requirement category:** risk  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

**Tests:** REQ-086-T01, REQ-086-T02, REQ-086-T03  
**Verification method:** AUDITABILITY_TEST + GOVERNANCE_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-087

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Model / system card"  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

**Tests:** REQ-087-T01, REQ-087-T02, REQ-087-T03  
**Verification method:** AUDITABILITY_TEST + GOVERNANCE_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-088

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Compliance mapping"  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

**Tests:** REQ-088-T01, REQ-088-T02, REQ-088-T03  
**Verification method:** AUDITABILITY_TEST + GOVERNANCE_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-089

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Output-risk classification"  
**Source type:** TABLE_ROW  
**Requirement category:** risk  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

**Tests:** REQ-089-T01, REQ-089-T02, REQ-089-T03, REQ-089-T04  
**Verification method:** GOVERNANCE_TEST + STATIC_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-090

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Evaluation report"  
**Source type:** TABLE_ROW  
**Requirement category:** evaluation  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Evaluation report | reports/eval_report.json + harness | DeepEval (or equiv) over a golden set: hallucination + faithfulness/relevance; LLM-as-judge
~~~

**Tests:** REQ-090-T01, REQ-090-T02  
**Verification method:** INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-091

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Routing-logic test"  
**Source type:** TABLE_ROW  
**Requirement category:** orchestration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Routing-logic test | tests/test_routing.py | asserts conditional edges route the right worker for given states
~~~

**Tests:** REQ-091-T01, REQ-091-T02  
**Verification method:** INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-092

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Loop/cascade guard"  
**Source type:** TABLE_ROW  
**Requirement category:** orchestration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

**Tests:** REQ-092-T01, REQ-092-T02, REQ-092-T03  
**Verification method:** ARCHITECTURE_TEST + INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-093

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Tool-contract test"  
**Source type:** TABLE_ROW  
**Requirement category:** integration  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Tool-contract test | tests/test_tool_contracts.py | asserts each tool's input/output schema + one error path
~~~

**Tests:** REQ-093-T01, REQ-093-T02  
**Verification method:** INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-094

**Source location:** Section 7.7 Engineering & Delivery — table row "Local-run runbook"  
**Source type:** TABLE_ROW  
**Requirement category:** non_functional  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

**Tests:** REQ-094-T01, REQ-094-T02, REQ-094-T03, REQ-094-T04  
**Verification method:** CONFIGURATION_TEST + DOCUMENTATION_TEST + RUNTIME_TEST + STATIC_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-095

**Source location:** Section 7.7 Engineering & Delivery — table row "Bonus"  
**Source type:** TABLE_ROW  
**Requirement category:** functional  
**Requirement class:** OPTIONAL

**Exact requirement (verbatim, unaltered):**

~~~text
Bonus | src/api/ (FastAPI streaming) | OPTIONAL: async FastAPI streaming endpoint — extra credit, not required
~~~

**Tests:** REQ-095-T01, REQ-095-T02  
**Verification method:** API_TEST + ARCHITECTURE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.
- Presence or absence of src/api/, and the state of the required CLI.

**Current status:** NOT_RUN

### REQ-096

**Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 1  
**Source type:** SENTENCE  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

**Tests:** REQ-096-T01, REQ-096-T02, REQ-096-T03  
**Verification method:** AUDITABILITY_TEST + DATA_VALIDATION_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-097

**Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 2  
**Source type:** SENTENCE  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

**Tests:** REQ-097-T01, REQ-097-T02, REQ-097-T03  
**Verification method:** NEGATIVE_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-098

**Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 3  
**Source type:** SENTENCE  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

**Tests:** REQ-098-T01, REQ-098-T02, REQ-098-T03  
**Verification method:** CONFIGURATION_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-099

**Source location:** Section 8. Producing the Evidence — table row "Phoenix trace export"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

**Tests:** REQ-099-T01, REQ-099-T02, REQ-099-T03, REQ-099-T04  
**Verification method:** AUDITABILITY_TEST + DATA_VALIDATION_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-100

**Source location:** Section 8. Producing the Evidence — table row "Tool-invocation log"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

**Tests:** REQ-100-T01, REQ-100-T02, REQ-100-T03  
**Verification method:** ARCHITECTURE_TEST + DATA_VALIDATION_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 7

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-101

**Source location:** Section 8. Producing the Evidence — table row "Failure-mode analysis"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Failure-mode analysis | Markdown | Open your Phoenix traces, pick ≥ 3 real failures, write each up citing its run_id + span_id, with root cause and the fix.
~~~

**Tests:** REQ-101-T01, REQ-101-T02  
**Verification method:** DATA_VALIDATION_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-102

**Source location:** Section 8. Producing the Evidence — table row "Golden-signals report"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

**Tests:** REQ-102-T01, REQ-102-T02, REQ-102-T03, REQ-102-T04  
**Verification method:** DATA_VALIDATION_TEST + OBSERVABILITY_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-103

**Source location:** Section 8. Producing the Evidence — table row "Cost/latency dashboard"  
**Source type:** TABLE_ROW  
**Requirement category:** observability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Cost/latency dashboard | PNG + CSV | Phoenix UI (localhost:6006) shows latency / cost / token dashboards — screenshot one; export the data with get_spans_dataframe().to_csv('reports/dashboard_data.csv').
~~~

**Tests:** REQ-103-T01, REQ-103-T02  
**Verification method:** AUDITABILITY_TEST + DATA_VALIDATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-104

**Source location:** Section 8. Producing the Evidence — table row "Guardrail code"  
**Source type:** TABLE_ROW  
**Requirement category:** security  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

**Tests:** REQ-104-T01, REQ-104-T02, REQ-104-T03  
**Verification method:** ARCHITECTURE_TEST + SECURITY_TEST + STATIC_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 6

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-105

**Source location:** Section 8. Producing the Evidence — table row "Audit trail"  
**Source type:** TABLE_ROW  
**Requirement category:** auditability  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Audit trail | JSONL | Audit middleware that appends {actor, action, tool, decision, timestamp} for each consequential action to logs/agent_actions.jsonl.
~~~

**Tests:** REQ-105-T01, REQ-105-T02  
**Verification method:** AUDITABILITY_TEST + DATA_VALIDATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-106

**Source location:** Section 8. Producing the Evidence — table row "Governance pack" (continuation table)  
**Source type:** TABLE_ROW  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Governance pack | Markdown | risk-register.md, model-card.md, compliance.md, output-risk.md — each entry cites the committed control/artifact it refers to.
~~~

**Tests:** REQ-106-T01, REQ-106-T02  
**Verification method:** AUDITABILITY_TEST + GOVERNANCE_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-107

**Source location:** Section 8. Producing the Evidence — table row "Evaluation report" (continuation table)  
**Source type:** TABLE_ROW  
**Requirement category:** evaluation  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Evaluation report | JSON | A DeepEval run over your golden set (hallucination, faithfulness, answer-relevance) that writes reports/eval_report.json, plus the harness.
~~~

**Tests:** REQ-107-T01, REQ-107-T02  
**Verification method:** DATA_VALIDATION_TEST + INTEGRATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 4

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-108

**Source location:** Section 8. Producing the Evidence — table row "Agent tests" (continuation table)  
**Source type:** TABLE_ROW  
**Requirement category:** evaluation  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

**Tests:** REQ-108-T01, REQ-108-T02, REQ-108-T03, REQ-108-T04  
**Verification method:** INTEGRATION_TEST + STATIC_TEST  
**Automatable tests:** 4  |  **Manual/static tests:** 0  |  **Total weight:** 5

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-109

**Source location:** Section 8.1 Good-to-Have — bullet 1  
**Source type:** BULLET  
**Requirement category:** functional  
**Requirement class:** OPTIONAL

**Exact requirement (verbatim, unaltered):**

~~~text
FastAPI streaming endpoint; a demonstrated local run (screenshot/log).
~~~

**Tests:** REQ-109-T01, REQ-109-T02  
**Verification method:** API_TEST + DOCUMENTATION_TEST  
**Automatable tests:** 2  |  **Manual/static tests:** 0  |  **Total weight:** 2

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-110

**Source location:** Section 8.1 Good-to-Have — bullet 2  
**Source type:** BULLET  
**Requirement category:** security  
**Requirement class:** OPTIONAL

**Exact requirement (verbatim, unaltered):**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

**Tests:** REQ-110-T01, REQ-110-T02, REQ-110-T03  
**Verification method:** DOCUMENTATION_TEST + SECURITY_TEST  
**Automatable tests:** 3  |  **Manual/static tests:** 0  |  **Total weight:** 3

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-111

**Source location:** Section 8.1 Good-to-Have — bullet 3  
**Source type:** BULLET  
**Requirement category:** observability  
**Requirement class:** OPTIONAL

**Exact requirement (verbatim, unaltered):**

~~~text
An optimization note showing a measured before/after latency or cost improvement (two Phoenix-derived reports).
~~~

**Tests:** REQ-111-T01  
**Verification method:** OBSERVABILITY_TEST  
**Automatable tests:** 1  |  **Manual/static tests:** 0  |  **Total weight:** 1

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

### REQ-112

**Source location:** Section 8.1 Good-to-Have — closing italic paragraph (final paragraph of the document)  
**Source type:** SENTENCE  
**Requirement category:** governance  
**Requirement class:** IMPLEMENTATION

**Exact requirement (verbatim, unaltered):**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Tests:** REQ-112-T01, REQ-112-T02, REQ-112-T03, REQ-112-T04, REQ-112-T05, REQ-112-T06  
**Verification method:** AUDITABILITY_TEST + GOVERNANCE_TEST + INTEGRATION_TEST + OBSERVABILITY_TEST + SECURITY_TEST  
**Automatable tests:** 6  |  **Manual/static tests:** 0  |  **Total weight:** 8

**Implementation evidence required:**

- Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Current status:** NOT_RUN

