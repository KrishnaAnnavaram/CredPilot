"""
Test cases for REQ-072 .. REQ-095.

Covers Section 7, "Required Artifacts - What to Commit": 7.1 Agentic System, 7.2
Observability & Tracing, 7.3 Performance & Cost Governance, 7.4 Security & Guardrails,
7.5 Governance & Compliance, 7.6 Agent Evaluation & Testing, 7.7 Engineering & Delivery.

Each row of those tables names an Area, an Artifact (path) and what it Must contain.
Each test below binds to one of those three, so a partially-satisfied row produces a
partial fit score and still FAILS the requirement.
"""

from __future__ import annotations

import bootstrap  # noqa: F401
from evidence_validator import (
    all_of,
    any_of,
    committed,
    dependency_declared,
    dir_exists,
    file_contains,
    file_exists,
    py_calls,
    py_imports,
    tree_contains,
)
from requirement_validator import TestCase
from response_validator import (
    artifact_has_producing_code,
    sample_inputs_committed,
    tool_names_reconcile,
)

from ._artifact_checks import (
    all_citations_resolve,
    audit_trail_records,
    eval_report_content,
    golden_signals_content,
    golden_signals_percentiles,
    guardrails_wired,
    mcp_transcript_committed,
    tool_call_log_fields,
)
from ._helpers import T
from ._shared_checks import (
    cli_present,
    dashboard_pair,
    document_covers,
    failure_analysis_content,
    gitignore_covers_env,
    mcp_surface,
    no_secrets_committed,
    optional_surface_reported,
    pytest_module_asserts,
    readme_documents_single_command,
    supervisor_and_workers,
    trace_export_content,
)

PY = (".py",)
DOCS = (".md",)

CASES: list[TestCase] = []
add = CASES.append


# ======================================================================================
# 7.1 Agentic System - Foundation (REQ-072 .. REQ-076)
# ======================================================================================

add(T(
    "REQ-072-T01", "REQ-072", "The LangGraph graph artifact exists at src/graph.py.",
    file_exists("src/graph.py"),
    test_type="STATIC_TEST",
    steps=("Locate src/graph.py at or near the path shown.",),
    expected="src/graph.py exists.",
))

add(T(
    "REQ-072-T02", "REQ-072", "The graph defines typed state.",
    tree_contains([r"TypedDict|BaseModel|Annotated\[|@dataclass"], "typed graph state", PY),
    test_type="ARCHITECTURE_TEST",
    steps=("Search for the graph's state type definition.",),
    expected="The graph state is a declared type.",
))

add(T(
    "REQ-072-T03", "REQ-072", "The graph has a supervisor and at least 3 worker agents.",
    supervisor_and_workers,
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the supervisor.",
           "Count the distinct worker agents; the document requires at least 3.",
           "Name each worker found and each expected worker not found."),
    expected="A supervisor plus at least 3 worker agents exist.",
    evidence="The supervisor location and the located worker agents.",
    weight=3,
))

add(T(
    "REQ-072-T04", "REQ-072", "The graph declares conditional edges.",
    py_calls(["add_conditional_edges"], "conditional edges added to the graph"),
    test_type="ARCHITECTURE_TEST",
    steps=("Analyse the Python AST for a call that adds conditional edges.",),
    expected="Conditional edges are added to the graph.",
    weight=2,
))

add(T(
    "REQ-072-T05", "REQ-072", "The graph has a checkpointer.",
    all_of("checkpointer",
           tree_contains([r"checkpoint"], "checkpointer referenced", PY),
           any_of("a checkpointer implementation",
                  tree_contains([r"SqliteSaver|AsyncSqliteSaver"], "SQLite checkpointer", PY),
                  tree_contains([r"MemorySaver|BaseCheckpointSaver"], "checkpointer class", PY))),
    test_type="ARCHITECTURE_TEST",
    steps=("Search for a checkpointer reference.",
           "Require a concrete checkpointer implementation."),
    expected="A checkpointer is configured on the graph.",
    weight=2,
))

add(T(
    "REQ-072-T06", "REQ-072", "The graph produces structured output at node boundaries.",
    tree_contains([r"with_structured_output|response_format|model_json_schema|return\s+\w*State"],
                  "structured output at node boundaries", PY),
    test_type="OUTPUT_VALIDATION_TEST",
    steps=("Search the node implementations for structured output at their boundaries.",),
    expected="Node boundaries carry structured output.",
))

