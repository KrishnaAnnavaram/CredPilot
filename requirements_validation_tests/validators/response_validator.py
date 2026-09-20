"""
Runtime / black-box response validation.

The task mandates black-box verification first, so the acceptance criteria in
Section 5.1 of the source document are driven through the implementation's own
public surface - the CLI the document requires ("Interface | CLI (required)") -
and the copilot's actual responses and produced artifacts are inspected.

Nothing here invents an interface. The run command is DISCOVERED:

1. ``config/validation_config.json`` -> ``runtime.run_command`` if an operator set it, else
2. the implementation's own ``README.md``, because the document requires a
   "single documented command" (NFR-02) and a "Local-run runbook | README.md".

If no command can be discovered, the runtime checks FAIL and say why. That failure is
itself the correct verdict for NFR-02 / the Local-run runbook requirement - it is never
papered over with a guessed command.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence

from evidence_validator import (
    Context,
    Evidence,
    _read_text,
    combine,
    found,
    locate_file,
    missing,
)

# Decision vocabulary is taken verbatim from AC-03: "(approve / refer / decline)".
DECISION_TERMS = ("approve", "refer", "decline")

SAMPLE_INPUT_DIRS = ("data", "samples", "sample_inputs", "inputs", "fixtures", "examples",
                     "data/samples", "data/applications", "tests/data")
SAMPLE_INPUT_SUFFIXES = (".json", ".jsonl", ".yaml", ".yml", ".csv", ".txt", ".md")

_FENCE = re.compile(r"```(?:bash|sh|shell|console|text|)?\s*\n(?P<body>.*?)```", re.DOTALL)
_COMMAND_HINT = re.compile(
    r"^\s*\$?\s*((?:uv\s+run\s+|poetry\s+run\s+|python3?\s+|py\s+)[-\w./\\ ]*"
    r"|(?:make|credpilot|credpilot-cli)\b.*)$",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------------------
# Command discovery
# --------------------------------------------------------------------------------------


@dataclass
class DiscoveredCommand:
    command: str | None
    origin: str
    candidates: list[str] = field(default_factory=list)


def discover_run_command(ctx: Context, kind: str = "run") -> DiscoveredCommand:
    """Discover the documented command for ``kind`` in {'run', 'traces', 'eval'}."""
    configured = ((ctx.config.get("runtime") or {}).get(f"{kind}_command") or "").strip()
    if configured:
        return DiscoveredCommand(configured, "config/validation_config.json")

    loc = locate_file(ctx, "README.md")
    if loc.path is None:
        return DiscoveredCommand(None, "no README.md found in the implementation")

    text = _read_text(loc.path)
    candidates: list[str] = []
    for block in _FENCE.finditer(text):
        for raw in block.group("body").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if _COMMAND_HINT.match(line):
                candidates.append(line.lstrip("$ ").strip())

    if not candidates:
        return DiscoveredCommand(None, f"{ctx.rel(loc.path)} documents no runnable command")

    keywords = {
        "run": ("run", "cli", "main", "copilot", "app", "start"),
        "traces": ("trace", "phoenix", "span", "observability"),
        "eval": ("eval", "deepeval", "golden", "judge"),
    }[kind]
    for cand in candidates:
        if any(k in cand.lower() for k in keywords):
            return DiscoveredCommand(cand, f"{ctx.rel(loc.path)} (documented command)", candidates)
    if kind == "run":
        return DiscoveredCommand(candidates[0], f"{ctx.rel(loc.path)} (first documented command)",
                                 candidates)
    return DiscoveredCommand(
        None, f"{ctx.rel(loc.path)} documents no command mentioning {keywords}", candidates
    )


# --------------------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------------------


@dataclass
class RunResult:
    ran: bool
    command: str
    returncode: int | None
    stdout: str
    stderr: str
    reason: str = ""

    @property
    def output(self) -> str:
        return f"{self.stdout}\n{self.stderr}"


def runtime_enabled(ctx: Context) -> bool:
    return bool((ctx.config.get("runtime") or {}).get("enabled", True))


def execute(ctx: Context, command: str, extra_args: Sequence[str] = ()) -> RunResult:
    """Run a discovered command inside the implementation root and capture its output."""
    if not runtime_enabled(ctx):
        return RunResult(False, command, None, "", "",
                         "runtime execution disabled in config/validation_config.json")
    timeout = int((ctx.config.get("runtime") or {}).get("timeout_seconds", 300))
    try:
        argv = shlex.split(command, posix=(os.name != "nt")) + list(extra_args)
    except ValueError as exc:
        return RunResult(False, command, None, "", "", f"command is not parseable: {exc}")
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        proc = subprocess.run(
            argv, cwd=str(ctx.root), capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, env=env, check=False,
        )
    except FileNotFoundError:
        return RunResult(False, command, None, "", "", f"executable not found for: {command}")
    except subprocess.TimeoutExpired:
        return RunResult(False, command, None, "", "", f"timed out after {timeout}s")
    except OSError as exc:  # pragma: no cover
        return RunResult(False, command, None, "", "", f"could not execute: {exc}")
    return RunResult(True, " ".join(argv), proc.returncode, proc.stdout, proc.stderr)


def _runtime_prelude(ctx: Context, kind: str) -> tuple[RunResult | None, Evidence | None]:
    disc = discover_run_command(ctx, kind)
    if disc.command is None:
        return None, missing(
            f"No documented '{kind}' command could be discovered: {disc.origin}. "
            "The source document requires a single documented command (NFR-02) and a "
            "Local-run runbook in README.md, so this cannot be substituted with a guess."
        )
    result = execute(ctx, disc.command)
    if not result.ran:
        return result, missing(f"Command '{disc.command}' (from {disc.origin}) did not run: {result.reason}")
    return result, None


# --------------------------------------------------------------------------------------
# Sample inputs
# --------------------------------------------------------------------------------------


def find_sample_inputs(ctx: Context) -> list[Path]:
    """Committed sample inputs, as required by NFR-02 and the Local-run runbook row."""
    hits: list[Path] = []
    for rel in SAMPLE_INPUT_DIRS:
        base = ctx.root / rel
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix.lower() in SAMPLE_INPUT_SUFFIXES:
                hits.append(p)
    return hits


def sample_inputs_committed(label: str = "committed sample inputs") -> Callable[[Context], Evidence]:
    def check(ctx: Context) -> Evidence:
        hits = find_sample_inputs(ctx)
        if not hits:
            return missing(
                f"{label}: no sample input files found under any of {', '.join(SAMPLE_INPUT_DIRS)}"
            )
        tracked = ctx.git_tracked()
        if not ctx.is_git_repo:
            return missing(
                f"{label}: {len(hits)} candidate input file(s) exist but {ctx.root} is not a git "
                "repository, so they cannot be shown to be committed"
            )
        committed_hits = [ctx.rel(p) for p in hits if ctx.rel(p) in tracked]
        if not committed_hits:
            return missing(
                f"{label}: {len(hits)} candidate input file(s) exist but none are git-tracked"
            )
        return found(
            f"{label}: {len(committed_hits)} committed input file(s): "
            + ", ".join(committed_hits[:10]) + ("..." if len(committed_hits) > 10 else ""),
            files=committed_hits,
        )

    return check


# --------------------------------------------------------------------------------------
# Runtime checks
# --------------------------------------------------------------------------------------


def cli_runs(label: str = "documented CLI run") -> Callable[[Context], Evidence]:
    """The documented command executes and exits successfully."""

    def check(ctx: Context) -> Evidence:
        result, failure = _runtime_prelude(ctx, "run")
        if failure is not None:
            return failure
        assert result is not None
        head = "\n".join(result.output.strip().splitlines()[:25])
        if result.returncode != 0:
            return missing(
                f"{label}: '{result.command}' exited {result.returncode}.\n--- output ---\n{head}"
            )
        return found(
            f"{label}: '{result.command}' exited 0.\n--- output (first lines) ---\n{head}",
            command=result.command, returncode=result.returncode,
        )

    return check


def cli_output_contains(
    patterns: Sequence[str], label: str, mode: str = "all", kind: str = "run"
) -> Callable[[Context], Evidence]:
    """The copilot's own observable output satisfies the named expectations."""

    def check(ctx: Context) -> Evidence:
        result, failure = _runtime_prelude(ctx, kind)
        if failure is not None:
            return failure
        assert result is not None
        out = result.output
        parts: list[Evidence] = []
        for pat in patterns:
            m = re.search(pat, out, re.IGNORECASE | re.MULTILINE)
            parts.append(
                found(f"/{pat}/ matched observable output: {m.group(0)[:160]!r}")
                if m else missing(f"/{pat}/ not present in the output of '{result.command}'")
            )
        tail = "\n".join(out.strip().splitlines()[-25:])
        agg = combine(f"{label} (from '{result.command}')", parts, mode)
        agg.summary += f"\n--- observable output (last lines) ---\n{tail}"
        return agg

    return check


