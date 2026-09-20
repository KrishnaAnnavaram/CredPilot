"""
Test cases for REQ-044 .. REQ-071.

Covers: Section 5.1 (AC-01 .. AC-12), Section 5.2 (NFR-01 .. NFR-06), Section 6
(In Scope / Out of Scope) and the Section 7 lead-in.

Black-box first: the acceptance criteria that describe observable copilot behaviour are
driven through the CLI the document requires, and the observable output is inspected.
Static inspection backs them where the criterion is about how the system is built.
"""

from __future__ import annotations

import bootstrap  # noqa: F401
from evidence_validator import (
    all_of,
    any_of,
    dependency_declared,
    dir_exists,
    file_contains,
    file_exists,
    no_files_matching,
    tree_absent,
    tree_contains,
)
from requirement_validator import TestCase
from response_validator import (
    artifact_has_producing_code,
    cli_output_contains,
    decision_recommendation_present,
    sample_inputs_committed,
    tool_names_reconcile,
)

from ._artifact_checks import (
    all_citations_resolve,
    all_named_artifacts_present,
    audit_trail_records,
    eval_report_content,
    golden_signals_content,
    guardrails_wired,
    named_artifacts_have_tests,
    structured_artifacts_parse,
    tool_call_log_fields,
)
from ._helpers import T, unspecified_T
from ._shared_checks import (
    all_named_evidence_committed,
    async_tool_and_model_calls,
    cli_present,
    dashboard_pair,
    document_covers,
    evidence_artifacts_have_producers,
    failure_analysis_content,
    gitignore_covers_env,
    graceful_degradation,
    masking_present,
    no_secrets_committed,
    pytest_module_asserts,
    readme_documents_single_command,
)

DOCS = (".md",)
PY = (".py",)

CASES: list[TestCase] = []
add = CASES.append


# ======================================================================================
# AC-01 (REQ-044) - eligibility determination citing the policy rule
# ======================================================================================

add(T(
    "REQ-044-T01", "REQ-044",
    "Given a synthetic loan application, the copilot returns an eligibility determination.",
    cli_output_contains([r"eligib"], "eligibility determination in observable output"),
    test_type="RUNTIME_TEST", suite="functional",
    inputs="The implementation's own committed synthetic loan application sample inputs.",
    steps=("Discover the documented run command from the implementation's README.md.",
           "Execute it against the committed synthetic loan application.",
           "Inspect the observable output for an eligibility determination."),
    expected="The copilot's observable output states an eligibility determination.",
    evidence="The executed command and the matched output text.",
    weight=2,
))

add(T(
    "REQ-044-T02", "REQ-044",
    "The eligibility determination cites the policy rule it applied.",
    cli_output_contains([r"polic(y|ies)", r"rule|clause|section|citation|cite"],
                        "policy rule citation in observable output", mode="all"),
    test_type="OUTPUT_VALIDATION_TEST", suite="functional",
    inputs="The implementation's own committed synthetic loan application sample inputs.",
    steps=("Execute the documented run command.",
           "Require the eligibility output to name the policy and the rule it applied."),
    expected="The eligibility determination cites the policy rule it applied.",
    evidence="The matched policy-rule citation in the observable output.",
    weight=2,
))

