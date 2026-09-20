"""
Composite checks for the Section 7 artifact checklist and the Section 8 evidence formats.

Split from :mod:`_shared_checks` only to keep each module readable; the two are used
interchangeably by the case files.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import bootstrap  # noqa: F401
from evidence_validator import (
    Context,
    Evidence,
    _read_text,
    combine,
    found,
    locate_dir,
    locate_file,
    missing,
    read_jsonl,
)

from ._shared_checks import NAMED_ARTIFACTS


# --------------------------------------------------------------------------------------
# Checklist-level composites (Section 7 lead-in)
# --------------------------------------------------------------------------------------

#: The document offers these two as alternatives for one artifact ("(or .jsonl)").
TRACE_ALTERNATIVES = ("traces/phoenix_spans.parquet", "traces/phoenix_spans.jsonl")


def all_named_artifacts_present(ctx: Context) -> Evidence:
    """REQ-070: each artifact is present at (or near) the path shown."""
    parts: list[Evidence] = []
    for rel in NAMED_ARTIFACTS:
        if rel in TRACE_ALTERNATIVES:
            continue
        loc = locate_file(ctx, rel)
        parts.append(
            found(f"{rel} -> {ctx.rel(loc.path)}" + ("" if loc.exact else " (near match)"))
            if loc.path is not None
            else missing(f"{rel} -> absent")
        )
    alt = next((a for a in TRACE_ALTERNATIVES if locate_file(ctx, a).path is not None), None)
    parts.append(
        found(f"{' or '.join(TRACE_ALTERNATIVES)} -> {alt}")
        if alt else missing(f"{' or '.join(TRACE_ALTERNATIVES)} -> absent")
    )
    return combine("every artifact named by the checklist is present at (or near) its path",
                   parts, "all")


def named_artifacts_have_tests(_ctx: Context) -> Evidence:
    """REQ-069: the checklist the submission is scored against is what this suite scores."""
    from . import TEST_CASES

    blob = " ".join(
        " ".join([c.purpose, c.expected_result, " ".join(c.steps), c.evidence_required])
        for c in TEST_CASES
    )

    def referenced(rel: str) -> bool:
        return rel in blob or Path(rel).name in blob

    # The document presents the two trace paths as alternatives ("(or .jsonl)"), so the
    # checklist entry is covered when either one is referenced.
    uncovered = [rel for rel in NAMED_ARTIFACTS
                 if rel not in TRACE_ALTERNATIVES and not referenced(rel)]
    if not any(referenced(a) for a in TRACE_ALTERNATIVES):
        uncovered.append(" or ".join(TRACE_ALTERNATIVES))
    if uncovered:
        return missing(
            f"{len(uncovered)} checklist artifact(s) are not referenced by any registered test: "
            + ", ".join(uncovered)
        )
    return found(
        f"All {len(NAMED_ARTIFACTS)} checklist artifacts are referenced by the "
        f"{len(TEST_CASES)} registered test cases, so this suite scores the stated checklist."
    )


def structured_artifacts_parse(ctx: Context) -> Evidence:
    """REQ-070: each present artifact contains what is listed - at minimum, real content."""
    parts: list[Evidence] = []
    considered = 0
    for rel in NAMED_ARTIFACTS:
        loc = locate_file(ctx, rel)
        if loc.path is None:
            continue
        considered += 1
        size = loc.path.stat().st_size
        if size == 0:
            parts.append(missing(f"{ctx.rel(loc.path)} is empty (0 bytes), so it contains nothing listed"))
            continue
        if loc.path.suffix == ".jsonl":
            records, errors = read_jsonl(loc.path)
            parts.append(
                found(f"{ctx.rel(loc.path)}: {len(records)} valid JSON record(s)")
                if records and not errors
                else missing(f"{ctx.rel(loc.path)}: {len(records)} record(s), "
                             f"{len(errors)} malformed line(s)")
            )
        elif loc.path.suffix == ".json":
            try:
                json.loads(_read_text(loc.path))
                parts.append(found(f"{ctx.rel(loc.path)}: valid JSON, {size} bytes"))
            except json.JSONDecodeError as exc:
                parts.append(missing(f"{ctx.rel(loc.path)}: invalid JSON: {exc}"))
        else:
            parts.append(found(f"{ctx.rel(loc.path)}: {size} bytes of content"))
    if considered == 0:
        return missing("No checklist artifact exists, so none can contain what is listed.")
    return combine(f"content of {considered} present checklist artifact(s)", parts, "all")


def all_citations_resolve(ctx: Context) -> Evidence:
    """REQ-071: every citation in every committed document resolves to a committed artifact."""
    from response_validator import extract_citations

    docs = [p for p in ctx.all_files() if p.suffix == ".md"]
    if not docs:
        return missing(f"No Markdown documents under {ctx.root} in which citations could resolve.")
    tracked = ctx.git_tracked()
    unresolved: list[str] = []
    resolved = 0
    for d in docs:
        for cite in extract_citations(_read_text(d)):
            target = locate_file(ctx, cite)
            if target.path is None:
                unresolved.append(f"{ctx.rel(d)} cites '{cite}' -> no such artifact")
            elif ctx.is_git_repo and ctx.rel(target.path) not in tracked:
                unresolved.append(f"{ctx.rel(d)} cites '{cite}' -> present but uncommitted")
            else:
                resolved += 1
    if unresolved:
        return missing(
            f"{len(unresolved)} unresolvable citation(s) across {len(docs)} document(s) "
            "(treated as missing per the Citation-Resolves Rule):\n" + "\n".join(unresolved[:20])
        )
    return found(f"All {resolved} citation(s) across {len(docs)} committed document(s) resolve to "
                 "committed artifacts.")


# --------------------------------------------------------------------------------------
# Guardrails, audit, logs
# --------------------------------------------------------------------------------------


def guardrails_wired(ctx: Context) -> Evidence:
    """REQ-053 / REQ-083 / REQ-104: guardrails WIRED INTO the I/O path, blocking or sanitizing."""
    loc = locate_dir(ctx, "src/guardrails")
    parts: list[Evidence] = []
    guard_files: list[Path] = []
    if loc.path is None:
        parts.append(missing("no guardrail package at or near 'src/guardrails/'"))
    else:
        guard_files = [p for p in ctx.all_files()
                       if p.suffix == ".py" and str(p).startswith(str(loc.path))]
        parts.append(
            found(f"guardrail package {ctx.rel(loc.path)} with {len(guard_files)} module(s)")
            if guard_files else missing(f"{ctx.rel(loc.path)} contains no Python modules")
        )

    blob = {ctx.rel(p): _read_text(p) for p in guard_files}
    for human, pattern in (
        ("input guardrail", r"input[_\- ]?guard|validate_input|check_input|on_input"),
        ("output guardrail", r"output[_\- ]?guard|validate_output|check_output|on_output"),
        ("blocks or sanitizes", r"\bblock|\brefus|saniti[sz]e|redact|\braise\b"),
    ):
        hit = next((f"{human}: {rel}" for rel, t in blob.items()
                    if re.search(pattern, t, re.IGNORECASE)), None)
        parts.append(found(hit) if hit
                     else missing(f"{human}: no match for /{pattern}/ in the guardrail package"))

    callers = [p for p in ctx.all_files()
               if p.suffix == ".py" and "guardrail" not in str(p).lower()]
    wired = next((f"{ctx.rel(p)} references the guardrail layer" for p in callers
                  if re.search(r"guardrail", _read_text(p), re.IGNORECASE)), None)
    parts.append(found(f"wired into the I/O path: {wired}") if wired else missing(
        "no module outside the guardrail package references it, so guardrails are not wired into "
        "the agent's I/O path"
    ))
    return combine("input/output guardrails wired into the I/O path", parts, "all")


def audit_trail_records(ctx: Context) -> Evidence:
    """REQ-084 / REQ-105: machine-generated audit trail carrying the five named fields."""
    loc = locate_file(ctx, "logs/agent_actions.jsonl")
    if loc.path is None:
        return missing("No audit trail at or near 'logs/agent_actions.jsonl'.")
    records, errors = read_jsonl(loc.path)
    parts = [
        found(f"{ctx.rel(loc.path)}: {len(records)} audit record(s)")
        if records and not errors
        else missing(f"{ctx.rel(loc.path)}: {len(records)} record(s), {len(errors)} malformed line(s)")
    ]
    seen = set().union(*(r.keys() for r in records)) if records else set()
    for field_name in ("actor", "action", "tool", "decision", "timestamp"):
        parts.append(
            found(f"field '{field_name}' present")
            if any(field_name in r for r in records)
            else missing(f"field '{field_name}' absent; fields seen: {sorted(seen)}")
        )
    middleware = next(
        (ctx.rel(p) for p in ctx.all_files() if p.suffix == ".py"
         and re.search(r"agent_actions\.jsonl", _read_text(p), re.IGNORECASE)),
        None,
    )
    parts.append(found(f"audit middleware writes it: {middleware}") if middleware else missing(
        "no committed Python source writes logs/agent_actions.jsonl, so the audit trail is not "
        "machine-generated by audit middleware"
    ))
    return combine("machine-generated audit trail", parts, "all")


def tool_call_log_fields(ctx: Context) -> Evidence:
    """REQ-050 / REQ-079 / REQ-100: the per-call fields the document names."""
    loc = locate_file(ctx, "logs/tool_calls.jsonl")
    if loc.path is None:
        return missing("No tool-invocation log at or near 'logs/tool_calls.jsonl'.")
    records, errors = read_jsonl(loc.path)
    parts = [
        found(f"{ctx.rel(loc.path)}: {len(records)} tool-call record(s)")
        if records and not errors
        else missing(f"{ctx.rel(loc.path)}: {len(records)} record(s), {len(errors)} malformed line(s)")
    ]
    seen = set().union(*(r.keys() for r in records)) if records else set()
    # Section 7.2 prints "agent/node"; Section 8 prints "agent". Either satisfies that field.
    for human, keys in (
        ("timestamp", ("timestamp",)), ("agent/node", ("agent", "node")),
        ("tool_name", ("tool_name",)), ("args", ("args",)), ("result", ("result",)),
        ("latency_ms", ("latency_ms",)), ("status", ("status",)),
    ):
        hit = [k for k in keys if any(k in r for r in records)]
        parts.append(
            found(f"field '{human}' present as {hit}") if hit
            else missing(f"field '{human}' absent; fields seen: {sorted(seen)}")
        )
    return combine("tool-invocation log per-call fields", parts, "all")


def mcp_transcript_committed(ctx: Context) -> Evidence:
    """REQ-073: a committed tool-call transcript from the MCP server."""
    loc = locate_file(ctx, "logs/mcp_transcript.jsonl")
    if loc.path is None:
        return missing("No MCP tool-call transcript at or near 'logs/mcp_transcript.jsonl'.")
    records, errors = read_jsonl(loc.path)
    parts = [
        found(f"{ctx.rel(loc.path)}: {len(records)} transcript record(s)")
        if records and not errors
        else missing(f"{ctx.rel(loc.path)}: {len(records)} record(s), {len(errors)} malformed line(s)"),
        found(f"{ctx.rel(loc.path)} is committed")
        if ctx.is_git_repo and ctx.rel(loc.path) in ctx.git_tracked()
        else missing(f"{ctx.rel(loc.path)} is not listed by 'git ls-files'"),
    ]
    return combine("committed MCP tool-call transcript", parts, "all")


def golden_signals_content(ctx: Context) -> Evidence:
    """REQ-052 / REQ-081 / REQ-102: latency by span type, tokens, cost, accuracy, hallucination."""
    loc = locate_file(ctx, "reports/golden_signals.json")
    if loc.path is None:
        return missing("No golden-signals report at or near 'reports/golden_signals.json'.")
    try:
        data = json.loads(_read_text(loc.path))
    except json.JSONDecodeError as exc:
        return missing(f"{ctx.rel(loc.path)} is not valid JSON: {exc}")
    blob = json.dumps(data).lower()
    parts = []
    for human, pattern in (
        ("latency for the thinking span type", r"thinking"),
        ("latency for the acting span type", r"acting"),
        ("latency for the tool span type", r"tool"),
        ("tokens in/out", r"token"),
        ("cost estimate", r"cost"),
        ("accuracy from the eval", r"accuracy"),
        ("hallucination rate from the eval", r"hallucinat"),
    ):
        parts.append(
            found(f"{human}: present in {ctx.rel(loc.path)}")
            if re.search(pattern, blob)
            else missing(f"{human}: no '{pattern}' key or value in {ctx.rel(loc.path)}")
        )
    return combine(f"golden-signals report {ctx.rel(loc.path)}", parts, "all")


def golden_signals_percentiles(ctx: Context) -> Evidence:
    """REQ-102: p50/p95 latency by span type, and cost computed as tokens x price."""
    loc = locate_file(ctx, "reports/golden_signals.json")
    if loc.path is None:
        return missing("No golden-signals report at or near 'reports/golden_signals.json'.")
    try:
        blob = json.dumps(json.loads(_read_text(loc.path))).lower()
    except json.JSONDecodeError as exc:
        return missing(f"{ctx.rel(loc.path)} is not valid JSON: {exc}")
    parts = [
        found("p50 latency present") if "p50" in blob else missing("no p50 latency figure"),
        found("p95 latency present") if "p95" in blob else missing("no p95 latency figure"),
    ]
    producer = next(
        (ctx.rel(p) for p in ctx.all_files() if p.suffix == ".py"
         and re.search(r"golden_signals\.json", _read_text(p), re.IGNORECASE)),
        None,
    )
    parts.append(
        found(f"producing script: {producer}") if producer
        else missing("no committed script writes reports/golden_signals.json")
    )
    if producer:
        text = _read_text(ctx.root / producer)
        parts.append(
            found("the producing script reads the Phoenix spans via get_spans_dataframe()")
            if "get_spans_dataframe" in text
            else missing("the producing script does not call get_spans_dataframe(), so the report "
                         "is not Phoenix-derived")
        )
        parts.append(
            found("cost is computed from tokens and a price")
            if re.search(r"cost\s*=\s*.*token|token.*\*\s*.*price|price\s*\*", text, re.IGNORECASE)
            else missing("the producing script does not compute cost as tokens x price")
        )
    return combine("golden-signals derivation", parts, "all")


def eval_report_content(ctx: Context) -> Evidence:
    """REQ-055 / REQ-090 / REQ-107: golden set, hallucination, faithfulness, answer-relevance."""
    loc = locate_file(ctx, "reports/eval_report.json")
    if loc.path is None:
        return missing("No evaluation report at or near 'reports/eval_report.json'.")
    try:
        blob = json.dumps(json.loads(_read_text(loc.path))).lower()
    except json.JSONDecodeError as exc:
        return missing(f"{ctx.rel(loc.path)} is not valid JSON: {exc}")
    parts = []
    for human, pattern in (
        ("hallucination metric", r"hallucinat"),
        ("faithfulness metric", r"faithful"),
        ("answer-relevance metric", r"relevan"),
        ("a golden set of cases", r"golden|test_case|testcase|dataset|cases"),
    ):
        parts.append(
            found(f"{human}: present in {ctx.rel(loc.path)}") if re.search(pattern, blob)
            else missing(f"{human}: no '{pattern}' present in {ctx.rel(loc.path)}")
        )
    harness = next(
        (ctx.rel(p) for p in ctx.all_files() if p.suffix == ".py"
         and re.search(r"eval_report\.json", _read_text(p), re.IGNORECASE)),
        None,
    )
    parts.append(found(f"evaluation harness: {harness}") if harness
                 else missing("no committed harness writes reports/eval_report.json"))
    if harness:
        text = _read_text(ctx.root / harness)
        parts.append(
            found("the harness uses DeepEval (or an equivalent LLM-as-judge)")
            if re.search(r"deepeval|llm[_\- ]?as[_\- ]?judge|judge", text, re.IGNORECASE)
            else missing("the harness shows no DeepEval or equivalent LLM-as-judge usage")
        )
    return combine("agent evaluation report", parts, "all")


def two_phoenix_reports(ctx: Context) -> Evidence:
    """REQ-111 (good-to-have): a measured before/after needs TWO Phoenix-derived reports."""
    candidates = [
        p for p in ctx.all_files()
        if p.suffix in {".json", ".csv"}
        and re.search(r"golden_signals|dashboard_data|before|after|baseline|optimi",
                      p.name, re.IGNORECASE)
    ]
    if len(candidates) < 2:
        return missing(
            f"only {len(candidates)} Phoenix-derived report(s) found "
            f"({[ctx.rel(p) for p in candidates]}); a measured before/after improvement needs two"
        )
    return found(
        f"{len(candidates)} Phoenix-derived report(s) available for a before/after comparison: "
        + ", ".join(ctx.rel(p) for p in candidates[:8]),
        reports=[ctx.rel(p) for p in candidates],
    )