def decision_recommendation_present() -> Callable[[Context], Evidence]:
    """AC-03: an approve / refer / decline recommendation appears in observable output."""

    def check(ctx: Context) -> Evidence:
        result, failure = _runtime_prelude(ctx, "run")
        if failure is not None:
            return failure
        assert result is not None
        out = result.output.lower()
        hits = [t for t in DECISION_TERMS if re.search(rf"\b{t}\w*\b", out)]
        if not hits:
            return missing(
                f"No decision recommendation term {list(DECISION_TERMS)} in the output of "
                f"'{result.command}'"
            )
        return found(
            f"Decision vocabulary present in observable output: {hits} "
            f"(from '{result.command}')", terms=hits,
        )

    return check


# --------------------------------------------------------------------------------------
# Citation resolution (Citation-Resolves Rule, REQ-030 / REQ-071)
# --------------------------------------------------------------------------------------


_CITATION = re.compile(
    r"(?:\[[^\]]*\]\((?P<md>[^)\s]+)\))"           # markdown link target
    r"|(?P<code>`[^`\n]+`)"                        # inline code that may name a file
    r"|(?P<bare>\b[\w./-]+\.(?:md|py|json|jsonl|csv|png|parquet|log|txt|yaml|yml)\b)"
)
_ARTIFACT_SUFFIX = re.compile(
    r"\.(?:md|py|json|jsonl|csv|png|parquet|log|txt|yaml|yml)$", re.IGNORECASE
)


