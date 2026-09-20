"""
Composite checks used by more than one test case, or too specific for a primitive.

Each function is a check: it takes a :class:`Context` and returns an :class:`Evidence`.
Factories return such a function.

These exist because several requirements in the source document name a COUNT ("supervisor
+ >=3 worker agents", ">=2 tools + 1 resource", ">=3 real failures") or a RELATIONSHIP
("names reconcile with code", "wired into the I/O path", "the underlying data file it was
drawn from"), and those cannot be reduced to a single regex without losing the point.
"""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

import bootstrap  # noqa: F401
from evidence_validator import (
    Context,
    Evidence,
    _parse,
    _read_text,
    combine,
    file_exists,
    found,
    locate_dir,
    locate_file,
    missing,
    read_jsonl,
)

# --------------------------------------------------------------------------------------
# The artifact inventory the source document names by path.
# Nothing here is invented: each entry appears literally in Section 5, 7 or 8.
# --------------------------------------------------------------------------------------

NAMED_ARTIFACTS: tuple[str, ...] = (
    "src/graph.py",
    "logs/mcp_transcript.jsonl",
    "tests/test_memory_persistence.py",
    "logs/memory_test.log",
    "src/tools/rag_tool.py",
    "src/observability/tracing.py",
    "traces/phoenix_spans.parquet",
    "traces/phoenix_spans.jsonl",
    "logs/tool_calls.jsonl",
    "docs/failure-analysis.md",
    "reports/golden_signals.json",
    "reports/dashboard.png",
    "reports/dashboard_data.csv",
    "logs/agent_actions.jsonl",
    ".env.example",
    ".gitignore",
    "docs/risk-register.md",
    "docs/model-card.md",
    "docs/compliance.md",
    "docs/output-risk.md",
    "reports/eval_report.json",
    "tests/test_routing.py",
    "tests/test_loops.py",
    "tests/test_tool_contracts.py",
    "README.md",
)

#: Artifacts the document explicitly calls machine-generated, with the producer patterns
#: that Section 8 says generate them.
MACHINE_GENERATED: dict[str, tuple[str, ...]] = {
    "logs/tool_calls.jsonl": (r"tool_calls\.jsonl",),
    "logs/agent_actions.jsonl": (r"agent_actions\.jsonl",),
    "logs/mcp_transcript.jsonl": (r"mcp_transcript\.jsonl",),
    "reports/golden_signals.json": (r"golden_signals\.json",),
    "reports/dashboard_data.csv": (r"dashboard_data\.csv",),
    "reports/eval_report.json": (r"eval_report\.json",),
    "traces/phoenix_spans.parquet": (r"phoenix_spans\.parquet", r"get_spans_dataframe"),
    "logs/memory_test.log": (r"memory_test\.log",),
}

SENSITIVE_LOG_PATTERNS = (
    r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",  # card numbers
    r"\baccount[_\- ]?number\"?\s*[:=]\s*\"?\d{6,}",                     # account numbers
    r"\bssn\"?\s*[:=]\s*\"?\d{3}-?\d{2}-?\d{4}",                         # credit identifier
)

LOG_SUFFIXES = (".jsonl", ".log", ".csv", ".txt")


# --------------------------------------------------------------------------------------
# Committed-evidence checks
# --------------------------------------------------------------------------------------


def all_named_evidence_committed(ctx: Context) -> Evidence:
    """Every artifact the document names by path, if it exists, is git-tracked."""
    if not ctx.is_git_repo:
        return missing(
            f"{ctx.root} is not a Git repository, so no artifact in it can be shown to be "
            "committed evidence. Under the Evidence-in-Repo Rule nothing here is scorable."
        )
    tracked = ctx.git_tracked()
    present: list[str] = []
    uncommitted: list[str] = []
    for rel in NAMED_ARTIFACTS:
        loc = locate_file(ctx, rel)
        if loc.path is None:
            continue
        actual = ctx.rel(loc.path)
        (present if actual in tracked else uncommitted).append(actual)
    if not present and not uncommitted:
        return missing(
            "None of the artifacts the source document names by path exist in the "
            f"implementation, so there is no committed evidence to score. "
            f"Looked for {len(NAMED_ARTIFACTS)} named paths under {ctx.root}."
        )
    if uncommitted:
        return missing(
            f"{len(uncommitted)} artifact(s) exist on disk but are not listed by 'git ls-files': "
            + ", ".join(uncommitted)
            + f". Committed: {len(present)}."
        )
    return found(
        f"All {len(present)} present named artifact(s) are committed: " + ", ".join(present),
        committed=present,
    )


