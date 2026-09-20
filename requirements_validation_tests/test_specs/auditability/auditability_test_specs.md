<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - auditability

Generated: 2026-09-20T05:48:35Z

11 requirement(s), 25 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-015

**Source location:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Every claim is scored from committed evidence.
~~~

### REQ-015-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-015-T01 |
| **Requirement ID** | REQ-015 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Every claim is scored from committed evidence.
~~~

**Purpose:** Claims can be scored from committed evidence because the deliverable is a Git repository.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the implementation root is a Git repository.

**Expected Result:** The implementation is a Git repository, so its artifacts can be committed evidence.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The implementation is a Git repository, so its artifacts can be committed evidence.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The implementation is a Git repository, so its artifacts can be committed evidence.

### REQ-015-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-015-T02 |
| **Requirement ID** | REQ-015 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Every claim is scored from committed evidence.
~~~

**Purpose:** Every evidence artifact that exists on disk is committed, not merely present in a working tree.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Enumerate the evidence artifacts the source document names by path.
2. For each one present on disk, confirm 'git ls-files' lists it.
3. Report any artifact that exists but is uncommitted.

**Expected Result:** No evidence artifact exists uncommitted; every present artifact is git-tracked.

**Evidence Required:** For each artifact: its path and its presence or absence in 'git ls-files'.

**Pass Condition:** Collected evidence satisfies: No evidence artifact exists uncommitted; every present artifact is git-tracked.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No evidence artifact exists uncommitted; every present artifact is git-tracked.

---

## REQ-029

**Source location:** Section 3.4 Applicable Rules — bullet 1 (Evidence-in-Repo Rule)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Evidence-in-Repo Rule. Only committed artifacts are scored. A claim with no committed evidence scores zero; an evidence artifact with no producing code (a metric, trace or log a team could hand-write) is heavily discounted.
~~~

### REQ-029-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-029-T01 |
| **Requirement ID** | REQ-029 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evidence-in-Repo Rule. Only committed artifacts are scored. A claim with no committed evidence scores zero; an evidence artifact with no producing code (a metric, trace or log a team could hand-write) is heavily discounted.
~~~

**Purpose:** Only committed artifacts can be scored, so every named artifact present is committed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Enumerate the artifacts the source document names by path.
2. Confirm each present artifact is listed by 'git ls-files'.

**Expected Result:** No named artifact exists uncommitted.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No named artifact exists uncommitted.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No named artifact exists uncommitted.

### REQ-029-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-029-T02 |
| **Requirement ID** | REQ-029 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evidence-in-Repo Rule. Only committed artifacts are scored. A claim with no committed evidence scores zero; an evidence artifact with no producing code (a metric, trace or log a team could hand-write) is heavily discounted.
~~~

**Purpose:** Each evidence artifact has producing code, so it is not a hand-written metric, trace or log.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. For each machine-generated evidence artifact named by the document, search committed Python sources for code that writes it.
2. Report any artifact with no producing code.

**Expected Result:** Every evidence artifact has committed producing code.

**Evidence Required:** For each artifact: the producing source file and line, or a statement that none exists.

**Pass Condition:** Collected evidence satisfies: Every evidence artifact has committed producing code.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every evidence artifact has committed producing code.

---

## REQ-030

**Source location:** Section 3.4 Applicable Rules — bullet 2 (Citation-Resolves Rule)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Citation-Resolves Rule. Wherever a document cites evidence (a Phoenix run/span id, a log record, a control file), the citation must resolve to a committed artifact. Unresolvable citations are treated as missing.
~~~

### REQ-030-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-030-T01 |
| **Requirement ID** | REQ-030 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Citation-Resolves Rule. Wherever a document cites evidence (a Phoenix run/span id, a log record, a control file), the citation must resolve to a committed artifact. Unresolvable citations are treated as missing.
~~~

**Purpose:** Citations in the failure-mode analysis resolve to committed artifacts.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Extract every file-path citation from docs/failure-analysis.md.
2. Resolve each to a committed artifact.
3. Treat unresolvable citations as missing.

**Expected Result:** Every citation in the failure-mode analysis resolves to a committed artifact.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every citation in the failure-mode analysis resolves to a committed artifact.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every citation in the failure-mode analysis resolves to a committed artifact.

### REQ-030-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-030-T02 |
| **Requirement ID** | REQ-030 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Citation-Resolves Rule. Wherever a document cites evidence (a Phoenix run/span id, a log record, a control file), the citation must resolve to a committed artifact. Unresolvable citations are treated as missing.
~~~

