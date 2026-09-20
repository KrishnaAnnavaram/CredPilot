"""
Test cases for REQ-096 .. REQ-112.

Covers Section 8, "Producing the Evidence - Format & Where to Obtain", its continuation
table, Section 8.1 Good-to-Have, and the document's closing paragraph.

Section 8 states, for each artifact, BOTH the format it must be committed in AND the tool
or method that must generate it. Both halves are tested: an artifact in the right format
with no producing method is exactly the hand-written evidence the Evidence-in-Repo Rule
discounts.
"""

from __future__ import annotations

import bootstrap  # noqa: F401
from evidence_validator import (
    all_of,
    any_of,
    binary_artifact,
    committed,
    csv_has_rows,
    dependency_declared,
    dir_exists,
    file_contains,
    file_exists,
    jsonl_records,
    no_files_matching,
    tree_contains,
)
from requirement_validator import TestCase
from response_validator import artifact_has_producing_code

from ._artifact_checks import (
    all_citations_resolve,
    audit_trail_records,
    eval_report_content,
    golden_signals_content,
    golden_signals_percentiles,
    guardrails_wired,
    tool_call_log_fields,
    two_phoenix_reports,
)
from ._helpers import T
from ._shared_checks import (
    all_named_evidence_committed,
    dashboard_pair,
    evidence_artifacts_have_producers,
    failure_analysis_content,
    masking_present,
    pytest_module_asserts,
    readme_documents_single_command,
    trace_export_content,
)

PY = (".py",)
DOCS = (".md",)

CASES: list[TestCase] = []
add = CASES.append


# ======================================================================================
# Section 8 lead-in (REQ-096 .. REQ-098)
# ======================================================================================

add(T(
    "REQ-096-T01", "REQ-096", "Every evidence artifact is produced by committed code.",
    evidence_artifacts_have_producers,
    test_type="AUDITABILITY_TEST",
    steps=("For each evidence artifact present, search the committed Python sources for the code "
           "that writes it.",
           "Report any artifact with no producing code."),
    expected="Every evidence artifact present has committed producing code.",
    weight=3,
))

add(T(
    "REQ-096-T02", "REQ-096", "Every evidence artifact is committed.",
    all_named_evidence_committed,
    test_type="AUDITABILITY_TEST",
    steps=("For each named artifact present on disk, confirm 'git ls-files' lists it.",),
    expected="Every present evidence artifact is committed.",
    weight=2,
))

add(T(
    "REQ-096-T03", "REQ-096",
    "Every evidence artifact is committed in the format the table shows.",
    all_of("artifacts in their stated formats",
           any_of("Phoenix trace export as Parquet or JSONL of OTel spans",
                  binary_artifact("traces/phoenix_spans.parquet", 1, b"PAR1", "Parquet trace export"),
                  jsonl_records("traces/phoenix_spans.jsonl", [], 1, "JSONL trace export")),
           jsonl_records("logs/tool_calls.jsonl", [], 1, "tool-invocation log as JSONL"),
           file_exists("docs/failure-analysis.md"),
           file_contains("reports/golden_signals.json", [r"^\s*[\{\[]"],
                         "golden-signals report as JSON"),
           binary_artifact("reports/dashboard.png", 1, b"\x89PNG\r\n\x1a\n", "dashboard as PNG"),
           csv_has_rows("reports/dashboard_data.csv", 1, "dashboard data as CSV"),
           jsonl_records("logs/agent_actions.jsonl", [], 1, "audit trail as JSONL"),
           file_contains("reports/eval_report.json", [r"^\s*[\{\[]"],
                         "evaluation report as JSON")),
    test_type="DATA_VALIDATION_TEST",
    steps=("For each artifact in the Section 8 table, verify the committed file really is in the "
           "stated format: Parquet magic bytes, one JSON object per JSONL line, parseable JSON, "
           "PNG signature, CSV with data rows, Markdown."),
    expected="Every evidence artifact is in the format the table states.",
    weight=3,
))

