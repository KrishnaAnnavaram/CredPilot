"""Render the final gap analysis: every open requirement, and what would close it.

`classify_failures.py` says what class each failure belongs to.  This goes one
level deeper, per requirement: which bound tests pass, which fail, the exact
failing condition, and — the question that matters before a submission — whether
a *truthful* team artifact could close it, or whether it needs an external event
or a value the source document never states.

Written as a generator rather than by hand because the answer changes as
attestations are signed and the GitLab push happens.  A hand-written gap list
goes stale the moment someone acts on it, and a stale gap list is worse than
none: it is the document people trust.

Usage
-----
    python requirements_validation_tests/traceability/build_gap_analysis.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SUITE_ROOT))

import bootstrap  # noqa: E402,F401

from console import use_utf8_console  # noqa: E402

DEFAULT_REPORT = SUITE_ROOT / "reports" / "latest_test_report.json"
DEFAULT_OUT = SUITE_ROOT / "reports" / "final_gap_analysis.md"

TEAM_ARTIFACT = "TEAM ARTIFACT CAN SATISFY"
EXTERNAL_EVENT = "NEEDS EXTERNAL EVENT"
SOURCE_GAP = "SOURCE STATES NO VALUE"

#: Per requirement: can a truthful team artifact close it, does it need an
#: external evaluator or event, and is it untestable because the source fixes no
#: value?  Reasoned once, here, so every downstream document agrees.
DISPOSITION: dict[str, dict] = {
    "REQ-008": {
        "route": TEAM_ARTIFACT,
        "external": False,
        "source_gap": False,
        "closes_with": (
            "A truthful duration attestation from the two team members, evidenced by "
            "`docs/team/WORKLOG.md` and `reports/team_worklog.xlsx`. The repository can "
            "show the wall-clock window; only the team can attest to effort inside it."
        ),
        "blocked_on": "Krishna Annavaram and Mahesh Rajendra confirming the statement.",
    },
    "REQ-009": {
        "route": TEAM_ARTIFACT,
        "external": False,
        "source_gap": False,
        "closes_with": (
            "A truthful team-size attestation. Git shows two distinct commit authors, "
            "which is corroboration but not proof of team size; `docs/team/TEAM_ATTESTATION.md` "
            "is the statement itself."
        ),
        "blocked_on": "Krishna Annavaram and Mahesh Rajendra confirming the statement.",
    },
    "REQ-010": {
        "route": EXTERNAL_EVENT,
        "external": True,
        "source_gap": False,
        "closes_with": (
            "Confirmation that the **official** automated review against the Hackathon "
            "Rubric was carried out. The team's own automated validation is recorded in "
            "`docs/team/AUTOMATED_REVIEW_EVIDENCE.md`, but that is the team reviewing "
            "itself and is not the evaluation the requirement describes."
        ),
        "blocked_on": "The official Virtusa evaluator running the rubric review.",
    },
    "REQ-011": {
        "route": EXTERNAL_EVENT,
        "external": True,
        "source_gap": True,
        "closes_with": (
            "`REQ-011-T02` closes when a real assigned Virtusa GitLab remote exists and "
            "the final commit is pushed from the Virtusa work laptop. `REQ-011-T03` "
            "cannot close: the source names a cut-off but states no date or time, and "
            "names the assigned project but no identity."
        ),
        "blocked_on": (
            "The actual push to the assigned Virtusa GitLab project (T02). T03 is a "
            "specification gap and stays open whatever the team does."
        ),
    },
    "REQ-012": {
        "route": EXTERNAL_EVENT,
        "external": True,
        "source_gap": False,
        "closes_with": (
            "The **per-team Excel report produced by the reviewer**. "
            "`reports/CredPilot_Internal_Peer_Review.xlsx` carries the same five "
            "sheets and is internal pre-submission preparation; presenting it as the "
            "reviewer's output would be a false claim about who produced it."
        ),
        "blocked_on": "The official reviewer producing and returning their report.",
    },
    "REQ-013": {
        "route": EXTERNAL_EVENT,
        "external": True,
        "source_gap": False,
        "closes_with": (
            "Confirmation that the stated bands (Pass >= 60, Not Yet Passed < 60) were "
            "the ones applied to an awarded grade. The bands are recorded in the "
            "internal review workbook; whether they were applied is the evaluator's fact."
        ),
        "blocked_on": "A grade being issued by the evaluator.",
    },
    "REQ-035": {
        "route": SOURCE_GAP,
        "external": False,
        "source_gap": True,
        "closes_with": (
            "Nothing the repository can add. `docs/THIRD_PARTY_LICENSES.md` and "
            "`reports/dependency_licenses.json` now evidence LangGraph's MIT licence "
            "from installed package metadata, which is the substantive claim — but the "
            "check asks for a licence *artifact the source requires*, and the source "
            "requires none."
        ),
        "blocked_on": "Nothing. The source places no licence-artifact obligation.",
    },
    "REQ-045": {
        "route": SOURCE_GAP,
        "external": False,
        "source_gap": True,
        "closes_with": (
            "Nothing, without inventing a number. Three of four bound tests pass: the "
            "copilot computes DTI, reports it in observable output, and names the "
            "threshold it failed. The fourth asks for the numeric threshold *the source "
            "document* fixes, and it fixes none."
        ),
        "blocked_on": "Nothing. Hard-coding 43% or 45% would fabricate a source value.",
    },
    "REQ-046": {
        "route": SOURCE_GAP,
        "external": False,
        "source_gap": True,
        "closes_with": (
            "Nothing, without inventing a boundary. Six of seven bound tests pass, "
            "including high-value routing (`src/review_triggers.py`). The seventh asks "
            "for the monetary boundary *the source document* fixes, and it fixes none."
        ),
        "blocked_on": "Nothing. Inventing a dollar figure would fabricate a source value.",
    },
}


def _ev(block) -> str:
    return block if isinstance(block, str) else "\n".join(str(x) for x in block)


def render(payload: dict) -> str:
    s = payload["summary"]
    reqs = {r["requirement_id"]: r for r in payload["requirements"]}
    by_req: dict[str, list[dict]] = {}
    for t in payload["tests"]:
        by_req.setdefault(t["requirement_id"], []).append(t)

    failed = s["failed_requirement_ids"]
    team = [r for r in failed if DISPOSITION[r]["route"] == TEAM_ARTIFACT]
    ext = [r for r in failed if DISPOSITION[r]["route"] == EXTERNAL_EVENT]
    gap = [r for r in failed if DISPOSITION[r]["route"] == SOURCE_GAP]

    out: list[str] = [
        "# Final gap analysis\n",
        f"Generated from `reports/latest_test_report.json` ({payload['generated_at']}) by ",
        "`traceability/build_gap_analysis.py`. Regenerate it after signing an attestation ",
        "or pushing to GitLab — the answers below change as those happen.\n",
        f"\nRequirements baseline SHA-256 `{payload['baseline_sha256']}`, "
        f"integrity **{payload['baseline_status']}**.\n",
        "\n## Where the score stands\n",
        "```",
        f"Requirements passed : {s['requirements_passed']} / {s['total_requirements']}",
        f"Requirements failed : {s['requirements_failed']}",
        f"Overall fit         : {s['overall_fit_pct']}%",
        f"IMPLEMENTATION      : {s['mandatory_passed']}/{s['mandatory_total']}",
        f"ENGAGEMENT          : {s['engagement_passed']}/{s['engagement_total']}",
        f"OPTIONAL            : {s['optional_passed']}/{s['optional_total']}",
        "```\n",
        "\n## The nine, by what would actually close them\n",
        "| Route | Requirements | Can the team close it? |",
        "| --- | --- | --- |",
        f"| **{TEAM_ARTIFACT}** | {', '.join(f'`{r}`' for r in team) or '—'} | "
        "Yes — a truthful attestation the team signs |",
        f"| **{EXTERNAL_EVENT}** | {', '.join(f'`{r}`' for r in ext) or '—'} | "
        "No — depends on the evaluator or on the submission happening |",
        f"| **{SOURCE_GAP}** | {', '.join(f'`{r}`' for r in gap) or '—'} | "
        "No — the source document fixes no value to test against |",
        "",
        "`REQ-011` appears once here but fails two tests for two different reasons: "
        "`T02` needs the GitLab push, `T03` is a specification gap. It is routed to "
        f"**{EXTERNAL_EVENT}** because that is the part anyone can act on.\n",
    ]

    for rid in failed:
        r = reqs[rid]
        d = DISPOSITION[rid]
        tests = sorted(by_req.get(rid, []), key=lambda t: t["test_id"])
        passing = [t for t in tests if t["status"] == "PASS"]
        failing = [t for t in tests if t["status"] != "PASS"]

        out += [
            f"\n---\n\n## {rid} — fit {r['fit_score']}/100\n",
            f"* **Class:** {r['requirement_class']}",
            f"* **Category:** {r['category']}",
            f"* **Source location:** {r['source_location']}",
            f"* **Bound tests:** {', '.join(t['test_id'] for t in tests)} "
            f"({len(passing)} passing, {len(failing)} failing)",
            f"* **Route:** **{d['route']}**",
            f"* **Needs an external evaluator or event:** {'yes' if d['external'] else 'no'}",
            f"* **Untestable because the source fixes no value:** "
            f"{'yes' if d['source_gap'] else 'no'}",
            "",
            "**Source wording, verbatim**\n",
            "~~~text",
            r["exact_requirement"],
            "~~~\n",
        ]

        if passing:
            out += ["**What already passes**\n"]
            for t in passing:
                first = " ".join(_ev(t["evidence"]).split())[:230]
                out.append(f"* `{t['test_id']}` — {first}")
            out.append("")

        out += ["**Exact failing condition**\n"]
        for t in failing:
            out += ["```", _ev(t["evidence"]).strip()[:900], "```", ""]

        out += [
            f"**What would close it:** {d['closes_with']}\n",
            f"**Blocked on:** {d['blocked_on']}\n",
        ]

    out += [
        "\n---\n",
        "## What was deliberately not done\n",
        "* No attestation was signed on anyone's behalf. `attested_by` stays empty until "
        "the named person confirms.\n"
        "* No GitLab remote was invented. `REQ-011-T02` passes on any remote URL matching "
        "`/gitlab/i`, which is exactly why it has to be satisfied by a real one.\n"
        "* The internal peer-review workbook is titled as internal pre-submission "
        "preparation. It is not presented as the reviewer's report, and `REQ-012` stays "
        "open.\n"
        "* No DTI percentage and no high-value monetary boundary were hard-coded. Both "
        "come from the retrieved, versioned policy corpus at runtime; the source document "
        "states neither.\n"
        "* No validator was edited. Where a check cannot pass, it still reports FAIL.\n",
        "\n## Not the official rubric\n",
        "Every figure here comes from this repository's own 112-requirement validator. "
        "The engagement is graded on a 7-category / 100-mark Hackathon Rubric that is "
        "**not in this repository and has not been run**. Nothing above is a mark "
        "against it.\n",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    use_utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", default=str(DEFAULT_REPORT))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    path = Path(args.report)
    if not path.exists():
        print(f"ERROR: no validation report at {path}. Run runners/run_all_tests.py first.")
        return 2

    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("partial_run"):
        print("ERROR: that report is from a partial run. A full run is needed.")
        return 2

    failed = payload["summary"]["failed_requirement_ids"]
    unknown = [r for r in failed if r not in DISPOSITION]
    if unknown:
        print("UNDISPOSED FAILING REQUIREMENT(S):")
        for r in unknown:
            print(f"  - {r}")
        print("\nAdd each to DISPOSITION with its route and what would close it.")
        return 1

    closed = [r for r in DISPOSITION if r not in failed]
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(payload), encoding="utf-8")

    s = payload["summary"]
    print(f"passed={s['requirements_passed']}/{s['total_requirements']}  "
          f"fit={s['overall_fit_pct']}%")
    for route in (TEAM_ARTIFACT, EXTERNAL_EVENT, SOURCE_GAP):
        ids = [r for r in failed if DISPOSITION[r]["route"] == route]
        print(f"  {route:<26} {len(ids)}  {', '.join(ids) or '-'}")
    if closed:
        print(f"\nNow passing (were in DISPOSITION): {', '.join(closed)}")
    print(f"\nWritten: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
