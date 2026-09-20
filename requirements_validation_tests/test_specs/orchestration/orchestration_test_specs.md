<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - orchestration

Generated: 2026-09-20T05:48:35Z

6 requirement(s), 25 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-022

**Source location:** Section 3.2 Your Role — sentence 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

### REQ-022-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-022-T01 |
| **Requirement ID** | REQ-022 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Purpose:** A LangGraph multi-agent copilot is built.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the graph module.
2. Confirm langgraph is imported.

**Expected Result:** A LangGraph-based graph module exists and imports langgraph.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A LangGraph-based graph module exists and imports langgraph.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A LangGraph-based graph module exists and imports langgraph.

### REQ-022-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-022-T02 |
| **Requirement ID** | REQ-022 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Purpose:** The copilot is instrumented with Arize Phoenix.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the tracing module.
2. Confirm Phoenix or openinference is imported.

**Expected Result:** Phoenix instrumentation code exists and imports the Phoenix/openinference stack.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Phoenix instrumentation code exists and imports the Phoenix/openinference stack.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Phoenix instrumentation code exists and imports the Phoenix/openinference stack.

### REQ-022-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-022-T03 |
| **Requirement ID** | REQ-022 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Purpose:** Cost and latency are governed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the golden-signals report that carries the latency and cost figures.

**Expected Result:** A golden-signals report exists as the cost and latency governance artifact.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A golden-signals report exists as the cost and latency governance artifact.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A golden-signals report exists as the cost and latency governance artifact.

### REQ-022-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-022-T04 |
| **Requirement ID** | REQ-022 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Purpose:** The copilot is hardened with guardrails and an audit trail.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrails package and the audit trail artifact.

**Expected Result:** Guardrail code and an audit trail both exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Guardrail code and an audit trail both exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Guardrail code and an audit trail both exist.

### REQ-022-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-022-T05 |
| **Requirement ID** | REQ-022 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Purpose:** Risk and compliance posture are documented.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the risk register and the compliance mapping.

**Expected Result:** Risk and compliance posture documents exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Risk and compliance posture documents exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Risk and compliance posture documents exist.

### REQ-022-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-022-T06 |
| **Requirement ID** | REQ-022 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Purpose:** Behaviour is proven with agent-level evaluation and tests.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the evaluation report and the three agent test modules.

**Expected Result:** An evaluation report and the three named agent tests exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An evaluation report and the three named agent tests exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An evaluation report and the three named agent tests exist.

### REQ-022-T07

| Field | Value |
| --- | --- |
| **Test ID** | REQ-022-T07 |
| **Requirement ID** | REQ-022 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Purpose:** Every artifact is delivered as committed evidence.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Enumerate the artifacts the document names by path.
2. Confirm each one present on disk is git-tracked.

**Expected Result:** Every present artifact is committed evidence.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every present artifact is committed evidence.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every present artifact is committed evidence.

---

## REQ-024

**Source location:** Section 3.3 Expected Solution — bullet 1  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

### REQ-024-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-024-T01 |
| **Requirement ID** | REQ-024 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Purpose:** The LangGraph graph uses typed state.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for a typed state definition.

**Expected Result:** The graph state is typed (TypedDict, pydantic model, or dataclass).

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The graph state is typed (TypedDict, pydantic model, or dataclass).

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The graph state is typed (TypedDict, pydantic model, or dataclass).

### REQ-024-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-024-T02 |
| **Requirement ID** | REQ-024 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Purpose:** A supervisor routes loan applications to worker agents.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for a supervisor router.

**Expected Result:** A supervisor component routes applications to workers.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A supervisor component routes applications to workers.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A supervisor component routes applications to workers.

### REQ-024-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-024-T03 |
| **Requirement ID** | REQ-024 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Purpose:** The three specialized worker agents the document names all exist.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for an eligibility-and-affordability agent.
2. Search for a policy-retrieval agent.
3. Search for a risk-screening agent.

**Expected Result:** An eligibility-and-affordability agent, a policy-retrieval agent and a risk-screening agent all exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An eligibility-and-affordability agent, a policy-retrieval agent and a risk-screening agent all exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An eligibility-and-affordability agent, a policy-retrieval agent and a risk-screening agent all exist.

### REQ-024-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-024-T04 |
| **Requirement ID** | REQ-024 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Purpose:** The graph uses conditional routing.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Analyse the Python AST for a call adding conditional edges to the graph.

**Expected Result:** Conditional routing is wired into the graph, not merely described.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Conditional routing is wired into the graph, not merely described.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Conditional routing is wired into the graph, not merely described.

### REQ-024-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-024-T05 |
| **Requirement ID** | REQ-024 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Purpose:** The graph uses checkpointing.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for checkpointer configuration.
2. Confirm the graph is compiled, which is where a checkpointer is attached.

**Expected Result:** A checkpointer is configured on the compiled graph.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A checkpointer is configured on the compiled graph.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A checkpointer is configured on the compiled graph.

### REQ-024-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-024-T06 |
| **Requirement ID** | REQ-024 |
| **Test Type** | OUTPUT_VALIDATION_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Purpose:** The graph produces structured output.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for structured-output binding or a schema type used for node output.