add(T(
    "REQ-097-T01", "REQ-097",
    "Observability is a concrete file that is generated, not a slide.",
    all_of("observability as generated files",
           any_of("a trace export",
                  file_exists("traces/phoenix_spans.parquet"),
                  file_exists("traces/phoenix_spans.jsonl")),
           artifact_has_producing_code("logs/tool_calls.jsonl", [r"tool_calls\.jsonl"],
                                       "generated tool-invocation log")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the generated observability files.",
           "Confirm committed code generates them."),
    expected="Observability exists as concrete generated files.",
    weight=2,
))

add(T(
    "REQ-097-T02", "REQ-097",
    "Cost governance is a concrete file that is generated, not a slide.",
    all_of("cost governance as generated files",
           artifact_has_producing_code("reports/golden_signals.json", [r"golden_signals\.json"],
                                       "generated golden-signals report"),
           artifact_has_producing_code("reports/dashboard_data.csv",
                                       [r"dashboard_data\.csv", r"to_csv\("],
                                       "generated dashboard data")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the generated cost-governance files.",
           "Confirm committed code generates them."),
    expected="Cost governance exists as concrete generated files.",
    weight=2,
))

add(T(
    "REQ-097-T03", "REQ-097",
    "No slide deck stands in for the generated evidence.",
    no_files_matching(["*.pptx", "*.ppt", "*.key", "*.odp"],
                      "slide decks substituted for generated evidence"),
    test_type="NEGATIVE_TEST",
    steps=("Scan the repository for slide-deck files.",),
    expected="No slide deck is committed in place of the generated evidence files.",
))

add(T(
    "REQ-098-T01", "REQ-098",
    "Arize Phoenix is enabled locally via the two packages the document names.",
    all_of("arize-phoenix and openinference-instrumentation-langchain",
           dependency_declared(["arize-phoenix"], "arize-phoenix declared"),
           dependency_declared(["openinference-instrumentation-langchain"],
                               "openinference-instrumentation-langchain declared")),
    test_type="CONFIGURATION_TEST",
    steps=("Confirm arize-phoenix is a declared dependency.",
           "Confirm openinference-instrumentation-langchain is a declared dependency."),
    expected="Both packages the document names are declared.",
    weight=2,
))

add(T(
    "REQ-098-T02", "REQ-098", "The Phoenix UI runs locally at localhost:6006.",
    tree_contains([r"localhost:6006|127\.0\.0\.1:6006|:6006"],
                  "the local Phoenix UI endpoint", (".py", ".md", ".env", ".example", ".yaml")),
    test_type="CONFIGURATION_TEST",
    steps=("Search the implementation and its documentation for the local Phoenix endpoint.",),
    expected="The local Phoenix UI endpoint is configured or documented.",
))

add(T(
    "REQ-098-T03", "REQ-098",
    "Phoenix is the single source of the traces, latency, token and cost evidence.",
    all_of("Phoenix as the single evidence source",
           artifact_has_producing_code("reports/golden_signals.json", [r"get_spans_dataframe"],
                                       "golden signals derived from Phoenix spans"),
           artifact_has_producing_code("reports/dashboard_data.csv", [r"get_spans_dataframe"],
                                       "dashboard data derived from Phoenix spans")),
    test_type="OBSERVABILITY_TEST",
    steps=("Confirm the golden-signals report is derived from the Phoenix spans.",
           "Confirm the dashboard data is derived from the Phoenix spans."),
    expected="The latency, token and cost evidence all derive from Phoenix spans.",
    weight=3,
))


# ======================================================================================
# Section 8 table (REQ-099 .. REQ-108)
# ======================================================================================

