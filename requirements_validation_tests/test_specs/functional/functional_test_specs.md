<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - functional

Generated: 2026-09-20T05:48:35Z

7 requirement(s), 20 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-043

**Source location:** Section 4. Technology & Framework Stack — table row "Interface" (continuation table)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Interface | CLI (required) · FastAPI streaming (optional / bonus)
~~~

### REQ-043-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-043-T01 |
| **Requirement ID** | REQ-043 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Interface | CLI (required) · FastAPI streaming (optional / bonus)
~~~

**Purpose:** A CLI interface exists, which the document marks as required.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for a CLI entry point: a console script, an argparse/click/typer parser, or a __main__ module.
2. Confirm the README documents how to invoke it.

**Expected Result:** A CLI entry point exists and is documented.

**Evidence Required:** The CLI entry point location and the documented invocation.

**Pass Condition:** Collected evidence satisfies: A CLI entry point exists and is documented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A CLI entry point exists and is documented.

### REQ-043-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-043-T02 |
| **Requirement ID** | REQ-043 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Interface | CLI (required) · FastAPI streaming (optional / bonus)
~~~

**Purpose:** The FastAPI streaming interface, which the document marks optional / bonus.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Look for the optional FastAPI streaming surface.
2. Record whether it is present; the document marks it optional / bonus, so its absence is not a defect of the required interface.

**Expected Result:** The optional FastAPI streaming surface is present (bonus).

**Evidence Required:** Presence or absence of the optional API surface.

**Pass Condition:** Collected evidence satisfies: The optional FastAPI streaming surface is present (bonus).

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The optional FastAPI streaming surface is present (bonus).

---

## REQ-048

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-05  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-05 | The copilot maintains context — it uses facts stated earlier in the interaction and recalls prior-session context on a return visit.
~~~

### REQ-048-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-048-T01 |
| **Requirement ID** | REQ-048 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-05 | The copilot maintains context — it uses facts stated earlier in the interaction and recalls prior-session context on a return visit.
~~~

**Purpose:** The copilot uses facts stated earlier in the interaction.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the memory package.
2. Confirm short-term conversational context is retained within an interaction.

**Expected Result:** Facts stated earlier in the interaction are retained and reused.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Facts stated earlier in the interaction are retained and reused.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Facts stated earlier in the interaction are retained and reused.

### REQ-048-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-048-T02 |
| **Requirement ID** | REQ-048 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-05 | The copilot maintains context — it uses facts stated earlier in the interaction and recalls prior-session context on a return visit.
~~~

**Purpose:** The copilot recalls prior-session context on a return visit.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the cross-session persistence test.
2. Locate its committed output log.
3. Confirm session-keyed persistence exists in the code.

**Expected Result:** Prior-session context is recalled on a return visit, evidenced by a committed test log.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Prior-session context is recalled on a return visit, evidenced by a committed test log.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Prior-session context is recalled on a return visit, evidenced by a committed test log.

---

## REQ-064

**Source location:** Section 6.1 In Scope — bullet 3  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

### REQ-064-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-064-T01 |
| **Requirement ID** | REQ-064 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

**Purpose:** A CLI exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the CLI entry point and its documented invocation.

**Expected Result:** A CLI entry point exists and is documented.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A CLI entry point exists and is documented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A CLI entry point exists and is documented.

### REQ-064-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-064-T02 |
| **Requirement ID** | REQ-064 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

**Purpose:** The CLI drives applications through the graph.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate where the CLI passes an application into the compiled graph.

**Expected Result:** The CLI drives applications through the graph.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The CLI drives applications through the graph.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The CLI drives applications through the graph.

### REQ-064-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-064-T03 |
| **Requirement ID** | REQ-064 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

**Purpose:** The CLI regenerates traces and the evaluation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read the documented commands.
2. Require documented commands that regenerate the traces and the evaluation.

**Expected Result:** The CLI regenerates the traces and the evaluation.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The CLI regenerates the traces and the evaluation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The CLI regenerates the traces and the evaluation.

---

## REQ-074

**Source location:** Section 7.1 Agentic System — Foundation — table row "Context engineering"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

### REQ-074-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-074-T01 |
| **Requirement ID** | REQ-074 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

**Purpose:** The context-engineering artifact exists at src/context/.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate src/context/ at or near the path shown.

**Expected Result:** src/context/ exists and is non-empty.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: src/context/ exists and is non-empty.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: src/context/ exists and is non-empty.

### REQ-074-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-074-T02 |
| **Requirement ID** | REQ-074 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

**Purpose:** Context engineering implements write, select, compress and isolate.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search src/context/ for each of the four operations the document names.

**Expected Result:** write, select, compress and isolate are all implemented.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: write, select, compress and isolate are all implemented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: write, select, compress and isolate are all implemented.

### REQ-074-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-074-T03 |
| **Requirement ID** | REQ-074 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

**Purpose:** Summarization middleware is present.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search src/context/ for summarization middleware.

**Expected Result:** Summarization middleware exists in the context layer.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Summarization middleware exists in the context layer.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Summarization middleware exists in the context layer.

### REQ-074-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-074-T04 |
| **Requirement ID** | REQ-074 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

**Purpose:** Untrusted text is quarantined in the context layer.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the quarantine of untrusted text.

**Expected Result:** Untrusted text is quarantined.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Untrusted text is quarantined.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Untrusted text is quarantined.

---

## REQ-075

**Source location:** Section 7.1 Agentic System — Foundation — table row "Tiered memory"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

### REQ-075-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-075-T01 |
| **Requirement ID** | REQ-075 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Purpose:** The tiered-memory artifact exists at src/memory/.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate src/memory/ at or near the path shown.