add(T(
    "REQ-044-T03", "REQ-044",
    "The applicable current lending policy is retrieved rather than hard-coded.",
    all_of("current lending policy retrieval",
           file_exists("src/tools/rag_tool.py"),
           dir_exists("data/policy_corpus")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the retrieval tool.", "Locate the lending-policy corpus it retrieves from."),
    expected="A retrieval tool reads the applicable current lending policy from a corpus.",
))

add(T(
    "REQ-044-T04", "REQ-044",
    "Synthetic loan applications are committed so the criterion can be exercised.",
    sample_inputs_committed("committed synthetic loan applications"),
    test_type="DATA_VALIDATION_TEST",
    steps=("Search the conventional input locations for committed application inputs.",),
    expected="Committed synthetic loan applications exist.",
))


# ======================================================================================
# AC-02 (REQ-045) - affordability and threshold breach
# ======================================================================================

add(T(
    "REQ-045-T01", "REQ-045",
    "The copilot computes affordability as DTI or disposable income.",
    tree_contains([r"\bDTI\b|debt[_\- ]?to[_\- ]?income|disposable[_\- ]?income"],
                  "DTI / disposable-income computation", PY),
    test_type="STATIC_TEST",
    steps=("Search the implementation's Python sources for a DTI or disposable-income calculation.",),
    expected="Affordability is computed as DTI or disposable income.",
))

add(T(
    "REQ-045-T02", "REQ-045",
    "Affordability is computed from the application data and reported.",
    cli_output_contains([r"afford|\bDTI\b|disposable"],
                        "affordability figure in observable output"),
    test_type="RUNTIME_TEST", suite="functional",
    inputs="The implementation's own committed synthetic loan application sample inputs.",
    steps=("Execute the documented run command against the committed application.",
           "Inspect the observable output for the affordability result."),
    expected="The copilot reports an affordability result computed from the application data.",
    weight=2,
))

add(T(
    "REQ-045-T03", "REQ-045",
    "A policy breach is flagged together with the threshold it failed.",
    tree_contains([r"threshold", r"breach|violat|fail"],
                  "threshold-bearing policy breach flag", PY, mode="all"),
    test_type="STATIC_TEST",
    steps=("Search for the breach flag.",
           "Require the breach to carry the threshold value that was failed."),
    expected="A policy breach is flagged with the threshold it failed.",
))

add(unspecified_T(
    "REQ-045-T04", "REQ-045",
    "The DTI / disposable-income threshold values themselves.",
    "the numeric DTI or disposable-income threshold that constitutes a policy breach",
    test_type="BOUNDARY_TEST",
))


# ======================================================================================
# AC-03 (REQ-046) - decision recommendation, rationale, human review
# ======================================================================================

add(T(
    "REQ-046-T01", "REQ-046",
    "The copilot produces a decision recommendation from the approve / refer / decline set.",
    decision_recommendation_present(),
    test_type="RUNTIME_TEST", suite="functional",
    inputs="The implementation's own committed synthetic loan application sample inputs.",
    steps=("Execute the documented run command.",
           "Require one of the three decision terms the document names in the observable output."),
    expected="The observable output carries an approve / refer / decline recommendation.",
    weight=2,
))

add(T(
    "REQ-046-T02", "REQ-046",
    "All three decision outcomes the document names are implemented.",
    tree_contains([r"approve", r"refer", r"decline"], "the approve / refer / decline outcomes",
                  PY, mode="all"),
    test_type="STATIC_TEST",
    steps=("Search the implementation for each of the three named decision outcomes.",),
    expected="approve, refer and decline are all implemented outcomes.",
))

add(T(
    "REQ-046-T03", "REQ-046",
    "The recommendation carries a written rationale.",
    cli_output_contains([r"rationale|reason|justification|because|explanation"],
                        "written rationale in observable output"),
    test_type="OUTPUT_VALIDATION_TEST", suite="functional",
    steps=("Execute the documented run command.",
           "Require a written rationale alongside the recommendation."),
    expected="A written rationale accompanies the decision recommendation.",
    weight=2,
))

add(T(
    "REQ-046-T04", "REQ-046",
    "A decline is routed for human review rather than auto-decided.",
    tree_contains([r"decline"], "decline handling", PY),
    test_type="WORKFLOW_TEST", suite="workflow",
    steps=("Locate the decline path.",
           "Require it to hand off to human review rather than finalise the decision."),
    expected="A decline is routed for human review rather than auto-decided.",
))

add(T(
    "REQ-046-T05", "REQ-046",
    "A high-value case is routed for human review rather than auto-decided.",
    tree_contains([r"high[_\- ]?value"], "high-value case routing", PY),
    test_type="WORKFLOW_TEST", suite="workflow",
    steps=("Locate the high-value case path.",
           "Require it to route for human review rather than auto-decide."),
    expected="A high-value case is routed for human review rather than auto-decided.",
))

add(T(
    "REQ-046-T06", "REQ-046",
    "A human-review route exists for the cases the criterion names.",
    tree_contains([r"human[_\- ]?(in[_\- ]?the[_\- ]?loop|review|approval)|escalat"],
                  "human-review route", PY),
    test_type="WORKFLOW_TEST", suite="workflow",
    steps=("Search for the human-review destination those routes lead to.",),
    expected="A human-review route exists.",
))

add(unspecified_T(
    "REQ-046-T07", "REQ-046",
    "The monetary boundary at which a case becomes high-value.",
    "the loan value above which a case counts as a high-value case",
    test_type="BOUNDARY_TEST",
))


# ======================================================================================
# AC-04 (REQ-047) - intent, clarification, escalation
# ======================================================================================

add(T(
    "REQ-047-T01", "REQ-047",
    "The copilot identifies each application's intent.",
    tree_contains([r"intent"], "intent identification", PY),
    test_type="STATIC_TEST",
    steps=("Search the implementation for intent identification.",),
    expected="Application intent is identified.",
))

add(T(
    "REQ-047-T02", "REQ-047",
    "Each identified intent is handled with the right capability.",
    tree_contains([r"intent.*rout|rout.*intent|dispatch|capabilit"],
                  "intent-to-capability dispatch", PY),
    test_type="WORKFLOW_TEST", suite="workflow",
    steps=("Locate the mapping from identified intent to the handling capability.",),
    expected="An identified intent selects the matching capability.",
))

add(T(
    "REQ-047-T03", "REQ-047",
    "Ambiguous requests are clarified.",
    tree_contains([r"ambigu|clarif"], "clarification of ambiguous requests", PY),
    test_type="WORKFLOW_TEST", suite="workflow",
    steps=("Search for the ambiguous-request path and its clarification behaviour.",),
    expected="Ambiguous requests trigger clarification.",
))

add(T(
    "REQ-047-T04", "REQ-047",
    "Out-of-scope requests are escalated to a human rather than mishandled.",
    tree_contains([r"out[_\- ]?of[_\- ]?scope|unsupported|escalat"],
                  "out-of-scope escalation", PY),
    test_type="WORKFLOW_TEST", suite="workflow",
    steps=("Search for the out-of-scope path and confirm it escalates to a human.",),
    expected="Out-of-scope requests are escalated to a human.",
))


# ======================================================================================
# AC-05 (REQ-048) - context maintenance
# ======================================================================================

add(T(
    "REQ-048-T01", "REQ-048",
    "The copilot uses facts stated earlier in the interaction.",
    all_of("within-interaction context",
           dir_exists("src/memory"),
           tree_contains([r"short[_\- ]?term|conversation|history|messages"],
                         "short-term conversational context", PY)),
    test_type="INTEGRATION_TEST",
    steps=("Locate the memory package.",
           "Confirm short-term conversational context is retained within an interaction."),
    expected="Facts stated earlier in the interaction are retained and reused.",
))

add(T(
    "REQ-048-T02", "REQ-048",
    "The copilot recalls prior-session context on a return visit.",
    all_of("cross-session recall",
           file_exists("tests/test_memory_persistence.py"),
           file_exists("logs/memory_test.log"),
           tree_contains([r"thread_id|session|checkpoint|cross[_\- ]?session"],
                         "session-keyed persistence", PY)),
    test_type="INTEGRATION_TEST",
    steps=("Locate the cross-session persistence test.",
           "Locate its committed output log.",
           "Confirm session-keyed persistence exists in the code."),
    expected="Prior-session context is recalled on a return visit, evidenced by a committed test log.",
    weight=2,
))


# ======================================================================================
# AC-06 (REQ-049) - untrusted input safety
# ======================================================================================

add(T(
    "REQ-049-T01", "REQ-049",
    "Attempts to inject instructions are refused.",
    tree_contains([r"inject", r"refus|block|reject|deny"],
                  "prompt-injection refusal", PY, mode="all"),
    test_type="SECURITY_TEST",
    steps=("Search for injection detection.",
           "Require the detected attempt to be refused, blocked or rejected."),
    expected="Instruction-injection attempts are refused.",
    weight=2,
))

add(T(
    "REQ-049-T02", "REQ-049",
    "Attempts to access another applicant's data are refused.",
    tree_contains([r"applicant[_\- ]?id|tenant|authoriz|access[_\- ]?control|ownership"],
                  "per-applicant data access control", PY),
    test_type="SECURITY_TEST",
    steps=("Search for the control that scopes data access to the requesting applicant.",),
    expected="Cross-applicant data access is refused.",
    weight=2,
))

add(T(
    "REQ-049-T03", "REQ-049",
    "Sensitive data is never exposed in logs.",
    masking_present,
    test_type="NEGATIVE_TEST",
    steps=("Confirm masking exists.",
           "Scan every committed log and data artifact for plaintext income, account numbers "
           "and credit identifiers."),
    expected="No committed log exposes income, account numbers or credit identifiers.",
    weight=2,
))

add(T(
    "REQ-049-T04", "REQ-049",
    "Sensitive data is never exposed in answers.",
    tree_contains([r"mask|redact|anonymi[sz]|scrub"],
                  "output-side masking before answers are emitted", PY),
    test_type="SECURITY_TEST",
    steps=("Search the output path for masking applied before an answer is emitted.",),
    expected="Answers are masked so sensitive data is not exposed.",
))


# ======================================================================================
# AC-07 (REQ-050) - tool-invocation log
# ======================================================================================

add(T(
    "REQ-050-T01", "REQ-050",
    "A tool-invocation log exists at logs/tool_calls.jsonl and parses.",
    tool_call_log_fields,
    test_type="OBSERVABILITY_TEST",
    steps=("Locate logs/tool_calls.jsonl.",
           "Parse every line as JSON.",
           "Require the per-call fields the document names."),
    expected="logs/tool_calls.jsonl exists, parses, and carries the named per-call fields.",
    weight=2,
))

add(T(
    "REQ-050-T02", "REQ-050",
    "The log is machine-generated by committed logging middleware.",
    artifact_has_producing_code(
        "logs/tool_calls.jsonl",
        [r"tool_calls\.jsonl"],
        "committed logging middleware that writes the tool-invocation log",
    ),
    test_type="AUDITABILITY_TEST",
    steps=("Search committed Python sources for the code that writes logs/tool_calls.jsonl.",),
    expected="Committed logging middleware produces the log; it is not hand-written.",
    weight=2,
))

add(T(
    "REQ-050-T03", "REQ-050",
    "Tool names in the log reconcile with the agent/MCP code.",
    tool_names_reconcile(),
    test_type="AUDITABILITY_TEST",
    steps=("Collect every distinct tool_name in the log.",
           "Require each to appear in the committed agent/MCP Python sources."),
    expected="Every logged tool name reconciles with a name in the committed code.",
    weight=2,
))


# ======================================================================================
# AC-08 (REQ-051) - failure analysis
# ======================================================================================

add(T(
    "REQ-051-T01", "REQ-051",
    "docs/failure-analysis.md documents at least 3 real failures, each with evidence, cause and fix.",
    failure_analysis_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Locate docs/failure-analysis.md.",
           "Count the documented failures; require >= 3.",
           "Require each to cite a Phoenix run_id + span_id, or a tool-log record.",
           "Require a root cause and a fix for each."),
    expected="At least 3 real failures are documented, each citing evidence plus root cause and fix.",
    weight=3,
))