add(T(
    "REQ-099-T01", "REQ-099",
    "The Phoenix trace export is committed as Parquet or JSONL of OTel spans.",
    any_of("Parquet or JSONL of OTel spans",
           binary_artifact("traces/phoenix_spans.parquet", 1, b"PAR1", "Parquet span export"),
           jsonl_records("traces/phoenix_spans.jsonl", [], 1, "JSONL span export")),
    test_type="DATA_VALIDATION_TEST",
    steps=("Verify the trace export is a real Parquet file, or a real JSONL of span objects.",),
    expected="The trace export is in one of the two stated formats.",
    weight=2,
))

add(T(
    "REQ-099-T02", "REQ-099",
    "Phoenix tracing is turned on with openinference-instrumentation-langchain.",
    all_of("openinference-instrumentation-langchain tracing",
           dependency_declared(["openinference-instrumentation-langchain"],
                               "openinference-instrumentation-langchain declared"),
           tree_contains([r"openinference"], "openinference instrumentation activated", PY)),
    test_type="OBSERVABILITY_TEST",
    steps=("Confirm the instrumentation package is declared.",
           "Confirm the implementation activates it."),
    expected="Phoenix tracing is turned on via openinference-instrumentation-langchain.",
    weight=2,
))

add(T(
    "REQ-099-T03", "REQ-099",
    "The export is produced by the method the document states.",
    all_of("the stated export method",
           tree_contains([r"get_spans_dataframe"], "px.Client().get_spans_dataframe()", PY),
           tree_contains([r"to_parquet|to_json"], "the span dataframe exported to file", PY)),
    test_type="AUDITABILITY_TEST",
    steps=("Search for the get_spans_dataframe() call the document specifies.",
           "Search for the export of that dataframe to the trace file."),
    expected="The export uses px.Client().get_spans_dataframe() written to the trace file.",
    weight=2,
))

add(T(
    "REQ-099-T04", "REQ-099",
    "The export covers one full conversation.",
    trace_export_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Open the trace export and require the spans of at least one full run.",),
    expected="The export contains one full conversation's spans.",
    weight=2,
))

add(T(
    "REQ-100-T01", "REQ-100",
    "The tool-invocation log is JSONL with one object per tool call.",
    jsonl_records("logs/tool_calls.jsonl", [], 1, "one JSON object per tool call"),
    test_type="DATA_VALIDATION_TEST",
    steps=("Parse logs/tool_calls.jsonl line by line.",
           "Require every line to be a single JSON object."),
    expected="The log is JSONL with one object per tool call.",
    weight=2,
))

add(T(
    "REQ-100-T02", "REQ-100",
    "Each object carries timestamp, agent, tool_name, args, result, latency_ms and status.",
    tool_call_log_fields,
    test_type="DATA_VALIDATION_TEST",
    steps=("Require each of the seven fields the document names in the log records.",),
    expected="All seven fields are present in the log records.",
    weight=3,
))

add(T(
    "REQ-100-T03", "REQ-100",
    "A logging wrapper or decorator on the tools appends to the log.",
    all_of("a logging wrapper/decorator",
           tree_contains([r"def\s+\w*log\w*\(|@\w*log\w*|functools\.wraps|def\s+wrapper"],
                         "a logging wrapper or decorator", PY),
           tree_contains([r"tool_calls\.jsonl"], "appending to logs/tool_calls.jsonl", PY)),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the logging wrapper or decorator.",
           "Confirm it appends to logs/tool_calls.jsonl."),
    expected="A logging wrapper/decorator appends each tool call to the log.",
    weight=2,
))

add(T(
    "REQ-101-T01", "REQ-101", "The failure-mode analysis is committed as Markdown.",
    all_of("Markdown failure-mode analysis",
           file_exists("docs/failure-analysis.md"),
           committed("docs/failure-analysis.md")),
    test_type="DATA_VALIDATION_TEST",
    steps=("Locate docs/failure-analysis.md.", "Confirm git tracks it."),
    expected="A committed Markdown failure-mode analysis exists.",
))

add(T(
    "REQ-101-T02", "REQ-101",
    "At least 3 real failures from the Phoenix traces are written up with run_id + span_id, root cause and fix.",
    failure_analysis_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Count the documented failures; require >= 3.",
           "Require each to cite its run_id and span_id.",
           "Require the root cause and the fix for each."),
    expected="Three or more trace-derived failures, each with its citation, cause and fix.",
    weight=3,
))