add(T(
    "REQ-073-T01", "REQ-073", "The MCP server artifact exists at mcp_server/.",
    dir_exists("mcp_server"),
    test_type="STATIC_TEST",
    steps=("Locate the mcp_server/ package at or near the path shown.",),
    expected="mcp_server/ exists and is non-empty.",
))

add(T(
    "REQ-073-T02", "REQ-073", "The MCP server exposes at least 2 tools and at least 1 resource.",
    mcp_surface,
    test_type="INTEGRATION_TEST",
    steps=("Parse the MCP server sources.",
           "Count decorated/registered MCP tools; require >= 2.",
           "Count decorated/registered MCP resources; require >= 1."),
    expected="At least 2 MCP tools and at least 1 MCP resource are registered.",
    evidence="The registered tool and resource names.",
    weight=3,
))

add(T(
    "REQ-073-T03", "REQ-073", "The MCP server is consumed via langchain-mcp-adapters.",
    all_of("consumed via langchain-mcp-adapters",
           dependency_declared(["langchain-mcp-adapters"], "langchain-mcp-adapters declared"),
           py_imports(["langchain_mcp_adapters"], "langchain_mcp_adapters imported")),
    test_type="INTEGRATION_TEST",
    steps=("Confirm the adapter package is declared.", "Confirm it is imported."),
    expected="The MCP server is consumed through langchain-mcp-adapters.",
    weight=2,
))

add(T(
    "REQ-073-T04", "REQ-073",
    "A committed tool-call transcript exists at logs/mcp_transcript.jsonl.",
    mcp_transcript_committed,
    test_type="AUDITABILITY_TEST",
    steps=("Locate logs/mcp_transcript.jsonl and parse it.",
           "Confirm git tracks it."),
    expected="A committed, parseable MCP tool-call transcript exists.",
    weight=2,
))

add(T(
    "REQ-074-T01", "REQ-074", "The context-engineering artifact exists at src/context/.",
    dir_exists("src/context"),
    test_type="STATIC_TEST",
    steps=("Locate src/context/ at or near the path shown.",),
    expected="src/context/ exists and is non-empty.",
))

add(T(
    "REQ-074-T02", "REQ-074", "Context engineering implements write, select, compress and isolate.",
    tree_contains([r"\bwrite\b", r"\bselect\b", r"\bcompress\b", r"\bisolate\b"],
                  "the four named context operations", PY, mode="all", under="src/context"),
    test_type="ARCHITECTURE_TEST",
    steps=("Search src/context/ for each of the four operations the document names.",),
    expected="write, select, compress and isolate are all implemented.",
    weight=2,
))

add(T(
    "REQ-074-T03", "REQ-074", "Summarization middleware is present.",
    tree_contains([r"summar"], "summarization middleware", PY, under="src/context"),
    test_type="ARCHITECTURE_TEST",
    steps=("Search src/context/ for summarization middleware.",),
    expected="Summarization middleware exists in the context layer.",
))

add(T(
    "REQ-074-T04", "REQ-074", "Untrusted text is quarantined in the context layer.",
    tree_contains([r"quarantin"], "quarantine of untrusted text", PY),
    test_type="SECURITY_TEST",
    steps=("Search for the quarantine of untrusted text.",),
    expected="Untrusted text is quarantined.",
    weight=2,
))

add(T(
    "REQ-075-T01", "REQ-075", "The tiered-memory artifact exists at src/memory/.",
    dir_exists("src/memory"),
    test_type="STATIC_TEST",
    steps=("Locate src/memory/ at or near the path shown.",),
    expected="src/memory/ exists and is non-empty.",
))

add(T(
    "REQ-075-T02", "REQ-075", "The cross-session recall test exists at tests/test_memory_persistence.py.",
    file_exists("tests/test_memory_persistence.py"),
    test_type="STATIC_TEST",
    steps=("Locate tests/test_memory_persistence.py at or near the path shown.",),
    expected="tests/test_memory_persistence.py exists.",
))

add(T(
    "REQ-075-T03", "REQ-075", "The committed output log exists at logs/memory_test.log.",
    all_of("committed memory test output log",
           file_exists("logs/memory_test.log"),
           committed("logs/memory_test.log")),
    test_type="AUDITABILITY_TEST",
    steps=("Locate logs/memory_test.log.", "Confirm git tracks it."),
    expected="A committed output log from the memory test exists.",
    weight=2,
))