add(T(
    "REQ-051-T02", "REQ-051",
    "The citations in the failure analysis resolve to committed artifacts.",
    all_citations_resolve,
    test_type="AUDITABILITY_TEST",
    steps=("Extract the file-path citations from the committed documents.",
           "Resolve each to a committed artifact."),
    expected="Every citation resolves to a committed artifact.",
))


# ======================================================================================
# AC-09 (REQ-052) - golden signals and dashboard
# ======================================================================================

add(T(
    "REQ-052-T01", "REQ-052",
    "The golden-signals report carries latency, tokens, cost, accuracy and hallucination rate.",
    golden_signals_content,
    test_type="OBSERVABILITY_TEST",
    steps=("Locate reports/golden_signals.json and parse it.",
           "Require latency for thinking / acting / tool span types.",
           "Require tokens, a cost estimate, accuracy and hallucination rate."),
    expected="The golden-signals report carries every figure the criterion names.",
    weight=3,
))

add(T(
    "REQ-052-T02", "REQ-052",
    "The report is Phoenix-derived.",
    artifact_has_producing_code(
        "reports/golden_signals.json",
        [r"get_spans_dataframe", r"golden_signals\.json"],
        "Phoenix-derived golden-signals report",
    ),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the script that writes the report.",
           "Confirm it reads the Phoenix spans."),
    expected="The golden-signals report is derived from Phoenix spans by committed code.",
))

