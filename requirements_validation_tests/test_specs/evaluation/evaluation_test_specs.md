<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - evaluation

Generated: 2026-09-20T05:48:35Z

6 requirement(s), 19 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-028

**Source location:** Section 3.3 Expected Solution — bullet 5  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

### REQ-028-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-028-T01 |
| **Requirement ID** | REQ-028 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Purpose:** Agent-level evaluation covers LLM-as-judge and hallucination.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the evaluation report.
2. Confirm it carries a hallucination metric.

**Expected Result:** An evaluation report exists and reports a hallucination metric.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An evaluation report exists and reports a hallucination metric.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An evaluation report exists and reports a hallucination metric.

### REQ-028-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-028-T02 |
| **Requirement ID** | REQ-028 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Purpose:** The routing-logic agent test exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_routing.py.

**Expected Result:** The routing-logic test module exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The routing-logic test module exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The routing-logic test module exists.

### REQ-028-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-028-T03 |
| **Requirement ID** | REQ-028 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Purpose:** The loop/cascade guard agent test exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_loops.py.

**Expected Result:** The loop/cascade guard test module exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The loop/cascade guard test module exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The loop/cascade guard test module exists.

### REQ-028-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-028-T04 |
| **Requirement ID** | REQ-028 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Purpose:** The tool-contract agent test exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_tool_contracts.py.

**Expected Result:** The tool-contract test module exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The tool-contract test module exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The tool-contract test module exists.

### REQ-028-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-028-T05 |
| **Requirement ID** | REQ-028 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Purpose:** A reproducible local-run runbook exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate README.md.
2. Confirm it documents at least one runnable command.

**Expected Result:** A README runbook documents how to run the system.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A README runbook documents how to run the system.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A README runbook documents how to run the system.

---

## REQ-041

**Source location:** Section 4. Technology & Framework Stack — table row "Evaluation"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Evaluation | DeepEval (LLM-as-judge = Gemini) · pytest for agent tests
~~~

### REQ-041-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-041-T01 |
| **Requirement ID** | REQ-041 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evaluation | DeepEval (LLM-as-judge = Gemini) · pytest for agent tests
~~~

**Purpose:** DeepEval provides LLM-as-judge evaluation with Gemini as the judge.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm deepeval is declared and used.
2. Confirm Gemini is the configured judge model.

**Expected Result:** DeepEval is used with Gemini as the LLM judge.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: DeepEval is used with Gemini as the LLM judge.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: DeepEval is used with Gemini as the LLM judge.

### REQ-041-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-041-T02 |
| **Requirement ID** | REQ-041 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evaluation | DeepEval (LLM-as-judge = Gemini) · pytest for agent tests
~~~

**Purpose:** pytest runs the agent tests.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm pytest is declared.
2. Confirm at least one named agent test module exists.

**Expected Result:** pytest is declared and agent tests exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: pytest is declared and agent tests exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: pytest is declared and agent tests exist.

---

## REQ-055

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-12  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

### REQ-055-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-055-T01 |
| **Requirement ID** | REQ-055 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

**Purpose:** A DeepEval (or equivalent) report covers a golden set with hallucination and faithfulness/relevance.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate reports/eval_report.json and parse it.
2. Require hallucination, faithfulness and answer-relevance metrics over a golden set.
3. Require a committed harness that produces it.

**Expected Result:** An evaluation report over a golden set exists with the named metrics and a harness.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An evaluation report over a golden set exists with the named metrics and a harness.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An evaluation report over a golden set exists with the named metrics and a harness.

### REQ-055-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-055-T02 |
| **Requirement ID** | REQ-055 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

**Purpose:** The routing-logic agent test asserts routing behaviour.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_routing.py.
2. Require test functions, assertions, and routing subject matter.

**Expected Result:** The routing-logic test asserts which worker a given state routes to.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The routing-logic test asserts which worker a given state routes to.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The routing-logic test asserts which worker a given state routes to.

### REQ-055-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-055-T03 |
| **Requirement ID** | REQ-055 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

**Purpose:** The loop/cascade guard test asserts a step or recursion limit.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_loops.py.
2. Require test functions, assertions, and a step/recursion limit subject.

**Expected Result:** The loop/cascade guard test asserts that a limit stops runaway loops.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The loop/cascade guard test asserts that a limit stops runaway loops.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The loop/cascade guard test asserts that a limit stops runaway loops.

### REQ-055-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-055-T04 |
| **Requirement ID** | REQ-055 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