add(T(
    "REQ-075-T04", "REQ-075", "Both short and long/semantic memory tiers exist.",
    all_of("short + long/semantic memory",
           tree_contains([r"short[_\- ]?term|short_memory|working[_\- ]?memory"],
                         "short-term memory tier", PY),
           tree_contains([r"long[_\- ]?term|semantic[_\- ]?memory|episodic|vector"],
                         "long/semantic memory tier", PY)),
    test_type="ARCHITECTURE_TEST",
    steps=("Search for a short-term memory tier.",
           "Search for a long/semantic memory tier."),
    expected="Both memory tiers the document names exist.",
    weight=2,
))

add(T(
    "REQ-075-T05", "REQ-075", "The cross-session recall test asserts recall across sessions.",
    pytest_module_asserts("tests/test_memory_persistence.py", {
        "cross-session recall subject": r"session|thread_id|persist|recall|restart",
    }, "cross-session recall test"),
    test_type="INTEGRATION_TEST",
    steps=("Locate the memory persistence test.",
           "Require test functions, assertions, and cross-session subject matter."),
    expected="The test asserts recall of prior-session context.",
    weight=2,
))

add(T(
    "REQ-076-T01", "REQ-076", "The agentic-RAG tool exists at src/tools/rag_tool.py.",
    file_exists("src/tools/rag_tool.py"),
    test_type="STATIC_TEST",
    steps=("Locate src/tools/rag_tool.py at or near the path shown.",),
    expected="src/tools/rag_tool.py exists.",
))

add(T(
    "REQ-076-T02", "REQ-076", "The lending-policy corpus exists at data/policy_corpus/.",
    dir_exists("data/policy_corpus"),
    test_type="DATA_VALIDATION_TEST",
    steps=("Locate data/policy_corpus/ at or near the path shown and confirm it is non-empty.",),
    expected="data/policy_corpus/ exists with content.",
))

add(T(
    "REQ-076-T03", "REQ-076", "Retrieval happens in the loop, not as a one-off preprocessing step.",
    all_of("retrieval-in-the-loop",
           tree_contains([r"@tool|StructuredTool|Tool\(|tool\b"],
                         "the RAG capability exposed as an agent tool", PY, under="src/tools"),
           tree_contains([r"retriev|search|similarity|query"],
                         "retrieval invoked by the tool", PY, under="src/tools")),
    test_type="INTEGRATION_TEST",
    steps=("Confirm the RAG capability is exposed to the agent as a callable tool.",
           "Confirm the tool performs retrieval when called."),
    expected="Retrieval is in the agent loop as a callable tool.",
    weight=2,
))

add(T(
    "REQ-076-T04", "REQ-076", "The corpus is a synthetic lending-policy corpus.",
    tree_contains([r"synthetic"], "the corpus declared synthetic", (".md", ".json", ".txt", ".py")),
    test_type="DATA_VALIDATION_TEST",
    steps=("Search the repository for the declaration that the policy corpus is synthetic.",),
    expected="The lending-policy corpus is declared synthetic.",
))


# ======================================================================================
# 7.2 Observability & Tracing (REQ-077 .. REQ-080)
# ======================================================================================

add(T(
    "REQ-077-T01", "REQ-077", "The Phoenix instrumentation exists at src/observability/tracing.py.",
    file_exists("src/observability/tracing.py"),
    test_type="STATIC_TEST",
    steps=("Locate src/observability/tracing.py at or near the path shown.",),
    expected="src/observability/tracing.py exists.",
))

add(T(
    "REQ-077-T02", "REQ-077",
    "The Phoenix/openinference tracer is CALLED, not just imported.",
    py_calls(["register", "instrument", "LangChainInstrumentor", "launch_app", "tracer_provider"],
             "the tracer actually invoked", mode="any"),
    test_type="OBSERVABILITY_TEST",
    steps=("Analyse the Python AST of the implementation.",
           "Require a call that activates the tracer, not merely an import of it."),
    expected="The tracer is invoked, satisfying 'called, not just imported'.",
    evidence="The AST call site that activates the tracer.",
    weight=3,
))

add(T(
    "REQ-077-T03", "REQ-077", "The tracer is wired into the run path.",
    tree_contains([r"tracing|tracer|instrument"],
                  "the run path referencing the tracing module", PY),
    test_type="OBSERVABILITY_TEST",
    steps=("Search the run path for a reference to the tracing module.",),
    expected="The run path activates tracing.",
    weight=2,
))