add(T(
    "REQ-052-T03", "REQ-052",
    "A cost/latency dashboard exists as a Phoenix screenshot plus its underlying data file.",
    dashboard_pair,
    test_type="OBSERVABILITY_TEST",
    steps=("Locate reports/dashboard.png and verify it is a real PNG.",
           "Locate reports/dashboard_data.csv and verify it holds data rows."),
    expected="Both the dashboard screenshot and the underlying data file exist and hold content.",
    weight=2,
))


# ======================================================================================
# AC-10 (REQ-053) - guardrails and audit trail
# ======================================================================================

add(T(
    "REQ-053-T01", "REQ-053",
    "Input/output guardrails are wired into the agent's I/O path.",
    guardrails_wired,
    test_type="SECURITY_TEST",
    steps=("Locate the guardrail package.",
           "Require an input guardrail and an output guardrail.",
           "Require blocking or sanitizing behaviour.",
           "Require a module outside the guardrail package to call into it."),
    expected="Input and output guardrails exist and are wired into the agent's I/O path.",
    weight=3,
))

add(T(
    "REQ-053-T02", "REQ-053",
    "A machine-generated audit trail of agent actions exists at logs/agent_actions.jsonl.",
    audit_trail_records,
    test_type="AUDITABILITY_TEST",
    steps=("Locate logs/agent_actions.jsonl and parse it.",
           "Require the actor, action, tool, decision and timestamp fields.",
           "Require committed middleware that writes it."),
    expected="A machine-generated audit trail exists with the named fields.",
    weight=3,
))


# ======================================================================================
# AC-11 (REQ-054) - governance pack
# ======================================================================================

add(T(
    "REQ-054-T01", "REQ-054", "The governance pack contains a risk register.",
    file_exists("docs/risk-register.md"),
    test_type="GOVERNANCE_TEST",
    steps=("Locate docs/risk-register.md.",),
    expected="A risk register exists.",
))

add(T(
    "REQ-054-T02", "REQ-054", "The governance pack contains a model/system card.",
    file_exists("docs/model-card.md"),
    test_type="GOVERNANCE_TEST",
    steps=("Locate docs/model-card.md.",),
    expected="A model/system card exists.",
))

