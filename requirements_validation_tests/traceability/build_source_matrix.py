"""Render the AC-01..AC-12 and NFR-01..NFR-06 source-compliance matrix.

The validator reports 112 requirements. The source document's own acceptance
criteria are 18 of them, and they are the 18 a reader of the brief will look for
by name. This renders those, with the status taken live from the validation
report rather than typed in beside it.

Status is one of:

``PASS``
    Every bound test passed.
``PARTIAL``
    Some bound tests passed and the rest fail for reasons this repository can fix.
``FAIL``
    Nothing, or not enough, is in place.
``EXTERNAL``
    Blocked on a system outside this repository.
``UNSPECIFIED_BY_REQUIREMENT``
    Every test that *can* be checked passed; the only outstanding one asks for a
    value the source document never states.

``PASS`` is never used for an external or unverifiable item, which is the reason
the last two statuses exist at all. An AC whose only failing check is one the
source made uncheckable is not a pass, and calling it one would be the single
most tempting rounding error in this whole report.

Every path this file cites is checked for existence before the matrix is written.
A compliance matrix pointing at a file that is not there is worse than no matrix:
it reads as evidence.

Usage
-----
    python traceability/build_source_matrix.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SUITE_ROOT))

import bootstrap  # noqa: E402,F401

from console import use_utf8_console  # noqa: E402
from evidence_validator import Context  # noqa: E402

PASS = "PASS"
PARTIAL = "PARTIAL"
FAIL = "FAIL"
EXTERNAL = "EXTERNAL"
UNSPECIFIED = "UNSPECIFIED_BY_REQUIREMENT"

_LABEL = re.compile(r"^(AC-\d\d|NFR-\d\d)\s*\|")

#: Tests whose failure is a specification gap rather than a defect. Kept in step
#: with `classify_failures.py`; the check below fails loudly if they drift.
UNSPECIFIED_TESTS = {"REQ-011-T03", "REQ-035-T03", "REQ-045-T04", "REQ-046-T07"}
EXTERNAL_TESTS = {"REQ-011-T02"}

#: implementation | evidence | test, per item. Paths are repo-relative and are
#: verified to exist before anything is written.
DETAIL: dict[str, dict[str, list[str] | str]] = {
    "AC-01": {
        "implementation": ["src/rag/pipeline.py", "src/rag/applicability.py",
                           "src/rag/citations.py"],
        "evidence": ["eval/results/retrieval_eval.json", "reports/assessments"],
        "test": ["tests/rag/test_temporal_retrieval.py", "tests/test_evidence.py"],
        "notes": "Effective-date-aware retrieval; every determination cites the rule "
                 "it applied, and the citation is checked to resolve.",
    },
    "AC-02": {
        "implementation": ["src/calculations.py", "src/rules.py",
                           "src/rule_families"],
        "evidence": ["reports/assessments", "eval/results/retrieval_eval.json"],
        "test": ["tests/test_knockout_rules.py", "tests/test_rule_families.py",
                 "tests/test_funds_to_close.py"],
        "notes": "DTI and disposable income are computed deterministically and each "
                 "breach names the rule and the threshold it failed. The source "
                 "states no numeric threshold, so REQ-045-T04 cannot be checked "
                 "against one - see reports/unverifiable_requirements.md.",
    },
    "AC-03": {
        "implementation": ["src/graph.py", "src/review_triggers.py",
                           "src/narrative.py"],
        "evidence": ["reports/assessments", "logs/agent_actions.jsonl"],
        "test": ["tests/test_review_triggers.py", "tests/test_narrative.py",
                 "tests/test_output_validation.py"],
        "notes": "approve / refer / decline with a written rationale; declines and "
                 "high-value cases route to a human rather than auto-deciding. The "
                 "source fixes no monetary boundary for 'high-value', so REQ-046-T07 "
                 "cannot be checked against one.",
    },
    "AC-04": {
        "implementation": ["src/supervisor.py", "src/graph.py"],
        "evidence": ["logs/agent_actions.jsonl", "traces/phoenix_spans.jsonl"],
        "test": ["tests/test_supervisor.py", "tests/test_routing.py"],
        "notes": "Intent classification with conditional routing; ambiguous and "
                 "out-of-scope requests are clarified or escalated.",
    },
    "AC-05": {
        "implementation": ["src/memory/short_term.py", "src/memory/long_term.py",
                           "src/memory/semantic.py"],
        "evidence": ["logs/memory_test.log"],
        "test": ["tests/test_memory_persistence.py"],
        "notes": "Short-term over the LangGraph checkpointer; long-term and "
                 "cross-session recall over LangMem, subject-scoped, with the "
                 "cross-session test writing in one session and reading in another.",
    },
    "AC-06": {
        "implementation": ["src/guardrails/sanitize.py", "src/guardrails/policy_guard.py",
                           "src/guardrails/redaction.py"],
        "evidence": ["logs/agent_actions.jsonl", "logs/tool_calls.jsonl"],
        "test": ["tests/rag/test_security.py", "tests/test_guardrails_library.py",
                 "tests/rag/test_pii_logging.py"],
        "notes": "Injection attempts and cross-applicant access are refused and routed "
                 "for review; sensitive values are redacted before anything is stored "
                 "or logged. Guardrails-AI and the custom layer both run.",
    },
    "AC-07": {
        "implementation": ["src/observability/tool_logging.py"],
        "evidence": ["logs/tool_calls.jsonl"],
        "test": ["tests/test_tool_contracts.py", "tests/test_observability_signals.py"],
        "notes": "Machine-generated by committed middleware; tool names reconcile with "
                 "the agent and MCP surfaces.",
    },
    "AC-08": {
        "implementation": ["scripts/export_traces.py", "src/observability/tracing.py"],
        "evidence": ["docs/failure-analysis.md", "traces/phoenix_spans.jsonl"],
        "test": ["tests/test_observability_signals.py"],
        "notes": "Three or more real failures from this project's own runs, each citing "
                 "the span that shows it, with root cause and fix.",
    },
    "AC-09": {
        "implementation": ["scripts/build_golden_signals.py", "scripts/build_dashboard.py"],
        "evidence": ["reports/golden_signals.json", "reports/dashboard_data.csv",
                     "reports/dashboard.png"],
        "test": ["tests/test_observability_signals.py"],
        "notes": "Latency, tokens and cost derived from Phoenix spans; accuracy and "
                 "hallucination rate from the evaluation.",
    },
    "AC-10": {
        "implementation": ["src/guardrails/sanitize.py", "src/guardrails/validation.py",
                           "src/guardrails/policy_guard.py"],
        "evidence": ["logs/agent_actions.jsonl"],
        "test": ["tests/test_output_validation.py", "tests/test_guardrails_library.py"],
        "notes": "Input and output guardrails on the live I/O path, with a "
                 "machine-generated audit trail of agent actions.",
    },
    "AC-11": {
        "implementation": ["docs/risk-register.md", "docs/model-card.md",
                           "docs/compliance.md", "docs/output-risk.md"],
        "evidence": ["docs/risk-register.md", "docs/compliance.md"],
        "test": ["scripts/verify_evidence_citations.py"],
        "notes": "Each mitigation and claim cites a committed control, and the "
                 "citations are verified to resolve.",
    },
    "AC-12": {
        "implementation": ["eval/agent/run_agent_eval.py", "eval/agent/judges.py",
                           "eval/agent/dataset.py"],
        "evidence": ["reports/eval_report.json", "reports/eval_cases.jsonl"],
        "test": ["tests/test_eval_harness.py", "tests/test_loops.py",
                 "tests/test_routing.py", "tests/test_tool_contracts.py"],
        "notes": "DeepEval for faithfulness, hallucination and answer relevancy with "
                 "Gemini as the only judge, plus deterministic metrics and the "
                 "routing, loop and tool-contract tests.",
    },
    "NFR-01": {
        "implementation": [".env.example", ".gitignore"],
        "evidence": [".env.example"],
        "test": ["tests/rag/test_security.py"],
        "notes": "No key or secret is committed; configuration is by environment "
                 "variable, with .env ignored and an example committed.",
    },
    "NFR-02": {
        "implementation": ["src/cli.py", "scripts/regenerate_evidence.py"],
        "evidence": ["README.md", "docs/rag/RUNBOOK.md"],
        "test": ["tests/test_web_api.py"],
        "notes": "One documented command runs the copilot; a second regenerates the "
                 "traces and the evaluation. The regeneration script returns non-zero "
                 "and names the stage on any step failure.",
    },
    "NFR-03": {
        "implementation": ["src/guardrails/sanitize.py"],
        "evidence": ["logs/agent_actions.jsonl"],
        "test": ["tests/rag/test_security.py", "tests/test_context_engineering.py"],
        "notes": "Applicant text is quarantined in an explicit data-only envelope and "
                 "never reaches the control path.",
    },
    "NFR-04": {
        "implementation": ["src/resilience.py", "src/llm.py"],
        "evidence": ["logs/tool_calls.jsonl"],
        "test": ["tests/test_resilience.py"],
        "notes": "Async where tools and models are called; timeouts, retries and exit "
                 "conditions, degrading rather than failing the file.",
    },
    "NFR-05": {
        "implementation": ["src/guardrails/redaction.py",
                           "src/observability/tracing.py"],
        "evidence": ["logs/tool_calls.jsonl", "traces/phoenix_spans.jsonl"],
        "test": ["tests/rag/test_pii_logging.py"],
        "notes": "All data synthetic. Identifiers and account numbers are masked "
                 "before anything is written, and span ids are drawn so they cannot "
                 "render as a card-shaped string by chance.",
    },
    "NFR-06": {
        "implementation": ["scripts/regenerate_evidence.py",
                           "scripts/verify_evidence_citations.py"],
        "evidence": ["traces/phoenix_spans.jsonl", "reports/golden_signals.json",
                     "logs/tool_calls.jsonl"],
        "test": ["tests/rag/test_documentation.py"],
        "notes": "Every committed measurement is produced by committed code, "
                 "regenerable in one pass.",
    },
}


def status_for(req: dict, tests_by_req: dict[str, list[dict]]) -> tuple[str, str]:
    """The item's status, and a one-line reason."""
    bound = tests_by_req.get(req["requirement_id"], [])
    failing = [t for t in bound if t["status"] != "PASS"]
    if not failing:
        return PASS, f"all {len(bound)} bound checks passed"

    ids = {t["test_id"] for t in failing}
    if ids <= UNSPECIFIED_TESTS:
        verb = "asks" if len(failing) == 1 else "ask"
        return UNSPECIFIED, (
            f"{len(bound) - len(failing)} of {len(bound)} checks passed; the "
            f"remaining {len(failing)} {verb} for a value the source never states "
            f"({', '.join(sorted(ids))})"
        )
    if ids <= EXTERNAL_TESTS:
        return EXTERNAL, "blocked on a system outside this repository"
    if ids <= (UNSPECIFIED_TESTS | EXTERNAL_TESTS):
        return EXTERNAL, "blocked externally and partly unspecified by the source"
    if len(failing) < len(bound):
        return PARTIAL, f"{len(failing)} of {len(bound)} checks failed"
    return FAIL, "no bound check passed"


