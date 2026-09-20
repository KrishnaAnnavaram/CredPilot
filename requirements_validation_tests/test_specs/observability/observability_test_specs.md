<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - observability

Generated: 2026-09-20T05:48:35Z

19 requirement(s), 54 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-026

**Source location:** Section 3.3 Expected Solution — bullet 3  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

### REQ-026-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-026-T01 |
| **Requirement ID** | REQ-026 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

**Purpose:** Arize Phoenix instrumentation has a committed trace export.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the trace export in Parquet or JSONL form.
2. Confirm git tracks it.

**Expected Result:** A Phoenix trace export exists and is committed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A Phoenix trace export exists and is committed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A Phoenix trace export exists and is committed.

### REQ-026-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-026-T02 |
| **Requirement ID** | REQ-026 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

**Purpose:** A machine-generated tool-invocation log exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate logs/tool_calls.jsonl.
2. Locate the committed code that writes it, so it is machine-generated rather than hand-written.

**Expected Result:** The tool-invocation log exists and committed code produces it.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The tool-invocation log exists and committed code produces it.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The tool-invocation log exists and committed code produces it.

### REQ-026-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-026-T03 |
| **Requirement ID** | REQ-026 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

**Purpose:** An evidence-linked failure-mode analysis exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/failure-analysis.md.
2. Confirm it links to Phoenix evidence via run_id / span_id.

**Expected Result:** A failure-mode analysis exists and links to trace evidence.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A failure-mode analysis exists and links to trace evidence.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A failure-mode analysis exists and links to trace evidence.

---

## REQ-040

**Source location:** Section 4. Technology & Framework Stack — table row "Observability (mandated)"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

### REQ-040-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-040-T01 |
| **Requirement ID** | REQ-040 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

**Purpose:** Arize Phoenix provides the mandated observability.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm arize-phoenix is declared.
2. Confirm phoenix is imported.

**Expected Result:** Arize Phoenix is declared and imported.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Arize Phoenix is declared and imported.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Arize Phoenix is declared and imported.

### REQ-040-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-040-T02 |
| **Requirement ID** | REQ-040 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

**Purpose:** OpenTelemetry / openinference instrumentation is present.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm an openinference/OpenTelemetry package is declared.
2. Confirm it is imported.

**Expected Result:** OpenTelemetry / openinference instrumentation is declared and imported.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: OpenTelemetry / openinference instrumentation is declared and imported.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: OpenTelemetry / openinference instrumentation is declared and imported.

### REQ-040-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-040-T03 |
| **Requirement ID** | REQ-040 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

**Purpose:** Phoenix runs locally and in-process.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for a local in-process Phoenix session or the local Phoenix endpoint.

**Expected Result:** Phoenix is configured to run locally and in-process.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Phoenix is configured to run locally and in-process.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Phoenix is configured to run locally and in-process.

---

## REQ-050

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-07  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

### REQ-050-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-050-T01 |
| **Requirement ID** | REQ-050 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

**Purpose:** A tool-invocation log exists at logs/tool_calls.jsonl and parses.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate logs/tool_calls.jsonl.
2. Parse every line as JSON.
3. Require the per-call fields the document names.

**Expected Result:** logs/tool_calls.jsonl exists, parses, and carries the named per-call fields.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: logs/tool_calls.jsonl exists, parses, and carries the named per-call fields.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: logs/tool_calls.jsonl exists, parses, and carries the named per-call fields.

### REQ-050-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-050-T02 |
| **Requirement ID** | REQ-050 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

**Purpose:** The log is machine-generated by committed logging middleware.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search committed Python sources for the code that writes logs/tool_calls.jsonl.

**Expected Result:** Committed logging middleware produces the log; it is not hand-written.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed logging middleware produces the log; it is not hand-written.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed logging middleware produces the log; it is not hand-written.

### REQ-050-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-050-T03 |
| **Requirement ID** | REQ-050 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

