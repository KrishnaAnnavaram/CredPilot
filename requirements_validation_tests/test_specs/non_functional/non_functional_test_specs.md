<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - non_functional

Generated: 2026-09-20T05:48:35Z

8 requirement(s), 16 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-017

**Source location:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Containerized/cloud deployment is out of scope for this cut.
~~~

### REQ-017-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-017-T01 |
| **Requirement ID** | REQ-017 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Containerized/cloud deployment is out of scope for this cut.
~~~

**Purpose:** Running the system does not depend on containerized or cloud deployment.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read the implementation's README.md.
2. Search its documented commands for docker / docker-compose / kubectl / helm.
3. Require that none is present.

**Expected Result:** The documented run path contains no containerized or cloud deployment command.

**Evidence Required:** The README lines searched, and any container command found.

**Pass Condition:** README.md exists and documents no container or cloud deployment command.

**Fail Condition:** A docker / docker-compose / kubectl / helm command appears in the documented run path, or no README.md exists from which the run path could be established.

---

## REQ-023

**Source location:** Section 3.3 Expected Solution — lead-in sentence  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
A working, instrumented multi-agent application delivered as a Git repository that demonstrates:
~~~

### REQ-023-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-023-T01 |
| **Requirement ID** | REQ-023 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A working, instrumented multi-agent application delivered as a Git repository that demonstrates:
~~~

**Purpose:** The application is delivered as a Git repository.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the implementation root is a Git repository with tracked files.

**Expected Result:** The deliverable is a Git repository.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The deliverable is a Git repository.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The deliverable is a Git repository.

### REQ-023-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-023-T02 |
| **Requirement ID** | REQ-023 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A working, instrumented multi-agent application delivered as a Git repository that demonstrates:
~~~

**Purpose:** The delivered application is a working, instrumented multi-agent application.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the multi-agent graph.
2. Locate the instrumentation module.
3. Locate a committed trace export, which only exists if the system actually ran.

**Expected Result:** A multi-agent graph, instrumentation, and a trace export from a real run all exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A multi-agent graph, instrumentation, and a trace export from a real run all exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A multi-agent graph, instrumentation, and a trace export from a real run all exist.

---

## REQ-033

**Source location:** Section 3.4 Applicable Rules — bullet 5 (Reproducibility Rule)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs.
~~~

### REQ-033-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-033-T01 |
| **Requirement ID** | REQ-033 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs.
~~~

**Purpose:** A single documented command regenerates the system, its traces and its evaluation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read the implementation's README.md.
2. Extract the documented commands.
3. Require a documented command for the run, for regenerating Phoenix traces, and for the evaluation.

**Expected Result:** README.md documents the commands that regenerate the system, its traces and its evaluation.

**Evidence Required:** The documented command lines found in README.md.

**Pass Condition:** Collected evidence satisfies: README.md documents the commands that regenerate the system, its traces and its evaluation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: README.md documents the commands that regenerate the system, its traces and its evaluation.

### REQ-033-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-033-T02 |
| **Requirement ID** | REQ-033 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs.
~~~

**Purpose:** Sample inputs are committed so the run is reproducible.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the conventional input locations for committed sample inputs.

**Expected Result:** Committed sample inputs exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed sample inputs exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed sample inputs exist.

---

## REQ-057

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-02  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

### REQ-057-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-057-T01 |
| **Requirement ID** | REQ-057 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

**Purpose:** A single documented command runs the copilot and a second regenerates the traces and the evaluation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read the implementation's README.md.
2. Require one documented command that runs the copilot.
3. Require a documented command that regenerates the Phoenix traces.
4. Require a documented command that regenerates the evaluation.

**Expected Result:** The run command and the regeneration commands are all documented.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The run command and the regeneration commands are all documented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The run command and the regeneration commands are all documented.

### REQ-057-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-057-T02 |
| **Requirement ID** | REQ-057 |
| **Test Type** | RUNTIME_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

**Purpose:** The documented run command actually executes.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Discover the documented run command.
2. Confirm a CLI entry point backs it.

**Expected Result:** The documented command is backed by a real CLI entry point.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The documented command is backed by a real CLI entry point.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The documented command is backed by a real CLI entry point.

