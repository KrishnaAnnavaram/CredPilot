#!/usr/bin/env python
"""Build the internal pre-submission peer-review workbook.

    python scripts/build_peer_review_workbook.py

Writes ``reports/CredPilot_Internal_Peer_Review.xlsx`` with the five sheets the
requirements document names — Summary, Categories, Scorecard, Detailed,
Improvement — populated from the live validator report rather than typed in.

**This is not the official review.** It is the delivery team reviewing its own
work before submitting, which is a different thing produced by different people
for a different purpose. The workbook says so on every sheet, and
``REQ-012`` stays open until the actual reviewer produces the actual report. A
spreadsheet with the right five tabs is not the deliverable; the reviewer's
judgement is.

Reviewer notes are left **empty**. Mahesh Rajendra fills them in when he reviews,
and the review status stays ``PENDING REVIEWER CONFIRMATION`` until he does.
Generating "reviewed and approved" text for a review that has not happened is the
one thing this file must never do.

Every evidence path referenced is checked for existence before the workbook is
written: a review pointing at a file that is not there reads as evidence.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REPORT = REPO_ROOT / "requirements_validation_tests" / "reports" / "latest_test_report.json"
OUT = REPO_ROOT / "reports" / "CredPilot_Internal_Peer_Review.xlsx"

TITLE = "CredPilot Internal Pre-Submission Peer Review"
DEVELOPER = "Krishna Annavaram"
REVIEWER = "Mahesh Rajendra"
REVIEW_STATUS = "PENDING REVIEWER CONFIRMATION"

NOT_OFFICIAL = (
    "INTERNAL preparation only. This is the delivery team reviewing its own work "
    "before submission. It is NOT the official Virtusa Hackathon review, NOT an "
    "official score, and the reviewer named here is an internal peer reviewer and "
    "co-developer, NOT an official Virtusa evaluator."
)

#: Category -> (implementation, evidence path, test/report). Paths are checked.
CATEGORIES: list[tuple[str, str, str, str]] = [
    ("Agentic architecture",
     "src/graph.py; src/supervisor.py",
     "logs/agent_actions.jsonl",
     "tests/test_routing.py; tests/test_supervisor.py"),
    ("Context engineering",
     "src/context",
     "logs/tool_calls.jsonl",
     "tests/test_context_engineering.py"),
    ("Memory",
     "src/memory/short_term.py; src/memory/long_term.py; src/memory/semantic.py",
     "logs/memory_test.log",
     "tests/test_memory_persistence.py"),
    ("MCP",
     "mcp_server; src/mcp_host",
     "logs/mcp_transcript.jsonl",
     "tests/test_mcp_capabilities.py"),
    ("RAG",
     "src/rag; src/tools/rag_tool.py",
     "eval/results/retrieval_eval.json",
     "tests/rag"),
    ("Observability",
     "src/observability/tracing.py; scripts/export_traces.py",
     "traces/phoenix_spans.jsonl",
     "tests/test_observability_signals.py"),
    ("Cost / latency",
     "scripts/build_golden_signals.py; scripts/build_dashboard.py",
     "reports/golden_signals.json; reports/dashboard.png",
     "tests/test_observability_signals.py"),
    ("Guardrails / security",
     "src/guardrails/sanitize.py; src/guardrails/policy_guard.py; src/guardrails/redaction.py",
     "logs/agent_actions.jsonl",
     "tests/test_guardrails_library.py; tests/rag/test_security.py; tests/rag/test_pii_logging.py"),
    ("Governance / compliance",
     "docs/risk-register.md; docs/model-card.md; docs/compliance.md; docs/output-risk.md",
     "docs/compliance.md",
     "scripts/verify_evidence_citations.py"),
    ("Evaluation / testing",
     "eval/agent/run_agent_eval.py; eval/agent/judges.py",
     "reports/eval_report.json",
     "tests/test_eval_harness.py"),
    ("Engineering / repeatability",
     "scripts/regenerate_evidence.py; requirements.txt",
     "docs/rag/RUNBOOK.md",
     "tests/rag/test_documentation.py"),
    ("Submission readiness",
     "docs/FINAL_SUBMISSION.md",
     "requirements_validation_tests/reports/final_gap_analysis.md",
     "requirements_validation_tests/runners/run_all_tests.py"),
]

#: Requirement -> (owner, next action) for the open items.
OPEN_ACTIONS: dict[str, tuple[str, str]] = {
    "REQ-008": (f"{DEVELOPER}; {REVIEWER}",
                "Both members sign docs/team/WORKLOG.md, then populate REQ-008-T01."),
    "REQ-009": (f"{DEVELOPER}; {REVIEWER}",
                "Both members sign docs/team/TEAM_ATTESTATION.md, then populate REQ-009-T01."),
    "REQ-010": ("External evaluator",
                "Official rubric review must be carried out by the evaluator."),
    "REQ-011": (DEVELOPER,
                "Push final commit to the assigned Virtusa GitLab from the Virtusa "
                "laptop (T02). T03 is a source gap and cannot close."),
    "REQ-012": ("External evaluator",
                "Reviewer produces the per-team Excel report. This workbook is "
                "internal preparation, not that report."),
    "REQ-013": ("External evaluator",
                "Grade issued and bands applied by the evaluator."),
    "REQ-035": ("N/A - source specification gap",
                "Third-party licence evidence added (docs/THIRD_PARTY_LICENSES.md). "
                "The source requires no licence artifact, so the check cannot pass."),
    "REQ-045": ("N/A - source specification gap",
                "Thresholds come from the retrieved policy corpus. The source states "
                "no DTI number; do not hard-code one."),
    "REQ-046": ("N/A - source specification gap",
                "High-value routing keys off the policy corpus. The source states no "
                "monetary boundary; do not invent one."),
}


def _git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(REPO_ROOT), capture_output=True,
                         text=True, encoding="utf-8", errors="replace", check=False)
    return out.stdout.strip() if out.returncode == 0 else ""


def verify_paths() -> list[str]:
    missing = []
    for _cat, impl, ev, test in CATEGORIES:
        for group in (impl, ev, test):
            for p in [x.strip() for x in group.split(";") if x.strip()]:
                if not (REPO_ROOT / p).exists():
                    missing.append(p)
    return sorted(set(missing))


def build(payload: dict) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    s = payload["summary"]
    reqs = {r["requirement_id"]: r for r in payload["requirements"]}
    tests_by_req: dict[str, list[dict]] = {}
    for t in payload["tests"]:
        tests_by_req.setdefault(t["requirement_id"], []).append(t)

    failed = s["failed_requirement_ids"]
    external = [r for r in failed if OPEN_ACTIONS[r][0] == "External evaluator"]
    spec_gaps = [r for r in failed if OPEN_ACTIONS[r][0].startswith("N/A")]

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="1F4E79")
    warn_fill = PatternFill("solid", fgColor="FFF2CC")
    wrap = Alignment(vertical="top", wrap_text=True)
    top = Alignment(vertical="top")
    bold = Font(bold=True)

    wb = Workbook()
    first = True

    def new_sheet(title, headers, widths, banner=NOT_OFFICIAL):
        nonlocal first
        ws = wb.active if first else wb.create_sheet()
        first = False
        ws.title = title
        ws.append([banner] + [""] * (len(headers) - 1))
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(len(headers), 2))
        c = ws.cell(row=1, column=1)
        c.font = Font(bold=True, color="9C5700")
        c.fill = warn_fill
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 34
        ws.append(headers)
        for cell in ws[2]:
            cell.font, cell.fill, cell.alignment = head_font, head_fill, top
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = "A3"
        return ws

    def finish(ws):
        for row in ws.iter_rows(min_row=3):
            for cell in row:
                cell.alignment = wrap

    # ------------------------------------------------------------------ Summary
    ws = new_sheet("Summary", ["Field", "Value"], [38, 104])
    rows = [
        ("Report title", TITLE),
        ("Report type", "Internal pre-submission peer review (NOT an official review)"),
        ("Project", "CredPilot - Loan Origination & Underwriting Copilot"),
        ("Project type", "Agentic AI Engineer Cross-Cutting Capstone"),
        ("", ""),
        ("Team", f"{DEVELOPER}; {REVIEWER}"),
        ("Team size", 2),
        ("Primary developer", DEVELOPER),
        ("Internal peer reviewer", f"{REVIEWER} (internal peer reviewer / co-developer)"),
        ("Reviewer is an official Virtusa evaluator?", "NO"),
        ("", ""),
        ("Workbook generated (UTC)", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
        ("Review date", "(set by reviewer on confirmation)"),
        ("Review status", REVIEW_STATUS),
        ("", ""),
        ("--- INTERNAL VALIDATOR RESULT ---", ""),
        ("Source", "requirements_validation_tests/reports/latest_test_report.json"),
        ("Requirements baseline SHA-256", payload.get("baseline_sha256", "")),
        ("Baseline integrity", payload.get("baseline_status", "")),
        ("Validator run at (UTC)", payload.get("generated_at", "")),
        ("Requirements passed", s["requirements_passed"]),
        ("Total requirements", s["total_requirements"]),
        ("Requirements failed", s["requirements_failed"]),
        ("Weighted validator fit (%)", s["overall_fit_pct"]),
        ("Implementation status", f"{s['mandatory_passed']}/{s['mandatory_total']}"),
        ("Engagement status", f"{s['engagement_passed']}/{s['engagement_total']}"),
        ("Optional status", f"{s['optional_passed']}/{s['optional_total']}"),
        ("Tests executed", s["tests_executed"]),
        ("", ""),
        ("--- OPEN ITEMS ---", ""),
        ("Open requirements", ", ".join(failed)),
        ("Open external actions",
         f"{len(external)} - {', '.join(external)} (evaluator or submission event)"),
        ("Open specification gaps",
         f"{len(spec_gaps)} - {', '.join(spec_gaps)} (source states no value)"),
        ("Pending team confirmations",
         "REQ-008, REQ-009 - unsigned until both members confirm"),
        ("", ""),
        ("--- INTERNAL vs OFFICIAL ---", ""),
        ("Internal validator score",
         f"{s['requirements_passed']}/{s['total_requirements']} requirements, "
         f"{s['overall_fit_pct']}% weighted fit, against this repository's own "
         f"112-requirement validator."),
        ("Official Virtusa Hackathon score", "NOT AVAILABLE - not yet evaluated."),
        ("Why they are not the same",
         "The official grade is a 7-category / 100-mark Hackathon Rubric that is NOT "
         "present in this repository and has NOT been run. The internal figure is a "
         "different instrument measuring a different thing. It must never be quoted "
         "as an official mark - e.g. 98% internal fit is NOT '98/100 official'."),
    ]
    for field, value in rows:
        ws.append([field, value])
        if str(field).startswith("---") or field in ("Review status",):
            ws.cell(row=ws.max_row, column=1).font = bold
    for row in ws.iter_rows(min_row=3):
        row[0].font = bold if str(row[0].value or "").startswith("---") else Font()
    finish(ws)

    # --------------------------------------------------------------- Categories
    ws = new_sheet("Categories",
                   ["Category", "Implementation", "Evidence path", "Test / report",
                    "Internal review status", "Comments (reviewer)"],
                   [30, 46, 44, 46, 26, 40])
    for cat, impl, ev, test in CATEGORIES:
        ws.append([cat, impl, ev, test, REVIEW_STATUS, ""])
    ws.append(["", "", "", "", "", ""])
    ws.append(["NOTE", "No point weights are assigned. The official 7-category / "
               "100-mark rubric is not present in this repository, and inventing "
               "weights would fabricate the scoring scheme.", "", "", "", ""])
    ws.cell(row=ws.max_row, column=1).font = bold
    finish(ws)

    # ---------------------------------------------------------------- Scorecard
    ws = new_sheet("Scorecard",
                   ["REQ ID", "Requirement", "Internal status", "Fit", "Evidence",
                    "Gap", "Owner", "Next action"],
                   [11, 60, 18, 7, 44, 52, 26, 56])
    for rid in failed:
        r = reqs[rid]
        owner, action = OPEN_ACTIONS[rid]
        failing = [t for t in tests_by_req.get(rid, []) if t["status"] != "PASS"]
        passing = [t for t in tests_by_req.get(rid, []) if t["status"] == "PASS"]
        gap = "; ".join(
            " ".join(str(t["evidence"]).split())[:180] for t in failing
        )
        ws.append([
            rid,
            r["exact_requirement"][:300],
            "OPEN",
            r["fit_score"],
            f"{len(passing)}/{len(passing) + len(failing)} bound tests pass",
            gap,
            owner,
            action,
        ])
    ws.append([""] * 8)
    ws.append(["PASSING", f"{s['requirements_passed']} of {s['total_requirements']} "
               "requirements pass and are not itemised here. Full detail: "
               "requirements_validation_tests/reports/latest_test_report.md",
               "PASS", s["overall_fit_pct"], "", "", "", ""])
    ws.cell(row=ws.max_row, column=1).font = bold
    ws.append([""] * 8)
    ws.append(["NOTE", "Internal validator statuses only. No official marks are "
               "assigned - the official rubric is not present and has not been run.",
               "", "", "", "", "", ""])
    ws.cell(row=ws.max_row, column=1).font = bold
    finish(ws)

    # ----------------------------------------------------------------- Detailed
    ws = new_sheet("Detailed",
                   ["Requirement", "Bound test", "Implementation / evidence file",
                    "Test result", "Evidence summary", "Reviewer notes"],
                   [12, 16, 46, 13, 74, 40])
    for rid in failed:
        for t in sorted(tests_by_req.get(rid, []), key=lambda x: x["test_id"]):
            ev = " ".join(str(t["evidence"]).split())
            ws.append([
                rid,
                t["test_id"],
                t.get("category", ""),
                t["status"],
                ev[:400],
                "",
            ])
    ws.append([""] * 6)
    ws.append(["NOTE", "", "", "", "Reviewer notes are intentionally empty. "
               f"{REVIEWER} completes them when the review is performed; no "
               "approval text is generated on his behalf.", ""])
    ws.cell(row=ws.max_row, column=1).font = bold
    finish(ws)

    # -------------------------------------------------------------- Improvement
    ws = new_sheet("Improvement",
                   ["#", "Action", "Why it matters", "Owner", "Status", "Blocked on"],
                   [5, 56, 56, 28, 28, 46])
    actions = [
        ("Transfer the final project to the Virtusa work laptop and push the exact "
         "final commit to the assigned Virtusa GitLab project",
         "REQ-011-T02. The personal GitHub is development/sharing only and is not "
         "the submission repository.",
         DEVELOPER, "NOT STARTED", "Access to the Virtusa laptop and the assigned "
         "GitLab project URL"),
        ("Record the GitLab remote URL, final commit SHA, branch and push timestamp "
         "in docs/FINAL_SUBMISSION.md, then verify the commit exists on the remote",
         "Makes the submission auditable rather than asserted.",
         DEVELOPER, "NOT STARTED", "The push actually happening"),
        ("Both members sign docs/team/TEAM_ATTESTATION.md, then populate REQ-009-T01",
         "REQ-009. Team size is an event fact no artifact can establish.",
         f"{DEVELOPER}; {REVIEWER}", "PENDING SIGNATURE", "Both members confirming"),
        ("Both members sign docs/team/WORKLOG.md, then populate REQ-008-T01",
         "REQ-008. Exact task-level hours are not mechanically derivable from Git.",
         f"{DEVELOPER}; {REVIEWER}", "PENDING SIGNATURE", "Both members confirming"),
        (f"{REVIEWER} completes docs/team/PEER_REVIEW.md and the reviewer notes in "
         "this workbook, then sets review status to REVIEWED",
         "Internal review evidence. Not a substitute for the official review.",
         REVIEWER, REVIEW_STATUS, "Reviewer performing the review"),
        ("Official automated review against the Hackathon Rubric",
         "REQ-010. The team's own validation is not the evaluation the requirement "
         "describes.",
         "External evaluator", "EXTERNAL - PENDING", "The evaluator running it"),
        ("Official per-team Excel review report produced by the reviewer",
         "REQ-012. This workbook is internal preparation and is not that report.",
         "External evaluator", "EXTERNAL - PENDING", "The evaluator producing it"),
        ("Grade awarded and bands applied (Pass >= 60, Not Yet Passed < 60)",
         "REQ-013. The bands are recorded here; whether they were applied is the "
         "evaluator's fact.",
         "External evaluator", "EXTERNAL - PENDING", "A grade being issued"),
        ("Re-run the Gemini judge (eval/requirements_judge.py) once API credits are "
         "restored",
         "Every Gemini model currently returns 402 RESOURCE_EXHAUSTED, so judged "
         "metrics are null rather than measured.",
         DEVELOPER, "BLOCKED", "Google AI Studio prepayment credits"),
        ("Regenerate DeepEval judged metrics once credits are restored",
         "reports/eval_report.json currently carries null judge_* metrics with the "
         "reason recorded. Deterministic metrics are unaffected.",
         DEVELOPER, "BLOCKED", "Google AI Studio prepayment credits"),
        ("Re-run scripts/regenerate_evidence.py and the three verifier scripts "
         "before the final push",
         "Evidence freshness: committed measurements must come from the committed "
         "code state.",
         DEVELOPER, "NOT STARTED", "Final code freeze"),
        ("Final secret scan and clean git status before the push",
         "No .env, key, token, credential or PII may be committed.",
         DEVELOPER, "NOT STARTED", "Final code freeze"),
        ("REQ-035 - LangGraph MIT licence",
         "Third-party licence evidence is now recorded in "
         "docs/THIRD_PARTY_LICENSES.md and reports/dependency_licenses.json. The "
         "source requires no licence artifact, so the check itself cannot pass.",
         "N/A - source specification gap", "WILL NOT CLOSE", "The source document"),
        ("REQ-045 - numeric DTI threshold",
         "Thresholds are read from the retrieved, versioned policy corpus at "
         "runtime. The source document states no DTI figure.",
         "N/A - source specification gap", "WILL NOT CLOSE", "The source document"),
        ("REQ-046 - high-value monetary boundary",
         "High-value routing keys off the policy corpus classification. The source "
         "document states no monetary boundary.",
         "N/A - source specification gap", "WILL NOT CLOSE", "The source document"),
    ]
    for i, (action, why, owner, status, blocked) in enumerate(actions, 1):
        ws.append([i, action, why, owner, status, blocked])
    finish(ws)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)


def main() -> int:
    from src.console import use_utf8_stdio

    use_utf8_stdio()

    if not REPORT.exists():
        print(f"ERROR: no validator report at {REPORT}.")
        print("Run: python requirements_validation_tests/runners/run_all_tests.py")
        return 2

    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    if payload.get("partial_run"):
        print("ERROR: that report is from a partial validator run.")
        return 2

    missing = verify_paths()
    if missing:
        print("CITED PATH(S) DO NOT EXIST:")
        for m in missing:
            print(f"  - {m}")
        print("\nA review pointing at a file that is not there reads as evidence.")
        return 1

    undisposed = [r for r in payload["summary"]["failed_requirement_ids"]
                  if r not in OPEN_ACTIONS]
    if undisposed:
        print(f"ERROR: no owner/next-action for: {', '.join(undisposed)}")
        return 1

    build(payload)

    s = payload["summary"]
    print(f"Title          : {TITLE}")
    print(f"Developer      : {DEVELOPER}")
    print(f"Reviewer       : {REVIEWER} (internal peer reviewer, NOT a Virtusa evaluator)")
    print(f"Review status  : {REVIEW_STATUS}")
    print(f"Validator      : {s['requirements_passed']}/{s['total_requirements']} "
          f"({s['overall_fit_pct']}% fit)")
    print(f"Open           : {', '.join(s['failed_requirement_ids'])}")
    print("Sheets         : Summary, Categories, Scorecard, Detailed, Improvement")
    print(f"\nWritten: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