**Expected Result:** Structured output is produced rather than free text only.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Structured output is produced rather than free text only.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Structured output is produced rather than free text only.

---

## REQ-062

**Source location:** Section 6.1 In Scope — bullet 1  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
The LangGraph multi-agent copilot (foundation) plus its full observability, cost-governance, security, governance and evaluation surface.
~~~

### REQ-062-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-062-T01 |
| **Requirement ID** | REQ-062 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
The LangGraph multi-agent copilot (foundation) plus its full observability, cost-governance, security, governance and evaluation surface.
~~~

**Purpose:** The full surface named in scope is delivered: copilot plus observability, cost-governance, security, governance and evaluation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the LangGraph copilot foundation.
2. Locate each of its five named surfaces: observability, cost-governance, security, governance and evaluation.

**Expected Result:** The copilot and all five named surfaces are delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The copilot and all five named surfaces are delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The copilot and all five named surfaces are delivered.

---

## REQ-072

**Source location:** Section 7.1 Agentic System — Foundation — table row "LangGraph graph"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

### REQ-072-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-072-T01 |
| **Requirement ID** | REQ-072 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Purpose:** The LangGraph graph artifact exists at src/graph.py.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate src/graph.py at or near the path shown.

**Expected Result:** src/graph.py exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: src/graph.py exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: src/graph.py exists.

### REQ-072-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-072-T02 |
| **Requirement ID** | REQ-072 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Purpose:** The graph defines typed state.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the graph's state type definition.

**Expected Result:** The graph state is a declared type.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The graph state is a declared type.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The graph state is a declared type.

### REQ-072-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-072-T03 |
| **Requirement ID** | REQ-072 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Purpose:** The graph has a supervisor and at least 3 worker agents.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the supervisor.
2. Count the distinct worker agents; the document requires at least 3.
3. Name each worker found and each expected worker not found.

**Expected Result:** A supervisor plus at least 3 worker agents exist.

**Evidence Required:** The supervisor location and the located worker agents.

**Pass Condition:** Collected evidence satisfies: A supervisor plus at least 3 worker agents exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A supervisor plus at least 3 worker agents exist.

### REQ-072-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-072-T04 |
| **Requirement ID** | REQ-072 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Purpose:** The graph declares conditional edges.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Analyse the Python AST for a call that adds conditional edges.

**Expected Result:** Conditional edges are added to the graph.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Conditional edges are added to the graph.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Conditional edges are added to the graph.

### REQ-072-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-072-T05 |
| **Requirement ID** | REQ-072 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Purpose:** The graph has a checkpointer.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for a checkpointer reference.
2. Require a concrete checkpointer implementation.

**Expected Result:** A checkpointer is configured on the graph.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A checkpointer is configured on the graph.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A checkpointer is configured on the graph.

### REQ-072-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-072-T06 |
| **Requirement ID** | REQ-072 |
| **Test Type** | OUTPUT_VALIDATION_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Purpose:** The graph produces structured output at node boundaries.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the node implementations for structured output at their boundaries.

**Expected Result:** Node boundaries carry structured output.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Node boundaries carry structured output.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Node boundaries carry structured output.

---

## REQ-091

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Routing-logic test"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Routing-logic test | tests/test_routing.py | asserts conditional edges route the right worker for given states
~~~

### REQ-091-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-091-T01 |
| **Requirement ID** | REQ-091 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Routing-logic test | tests/test_routing.py | asserts conditional edges route the right worker for given states
~~~

**Purpose:** The routing-logic test exists at tests/test_routing.py.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_routing.py at or near the path shown.

**Expected Result:** tests/test_routing.py exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: tests/test_routing.py exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: tests/test_routing.py exists.

### REQ-091-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-091-T02 |
| **Requirement ID** | REQ-091 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Routing-logic test | tests/test_routing.py | asserts conditional edges route the right worker for given states
~~~

**Purpose:** It asserts that conditional edges route the right worker for given states.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require test functions and assertions.
2. Require the assertions to be about routing a given state to a worker.

**Expected Result:** The test asserts conditional-edge routing for given states.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The test asserts conditional-edge routing for given states.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The test asserts conditional-edge routing for given states.

---

## REQ-092

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Loop/cascade guard"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

### REQ-092-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-092-T01 |
| **Requirement ID** | REQ-092 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

**Purpose:** The loop/cascade guard test exists at tests/test_loops.py.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_loops.py at or near the path shown.

**Expected Result:** tests/test_loops.py exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: tests/test_loops.py exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: tests/test_loops.py exists.

### REQ-092-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-092-T02 |
| **Requirement ID** | REQ-092 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

**Purpose:** It asserts that a max-steps / recursion-limit stops runaway loops.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require test functions and assertions.
2. Require a max-steps or recursion-limit subject and a stopping assertion.

**Expected Result:** The test asserts that a limit stops runaway loops.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The test asserts that a limit stops runaway loops.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The test asserts that a limit stops runaway loops.

### REQ-092-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-092-T03 |
| **Requirement ID** | REQ-092 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

**Purpose:** A max-steps / recursion limit exists in the implementation to be asserted.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for the configured step or recursion limit.

**Expected Result:** A max-steps / recursion limit is configured.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A max-steps / recursion limit is configured.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A max-steps / recursion limit is configured.

---
