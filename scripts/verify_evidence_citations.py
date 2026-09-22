"""Check that every machine-evidence citation in the failure analysis resolves.

AC-08 asks for at least three real failures, each citing the evidence that
showed it. A citation is only worth something if it still resolves, and most of
the artifacts it points into — trace exports, tool logs, evaluation reports —
are *regenerated*. A run that fixes a bug is also the run that deletes the
evidence of it, so a document written once and never re-checked drifts into
citing things that are no longer there.

This script is the check. Each entry below names a failure, the artifact its
evidence lives in, and a predicate that must hold in that artifact. It also
asserts that the failure's own section in ``docs/failure-analysis.md`` names
the artifact, so the manifest cannot quietly diverge from the prose.

It verifies that a citation *resolves*. It cannot verify that the prose around
it is honest — that remains a matter of not writing things that are untrue.

Run::

    python scripts/verify_evidence_citations.py

Exits non-zero if any citation no longer resolves. ``tests/test_evidence.py``
runs it.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FAILURE_ANALYSIS = REPO_ROOT / "docs" / "failure-analysis.md"


@dataclass(frozen=True)
class Citation:
    """One checkable claim: failure X cites artifact Y, and Y still says Z."""

    failure: str
    artifact: str
    claim: str
    check: Callable[[Path], tuple[bool, str]]
    #: Substring the failure's own section must contain, if it differs from the
    #: artifact path (a section may cite a file by a link rather than its path).
    mentions: str | None = None


# --------------------------------------------------------------------------------------
# Readers
# --------------------------------------------------------------------------------------


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _sections(text: str) -> dict[str, str]:
    """Split the failure analysis into ``{"F-14": "...section text..."}``."""
    out: dict[str, str] = {}
    parts = re.split(r"(?m)^##\s+(F-\d+)\s+—", text)
    for ident, body in zip(parts[1::2], parts[2::2]):
        out[ident] = body
    return out


# --------------------------------------------------------------------------------------
# The checks
# --------------------------------------------------------------------------------------


def _f14_cold_start(path: Path) -> tuple[bool, str]:
    spans = _jsonl(path)
    named = [s for s in spans if s.get("name") == "graph.intake"]
    hit = [s for s in named if s.get("span_id") == "d95923312aa55be9"]
    if not hit:
        return False, f"span d95923312aa55be9 not in {len(named)} graph.intake span(s)"
    latency = float(hit[0].get("latency_ms") or 0.0)
    if latency < 30_000:
        return False, f"span d95923312aa55be9 is {latency:,.0f} ms, not the cited 31,107"
    others = sorted(float(s.get("latency_ms") or 0.0) for s in named if s is not hit[0])
    p50 = others[len(others) // 2] if others else 0.0
    return True, (
        f"{len(named)} graph.intake spans; d95923312aa55be9 = {latency:,.1f} ms "
        f"against a {p50:,.1f} ms median for the other {len(others)}"
    )


def _f17_required_rule_fetch(path: Path) -> tuple[bool, str]:
    rows = [r for r in _jsonl(path) if r.get("tool_name") == "fetch_policy_rules"]
    if not rows:
        return False, "no fetch_policy_rules records; run scripts/export_traces.py"
    doc_req = [r for r in rows if "DOC-REQ-002" in ((r.get("args") or {}).get("rule_ids") or [])]
    if not doc_req:
        return False, f"{len(rows)} fetch_policy_rules records, none asking for DOC-REQ-002"
    latencies = sorted(float(r.get("latency_ms") or 0.0) for r in doc_req)
    per_call = latencies[len(latencies) // 2]
    return True, (
        f"{len(doc_req)} of {len(rows)} fetch_policy_rules records ask for DOC-REQ-002 "
        f"by id; median {per_call:,.0f} ms for the whole batch"
    )


def _f20_undated_refusal(path: Path) -> tuple[bool, str]:
    rows = [r for r in _jsonl(path) if r.get("action") == "reject_undated_application"]
    if not rows:
        return False, (
            "no reject_undated_application record; run scripts/export_traces.py, "
            "which submits the undated packet"
        )
    decisions = {r.get("decision") for r in rows}
    if decisions != {"MISSING_AS_OF_DATE"}:
        return False, f"unexpected decision(s) on the refusal record: {decisions}"
    return True, (
        f"{len(rows)} reject_undated_application record(s), all MISSING_AS_OF_DATE"
    )


def _f20_nothing_retrieved(path: Path) -> tuple[bool, str]:
    """The refusal's point: no retrieval happened for the undated application."""
    rows = _jsonl(path)
    ids = {
        str((r.get("args") or {}).get("application_id") or "")
        for r in rows
        if r.get("tool_name") in {"retrieve_policy", "fetch_policy_rules"}
    }
    if "APP-999001" in ids:
        return False, "the undated application APP-999001 reached a retrieval tool"
    return True, (
        f"no retrieval record for the undated application, across "
        f"{len(rows)} tool call(s)"
    )