**Purpose:** Citations in the governance pack resolve to committed artifacts.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Extract file-path citations from each governance document.
2. Resolve each citation to a committed artifact.

**Expected Result:** Every citation in each of the four governance documents resolves to a committed artifact.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every citation in each of the four governance documents resolves to a committed artifact.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every citation in each of the four governance documents resolves to a committed artifact.

---

## REQ-053

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-10  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-10 | Input/output guardrails wired into the agent's I/O path, and a machine-generated audit trail of agent actions (logs/agent_actions.jsonl).
~~~

### REQ-053-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-053-T01 |
| **Requirement ID** | REQ-053 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-10 | Input/output guardrails wired into the agent's I/O path, and a machine-generated audit trail of agent actions (logs/agent_actions.jsonl).
~~~

**Purpose:** Input/output guardrails are wired into the agent's I/O path.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrail package.
2. Require an input guardrail and an output guardrail.
3. Require blocking or sanitizing behaviour.
4. Require a module outside the guardrail package to call into it.

**Expected Result:** Input and output guardrails exist and are wired into the agent's I/O path.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Input and output guardrails exist and are wired into the agent's I/O path.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Input and output guardrails exist and are wired into the agent's I/O path.

### REQ-053-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-053-T02 |
| **Requirement ID** | REQ-053 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-10 | Input/output guardrails wired into the agent's I/O path, and a machine-generated audit trail of agent actions (logs/agent_actions.jsonl).
~~~

**Purpose:** A machine-generated audit trail of agent actions exists at logs/agent_actions.jsonl.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate logs/agent_actions.jsonl and parse it.
2. Require the actor, action, tool, decision and timestamp fields.
3. Require committed middleware that writes it.

**Expected Result:** A machine-generated audit trail exists with the named fields.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A machine-generated audit trail exists with the named fields.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A machine-generated audit trail exists with the named fields.

---

## REQ-061

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-06  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
NFR-06 | Evidence artifacts (traces, logs, reports) are machine-generated by committed code; the code that produced each is committed alongside it.
~~~

### REQ-061-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-061-T01 |
| **Requirement ID** | REQ-061 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-06 | Evidence artifacts (traces, logs, reports) are machine-generated by committed code; the code that produced each is committed alongside it.
~~~

**Purpose:** Traces, logs and reports are machine-generated by committed code.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. F
2. o
3. r
4.  
5. e
6. a
7. c
8. h
9.  
10. e
11. v
12. i
13. d
14. e
15. n
16. c
17. e
18.  
19. a
20. r
21. t
22. i
23. f
24. a
25. c
26. t
27.  
28. p
29. r
30. e
31. s
32. e
33. n
34. t
35. ,
36.  
37. s
38. e
39. a
40. r
41. c
42. h
43.  
44. c
45. o
46. m
47. m
48. i
49. t
50. t
51. e
52. d
53.  
54. P
55. y
56. t
57. h
58. o
59. n
60.  
61. s
62. o
63. u
64. r
65. c
66. e
67. s
68.  
69. f
70. o
71. r
72.  
73. t
74. h
75. e
76.  
77. c
78. o
79. d
80. e
81.  
82. t
83. h
84. a
85. t
86.  
87. w
88. r
89. i
90. t
91. e
92. s
93.  
94. i
95. t
96. .

**Expected Result:** Every present evidence artifact has committed producing code.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every present evidence artifact has committed producing code.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every present evidence artifact has committed producing code.

### REQ-061-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-061-T02 |
| **Requirement ID** | REQ-061 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-06 | Evidence artifacts (traces, logs, reports) are machine-generated by committed code; the code that produced each is committed alongside it.
~~~

**Purpose:** The producing code is committed alongside the artifact it produced.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm each evidence artifact is git-tracked.
2. Confirm its producing code is also git-tracked.

**Expected Result:** Each evidence artifact and the code that produced it are both committed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Each evidence artifact and the code that produced it are both committed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Each evidence artifact and the code that produced it are both committed.

---

## REQ-070

**Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Each artifact must be present at (or near) the path shown and contain what is listed.
~~~

### REQ-070-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-070-T01 |
| **Requirement ID** | REQ-070 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Each artifact must be present at (or near) the path shown and contain what is listed.
~~~

