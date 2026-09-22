"""Observability: the span taxonomy, the golden signals, and the audit trail.

AC-09 asks for latency split into **thinking, acting and tool** time. That split
cannot be recovered from a stopwatch around the evaluation loop, and it cannot
be recovered from span names either once new nodes are added by someone who did
not read the aggregator. So every span declares its kind as an attribute, and
these tests hold the two ends of that contract together:

* every span CredPilot opens carries a kind, and the kind is one of four;
* the golden-signals report reads that attribute rather than pattern-matching
  names it does not control;
* the operational figures come from spans and the quality figures come from the
  evaluation, and neither is derived from the other.

Plus the thing F-14 cost: the first request must not pay a cold start that
belongs at start-up.
"""

from __future__ import annotations

import json

import pytest

from src.observability import tracing


# ------------------------------------------------------------ the taxonomy


def test_there_are_exactly_four_span_kinds():
    kinds = {
        tracing.SPAN_KIND_THINKING,
        tracing.SPAN_KIND_ACTING,
        tracing.SPAN_KIND_TOOL,
        tracing.SPAN_KIND_RETRIEVAL,
    }
    assert kinds == {"THINKING", "ACTING", "TOOL", "RETRIEVAL"}


def test_every_named_span_has_a_declared_kind():
    """A span name with no mapping falls back to ACTING, which would quietly
    misclassify a model call as deterministic work and understate thinking
    latency. Every name the code uses is mapped explicitly."""
    named = [
        value
        for name, value in vars(tracing).items()
        if name.startswith("SPAN_") and isinstance(value, str)
        and not name.startswith("SPAN_KIND")
    ]
    assert named
    for span_name in named:
        assert span_name in tracing._DEFAULT_SPAN_KINDS, (
            f"{span_name!r} has no declared kind and would default to ACTING"
        )


def test_model_calls_are_classified_as_thinking():
    assert tracing.span_kind_for("llm.narrative") == tracing.SPAN_KIND_THINKING
    assert tracing.span_kind_for("supervisor.classify") == tracing.SPAN_KIND_THINKING


def test_retrieval_stages_are_classified_as_retrieval():
    for name in ("bm25.search", "chroma.search", "embedding.query", "rrf.fusion",
                 "reranker.run", "temporal.validate", "citation.validate"):
        assert tracing.span_kind_for(name) == tracing.SPAN_KIND_RETRIEVAL, name


def test_mcp_calls_are_classified_as_tool():
    for name in ("mcp.tool", "mcp.resource", "mcp.prompt", "mcp.connect"):
        assert tracing.span_kind_for(name) == tracing.SPAN_KIND_TOOL, name


def test_an_explicit_kind_overrides_the_name():
    assert tracing.span_kind_for("bm25.search", "THINKING") == "THINKING"


# --------------------------------------------------- the committed export


@pytest.fixture(scope="module")
def spans(repo_root):
    path = repo_root / "traces" / "phoenix_spans.jsonl"
    if not path.exists():
        pytest.skip("no committed span export; run scripts/export_traces.py")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_the_export_carries_the_span_kind_attribute(spans):
    """Without it the golden-signals split is a guess."""
    assert spans
    with_kind = [
        s for s in spans
        if tracing.SPAN_KIND_ATTRIBUTE in (s.get("attributes") or {})
    ]
    assert len(with_kind) == len(spans), (
        f"{len(spans) - len(with_kind)} span(s) carry no kind attribute"
    )


def test_the_export_covers_all_four_kinds(spans):
    kinds = {
        (s.get("attributes") or {}).get(tracing.SPAN_KIND_ATTRIBUTE) for s in spans
    }
    assert kinds == {"THINKING", "ACTING", "TOOL", "RETRIEVAL"}, kinds


def test_the_export_covers_the_whole_architecture(spans):
    """Not only the assessment path. A trace export that never recorded a
    greeting could not evidence that a greeting does not retrieve."""
    names = {s["name"] for s in spans}
    for required in ("graph.intake", "guardrails.input", "supervisor.route",
                     "agent.mortgage", "agent.education", "agent.eligibility",
                     "agent.risk", "agent.recommendation", "agent.final_response",
                     "guardrails.output", "rag.retrieve", "reranker.run"):
        assert required in names, f"{required} is missing from the export"


def test_every_span_has_a_resolvable_identity(spans):
    """The failure analysis cites span ids. They have to be there and unique."""
    ids = [s.get("span_id") for s in spans]
    assert all(ids), "a span has no id"
    assert len(set(ids)) == len(ids), "span ids are not unique"
    assert all(s.get("trace_id") for s in spans)