**Expected Result:** src/memory/ exists and is non-empty.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: src/memory/ exists and is non-empty.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: src/memory/ exists and is non-empty.

### REQ-075-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-075-T02 |
| **Requirement ID** | REQ-075 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Purpose:** The cross-session recall test exists at tests/test_memory_persistence.py.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate tests/test_memory_persistence.py at or near the path shown.

**Expected Result:** tests/test_memory_persistence.py exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: tests/test_memory_persistence.py exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: tests/test_memory_persistence.py exists.

### REQ-075-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-075-T03 |
| **Requirement ID** | REQ-075 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Purpose:** The committed output log exists at logs/memory_test.log.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate logs/memory_test.log.
2. Confirm git tracks it.

**Expected Result:** A committed output log from the memory test exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A committed output log from the memory test exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A committed output log from the memory test exists.

### REQ-075-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-075-T04 |
| **Requirement ID** | REQ-075 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Purpose:** Both short and long/semantic memory tiers exist.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for a short-term memory tier.
2. Search for a long/semantic memory tier.

**Expected Result:** Both memory tiers the document names exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both memory tiers the document names exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both memory tiers the document names exist.

### REQ-075-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-075-T05 |
| **Requirement ID** | REQ-075 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Purpose:** The cross-session recall test asserts recall across sessions.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the memory persistence test.
2. Require test functions, assertions, and cross-session subject matter.

**Expected Result:** The test asserts recall of prior-session context.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The test asserts recall of prior-session context.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The test asserts recall of prior-session context.

---

## REQ-095

**Source location:** Section 7.7 Engineering & Delivery — table row "Bonus"  
**Requirement class:** OPTIONAL

**Exact Original Requirement:**

~~~text
Bonus | src/api/ (FastAPI streaming) | OPTIONAL: async FastAPI streaming endpoint — extra credit, not required
~~~

### REQ-095-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-095-T01 |
| **Requirement ID** | REQ-095 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Bonus | src/api/ (FastAPI streaming) | OPTIONAL: async FastAPI streaming endpoint — extra credit, not required
~~~

**Purpose:** The optional FastAPI streaming endpoint at src/api/ - extra credit, not required.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Look for src/api/.
2. Record whether the optional bonus surface is present.
3. Confirm the required CLI interface is not displaced by it.

**Expected Result:** The optional FastAPI streaming endpoint is present as extra credit.

**Evidence Required:** Presence or absence of src/api/, and the state of the required CLI.

**Pass Condition:** Collected evidence satisfies: The optional FastAPI streaming endpoint is present as extra credit.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The optional FastAPI streaming endpoint is present as extra credit.

### REQ-095-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-095-T02 |
| **Requirement ID** | REQ-095 |
| **Test Type** | API_TEST |
| **Executing suite** | `automated_tests/api/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Bonus | src/api/ (FastAPI streaming) | OPTIONAL: async FastAPI streaming endpoint — extra credit, not required
~~~

**Purpose:** If present, the bonus endpoint is an async FastAPI streaming endpoint.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. If src/api/ exists, require fastapi to be declared and the endpoint to be async and streaming.
2. If it does not exist, the document marks it not required.

**Expected Result:** Either an async FastAPI streaming endpoint exists, or the optional surface is absent.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Either an async FastAPI streaming endpoint exists, or the optional surface is absent.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Either an async FastAPI streaming endpoint exists, or the optional surface is absent.

---

## REQ-109

**Source location:** Section 8.1 Good-to-Have — bullet 1  
**Requirement class:** OPTIONAL

**Exact Original Requirement:**

~~~text
FastAPI streaming endpoint; a demonstrated local run (screenshot/log).
~~~

### REQ-109-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-109-T01 |
| **Requirement ID** | REQ-109 |
| **Test Type** | API_TEST |
| **Executing suite** | `automated_tests/api/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
FastAPI streaming endpoint; a demonstrated local run (screenshot/log).
~~~

**Purpose:** A FastAPI streaming endpoint exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target). Runtime execution is enabled and the implementation documents a runnable command.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate src/api/.
2. Confirm fastapi is declared.
3. Confirm the endpoint is async and streaming.

**Expected Result:** An async FastAPI streaming endpoint exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An async FastAPI streaming endpoint exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An async FastAPI streaming endpoint exists.

### REQ-109-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-109-T02 |
| **Requirement ID** | REQ-109 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
FastAPI streaming endpoint; a demonstrated local run (screenshot/log).
~~~

**Purpose:** A demonstrated local run of the endpoint is committed as a screenshot or log.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. S
2. e
3. a
4. r
5. c
6. h
7.  
8. t
9. h
10. e
11.  
12. c
13. o
14. m
15. m
16. i
17. t
18. t
19. e
20. d
21.  
22. l
23. o
24. g
25. s
26.  
27. a
28. n
29. d
30.  
31. d
32. o
33. c
34. u
35. m
36. e
37. n
38. t
39. a
40. t
41. i
42. o
43. n
44.  
45. f
46. o
47. r
48.  
49. a
50.  
51. d
52. e
53. m
54. o
55. n
56. s
57. t
58. r
59. a
60. t
61. e
62. d
63.  
64. l
65. o
66. c
67. a
68. l
69.  
70. r
71. u
72. n
73.  
74. o
75. f
76.  
77. t
78. h
79. e
80.  
81. s
82. t
83. r
84. e
85. a
86. m
87. i
88. n
89. g
90.  
91. e
92. n
93. d
94. p
95. o
96. i
97. n
98. t
99. .

**Expected Result:** A screenshot or log demonstrating a local run is committed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A screenshot or log demonstrating a local run is committed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A screenshot or log demonstrating a local run is committed.

---