add(T(
    "REQ-078-T01", "REQ-078",
    "The trace export exists at traces/phoenix_spans.parquet (or .jsonl).",
    any_of("trace export artifact",
           file_exists("traces/phoenix_spans.parquet"),
           file_exists("traces/phoenix_spans.jsonl")),
    test_type="STATIC_TEST",
    steps=("Locate traces/phoenix_spans.parquet, or the .jsonl alternative the document permits.",),
    expected="A trace export exists in one of the two permitted formats.",
))

add(T(
    "REQ-078-T02", "REQ-078",
    "The export covers at least one full run, spans multiple agents and every tool call, and carries latencies.",
    trace_export_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Open the trace export.",
           "Require at least one full run's spans.",
           "Require spans across more than one agent/tool.",
           "Require latency or duration data on the spans."),
    expected="The export shows >= 1 full run, spans across multiple agents and every tool call, and latencies.",
    evidence="Span count, distinct span names, and the latency column or key.",
    weight=3,
))

add(T(
    "REQ-079-T01", "REQ-079", "The tool-invocation log exists at logs/tool_calls.jsonl.",
    file_exists("logs/tool_calls.jsonl"),
    test_type="STATIC_TEST",
    steps=("Locate logs/tool_calls.jsonl at or near the path shown.",),
    expected="logs/tool_calls.jsonl exists.",
))

add(T(
    "REQ-079-T02", "REQ-079",
    "Every per-call field the document names is present: timestamp, agent/node, tool_name, args, result, latency_ms, status.",
    tool_call_log_fields,
    test_type="OBSERVABILITY_TEST",
    steps=("Parse every record in the log.",
           "Require each of the seven named per-call fields."),
    expected="All seven per-call fields are present.",
    weight=3,
))

add(T(
    "REQ-079-T03", "REQ-079", "The log is machine-generated.",
    artifact_has_producing_code("logs/tool_calls.jsonl", [r"tool_calls\.jsonl"],
                                "machine-generated tool-invocation log"),
    test_type="AUDITABILITY_TEST",
    steps=("Locate the committed code that writes the log.",),
    expected="Committed code produces the log.",
    weight=2,
))

add(T(
    "REQ-079-T04", "REQ-079", "Tool names in the log reconcile with the code.",
    tool_names_reconcile(),
    test_type="AUDITABILITY_TEST",
    steps=("Collect the distinct tool names from the log.",
           "Require each to appear in the committed Python sources."),
    expected="Every logged tool name reconciles with the code.",
    weight=2,
))

add(T(
    "REQ-080-T01", "REQ-080", "The failure-mode analysis exists at docs/failure-analysis.md.",
    file_exists("docs/failure-analysis.md"),
    test_type="STATIC_TEST",
    steps=("Locate docs/failure-analysis.md at or near the path shown.",),
    expected="docs/failure-analysis.md exists.",
))

add(T(
    "REQ-080-T02", "REQ-080",
    "At least 3 real failures are documented, EACH citing run_id + span_id (or a tool-log record), plus root cause and fix.",
    failure_analysis_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Count the documented failures; require >= 3.",
           "Require each to cite a Phoenix run_id + span_id, or a tool-log record.",
           "Require a root cause and a fix for each."),
    expected="Three or more failures, each fully evidenced with cause and fix.",
    weight=3,
))


# ======================================================================================
# 7.3 Performance & Cost Governance (REQ-081 .. REQ-082)
# ======================================================================================

add(T(
    "REQ-081-T01", "REQ-081", "The golden-signals report exists at reports/golden_signals.json.",
    file_exists("reports/golden_signals.json"),
    test_type="STATIC_TEST",
    steps=("Locate reports/golden_signals.json at or near the path shown.",),
    expected="reports/golden_signals.json exists.",
))

add(T(
    "REQ-081-T02", "REQ-081", "A producing script accompanies the report.",
    artifact_has_producing_code("reports/golden_signals.json",
                                [r"golden_signals\.json"], "the report's producing script"),
    test_type="AUDITABILITY_TEST",
    steps=("Locate the committed script that writes the report.",),
    expected="A committed producing script exists.",
    weight=2,
))