def test_the_span_ids_the_failure_analysis_cites_resolve(spans, repo_root):
    """AC-08: every reference must resolve to committed evidence.

    Read out of the document rather than hard-coded here, so a citation added
    later is checked too and one that goes stale fails this test rather than
    quietly misleading a reader.

    Resolved against the live export **and** the frozen extracts under
    `docs/evidence/`. The export is regenerated, and a fix deletes the evidence
    of the bug it fixed — F-14's 31-second `graph.intake` span does not occur
    any more, by design. Re-creating it would mean re-introducing the bug, so
    those spans are kept verbatim instead. A citation that resolves in neither
    place still fails here.
    """
    import re

    document = (repo_root / "docs" / "failure-analysis.md").read_text(encoding="utf-8")
    frozen = []
    for path in sorted((repo_root / "docs" / "evidence").glob("*.jsonl")):
        frozen += [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    known = list(spans) + frozen
    by_id = {s["span_id"]: s for s in known}
    traces = {s["trace_id"] for s in known}

    cited_spans = set(re.findall(r"span_id\s+([0-9a-f]{16})", document))
    cited_spans |= set(re.findall(r"span=([0-9a-f]{16})", document))
    cited_spans |= set(re.findall(r"`([0-9a-f]{16})`", document))
    cited_traces = set(re.findall(r"trace_id\s+([0-9a-f]{32})", document))

    assert cited_spans, "the failure analysis cites no span id at all"
    for span_id in cited_spans:
        assert span_id in by_id, (
            f"failure analysis cites span {span_id}, which is in neither "
            "traces/phoenix_spans.jsonl nor docs/evidence/"
        )
    for trace_id in cited_traces:
        assert trace_id in traces, (
            f"failure analysis cites trace {trace_id}, which is in neither "
            "traces/phoenix_spans.jsonl nor docs/evidence/"
        )


def test_no_span_attribute_carries_a_sensitive_value(spans):
    from src.guardrails.redaction import find_sensitive

    for span in spans:
        body = json.dumps(span.get("attributes") or {}, default=str)
        found = find_sensitive(body)
        assert not found, f"{span['name']} ({span['span_id']}) carries {found}"


# ------------------------------------------------------- the golden signals


@pytest.fixture(scope="module")
def signals(repo_root):
    path = repo_root / "reports" / "golden_signals.json"
    if not path.exists():
        pytest.skip("no golden signals; run scripts/build_golden_signals.py")
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_operational_figures_come_from_phoenix(signals):
    """AC-09 asks for a *Phoenix-derived* report. A latency split re-derived
    from the evaluation's own case file would not be one."""
    assert "phoenix" in signals["sources"]["operational"].lower()
    assert signals["latency"]["source"] == "phoenix spans"
    assert "phoenix" in signals["tokens"]["source"]
    assert "phoenix" in signals["cost"]["source"]


def test_the_quality_figures_come_from_the_evaluation(signals):
    assert signals["accuracy"]["source"].endswith("eval_report.json")
    assert signals["grounding"]["source"].endswith("eval_report.json")


def test_latency_is_split_into_thinking_acting_and_tool(signals):
    """The split AC-09 names, by name."""
    latency = signals["latency"]
    for block in ("request", "thinking", "acting", "tool", "retrieval"):
        assert block in latency, block
        assert "p50" in latency[block] and "p95" in latency[block]
    # And the split is real rather than three copies of one number.
    assert latency["acting"]["count"] > 0
    assert latency["tool"]["count"] > 0
    assert latency["retrieval"]["count"] > 0


def test_a_run_with_no_billed_tokens_says_so(signals):
    """$0.00 per assessment is an efficiency result or a broken key, and the
    report must not let a reader confuse the two."""
    tokens = signals["tokens"]
    if tokens["model_calls"] and not tokens["input_total"] and not tokens["output_total"]:
        assert tokens["model_calls_recorded_no_tokens"] is True
        assert "did not reach the provider" in tokens["zero_token_note"]


def test_the_signals_report_names_the_code_that_wrote_it(signals):
    """The Evidence-in-Repo Rule, applied to this artifact.

    Also the thing that lets a reader — or a validator — find the producer
    without guessing from whichever file happens to mention the filename
    first.
    """
    assert signals["generated_by"] == "scripts/build_golden_signals.py"


def test_the_producing_script_derives_cost_from_tokens_and_a_price(repo_root):
    """REQ-102 names the derivation: cost = tokens x price, from Phoenix spans.

    Asserted on the script rather than on the number, because with no model
    reachable the number is legitimately zero and a zero proves nothing about
    how it was computed.
    """
    source = (repo_root / "scripts" / "build_golden_signals.py").read_text(
        encoding="utf-8"
    )
    assert "get_spans_dataframe" in source
    assert "PRICE_IN_PER_MILLION" in source and "PRICE_OUT_PER_MILLION" in source
    assert "1_000_000 * PRICE_IN_PER_MILLION" in source


def test_the_dashboard_csv_is_written_with_to_csv(repo_root):
    """REQ-103 names the method. Using it costs nothing and pandas is already
    a dependency, so there is no reason for the artifact not to be written the
    way the requirement describes."""
    source = (repo_root / "scripts" / "build_golden_signals.py").read_text(
        encoding="utf-8"
    )
    assert ".to_csv(" in source


def test_the_dashboard_data_names_the_source_of_every_row(repo_root):
    """A reader checking the chart has to be able to tell a Phoenix-derived
    latency from an eval-derived accuracy."""
    import csv

    path = repo_root / "reports" / "dashboard_data.csv"
    if not path.exists():
        pytest.skip("no dashboard data")
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows
    assert all(r["source"] in ("phoenix", "eval") for r in rows), (
        {r["source"] for r in rows}
    )
    assert any(r["source"] == "phoenix" for r in rows)
    assert any(r["source"] == "eval" for r in rows)
    # Latency must be Phoenix-derived; accuracy must not be.
    for row in rows:
        if row["group"] == "latency":
            assert row["source"] == "phoenix", row
        if row["group"] in ("accuracy", "grounding"):
            assert row["source"] == "eval", row


# ----------------------------------------------------------- the cold start


def test_the_first_request_does_not_pay_the_redaction_cold_start():
    """F-14: building Presidio cost 17s inside the first request's intake node.

    Asserted on where the cost is paid, not on how long it takes — a timing
    assertion would be flaky on a loaded machine, and the defect was never
    about the duration. It was about the cost landing inside a user's request
    instead of at start-up.
    """
    import src.guardrails.redaction as redaction

    source = (
        __import__("pathlib").Path(redaction.__file__).read_text(encoding="utf-8")
    )
    assert "def warm_redaction" in source

    from src.graph import build_graph

    graph_source = (
        __import__("pathlib")
        .Path(__import__("src.graph", fromlist=["graph"]).__file__)
        .read_text(encoding="utf-8")
    )
    assert "warm_redaction()" in graph_source, (
        "build_graph no longer warms the redaction engine; the cold start is "
        "back inside the first request"
    )


def test_warming_is_idempotent_and_never_raises():
    from src.guardrails.redaction import redaction_is_warm, warm_redaction

    warm_redaction(background=False)
    assert redaction_is_warm() is True
    warm_redaction(background=False)
    warm_redaction()
    assert redaction_is_warm() is True


# ------------------------------------------------------------- audit trail


@pytest.mark.integration
def test_the_audit_trail_records_every_consequential_action(
    indexes_built, tmp_path, repo_root, monkeypatch
):
    """AC-10: a machine-generated audit trail of agent actions."""
    if not indexes_built:
        pytest.skip("indexes not built")

    monkeypatch.setenv("CREDPILOT_LOG_DIR", str(tmp_path))
    import importlib

    from src.observability import tool_logging

    importlib.reload(tool_logging)
    try:
        import src.graph as graph_module

        importlib.reload(graph_module)
        graph, context = graph_module.build_graph(
            checkpoint_path=tmp_path / "audit.sqlite"
        )
        try:
            graph.invoke(
                graph_module.initial_state(
                    repo_root / "synthetic_data/mortgage/applications/APP-000056.json"
                ),
                config={"configurable": {"thread_id": "audit-1"}},
            )
        finally:
            if context is not None:
                context.__exit__(None, None, None)

        records = tool_logging.read_log(tool_logging.AGENT_ACTION_LOG)
        assert records

        actors = {r.get("actor") for r in records}
        actions = {r.get("action") for r in records}
        # The decisions a reviewer would ask about, each attributable.
        assert "supervisor" in actors
        assert {"intake", "eligibility_agent", "recommendation_agent"} <= actors
        assert "route_request" in actions
        assert "draft_recommendation" in actions
        assert "route_for_human_review" in actions

        for record in records:
            assert record.get("timestamp")
            assert record.get("actor")
            assert record.get("action")

        # A decline is recorded as a decline, with the file it belongs to.
        declines = [r for r in records if r.get("decision") == "DECLINE_RECOMMENDATION"]
        assert declines
        assert declines[0]["application_id"] == "APP-000056"
    finally:
        importlib.reload(tool_logging)
        import src.graph as graph_module

        importlib.reload(graph_module)


@pytest.mark.integration
def test_the_tool_log_reconciles_with_the_tools_the_code_declares(repo_root):
    """AC-07: tool names in the log must reconcile with the agent/MCP code.

    The name is unprefixed whatever the transport, so every name in the log is
    a string that appears in committed source. `transport` carries the rest.
    """
    from src.observability.tool_logging import TOOL_CALL_LOG, read_log
    from src.tools.rag_tool import FETCH_RULES_TOOL_NAME, TOOL_NAME

    if not TOOL_CALL_LOG.exists():
        pytest.skip("no tool-call log yet")

    logged = {r.get("tool_name") for r in read_log(TOOL_CALL_LOG)}
    assert logged

    from mcp_server.capabilities import TOOLS as MCP_TOOLS

    known = {TOOL_NAME, FETCH_RULES_TOOL_NAME} | set(MCP_TOOLS)
    unknown = {name for name in logged if name not in known}
    assert not unknown, f"the log names tools the code does not declare: {unknown}"