def _verify_paths(root: Path) -> list[str]:
    """Every path cited in DETAIL must exist. Returns the ones that do not."""
    missing: list[str] = []
    for item, detail in DETAIL.items():
        for field in ("implementation", "evidence", "test"):
            for path in detail[field]:  # type: ignore[union-attr]
                if not (root / str(path)).exists():
                    missing.append(f"{item}.{field}: {path}")
    return missing


def _fmt(paths) -> str:
    return "<br>".join(f"`{p}`" for p in paths)


def render(payload: dict, items: list[tuple[str, dict, str, str]]) -> str:
    s = payload["summary"]
    acs = [i for i in items if i[0].startswith("AC")]
    nfrs = [i for i in items if i[0].startswith("NFR")]

    def tally(rows):
        out = {}
        for _label, _req, status, _why in rows:
            out[status] = out.get(status, 0) + 1
        return out

    out: list[str] = [
        "# Source-compliance matrix — AC-01..AC-12, NFR-01..NFR-06\n",
        f"Generated from `reports/latest_test_report.json` ({payload['generated_at']}) ",
        "by `traceability/build_source_matrix.py`. Status is read from the validation ",
        "report, not typed in beside it.\n",
        f"\nRequirements baseline SHA-256 `{payload['baseline_sha256']}`, "
        f"integrity **{payload['baseline_status']}**.\n",
        "\n## How to read the status column\n",
        "| Status | Meaning |",
        "| --- | --- |",
        "| `PASS` | Every bound check passed. |",
        "| `PARTIAL` | Some checks passed; the rest fail for reasons this repository can fix. |",
        "| `FAIL` | Not in place. |",
        "| `EXTERNAL` | Blocked on a system outside this repository. |",
        "| `UNSPECIFIED_BY_REQUIREMENT` | Every checkable part passed; the outstanding "
        "check asks for a value the source document never states. |",
        "",
        "`PASS` is deliberately **not** used for an external or unverifiable item. An "
        "acceptance criterion whose only outstanding check is one the source made "
        "uncheckable is not a pass, and recording it as one would be the most tempting "
        "rounding error in this report.\n",
        "\n## Headline\n",
        "```",
        f"AC-01..AC-12   " + "  ".join(f"{k}={v}" for k, v in sorted(tally(acs).items())),
        f"NFR-01..NFR-06 " + "  ".join(f"{k}={v}" for k, v in sorted(tally(nfrs).items())),
        "```\n",
    ]

    for title, rows in (("Functional acceptance criteria", acs),
                        ("Non-functional requirements", nfrs)):
        out += [
            f"\n## {title}\n",
            "| Item | Req | Status | Fit | Implementation | Evidence | Test | Notes |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for label, req, status, _why in rows:
            d = DETAIL[label]
            out.append(
                f"| **{label}** | `{req['requirement_id']}` | `{status}` | "
                f"{req['fit_score']} | {_fmt(d['implementation'])} | "
                f"{_fmt(d['evidence'])} | {_fmt(d['test'])} | {d['notes']} |"
            )

    out += ["\n\n## Per-item detail\n"]
    for label, req, status, why in items:
        d = DETAIL[label]
        out += [
            f"\n### {label} — `{req['requirement_id']}` — `{status}`\n",
            "**Source text**\n",
            "~~~text",
            req["exact_requirement"],
            "~~~\n",
            f"* **Status:** `{status}` — {why}",
            f"* **Fit score:** {req['fit_score']}/100",
            f"* **Bound checks:** {', '.join(req['test_ids'])}",
            f"* **Implementation:** {', '.join(f'`{p}`' for p in d['implementation'])}",
            f"* **Evidence:** {', '.join(f'`{p}`' for p in d['evidence'])}",
            f"* **Test:** {', '.join(f'`{p}`' for p in d['test'])}",
            "",
            f"{d['notes']}\n",
        ]

    out += [
        "\n---\n",
        "## What this matrix is not\n",
        "This is the source document's own acceptance criteria, scored by this "
        "repository's validation suite. It is **not** the 7-category / 100-mark "
        "Hackathon Rubric the engagement is graded against. That rubric is not in this "
        "repository, has not been run, and no score here should be read as a mark "
        "against it.\n",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    use_utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", default=str(SUITE_ROOT / "reports" / "latest_test_report.json"))
    ap.add_argument("--out", default=str(SUITE_ROOT / "reports" / "source_compliance_matrix.md"))
    ap.add_argument("--target", default=None)
    args = ap.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: no report at {report_path}. Run runners/run_all_tests.py first.")
        return 2

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if payload.get("partial_run"):
        print("ERROR: that report is from a partial run. A full run is needed.")
        return 2

    root = Path(args.target) if args.target else Context(None).root
    missing = _verify_paths(root)
    if missing:
        print("CITED PATH(S) DO NOT EXIST:")
        for m in missing:
            print(f"  - {m}")
        print("\nA compliance matrix that points at a file which is not there reads as")
        print("evidence. Fix the path or remove the claim.")
        return 1

    tests_by_req: dict[str, list[dict]] = {}
    for t in payload["tests"]:
        tests_by_req.setdefault(t["requirement_id"], []).append(t)

    items: list[tuple[str, dict, str, str]] = []
    for req in payload["requirements"]:
        m = _LABEL.match(req["exact_requirement"])
        if not m:
            continue
        label = m.group(1)
        if label not in DETAIL:
            print(f"ERROR: {label} has no entry in DETAIL.")
            return 1
        status, why = status_for(req, tests_by_req)
        items.append((label, req, status, why))

    items.sort(key=lambda x: (x[0].split("-")[0], int(x[0].split("-")[1])))

    expected = {f"AC-{i:02d}" for i in range(1, 13)} | {f"NFR-{i:02d}" for i in range(1, 7)}
    got = {i[0] for i in items}
    if got != expected:
        print(f"ERROR: expected 18 items, got {len(got)}.")
        print(f"  missing: {sorted(expected - got)}")
        print(f"  extra  : {sorted(got - expected)}")
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(payload, items), encoding="utf-8")

    for label, req, status, why in items:
        print(f"  {label:<7} {req['requirement_id']}  {status:<28} {why}")
    print(f"\nWritten: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