add(T(
    "REQ-081-T03", "REQ-081",
    "The report carries Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate, accuracy and hallucination rate.",
    golden_signals_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Parse the report.",
           "Require latency for each of the thinking, acting and tool span types.",
           "Require tokens, a cost estimate, accuracy and hallucination rate."),
    expected="Every figure the row lists is present in the report.",
    weight=3,
))

add(T(
    "REQ-082-T01", "REQ-082",
    "The dashboard screenshot AND the underlying data file it was drawn from both exist.",
    dashboard_pair,
    test_type="OBSERVABILITY_TEST",
    steps=("Locate reports/dashboard.png and verify the PNG signature.",
           "Locate reports/dashboard_data.csv and verify it holds data rows."),
    expected="Both artifacts exist with real content - the row requires the screenshot AND the data file.",
    weight=3,
))

add(T(
    "REQ-082-T02", "REQ-082", "The underlying data file is machine-exported.",
    artifact_has_producing_code("reports/dashboard_data.csv",
                                [r"dashboard_data\.csv", r"to_csv\("],
                                "the dashboard data export"),
    test_type="AUDITABILITY_TEST",
    steps=("Locate the committed code that exports the dashboard data.",),
    expected="Committed code exports the dashboard data file.",
))


# ======================================================================================
# 7.4 Security & Guardrails (REQ-083 .. REQ-085)
# ======================================================================================

add(T(
    "REQ-083-T01", "REQ-083", "The guardrail code exists at src/guardrails/.",
    dir_exists("src/guardrails"),
    test_type="STATIC_TEST",
    steps=("Locate src/guardrails/ at or near the path shown.",),
    expected="src/guardrails/ exists and is non-empty.",
))

add(T(
    "REQ-083-T02", "REQ-083",
    "Input/output guardrails are wired into the agent's I/O path and block or sanitize.",
    guardrails_wired,
    test_type="SECURITY_TEST",
    steps=("Require an input guardrail and an output guardrail.",
           "Require blocking or sanitizing behaviour.",
           "Require a module outside the guardrail package to call into it."),
    expected="Guardrails are wired into the I/O path and block or sanitize.",
    weight=3,
))

add(T(
    "REQ-084-T01", "REQ-084", "The audit trail exists at logs/agent_actions.jsonl.",
    file_exists("logs/agent_actions.jsonl"),
    test_type="STATIC_TEST",
    steps=("Locate logs/agent_actions.jsonl at or near the path shown.",),
    expected="logs/agent_actions.jsonl exists.",
))

add(T(
    "REQ-084-T02", "REQ-084",
    "Audit middleware machine-generates records carrying actor, action, tool, decision and timestamp.",
    audit_trail_records,
    test_type="AUDITABILITY_TEST",
    steps=("Parse the audit trail.",
           "Require the five named fields.",
           "Require committed audit middleware that writes it."),
    expected="Machine-generated audit records with all five named fields.",
    weight=3,
))

add(T(
    "REQ-084-T03", "REQ-084", "Consequential actions are what the audit trail records.",
    tree_contains([r"audit"], "audit middleware invoked on agent actions", PY),
    test_type="AUDITABILITY_TEST",
    steps=("Locate where the audit middleware is invoked on the agent's consequential actions.",),
    expected="The audit middleware is invoked for consequential actions.",
))

add(T(
    "REQ-085-T01", "REQ-085",
    "Env-var config with a committed .env.example, and .gitignore covering .env.",
    gitignore_covers_env,
    test_type="CONFIGURATION_TEST",
    steps=("Locate .gitignore and require a rule covering .env.",
           "Locate the committed .env.example.",
           "Confirm no real .env is committed."),
    expected="Secrets hygiene per the row: env-var config, .gitignore covers .env.",
    weight=2,
))

add(T(
    "REQ-085-T02", "REQ-085", "No secrets are committed anywhere.",
    no_secrets_committed,
    test_type="SECURITY_TEST",
    steps=("Scan every committed text artifact against a set of credential patterns.",),
    expected="No secret is committed anywhere in the repository.",
    weight=3,
))


# ======================================================================================
# 7.5 Governance & Compliance (citation-gated) (REQ-086 .. REQ-089)
# ======================================================================================

add(T(
    "REQ-086-T01", "REQ-086", "The risk register exists at docs/risk-register.md.",
    file_exists("docs/risk-register.md"),
    test_type="STATIC_TEST",
    steps=("Locate docs/risk-register.md at or near the path shown.",),
    expected="docs/risk-register.md exists.",
))