def evidence_artifacts_have_producers(ctx: Context) -> Evidence:
    """Each machine-generated artifact that exists has committed code that writes it."""
    sources = {ctx.rel(p): _read_text(p) for p in ctx.all_files() if p.suffix == ".py"}
    if not sources:
        return missing(f"No Python sources under {ctx.root}, so no artifact can have producing code.")

    parts: list[Evidence] = []
    considered = 0
    for artifact, patterns in MACHINE_GENERATED.items():
        loc = locate_file(ctx, artifact)
        if loc.path is None:
            continue  # absence is scored by the requirement that names the artifact
        considered += 1
        hit = None
        for pat in patterns:
            rx = re.compile(pat, re.IGNORECASE)
            for rel, text in sources.items():
                m = rx.search(text)
                if m:
                    line_no = text.count("\n", 0, m.start()) + 1
                    hit = found(
                        f"{artifact} <- produced by {rel}:{line_no}: "
                        f"{text.splitlines()[line_no - 1].strip()[:160]}"
                    )
                    break
            if hit:
                break
        parts.append(hit or missing(
            f"{artifact} exists but no committed Python source references it - it cannot be "
            "shown to be machine-generated rather than hand-written"
        ))
    if considered == 0:
        return missing(
            "None of the machine-generated evidence artifacts named by the document exist, "
            "so no producing code can be evidenced."
        )
    return combine(f"producing code for {considered} present evidence artifact(s)", parts, "all")


# --------------------------------------------------------------------------------------
# Self-scoping check for REQ-016
# --------------------------------------------------------------------------------------


_UNSCORED_TOPICS = (
    (r"visual\s+polish|css|styling|look[\s-]and[\s-]feel|pixel", "interface visual polish"),
    (r"unit[\s-]test\s+(count|volume|number)|coverage\s+percent", "generic unit-test volume"),
    (r"must\s+(use|deploy\s+via)\s+(docker|kubernetes|k8s|rancher)", "a mandated deployment path"),
)


#: The requirements whose own text IS the exclusion. A test bound to one of these
#: necessarily names the excluded topic in order to assert its absence, so naming it is
#: not the same as scoring it.
_EXCLUSION_STATING_REQUIREMENTS = frozenset({"REQ-016", "REQ-067"})


def suite_excludes_unscored_topics(_ctx: Context) -> Evidence:
    """The validation suite itself does not score what the document excludes.

    A test only "scores" an excluded topic if it would mark an implementation down for
    lacking it. A NEGATIVE_TEST asserts the topic's ABSENCE, and a test bound to the
    exclusion statement itself has to name the topic to exclude it - neither counts.
    """
    from . import TEST_CASES  # local import: the registry is built at module import

    offenders: list[str] = []
    scanned = 0
    for case in TEST_CASES:
        if case.req_id in _EXCLUSION_STATING_REQUIREMENTS or case.test_type == "NEGATIVE_TEST":
            continue
        scanned += 1
        blob = " ".join([case.purpose, case.expected_result, case.pass_condition]).lower()
        for pattern, topic in _UNSCORED_TOPICS:
            if re.search(pattern, blob):
                offenders.append(f"{case.test_id} would score {topic}")
    if offenders:
        return missing(
            "The validation suite scores material the source document excludes from evaluation:\n"
            + "\n".join(offenders)
        )
    return found(
        f"Scanned {scanned} of {len(TEST_CASES)} registered test cases (excluding the "
        f"{len(_EXCLUSION_STATING_REQUIREMENTS)} exclusion-stating requirements and the "
        "absence-asserting NEGATIVE_TESTs, which must name a topic in order to exclude it): "
        "none would score interface visual polish, generic unit-test volume, or a particular "
        "optional deployment path.",
        scanned=scanned,
    )


# --------------------------------------------------------------------------------------
# README / command checks
# --------------------------------------------------------------------------------------


_CONTAINER_CMD = re.compile(r"(?m)^\s*\$?\s*(docker|docker-compose|kubectl|helm)\b")