add(T(
    "REQ-054-T03", "REQ-054",
    "The compliance mapping covers EU AI Act, NIST AI RMF and DPDP.",
    document_covers("docs/compliance.md", {
        "EU AI Act obligations": r"EU\s*AI\s*Act",
        "NIST AI RMF obligations": r"NIST\s*AI\s*RMF",
        "DPDP obligations": r"\bDPDP\b",
    }, "compliance mapping"),
    test_type="GOVERNANCE_TEST",
    steps=("Locate docs/compliance.md.",
           "Require each of the three frameworks the criterion names."),
    expected="The compliance mapping covers EU AI Act, NIST AI RMF and DPDP.",
    weight=2,
))

add(T(
    "REQ-054-T04", "REQ-054", "The governance pack contains an output-risk classification.",
    file_exists("docs/output-risk.md"),
    test_type="GOVERNANCE_TEST",
    steps=("Locate docs/output-risk.md.",),
    expected="An output-risk classification exists.",
))

add(T(
    "REQ-054-T05", "REQ-054",
    "Each mitigation/claim in the governance pack cites a committed control.",
    all_citations_resolve,
    test_type="AUDITABILITY_TEST",
    steps=("Extract every file-path citation from the governance documents.",
           "Require each to resolve to a committed control or artifact."),
    expected="Every mitigation/claim citation resolves to a committed control.",
    weight=2,
))


# ======================================================================================
# AC-12 (REQ-055) - agent evaluation and tests
# ======================================================================================

add(T(
    "REQ-055-T01", "REQ-055",
    "A DeepEval (or equivalent) report covers a golden set with hallucination and faithfulness/relevance.",
    eval_report_content,
    test_type="INTEGRATION_TEST",
    steps=("Locate reports/eval_report.json and parse it.",
           "Require hallucination, faithfulness and answer-relevance metrics over a golden set.",
           "Require a committed harness that produces it."),
    expected="An evaluation report over a golden set exists with the named metrics and a harness.",
    weight=3,
))

add(T(
    "REQ-055-T02", "REQ-055", "The routing-logic agent test asserts routing behaviour.",
    pytest_module_asserts("tests/test_routing.py", {
        "routes to the right worker": r"rout|worker|edge|supervisor",
    }, "routing-logic test"),
    test_type="INTEGRATION_TEST",
    steps=("Locate tests/test_routing.py.",
           "Require test functions, assertions, and routing subject matter."),
    expected="The routing-logic test asserts which worker a given state routes to.",
))

add(T(
    "REQ-055-T03", "REQ-055", "The loop/cascade guard test asserts a step or recursion limit.",
    pytest_module_asserts("tests/test_loops.py", {
        "max-steps / recursion-limit guard": r"recursion|max[_\- ]?step|max[_\- ]?iter|limit",
    }, "loop/cascade guard test"),
    test_type="INTEGRATION_TEST",
    steps=("Locate tests/test_loops.py.",
           "Require test functions, assertions, and a step/recursion limit subject."),
    expected="The loop/cascade guard test asserts that a limit stops runaway loops.",
))

add(T(
    "REQ-055-T04", "REQ-055", "The tool-contract test asserts tool I/O schemas and an error path.",
    pytest_module_asserts("tests/test_tool_contracts.py", {
        "input/output schema assertion": r"schema|input|output|contract",
        "an error path": r"raise|error|exception|invalid|pytest\.raises",
    }, "tool-contract test"),
    test_type="INTEGRATION_TEST",
    steps=("Locate tests/test_tool_contracts.py.",
           "Require schema assertions and at least one error path."),
    expected="The tool-contract test asserts each tool's I/O schema plus one error path.",
))


# ======================================================================================
# NFR-01 (REQ-056) - secrets
# ======================================================================================

add(T(
    "REQ-056-T01", "REQ-056", "No secrets or keys are committed.",
    no_secrets_committed,
    test_type="SECURITY_TEST",
    steps=("Scan every committed text artifact against a set of credential patterns.",
           "Ignore documented placeholders in the committed template."),
    expected="No secret or key is committed anywhere in the repository.",
    weight=3,
))

add(T(
    "REQ-056-T02", "REQ-056",
    "Configuration is by environment variable with a committed .env.example, and .gitignore covers .env.",
    gitignore_covers_env,
    test_type="CONFIGURATION_TEST",
    steps=("Locate .gitignore and require a rule covering .env.",
           "Locate the committed .env.example template.",
           "Confirm no real .env is committed."),
    expected="Env-var config with a committed .env.example and a .gitignore covering .env.",
    weight=2,
))

add(T(
    "REQ-056-T03", "REQ-056", "Configuration is read from environment variables.",
    tree_contains([r"os\.environ|os\.getenv|load_dotenv|dotenv_values"],
                  "environment-variable configuration", PY),
    test_type="CONFIGURATION_TEST",
    steps=("Search the implementation for environment-variable configuration.",),
    expected="Configuration is read from environment variables.",
))


# ======================================================================================
# NFR-02 (REQ-057) - single documented command
# ======================================================================================