add(T(
    "REQ-102-T01", "REQ-102", "The golden-signals report is committed as JSON.",
    file_contains("reports/golden_signals.json", [r"^\s*[\{\[]"], "valid JSON report"),
    test_type="DATA_VALIDATION_TEST",
    steps=("Confirm reports/golden_signals.json parses as JSON.",),
    expected="The golden-signals report is JSON.",
))

add(T(
    "REQ-102-T02", "REQ-102",
    "A script reads the Phoenix spans via get_spans_dataframe() and computes p50/p95 and cost = tokens x price.",
    golden_signals_percentiles,
    test_type="OBSERVABILITY_TEST",
    steps=("Require p50 and p95 latency figures in the report.",
           "Locate the producing script.",
           "Confirm it calls get_spans_dataframe().",
           "Confirm it computes cost from tokens and a price."),
    expected="The report is produced by a script that derives p50/p95 from Phoenix spans and "
             "computes cost as tokens x price.",
    weight=3,
))

add(T(
    "REQ-102-T03", "REQ-102",
    "Latency is reported by span type (thinking / acting / tool) and token totals come from the LLM spans.",
    golden_signals_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Require latency for each of the thinking, acting and tool span types.",
           "Require token totals."),
    expected="Latency by span type and token totals are present.",
    weight=2,
))

add(T(
    "REQ-102-T04", "REQ-102",
    "Accuracy and hallucination are imported from the eval report.",
    all_of("accuracy and hallucination imported from the eval report",
           golden_signals_content,
           file_exists("reports/eval_report.json")),
    test_type="OBSERVABILITY_TEST",
    steps=("Require accuracy and hallucination figures in the golden-signals report.",
           "Require the eval report they are imported from to exist."),
    expected="Accuracy and hallucination in the golden-signals report come from the eval report.",
    weight=2,
))

add(T(
    "REQ-103-T01", "REQ-103", "The cost/latency dashboard is committed as PNG + CSV.",
    dashboard_pair,
    test_type="DATA_VALIDATION_TEST",
    steps=("Verify reports/dashboard.png is a real PNG.",
           "Verify reports/dashboard_data.csv holds data rows."),
    expected="A real PNG screenshot and a real CSV data file are both committed.",
    weight=3,
))

add(T(
    "REQ-103-T02", "REQ-103",
    "The data is exported with get_spans_dataframe().to_csv('reports/dashboard_data.csv').",
    all_of("the stated CSV export method",
           tree_contains([r"get_spans_dataframe"], "the Phoenix spans dataframe", PY),
           tree_contains([r"to_csv\("], "the to_csv export", PY),
           tree_contains([r"dashboard_data\.csv"], "the dashboard data target path", PY)),
    test_type="AUDITABILITY_TEST",
    steps=("Search for get_spans_dataframe().", "Search for the to_csv export.",
           "Confirm it targets reports/dashboard_data.csv."),
    expected="The dashboard data is exported from the Phoenix spans by the stated method.",
    weight=2,
))

add(T(
    "REQ-104-T01", "REQ-104", "The guardrail code is a Python module.",
    all_of("guardrail Python module",
           dir_exists("src/guardrails"),
           tree_contains([r"def\s+\w+|class\s+\w+"], "Python definitions in the guardrail module",
                         PY, under="src/guardrails")),
    test_type="STATIC_TEST",
    steps=("Locate the guardrail package.", "Confirm it contains Python definitions.",),
    expected="The guardrail code is a real Python module.",
))