def no_container_command_in_readme(ctx: Context) -> Evidence:
    loc = locate_file(ctx, "README.md")
    if loc.path is None:
        return missing(
            "No README.md exists, so the documented run path cannot be established and cannot be "
            "shown to be free of containerized or cloud deployment."
        )
    text = _read_text(loc.path)
    hits = [
        f"line {text.count(chr(10), 0, m.start()) + 1}: {m.group(0).strip()}"
        for m in _CONTAINER_CMD.finditer(text)
    ]
    if hits:
        return missing(
            f"{ctx.rel(loc.path)} documents container/cloud deployment command(s):\n"
            + "\n".join(hits[:10])
        )
    return found(
        f"{ctx.rel(loc.path)} ({len(text.splitlines())} lines) documents no docker / "
        "docker-compose / kubectl / helm command, so the run path does not depend on "
        "containerized or cloud deployment."
    )


def documented_commands(ctx: Context) -> Evidence:
    """README documents the run, the trace regeneration and the evaluation commands."""
    from response_validator import discover_run_command

    parts: list[Evidence] = []
    for kind, human in (("run", "run the copilot"),
                        ("traces", "regenerate the Phoenix traces"),
                        ("eval", "regenerate the evaluation")):
        disc = discover_run_command(ctx, kind)
        parts.append(
            found(f"documented command to {human}: '{disc.command}' (from {disc.origin})")
            if disc.command
            else missing(f"no documented command to {human}: {disc.origin}")
        )
    return combine("documented regeneration commands", parts, "all")


def readme_documents_single_command(ctx: Context) -> Evidence:
    """NFR-02 / 7.7: one documented command runs the copilot, a second regenerates evidence."""
    from response_validator import discover_run_command

    run = discover_run_command(ctx, "run")
    traces = discover_run_command(ctx, "traces")
    ev = discover_run_command(ctx, "eval")
    parts = [
        found(f"single documented run command: '{run.command}' (from {run.origin})")
        if run.command else missing(f"no single documented run command: {run.origin}"),
        found(f"second documented command regenerates traces: '{traces.command}'")
        if traces.command else missing(f"no documented trace-regeneration command: {traces.origin}"),
        found(f"documented command regenerates the evaluation: '{ev.command}'")
        if ev.command else missing(f"no documented evaluation command: {ev.origin}"),
    ]
    return combine("single documented command plus a regeneration command", parts, "all")


def cli_present(ctx: Context) -> Evidence:
    """A CLI entry point exists and is documented. The document marks the CLI required."""
    parts: list[Evidence] = []

    entry: Evidence | None = None
    for p in (q for q in ctx.all_files() if q.suffix == ".py"):
        tree = _parse(str(p))
        if tree is None:
            continue
        text = _read_text(p)
        if re.search(r"argparse\.ArgumentParser|import\s+click|import\s+typer|from\s+typer", text):
            entry = found(f"CLI parser defined in {ctx.rel(p)}")
            break
        if p.name in ("__main__.py", "cli.py", "main.py") and "__main__" in text:
            entry = found(f"CLI entry module {ctx.rel(p)}")
            break
    if entry is None:
        for manifest in ("pyproject.toml", "setup.cfg", "setup.py"):
            loc = locate_file(ctx, manifest)
            if loc.path and re.search(r"console_scripts|\[project\.scripts\]|entry_points",
                                      _read_text(loc.path)):
                entry = found(f"console-script entry point declared in {ctx.rel(loc.path)}")
                break
    parts.append(entry or missing(
        "no CLI entry point found: no argparse/click/typer parser, no __main__/cli/main module, "
        "and no console-script declaration"
    ))

    from response_validator import discover_run_command

    disc = discover_run_command(ctx, "run")
    parts.append(
        found(f"CLI invocation documented: '{disc.command}' (from {disc.origin})")
        if disc.command else missing(f"CLI invocation is not documented: {disc.origin}")
    )
    return combine("required CLI interface", parts, "all")


def optional_surface_reported(relpath: str, label: str):
    """The document marks this surface optional / bonus, so absence is not a defect.

    It fails only if the optional surface has DISPLACED the required interface.
    """

    def check(ctx: Context) -> Evidence:
        loc = locate_dir(ctx, relpath)
        if loc.path is None:
            return found(
                f"{label}: not present at or near '{relpath}'. The source text marks this surface "
                "optional / bonus and explicitly not required, so its absence satisfies the "
                "interface requirement."
            )
        cli = cli_present(ctx)
        if cli.ok:
            return found(
                f"{label}: present at {ctx.rel(loc.path)} as an addition to the required CLI.\n"
                + cli.summary
            )
        return missing(
            f"{label}: present at {ctx.rel(loc.path)} but the REQUIRED CLI interface is not, so "
            "the optional surface has displaced the required one.\n" + cli.summary
        )

    return check


