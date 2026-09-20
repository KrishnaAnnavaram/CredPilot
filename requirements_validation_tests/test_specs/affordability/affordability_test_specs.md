<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - affordability

Generated: 2026-09-20T05:48:35Z

1 requirement(s), 4 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-045

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-02  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

### REQ-045-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-045-T01 |
| **Requirement ID** | REQ-045 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Purpose:** The copilot computes affordability as DTI or disposable income.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation's Python sources for a DTI or disposable-income calculation.

**Expected Result:** Affordability is computed as DTI or disposable income.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Affordability is computed as DTI or disposable income.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Affordability is computed as DTI or disposable income.

### REQ-045-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-045-T02 |
| **Requirement ID** | REQ-045 |
| **Test Type** | RUNTIME_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Purpose:** Affordability is computed from the application data and reported.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** The implementation's own committed synthetic loan application sample inputs.

**Execution Steps:**

1. Execute the documented run command against the committed application.
2. Inspect the observable output for the affordability result.

**Expected Result:** The copilot reports an affordability result computed from the application data.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The copilot reports an affordability result computed from the application data.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The copilot reports an affordability result computed from the application data.

### REQ-045-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-045-T03 |
| **Requirement ID** | REQ-045 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Purpose:** A policy breach is flagged together with the threshold it failed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the breach flag.
2. Require the breach to carry the threshold value that was failed.

**Expected Result:** A policy breach is flagged with the threshold it failed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A policy breach is flagged with the threshold it failed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A policy breach is flagged with the threshold it failed.

### REQ-045-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-045-T04 |
| **Requirement ID** | REQ-045 |
| **Test Type** | BOUNDARY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Purpose:** The DTI / disposable-income threshold values themselves.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Re-read the exact source text of REQ-045.
2. Confirm the document specifies no verifiable value or artifact for 'the numeric DTI or disposable-income threshold that constitutes a policy breach'.
3. Record UNSPECIFIED_BY_REQUIREMENT rather than inventing a threshold or path.

**Expected Result:** UNSPECIFIED_BY_REQUIREMENT for 'the numeric DTI or disposable-income threshold that constitutes a policy breach'

**Evidence Required:** The exact source text of REQ-045, showing it fixes no testable value for 'the numeric DTI or disposable-income threshold that constitutes a policy breach'.

**Pass Condition:** Not reachable: the document supplies nothing to verify against.

**Fail Condition:** Recorded as UNSPECIFIED_BY_REQUIREMENT because the document fixes no value for 'the numeric DTI or disposable-income threshold that constitutes a policy breach'.

---
