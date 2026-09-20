<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - workflow

Generated: 2026-09-20T05:48:35Z

1 requirement(s), 4 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-047

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-04  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

### REQ-047-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-047-T01 |
| **Requirement ID** | REQ-047 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

**Purpose:** The copilot identifies each application's intent.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for intent identification.

**Expected Result:** Application intent is identified.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Application intent is identified.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Application intent is identified.

### REQ-047-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-047-T02 |
| **Requirement ID** | REQ-047 |
| **Test Type** | WORKFLOW_TEST |
| **Executing suite** | `automated_tests/workflow/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

**Purpose:** Each identified intent is handled with the right capability.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the mapping from identified intent to the handling capability.

**Expected Result:** An identified intent selects the matching capability.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An identified intent selects the matching capability.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An identified intent selects the matching capability.

### REQ-047-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-047-T03 |
| **Requirement ID** | REQ-047 |
| **Test Type** | WORKFLOW_TEST |
| **Executing suite** | `automated_tests/workflow/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

**Purpose:** Ambiguous requests are clarified.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the ambiguous-request path and its clarification behaviour.

**Expected Result:** Ambiguous requests trigger clarification.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Ambiguous requests trigger clarification.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Ambiguous requests trigger clarification.

### REQ-047-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-047-T04 |
| **Requirement ID** | REQ-047 |
| **Test Type** | WORKFLOW_TEST |
| **Executing suite** | `automated_tests/workflow/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

**Purpose:** Out-of-scope requests are escalated to a human rather than mishandled.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the out-of-scope path and confirm it escalates to a human.

**Expected Result:** Out-of-scope requests are escalated to a human.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Out-of-scope requests are escalated to a human.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Out-of-scope requests are escalated to a human.

---