**Purpose:** Tool names in the log reconcile with the agent/MCP code.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Collect every distinct tool_name in the log.
2. Require each to appear in the committed agent/MCP Python sources.

**Expected Result:** Every logged tool name reconciles with a name in the committed code.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every logged tool name reconciles with a name in the committed code.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every logged tool name reconciles with a name in the committed code.

---

## REQ-051

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-08  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-08 | docs/failure-analysis.md documents ≥ 3 real failures from your own runs, each citing the Phoenix run_id + span_id (or a tool-log record) that shows it, plus root cause and fix.
~~~

### REQ-051-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-051-T01 |
| **Requirement ID** | REQ-051 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-08 | docs/failure-analysis.md documents ≥ 3 real failures from your own runs, each citing the Phoenix run_id + span_id (or a tool-log record) that shows it, plus root cause and fix.
~~~

**Purpose:** docs/failure-analysis.md documents at least 3 real failures, each with evidence, cause and fix.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/failure-analysis.md.
2. Count the documented failures; require >= 3.
3. Require each to cite a Phoenix run_id + span_id, or a tool-log record.
4. Require a root cause and a fix for each.

**Expected Result:** At least 3 real failures are documented, each citing evidence plus root cause and fix.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: At least 3 real failures are documented, each citing evidence plus root cause and fix.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: At least 3 real failures are documented, each citing evidence plus root cause and fix.

### REQ-051-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-051-T02 |
| **Requirement ID** | REQ-051 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-08 | docs/failure-analysis.md documents ≥ 3 real failures from your own runs, each citing the Phoenix run_id + span_id (or a tool-log record) that shows it, plus root cause and fix.
~~~

**Purpose:** The citations in the failure analysis resolve to committed artifacts.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Extract the file-path citations from the committed documents.
2. Resolve each to a committed artifact.

**Expected Result:** Every citation resolves to a committed artifact.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every citation resolves to a committed artifact.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every citation resolves to a committed artifact.

---

## REQ-052

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-09  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

### REQ-052-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-052-T01 |
| **Requirement ID** | REQ-052 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

**Purpose:** The golden-signals report carries latency, tokens, cost, accuracy and hallucination rate.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate reports/golden_signals.json and parse it.
2. Require latency for thinking / acting / tool span types.
3. Require tokens, a cost estimate, accuracy and hallucination rate.

**Expected Result:** The golden-signals report carries every figure the criterion names.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The golden-signals report carries every figure the criterion names.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The golden-signals report carries every figure the criterion names.

### REQ-052-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-052-T02 |
| **Requirement ID** | REQ-052 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

**Purpose:** The report is Phoenix-derived.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the script that writes the report.
2. Confirm it reads the Phoenix spans.

**Expected Result:** The golden-signals report is derived from Phoenix spans by committed code.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The golden-signals report is derived from Phoenix spans by committed code.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The golden-signals report is derived from Phoenix spans by committed code.

### REQ-052-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-052-T03 |
| **Requirement ID** | REQ-052 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

**Purpose:** A cost/latency dashboard exists as a Phoenix screenshot plus its underlying data file.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate reports/dashboard.png and verify it is a real PNG.
2. Locate reports/dashboard_data.csv and verify it holds data rows.

**Expected Result:** Both the dashboard screenshot and the underlying data file exist and hold content.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both the dashboard screenshot and the underlying data file exist and hold content.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both the dashboard screenshot and the underlying data file exist and hold content.

---

## REQ-063

**Source location:** Section 6.1 In Scope — bullet 2  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

### REQ-063-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-063-T01 |
| **Requirement ID** | REQ-063 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Purpose:** Arize Phoenix tracing is in scope and delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the tracing module and a trace export.

**Expected Result:** Phoenix tracing and a trace export are delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Phoenix tracing and a trace export are delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Phoenix tracing and a trace export are delivered.

### REQ-063-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-063-T02 |
| **Requirement ID** | REQ-063 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Purpose:** Golden-signals plus cost/latency governance are delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the golden-signals report and the cost/latency data file.