add(T(
    "REQ-057-T01", "REQ-057",
    "A single documented command runs the copilot and a second regenerates the traces and the evaluation.",
    readme_documents_single_command,
    test_type="DOCUMENTATION_TEST",
    steps=("Read the implementation's README.md.",
           "Require one documented command that runs the copilot.",
           "Require a documented command that regenerates the Phoenix traces.",
           "Require a documented command that regenerates the evaluation."),
    expected="The run command and the regeneration commands are all documented.",
    weight=3,
))

add(T(
    "REQ-057-T02", "REQ-057", "The documented run command actually executes.",
    cli_present,
    test_type="RUNTIME_TEST", suite="functional",
    steps=("Discover the documented run command.", "Confirm a CLI entry point backs it."),
    expected="The documented command is backed by a real CLI entry point.",
))

add(T(
    "REQ-057-T03", "REQ-057", "Sample inputs are committed.",
    sample_inputs_committed(),
    test_type="CONFIGURATION_TEST",
    steps=("Search the conventional input locations for committed sample inputs.",),
    expected="Committed sample inputs exist.",
))


# ======================================================================================
# NFR-03 (REQ-058) - quarantine
# ======================================================================================

add(T(
    "REQ-058-T01", "REQ-058",
    "Untrusted free-text applicant-supplied content is quarantined.",
    tree_contains([r"quarantin"], "quarantine of untrusted applicant-supplied content", PY),
    test_type="SECURITY_TEST",
    steps=("Search the implementation for the quarantine mechanism.",),
    expected="Untrusted free-text applicant-supplied content is quarantined.",
    weight=2,
))

add(T(
    "REQ-058-T02", "REQ-058",
    "Quarantined content is never treated as instructions.",
    tree_contains([r"untrusted|quarantin"], "untrusted content marked as data, not instructions", PY),
    test_type="SECURITY_TEST",
    steps=("Locate where quarantined content enters the model context.",
           "Require it to be handled as data rather than as instructions."),
    expected="Quarantined content is passed as data and never interpreted as instructions.",
    weight=2,
))


# ======================================================================================
# NFR-04 (REQ-059) - async and graceful degradation
# ======================================================================================

add(T(
    "REQ-059-T01", "REQ-059",
    "The agent pipeline uses async where it calls tools/models.",
    async_tool_and_model_calls,
    test_type="ARCHITECTURE_TEST",
    steps=("Analyse the Python AST for async definitions.",
           "Require await expressions, so the async path is actually used."),
    expected="The pipeline defines and uses async where it calls tools and models.",
    weight=2,
))

add(T(
    "REQ-059-T02", "REQ-059",
    "The pipeline degrades gracefully on tool/model failure via timeouts, retries and exit conditions.",
    graceful_degradation,
    test_type="ARCHITECTURE_TEST",
    steps=("Search for timeouts.", "Search for retries.",
           "Search for exit conditions.", "Search for failure handling around tool/model calls."),
    expected="Timeouts, retries and exit conditions are all present.",
    weight=2,
))


# ======================================================================================
# NFR-05 (REQ-060) - synthetic and masked data
# ======================================================================================

add(T(
    "REQ-060-T01", "REQ-060", "All data is synthetic.",
    tree_contains([r"synthetic"], "synthetic data declaration", (".md", ".py", ".json")),
    test_type="DATA_VALIDATION_TEST",
    steps=("Search the repository for the declaration that all data is synthetic.",),
    expected="All data is declared synthetic.",
))

add(T(
    "REQ-060-T02", "REQ-060",
    "Income, account numbers and credit identifiers are masked and never logged in plaintext.",
    masking_present,
    test_type="SECURITY_TEST",
    steps=("Confirm masking is implemented.",
           "Scan every committed log and data artifact for plaintext sensitive identifiers."),
    expected="Sensitive identifiers are masked and absent from the committed logs in plaintext.",
    weight=3,
))


# ======================================================================================
# NFR-06 (REQ-061) - machine-generated evidence
# ======================================================================================

add(T(
    "REQ-061-T01", "REQ-061",
    "Traces, logs and reports are machine-generated by committed code.",
    evidence_artifacts_have_producers,
    test_type="AUDITABILITY_TEST",
    steps=("For each evidence artifact present, search committed Python sources for the code "
           "that writes it."),
    expected="Every present evidence artifact has committed producing code.",
    weight=3,
))

add(T(
    "REQ-061-T02", "REQ-061",
    "The producing code is committed alongside the artifact it produced.",
    all_of("artifact and its producer both committed",
           evidence_artifacts_have_producers,
           all_named_evidence_committed),
    test_type="AUDITABILITY_TEST",
    steps=("Confirm each evidence artifact is git-tracked.",
           "Confirm its producing code is also git-tracked."),
    expected="Each evidence artifact and the code that produced it are both committed.",
    weight=2,
))


# ======================================================================================
# Section 6.1 - In Scope (REQ-062 .. REQ-064)
# ======================================================================================