add(T(
    "REQ-086-T02", "REQ-086",
    "The risk register carries risk, category (OWASP/NIST), likelihood, impact, mitigation, residual risk and owner.",
    document_covers("docs/risk-register.md", {
        "risk": r"\brisk\b",
        "category (OWASP/NIST)": r"OWASP|NIST",
        "likelihood": r"likelihood",
        "impact": r"impact",
        "mitigation": r"mitigat",
        "residual risk": r"residual",
        "owner": r"owner",
    }, "risk register columns"),
    test_type="GOVERNANCE_TEST",
    steps=("Read docs/risk-register.md.",
           "Require each of the seven elements the row names."),
    expected="All seven risk-register elements are present.",
    weight=3,
))

add(T(
    "REQ-086-T03", "REQ-086", "Each mitigation cites the committed control.",
    all_citations_resolve,
    test_type="AUDITABILITY_TEST",
    steps=("Extract the citations from the risk register.",
           "Require each to resolve to a committed control."),
    expected="Every mitigation citation resolves to a committed control.",
    weight=2,
))

add(T(
    "REQ-087-T01", "REQ-087", "The model / system card exists at docs/model-card.md.",
    file_exists("docs/model-card.md"),
    test_type="STATIC_TEST",
    steps=("Locate docs/model-card.md at or near the path shown.",),
    expected="docs/model-card.md exists.",
))

add(T(
    "REQ-087-T02", "REQ-087",
    "The model card states model (Gemini), data (synthetic), intended use, limitations, known failure modes and out-of-scope.",
    document_covers("docs/model-card.md", {
        "model (Gemini)": r"gemini",
        "data (synthetic)": r"synthetic",
        "intended use": r"intended\s+use",
        "limitations": r"limitation",
        "known failure modes": r"failure\s+mode",
        "out-of-scope": r"out[\s-]of[\s-]scope",
    }, "model card contents"),
    test_type="GOVERNANCE_TEST",
    steps=("Read docs/model-card.md.",
           "Require each of the six elements the row names."),
    expected="All six model-card elements are present.",
    weight=3,
))

add(T(
    "REQ-087-T03", "REQ-087", "The known failure modes cite failure-analysis.md.",
    file_contains("docs/model-card.md", [r"failure-analysis\.md"],
                  "citation of failure-analysis.md"),
    test_type="AUDITABILITY_TEST",
    steps=("Search the model card for the citation of failure-analysis.md the row requires.",),
    expected="The model card cites failure-analysis.md for its known failure modes.",
    weight=2,
))

add(T(
    "REQ-088-T01", "REQ-088", "The compliance mapping exists at docs/compliance.md.",
    file_exists("docs/compliance.md"),
    test_type="STATIC_TEST",
    steps=("Locate docs/compliance.md at or near the path shown.",),
    expected="docs/compliance.md exists.",
))

add(T(
    "REQ-088-T02", "REQ-088",
    "The mapping names the applicable EU AI Act, NIST AI RMF and DPDP obligations.",
    document_covers("docs/compliance.md", {
        "EU AI Act": r"EU\s*AI\s*Act",
        "NIST AI RMF": r"NIST\s*AI\s*RMF",
        "DPDP": r"\bDPDP\b",
    }, "compliance frameworks"),
    test_type="GOVERNANCE_TEST",
    steps=("Read docs/compliance.md.", "Require all three named frameworks."),
    expected="All three frameworks are mapped.",
    weight=2,
))

add(T(
    "REQ-088-T03", "REQ-088",
    "Each obligation maps to how it is addressed and to an evidence artifact.",
    all_of("obligation -> how addressed -> evidence artifact",
           document_covers("docs/compliance.md", {
               "how addressed": r"how\s+addressed|addressed\s+by|mitigation|control",
               "evidence artifact": r"evidence",
           }, "compliance mapping columns"),
           all_citations_resolve),
    test_type="AUDITABILITY_TEST",
    steps=("Require a 'how addressed' element and an 'evidence artifact' element.",
           "Require every cited evidence artifact to resolve to a committed file."),
    expected="Each obligation maps through to a resolvable committed evidence artifact.",
    weight=3,
))

add(T(
    "REQ-089-T01", "REQ-089", "The output-risk classification exists at docs/output-risk.md.",
    file_exists("docs/output-risk.md"),
    test_type="STATIC_TEST",
    steps=("Locate docs/output-risk.md at or near the path shown.",),
    expected="docs/output-risk.md exists.",
))