### REQ-057-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-057-T03 |
| **Requirement ID** | REQ-057 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

**Purpose:** Sample inputs are committed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the conventional input locations for committed sample inputs.

**Expected Result:** Committed sample inputs exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed sample inputs exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed sample inputs exist.

---

## REQ-059

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-04  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
NFR-04 | Agent pipeline uses async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions).
~~~

### REQ-059-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-059-T01 |
| **Requirement ID** | REQ-059 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-04 | Agent pipeline uses async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions).
~~~

**Purpose:** The agent pipeline uses async where it calls tools/models.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Analyse the Python AST for async definitions.
2. Require await expressions, so the async path is actually used.

**Expected Result:** The pipeline defines and uses async where it calls tools and models.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The pipeline defines and uses async where it calls tools and models.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The pipeline defines and uses async where it calls tools and models.

### REQ-059-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-059-T02 |
| **Requirement ID** | REQ-059 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-04 | Agent pipeline uses async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions).
~~~

**Purpose:** The pipeline degrades gracefully on tool/model failure via timeouts, retries and exit conditions.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for timeouts.
2. Search for retries.
3. Search for exit conditions.
4. Search for failure handling around tool/model calls.

**Expected Result:** Timeouts, retries and exit conditions are all present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Timeouts, retries and exit conditions are all present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Timeouts, retries and exit conditions are all present.

---

## REQ-065

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 1  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Containerized / cloud deployment (Docker, Rancher, k8s) — deferred; do not spend hackathon time on it.
~~~

### REQ-065-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-065-T01 |
| **Requirement ID** | REQ-065 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Containerized / cloud deployment (Docker, Rancher, k8s) — deferred; do not spend hackathon time on it.
~~~

**Purpose:** Containerized / cloud deployment is deferred, so no hackathon time went into it.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the repository for Docker, Rancher and Kubernetes deployment artifacts.

**Expected Result:** No containerized or cloud deployment artifact is present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No containerized or cloud deployment artifact is present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No containerized or cloud deployment artifact is present.

---

## REQ-067

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 3  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Front-end visual polish; generic unit-test volume for its own sake.
~~~

### REQ-067-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-067-T01 |
| **Requirement ID** | REQ-067 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Front-end visual polish; generic unit-test volume for its own sake.
~~~

**Purpose:** No front-end build system is present, so no hackathon time went into visual polish.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the repository for front-end build tooling.

**Expected Result:** No front-end build system is present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No front-end build system is present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No front-end build system is present.

---

## REQ-094

**Source location:** Section 7.7 Engineering & Delivery — table row "Local-run runbook"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

### REQ-094-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-094-T01 |
| **Requirement ID** | REQ-094 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

**Purpose:** The local-run runbook exists at README.md.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate README.md at or near the path shown.

**Expected Result:** README.md exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: README.md exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: README.md exists.

### REQ-094-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-094-T02 |
| **Requirement ID** | REQ-094 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

**Purpose:** The runbook documents the single-command run and how to regenerate the traces and the eval.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read README.md.
2. Require a single-command run.
3. Require documented commands that regenerate the Phoenix traces and the evaluation.

**Expected Result:** The runbook documents the single-command run and both regeneration commands.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The runbook documents the single-command run and both regeneration commands.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The runbook documents the single-command run and both regeneration commands.

### REQ-094-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-094-T03 |
| **Requirement ID** | REQ-094 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

**Purpose:** The runbook's committed sample inputs exist.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the committed sample inputs the runbook relies on.

**Expected Result:** Committed sample inputs exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed sample inputs exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed sample inputs exist.

### REQ-094-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-094-T04 |
| **Requirement ID** | REQ-094 |
| **Test Type** | RUNTIME_TEST |
| **Executing suite** | `automated_tests/functional/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

**Purpose:** The documented command is backed by a real CLI entry point.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Discover the documented command.
2. Confirm a CLI entry point backs it.

**Expected Result:** The documented single command is backed by a real CLI entry point.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The documented single command is backed by a real CLI entry point.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The documented single command is backed by a real CLI entry point.

---
