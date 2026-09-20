"""
Test cases for REQ-004 .. REQ-043.

Covers: Section 1 (Project Identity), Section 2 (Engagement Overview), Section 3
(Problem Statement, Your Role, Expected Solution, Applicable Rules) and Section 4
(Technology & Framework Stack).

Every check here is derived only from the exact source text of the requirement it is
bound to. Where the document fixes no value, the test records UNSPECIFIED_BY_REQUIREMENT
instead of inventing one.
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
    git_has_remote,
    is_git_repository,
    json_keys,
    no_files_matching,
    py_calls,
    py_imports,
    python_version_declared,
    tree_absent,
    tree_contains,
)
from requirement_validator import TestCase
from response_validator import (
    artifact_has_producing_code,
    citations_resolve,
    sample_inputs_committed,
)

from ._helpers import T, manual_T, unspecified_T
from ._shared_checks import (
    all_named_evidence_committed,
    cli_present,
    documented_commands,
    evidence_artifacts_have_producers,
    masking_present,
    mcp_surface,
    no_container_command_in_readme,
    optional_surface_reported,
    remote_matches_gitlab,
    suite_excludes_unscored_topics,
)

DOCS = (".md",)
ALLTEXT = (".md", ".txt", ".rst", ".toml", ".cfg")
MANIFESTS = (".txt", ".toml", ".cfg")

CASES: list[TestCase] = []
add = CASES.append


# ======================================================================================
# Document title block (REQ-001 .. REQ-003)
# ======================================================================================

add(T(
    "REQ-001-T01", "REQ-001",
    "The delivered repository is identifiable as work on the pathway and capstone hackathon named in the document's banner line.",
    tree_contains([r"Agentic\s+AI\s+Engineer\s+Pathway", r"Capstone\s+Hackathon"],
                  "the pathway and capstone hackathon named in the banner line", DOCS, mode="all"),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan every committed Markdown document in the implementation.",
           "Require both halves of the banner line: the pathway and the capstone hackathon."),
    expected="The banner line 'Agentic AI Engineer Pathway - Capstone Hackathon' is reflected in the repository documentation.",
    evidence="File paths and line numbers for both matched fragments.",
))

add(T(
    "REQ-002-T01", "REQ-002",
    "The delivered repository carries the document's title.",
    tree_contains([r"Loan\s+Origination\s*&\s*Underwriting\s+Copilot"],
                  "the document title declared in repository documentation", DOCS),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan every committed Markdown document in the implementation.",
           "Look for the document title exactly as printed."),
    expected="The title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.",
    evidence="File path and line number of the matched title.",
))

add(T(
    "REQ-003-T01", "REQ-003",
    "The repository declares the business case ID and domain the subtitle states.",
    all_of("business case ID and domain from the subtitle",
           tree_contains([r"BC-AAIE-HACK-02"], "business case ID", ALLTEXT),
           tree_contains([r"Banking\s*&\s*Finance|Banking and Finance"], "domain", DOCS)),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan the repository for the business case ID.",
           "Scan the repository documentation for the declared domain."),
    expected="Both the business case ID and the domain from the subtitle are declared.",
))

# The subtitle names the seven areas this cross-cutting finale integrates. Each is
# separately verifiable, so each gets its own test against the requirement.
add(T(
    "REQ-003-T02", "REQ-003", "The Agentic Core area of the cross-cutting finale is delivered.",
    all_of("Agentic Core",
           file_exists("src/graph.py"),
           dependency_declared(["langgraph"], "LangGraph declared as a dependency")),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the agent graph that constitutes the agentic core.",
           "Confirm the agent framework is a declared dependency."),
    expected="The Agentic Core is delivered.",
))

add(T(
    "REQ-003-T03", "REQ-003", "The Context Engineering area of the cross-cutting finale is delivered.",
    dir_exists("src/context"),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the context-engineering package.",),
    expected="Context Engineering is delivered.",
))

add(T(
    "REQ-003-T04", "REQ-003", "The MCP area of the cross-cutting finale is delivered.",
    all_of("MCP",
           dir_exists("mcp_server"),
           dependency_declared(["mcp"], "the MCP Python SDK declared")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the MCP server package.", "Confirm the MCP SDK is a declared dependency."),
    expected="MCP is delivered.",
))

add(T(
    "REQ-003-T05", "REQ-003", "The Observability area of the cross-cutting finale is delivered.",
    all_of("Observability",
           file_exists("src/observability/tracing.py"),
           dependency_declared(["arize-phoenix"], "arize-phoenix declared as a dependency")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the tracing module.", "Confirm the observability stack is declared."),
    expected="Observability is delivered.",
))

add(T(
    "REQ-003-T06", "REQ-003", "The Cost Governance area of the cross-cutting finale is delivered.",
    all_of("Cost Governance",
           file_exists("reports/golden_signals.json"),
           file_exists("reports/dashboard_data.csv")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the golden-signals report and the cost/latency data file.",),
    expected="Cost Governance is delivered.",
))

add(T(
    "REQ-003-T07", "REQ-003",
    "The Security & Governance area of the cross-cutting finale is delivered.",
    all_of("Security & Governance",
           dir_exists("src/guardrails"),
           file_exists("docs/risk-register.md"),
           file_exists("docs/compliance.md")),
    test_type="GOVERNANCE_TEST",
    steps=("Locate the guardrail package.",
           "Locate the risk register and the compliance mapping."),
    expected="Security & Governance is delivered.",
))

add(T(
    "REQ-003-T08", "REQ-003", "The Agent Evaluation area of the cross-cutting finale is delivered.",
    all_of("Agent Evaluation",
           file_exists("reports/eval_report.json"),
           file_exists("tests/test_routing.py")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the evaluation report.", "Locate at least one committed agent test.",),
    expected="Agent Evaluation is delivered.",
))


# ======================================================================================
# Section 1 - Project Identity (REQ-004 .. REQ-007)
# ======================================================================================

add(T(
    "REQ-004-T01", "REQ-004",
    "The delivered repository identifies itself as the business case titled in the source document.",
    tree_contains([r"Loan\s+Origination\s*&\s*Underwriting\s+Copilot"],
                  "business case title declared in repository documentation", DOCS),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan every committed Markdown document in the implementation.",
           "Look for the business case title exactly as the source document states it."),
    expected="The business case title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.",
    evidence="File path and line number of the matched title.",
))

add(T(
    "REQ-005-T01", "REQ-005",
    "The delivered repository is identifiable as business case BC-AAIE-HACK-02.",
    tree_contains([r"BC-AAIE-HACK-02"], "business case ID declared in the repository", ALLTEXT),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan the repository's documentation and project metadata files.",
           "Look for the literal business case ID."),
    expected="The business case ID 'BC-AAIE-HACK-02' appears in the repository.",
    evidence="File path and line number of the matched ID.",
))

add(T(
    "REQ-006-T01", "REQ-006",
    "The delivered repository declares its domain as Banking & Finance.",
    tree_contains([r"Banking\s*&\s*Finance|Banking and Finance"],
                  "domain declared in repository documentation", DOCS),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan committed Markdown documentation for the declared domain.",),
    expected="The domain 'Banking & Finance' appears in the repository documentation.",
    evidence="File path and line number of the matched domain statement.",
))

add(T(
    "REQ-007-T01", "REQ-007",
    "The delivered repository declares the project type stated in the source document.",
    tree_contains([r"Agentic\s+AI\s+Engineer\s+Pathway", r"Capstone\s+Hackathon"],
                  "project type declared in repository documentation", DOCS, mode="all"),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan committed Markdown documentation.",
           "Require both halves of the project type: the pathway and the capstone hackathon."),
    expected="The project type 'Agentic AI Engineer Pathway - Cross-Cutting Capstone Hackathon' is declared.",
    evidence="File paths and line numbers for both matched fragments.",
))


# ======================================================================================
# Section 2 - Engagement Overview (REQ-008 .. REQ-017)
# ======================================================================================

add(manual_T(
    "REQ-008-T01", "REQ-008",
    "The engagement ran for the stated duration.",
    "the 20-hour engagement duration",
    test_type="GOVERNANCE_TEST",
    expected="A reviewer records that the engagement duration was 20 hours.",
))

add(manual_T(
    "REQ-009-T01", "REQ-009",
    "The delivery team matched the stated team size.",
    "a team of 2-4 people",
    test_type="GOVERNANCE_TEST",
    expected="A reviewer records that the team size was within 2-4.",
))

add(T(
    "REQ-010-T01", "REQ-010",
    "The submission is a Git repository, which is what the stated evaluation mode reviews.",
    is_git_repository(),
    test_type="GOVERNANCE_TEST",
    steps=("Confirm a .git directory exists at the implementation root.",
           "Run 'git ls-files' and count the tracked files."),
    expected="The implementation root is a Git repository with tracked files.",
    evidence="git ls-files output count.",
))

add(manual_T(
    "REQ-010-T02", "REQ-010",
    "The review was performed automatically against the Hackathon Rubric with no live demo judging.",
    "an automated review against the Hackathon Rubric (7 categories / 100 marks), with no live demo judging",
    test_type="GOVERNANCE_TEST",
    expected="A reviewer records that scoring was automated, rubric-based, and included no live demo judging.",
))

add(T(
    "REQ-011-T01", "REQ-011",
    "The repository has been pushed to a remote, as the submission instruction requires.",
    git_has_remote(),
    test_type="GOVERNANCE_TEST",
    steps=("Run 'git remote -v' in the implementation root.",),
    expected="At least one Git remote is configured.",
    evidence="The 'git remote -v' output.",
))

add(T(
    "REQ-011-T02", "REQ-011",
    "The configured remote is a GitLab project, as the submission instruction names.",
    remote_matches_gitlab,
    test_type="GOVERNANCE_TEST",
    steps=("Run 'git remote -v'.",
           "Require at least one remote URL naming GitLab."),
    expected="A configured Git remote URL identifies a GitLab project.",
    evidence="The matching remote URL.",
))

add(unspecified_T(
    "REQ-011-T03", "REQ-011",
    "The push happened by the cut-off.",
    "the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project",
    test_type="GOVERNANCE_TEST",
))

add(manual_T(
    "REQ-012-T01", "REQ-012",
    "The per-team Excel review report with its five stated sections was produced.",
    "a per-team Excel report containing the Summary, Categories, Scorecard, Detailed and Improvement sections",
    test_type="GOVERNANCE_TEST",
    expected="A reviewer records that the Excel report exists with all five named sections.",
))

add(manual_T(
    "REQ-013-T01", "REQ-013",
    "The stated grade bands were applied.",
    "the grade bands Pass >= 60 and Not Yet Passed < 60",
    test_type="GOVERNANCE_TEST",
    expected="A reviewer records that the Pass >= 60 / Not Yet Passed < 60 bands were applied to the score.",
))

# REQ-014 names ten separately verifiable constituents of the evaluated system.
add(T(
    "REQ-014-T01", "REQ-014",
    "A working LangGraph multi-agent system exists.",
    all_of("LangGraph multi-agent system",
           file_exists("src/graph.py"),
           dependency_declared(["langgraph"], "LangGraph declared as a dependency")),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the graph module.", "Confirm LangGraph is a declared dependency."),
    expected="A LangGraph graph module is present and LangGraph is a declared dependency.",
))

add(T(
    "REQ-014-T02", "REQ-014", "Context engineering is present as part of the foundation.",
    dir_exists("src/context"),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the context-engineering package.",),
    expected="A context-engineering module/package exists and is non-empty.",
))

add(T(
    "REQ-014-T03", "REQ-014", "Tiered memory is present as part of the foundation.",
    dir_exists("src/memory"),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the memory package.",),
    expected="A memory module/package exists and is non-empty.",
))

add(T(
    "REQ-014-T04", "REQ-014", "A custom MCP server is present as part of the foundation.",
    dir_exists("mcp_server"),
    test_type="INTEGRATION_TEST",
    steps=("Locate the MCP server package.",),
    expected="A custom MCP server package exists and is non-empty.",
))

add(T(
    "REQ-014-T05", "REQ-014", "An agentic-RAG tool is present as part of the foundation.",
    file_exists("src/tools/rag_tool.py"),
    test_type="INTEGRATION_TEST",
    steps=("Locate the agentic-RAG tool module.",),
    expected="An agentic-RAG tool module exists.",
))

add(T(
    "REQ-014-T06", "REQ-014", "Arize Phoenix observability instruments the system.",
    all_of("Arize Phoenix observability",
           file_exists("src/observability/tracing.py"),
           dependency_declared(["arize-phoenix"], "arize-phoenix declared as a dependency")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the tracing module.", "Confirm arize-phoenix is a declared dependency."),
    expected="A Phoenix tracing module exists and arize-phoenix is a declared dependency.",
))

add(T(
    "REQ-014-T07", "REQ-014", "Cost & latency governance is present.",
    all_of("cost and latency governance artifacts",
           file_exists("reports/golden_signals.json"),
           any_of("cost/latency dashboard",
                  file_exists("reports/dashboard.png"),
                  file_exists("reports/dashboard_data.csv"))),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the golden-signals report.", "Locate the cost/latency dashboard artifacts."),
    expected="Golden-signals and cost/latency dashboard artifacts exist.",
))

add(T(
    "REQ-014-T08", "REQ-014", "Guardrails & audit are present.",
    all_of("guardrails and audit",
           dir_exists("src/guardrails"),
           file_exists("logs/agent_actions.jsonl")),
    test_type="SECURITY_TEST",
    steps=("Locate the guardrails package.", "Locate the audit trail artifact."),
    expected="A guardrails package and an audit-trail artifact both exist.",
))

add(T(
    "REQ-014-T09", "REQ-014", "Governance/compliance documentation is present.",
    all_of("governance and compliance documentation",
           file_exists("docs/risk-register.md"),
           file_exists("docs/model-card.md"),
           file_exists("docs/compliance.md"),
           file_exists("docs/output-risk.md")),
    test_type="GOVERNANCE_TEST",
    steps=("Locate each of the four governance documents named by the document.",),
    expected="The risk register, model card, compliance mapping and output-risk classification all exist.",
))

add(T(
    "REQ-014-T10", "REQ-014", "Agent-level evaluation & testing are present.",
    all_of("agent-level evaluation and tests",
           file_exists("reports/eval_report.json"),
           file_exists("tests/test_routing.py"),
           file_exists("tests/test_loops.py"),
           file_exists("tests/test_tool_contracts.py")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the evaluation report.", "Locate the three named agent test modules."),
    expected="An evaluation report and the three named agent test modules exist.",
))

add(T(
    "REQ-015-T01", "REQ-015",
    "Claims can be scored from committed evidence because the deliverable is a Git repository.",
    is_git_repository(),
    test_type="AUDITABILITY_TEST",
    steps=("Confirm the implementation root is a Git repository.",),
    expected="The implementation is a Git repository, so its artifacts can be committed evidence.",
))

add(T(
    "REQ-015-T02", "REQ-015",
    "Every evidence artifact that exists on disk is committed, not merely present in a working tree.",
    all_named_evidence_committed,
    test_type="AUDITABILITY_TEST",
    steps=("Enumerate the evidence artifacts the source document names by path.",
           "For each one present on disk, confirm 'git ls-files' lists it.",
           "Report any artifact that exists but is uncommitted."),
    expected="No evidence artifact exists uncommitted; every present artifact is git-tracked.",
    evidence="For each artifact: its path and its presence or absence in 'git ls-files'.",
))

add(T(
    "REQ-016-T01", "REQ-016",
    "This validation suite does not score what the source document excludes from evaluation.",
    suite_excludes_unscored_topics,
    test_type="GOVERNANCE_TEST",
    steps=("Inspect every test case in this registry.",
           "Confirm none of them scores interface visual polish, raw unit-test volume, or a "
           "particular optional deployment path."),
    expected="No registered test scores visual polish, generic unit-test volume, or a chosen deployment path.",
    evidence="The registry scan result, listing any offending test IDs.",
    preconditions="The test registry is importable.",
))

add(T(
    "REQ-017-T01", "REQ-017",
    "Running the system does not depend on containerized or cloud deployment.",
    no_container_command_in_readme,
    test_type="NEGATIVE_TEST",
    steps=("Read the implementation's README.md.",
           "Search its documented commands for docker / docker-compose / kubectl / helm.",
           "Require that none is present."),
    expected="The documented run path contains no containerized or cloud deployment command.",
    evidence="The README lines searched, and any container command found.",
    pass_condition="README.md exists and documents no container or cloud deployment command.",
    fail_condition="A docker / docker-compose / kubectl / helm command appears in the documented run "
                   "path, or no README.md exists from which the run path could be established.",
))


# ======================================================================================
# Section 3.1 / 3.2 - Problem and Role (REQ-018 .. REQ-022)
# ======================================================================================

add(T(
    "REQ-018-T01", "REQ-018",
    "The manual loan-officer activities the document names are the activities the delivered system documents itself as covering.",
    tree_contains(
        [r"document", r"eligibilit", r"affordabilit", r"risk", r"rationale|recommendation"],
        "the five manual activities named in the problem statement", DOCS, mode="all",
    ),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan committed Markdown documentation.",
           "Require each activity named in the problem statement to be addressed: gathering "
           "documents, checking eligibility, computing affordability, screening risk flags, "
           "drafting a decision rationale."),
    expected="All five manual activities named in the problem statement are addressed in the documentation.",
))

add(T(
    "REQ-019-T01", "REQ-019",
    "Lending rules are retrieved from a policy corpus rather than being fixed in code, so changes are picked up.",
    all_of("policy retrieved from a corpus",
           dir_exists("data/policy_corpus"),
           file_exists("src/tools/rag_tool.py")),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the policy corpus directory.",
           "Locate the retrieval tool that reads it."),
    expected="A policy corpus and a retrieval tool over it both exist, so changed rules are re-read rather than re-coded.",
))

add(T(
    "REQ-020-T01", "REQ-020", "The copilot ingests a loan application.",
    all_of("loan application ingestion",
           sample_inputs_committed("committed loan application inputs"),
           tree_contains([r"applicat"], "application handling in source", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Locate committed sample loan applications.",
           "Confirm the source code handles applications."),
    expected="Committed loan application inputs exist and the code ingests them.",
))

add(T(
    "REQ-020-T02", "REQ-020", "The copilot retrieves the current lending policy.",
    all_of("current lending policy retrieval",
           file_exists("src/tools/rag_tool.py"),
           dir_exists("data/policy_corpus")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the policy-retrieval tool and the lending-policy corpus.",),
    expected="A policy-retrieval capability over a lending-policy corpus exists.",
))

add(T(
    "REQ-020-T03", "REQ-020", "The copilot computes eligibility and affordability.",
    tree_contains([r"eligib", r"afford"], "eligibility and affordability computation", (".py",),
                  mode="all"),
    test_type="STATIC_TEST",
    steps=("Search the implementation's Python sources for eligibility and affordability logic.",),
    expected="Both eligibility and affordability computation are implemented.",
))

add(T(
    "REQ-020-T04", "REQ-020", "The copilot screens risk.",
    tree_contains([r"risk"], "risk screening in source", (".py",)),
    test_type="STATIC_TEST",
    steps=("Search the implementation's Python sources for risk screening.",),
    expected="Risk screening is implemented.",
))

add(T(
    "REQ-020-T05", "REQ-020", "The copilot drafts an auditable decision recommendation.",
    all_of("auditable decision recommendation",
           tree_contains([r"approve", r"refer", r"decline"], "decision vocabulary in source",
                         (".py",), mode="all"),
           file_exists("logs/agent_actions.jsonl")),
    test_type="AUDITABILITY_TEST",
    steps=("Confirm the decision vocabulary exists in the code.",
           "Confirm an audit trail records the decision, making it auditable."),
    expected="A decision recommendation is produced and recorded in an audit trail.",
))

add(T(
    "REQ-020-T06", "REQ-020", "A human makes the final call rather than the system auto-deciding.",
    tree_contains([r"human[_\- ]?(in[_\- ]?the[_\- ]?loop|review|approval)|escalat"],
                  "human-in-the-loop final decision", (".py",)),
    test_type="WORKFLOW_TEST",
    steps=("Search the implementation for a human-review / escalation path.",),
    expected="A human-review or escalation path exists so a human makes the final call.",
))

add(T(
    "REQ-021-T01", "REQ-021", "The delivered work is presented as the work of the stated role.",
    tree_contains([r"Agentic\s+AI\s+Engineer"], "the stated role named in documentation", DOCS),
    test_type="DOCUMENTATION_TEST",
    steps=("Scan committed Markdown documentation for the role statement.",),
    expected="The role 'Agentic AI Engineer' is named in the repository documentation.",
))

add(T(
    "REQ-022-T01", "REQ-022", "A LangGraph multi-agent copilot is built.",
    all_of("LangGraph multi-agent copilot",
           file_exists("src/graph.py"),
           py_imports(["langgraph"], "LangGraph imported by the implementation")),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the graph module.", "Confirm langgraph is imported."),
    expected="A LangGraph-based graph module exists and imports langgraph.",
))

add(T(
    "REQ-022-T02", "REQ-022", "The copilot is instrumented with Arize Phoenix.",
    all_of("Arize Phoenix instrumentation",
           file_exists("src/observability/tracing.py"),
           py_imports(["phoenix", "openinference"], "Phoenix/openinference imported", mode="any")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the tracing module.", "Confirm Phoenix or openinference is imported."),
    expected="Phoenix instrumentation code exists and imports the Phoenix/openinference stack.",
))

add(T(
    "REQ-022-T03", "REQ-022", "Cost and latency are governed.",
    file_exists("reports/golden_signals.json"),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the golden-signals report that carries the latency and cost figures.",),
    expected="A golden-signals report exists as the cost and latency governance artifact.",
))

add(T(
    "REQ-022-T04", "REQ-022", "The copilot is hardened with guardrails and an audit trail.",
    all_of("guardrails and audit trail",
           dir_exists("src/guardrails"),
           file_exists("logs/agent_actions.jsonl")),
    test_type="SECURITY_TEST",
    steps=("Locate the guardrails package and the audit trail artifact.",),
    expected="Guardrail code and an audit trail both exist.",
))

add(T(
    "REQ-022-T05", "REQ-022", "Risk and compliance posture are documented.",
    all_of("risk and compliance documentation",
           file_exists("docs/risk-register.md"),
           file_exists("docs/compliance.md")),
    test_type="GOVERNANCE_TEST",
    steps=("Locate the risk register and the compliance mapping.",),
    expected="Risk and compliance posture documents exist.",
))

add(T(
    "REQ-022-T06", "REQ-022", "Behaviour is proven with agent-level evaluation and tests.",
    all_of("agent-level evaluation and tests",
           file_exists("reports/eval_report.json"),
           file_exists("tests/test_routing.py"),
           file_exists("tests/test_loops.py"),
           file_exists("tests/test_tool_contracts.py")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the evaluation report and the three agent test modules.",),
    expected="An evaluation report and the three named agent tests exist.",
))

add(T(
    "REQ-022-T07", "REQ-022", "Every artifact is delivered as committed evidence.",
    all_named_evidence_committed,
    test_type="AUDITABILITY_TEST",
    steps=("Enumerate the artifacts the document names by path.",
           "Confirm each one present on disk is git-tracked."),
    expected="Every present artifact is committed evidence.",
))


# ======================================================================================
# Section 3.3 - Expected Solution (REQ-023 .. REQ-028)
# ======================================================================================

add(T(
    "REQ-023-T01", "REQ-023", "The application is delivered as a Git repository.",
    is_git_repository(),
    test_type="AUDITABILITY_TEST",
    steps=("Confirm the implementation root is a Git repository with tracked files.",),
    expected="The deliverable is a Git repository.",
))

add(T(
    "REQ-023-T02", "REQ-023",
    "The delivered application is a working, instrumented multi-agent application.",
    all_of("working instrumented multi-agent application",
           file_exists("src/graph.py"),
           file_exists("src/observability/tracing.py"),
           any_of("a committed trace export proving it ran",
                  file_exists("traces/phoenix_spans.parquet"),
                  file_exists("traces/phoenix_spans.jsonl"))),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the multi-agent graph.",
           "Locate the instrumentation module.",
           "Locate a committed trace export, which only exists if the system actually ran."),
    expected="A multi-agent graph, instrumentation, and a trace export from a real run all exist.",
))

add(T(
    "REQ-024-T01", "REQ-024", "The LangGraph graph uses typed state.",
    tree_contains([r"TypedDict|BaseModel|Annotated\[|@dataclass|pydantic"],
                  "typed state definition", (".py",)),
    test_type="ARCHITECTURE_TEST",
    steps=("Search the implementation for a typed state definition.",),
    expected="The graph state is typed (TypedDict, pydantic model, or dataclass).",
))

add(T(
    "REQ-024-T02", "REQ-024", "A supervisor routes loan applications to worker agents.",
    tree_contains([r"supervisor"], "supervisor routing node", (".py",)),
    test_type="ARCHITECTURE_TEST",
    steps=("Search the implementation for a supervisor router.",),
    expected="A supervisor component routes applications to workers.",
))

add(T(
    "REQ-024-T03", "REQ-024", "The three specialized worker agents the document names all exist.",
    tree_contains(
        [r"eligib.*afford|afford.*eligib|eligibility_and_affordability",
         r"policy[_\- ]?retriev",
         r"risk[_\- ]?screen"],
        "the three named worker agents", (".py",), mode="all",
    ),
    test_type="ARCHITECTURE_TEST",
    steps=("Search for an eligibility-and-affordability agent.",
           "Search for a policy-retrieval agent.",
           "Search for a risk-screening agent."),
    expected="An eligibility-and-affordability agent, a policy-retrieval agent and a risk-screening agent all exist.",
))

add(T(
    "REQ-024-T04", "REQ-024", "The graph uses conditional routing.",
    py_calls(["add_conditional_edges"], "conditional routing wired into the graph"),
    test_type="ARCHITECTURE_TEST",
    steps=("Analyse the Python AST for a call adding conditional edges to the graph.",),
    expected="Conditional routing is wired into the graph, not merely described.",
))

add(T(
    "REQ-024-T05", "REQ-024", "The graph uses checkpointing.",
    all_of("checkpointing",
           tree_contains([r"checkpoint"], "checkpointer configured", (".py",)),
           py_calls(["compile"], "graph compiled, which is where a checkpointer is attached")),
    test_type="ARCHITECTURE_TEST",
    steps=("Search for checkpointer configuration.",
           "Confirm the graph is compiled, which is where a checkpointer is attached."),
    expected="A checkpointer is configured on the compiled graph.",
))

add(T(
    "REQ-024-T06", "REQ-024", "The graph produces structured output.",
    tree_contains([r"with_structured_output|response_format|BaseModel|TypedDict|model_json_schema"],
                  "structured output at the graph boundary", (".py",)),
    test_type="OUTPUT_VALIDATION_TEST",
    steps=("Search for structured-output binding or a schema type used for node output.",),
    expected="Structured output is produced rather than free text only.",
))

add(T(
    "REQ-025-T01", "REQ-025", "A custom MCP server exists with at least 2 tools and 1 resource.",
    mcp_surface,
    test_type="INTEGRATION_TEST",
    steps=("Locate the MCP server package.",
           "Count distinct MCP tool registrations; require >= 2.",
           "Count distinct MCP resource registrations; require >= 1."),
    expected="The MCP server exposes at least 2 tools and at least 1 resource.",
    evidence="The registered tool and resource names found in the MCP server sources.",
))

add(T(
    "REQ-025-T02", "REQ-025", "The MCP server is consumed via langchain-mcp-adapters.",
    all_of("langchain-mcp-adapters consumption",
           dependency_declared(["langchain-mcp-adapters"], "langchain-mcp-adapters declared"),
           py_imports(["langchain_mcp_adapters"], "langchain_mcp_adapters imported")),
    test_type="INTEGRATION_TEST",
    steps=("Confirm langchain-mcp-adapters is a declared dependency.",
           "Confirm it is imported by the implementation."),
    expected="The MCP server is consumed through langchain-mcp-adapters.",
))

add(T(
    "REQ-025-T03", "REQ-025", "Engineered context implements write, select, compress and isolate.",
    tree_contains([r"\bwrite\b", r"\bselect\b", r"\bcompress\b", r"\bisolate\b"],
                  "the four context operations", (".py",), mode="all", under="src/context"),
    test_type="ARCHITECTURE_TEST",
    steps=("Search the context package for each of write, select, compress and isolate.",),
    expected="All four context operations are implemented.",
))

add(T(
    "REQ-025-T04", "REQ-025", "Context engineering includes summarization.",
    tree_contains([r"summar"], "summarization in the context layer", (".py",), under="src/context"),
    test_type="ARCHITECTURE_TEST",
    steps=("Search the context package for summarization.",),
    expected="Summarization is implemented in the context layer.",
))

add(T(
    "REQ-025-T05", "REQ-025", "Untrusted applicant-supplied text is quarantined.",
    tree_contains([r"quarantin"], "quarantine of untrusted applicant-supplied text", (".py",)),
    test_type="SECURITY_TEST",
    steps=("Search the implementation for quarantine handling of untrusted text.",),
    expected="Untrusted applicant-supplied text is quarantined.",
))

add(T(
    "REQ-025-T06", "REQ-025", "Tiered memory has verified cross-session persistence.",
    all_of("verified cross-session persistence",
           dir_exists("src/memory"),
           file_exists("tests/test_memory_persistence.py"),
           file_exists("logs/memory_test.log")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the memory package.",
           "Locate the cross-session persistence test.",
           "Locate the committed output log that verifies it ran."),
    expected="Tiered memory exists with a persistence test and a committed output log proving it was verified.",
))

add(T(
    "REQ-025-T07", "REQ-025", "An agentic-RAG tool operates over a synthetic lending-policy corpus.",
    all_of("agentic-RAG over a synthetic lending-policy corpus",
           file_exists("src/tools/rag_tool.py"),
           dir_exists("data/policy_corpus")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the RAG tool.", "Locate the lending-policy corpus it retrieves over."),
    expected="A RAG tool and a lending-policy corpus both exist.",
))

add(T(
    "REQ-026-T01", "REQ-026", "Arize Phoenix instrumentation has a committed trace export.",
    all_of("committed Phoenix trace export",
           any_of("trace export artifact",
                  file_exists("traces/phoenix_spans.parquet"),
                  file_exists("traces/phoenix_spans.jsonl")),
           any_of("the export is committed",
                  committed("traces/phoenix_spans.parquet"),
                  committed("traces/phoenix_spans.jsonl"))),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the trace export in Parquet or JSONL form.", "Confirm git tracks it."),
    expected="A Phoenix trace export exists and is committed.",
))

add(T(
    "REQ-026-T02", "REQ-026", "A machine-generated tool-invocation log exists.",
    artifact_has_producing_code(
        "logs/tool_calls.jsonl",
        [r"tool_calls\.jsonl", r"tool[_\- ]?call.*(?:append|write|dump)"],
        "machine-generated tool-invocation log",
    ),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate logs/tool_calls.jsonl.",
           "Locate the committed code that writes it, so it is machine-generated rather than hand-written."),
    expected="The tool-invocation log exists and committed code produces it.",
))

add(T(
    "REQ-026-T03", "REQ-026", "An evidence-linked failure-mode analysis exists.",
    all_of("evidence-linked failure-mode analysis",
           file_exists("docs/failure-analysis.md"),
           file_contains("docs/failure-analysis.md", [r"run_id", r"span_id"],
                         "Phoenix evidence links", mode="any")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate docs/failure-analysis.md.",
           "Confirm it links to Phoenix evidence via run_id / span_id."),
    expected="A failure-mode analysis exists and links to trace evidence.",
))

add(T(
    "REQ-027-T01", "REQ-027", "A Phoenix-derived golden-signals report exists.",
    file_exists("reports/golden_signals.json"),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the golden-signals report.",),
    expected="reports/golden_signals.json exists.",
))

add(T(
    "REQ-027-T02", "REQ-027", "A cost/latency dashboard exists.",
    all_of("cost/latency dashboard",
           file_exists("reports/dashboard.png"),
           file_exists("reports/dashboard_data.csv")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the dashboard screenshot and its underlying data file.",),
    expected="Both the dashboard image and its underlying data file exist.",
))

add(T(
    "REQ-027-T03", "REQ-027", "Input/output guardrails exist.",
    dir_exists("src/guardrails"),
    test_type="SECURITY_TEST",
    steps=("Locate the guardrails package.",),
    expected="A guardrails package exists.",
))

add(T(
    "REQ-027-T04", "REQ-027", "An audit trail exists.",
    file_exists("logs/agent_actions.jsonl"),
    test_type="AUDITABILITY_TEST",
    steps=("Locate the audit trail artifact.",),
    expected="logs/agent_actions.jsonl exists.",
))

add(T(
    "REQ-027-T05", "REQ-027", "Secrets hygiene is in place.",
    all_of("secrets hygiene", file_exists(".env.example"), file_exists(".gitignore")),
    test_type="SECURITY_TEST",
    steps=("Locate .env.example and .gitignore.",),
    expected="Both .env.example and .gitignore exist.",
))

add(T(
    "REQ-027-T06", "REQ-027", "The governance pack contains all four named documents.",
    all_of("governance pack",
           file_exists("docs/risk-register.md"),
           file_exists("docs/model-card.md"),
           file_exists("docs/compliance.md"),
           file_exists("docs/output-risk.md")),
    test_type="GOVERNANCE_TEST",
    steps=("Locate the risk register, model card, compliance mapping and output-risk classification.",),
    expected="All four governance pack documents exist.",
))

add(T(
    "REQ-028-T01", "REQ-028", "Agent-level evaluation covers LLM-as-judge and hallucination.",
    all_of("LLM-as-judge and hallucination evaluation",
           file_exists("reports/eval_report.json"),
           json_keys("reports/eval_report.json", ["hallucinat"],
                     "hallucination metric in the eval report")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the evaluation report.", "Confirm it carries a hallucination metric."),
    expected="An evaluation report exists and reports a hallucination metric.",
))

add(T(
    "REQ-028-T02", "REQ-028", "The routing-logic agent test exists.",
    file_exists("tests/test_routing.py"),
    test_type="INTEGRATION_TEST",
    steps=("Locate tests/test_routing.py.",),
    expected="The routing-logic test module exists.",
))

add(T(
    "REQ-028-T03", "REQ-028", "The loop/cascade guard agent test exists.",
    file_exists("tests/test_loops.py"),
    test_type="INTEGRATION_TEST",
    steps=("Locate tests/test_loops.py.",),
    expected="The loop/cascade guard test module exists.",
))

add(T(
    "REQ-028-T04", "REQ-028", "The tool-contract agent test exists.",
    file_exists("tests/test_tool_contracts.py"),
    test_type="INTEGRATION_TEST",
    steps=("Locate tests/test_tool_contracts.py.",),
    expected="The tool-contract test module exists.",
))

add(T(
    "REQ-028-T05", "REQ-028", "A reproducible local-run runbook exists.",
    all_of("local-run runbook",
           file_exists("README.md"),
           file_contains("README.md", [r"```"], "a documented runnable command block", mode="any")),
    test_type="DOCUMENTATION_TEST",
    steps=("Locate README.md.", "Confirm it documents at least one runnable command."),
    expected="A README runbook documents how to run the system.",
))


# ======================================================================================
# Section 3.4 - Applicable Rules (REQ-029 .. REQ-033)
# ======================================================================================

add(T(
    "REQ-029-T01", "REQ-029",
    "Only committed artifacts can be scored, so every named artifact present is committed.",
    all_named_evidence_committed,
    test_type="AUDITABILITY_TEST",
    steps=("Enumerate the artifacts the source document names by path.",
           "Confirm each present artifact is listed by 'git ls-files'."),
    expected="No named artifact exists uncommitted.",
))

add(T(
    "REQ-029-T02", "REQ-029",
    "Each evidence artifact has producing code, so it is not a hand-written metric, trace or log.",
    evidence_artifacts_have_producers,
    test_type="AUDITABILITY_TEST",
    steps=("For each machine-generated evidence artifact named by the document, search committed "
           "Python sources for code that writes it.",
           "Report any artifact with no producing code."),
    expected="Every evidence artifact has committed producing code.",
    evidence="For each artifact: the producing source file and line, or a statement that none exists.",
))

add(T(
    "REQ-030-T01", "REQ-030", "Citations in the failure-mode analysis resolve to committed artifacts.",
    citations_resolve("docs/failure-analysis.md", 1, "failure-analysis citations"),
    test_type="AUDITABILITY_TEST",
    steps=("Extract every file-path citation from docs/failure-analysis.md.",
           "Resolve each to a committed artifact.",
           "Treat unresolvable citations as missing."),
    expected="Every citation in the failure-mode analysis resolves to a committed artifact.",
))

add(T(
    "REQ-030-T02", "REQ-030", "Citations in the governance pack resolve to committed artifacts.",
    all_of("governance pack citations resolve",
           citations_resolve("docs/risk-register.md", 1, "risk register citations"),
           citations_resolve("docs/model-card.md", 1, "model card citations"),
           citations_resolve("docs/compliance.md", 1, "compliance mapping citations"),
           citations_resolve("docs/output-risk.md", 1, "output-risk citations")),
    test_type="AUDITABILITY_TEST",
    steps=("Extract file-path citations from each governance document.",
           "Resolve each citation to a committed artifact."),
    expected="Every citation in each of the four governance documents resolves to a committed artifact.",
))

add(T(
    "REQ-031-T01", "REQ-031", "Loan applications and lending policies are synthetic.",
    tree_contains([r"synthetic"], "synthetic data declared for applications and policies",
                  (".md", ".py", ".json")),
    test_type="DATA_VALIDATION_TEST",
    steps=("Search the repository for the declaration that the application and policy data is synthetic.",),
    expected="The loan application and lending policy data is declared synthetic.",
))

add(T(
    "REQ-031-T02", "REQ-031",
    "No real-format account or card numbers are written in plaintext anywhere in the repository.",
    tree_absent(
        [r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"],
        "unmasked payment-card numbers",
        (".py", ".md", ".txt", ".json", ".jsonl", ".csv", ".log", ".yaml", ".yml"),
    ),
    test_type="NEGATIVE_TEST",
    steps=("Scan every committed text artifact for card numbers matching the major issuer patterns.",),
    expected="No unmasked card number appears anywhere in the repository.",
    evidence="The scanned file count, and any matching file and line.",
))

add(T(
    "REQ-031-T03", "REQ-031",
    "Applicant PII is masked where shown and never written to logs in plaintext.",
    masking_present,
    test_type="SECURITY_TEST",
    steps=("Confirm masking/redaction code exists in the implementation.",
           "Scan the committed logs for unmasked account, card and credit identifiers."),
    expected="Masking is implemented and no committed log contains plaintext sensitive identifiers.",
))

add(T(
    "REQ-032-T01", "REQ-032", "Google Gemini is used as the model provider.",
    all_of("Google Gemini as model provider",
           dependency_declared(["google-genai", "google-generativeai", "langchain-google-genai"],
                               "a Google Gemini SDK declared", mode="any"),
           tree_contains([r"gemini"], "Gemini referenced in the implementation", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Confirm a Google Gemini SDK is a declared dependency.",
           "Confirm Gemini is referenced in the implementation sources."),
    expected="Google Gemini is the configured model provider.",
))

add(T(
    "REQ-032-T02", "REQ-032", "Claude is not used as a model provider.",
    all_of("no Claude provider",
           tree_absent([r"anthropic", r"\bclaude-\w"], "Claude/Anthropic provider usage", (".py",)),
           tree_absent([r"(?m)^\s*anthropic\b", r"(?m)^\s*langchain[-_]anthropic\b"],
                       "Claude/Anthropic dependency declaration", MANIFESTS)),
    test_type="NEGATIVE_TEST",
    steps=("Scan the implementation sources for Anthropic/Claude provider usage.",
           "Scan the dependency manifests for an Anthropic client."),
    expected="No Anthropic/Claude model provider is used or declared.",
    evidence="Scanned file count, and any offending file and line.",
))

add(T(
    "REQ-032-T03", "REQ-032", "The project builds, runs and evaluates with pip + Python.",
    all_of("pip + Python toolchain",
           any_of("a pip-installable dependency manifest",
                  file_exists("requirements.txt"), file_exists("pyproject.toml")),
           file_contains("README.md", [r"pip\s+install"], "documented pip install step", mode="any")),
    test_type="CONFIGURATION_TEST",
    steps=("Locate a pip-installable dependency manifest.",
           "Confirm the README documents a pip install step."),
    expected="The project installs and runs through pip + Python.",
))

add(T(
    "REQ-032-T04", "REQ-032", "No Docker or external database service is required for this cut.",
    all_of("no Docker or external DB service required",
           no_files_matching(["Dockerfile", "docker-compose*.yml", "docker-compose*.yaml",
                              "*.dockerfile", "compose.yaml", "compose.yml"],
                             "container build/orchestration files"),
           tree_absent([r"\bpostgres(ql)?://", r"\bmysql://", r"\bmongodb(\+srv)?://", r"\bredis://"],
                       "external database service connection strings",
                       (".py", ".md", ".txt", ".toml", ".cfg", ".yaml", ".yml", ".example"))),
    test_type="NEGATIVE_TEST",
    steps=("Confirm no Dockerfile or compose file exists.",
           "Scan for external database service connection strings."),
    expected="Neither Docker nor an external database service is required.",
))

add(T(
    "REQ-033-T01", "REQ-033",
    "A single documented command regenerates the system, its traces and its evaluation.",
    documented_commands,
    test_type="DOCUMENTATION_TEST",
    steps=("Read the implementation's README.md.",
           "Extract the documented commands.",
           "Require a documented command for the run, for regenerating Phoenix traces, and for the evaluation."),
    expected="README.md documents the commands that regenerate the system, its traces and its evaluation.",
    evidence="The documented command lines found in README.md.",
))

add(T(
    "REQ-033-T02", "REQ-033", "Sample inputs are committed so the run is reproducible.",
    sample_inputs_committed(),
    test_type="CONFIGURATION_TEST",
    steps=("Search the conventional input locations for committed sample inputs.",),
    expected="Committed sample inputs exist.",
))


# ======================================================================================
# Section 4 - Technology & Framework Stack (REQ-034 .. REQ-043)
# ======================================================================================

add(T(
    "REQ-034-T01", "REQ-034", "Google Gemini is the only model provider in the toolchain.",
    all_of("Gemini is the only model provider",
           dependency_declared(["google-genai", "google-generativeai", "langchain-google-genai"],
                               "a Google Gemini SDK declared", mode="any"),
           tree_absent([r"(?m)^\s*(anthropic|openai|cohere|mistralai|together|replicate)\b"],
                       "a competing model-provider dependency", MANIFESTS)),
    test_type="CONFIGURATION_TEST",
    steps=("Confirm a Gemini SDK is declared.", "Confirm no other model-provider SDK is declared."),
    expected="Gemini is declared and no other model provider is.",
))

add(T(
    "REQ-034-T02", "REQ-034", "Everything installs with pip.",
    any_of("pip-installable manifest", file_exists("requirements.txt"), file_exists("pyproject.toml")),
    test_type="CONFIGURATION_TEST",
    steps=("Locate a pip-installable dependency manifest.",),
    expected="A pip-installable dependency manifest exists.",
))

add(T(
    "REQ-034-T03", "REQ-034", "No Docker or external DB service is required.",
    all_of("no Docker or external DB service",
           no_files_matching(["Dockerfile", "docker-compose*.yml", "docker-compose*.yaml",
                              "compose.yaml", "compose.yml"], "container build/orchestration files"),
           tree_absent([r"\bpostgres(ql)?://", r"\bmysql://", r"\bmongodb(\+srv)?://", r"\bredis://"],
                       "external database service connection strings",
                       (".py", ".md", ".txt", ".toml", ".cfg", ".yaml", ".yml", ".example"))),
    test_type="NEGATIVE_TEST",
    steps=("Confirm no container build or orchestration file exists.",
           "Scan for external database connection strings."),
    expected="No Docker or external DB service is required.",
))

add(T(
    "REQ-035-T01", "REQ-035", "The project declares Python 3.11 or newer.",
    python_version_declared("3.11"),
    test_type="CONFIGURATION_TEST",
    steps=("Search pyproject.toml, setup.cfg, .python-version, runtime.txt and README.md "
           "for a declared Python version.",),
    expected="Python 3.11+ is declared.",
))

add(T(
    "REQ-035-T02", "REQ-035", "LangGraph is the agent framework.",
    all_of("LangGraph agent framework",
           dependency_declared(["langgraph"], "langgraph declared"),
           py_imports(["langgraph"], "langgraph imported")),
    test_type="CONFIGURATION_TEST",
    steps=("Confirm langgraph is declared as a dependency.", "Confirm it is imported."),
    expected="LangGraph is declared and used.",
))

add(unspecified_T(
    "REQ-035-T03", "REQ-035", "LangGraph is used under the MIT licence.",
    "any licence artifact the implementation must carry to evidence LangGraph's MIT licence",
    test_type="GOVERNANCE_TEST",
))

add(T(
    "REQ-036-T01", "REQ-036", "Google Gemini is used through its API.",
    all_of("Gemini API usage",
           dependency_declared(["google-genai", "google-generativeai", "langchain-google-genai"],
                               "a Google Gemini SDK declared", mode="any"),
           tree_contains([r"gemini"], "Gemini model referenced", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Confirm a Gemini SDK is declared.", "Confirm a Gemini model is referenced in code."),
    expected="The Gemini API is the model provider in use.",
))

add(T(
    "REQ-036-T02", "REQ-036", "Claude is not used, since Gemini is the only approved provider.",
    tree_absent([r"anthropic", r"\bclaude-\w"], "Claude/Anthropic usage", (".py",) + MANIFESTS),
    test_type="NEGATIVE_TEST",
    steps=("Scan source and dependency manifests for Anthropic/Claude.",),
    expected="Claude is not used as a provider.",
))

add(T(
    "REQ-037-T01", "REQ-037", "The MCP Python SDK is used over stdio.",
    all_of("MCP Python SDK over stdio",
           dependency_declared(["mcp"], "the MCP Python SDK declared"),
           tree_contains([r"stdio"], "stdio transport configured", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Confirm the MCP Python SDK is declared.", "Confirm the stdio transport is used."),
    expected="The MCP Python SDK is used with the stdio transport.",
))

add(T(
    "REQ-037-T02", "REQ-037", "langchain-mcp-adapters provides interoperability.",
    all_of("langchain-mcp-adapters",
           dependency_declared(["langchain-mcp-adapters"], "langchain-mcp-adapters declared"),
           py_imports(["langchain_mcp_adapters"], "langchain_mcp_adapters imported")),
    test_type="INTEGRATION_TEST",
    steps=("Confirm langchain-mcp-adapters is declared.", "Confirm it is imported."),
    expected="langchain-mcp-adapters is declared and used.",
))

add(T(
    "REQ-038-T01", "REQ-038", "langgraph-checkpoint-sqlite provides the SQLite-file checkpointer.",
    all_of("langgraph-checkpoint-sqlite",
           dependency_declared(["langgraph-checkpoint-sqlite"], "langgraph-checkpoint-sqlite declared"),
           tree_contains([r"SqliteSaver|langgraph\.checkpoint\.sqlite|AsyncSqliteSaver"],
                         "SQLite checkpointer used", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Confirm langgraph-checkpoint-sqlite is declared.",
           "Confirm the SQLite checkpointer is used in code."),
    expected="The SQLite-file checkpointer is declared and used.",
))

add(T(
    "REQ-038-T02", "REQ-038", "LangMem provides the memory layer.",
    all_of("LangMem",
           dependency_declared(["langmem"], "langmem declared"),
           tree_contains([r"langmem"], "LangMem used", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Confirm langmem is declared.", "Confirm it is used in code."),
    expected="LangMem is declared and used.",
))

add(T(
    "REQ-039-T01", "REQ-039", "Chroma or FAISS provides retrieval.",
    any_of("Chroma or FAISS",
           all_of("Chroma", dependency_declared(["chromadb"], "chromadb declared"),
                  tree_contains([r"chroma"], "Chroma used", (".py",))),
           all_of("FAISS", dependency_declared(["faiss"], "faiss declared"),
                  tree_contains([r"faiss"], "FAISS used", (".py",)))),
    test_type="INTEGRATION_TEST",
    steps=("Check for Chroma as the vector store.",
           "Otherwise check for FAISS - the document permits either."),
    expected="Either Chroma or FAISS is declared and used.",
))

add(T(
    "REQ-039-T02", "REQ-039", "Sentence-Transformers provides local embeddings.",
    all_of("Sentence-Transformers (local)",
           dependency_declared(["sentence-transformers"], "sentence-transformers declared"),
           tree_contains([r"sentence_transformers|SentenceTransformer"],
                         "Sentence-Transformers used", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Confirm sentence-transformers is declared.", "Confirm it is used in code."),
    expected="Sentence-Transformers is declared and used locally.",
))

add(T(
    "REQ-040-T01", "REQ-040", "Arize Phoenix provides the mandated observability.",
    all_of("Arize Phoenix",
           dependency_declared(["arize-phoenix"], "arize-phoenix declared"),
           py_imports(["phoenix"], "phoenix imported")),
    test_type="OBSERVABILITY_TEST",
    steps=("Confirm arize-phoenix is declared.", "Confirm phoenix is imported."),
    expected="Arize Phoenix is declared and imported.",
))

add(T(
    "REQ-040-T02", "REQ-040", "OpenTelemetry / openinference instrumentation is present.",
    all_of("OpenTelemetry / openinference",
           dependency_declared(["openinference-instrumentation-langchain", "opentelemetry"],
                               "openinference/OpenTelemetry declared", mode="any"),
           py_imports(["openinference", "opentelemetry"], "openinference/OpenTelemetry imported",
                      mode="any")),
    test_type="OBSERVABILITY_TEST",
    steps=("Confirm an openinference/OpenTelemetry package is declared.", "Confirm it is imported."),
    expected="OpenTelemetry / openinference instrumentation is declared and imported.",
))

add(T(
    "REQ-040-T03", "REQ-040", "Phoenix runs locally and in-process.",
    tree_contains([r"px\.launch_app|phoenix\.launch_app|localhost:6006|127\.0\.0\.1:6006|register\("],
                  "local in-process Phoenix session", (".py", ".md")),
    test_type="OBSERVABILITY_TEST",
    steps=("Search for a local in-process Phoenix session or the local Phoenix endpoint.",),
    expected="Phoenix is configured to run locally and in-process.",
))

add(T(
    "REQ-041-T01", "REQ-041", "DeepEval provides LLM-as-judge evaluation with Gemini as the judge.",
    all_of("DeepEval with a Gemini judge",
           dependency_declared(["deepeval"], "deepeval declared"),
           tree_contains([r"deepeval"], "DeepEval used", (".py",)),
           tree_contains([r"gemini"], "Gemini configured as the judge model", (".py",))),
    test_type="INTEGRATION_TEST",
    steps=("Confirm deepeval is declared and used.", "Confirm Gemini is the configured judge model."),
    expected="DeepEval is used with Gemini as the LLM judge.",
))

add(T(
    "REQ-041-T02", "REQ-041", "pytest runs the agent tests.",
    all_of("pytest for agent tests",
           dependency_declared(["pytest"], "pytest declared"),
           file_exists("tests/test_routing.py")),
    test_type="CONFIGURATION_TEST",
    steps=("Confirm pytest is declared.", "Confirm at least one named agent test module exists."),
    expected="pytest is declared and agent tests exist.",
))

add(T(
    "REQ-042-T01", "REQ-042", "Guardrails-AI or LLM Guard provides the guardrail layer.",
    any_of("Guardrails-AI or LLM Guard",
           dependency_declared(["guardrails-ai"], "guardrails-ai declared"),
           dependency_declared(["llm-guard"], "llm-guard declared")),
    test_type="SECURITY_TEST",
    steps=("Check for guardrails-ai.", "Otherwise check for llm-guard - the document permits either."),
    expected="Either Guardrails-AI or LLM Guard is declared.",
))

add(T(
    "REQ-042-T02", "REQ-042", "Presidio provides PII handling.",
    all_of("Presidio for PII",
           dependency_declared(["presidio-analyzer", "presidio_analyzer", "presidio"],
                               "presidio declared", mode="any"),
           tree_contains([r"presidio"], "Presidio used", (".py",))),
    test_type="SECURITY_TEST",
    steps=("Confirm Presidio is declared.", "Confirm it is used in code."),
    expected="Presidio is declared and used for PII.",
))

add(T(
    "REQ-042-T03", "REQ-042", "python-dotenv provides environment configuration.",
    all_of("python-dotenv",
           dependency_declared(["python-dotenv"], "python-dotenv declared"),
           tree_contains([r"dotenv"], "dotenv used", (".py",))),
    test_type="SECURITY_TEST",
    steps=("Confirm python-dotenv is declared.", "Confirm it is used."),
    expected="python-dotenv is declared and used.",
))

add(T(
    "REQ-043-T01", "REQ-043", "A CLI interface exists, which the document marks as required.",
    cli_present,
    test_type="CONFIGURATION_TEST",
    steps=("Search for a CLI entry point: a console script, an argparse/click/typer parser, "
           "or a __main__ module.",
           "Confirm the README documents how to invoke it."),
    expected="A CLI entry point exists and is documented.",
    evidence="The CLI entry point location and the documented invocation.",
))

add(T(
    "REQ-043-T02", "REQ-043", "The FastAPI streaming interface, which the document marks optional / bonus.",
    optional_surface_reported("src/api", "FastAPI streaming (optional / bonus)"),
    test_type="ARCHITECTURE_TEST",
    steps=("Look for the optional FastAPI streaming surface.",
           "Record whether it is present; the document marks it optional / bonus, so its absence "
           "is not a defect of the required interface."),
    expected="The optional FastAPI streaming surface is present (bonus).",
    evidence="Presence or absence of the optional API surface.",
))