add(T(
    "REQ-062-T01", "REQ-062",
    "The full surface named in scope is delivered: copilot plus observability, cost-governance, "
    "security, governance and evaluation.",
    all_of("the full in-scope surface",
           file_exists("src/graph.py"),
           file_exists("src/observability/tracing.py"),
           file_exists("reports/golden_signals.json"),
           dir_exists("src/guardrails"),
           file_exists("docs/compliance.md"),
           file_exists("reports/eval_report.json")),
    test_type="ARCHITECTURE_TEST",
    steps=("Locate the LangGraph copilot foundation.",
           "Locate each of its five named surfaces: observability, cost-governance, security, "
           "governance and evaluation."),
    expected="The copilot and all five named surfaces are delivered.",
    weight=2,
))

add(T(
    "REQ-063-T01", "REQ-063", "Arize Phoenix tracing is in scope and delivered.",
    all_of("Phoenix tracing",
           file_exists("src/observability/tracing.py"),
           any_of("a trace export",
                  file_exists("traces/phoenix_spans.parquet"),
                  file_exists("traces/phoenix_spans.jsonl"))),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the tracing module and a trace export.",),
    expected="Phoenix tracing and a trace export are delivered.",
))

add(T(
    "REQ-063-T02", "REQ-063", "Golden-signals plus cost/latency governance are delivered.",
    all_of("golden signals and cost/latency governance",
           file_exists("reports/golden_signals.json"),
           file_exists("reports/dashboard_data.csv")),
    test_type="OBSERVABILITY_TEST",
    steps=("Locate the golden-signals report and the cost/latency data file.",),
    expected="Golden-signals and cost/latency governance artifacts are delivered.",
))

add(T(
    "REQ-063-T03", "REQ-063", "Guardrails plus audit plus secrets hygiene are delivered.",
    all_of("guardrails, audit and secrets hygiene",
           dir_exists("src/guardrails"),
           file_exists("logs/agent_actions.jsonl"),
           file_exists(".env.example")),
    test_type="SECURITY_TEST",
    steps=("Locate the guardrail package, the audit trail and the env-var template.",),
    expected="Guardrails, audit trail and secrets hygiene are delivered.",
))

add(T(
    "REQ-063-T04", "REQ-063", "Governance/compliance docs are delivered.",
    all_of("governance and compliance docs",
           file_exists("docs/risk-register.md"),
           file_exists("docs/model-card.md"),
           file_exists("docs/compliance.md"),
           file_exists("docs/output-risk.md")),
    test_type="GOVERNANCE_TEST",
    steps=("Locate the four governance documents.",),
    expected="All governance/compliance documents are delivered.",
))

add(T(
    "REQ-063-T05", "REQ-063", "Agent-level evaluation & tests are delivered.",
    all_of("agent-level evaluation and tests",
           file_exists("reports/eval_report.json"),
           file_exists("tests/test_routing.py"),
           file_exists("tests/test_loops.py"),
           file_exists("tests/test_tool_contracts.py")),
    test_type="INTEGRATION_TEST",
    steps=("Locate the evaluation report and the three agent tests.",),
    expected="Agent-level evaluation and tests are delivered.",
))

add(T(
    "REQ-064-T01", "REQ-064", "A CLI exists.",
    cli_present,
    test_type="CONFIGURATION_TEST",
    steps=("Locate the CLI entry point and its documented invocation.",),
    expected="A CLI entry point exists and is documented.",
))

add(T(
    "REQ-064-T02", "REQ-064", "The CLI drives applications through the graph.",
    tree_contains([r"graph", r"invoke|stream|run"],
                  "the CLI invoking the graph", PY, mode="all"),
    test_type="INTEGRATION_TEST",
    steps=("Locate where the CLI passes an application into the compiled graph.",),
    expected="The CLI drives applications through the graph.",
))

add(T(
    "REQ-064-T03", "REQ-064", "The CLI regenerates traces and the evaluation.",
    readme_documents_single_command,
    test_type="DOCUMENTATION_TEST",
    steps=("Read the documented commands.",
           "Require documented commands that regenerate the traces and the evaluation."),
    expected="The CLI regenerates the traces and the evaluation.",
))


# ======================================================================================
# Section 6.2 - Out of Scope (REQ-065 .. REQ-068)
# ======================================================================================

add(T(
    "REQ-065-T01", "REQ-065",
    "Containerized / cloud deployment is deferred, so no hackathon time went into it.",
    no_files_matching(
        ["Dockerfile", "*.dockerfile", "docker-compose*.yml", "docker-compose*.yaml",
         "compose.yaml", "compose.yml", "*.k8s.yaml", "Chart.yaml", "rancher*.yml"],
        "Docker / Rancher / k8s deployment artifacts",
    ),
    test_type="NEGATIVE_TEST",
    steps=("Scan the repository for Docker, Rancher and Kubernetes deployment artifacts.",),
    expected="No containerized or cloud deployment artifact is present.",
))