**Expected Result:** Golden-signals and cost/latency governance artifacts are delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Golden-signals and cost/latency governance artifacts are delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Golden-signals and cost/latency governance artifacts are delivered.

### REQ-063-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-063-T03 |
| **Requirement ID** | REQ-063 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Purpose:** Guardrails plus audit plus secrets hygiene are delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrail package, the audit trail and the env-var template.

**Expected Result:** Guardrails, audit trail and secrets hygiene are delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Guardrails, audit trail and secrets hygiene are delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Guardrails, audit trail and secrets hygiene are delivered.

### REQ-063-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-063-T04 |
| **Requirement ID** | REQ-063 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Purpose:** Governance/compliance docs are delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the four governance documents.

**Expected Result:** All governance/compliance documents are delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All governance/compliance documents are delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All governance/compliance documents are delivered.

### REQ-063-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-063-T05 |
| **Requirement ID** | REQ-063 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Purpose:** Agent-level evaluation & tests are delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the evaluation report and the three agent tests.

**Expected Result:** Agent-level evaluation and tests are delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Agent-level evaluation and tests are delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Agent-level evaluation and tests are delivered.

---

## REQ-077

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Phoenix instrumentation"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

### REQ-077-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-077-T01 |
| **Requirement ID** | REQ-077 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

**Purpose:** The Phoenix instrumentation exists at src/observability/tracing.py.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate src/observability/tracing.py at or near the path shown.

**Expected Result:** src/observability/tracing.py exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: src/observability/tracing.py exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: src/observability/tracing.py exists.

### REQ-077-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-077-T02 |
| **Requirement ID** | REQ-077 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

**Purpose:** The Phoenix/openinference tracer is CALLED, not just imported.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Analyse the Python AST of the implementation.
2. Require a call that activates the tracer, not merely an import of it.

**Expected Result:** The tracer is invoked, satisfying 'called, not just imported'.

**Evidence Required:** The AST call site that activates the tracer.

**Pass Condition:** Collected evidence satisfies: The tracer is invoked, satisfying 'called, not just imported'.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The tracer is invoked, satisfying 'called, not just imported'.

### REQ-077-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-077-T03 |
| **Requirement ID** | REQ-077 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

**Purpose:** The tracer is wired into the run path.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the run path for a reference to the tracing module.

**Expected Result:** The run path activates tracing.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The run path activates tracing.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The run path activates tracing.

---

## REQ-078

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Trace export"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Trace export | traces/phoenix_spans.parquet (or .jsonl) | ≥1 full run; spans across multiple agents + every tool call; latencies present
~~~

### REQ-078-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-078-T01 |
| **Requirement ID** | REQ-078 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Trace export | traces/phoenix_spans.parquet (or .jsonl) | ≥1 full run; spans across multiple agents + every tool call; latencies present
~~~

**Purpose:** The trace export exists at traces/phoenix_spans.parquet (or .jsonl).

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate traces/phoenix_spans.parquet, or the .jsonl alternative the document permits.

**Expected Result:** A trace export exists in one of the two permitted formats.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A trace export exists in one of the two permitted formats.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A trace export exists in one of the two permitted formats.

### REQ-078-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-078-T02 |
| **Requirement ID** | REQ-078 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Trace export | traces/phoenix_spans.parquet (or .jsonl) | ≥1 full run; spans across multiple agents + every tool call; latencies present
~~~

**Purpose:** The export covers at least one full run, spans multiple agents and every tool call, and carries latencies.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Open the trace export.
2. Require at least one full run's spans.
3. Require spans across more than one agent/tool.
4. Require latency or duration data on the spans.

**Expected Result:** The export shows >= 1 full run, spans across multiple agents and every tool call, and latencies.

**Evidence Required:** Span count, distinct span names, and the latency column or key.

**Pass Condition:** Collected evidence satisfies: The export shows >= 1 full run, spans across multiple agents and every tool call, and latencies.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The export shows >= 1 full run, spans across multiple agents and every tool call, and latencies.

---

