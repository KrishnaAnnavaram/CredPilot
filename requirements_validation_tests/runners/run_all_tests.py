"""
CredPilot requirements-validation runner.

Executes every test case in the registry against a CredPilot implementation, grades each
requirement PASS / FAIL with a 0-100 fit score, and writes the validation report.

Pipeline
--------
    Requirements Document
            v
    Independent Requirements Tests   (this suite)
            v
    CredPilot Implementation         (--target)
            v
    Validation Execution             (this runner)
            v
    PASS / FAIL / SCORE              (reports/)

Grading, as specified by the validation brief
---------------------------------------------
* A test passes only with concrete evidence. No evidence is a FAIL.
* A requirement passes only if EVERY test bound to it passes. Partial implementation
  earns a partial fit score and still FAILS.
* Fit score = weighted percentage of that requirement's tests that passed.
* Final project status is gated on IMPLEMENTATION-class requirements. OPTIONAL and
  ENGAGEMENT requirements are executed, scored and reported separately - see
  ``BASELINE_REQUIREMENTS.md`` for why, and note that nothing about that grouping
  weakens a test.

Usage
-----
    python runners/run_all_tests.py
    python runners/run_all_tests.py --target /path/to/CredPilot
    python runners/run_all_tests.py --suite static --suite governance
    python runners/run_all_tests.py --fail-fast-on-baseline
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SUITE_ROOT))

import bootstrap  # noqa: E402,F401

from baseline_guard import BASELINE_MODIFIED, check_baseline  # noqa: E402
from console import use_utf8_console  # noqa: E402
from evidence_validator import Context  # noqa: E402
from requirement_loader import load_requirements  # noqa: E402
from requirement_validator import (  # noqa: E402
    FAIL,
    PASS,
    RequirementResult,
    TestResult,
    grade_requirement,
    run_test,
    summarise,
)

from automated_tests.registry import TEST_CASES, suites  # noqa: E402

REPORTS = SUITE_ROOT / "reports"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------------------
# Report rendering
# --------------------------------------------------------------------------------------


def render_markdown(payload: dict) -> str:
    s = payload["summary"]
    out: list[str] = [
        "# CredPilot Requirements Validation Report\n",
        f"Generated: {payload['generated_at']}  ",
        f"Implementation under validation: `{payload['target_root']}`  ",
        f"Requirements baseline: `source_requirements/requirements_verbatim.md`  ",
        f"Baseline SHA-256: `{payload['baseline_sha256']}`  ",
        f"Baseline integrity: **{payload['baseline_status']}**  ",
        f"Suites executed: {', '.join(payload['suites_executed'])}  ",
        f"Wall time: {payload['duration_seconds']}s\n",
        "---\n",
        "## Headline\n",
        "```",
        "CredPilot Requirements Validation Report",
        "",
        f"Total Requirements: {s['total_requirements']}",
        f"Tests Executed: {s['tests_executed']}",
        f"Requirements Passed: {s['requirements_passed']}",
        f"Requirements Failed: {s['requirements_failed']}",
        f"Requirement Coverage: {s['requirement_coverage_pct']}%",
        f"Overall Requirement Fit: {s['overall_fit_pct']}%",
        "",
        "Final Status:",
        s["final_status"],
        "```\n",
        "## Breakdown by requirement class\n",
        "| Class | Total | Passed | Failed | Gates final status |",
        "| --- | --- | --- | --- | --- |",
        f"| IMPLEMENTATION | {s['mandatory_total']} | {s['mandatory_passed']} "
        f"| {s['mandatory_failed']} | yes |",
        f"| OPTIONAL | {s['optional_total']} | {s['optional_passed']} "
        f"| {s['optional_total'] - s['optional_passed']} | no - the source text marks these "
        "optional / bonus / good-to-have |",
        f"| ENGAGEMENT | {s['engagement_total']} | {s['engagement_passed']} "
        f"| {s['engagement_total'] - s['engagement_passed']} | no - these describe the "
        "engagement or the evaluator, not the deliverable |",
        "",
        f"Automated tests executed: {s['automated_tests']}  |  "
        f"Manual / non-automatable tests executed: {s['manual_tests']}\n",
    ]

    failed_mandatory = [r for r in payload["requirements"]
                        if r["status"] == FAIL and r["requirement_class"] == "IMPLEMENTATION"]
    out += ["## Failed requirements (IMPLEMENTATION class)\n"]
    if failed_mandatory:
        out += ["| Requirement | Fit | Category | Reason |", "| --- | --- | --- | --- |"]
        out += [f"| {r['requirement_id']} | {r['fit_score']} | {r['category']} | {r['reason']} |"
                for r in failed_mandatory]
    else:
        out.append("None.\n")

    other_failed = [r for r in payload["requirements"]
                    if r["status"] == FAIL and r["requirement_class"] != "IMPLEMENTATION"]
    out += ["\n## Failed requirements (OPTIONAL / ENGAGEMENT - not gating)\n"]
    if other_failed:
        out += ["| Requirement | Class | Fit | Reason |", "| --- | --- | --- | --- |"]
        out += [f"| {r['requirement_id']} | {r['requirement_class']} | {r['fit_score']} "
                f"| {r['reason']} |" for r in other_failed]
    else:
        out.append("None.\n")

    out += ["\n## Fit score by category\n", "| Category | Requirements | Passed | Mean fit |",
            "| --- | --- | --- | --- |"]
    by_cat: dict[str, list] = defaultdict(list)
    for r in payload["requirements"]:
        by_cat[r["category"]].append(r)
    for cat, rows in sorted(by_cat.items()):
        mean = round(sum(x["fit_score"] for x in rows) / len(rows))
        out.append(f"| {cat} | {len(rows)} | {sum(1 for x in rows if x['status'] == PASS)} | {mean} |")

    out += ["\n---\n", "## Per-requirement result\n",
            "Each entry carries the exact original requirement, its status, its fit score, "
            "the actual evidence collected, and a factual reason.\n"]

    for r in payload["requirements"]:
        out += [
            f"### {r['requirement_id']} - {r['status']} ({r['fit_score']}/100)\n",
            f"**Class:** {r['requirement_class']}  |  **Category:** {r['category']}  |  "
            f"**Source:** {r['source_location']}\n",
            "**Requirement:**\n",
            "~~~text",
            r["exact_requirement"],
            "~~~\n",
            f"**Status:** {r['status']}  ",
            f"**Fit Score:** {r['fit_score']}  ",
            f"**Tests:** {', '.join(r['test_ids'])}  ",
            f"**Reason:** {r['reason']}\n",
            "**Evidence:**\n",
            "```",
        ]
        for line in r["evidence"]:
            out.append(line)
        out += ["```\n"]

    out += [
        "---\n",
        "## How to read this report\n",
        "* **PASS** means the implementation provided sufficient verifiable evidence that the "
        "original requirement is satisfied.\n"
        "* **FAIL** means it did not. Partial implementation stays FAIL even where the fit "
        "score is high.\n"
        "* **Fit Score** is the weighted percentage of that requirement's tests that passed: "
        "100 = fully satisfied with evidence; 75-99 = substantial but one or more explicit "
        "parts incomplete; 50-74 = partially implemented; 1-49 = minimal; 0 = absent.\n"
        "* `UNSPECIFIED_BY_REQUIREMENT` in an evidence line means the source document fixes no "
        "value to test against. That is a specification gap recorded honestly, not an "
        "implementation defect, and no threshold was invented to fill it.\n",
        "Do not edit the expectations in this suite to turn a FAIL into a PASS. The "
        "requirements define the expected behaviour; the implementation does not.\n",
    ]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------


def main() -> int:
    use_utf8_console()
    ap = argparse.ArgumentParser(description="Run the CredPilot requirements validation suite.")
    ap.add_argument("--target", default=None,
                    help="Path to the CredPilot implementation. Overrides CREDPILOT_ROOT and "
                         "config/validation_config.json.")
    ap.add_argument("--suite", action="append", default=None, choices=sorted(suites()),
                    help="Run only these suites. Repeatable. Default: all.")
    ap.add_argument("--requirement", action="append", default=None,
                    help="Run only these requirement IDs. Repeatable.")
    ap.add_argument("--json-out", default=str(REPORTS / "latest_test_report.json"))
    ap.add_argument("--md-out", default=str(REPORTS / "latest_test_report.md"))
    ap.add_argument("--quiet", action="store_true", help="Only print the headline block.")
    args = ap.parse_args()

    # --- Baseline protection -----------------------------------------------------------
    status = check_baseline()
    if not status.ok:
        print("=" * 72)
        print(status.code)
        print("=" * 72)
        if status.code == BASELINE_MODIFIED:
            print("The requirements baseline has changed since it was generated from the source")
            print("document. Validation is STOPPED so that a failing implementation cannot be")
            print("made to pass by editing the requirements.")
            print(f"  expected sha256: {status.expected_sha256}")
            print(f"  actual   sha256: {status.actual_sha256}")
        else:
            print(f"  baseline: {status.baseline_path}")
            print(f"  hash file: {status.hash_path}")
        return 3

    reqs = load_requirements()
    ctx = Context(args.target)

    cases = list(TEST_CASES)
    if args.suite:
        cases = [c for c in cases if c.suite in set(args.suite)]
    if args.requirement:
        wanted = set(args.requirement)
        cases = [c for c in cases if c.req_id in wanted]
    cases.sort(key=lambda c: c.test_id)

    if not cases:
        print("No test cases selected.")
        return 4

    if not args.quiet:
        print(f"Requirements baseline : {status.actual_sha256}")
        print(f"Implementation target : {ctx.root}")
        print(f"Target exists         : {ctx.exists}")
        print(f"Target is a git repo  : {ctx.is_git_repo}")
        print(f"Test cases selected   : {len(cases)}\n")

    started = time.perf_counter()
    results: list[TestResult] = []
    for i, case in enumerate(cases, 1):
        result = run_test(case, ctx)
        results.append(result)
        if not args.quiet:
            mark = "PASS" if result.passed else "FAIL"
            print(f"[{i:>3}/{len(cases)}] {mark}  {case.test_id:<14} {case.purpose[:78]}")
    duration = round(time.perf_counter() - started, 2)

    by_req: dict[str, list[TestResult]] = defaultdict(list)
    for r in results:
        by_req[r.req_id].append(r)

    graded: list[RequirementResult] = []
    executed_req_ids = {c.req_id for c in cases}
    for req_id, req in reqs.items():
        if req_id not in executed_req_ids:
            continue
        graded.append(grade_requirement(req, by_req.get(req_id, [])))

    summary = summarise(graded, results)

    payload = {
        "generated_at": _now(),
        "target_root": str(ctx.root),
        "target_exists": ctx.exists,
        "target_is_git_repo": ctx.is_git_repo,
        "baseline_sha256": status.actual_sha256,
        "baseline_status": status.code,
        "suites_executed": sorted({c.suite for c in cases}),
        "duration_seconds": duration,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "partial_run": bool(args.suite or args.requirement),
        "summary": {
            "total_requirements": summary.total_requirements,
            "tests_executed": summary.tests_executed,
            "requirements_passed": summary.requirements_passed,
            "requirements_failed": summary.requirements_failed,
            "requirement_coverage_pct": summary.requirement_coverage_pct,
            "overall_fit_pct": summary.overall_fit_pct,
            "final_status": summary.final_status,
            "failed_requirement_ids": summary.failed_requirement_ids,
            "mandatory_total": summary.mandatory_total,
            "mandatory_passed": summary.mandatory_passed,
            "mandatory_failed": summary.mandatory_failed,
            "optional_total": summary.optional_total,
            "optional_passed": summary.optional_passed,
            "engagement_total": summary.engagement_total,
            "engagement_passed": summary.engagement_passed,
            "automated_tests": summary.automated_tests,
            "manual_tests": summary.manual_tests,
        },
        "requirements": [
            {
                "requirement_id": g.req_id,
                "status": g.status,
                "fit_score": g.fit_score,
                "requirement_class": g.req_class,
                "category": g.category,
                "source_location": g.source_location,
                "exact_requirement": g.exact_requirement,
                "test_ids": g.test_ids,
                "evidence": g.evidence,
                "reason": g.reason,
                "weight_total": g.weight_total,
                "weight_passed": g.weight_passed,
            }
            for g in graded
        ],
        "tests": [
            {
                "test_id": r.test_id,
                "requirement_id": r.req_id,
                "status": r.status,
                "test_type": r.test_type,
                "suite": r.suite,
                "category": r.category,
                "weight": r.weight,
                "automatable": r.automatable,
                "duration_ms": r.duration_ms,
                "evidence": r.evidence,
                "error": r.error,
            }
            for r in results
        ],
    }

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_out.write_text(render_markdown(payload), encoding="utf-8")

    s = payload["summary"]
    print("\n" + "=" * 72)
    print("CredPilot Requirements Validation Report")
    print("")
    print(f"Total Requirements: {s['total_requirements']}")
    print(f"Tests Executed: {s['tests_executed']}")
    print(f"Requirements Passed: {s['requirements_passed']}")
    print(f"Requirements Failed: {s['requirements_failed']}")
    print(f"Requirement Coverage: {s['requirement_coverage_pct']}%")
    print(f"Overall Requirement Fit: {s['overall_fit_pct']}%")
    print("")
    print("Final Status:")
    print(s["final_status"])
    if s["failed_requirement_ids"]:
        print("")
        print("Failed Requirements:")
        for rid in s["failed_requirement_ids"]:
            print(rid)
    print("=" * 72)
    if payload["partial_run"]:
        print("NOTE: partial run - --suite/--requirement was given, so these totals cover only "
              "the selected subset.")
    print(f"\nReports written:\n  {json_out}\n  {md_out}")

    return 0 if s["final_status"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