add(T(
    "REQ-104-T02", "REQ-104",
    "Guardrails-AI / LLM Guard validators, or policy functions, wrap the agent's input and output.",
    all_of("validators or policy functions wrapping input and output",
           any_of("Guardrails-AI, LLM Guard, or policy functions",
                  dependency_declared(["guardrails-ai"], "guardrails-ai declared"),
                  dependency_declared(["llm-guard"], "llm-guard declared"),
                  tree_contains([r"def\s+\w*polic\w*|def\s+\w*validat\w*"],
                                "policy/validator functions", PY, under="src/guardrails")),
           guardrails_wired),
    test_type="SECURITY_TEST",
    steps=("Require Guardrails-AI, LLM Guard, or policy functions - the document permits any.",
           "Require them to wrap both the input and the output."),
    expected="Validators or policy functions wrap the agent's input and output.",
    weight=3,
))

add(T(
    "REQ-104-T03", "REQ-104", "The guardrails are wired into the graph's I/O nodes.",
    all_of("wired into the graph's I/O nodes",
           guardrails_wired,
           tree_contains([r"guardrail"], "the graph referencing the guardrail layer", PY)),
    test_type="ARCHITECTURE_TEST",
    steps=("Confirm the graph references the guardrail layer at its I/O nodes.",),
    expected="Guardrails are wired into the graph's I/O nodes.",
    weight=2,
))

add(T(
    "REQ-105-T01", "REQ-105", "The audit trail is committed as JSONL.",
    jsonl_records("logs/agent_actions.jsonl", [], 1, "audit trail as JSONL"),
    test_type="DATA_VALIDATION_TEST",
    steps=("Parse logs/agent_actions.jsonl and require valid JSON objects.",),
    expected="The audit trail is valid JSONL.",
))

add(T(
    "REQ-105-T02", "REQ-105",
    "Audit middleware appends actor, action, tool, decision and timestamp for each consequential action.",
    audit_trail_records,
    test_type="AUDITABILITY_TEST",
    steps=("Require the five named fields on the audit records.",
           "Require committed audit middleware that appends them."),
    expected="Audit middleware appends all five named fields per consequential action.",
    weight=3,
))

add(T(
    "REQ-106-T01", "REQ-106", "The governance pack is four committed Markdown documents.",
    all_of("the four governance Markdown documents",
           file_exists("docs/risk-register.md"),
           file_exists("docs/model-card.md"),
           file_exists("docs/compliance.md"),
           file_exists("docs/output-risk.md")),
    test_type="GOVERNANCE_TEST",
    steps=("Locate risk-register.md, model-card.md, compliance.md and output-risk.md.",),
    expected="All four governance documents exist as Markdown.",
    weight=2,
))

add(T(
    "REQ-106-T02", "REQ-106",
    "Each entry cites the committed control/artifact it refers to.",
    all_citations_resolve,
    test_type="AUDITABILITY_TEST",
    steps=("Extract every citation from the governance documents.",
           "Require each to resolve to a committed control or artifact."),
    expected="Every governance entry's citation resolves to a committed artifact.",
    weight=3,
))

add(T(
    "REQ-107-T01", "REQ-107", "The evaluation report is committed as JSON.",
    file_contains("reports/eval_report.json", [r"^\s*[\{\[]"], "valid JSON evaluation report"),
    test_type="DATA_VALIDATION_TEST",
    steps=("Confirm reports/eval_report.json parses as JSON.",),
    expected="The evaluation report is JSON.",
))

add(T(
    "REQ-107-T02", "REQ-107",
    "A DeepEval run over the golden set reports hallucination, faithfulness and answer-relevance, plus the harness.",
    eval_report_content,
    test_type="INTEGRATION_TEST",
    steps=("Parse the report.",
           "Require hallucination, faithfulness and answer-relevance over a golden set.",
           "Require the committed harness that writes it."),
    expected="The DeepEval run and its harness satisfy everything the row states.",
    weight=3,
))

add(T(
    "REQ-108-T01", "REQ-108", "The three agent tests exist as pytest files.",
    all_of("the three pytest files",
           file_exists("tests/test_routing.py"),
           file_exists("tests/test_loops.py"),
           file_exists("tests/test_tool_contracts.py")),
    test_type="STATIC_TEST",
    steps=("Locate each of the three test modules the row names.",),
    expected="All three agent test files exist.",
    weight=2,
))