## REQ-079

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Tool-invocation log"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

### REQ-079-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-079-T01 |
| **Requirement ID** | REQ-079 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

**Purpose:** The tool-invocation log exists at logs/tool_calls.jsonl.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate logs/tool_calls.jsonl at or near the path shown.

**Expected Result:** logs/tool_calls.jsonl exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: logs/tool_calls.jsonl exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: logs/tool_calls.jsonl exists.

### REQ-079-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-079-T02 |
| **Requirement ID** | REQ-079 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

**Purpose:** Every per-call field the document names is present: timestamp, agent/node, tool_name, args, result, latency_ms, status.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse every record in the log.
2. Require each of the seven named per-call fields.

**Expected Result:** All seven per-call fields are present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All seven per-call fields are present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All seven per-call fields are present.

### REQ-079-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-079-T03 |
| **Requirement ID** | REQ-079 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

**Purpose:** The log is machine-generated.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the committed code that writes the log.

**Expected Result:** Committed code produces the log.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed code produces the log.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed code produces the log.

### REQ-079-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-079-T04 |
| **Requirement ID** | REQ-079 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

**Purpose:** Tool names in the log reconcile with the code.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Collect the distinct tool names from the log.
2. Require each to appear in the committed Python sources.

**Expected Result:** Every logged tool name reconciles with the code.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every logged tool name reconciles with the code.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every logged tool name reconciles with the code.

---

## REQ-080

**Source location:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Failure-mode analysis"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Failure-mode analysis | docs/failure-analysis.md | ≥3 real failures, EACH citing Phoenix run_id + span_id (or tool-log record) + root cause + fix
~~~

### REQ-080-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-080-T01 |
| **Requirement ID** | REQ-080 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Failure-mode analysis | docs/failure-analysis.md | ≥3 real failures, EACH citing Phoenix run_id + span_id (or tool-log record) + root cause + fix
~~~

**Purpose:** The failure-mode analysis exists at docs/failure-analysis.md.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/failure-analysis.md at or near the path shown.

**Expected Result:** docs/failure-analysis.md exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: docs/failure-analysis.md exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: docs/failure-analysis.md exists.

### REQ-080-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-080-T02 |
| **Requirement ID** | REQ-080 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Failure-mode analysis | docs/failure-analysis.md | ≥3 real failures, EACH citing Phoenix run_id + span_id (or tool-log record) + root cause + fix
~~~

**Purpose:** At least 3 real failures are documented, EACH citing run_id + span_id (or a tool-log record), plus root cause and fix.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Count the documented failures; require >= 3.
2. Require each to cite a Phoenix run_id + span_id, or a tool-log record.
3. Require a root cause and a fix for each.

**Expected Result:** Three or more failures, each fully evidenced with cause and fix.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Three or more failures, each fully evidenced with cause and fix.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Three or more failures, each fully evidenced with cause and fix.

---

## REQ-081

**Source location:** Section 7.3 Performance & Cost Governance — table row "Golden-signals report"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

### REQ-081-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-081-T01 |
| **Requirement ID** | REQ-081 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

**Purpose:** The golden-signals report exists at reports/golden_signals.json.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate reports/golden_signals.json at or near the path shown.

**Expected Result:** reports/golden_signals.json exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: reports/golden_signals.json exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: reports/golden_signals.json exists.

### REQ-081-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-081-T02 |
| **Requirement ID** | REQ-081 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

**Purpose:** A producing script accompanies the report.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the committed script that writes the report.

**Expected Result:** A committed producing script exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A committed producing script exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A committed producing script exists.

### REQ-081-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-081-T03 |
| **Requirement ID** | REQ-081 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

**Purpose:** The report carries Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate, accuracy and hallucination rate.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse the report.
2. Require latency for each of the thinking, acting and tool span types.
3. Require tokens, a cost estimate, accuracy and hallucination rate.

**Expected Result:** Every figure the row lists is present in the report.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every figure the row lists is present in the report.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every figure the row lists is present in the report.