add(T(
    "REQ-089-T02", "REQ-089", "The classification defines low, medium and high output tiers.",
    document_covers("docs/output-risk.md", {
        "low tier": r"\blow\b",
        "medium tier": r"\bmed(ium)?\b",
        "high tier": r"\bhigh\b",
    }, "output-risk tiers"),
    test_type="GOVERNANCE_TEST",
    steps=("Read docs/output-risk.md.", "Require the low, medium and high tiers."),
    expected="All three output-risk tiers are defined.",
    weight=2,
))

add(T(
    "REQ-089-T03", "REQ-089",
    "The document states how high-risk output is gated by human-in-loop or refusal.",
    document_covers("docs/output-risk.md", {
        "high-risk gating": r"gat(e|ed|ing)|escalat|block",
        "human-in-loop or refusal": r"human[\s-]in[\s-]loop|human[\s-]in[\s-]the[\s-]loop|refus",
    }, "high-risk gating"),
    test_type="GOVERNANCE_TEST",
    steps=("Require a statement of how high-risk output is gated.",
           "Require the gate to be human-in-loop or refusal."),
    expected="High-risk output is gated by human-in-loop or refusal.",
    weight=2,
))

add(T(
    "REQ-089-T04", "REQ-089", "A sample is included.",
    document_covers("docs/output-risk.md", {"a sample": r"sample|example"},
                    "output-risk sample"),
    test_type="GOVERNANCE_TEST",
    steps=("Require the sample the row asks for.",),
    expected="A sample is included in the output-risk classification.",
))


# ======================================================================================
# 7.6 Agent Evaluation & Testing (REQ-090 .. REQ-093)
# ======================================================================================

add(T(
    "REQ-090-T01", "REQ-090", "The evaluation report exists at reports/eval_report.json.",
    file_exists("reports/eval_report.json"),
    test_type="STATIC_TEST",
    steps=("Locate reports/eval_report.json at or near the path shown.",),
    expected="reports/eval_report.json exists.",
))

add(T(
    "REQ-090-T02", "REQ-090",
    "A DeepEval (or equivalent) run over a golden set reports hallucination and faithfulness/relevance via LLM-as-judge, with its harness.",
    eval_report_content,
    test_type="INTEGRATION_TEST",
    steps=("Parse the report.",
           "Require hallucination, faithfulness and answer-relevance over a golden set.",
           "Require a committed harness using DeepEval or an equivalent LLM-as-judge."),
    expected="The evaluation report and its harness satisfy every element the row lists.",
    weight=3,
))

add(T(
    "REQ-091-T01", "REQ-091", "The routing-logic test exists at tests/test_routing.py.",
    file_exists("tests/test_routing.py"),
    test_type="STATIC_TEST",
    steps=("Locate tests/test_routing.py at or near the path shown.",),
    expected="tests/test_routing.py exists.",
))

add(T(
    "REQ-091-T02", "REQ-091",
    "It asserts that conditional edges route the right worker for given states.",
    pytest_module_asserts("tests/test_routing.py", {
        "the routing subject": r"rout|edge|worker|supervisor",
        "a given state": r"state|input|case|scenario",
    }, "routing-logic assertions"),
    test_type="INTEGRATION_TEST",
    steps=("Require test functions and assertions.",
           "Require the assertions to be about routing a given state to a worker."),
    expected="The test asserts conditional-edge routing for given states.",
    weight=2,
))

add(T(
    "REQ-092-T01", "REQ-092", "The loop/cascade guard test exists at tests/test_loops.py.",
    file_exists("tests/test_loops.py"),
    test_type="STATIC_TEST",
    steps=("Locate tests/test_loops.py at or near the path shown.",),
    expected="tests/test_loops.py exists.",
))

add(T(
    "REQ-092-T02", "REQ-092",
    "It asserts that a max-steps / recursion-limit stops runaway loops.",
    pytest_module_asserts("tests/test_loops.py", {
        "max-steps / recursion limit": r"recursion[_\- ]?limit|max[_\- ]?step|max[_\- ]?iter",
        "stopping a runaway loop": r"stop|halt|raise|limit|exceed",
    }, "loop/cascade guard assertions"),
    test_type="INTEGRATION_TEST",
    steps=("Require test functions and assertions.",
           "Require a max-steps or recursion-limit subject and a stopping assertion."),
    expected="The test asserts that a limit stops runaway loops.",
    weight=2,
))

