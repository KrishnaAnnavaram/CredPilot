<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - underwriting

Generated: 2026-09-20T05:48:35Z

3 requirement(s), 14 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-018

**Source location:** Section 3.1 Problem — sentence 1  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
A retail bank's loan officers spend most of an application on manual work: gathering the applicant's documents, checking eligibility against product policy, computing affordability, screening for risk flags, and drafting a decision rationale.
~~~

### REQ-018-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-018-T01 |
| **Requirement ID** | REQ-018 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A retail bank's loan officers spend most of an application on manual work: gathering the applicant's documents, checking eligibility against product policy, computing affordability, screening for risk flags, and drafting a decision rationale.
~~~

**Purpose:** The manual loan-officer activities the document names are the activities the delivered system documents itself as covering.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan committed Markdown documentation.
2. Require each activity named in the problem statement to be addressed: gathering documents, checking eligibility, computing affordability, screening risk flags, drafting a decision rationale.

**Expected Result:** All five manual activities named in the problem statement are addressed in the documentation.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All five manual activities named in the problem statement are addressed in the documentation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All five manual activities named in the problem statement are addressed in the documentation.

---

## REQ-020

**Source location:** Section 3.1 Problem — sentence 3  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

### REQ-020-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-020-T01 |
| **Requirement ID** | REQ-020 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Purpose:** The copilot ingests a loan application.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate committed sample loan applications.
2. Confirm the source code handles applications.

**Expected Result:** Committed loan application inputs exist and the code ingests them.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed loan application inputs exist and the code ingests them.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed loan application inputs exist and the code ingests them.

### REQ-020-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-020-T02 |
| **Requirement ID** | REQ-020 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Purpose:** The copilot retrieves the current lending policy.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the policy-retrieval tool and the lending-policy corpus.

**Expected Result:** A policy-retrieval capability over a lending-policy corpus exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A policy-retrieval capability over a lending-policy corpus exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A policy-retrieval capability over a lending-policy corpus exists.

### REQ-020-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-020-T03 |
| **Requirement ID** | REQ-020 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Purpose:** The copilot computes eligibility and affordability.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation's Python sources for eligibility and affordability logic.

**Expected Result:** Both eligibility and affordability computation are implemented.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both eligibility and affordability computation are implemented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both eligibility and affordability computation are implemented.

### REQ-020-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-020-T04 |
| **Requirement ID** | REQ-020 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Purpose:** The copilot screens risk.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation's Python sources for risk screening.

**Expected Result:** Risk screening is implemented.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Risk screening is implemented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Risk screening is implemented.

### REQ-020-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-020-T05 |
| **Requirement ID** | REQ-020 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Purpose:** The copilot drafts an auditable decision recommendation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the decision vocabulary exists in the code.
2. Confirm an audit trail records the decision, making it auditable.

**Expected Result:** A decision recommendation is produced and recorded in an audit trail.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A decision recommendation is produced and recorded in an audit trail.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A decision recommendation is produced and recorded in an audit trail.

### REQ-020-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-020-T06 |
| **Requirement ID** | REQ-020 |
| **Test Type** | WORKFLOW_TEST |
| **Executing suite** | `automated_tests/workflow/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Purpose:** A human makes the final call rather than the system auto-deciding.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for a human-review / escalation path.

**Expected Result:** A human-review or escalation path exists so a human makes the final call.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A human-review or escalation path exists so a human makes the final call.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A human-review or escalation path exists so a human makes the final call.

---

## REQ-046

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-03  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

### REQ-046-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-046-T01 |
| **Requirement ID** | REQ-046 |
| **Test Type** | RUNTIME_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Purpose:** The copilot produces a decision recommendation from the approve / refer / decline set.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** The implementation's own committed synthetic loan application sample inputs.

**Execution Steps:**

1. Execute the documented run command.
2. Require one of the three decision terms the document names in the observable output.

**Expected Result:** The observable output carries an approve / refer / decline recommendation.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The observable output carries an approve / refer / decline recommendation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The observable output carries an approve / refer / decline recommendation.

### REQ-046-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-046-T02 |
| **Requirement ID** | REQ-046 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Purpose:** All three decision outcomes the document names are implemented.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for each of the three named decision outcomes.

**Expected Result:** approve, refer and decline are all implemented outcomes.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: approve, refer and decline are all implemented outcomes.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: approve, refer and decline are all implemented outcomes.

### REQ-046-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-046-T03 |
| **Requirement ID** | REQ-046 |
| **Test Type** | OUTPUT_VALIDATION_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Purpose:** The recommendation carries a written rationale.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Execute the documented run command.
2. Require a written rationale alongside the recommendation.

**Expected Result:** A written rationale accompanies the decision recommendation.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A written rationale accompanies the decision recommendation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A written rationale accompanies the decision recommendation.

### REQ-046-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-046-T04 |
| **Requirement ID** | REQ-046 |
| **Test Type** | WORKFLOW_TEST |
| **Executing suite** | `automated_tests/workflow/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Purpose:** A decline is routed for human review rather than auto-decided.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the decline path.
2. Require it to hand off to human review rather than finalise the decision.

**Expected Result:** A decline is routed for human review rather than auto-decided.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A decline is routed for human review rather than auto-decided.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A decline is routed for human review rather than auto-decided.

### REQ-046-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-046-T05 |
| **Requirement ID** | REQ-046 |
| **Test Type** | WORKFLOW_TEST |
| **Executing suite** | `automated_tests/workflow/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Purpose:** A high-value case is routed for human review rather than auto-decided.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the high-value case path.
2. Require it to route for human review rather than auto-decide.

**Expected Result:** A high-value case is routed for human review rather than auto-decided.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A high-value case is routed for human review rather than auto-decided.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A high-value case is routed for human review rather than auto-decided.

### REQ-046-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-046-T06 |
| **Requirement ID** | REQ-046 |
| **Test Type** | WORKFLOW_TEST |
| **Executing suite** | `automated_tests/workflow/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Purpose:** A human-review route exists for the cases the criterion names.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the human-review destination those routes lead to.

**Expected Result:** A human-review route exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A human-review route exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A human-review route exists.

### REQ-046-T07

| Field | Value |
| --- | --- |
| **Test ID** | REQ-046-T07 |
| **Requirement ID** | REQ-046 |
| **Test Type** | BOUNDARY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Purpose:** The monetary boundary at which a case becomes high-value.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Re-read the exact source text of REQ-046.
2. Confirm the document specifies no verifiable value or artifact for 'the loan value above which a case counts as a high-value case'.
3. Record UNSPECIFIED_BY_REQUIREMENT rather than inventing a threshold or path.

**Expected Result:** UNSPECIFIED_BY_REQUIREMENT for 'the loan value above which a case counts as a high-value case'

**Evidence Required:** The exact source text of REQ-046, showing it fixes no testable value for 'the loan value above which a case counts as a high-value case'.

**Pass Condition:** Not reachable: the document supplies nothing to verify against.

**Fail Condition:** Recorded as UNSPECIFIED_BY_REQUIREMENT because the document fixes no value for 'the loan value above which a case counts as a high-value case'.

---