---

## REQ-082

**Source location:** Section 7.3 Performance & Cost Governance — table row "Cost/latency dashboard"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Cost/latency dashboard | reports/dashboard.png + reports/dashboard_data.csv | Phoenix latency/cost/token dashboard screenshot AND the underlying data file it was drawn from
~~~

### REQ-082-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-082-T01 |
| **Requirement ID** | REQ-082 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Cost/latency dashboard | reports/dashboard.png + reports/dashboard_data.csv | Phoenix latency/cost/token dashboard screenshot AND the underlying data file it was drawn from
~~~

**Purpose:** The dashboard screenshot AND the underlying data file it was drawn from both exist.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate reports/dashboard.png and verify the PNG signature.
2. Locate reports/dashboard_data.csv and verify it holds data rows.

**Expected Result:** Both artifacts exist with real content - the row requires the screenshot AND the data file.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both artifacts exist with real content - the row requires the screenshot AND the data file.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both artifacts exist with real content - the row requires the screenshot AND the data file.

### REQ-082-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-082-T02 |
| **Requirement ID** | REQ-082 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Cost/latency dashboard | reports/dashboard.png + reports/dashboard_data.csv | Phoenix latency/cost/token dashboard screenshot AND the underlying data file it was drawn from
~~~

**Purpose:** The underlying data file is machine-exported.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the committed code that exports the dashboard data.

**Expected Result:** Committed code exports the dashboard data file.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Committed code exports the dashboard data file.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Committed code exports the dashboard data file.

---

## REQ-098

**Source location:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 3  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

### REQ-098-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-098-T01 |
| **Requirement ID** | REQ-098 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

**Purpose:** Arize Phoenix is enabled locally via the two packages the document names.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm arize-phoenix is a declared dependency.
2. Confirm openinference-instrumentation-langchain is a declared dependency.

**Expected Result:** Both packages the document names are declared.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both packages the document names are declared.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both packages the document names are declared.

### REQ-098-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-098-T02 |
| **Requirement ID** | REQ-098 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

**Purpose:** The Phoenix UI runs locally at localhost:6006.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation and its documentation for the local Phoenix endpoint.

**Expected Result:** The local Phoenix UI endpoint is configured or documented.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The local Phoenix UI endpoint is configured or documented.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The local Phoenix UI endpoint is configured or documented.

### REQ-098-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-098-T03 |
| **Requirement ID** | REQ-098 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

**Purpose:** Phoenix is the single source of the traces, latency, token and cost evidence.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the golden-signals report is derived from the Phoenix spans.
2. Confirm the dashboard data is derived from the Phoenix spans.

**Expected Result:** The latency, token and cost evidence all derive from Phoenix spans.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The latency, token and cost evidence all derive from Phoenix spans.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The latency, token and cost evidence all derive from Phoenix spans.

---

## REQ-099

**Source location:** Section 8. Producing the Evidence — table row "Phoenix trace export"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

### REQ-099-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-099-T01 |
| **Requirement ID** | REQ-099 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

**Purpose:** The Phoenix trace export is committed as Parquet or JSONL of OTel spans.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Verify the trace export is a real Parquet file, or a real JSONL of span objects.

**Expected Result:** The trace export is in one of the two stated formats.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The trace export is in one of the two stated formats.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The trace export is in one of the two stated formats.

### REQ-099-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-099-T02 |
| **Requirement ID** | REQ-099 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

**Purpose:** Phoenix tracing is turned on with openinference-instrumentation-langchain.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the instrumentation package is declared.
2. Confirm the implementation activates it.

**Expected Result:** Phoenix tracing is turned on via openinference-instrumentation-langchain.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Phoenix tracing is turned on via openinference-instrumentation-langchain.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Phoenix tracing is turned on via openinference-instrumentation-langchain.

### REQ-099-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-099-T03 |
| **Requirement ID** | REQ-099 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

**Purpose:** The export is produced by the method the document states.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the get_spans_dataframe() call the document specifies.
2. Search for the export of that dataframe to the trace file.