add(T(
    "REQ-108-T02", "REQ-108", "tests/test_routing.py covers routing.",
    pytest_module_asserts("tests/test_routing.py", {"routing subject": r"rout|edge|worker"},
                          "routing test"),
    test_type="INTEGRATION_TEST",
    steps=("Require test functions, assertions, and routing subject matter.",),
    expected="The routing test covers routing.",
))

add(T(
    "REQ-108-T03", "REQ-108", "tests/test_loops.py covers the recursion/step limit.",
    pytest_module_asserts("tests/test_loops.py",
                          {"recursion/step limit subject": r"recursion|step|iter|limit"},
                          "loops test"),
    test_type="INTEGRATION_TEST",
    steps=("Require test functions, assertions, and a recursion/step-limit subject.",),
    expected="The loops test covers the recursion/step limit.",
))

add(T(
    "REQ-108-T04", "REQ-108", "tests/test_tool_contracts.py covers the I/O schema and an error path.",
    pytest_module_asserts("tests/test_tool_contracts.py", {
        "I/O schema": r"schema|input|output|contract",
        "error path": r"raise|error|exception|invalid",
    }, "tool-contract test"),
    test_type="INTEGRATION_TEST",
    steps=("Require test functions, assertions, schema coverage and an error path.",),
    expected="The tool-contract test covers the I/O schema and an error path.",
))


# ======================================================================================
# Section 8.1 Good-to-Have (REQ-109 .. REQ-111) - the source text marks these optional
# ======================================================================================

add(T(
    "REQ-109-T01", "REQ-109",
    "A FastAPI streaming endpoint exists.",
    all_of("FastAPI streaming endpoint",
           dir_exists("src/api"),
           dependency_declared(["fastapi"], "fastapi declared"),
           tree_contains([r"async\s+def", r"stream|Streaming|yield"],
                         "an async streaming endpoint", PY, mode="all", under="src/api")),
    test_type="API_TEST", suite="api",
    steps=("Locate src/api/.", "Confirm fastapi is declared.",
           "Confirm the endpoint is async and streaming."),
    expected="An async FastAPI streaming endpoint exists.",
))

add(T(
    "REQ-109-T02", "REQ-109",
    "A demonstrated local run of the endpoint is committed as a screenshot or log.",
    any_of("a demonstrated local run",
           tree_contains([r"uvicorn|fastapi|/stream|127\.0\.0\.1:8000|localhost:8000"],
                         "a committed run log of the streaming endpoint", (".log", ".txt", ".md")),
           file_exists("docs/api-run.png")),
    test_type="DOCUMENTATION_TEST",
    steps=("Search the committed logs and documentation for a demonstrated local run of the "
           "streaming endpoint."),
    expected="A screenshot or log demonstrating a local run is committed.",
))

add(T(
    "REQ-110-T01", "REQ-110", "PII-redaction middleware using Presidio exists.",
    all_of("Presidio PII-redaction middleware",
           dependency_declared(["presidio-analyzer", "presidio_analyzer", "presidio"],
                               "presidio declared", mode="any"),
           tree_contains([r"presidio"], "Presidio used in the redaction path", PY),
           masking_present),
    test_type="SECURITY_TEST",
    steps=("Confirm Presidio is declared and used.", "Confirm redaction is applied."),
    expected="Presidio-based PII-redaction middleware exists.",
))

add(T(
    "REQ-110-T02", "REQ-110", "A before/after redaction sample is committed.",
    tree_contains([r"before.{0,40}after|redact.{0,80}sample|sample.{0,80}redact"],
                  "a before/after redaction sample", (".md", ".json", ".txt")),
    test_type="DOCUMENTATION_TEST",
    steps=("Search the committed documentation and data for a before/after redaction sample.",),
    expected="A before/after redaction sample is committed.",
))

