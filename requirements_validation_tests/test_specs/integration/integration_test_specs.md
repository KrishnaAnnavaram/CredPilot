<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - integration

Generated: 2026-09-20T05:48:35Z

10 requirement(s), 31 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-025

**Source location:** Section 3.3 Expected Solution — bullet 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

### REQ-025-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-025-T01 |
| **Requirement ID** | REQ-025 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Purpose:** A custom MCP server exists with at least 2 tools and 1 resource.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the MCP server package.
2. Count distinct MCP tool registrations; require >= 2.
3. Count distinct MCP resource registrations; require >= 1.

**Expected Result:** The MCP server exposes at least 2 tools and at least 1 resource.

**Evidence Required:** The registered tool and resource names found in the MCP server sources.

**Pass Condition:** Collected evidence satisfies: The MCP server exposes at least 2 tools and at least 1 resource.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The MCP server exposes at least 2 tools and at least 1 resource.

### REQ-025-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-025-T02 |
| **Requirement ID** | REQ-025 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Purpose:** The MCP server is consumed via langchain-mcp-adapters.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm langchain-mcp-adapters is a declared dependency.
2. Confirm it is imported by the implementation.

**Expected Result:** The MCP server is consumed through langchain-mcp-adapters.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The MCP server is consumed through langchain-mcp-adapters.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The MCP server is consumed through langchain-mcp-adapters.

### REQ-025-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-025-T03 |
| **Requirement ID** | REQ-025 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Purpose:** Engineered context implements write, select, compress and isolate.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the context package for each of write, select, compress and isolate.

**Expected Result:** All four context operations are implemented.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All four context operations are implemented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All four context operations are implemented.

### REQ-025-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-025-T04 |
| **Requirement ID** | REQ-025 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Purpose:** Context engineering includes summarization.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the context package for summarization.

**Expected Result:** Summarization is implemented in the context layer.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Summarization is implemented in the context layer.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Summarization is implemented in the context layer.

### REQ-025-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-025-T05 |
| **Requirement ID** | REQ-025 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Purpose:** Untrusted applicant-supplied text is quarantined.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for quarantine handling of untrusted text.

**Expected Result:** Untrusted applicant-supplied text is quarantined.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Untrusted applicant-supplied text is quarantined.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Untrusted applicant-supplied text is quarantined.

### REQ-025-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-025-T06 |
| **Requirement ID** | REQ-025 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Purpose:** Tiered memory has verified cross-session persistence.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the memory package.
2. Locate the cross-session persistence test.
3. Locate the committed output log that verifies it ran.

**Expected Result:** Tiered memory exists with a persistence test and a committed output log proving it was verified.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Tiered memory exists with a persistence test and a committed output log proving it was verified.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Tiered memory exists with a persistence test and a committed output log proving it was verified.

### REQ-025-T07

| Field | Value |
| --- | --- |
| **Test ID** | REQ-025-T07 |
| **Requirement ID** | REQ-025 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Purpose:** An agentic-RAG tool operates over a synthetic lending-policy corpus.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the RAG tool.
2. Locate the lending-policy corpus it retrieves over.

**Expected Result:** A RAG tool and a lending-policy corpus both exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A RAG tool and a lending-policy corpus both exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A RAG tool and a lending-policy corpus both exist.

---

## REQ-032

**Source location:** Section 3.4 Applicable Rules — bullet 4 (Open-Source & Gemini-Only Rule)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

### REQ-032-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-032-T01 |
| **Requirement ID** | REQ-032 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

**Purpose:** Google Gemini is used as the model provider.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm a Google Gemini SDK is a declared dependency.
2. Confirm Gemini is referenced in the implementation sources.

**Expected Result:** Google Gemini is the configured model provider.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Google Gemini is the configured model provider.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Google Gemini is the configured model provider.

### REQ-032-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-032-T02 |
| **Requirement ID** | REQ-032 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

**Purpose:** Claude is not used as a model provider.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the implementation sources for Anthropic/Claude provider usage.
2. Scan the dependency manifests for an Anthropic client.

**Expected Result:** No Anthropic/Claude model provider is used or declared.

**Evidence Required:** Scanned file count, and any offending file and line.

**Pass Condition:** Collected evidence satisfies: No Anthropic/Claude model provider is used or declared.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No Anthropic/Claude model provider is used or declared.

### REQ-032-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-032-T03 |
| **Requirement ID** | REQ-032 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

**Purpose:** The project builds, runs and evaluates with pip + Python.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate a pip-installable dependency manifest.
2. Confirm the README documents a pip install step.

**Expected Result:** The project installs and runs through pip + Python.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The project installs and runs through pip + Python.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The project installs and runs through pip + Python.

### REQ-032-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-032-T04 |
| **Requirement ID** | REQ-032 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

**Purpose:** No Docker or external database service is required for this cut.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm no Dockerfile or compose file exists.
2. Scan for external database service connection strings.