**Purpose:** The tool-contract test asserts tool I/O schemas and an error path.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_tool_contracts.py.
2. Require schema assertions and at least one error path.

**Expected Result:** The tool-contract test asserts each tool's I/O schema plus one error path.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The tool-contract test asserts each tool's I/O schema plus one error path.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The tool-contract test asserts each tool's I/O schema plus one error path.

---

## REQ-090

**Source location:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Evaluation report"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Evaluation report | reports/eval_report.json + harness | DeepEval (or equiv) over a golden set: hallucination + faithfulness/relevance; LLM-as-judge
~~~

### REQ-090-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-090-T01 |
| **Requirement ID** | REQ-090 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evaluation report | reports/eval_report.json + harness | DeepEval (or equiv) over a golden set: hallucination + faithfulness/relevance; LLM-as-judge
~~~

**Purpose:** The evaluation report exists at reports/eval_report.json.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate reports/eval_report.json at or near the path shown.

**Expected Result:** reports/eval_report.json exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: reports/eval_report.json exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: reports/eval_report.json exists.

### REQ-090-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-090-T02 |
| **Requirement ID** | REQ-090 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evaluation report | reports/eval_report.json + harness | DeepEval (or equiv) over a golden set: hallucination + faithfulness/relevance; LLM-as-judge
~~~

**Purpose:** A DeepEval (or equivalent) run over a golden set reports hallucination and faithfulness/relevance via LLM-as-judge, with its harness.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse the report.
2. Require hallucination, faithfulness and answer-relevance over a golden set.
3. Require a committed harness using DeepEval or an equivalent LLM-as-judge.

**Expected Result:** The evaluation report and its harness satisfy every element the row lists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The evaluation report and its harness satisfy every element the row lists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The evaluation report and its harness satisfy every element the row lists.

---

## REQ-107

**Source location:** Section 8. Producing the Evidence — table row "Evaluation report" (continuation table)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Evaluation report | JSON | A DeepEval run over your golden set (hallucination, faithfulness, answer-relevance) that writes reports/eval_report.json, plus the harness.
~~~

### REQ-107-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-107-T01 |
| **Requirement ID** | REQ-107 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evaluation report | JSON | A DeepEval run over your golden set (hallucination, faithfulness, answer-relevance) that writes reports/eval_report.json, plus the harness.
~~~

**Purpose:** The evaluation report is committed as JSON.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm reports/eval_report.json parses as JSON.

**Expected Result:** The evaluation report is JSON.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The evaluation report is JSON.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The evaluation report is JSON.

### REQ-107-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-107-T02 |
| **Requirement ID** | REQ-107 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evaluation report | JSON | A DeepEval run over your golden set (hallucination, faithfulness, answer-relevance) that writes reports/eval_report.json, plus the harness.
~~~

**Purpose:** A DeepEval run over the golden set reports hallucination, faithfulness and answer-relevance, plus the harness.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse the report.
2. Require hallucination, faithfulness and answer-relevance over a golden set.
3. Require the committed harness that writes it.

**Expected Result:** The DeepEval run and its harness satisfy everything the row states.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The DeepEval run and its harness satisfy everything the row states.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The DeepEval run and its harness satisfy everything the row states.

---

## REQ-108

**Source location:** Section 8. Producing the Evidence — table row "Agent tests" (continuation table)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

### REQ-108-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-108-T01 |
| **Requirement ID** | REQ-108 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

**Purpose:** The three agent tests exist as pytest files.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate each of the three test modules the row names.

**Expected Result:** All three agent test files exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All three agent test files exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All three agent test files exist.

### REQ-108-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-108-T02 |
| **Requirement ID** | REQ-108 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

**Purpose:** tests/test_routing.py covers routing.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require test functions, assertions, and routing subject matter.

**Expected Result:** The routing test covers routing.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The routing test covers routing.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The routing test covers routing.

### REQ-108-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-108-T03 |
| **Requirement ID** | REQ-108 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

**Purpose:** tests/test_loops.py covers the recursion/step limit.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require test functions, assertions, and a recursion/step-limit subject.

**Expected Result:** The loops test covers the recursion/step limit.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The loops test covers the recursion/step limit.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The loops test covers the recursion/step limit.

### REQ-108-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-108-T04 |
| **Requirement ID** | REQ-108 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

**Purpose:** tests/test_tool_contracts.py covers the I/O schema and an error path.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require test functions, assertions, schema coverage and an error path.

**Expected Result:** The tool-contract test covers the I/O schema and an error path.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The tool-contract test covers the I/O schema and an error path.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The tool-contract test covers the I/O schema and an error path.

---