**Expected Result:** The export uses px.Client().get_spans_dataframe() written to the trace file.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The export uses px.Client().get_spans_dataframe() written to the trace file.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The export uses px.Client().get_spans_dataframe() written to the trace file.

### REQ-099-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-099-T04 |
| **Requirement ID** | REQ-099 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

**Purpose:** The export covers one full conversation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Open the trace export and require the spans of at least one full run.

**Expected Result:** The export contains one full conversation's spans.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The export contains one full conversation's spans.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The export contains one full conversation's spans.

---

## REQ-100

**Source location:** Section 8. Producing the Evidence — table row "Tool-invocation log"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

### REQ-100-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-100-T01 |
| **Requirement ID** | REQ-100 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

**Purpose:** The tool-invocation log is JSONL with one object per tool call.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Parse logs/tool_calls.jsonl line by line.
2. Require every line to be a single JSON object.

**Expected Result:** The log is JSONL with one object per tool call.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The log is JSONL with one object per tool call.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The log is JSONL with one object per tool call.

### REQ-100-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-100-T02 |
| **Requirement ID** | REQ-100 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

**Purpose:** Each object carries timestamp, agent, tool_name, args, result, latency_ms and status.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require each of the seven fields the document names in the log records.

**Expected Result:** All seven fields are present in the log records.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All seven fields are present in the log records.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All seven fields are present in the log records.

### REQ-100-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-100-T03 |
| **Requirement ID** | REQ-100 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

**Purpose:** A logging wrapper or decorator on the tools appends to the log.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the logging wrapper or decorator.
2. Confirm it appends to logs/tool_calls.jsonl.

**Expected Result:** A logging wrapper/decorator appends each tool call to the log.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A logging wrapper/decorator appends each tool call to the log.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A logging wrapper/decorator appends each tool call to the log.

---

## REQ-101

**Source location:** Section 8. Producing the Evidence — table row "Failure-mode analysis"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Failure-mode analysis | Markdown | Open your Phoenix traces, pick ≥ 3 real failures, write each up citing its run_id + span_id, with root cause and the fix.
~~~

### REQ-101-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-101-T01 |
| **Requirement ID** | REQ-101 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Failure-mode analysis | Markdown | Open your Phoenix traces, pick ≥ 3 real failures, write each up citing its run_id + span_id, with root cause and the fix.
~~~

**Purpose:** The failure-mode analysis is committed as Markdown.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/failure-analysis.md.
2. Confirm git tracks it.

**Expected Result:** A committed Markdown failure-mode analysis exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A committed Markdown failure-mode analysis exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A committed Markdown failure-mode analysis exists.

### REQ-101-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-101-T02 |
| **Requirement ID** | REQ-101 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Failure-mode analysis | Markdown | Open your Phoenix traces, pick ≥ 3 real failures, write each up citing its run_id + span_id, with root cause and the fix.
~~~

**Purpose:** At least 3 real failures from the Phoenix traces are written up with run_id + span_id, root cause and fix.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Count the documented failures; require >= 3.
2. Require each to cite its run_id and span_id.
3. Require the root cause and the fix for each.

**Expected Result:** Three or more trace-derived failures, each with its citation, cause and fix.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Three or more trace-derived failures, each with its citation, cause and fix.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Three or more trace-derived failures, each with its citation, cause and fix.

---

## REQ-102

**Source location:** Section 8. Producing the Evidence — table row "Golden-signals report"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

### REQ-102-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-102-T01 |
| **Requirement ID** | REQ-102 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

**Purpose:** The golden-signals report is committed as JSON.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm reports/golden_signals.json parses as JSON.

**Expected Result:** The golden-signals report is JSON.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The golden-signals report is JSON.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The golden-signals report is JSON.

### REQ-102-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-102-T02 |
| **Requirement ID** | REQ-102 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