**Expected Result:** Neither Docker nor an external database service is required.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Neither Docker nor an external database service is required.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Neither Docker nor an external database service is required.

---

## REQ-034

**Source location:** Section 4. Technology & Framework Stack — lead-in paragraph  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

### REQ-034-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-034-T01 |
| **Requirement ID** | REQ-034 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

**Purpose:** Google Gemini is the only model provider in the toolchain.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm a Gemini SDK is declared.
2. Confirm no other model-provider SDK is declared.

**Expected Result:** Gemini is declared and no other model provider is.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Gemini is declared and no other model provider is.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Gemini is declared and no other model provider is.

### REQ-034-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-034-T02 |
| **Requirement ID** | REQ-034 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

**Purpose:** Everything installs with pip.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate a pip-installable dependency manifest.

**Expected Result:** A pip-installable dependency manifest exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A pip-installable dependency manifest exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A pip-installable dependency manifest exists.

### REQ-034-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-034-T03 |
| **Requirement ID** | REQ-034 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

**Purpose:** No Docker or external DB service is required.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm no container build or orchestration file exists.
2. Scan for external database connection strings.

**Expected Result:** No Docker or external DB service is required.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No Docker or external DB service is required.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No Docker or external DB service is required.

---

## REQ-035

**Source location:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

### REQ-035-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-035-T01 |
| **Requirement ID** | REQ-035 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**Purpose:** The project declares Python 3.11 or newer.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search pyproject.toml, setup.cfg, .python-version, runtime.txt and README.md for a declared Python version.

**Expected Result:** Python 3.11+ is declared.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Python 3.11+ is declared.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Python 3.11+ is declared.

### REQ-035-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-035-T02 |
| **Requirement ID** | REQ-035 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**Purpose:** LangGraph is the agent framework.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm langgraph is declared as a dependency.
2. Confirm it is imported.

**Expected Result:** LangGraph is declared and used.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: LangGraph is declared and used.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: LangGraph is declared and used.

### REQ-035-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-035-T03 |
| **Requirement ID** | REQ-035 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**Purpose:** LangGraph is used under the MIT licence.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Re-read the exact source text of REQ-035.
2. Confirm the document specifies no verifiable value or artifact for 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence'.
3. Record UNSPECIFIED_BY_REQUIREMENT rather than inventing a threshold or path.

**Expected Result:** UNSPECIFIED_BY_REQUIREMENT for 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence'

**Evidence Required:** The exact source text of REQ-035, showing it fixes no testable value for 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence'.

**Pass Condition:** Not reachable: the document supplies nothing to verify against.

**Fail Condition:** Recorded as UNSPECIFIED_BY_REQUIREMENT because the document fixes no value for 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence'.

---

## REQ-036

**Source location:** Section 4. Technology & Framework Stack — table row "LLM Provider"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
LLM Provider | Google Gemini (API) — the only approved provider; not Claude
~~~

### REQ-036-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-036-T01 |
| **Requirement ID** | REQ-036 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LLM Provider | Google Gemini (API) — the only approved provider; not Claude
~~~

**Purpose:** Google Gemini is used through its API.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm a Gemini SDK is declared.
2. Confirm a Gemini model is referenced in code.

**Expected Result:** The Gemini API is the model provider in use.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The Gemini API is the model provider in use.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The Gemini API is the model provider in use.

### REQ-036-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-036-T02 |
| **Requirement ID** | REQ-036 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LLM Provider | Google Gemini (API) — the only approved provider; not Claude
~~~

**Purpose:** Claude is not used, since Gemini is the only approved provider.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan source and dependency manifests for Anthropic/Claude.

**Expected Result:** Claude is not used as a provider.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Claude is not used as a provider.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Claude is not used as a provider.

---

## REQ-037

**Source location:** Section 4. Technology & Framework Stack — table row "Interoperability"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Interoperability | MCP Python SDK (stdio) + langchain-mcp-adapters
~~~

### REQ-037-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-037-T01 |
| **Requirement ID** | REQ-037 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Interoperability | MCP Python SDK (stdio) + langchain-mcp-adapters
~~~

**Purpose:** The MCP Python SDK is used over stdio.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the MCP Python SDK is declared.
2. Confirm the stdio transport is used.

**Expected Result:** The MCP Python SDK is used with the stdio transport.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The MCP Python SDK is used with the stdio transport.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The MCP Python SDK is used with the stdio transport.

### REQ-037-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-037-T02 |
| **Requirement ID** | REQ-037 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Interoperability | MCP Python SDK (stdio) + langchain-mcp-adapters
~~~

**Purpose:** langchain-mcp-adapters provides interoperability.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm langchain-mcp-adapters is declared.
2. Confirm it is imported.

**Expected Result:** langchain-mcp-adapters is declared and used.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: langchain-mcp-adapters is declared and used.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: langchain-mcp-adapters is declared and used.

---

## REQ-038

**Source location:** Section 4. Technology & Framework Stack — table row "Memory"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Memory | langgraph-checkpoint-sqlite (SQLite file) + LangMem
~~~