add(T(
    "REQ-092-T03", "REQ-092", "A max-steps / recursion limit exists in the implementation to be asserted.",
    tree_contains([r"recursion_limit|max_steps|max_iterations"],
                  "a configured step or recursion limit", PY),
    test_type="ARCHITECTURE_TEST",
    steps=("Search the implementation for the configured step or recursion limit.",),
    expected="A max-steps / recursion limit is configured.",
))

add(T(
    "REQ-093-T01", "REQ-093", "The tool-contract test exists at tests/test_tool_contracts.py.",
    file_exists("tests/test_tool_contracts.py"),
    test_type="STATIC_TEST",
    steps=("Locate tests/test_tool_contracts.py at or near the path shown.",),
    expected="tests/test_tool_contracts.py exists.",
))

add(T(
    "REQ-093-T02", "REQ-093",
    "It asserts each tool's input/output schema plus one error path.",
    pytest_module_asserts("tests/test_tool_contracts.py", {
        "input/output schema": r"schema|args_schema|input|output|contract|model_json_schema",
        "one error path": r"pytest\.raises|raise|invalid|error|exception",
    }, "tool-contract assertions"),
    test_type="INTEGRATION_TEST",
    steps=("Require test functions and assertions.",
           "Require input/output schema assertions.",
           "Require at least one error path."),
    expected="The test asserts each tool's I/O schema and an error path.",
    weight=2,
))


# ======================================================================================
# 7.7 Engineering & Delivery (REQ-094 .. REQ-095)
# ======================================================================================

add(T(
    "REQ-094-T01", "REQ-094", "The local-run runbook exists at README.md.",
    file_exists("README.md"),
    test_type="STATIC_TEST",
    steps=("Locate README.md at or near the path shown.",),
    expected="README.md exists.",
))

add(T(
    "REQ-094-T02", "REQ-094",
    "The runbook documents the single-command run and how to regenerate the traces and the eval.",
    readme_documents_single_command,
    test_type="DOCUMENTATION_TEST",
    steps=("Read README.md.",
           "Require a single-command run.",
           "Require documented commands that regenerate the Phoenix traces and the evaluation."),
    expected="The runbook documents the single-command run and both regeneration commands.",
    weight=3,
))

add(T(
    "REQ-094-T03", "REQ-094", "The runbook's committed sample inputs exist.",
    sample_inputs_committed("runbook sample inputs"),
    test_type="CONFIGURATION_TEST",
    steps=("Locate the committed sample inputs the runbook relies on.",),
    expected="Committed sample inputs exist.",
))

add(T(
    "REQ-094-T04", "REQ-094", "The documented command is backed by a real CLI entry point.",
    cli_present,
    test_type="RUNTIME_TEST", suite="functional",
    steps=("Discover the documented command.", "Confirm a CLI entry point backs it."),
    expected="The documented single command is backed by a real CLI entry point.",
))

add(T(
    "REQ-095-T01", "REQ-095",
    "The optional FastAPI streaming endpoint at src/api/ - extra credit, not required.",
    optional_surface_reported("src/api", "FastAPI streaming endpoint (OPTIONAL, not required)"),
    test_type="ARCHITECTURE_TEST",
    steps=("Look for src/api/.",
           "Record whether the optional bonus surface is present.",
           "Confirm the required CLI interface is not displaced by it."),
    expected="The optional FastAPI streaming endpoint is present as extra credit.",
    evidence="Presence or absence of src/api/, and the state of the required CLI.",
))

add(T(
    "REQ-095-T02", "REQ-095", "If present, the bonus endpoint is an async FastAPI streaming endpoint.",
    any_of("async FastAPI streaming endpoint, or the surface is absent",
           all_of("async FastAPI streaming endpoint",
                  dir_exists("src/api"),
                  dependency_declared(["fastapi"], "fastapi declared"),
                  tree_contains([r"async\s+def", r"Streaming|stream|EventSource|yield"],
                                "async streaming endpoint", PY, mode="all", under="src/api")),
           optional_surface_reported(
               "src/api", "FastAPI streaming endpoint (OPTIONAL, not required)")),
    test_type="API_TEST", suite="api",
    steps=("If src/api/ exists, require fastapi to be declared and the endpoint to be async and streaming.",
           "If it does not exist, the document marks it not required."),
    expected="Either an async FastAPI streaming endpoint exists, or the optional surface is absent.",
))