**Purpose:** Each artifact is present at (or near) the path shown.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. For each artifact the checklist names, look for it at its exact path.
2. If absent, look for the same filename elsewhere in the tree ('or near').
3. Report each as exact, near, or absent.

**Expected Result:** Every checklist artifact is present at or near the path shown.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every checklist artifact is present at or near the path shown.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every checklist artifact is present at or near the path shown.

### REQ-070-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-070-T02 |
| **Requirement ID** | REQ-070 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Each artifact must be present at (or near) the path shown and contain what is listed.
~~~

**Purpose:** Each present artifact contains what is listed rather than being an empty placeholder.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. For each present checklist artifact, require non-zero content.
2. Parse JSON and JSONL artifacts and require valid records.

**Expected Result:** No present checklist artifact is empty or malformed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No present checklist artifact is empty or malformed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No present checklist artifact is empty or malformed.

---

## REQ-071

**Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 3  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Remember the Evidence-in-Repo and Citation-Resolves rules: outputs must be produced by committed code, and every citation must resolve to a committed artifact.
~~~

### REQ-071-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-071-T01 |
| **Requirement ID** | REQ-071 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Remember the Evidence-in-Repo and Citation-Resolves rules: outputs must be produced by committed code, and every citation must resolve to a committed artifact.
~~~

**Purpose:** Outputs are produced by committed code.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. For each evidence artifact present, locate the committed code that writes it.

**Expected Result:** Every output is produced by committed code.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every output is produced by committed code.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every output is produced by committed code.

### REQ-071-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-071-T02 |
| **Requirement ID** | REQ-071 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Remember the Evidence-in-Repo and Citation-Resolves rules: outputs must be produced by committed code, and every citation must resolve to a committed artifact.
~~~

**Purpose:** Every citation resolves to a committed artifact.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Extract every file-path citation from every committed document.
2. Resolve each to a committed artifact.

**Expected Result:** Every citation resolves to a committed artifact.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every citation resolves to a committed artifact.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every citation resolves to a committed artifact.

---

## REQ-084

**Source location:** Section 7.4 Security & Guardrails — table row "Audit trail"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

### REQ-084-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-084-T01 |
| **Requirement ID** | REQ-084 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

**Purpose:** The audit trail exists at logs/agent_actions.jsonl.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate logs/agent_actions.jsonl at or near the path shown.

**Expected Result:** logs/agent_actions.jsonl exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: logs/agent_actions.jsonl exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: logs/agent_actions.jsonl exists.

### REQ-084-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-084-T02 |
| **Requirement ID** | REQ-084 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

**Purpose:** Audit middleware machine-generates records carrying actor, action, tool, decision and timestamp.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse the audit trail.
2. Require the five named fields.
3. Require committed audit middleware that writes it.

**Expected Result:** Machine-generated audit records with all five named fields.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Machine-generated audit records with all five named fields.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Machine-generated audit records with all five named fields.

### REQ-084-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-084-T03 |
| **Requirement ID** | REQ-084 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

**Purpose:** Consequential actions are what the audit trail records.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate where the audit middleware is invoked on the agent's consequential actions.

**Expected Result:** The audit middleware is invoked for consequential actions.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The audit middleware is invoked for consequential actions.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The audit middleware is invoked for consequential actions.

---

## REQ-096

**Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 1  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

### REQ-096-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-096-T01 |
| **Requirement ID** | REQ-096 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

**Purpose:** Every evidence artifact is produced by committed code.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. For each evidence artifact present, search the committed Python sources for the code that writes it.
2. Report any artifact with no producing code.

**Expected Result:** Every evidence artifact present has committed producing code.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every evidence artifact present has committed producing code.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every evidence artifact present has committed producing code.

### REQ-096-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-096-T02 |
| **Requirement ID** | REQ-096 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

**Purpose:** Every evidence artifact is committed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. For each named artifact present on disk, confirm 'git ls-files' lists it.

**Expected Result:** Every present evidence artifact is committed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every present evidence artifact is committed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every present evidence artifact is committed.

### REQ-096-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-096-T03 |
| **Requirement ID** | REQ-096 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