def extract_citations(text: str) -> list[str]:
    """File-path-like citations appearing in a governance/analysis document."""
    out: list[str] = []
    for m in _CITATION.finditer(text):
        raw = m.group("md") or m.group("code") or m.group("bare") or ""
        raw = raw.strip("`").strip()
        raw = raw.split("#", 1)[0].strip()
        if raw.startswith(("http://", "https://", "mailto:")):
            continue
        if _ARTIFACT_SUFFIX.search(raw):
            out.append(raw.lstrip("./"))
    seen: list[str] = []
    for c in out:
        if c not in seen:
            seen.append(c)
    return seen


def citations_resolve(
    relpath: str, min_citations: int = 1, label: str = ""
) -> Callable[[Context], Evidence]:
    """Every file-path citation in the document resolves to a committed artifact."""

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"Cannot check citations: no document at or near '{relpath}'")
        text = _read_text(loc.path)
        cites = extract_citations(text)
        rel_doc = ctx.rel(loc.path)
        if len(cites) < min_citations:
            return missing(
                f"{label or rel_doc}: {len(cites)} resolvable-looking citation(s) found, "
                f"the requirement needs at least {min_citations}. Citations seen: {cites}"
            )
        tracked = ctx.git_tracked()
        resolved: list[str] = []
        unresolved: list[str] = []
        for c in cites:
            target = locate_file(ctx, c)
            if target.path is None:
                unresolved.append(f"{c} -> no such artifact in the repository")
            elif ctx.is_git_repo and ctx.rel(target.path) not in tracked:
                unresolved.append(f"{c} -> exists at {ctx.rel(target.path)} but is not committed")
            else:
                resolved.append(f"{c} -> {ctx.rel(target.path)}")
        if unresolved:
            return missing(
                f"{label or rel_doc}: {len(unresolved)} unresolvable citation(s) "
                "(treated as missing per the Citation-Resolves Rule):\n"
                + "\n".join(unresolved[:15])
                + (f"\nResolved: {len(resolved)}" if resolved else "")
            )
        return found(
            f"{label or rel_doc}: all {len(resolved)} citation(s) resolve to committed artifacts\n"
            + "\n".join(resolved[:15]),
            resolved=resolved,
        )

    return check