# --------------------------------------------------------------------------------------
# Git remote
# --------------------------------------------------------------------------------------


def remote_matches_gitlab(ctx: Context) -> Evidence:
    if not ctx.is_git_repo:
        return missing(f"{ctx.root} is not a Git repository, so it has no remote to inspect.")
    try:
        out = subprocess.run(["git", "remote", "-v"], cwd=str(ctx.root), capture_output=True,
                             text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):  # pragma: no cover
        return missing("Unable to execute 'git remote -v'.")
    lines = [ln for ln in out.stdout.splitlines() if ln.strip()]
    if not lines:
        return missing("'git remote -v' returned no remotes: the repository has not been pushed.")
    hits = [ln for ln in lines if re.search(r"gitlab", ln, re.IGNORECASE)]
    if not hits:
        return missing(
            "No configured remote names GitLab, but the submission instruction names a Virtusa "
            "GitLab project. Remotes found:\n" + "\n".join(lines)
        )
    return found("Remote identifies a GitLab project:\n" + "\n".join(hits))


# --------------------------------------------------------------------------------------
# MCP surface
# --------------------------------------------------------------------------------------


_MCP_TOOL_DECORATOR = re.compile(r"@(?:\w+\.)?tool\b|add_tool\(|Tool\(", re.IGNORECASE)
_MCP_RESOURCE_DECORATOR = re.compile(r"@(?:\w+\.)?resource\b|add_resource\(|Resource\(", re.IGNORECASE)