**Purpose:** A script reads the Phoenix spans via get_spans_dataframe() and computes p50/p95 and cost = tokens x price.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require p50 and p95 latency figures in the report.
2. Locate the producing script.
3. Confirm it calls get_spans_dataframe().
4. Confirm it computes cost from tokens and a price.

**Expected Result:** The report is produced by a script that derives p50/p95 from Phoenix spans and computes cost as tokens x price.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The report is produced by a script that derives p50/p95 from Phoenix spans and computes cost as tokens x price.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The report is produced by a script that derives p50/p95 from Phoenix spans and computes cost as tokens x price.

### REQ-102-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-102-T03 |
| **Requirement ID** | REQ-102 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

**Purpose:** Latency is reported by span type (thinking / acting / tool) and token totals come from the LLM spans.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require latency for each of the thinking, acting and tool span types.
2. Require token totals.

**Expected Result:** Latency by span type and token totals are present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Latency by span type and token totals are present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Latency by span type and token totals are present.

### REQ-102-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-102-T04 |
| **Requirement ID** | REQ-102 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

**Purpose:** Accuracy and hallucination are imported from the eval report.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require accuracy and hallucination figures in the golden-signals report.
2. Require the eval report they are imported from to exist.

**Expected Result:** Accuracy and hallucination in the golden-signals report come from the eval report.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Accuracy and hallucination in the golden-signals report come from the eval report.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Accuracy and hallucination in the golden-signals report come from the eval report.

---

## REQ-103

**Source location:** Section 8. Producing the Evidence — table row "Cost/latency dashboard"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Cost/latency dashboard | PNG + CSV | Phoenix UI (localhost:6006) shows latency / cost / token dashboards — screenshot one; export the data with get_spans_dataframe().to_csv('reports/dashboard_data.csv').
~~~

### REQ-103-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-103-T01 |
| **Requirement ID** | REQ-103 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Cost/latency dashboard | PNG + CSV | Phoenix UI (localhost:6006) shows latency / cost / token dashboards — screenshot one; export the data with get_spans_dataframe().to_csv('reports/dashboard_data.csv').
~~~

**Purpose:** The cost/latency dashboard is committed as PNG + CSV.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Verify reports/dashboard.png is a real PNG.
2. Verify reports/dashboard_data.csv holds data rows.

**Expected Result:** A real PNG screenshot and a real CSV data file are both committed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A real PNG screenshot and a real CSV data file are both committed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A real PNG screenshot and a real CSV data file are both committed.

### REQ-103-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-103-T02 |
| **Requirement ID** | REQ-103 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Cost/latency dashboard | PNG + CSV | Phoenix UI (localhost:6006) shows latency / cost / token dashboards — screenshot one; export the data with get_spans_dataframe().to_csv('reports/dashboard_data.csv').
~~~

**Purpose:** The data is exported with get_spans_dataframe().to_csv('reports/dashboard_data.csv').

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for get_spans_dataframe().
2. Search for the to_csv export.
3. Confirm it targets reports/dashboard_data.csv.

**Expected Result:** The dashboard data is exported from the Phoenix spans by the stated method.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The dashboard data is exported from the Phoenix spans by the stated method.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The dashboard data is exported from the Phoenix spans by the stated method.

---

## REQ-111

**Source location:** Section 8.1 Good-to-Have — bullet 3  
**Requirement class:** OPTIONAL

**Exact Original Requirement:**

~~~text
An optimization note showing a measured before/after latency or cost improvement (two Phoenix-derived reports).
~~~

### REQ-111-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-111-T01 |
| **Requirement ID** | REQ-111 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
An optimization note showing a measured before/after latency or cost improvement (two Phoenix-derived reports).
~~~

**Purpose:** An optimization note shows a measured before/after latency or cost improvement from two Phoenix-derived reports.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the optimization note.
2. Confirm it states a measured before/after latency or cost figure.
3. Confirm two Phoenix-derived reports back it.

**Expected Result:** An optimization note is backed by two Phoenix-derived reports.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An optimization note is backed by two Phoenix-derived reports.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An optimization note is backed by two Phoenix-derived reports.

---