def _f11_run_scoped_threads(path: Path) -> tuple[bool, str]:
    report = json.loads(path.read_text(encoding="utf-8"))
    run_id = report.get("run_id")
    if not run_id:
        return False, "the evaluation report carries no run_id to scope threads with"
    cases_path = path.parent / "eval_cases.jsonl"
    if not cases_path.exists():
        return False, f"{cases_path.name} is missing; cannot check per-case latency"
    cases = _jsonl(cases_path)
    latencies = [float(c.get("latency_ms") or 0.0) for c in cases if c.get("latency_ms")]
    if not latencies:
        return False, "no per-case latency recorded; a replay would be invisible"
    fastest = min(latencies)
    if fastest < 1_000:
        return False, (
            f"a case completed in {fastest:,.0f} ms, which is not enough to run the "
            "graph — the checkpoint replay of F-11 is back"
        )
    return True, (
        f"run_id {run_id} scopes every thread; fastest of {len(latencies)} cases is "
        f"{fastest:,.0f} ms, so none replayed"
    )


def _ac07_no_legacy_tool_names(path: Path) -> tuple[bool, str]:
    """Not a failure citation — the reconciliation AC-07 depends on."""
    rows = _jsonl(path)
    legacy = sorted({
        str(r.get("tool_name")) for r in rows if str(r.get("tool_name")).startswith("mcp:")
    })
    if legacy:
        return False, (
            f"{len(legacy)} tool name(s) under the retired `mcp:` prefix: "
            f"{', '.join(legacy[:4])}"
        )
    transports = {r.get("transport") for r in rows}
    return True, (
        f"{len(rows)} records, no retired names; transports {sorted(map(str, transports))}"
    )


CITATIONS: tuple[Citation, ...] = (
    Citation(
        failure="F-11",
        artifact="reports/eval_report.json",
        claim="the report records a run_id, and no case completed too fast to have run",
        check=_f11_run_scoped_threads,
        mentions="run_id",
    ),
    Citation(
        failure="F-14",
        artifact="docs/evidence/f14-intake-spans.jsonl",
        claim="span d95923312aa55be9 is a 31-second graph.intake against a millisecond median",
        check=_f14_cold_start,
        mentions="f14-intake-spans.jsonl",
    ),
    Citation(
        failure="F-17",
        artifact="logs/tool_calls.jsonl",
        claim="DOC-REQ-002 is fetched by id rather than left to the ranking funnel",
        check=_f17_required_rule_fetch,
        mentions="fetch_policy_rules",
    ),
    Citation(
        failure="F-20",
        artifact="logs/agent_actions.jsonl",
        claim="the undated application is refused as an audited outcome",
        check=_f20_undated_refusal,
        mentions="reject_undated_application",
    ),
    Citation(
        failure="F-20",
        artifact="logs/tool_calls.jsonl",
        claim="nothing was retrieved for the undated application",
        check=_f20_nothing_retrieved,
        mentions="tool_calls.jsonl",
    ),
)

#: Checks that are not citations but that the same artifacts must satisfy.
INVARIANTS: tuple[tuple[str, str, Callable[[Path], tuple[bool, str]]], ...] = (
    (
        "AC-07",
        "logs/tool_calls.jsonl",
        _ac07_no_legacy_tool_names,
    ),
)


def verify() -> list[tuple[bool, str]]:
    """Run every check. Returns ``[(ok, line)]`` in report order."""
    results: list[tuple[bool, str]] = []
    doc_text = FAILURE_ANALYSIS.read_text(encoding="utf-8") if FAILURE_ANALYSIS.exists() else ""
    sections = _sections(doc_text)

    if not doc_text:
        return [(False, f"missing {FAILURE_ANALYSIS.relative_to(REPO_ROOT)}")]

    for citation in CITATIONS:
        path = REPO_ROOT / citation.artifact
        label = f"{citation.failure}  {citation.artifact}"

        section = sections.get(citation.failure)
        if section is None:
            results.append((False, f"{label}  — no section for {citation.failure} in the document"))
            continue
        needle = citation.mentions or citation.artifact
        if needle not in section:
            results.append((
                False,
                f"{label}  — the {citation.failure} section does not mention {needle!r}, "
                "so the citation is in this manifest but not in the document",
            ))
            continue

        if not path.exists():
            results.append((False, f"{label}  — artifact missing"))
            continue
        try:
            ok, detail = citation.check(path)
        except Exception as exc:  # noqa: BLE001 - a broken check is a failed check
            ok, detail = False, f"check raised {type(exc).__name__}: {exc}"
        results.append((ok, f"{label}  — {detail}"))

    for name, artifact, check in INVARIANTS:
        path = REPO_ROOT / artifact
        label = f"{name}  {artifact}"
        if not path.exists():
            results.append((False, f"{label}  — artifact missing"))
            continue
        try:
            ok, detail = check(path)
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"check raised {type(exc).__name__}: {exc}"
        results.append((ok, f"{label}  — {detail}"))

    return results


def _print(results: Iterable[tuple[bool, str]]) -> int:
    failures = 0
    for ok, line in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {line}")
        failures += 0 if ok else 1
    return failures


def main() -> int:
    from src.console import use_utf8_stdio

    use_utf8_stdio()

    print("Evidence citations in docs/failure-analysis.md")
    print()
    results = verify()
    failures = _print(results)
    print()
    total = len(results)
    if failures:
        print(f"{total - failures}/{total} resolve; {failures} do not.")
        return 1
    print(f"{total}/{total} citations resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