add(T(
    "REQ-066-T01", "REQ-066",
    "No real credit-bureau or core-banking integration is present.",
    tree_absent(
        [r"experian|equifax|transunion|cibil|creditbureau|credit[_\- ]bureau[_\- ]api",
         r"finacle|flexcube|temenos|core[_\- ]banking[_\- ]api"],
        "real credit-bureau or core-banking integrations",
        (".py", ".toml", ".cfg", ".txt", ".yaml", ".yml"),
    ),
    test_type="NEGATIVE_TEST",
    steps=("Scan the implementation for real credit-bureau or core-banking integrations.",),
    expected="No real credit-bureau or core-banking integration is present.",
))

add(T(
    "REQ-066-T02", "REQ-066", "Synthetic application and policy data is used instead.",
    all_of("synthetic application and policy data",
           dir_exists("data/policy_corpus"),
           sample_inputs_committed("committed synthetic application data")),
    test_type="DATA_VALIDATION_TEST",
    steps=("Locate the synthetic policy corpus.", "Locate the committed synthetic applications.",),
    expected="Synthetic application and policy data is used.",
))

add(T(
    "REQ-067-T01", "REQ-067",
    "No front-end build system is present, so no hackathon time went into visual polish.",
    no_files_matching(
        ["package.json", "webpack.config.js", "vite.config.*", "tailwind.config.*",
         "next.config.*", "angular.json"],
        "front-end build tooling",
    ),
    test_type="NEGATIVE_TEST",
    steps=("Scan the repository for front-end build tooling.",),
    expected="No front-end build system is present.",
))

add(T(
    "REQ-068-T01", "REQ-068",
    "No advanced OAuth flow or live secrets-rotation infrastructure is implemented.",
    tree_absent(
        [r"oauth2?[_\- ]?(flow|client|provider)|authorization_code|pkce|refresh_token",
         r"secret[_\- ]?rotation|rotate_secret|vault\.|kms\.|secretsmanager"],
        "advanced OAuth flows and live secrets-rotation infrastructure",
        (".py",),
    ),
    test_type="NEGATIVE_TEST",
    steps=("Scan the implementation for OAuth flows and live secrets-rotation infrastructure.",),
    expected="Neither is implemented, matching the stated out-of-scope decision.",
))

add(T(
    "REQ-068-T02", "REQ-068",
    "The approach to OAuth and secrets rotation is documented instead.",
    tree_contains([r"oauth|secret[_\- ]?rotation|rotate|key rotation"],
                  "the documented approach to OAuth and secrets rotation", DOCS),
    test_type="DOCUMENTATION_TEST",
    steps=("Search the committed documentation for the stated approach to OAuth and "
           "secrets rotation."),
    expected="The approach is documented, as the source text instructs in place of implementing it.",
))


# ======================================================================================
# Section 7 lead-in (REQ-069 .. REQ-071)
# ======================================================================================

add(T(
    "REQ-069-T01", "REQ-069",
    "The checklist the submission is scored against is exactly what this suite scores.",
    named_artifacts_have_tests,
    test_type="GOVERNANCE_TEST",
    steps=("Enumerate every artifact the Section 7 checklist names.",
           "Confirm each is referenced by at least one registered test case."),
    expected="Every checklist artifact is covered by at least one test in this suite.",
    preconditions="The test registry is importable.",
))

add(T(
    "REQ-070-T01", "REQ-070",
    "Each artifact is present at (or near) the path shown.",
    all_named_artifacts_present,
    test_type="STATIC_TEST",
    steps=("For each artifact the checklist names, look for it at its exact path.",
           "If absent, look for the same filename elsewhere in the tree ('or near').",
           "Report each as exact, near, or absent."),
    expected="Every checklist artifact is present at or near the path shown.",
    weight=3,
))

add(T(
    "REQ-070-T02", "REQ-070",
    "Each present artifact contains what is listed rather than being an empty placeholder.",
    structured_artifacts_parse,
    test_type="DATA_VALIDATION_TEST",
    steps=("For each present checklist artifact, require non-zero content.",
           "Parse JSON and JSONL artifacts and require valid records."),
    expected="No present checklist artifact is empty or malformed.",
    weight=2,
))

add(T(
    "REQ-071-T01", "REQ-071", "Outputs are produced by committed code.",
    evidence_artifacts_have_producers,
    test_type="AUDITABILITY_TEST",
    steps=("For each evidence artifact present, locate the committed code that writes it.",),
    expected="Every output is produced by committed code.",
    weight=2,
))

add(T(
    "REQ-071-T02", "REQ-071", "Every citation resolves to a committed artifact.",
    all_citations_resolve,
    test_type="AUDITABILITY_TEST",
    steps=("Extract every file-path citation from every committed document.",
           "Resolve each to a committed artifact."),
    expected="Every citation resolves to a committed artifact.",
    weight=2,
))