### REQ-038-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-038-T01 |
| **Requirement ID** | REQ-038 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Memory | langgraph-checkpoint-sqlite (SQLite file) + LangMem
~~~

**Purpose:** langgraph-checkpoint-sqlite provides the SQLite-file checkpointer.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm langgraph-checkpoint-sqlite is declared.
2. Confirm the SQLite checkpointer is used in code.

**Expected Result:** The SQLite-file checkpointer is declared and used.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The SQLite-file checkpointer is declared and used.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The SQLite-file checkpointer is declared and used.

### REQ-038-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-038-T02 |
| **Requirement ID** | REQ-038 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Memory | langgraph-checkpoint-sqlite (SQLite file) + LangMem
~~~

**Purpose:** LangMem provides the memory layer.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm langmem is declared.
2. Confirm it is used in code.

**Expected Result:** LangMem is declared and used.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: LangMem is declared and used.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: LangMem is declared and used.

---

## REQ-066

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Real credit-bureau or core-banking integrations — use synthetic application and policy data.
~~~

### REQ-066-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-066-T01 |
| **Requirement ID** | REQ-066 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Real credit-bureau or core-banking integrations — use synthetic application and policy data.
~~~

**Purpose:** No real credit-bureau or core-banking integration is present.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the implementation for real credit-bureau or core-banking integrations.

**Expected Result:** No real credit-bureau or core-banking integration is present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No real credit-bureau or core-banking integration is present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No real credit-bureau or core-banking integration is present.

### REQ-066-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-066-T02 |
| **Requirement ID** | REQ-066 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Real credit-bureau or core-banking integrations — use synthetic application and policy data.
~~~

**Purpose:** Synthetic application and policy data is used instead.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the synthetic policy corpus.
2. Locate the committed synthetic applications.

**Expected Result:** Synthetic application and policy data is used.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Synthetic application and policy data is used.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Synthetic application and policy data is used.

---

## REQ-073

**Source location:** Section 7.1 Agentic System — Foundation — table row "MCP server"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

### REQ-073-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-073-T01 |
| **Requirement ID** | REQ-073 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

**Purpose:** The MCP server artifact exists at mcp_server/.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the mcp_server/ package at or near the path shown.

**Expected Result:** mcp_server/ exists and is non-empty.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: mcp_server/ exists and is non-empty.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: mcp_server/ exists and is non-empty.

### REQ-073-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-073-T02 |
| **Requirement ID** | REQ-073 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

**Purpose:** The MCP server exposes at least 2 tools and at least 1 resource.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse the MCP server sources.
2. Count decorated/registered MCP tools; require >= 2.
3. Count decorated/registered MCP resources; require >= 1.

**Expected Result:** At least 2 MCP tools and at least 1 MCP resource are registered.

**Evidence Required:** The registered tool and resource names.

**Pass Condition:** Collected evidence satisfies: At least 2 MCP tools and at least 1 MCP resource are registered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: At least 2 MCP tools and at least 1 MCP resource are registered.

### REQ-073-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-073-T03 |
| **Requirement ID** | REQ-073 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

**Purpose:** The MCP server is consumed via langchain-mcp-adapters.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the adapter package is declared.
2. Confirm it is imported.

**Expected Result:** The MCP server is consumed through langchain-mcp-adapters.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The MCP server is consumed through langchain-mcp-adapters.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The MCP server is consumed through langchain-mcp-adapters.

### REQ-073-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-073-T04 |
| **Requirement ID** | REQ-073 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

**Purpose:** A committed tool-call transcript exists at logs/mcp_transcript.jsonl.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate logs/mcp_transcript.jsonl and parse it.
2. Confirm git tracks it.

**Expected Result:** A committed, parseable MCP tool-call transcript exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A committed, parseable MCP tool-call transcript exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A committed, parseable MCP tool-call transcript exists.

---

## REQ-093

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Tool-contract test"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Tool-contract test | tests/test_tool_contracts.py | asserts each tool's input/output schema + one error path
~~~

### REQ-093-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-093-T01 |
| **Requirement ID** | REQ-093 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-contract test | tests/test_tool_contracts.py | asserts each tool's input/output schema + one error path
~~~

**Purpose:** The tool-contract test exists at tests/test_tool_contracts.py.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_tool_contracts.py at or near the path shown.

**Expected Result:** tests/test_tool_contracts.py exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: tests/test_tool_contracts.py exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: tests/test_tool_contracts.py exists.

### REQ-093-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-093-T02 |
| **Requirement ID** | REQ-093 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-contract test | tests/test_tool_contracts.py | asserts each tool's input/output schema + one error path
~~~

**Purpose:** It asserts each tool's input/output schema plus one error path.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require test functions and assertions.
2. Require input/output schema assertions.
3. Require at least one error path.

**Expected Result:** The test asserts each tool's I/O schema and an error path.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The test asserts each tool's I/O schema and an error path.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The test asserts each tool's I/O schema and an error path.

---