**Purpose:** Every evidence artifact is committed in the format the table shows.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. F
2. o
3. r
4.  
5. e
6. a
7. c
8. h
9.  
10. a
11. r
12. t
13. i
14. f
15. a
16. c
17. t
18.  
19. i
20. n
21.  
22. t
23. h
24. e
25.  
26. S
27. e
28. c
29. t
30. i
31. o
32. n
33.  
34. 8
35.  
36. t
37. a
38. b
39. l
40. e
41. ,
42.  
43. v
44. e
45. r
46. i
47. f
48. y
49.  
50. t
51. h
52. e
53.  
54. c
55. o
56. m
57. m
58. i
59. t
60. t
61. e
62. d
63.  
64. f
65. i
66. l
67. e
68.  
69. r
70. e
71. a
72. l
73. l
74. y
75.  
76. i
77. s
78.  
79. i
80. n
81.  
82. t
83. h
84. e
85.  
86. s
87. t
88. a
89. t
90. e
91. d
92.  
93. f
94. o
95. r
96. m
97. a
98. t
99. :
100.  
101. P
102. a
103. r
104. q
105. u
106. e
107. t
108.  
109. m
110. a
111. g
112. i
113. c
114.  
115. b
116. y
117. t
118. e
119. s
120. ,
121.  
122. o
123. n
124. e
125.  
126. J
127. S
128. O
129. N
130.  
131. o
132. b
133. j
134. e
135. c
136. t
137.  
138. p
139. e
140. r
141.  
142. J
143. S
144. O
145. N
146. L
147.  
148. l
149. i
150. n
151. e
152. ,
153.  
154. p
155. a
156. r
157. s
158. e
159. a
160. b
161. l
162. e
163.  
164. J
165. S
166. O
167. N
168. ,
169.  
170. P
171. N
172. G
173.  
174. s
175. i
176. g
177. n
178. a
179. t
180. u
181. r
182. e
183. ,
184.  
185. C
186. S
187. V
188.  
189. w
190. i
191. t
192. h
193.  
194. d
195. a
196. t
197. a
198.  
199. r
200. o
201. w
202. s
203. ,
204.  
205. M
206. a
207. r
208. k
209. d
210. o
211. w
212. n
213. .

**Expected Result:** Every evidence artifact is in the format the table states.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every evidence artifact is in the format the table states.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every evidence artifact is in the format the table states.

---

## REQ-097

**Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

### REQ-097-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-097-T01 |
| **Requirement ID** | REQ-097 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

**Purpose:** Observability is a concrete file that is generated, not a slide.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the generated observability files.
2. Confirm committed code generates them.

**Expected Result:** Observability exists as concrete generated files.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Observability exists as concrete generated files.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Observability exists as concrete generated files.

### REQ-097-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-097-T02 |
| **Requirement ID** | REQ-097 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

**Purpose:** Cost governance is a concrete file that is generated, not a slide.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the generated cost-governance files.
2. Confirm committed code generates them.

**Expected Result:** Cost governance exists as concrete generated files.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Cost governance exists as concrete generated files.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Cost governance exists as concrete generated files.

### REQ-097-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-097-T03 |
| **Requirement ID** | REQ-097 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

**Purpose:** No slide deck stands in for the generated evidence.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the repository for slide-deck files.

**Expected Result:** No slide deck is committed in place of the generated evidence files.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No slide deck is committed in place of the generated evidence files.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No slide deck is committed in place of the generated evidence files.

---

## REQ-105

**Source location:** Section 8. Producing the Evidence — table row "Audit trail"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Audit trail | JSONL | Audit middleware that appends {actor, action, tool, decision, timestamp} for each consequential action to logs/agent_actions.jsonl.
~~~

### REQ-105-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-105-T01 |
| **Requirement ID** | REQ-105 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Audit trail | JSONL | Audit middleware that appends {actor, action, tool, decision, timestamp} for each consequential action to logs/agent_actions.jsonl.
~~~

**Purpose:** The audit trail is committed as JSONL.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse logs/agent_actions.jsonl and require valid JSON objects.

**Expected Result:** The audit trail is valid JSONL.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The audit trail is valid JSONL.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The audit trail is valid JSONL.

### REQ-105-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-105-T02 |
| **Requirement ID** | REQ-105 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Audit trail | JSONL | Audit middleware that appends {actor, action, tool, decision, timestamp} for each consequential action to logs/agent_actions.jsonl.
~~~

**Purpose:** Audit middleware appends actor, action, tool, decision and timestamp for each consequential action.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require the five named fields on the audit records.
2. Require committed audit middleware that appends them.

**Expected Result:** Audit middleware appends all five named fields per consequential action.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Audit middleware appends all five named fields per consequential action.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Audit middleware appends all five named fields per consequential action.

---
