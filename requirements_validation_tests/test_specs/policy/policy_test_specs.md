<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - policy

Generated: 2026-09-20T05:48:35Z

3 requirement(s), 7 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-019

**Source location:** Section 3.1 Problem — sentence 2  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Rules are scattered across policy PDFs and change often, so decisions are inconsistent and slow.
~~~

### REQ-019-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-019-T01 |
| **Requirement ID** | REQ-019 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Rules are scattered across policy PDFs and change often, so decisions are inconsistent and slow.
~~~

**Purpose:** Lending rules are retrieved from a policy corpus rather than being fixed in code, so changes are picked up.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the policy corpus directory.
2. Locate the retrieval tool that reads it.

**Expected Result:** A policy corpus and a retrieval tool over it both exist, so changed rules are re-read rather than re-coded.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A policy corpus and a retrieval tool over it both exist, so changed rules are re-read rather than re-coded.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A policy corpus and a retrieval tool over it both exist, so changed rules are re-read rather than re-coded.

---

## REQ-039

**Source location:** Section 4. Technology & Framework Stack — table row "Retrieval"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Retrieval | Chroma or FAISS + Sentence-Transformers (local)
~~~

### REQ-039-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-039-T01 |
| **Requirement ID** | REQ-039 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Retrieval | Chroma or FAISS + Sentence-Transformers (local)
~~~

**Purpose:** Chroma or FAISS provides retrieval.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Check for Chroma as the vector store.
2. Otherwise check for FAISS - the document permits either.

**Expected Result:** Either Chroma or FAISS is declared and used.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Either Chroma or FAISS is declared and used.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Either Chroma or FAISS is declared and used.

### REQ-039-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-039-T02 |
| **Requirement ID** | REQ-039 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Retrieval | Chroma or FAISS + Sentence-Transformers (local)
~~~

**Purpose:** Sentence-Transformers provides local embeddings.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm sentence-transformers is declared.
2. Confirm it is used in code.

**Expected Result:** Sentence-Transformers is declared and used locally.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Sentence-Transformers is declared and used locally.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Sentence-Transformers is declared and used locally.

---

## REQ-076

**Source location:** Section 7.1 Agentic System — Foundation — table row "Agentic-RAG tool"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

### REQ-076-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-076-T01 |
| **Requirement ID** | REQ-076 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

**Purpose:** The agentic-RAG tool exists at src/tools/rag_tool.py.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate src/tools/rag_tool.py at or near the path shown.

**Expected Result:** src/tools/rag_tool.py exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: src/tools/rag_tool.py exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: src/tools/rag_tool.py exists.

### REQ-076-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-076-T02 |
| **Requirement ID** | REQ-076 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

**Purpose:** The lending-policy corpus exists at data/policy_corpus/.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate data/policy_corpus/ at or near the path shown and confirm it is non-empty.

**Expected Result:** data/policy_corpus/ exists with content.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: data/policy_corpus/ exists with content.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: data/policy_corpus/ exists with content.

### REQ-076-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-076-T03 |
| **Requirement ID** | REQ-076 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

**Purpose:** Retrieval happens in the loop, not as a one-off preprocessing step.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the RAG capability is exposed to the agent as a callable tool.
2. Confirm the tool performs retrieval when called.

**Expected Result:** Retrieval is in the agent loop as a callable tool.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Retrieval is in the agent loop as a callable tool.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Retrieval is in the agent loop as a callable tool.

### REQ-076-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-076-T04 |
| **Requirement ID** | REQ-076 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

**Purpose:** The corpus is a synthetic lending-policy corpus.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the repository for the declaration that the policy corpus is synthetic.

**Expected Result:** The lending-policy corpus is declared synthetic.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The lending-policy corpus is declared synthetic.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The lending-policy corpus is declared synthetic.

---