add(T(
    "REQ-110-T03", "REQ-110", "A small red-team attack set and its results are committed.",
    all_of("red-team attack set and results",
           tree_contains([r"red[_\- ]?team|attack[_\- ]?set|adversarial"],
                         "a red-team attack set", (".md", ".json", ".jsonl", ".py", ".csv")),
           tree_contains([r"result|outcome|blocked|refused|pass|fail"],
                         "the attack results", (".md", ".json", ".jsonl", ".csv"))),
    test_type="SECURITY_TEST",
    steps=("Locate the committed red-team attack set.", "Locate its committed results.",),
    expected="A red-team attack set and its results are both committed.",
))

add(T(
    "REQ-111-T01", "REQ-111",
    "An optimization note shows a measured before/after latency or cost improvement from two Phoenix-derived reports.",
    all_of("optimization note backed by two Phoenix-derived reports",
           tree_contains([r"optimi[sz]ation|before.{0,40}after|improvement"],
                         "the optimization note", DOCS),
           tree_contains([r"latency|cost"], "the measured dimension", DOCS),
           two_phoenix_reports),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the optimization note.",
           "Confirm it states a measured before/after latency or cost figure.",
           "Confirm two Phoenix-derived reports back it."),
    expected="An optimization note is backed by two Phoenix-derived reports.",
))


# ======================================================================================
# Closing paragraph (REQ-112)
# ======================================================================================

add(T(
    "REQ-112-T01", "REQ-112", "The lending decision is observable.",
    all_of("observable lending decision",
           any_of("a trace export",
                  file_exists("traces/phoenix_spans.parquet"),
                  file_exists("traces/phoenix_spans.jsonl")),
           file_exists("logs/tool_calls.jsonl")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the trace export and the tool-invocation log that make the decision observable.",),
    expected="The lending decision is observable through committed traces and logs.",
))

add(T(
    "REQ-112-T02", "REQ-112", "The lending decision is cost-governed.",
    all_of("cost governance",
           file_exists("reports/golden_signals.json"),
           file_exists("reports/dashboard_data.csv")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the golden-signals report and the cost/latency data.",),
    expected="Cost governance artifacts exist.",
))

add(T(
    "REQ-112-T03", "REQ-112", "The lending decision is secure.",
    all_of("security",
           dir_exists("src/guardrails"),
           file_exists(".env.example"),
           masking_present),
    test_type="SECURITY_TEST",
    steps=("Locate the guardrails, the secrets hygiene template and the masking implementation.",),
    expected="The security surface is in place.",
))

add(T(
    "REQ-112-T04", "REQ-112", "The lending decision is compliant.",
    all_of("compliance",
           file_exists("docs/compliance.md"),
           file_exists("docs/risk-register.md"),
           file_exists("docs/model-card.md"),
           file_exists("docs/output-risk.md")),
    test_type="GOVERNANCE_TEST",
    steps=("Locate the four governance and compliance documents.",),
    expected="The compliance surface is in place.",
))

add(T(
    "REQ-112-T05", "REQ-112", "The lending decision is continuously evaluated.",
    all_of("continuous evaluation",
           file_exists("reports/eval_report.json"),
           file_exists("tests/test_routing.py"),
           file_exists("tests/test_loops.py"),
           file_exists("tests/test_tool_contracts.py")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the evaluation report and the three agent tests.",),
    expected="The evaluation surface is in place.",
))

add(T(
    "REQ-112-T06", "REQ-112",
    "The result is proven with committed evidence rather than a demo that worked once.",
    all_of("committed, regenerable evidence",
           all_named_evidence_committed,
           evidence_artifacts_have_producers,
           readme_documents_single_command),
    test_type="AUDITABILITY_TEST",
    steps=("Confirm every named artifact present is committed.",
           "Confirm each evidence artifact has committed producing code.",
           "Confirm the documented commands can regenerate it, so it is not a one-off demo."),
    expected="The evidence is committed, machine-generated and regenerable on demand.",
    weight=3,
))