# --------------------------------------------------------------------------------------
# Reconciliation between evidence artifacts and producing code
# --------------------------------------------------------------------------------------


def tool_names_reconcile(
    log_relpath: str = "logs/tool_calls.jsonl", key: str = "tool_name"
) -> Callable[[Context], Evidence]:
    """AC-07 / 7.2: every tool name in the log is traceable to the agent/MCP source."""

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, log_relpath)
        if loc.path is None:
            return missing(f"Cannot reconcile tool names: no log at or near '{log_relpath}'")
        from evidence_validator import read_jsonl

        records, errors = read_jsonl(loc.path)
        if errors:
            return missing(f"{ctx.rel(loc.path)} has malformed lines: " + "; ".join(errors[:5]))
        names = sorted({str(r[key]) for r in records if r.get(key)})
        if not names:
            return missing(f"{ctx.rel(loc.path)} contains no '{key}' values to reconcile")
        sources = [p for p in ctx.all_files() if p.suffix == ".py"]
        blob = {ctx.rel(p): _read_text(p) for p in sources}
        unreconciled: list[str] = []
        reconciled: list[str] = []
        for name in names:
            hit = next((rel for rel, text in blob.items()
                        if re.search(rf"\b{re.escape(name)}\b", text)), None)
            (reconciled.append(f"{name} -> {hit}") if hit
             else unreconciled.append(name))
        if unreconciled:
            return missing(
                f"{ctx.rel(loc.path)}: {len(unreconciled)} tool name(s) do not reconcile with any "
                f"committed Python source: {unreconciled}"
            )
        return found(
            f"All {len(reconciled)} tool name(s) in {ctx.rel(loc.path)} reconcile with source:\n"
            + "\n".join(reconciled[:15]),
            names=names,
        )

    return check


def artifact_has_producing_code(
    artifact_rel: str, producer_patterns: Sequence[str], label: str
) -> Callable[[Context], Evidence]:
    """Evidence-in-Repo Rule: the artifact exists AND committed code writes it.

    An evidence artifact with no producing code is exactly what the source document
    calls "heavily discounted" - here it is a FAIL, because there is no evidence the
    artifact was machine-generated rather than hand-written.
    """

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, artifact_rel)
        parts: list[Evidence] = []
        if loc.path is None:
            parts.append(missing(f"artifact absent: no file at or near '{artifact_rel}'"))
        else:
            parts.append(found(f"artifact present: {ctx.rel(loc.path)}"))
        sources = [p for p in ctx.all_files() if p.suffix == ".py"]
        producer: Evidence | None = None
        for pat in producer_patterns:
            rx = re.compile(pat, re.IGNORECASE)
            for p in sources:
                m = rx.search(_read_text(p))
                if m:
                    text = _read_text(p)
                    line_no = text.count("\n", 0, m.start()) + 1
                    producer = found(
                        f"producing code: {ctx.rel(p)}:{line_no}: "
                        f"{text.splitlines()[line_no - 1].strip()[:200]}"
                    )
                    break
            if producer:
                break
        parts.append(
            producer or missing(
                f"no committed Python source matches any producer pattern {list(producer_patterns)}"
                f" - the artifact cannot be shown to be machine-generated"
            )
        )
        return combine(label, parts, "all")

    return check


def json_report_written_by_code(
    report_rel: str, required_keys: Sequence[str], producer_patterns: Sequence[str], label: str
) -> Callable[[Context], Evidence]:
    """A JSON evidence report that both parses with the required content AND has a producer."""

    def check(ctx: Context) -> Evidence:
        from evidence_validator import json_keys

        parts = [
            json_keys(report_rel, required_keys, label=label)(ctx),
            artifact_has_producing_code(report_rel, producer_patterns, f"{label}: producer")(ctx),
        ]
        return combine(label, parts, "all")

    return check


def load_manual_config(ctx: Context) -> dict:  # pragma: no cover - convenience
    return json.loads(json.dumps(ctx.config))