def _decorated_names(tree: ast.AST, decorator_rx: re.Pattern[str], source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                seg = ast.get_source_segment(source, dec) or ""
                if decorator_rx.search(seg):
                    names.add(node.name)
    return names


def mcp_surface(ctx: Context) -> Evidence:
    """REQ-025 / REQ-073: the MCP server exposes >= 2 tools and >= 1 resource."""
    loc = locate_dir(ctx, "mcp_server")
    if loc.path is None:
        return missing("No MCP server package at or near 'mcp_server/'.")
    files = [p for p in ctx.all_files() if p.suffix == ".py" and str(p).startswith(str(loc.path))]
    if not files:
        return missing(f"{ctx.rel(loc.path)} contains no Python sources defining an MCP surface.")

    tools: set[str] = set()
    resources: set[str] = set()
    for p in files:
        src = _read_text(p)
        tree = _parse(str(p))
        if tree is None:
            continue
        tools |= _decorated_names(tree, _MCP_TOOL_DECORATOR, src)
        resources |= _decorated_names(tree, _MCP_RESOURCE_DECORATOR, src)

    parts = [
        found(f">=2 MCP tools: {len(tools)} registered {sorted(tools)}")
        if len(tools) >= 2
        else missing(f"only {len(tools)} MCP tool(s) registered {sorted(tools)}, the document "
                     f"requires at least 2"),
        found(f">=1 MCP resource: {len(resources)} registered {sorted(resources)}")
        if len(resources) >= 1
        else missing("no MCP resource registered; the document requires at least 1"),
    ]
    return combine(f"MCP surface in {ctx.rel(loc.path)} ({len(files)} module(s))", parts, "all")


# --------------------------------------------------------------------------------------
# Counting worker agents
# --------------------------------------------------------------------------------------


def supervisor_and_workers(ctx: Context) -> Evidence:
    """REQ-072: 'supervisor + >=3 worker agents'."""
    loc = locate_file(ctx, "src/graph.py")
    if loc.path is None:
        return missing("No graph module at or near 'src/graph.py' in which to count agents.")
    scope = [p for p in ctx.all_files() if p.suffix == ".py"]
    blob = {ctx.rel(p): _read_text(p) for p in scope}

    sup = next((f"{rel}: supervisor" for rel, t in blob.items()
                if re.search(r"supervisor", t, re.IGNORECASE)), None)

    worker_terms = {
        "eligibility-and-affordability agent": r"eligib\w*[_\- ]?(and[_\- ])?afford|afford\w*[_\- ]?(and[_\- ])?eligib",
        "policy-retrieval agent": r"policy[_\- ]?retriev",
        "risk-screening agent": r"risk[_\- ]?screen",
    }
    workers: list[str] = []
    missing_workers: list[str] = []
    for human, pat in worker_terms.items():
        rx = re.compile(pat, re.IGNORECASE)
        hit = next((rel for rel, t in blob.items() if rx.search(t)), None)
        (workers.append(f"{human} -> {hit}") if hit else missing_workers.append(human))

    parts = [
        found(f"supervisor present ({sup})") if sup else missing("no supervisor found in the graph"),
        found(f">=3 worker agents present:\n" + "\n".join(workers))
        if len(workers) >= 3
        else missing(f"only {len(workers)} of the 3 named worker agents found; "
                     f"absent: {missing_workers}"),
    ]
    return combine(f"supervisor + >=3 worker agents (graph at {ctx.rel(loc.path)})", parts, "all")


# --------------------------------------------------------------------------------------
# Trace export content
# --------------------------------------------------------------------------------------


def trace_export_content(ctx: Context) -> Evidence:
    """REQ-078: >=1 full run, spans across multiple agents + every tool call, latencies present."""
    parquet = locate_file(ctx, "traces/phoenix_spans.parquet")
    jsonl = locate_file(ctx, "traces/phoenix_spans.jsonl")
    target = parquet.path or jsonl.path
    if target is None:
        return missing("No trace export at or near 'traces/phoenix_spans.parquet' or '.jsonl'.")

    if target.suffix == ".jsonl":
        records, errors = read_jsonl(target)
        if errors:
            return missing(f"{ctx.rel(target)} has malformed lines: " + "; ".join(errors[:5]))
        if not records:
            return missing(f"{ctx.rel(target)} contains no spans, so no full run is evidenced.")
        keys = set().union(*(r.keys() for r in records))
        names = {str(r.get("name") or r.get("span_name") or "") for r in records}
        latency_keys = [k for k in keys
                        if re.search(r"latency|duration|start_time|end_time", k, re.IGNORECASE)]
        parts = [
            found(f"{len(records)} span(s) exported from at least one full run"),
            found(f"spans span multiple components: {sorted(n for n in names if n)[:12]}")
            if len({n for n in names if n}) > 1
            else missing(f"spans cover only {len({n for n in names if n})} distinct name(s); "
                         "the document requires spans across multiple agents and every tool call"),
            found(f"latency evidence present via key(s) {latency_keys}")
            if latency_keys
            else missing(f"no latency/duration key among {sorted(keys)}"),
        ]
        return combine(f"trace export {ctx.rel(target)}", parts, "all")

    # Parquet: verify it is a real Parquet file, then read it if pyarrow/pandas is available.
    head = target.open("rb").read(4)
    if head != b"PAR1":
        return missing(f"{ctx.rel(target)} does not begin with the Parquet magic 'PAR1' "
                       f"(found {head!r}), so it is not a valid trace export.")
    try:
        import pandas as pd  # noqa: PLC0415

        df = pd.read_parquet(target)
    except ImportError:
        return missing(
            f"{ctx.rel(target)} is a valid Parquet file ({target.stat().st_size} bytes) but its "
            "contents could not be inspected: neither pandas nor pyarrow is installed in the "
            "validation environment. Install pandas+pyarrow to complete this check - it is not "
            "passed on the file's existence alone."
        )
    except Exception as exc:  # noqa: BLE001
        return missing(f"{ctx.rel(target)} could not be read as Parquet: {exc}")

    cols = list(df.columns)
    name_col = next((c for c in cols if re.search(r"^name$|span_name", str(c), re.IGNORECASE)), None)
    latency_cols = [c for c in cols
                    if re.search(r"latency|duration|start_time|end_time", str(c), re.IGNORECASE)]
    distinct = int(df[name_col].nunique()) if name_col else 0
    parts = [
        found(f"{len(df)} span row(s) exported from at least one full run")
        if len(df) else missing(f"{ctx.rel(target)} contains 0 spans"),
        found(f"spans cover {distinct} distinct span names (multiple agents + tool calls)")
        if distinct > 1
        else missing(f"spans cover {distinct} distinct name(s); the document requires spans across "
                     "multiple agents and every tool call"),
        found(f"latency evidence present in column(s) {latency_cols}")
        if latency_cols else missing(f"no latency/duration column among {cols}"),
    ]
    return combine(f"trace export {ctx.rel(target)}", parts, "all")


# --------------------------------------------------------------------------------------
# Failure-mode analysis
# --------------------------------------------------------------------------------------


def failure_analysis_content(ctx: Context) -> Evidence:
    """REQ-051 / REQ-080 / REQ-101: >=3 real failures, EACH citing run_id + span_id, + cause + fix."""
    loc = locate_file(ctx, "docs/failure-analysis.md")
    if loc.path is None:
        return missing("No failure-mode analysis at or near 'docs/failure-analysis.md'.")
    text = _read_text(loc.path)

    sections = re.split(r"(?m)^#{2,4}\s+", text)[1:]
    if len(sections) < 3:
        sections = [s for s in re.split(r"(?m)^\s*(?:---+|\*\*\*+)\s*$", text) if s.strip()]

    run_ids = re.findall(r"run[_\- ]?id\s*[:=]?\s*[`\"']?([\w-]{4,})", text, re.IGNORECASE)
    span_ids = re.findall(r"span[_\- ]?id\s*[:=]?\s*[`\"']?([\w-]{4,})", text, re.IGNORECASE)
    tool_log_refs = re.findall(r"tool_calls\.jsonl", text, re.IGNORECASE)
    root_causes = re.findall(r"root\s*cause", text, re.IGNORECASE)
    fixes = re.findall(r"\bfix\b", text, re.IGNORECASE)

    cited = max(len(set(run_ids)), len(tool_log_refs))
    parts = [
        found(f"{len(sections)} documented failure section(s) (>= 3)")
        if len(sections) >= 3
        else missing(f"only {len(sections)} documented failure section(s); the document requires >= 3"),
        found(f"{len(set(run_ids))} distinct run_id and {len(set(span_ids))} distinct span_id citation(s)")
        if run_ids and span_ids
        else (found(f"{len(tool_log_refs)} tool-log record citation(s), the permitted alternative")
              if tool_log_refs
              else missing("no Phoenix run_id + span_id citations and no tool-log record citation")),
        found(f"{cited} failure(s) carry an evidence citation (>= 3)")
        if cited >= 3
        else missing(f"only {cited} failure(s) carry an evidence citation; the document requires "
                     "EACH of >= 3 failures to cite its evidence"),
        found(f"{len(root_causes)} root-cause statement(s)")
        if len(root_causes) >= 3
        else missing(f"only {len(root_causes)} root-cause statement(s) for >= 3 required failures"),
        found(f"{len(fixes)} fix statement(s)")
        if len(fixes) >= 3
        else missing(f"only {len(fixes)} fix statement(s) for >= 3 required failures"),
    ]
    return combine(f"failure-mode analysis {ctx.rel(loc.path)}", parts, "all")


# --------------------------------------------------------------------------------------
# Security / masking
# --------------------------------------------------------------------------------------


def masking_present(ctx: Context) -> Evidence:
    """REQ-031 / REQ-060: masking exists AND no committed log leaks sensitive values."""
    sources = [p for p in ctx.all_files() if p.suffix == ".py"]
    mask_hit = None
    for p in sources:
        text = _read_text(p)
        m = re.search(r"\b(mask|redact|anonymi[sz]e|scrub|saniti[sz]e)\w*\s*\(", text, re.IGNORECASE)
        if m:
            line_no = text.count("\n", 0, m.start()) + 1
            mask_hit = found(f"masking implemented at {ctx.rel(p)}:{line_no}: {m.group(0)}")
            break

    logs = [p for p in ctx.all_files() if p.suffix.lower() in LOG_SUFFIXES]
    leaks: list[str] = []
    for p in logs:
        text = _read_text(p)
        for pat in SENSITIVE_LOG_PATTERNS:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                line_no = text.count("\n", 0, m.start()) + 1
                leaks.append(f"{ctx.rel(p)}:{line_no} matches /{pat}/")

    parts = [
        mask_hit or missing("no masking / redaction implementation found in the Python sources"),
        found(f"no plaintext sensitive identifier in {len(logs)} scanned log/data artifact(s)")
        if not leaks
        else missing(f"{len(leaks)} sensitive value(s) written in plaintext:\n" + "\n".join(leaks[:10])),
    ]
    return combine("PII masking and leak-free logs", parts, "all")


def gitignore_covers_env(ctx: Context) -> Evidence:
    """REQ-056 / REQ-085: .gitignore covers .env, .env.example is committed, no secrets committed."""
    parts: list[Evidence] = []

    gi = locate_file(ctx, ".gitignore")
    if gi.path is None:
        parts.append(missing("no .gitignore found"))
    else:
        text = _read_text(gi.path)
        covered = re.search(r"(?m)^\s*\.?\*?\.env\b|^\s*\*\.env\s*$|^\s*\.env\s*$", text)
        parts.append(
            found(f"{ctx.rel(gi.path)} ignores .env: {covered.group(0).strip()!r}")
            if covered else missing(f"{ctx.rel(gi.path)} has no rule covering .env")
        )

    ex = locate_file(ctx, ".env.example")
    parts.append(
        found(f"{ctx.rel(ex.path)} present as the committed env-var template")
        if ex.path else missing("no .env.example committed as the env-var config template")
    )

    env_files = [p for p in ctx.all_files() if p.name == ".env"]
    tracked = ctx.git_tracked()
    committed_env = [ctx.rel(p) for p in env_files if ctx.rel(p) in tracked]
    parts.append(
        missing(f"a real .env is committed: {committed_env}")
        if committed_env else found("no .env file is committed")
    )
    return combine("secrets hygiene", parts, "all")


_SECRET_PATTERNS = (
    (r"AIza[0-9A-Za-z_\-]{35}", "Google API key"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style secret key"),
    (r"(?i)\b(api[_\-]?key|secret|token|password)\s*[:=]\s*[\"'][^\"'\s]{16,}[\"']", "inline credential"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key"),
    (r"(?i)\bghp_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"(?i)\bglpat-[A-Za-z0-9_\-]{18,}", "GitLab token"),
)


def no_secrets_committed(ctx: Context) -> Evidence:
    """REQ-056 / REQ-085: no secrets or keys committed anywhere."""
    scanned = [p for p in ctx.all_files()
               if p.suffix.lower() in {".py", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml",
                                       ".toml", ".cfg", ".ini", ".env", ".example", ".sh", ".ps1"}
               or p.name in {".env", ".env.example"}]
    if not scanned:
        return missing(f"No scannable text files under {ctx.root} to check for committed secrets.")
    hits: list[str] = []
    for p in scanned:
        text = _read_text(p)
        for pat, human in _SECRET_PATTERNS:
            for m in re.finditer(pat, text):
                # A placeholder in the committed template is the documented pattern, not a secret.
                literal = m.group(0)
                if re.search(r"your[_\-]?|xxx|placeholder|change[_\-]?me|<[^>]+>|\.\.\.",
                             literal, re.IGNORECASE):
                    continue
                line_no = text.count("\n", 0, m.start()) + 1
                hits.append(f"{ctx.rel(p)}:{line_no}: possible {human}")
    if hits:
        return missing(f"{len(hits)} possible committed secret(s):\n" + "\n".join(hits[:15]))
    return found(f"No committed secret matched {len(_SECRET_PATTERNS)} credential patterns across "
                 f"{len(scanned)} scanned files.")


# --------------------------------------------------------------------------------------
# Resilience
# --------------------------------------------------------------------------------------


def async_tool_and_model_calls(ctx: Context) -> Evidence:
    """REQ-059: the agent pipeline uses async where it calls tools/models."""
    files = [p for p in ctx.all_files() if p.suffix == ".py"]
    if not files:
        return missing(f"No Python sources under {ctx.root}.")
    async_defs: list[str] = []
    awaits: list[str] = []
    for p in files:
        tree = _parse(str(p))
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_defs.append(f"{ctx.rel(p)}:{node.lineno}: async def {node.name}")
            elif isinstance(node, ast.Await):
                awaits.append(f"{ctx.rel(p)}:{node.lineno}")
    parts = [
        found(f"{len(async_defs)} async definition(s):\n" + "\n".join(async_defs[:10]))
        if async_defs else missing("no 'async def' anywhere in the agent pipeline"),
        found(f"{len(awaits)} await expression(s), so the async path is actually used")
        if awaits else missing("no 'await' expression: async is declared but never used"),
    ]
    return combine("async tool/model invocation", parts, "all")


def graceful_degradation(ctx: Context) -> Evidence:
    """REQ-059: graceful degradation on tool/model failure - timeouts, retries, exit conditions."""
    files = [p for p in ctx.all_files() if p.suffix == ".py"]
    if not files:
        return missing(f"No Python sources under {ctx.root}.")
    blob = {ctx.rel(p): _read_text(p) for p in files}

    def _find(pattern: str, human: str) -> Evidence:
        rx = re.compile(pattern, re.IGNORECASE)
        for rel, text in blob.items():
            m = rx.search(text)
            if m:
                line_no = text.count("\n", 0, m.start()) + 1
                return found(f"{human}: {rel}:{line_no}: {text.splitlines()[line_no - 1].strip()[:140]}")
        return missing(f"{human}: no match for /{pattern}/ in {len(blob)} Python file(s)")

    parts = [
        _find(r"\btimeout\b", "timeouts"),
        _find(r"\bretry|retries|tenacity|max_attempts|backoff\b", "retries"),
        _find(r"recursion_limit|max_steps|max_iterations|\bbreak\b|StopIteration|exit_condition",
              "exit conditions"),
        _find(r"except\s+\w*(Error|Exception)", "failure handling around tool/model calls"),
    ]
    return combine("graceful degradation on tool/model failure", parts, "all")


# --------------------------------------------------------------------------------------
# Governance document content
# --------------------------------------------------------------------------------------


def document_covers(relpath: str, required: dict[str, str], label: str):
    """Every named element of a governance document is present.

    ``required`` maps a human name (from the source text) to the regex that evidences it.
    """

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"{label}: no document at or near '{relpath}'.")
        text = _read_text(loc.path)
        parts: list[Evidence] = []
        for human, pattern in required.items():
            m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if m:
                line_no = text.count("\n", 0, m.start()) + 1
                parts.append(found(f"{human}: {ctx.rel(loc.path)}:{line_no}: {m.group(0)[:120]}"))
            else:
                parts.append(missing(f"{human}: no match for /{pattern}/ in {ctx.rel(loc.path)}"))
        return combine(f"{label} at {ctx.rel(loc.path)}", parts, "all")

    return check


def dashboard_pair(ctx: Context) -> Evidence:
    """REQ-082 / REQ-103: the screenshot AND the underlying data file it was drawn from."""
    png = locate_file(ctx, "reports/dashboard.png")
    csv_ = locate_file(ctx, "reports/dashboard_data.csv")
    parts: list[Evidence] = []
    if png.path is None:
        parts.append(missing("no dashboard screenshot at or near 'reports/dashboard.png'"))
    else:
        head = png.path.open("rb").read(8)
        parts.append(
            found(f"{ctx.rel(png.path)}: valid PNG, {png.path.stat().st_size} bytes")
            if head.startswith(b"\x89PNG\r\n\x1a\n")
            else missing(f"{ctx.rel(png.path)} is not a valid PNG (header {head!r})")
        )
    if csv_.path is None:
        parts.append(missing("no underlying data file at or near 'reports/dashboard_data.csv'"))
    else:
        lines = [ln for ln in _read_text(csv_.path).splitlines() if ln.strip()]
        parts.append(
            found(f"{ctx.rel(csv_.path)}: {len(lines) - 1} data row(s), header={lines[0][:160]!r}")
            if len(lines) >= 2
            else missing(f"{ctx.rel(csv_.path)} has no data rows, so the screenshot has no "
                         "underlying data file it was drawn from")
        )
    return combine("cost/latency dashboard screenshot AND its underlying data file", parts, "all")


def pytest_module_asserts(relpath: str, patterns: dict[str, str], label: str):
    """A committed pytest module both contains tests and asserts the named behaviour."""

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"{label}: no test module at or near '{relpath}'.")
        text = _read_text(loc.path)
        tree = _parse(str(loc.path))
        test_fns = []
        if tree is not None:
            test_fns = [n.name for n in ast.walk(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and n.name.startswith("test_")]
        parts = [
            found(f"{ctx.rel(loc.path)} defines {len(test_fns)} test function(s): {test_fns[:8]}")
            if test_fns else missing(f"{ctx.rel(loc.path)} defines no test_* function"),
            found(f"{ctx.rel(loc.path)} contains assertions")
            if re.search(r"\bassert\b|pytest\.raises", text)
            else missing(f"{ctx.rel(loc.path)} contains no assertion, so it asserts nothing"),
        ]
        for human, pattern in patterns.items():
            m = re.search(pattern, text, re.IGNORECASE)
            parts.append(
                found(f"{human}: matched {m.group(0)[:120]!r}") if m
                else missing(f"{human}: no match for /{pattern}/ in {ctx.rel(loc.path)}")
            )
        return combine(f"{label} at {ctx.rel(loc.path)}", parts, "all")

    return check
