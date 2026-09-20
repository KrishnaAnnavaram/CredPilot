<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - eligibility

Generated: 2026-09-20T05:48:35Z

1 requirement(s), 4 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-044

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-01  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

### REQ-044-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-044-T01 |
| **Requirement ID** | REQ-044 |
| **Test Type** | RUNTIME_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

**Purpose:** Given a synthetic loan application, the copilot returns an eligibility determination.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** The implementation's own committed synthetic loan application sample inputs.

**Execution Steps:**

1. Discover the documented run command from the implementation's README.md.
2. Execute it against the committed synthetic loan application.
3. Inspect the observable output for an eligibility determination.

**Expected Result:** The copilot's observable output states an eligibility determination.

**Evidence Required:** The executed command and the matched output text.

**Pass Condition:** Collected evidence satisfies: The copilot's observable output states an eligibility determination.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The copilot's observable output states an eligibility determination.

### REQ-044-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-044-T02 |
| **Requirement ID** | REQ-044 |
| **Test Type** | OUTPUT_VALIDATION_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

**Purpose:** The eligibility determination cites the policy rule it applied.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** The implementation's own committed synthetic loan application sample inputs.

**Execution Steps:**

1. Execute the documented run command.
2. Require the eligibility output to name the policy and the rule it applied.

**Expected Result:** The eligibility determination cites the policy rule it applied.

**Evidence Required:** The matched policy-rule citation in the observable output.

**Pass Condition:** Collected evidence satisfies: The eligibility determination cites the policy rule it applied.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The eligibility determination cites the policy rule it applied.

### REQ-044-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-044-T03 |
| **Requirement ID** | REQ-044 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

**Purpose:** The applicable current lending policy is retrieved rather than hard-coded.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the retrieval tool.
2. Locate the lending-policy corpus it retrieves from.

**Expected Result:** A retrieval tool reads the applicable current lending policy from a corpus.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A retrieval tool reads the applicable current lending policy from a corpus.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A retrieval tool reads the applicable current lending policy from a corpus.

### REQ-044-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-044-T04 |
| **Requirement ID** | REQ-044 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

**Purpose:** Synthetic loan applications are committed so the criterion can be exercised.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the conventional input locations for committed application inputs.

**Expected Result:** Committed synthetic loan applications exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed synthetic loan applications exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed synthetic loan applications exist.

---
