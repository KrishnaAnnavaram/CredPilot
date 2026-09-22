"""Classify every failing requirement-validation test, and reconcile the arithmetic.

The validation report says *what* failed. It does not say *why the failure is the
shape it is*, and that distinction is the whole point: a missing library is a
defect this repository can fix, while the identity of an externally assigned
GitLab project is not, and neither is a threshold the source document never
states. Reporting all three as "11 remaining" invites someone to close the gap by
editing a validator.

Four classes, defined once here and used by every downstream document:

``REAL_IMPLEMENTATION_GAP``
    The source fixes a concrete requirement and the repository does not meet it.
    Fixable in code, and therefore must be fixed in code.

``MANUAL_ATTESTATION_REQUIRED``
    The truth is a fact about a human or an event — how long the team worked, who
    reviewed the submission — that no artifact in the repository can establish.
    Left blank until someone who knows signs it.

``EXTERNAL_SUBMISSION_DEPENDENCY``
    The truth depends on a system outside this repository, such as the assigned
    Virtusa GitLab project. Not satisfiable by anything committed here.

``UNSPECIFIED_BY_REQUIREMENT``
    The source asks for something but supplies no value to test against — "flags
    any policy breach with the threshold it failed", with no threshold anywhere in
    the document. A specification gap, recorded rather than guessed.

Two invariants are asserted, and the script exits non-zero if either breaks:

1. ``passed + failed == total``, and every failing ID appears exactly once;
2. every failing test has a classification here.

The second matters more than it looks. A new failure that nobody has classified
would otherwise be absorbed silently into whichever bucket a reader assumed, and
the bucket totals would still add up. Here it stops the script instead.

Usage
-----
    python traceability/classify_failures.py
    python traceability/classify_failures.py --report path/to/report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SUITE_ROOT))

import bootstrap  # noqa: E402,F401

from console import use_utf8_console  # noqa: E402

REAL = "REAL_IMPLEMENTATION_GAP"
MANUAL = "MANUAL_ATTESTATION_REQUIRED"
EXTERNAL = "EXTERNAL_SUBMISSION_DEPENDENCY"
UNSPECIFIED = "UNSPECIFIED_BY_REQUIREMENT"

CLASS_ORDER = (REAL, MANUAL, EXTERNAL, UNSPECIFIED)


class Verdict:
    """One classified test, with the reasoning that put it in its class."""

    __slots__ = ("klass", "why", "action", "fixable")

    def __init__(self, klass: str, why: str, action: str):
        self.klass = klass
        self.why = why
        self.action = action
        self.fixable = klass == REAL


#: Keyed by test ID, because a requirement can fail for two different reasons at
#: once. REQ-011 is the example that forced this: its remote check is an external
#: dependency, and its cut-off check is unspecified by the source. Classifying at
#: requirement level would have to pick one, and the count would then double-count
#: REQ-011 across two buckets — which is exactly the arithmetic error this script
#: exists to prevent.
CLASSIFICATION: dict[str, Verdict] = {
    # -- engagement facts no artifact can establish -----------------------------
    "REQ-008-T01": Verdict(
        MANUAL,
        "The source fixes the engagement duration at 20 hours. How long the team "
        "actually worked is an event fact; no file in the repository records it, and "
        "commit timestamps measure elapsed wall-clock, not effort.",
        "Leave the attestation blank until a team member signs it.",
    ),
    "REQ-009-T01": Verdict(
        MANUAL,
        "The source fixes the team size at 2-4. Repository authorship shows who "
        "committed, not who was on the team, and a single-committer history is "
        "consistent with several team sizes.",
        "Leave the attestation blank until a team member signs it.",
    ),
    "REQ-010-T02": Verdict(
        MANUAL,
        "The evaluator runs the 7-category / 100-mark Hackathon Rubric. That rubric "
        "is not in this repository, so nothing here can show it was applied or what "
        "it scored.",
        "Leave blank. Only the reviewer who ran the rubric can attest to it.",
    ),
    "REQ-012-T01": Verdict(
        MANUAL,
        "The per-team Excel review report is produced by the reviewer, not by the "
        "team. Claiming it exists before the reviewer has produced it would be a "
        "fabricated attestation.",
        "Leave blank until the reviewer produces the report.",
    ),
    "REQ-013-T01": Verdict(
        MANUAL,
        "Grade bands (Pass >= 60) are applied by the evaluator against the rubric. "
        "The repository holds neither the rubric nor the awarded grade.",
        "Leave blank until the evaluator issues a grade.",
    ),
    # -- external systems -------------------------------------------------------
    "REQ-011-T02": Verdict(
        EXTERNAL,
        "The check requires a git remote pointing at the assigned Virtusa GitLab "
        "project. No such remote is configured, and the assigned URL was never "
        "supplied to this repository. Adding a plausible-looking GitLab URL would "
        "make the check pass while pushing nowhere real.",
        "Record as an external dependency. Add the real remote at submission time "
        "using docs/FINAL_SUBMISSION.md; do not invent a URL.",
    ),
    # -- the source supplies no value to test against ---------------------------
    "REQ-011-T03": Verdict(
        UNSPECIFIED,
        "The source says to push 'by the cut-off' and names 'your assigned Virtusa "
        "GitLab project', but states neither the cut-off date and time nor the "
        "project identity anywhere in the document.",
        "Report as a specification gap. A human supplies both values at submission.",
    ),
    "REQ-035-T03": Verdict(
        UNSPECIFIED,
        "The source names LangGraph's licence as MIT in a stack table. It does not "
        "say the implementation must carry any licence artifact, nor name one, so "
        "there is no artifact to check for.",
        "Report as a specification gap. LangGraph's MIT licence is a fact about the "
        "dependency, not an obligation the source places on this repository.",
    ),
    "REQ-045-T04": Verdict(
        UNSPECIFIED,
        "AC-02 requires affordability breaches to be flagged 'with the threshold it "
        "failed'. The source never states a DTI or disposable-income number, so "
        "there is no value against which to verify the one the implementation uses.",
        "Report as a specification gap. The implementation's thresholds come from "
        "its own committed policy corpus, which is the auditable substitute.",
    ),
    "REQ-046-T07": Verdict(
        UNSPECIFIED,
        "AC-03 routes a 'high-value case' for human review. The source never fixes "
        "the monetary boundary at which a case becomes high-value.",
        "Report as a specification gap. The implementation's boundary is set in its "
        "committed review-trigger rules.",
    ),
    # -- genuine implementation gaps --------------------------------------------
    "REQ-038-T02": Verdict(
        REAL,
        "The source's Memory row names 'langgraph-checkpoint-sqlite (SQLite file) + "
        "LangMem'. The checkpointer is present; LangMem was neither declared nor "
        "used.",
        "Integrate LangMem over a LangGraph store, declare it, and prove "
        "cross-session recall and subject isolation with tests.",
    ),
    "REQ-042-T01": Verdict(
        REAL,
        "The source's Security row names 'Guardrails-AI / LLM Guard' alongside "
        "Presidio. Presidio and a custom guardrail layer are present; neither named "
        "library was.",
        "Integrate Guardrails-AI into the live input and output paths, keeping the "
        "existing Presidio and custom controls.",
    ),
}

#: What a human has to supply, per unspecified requirement, and how the absence of
#: a value in the source is *shown* rather than asserted.
#:
#: Each probe is a regex run over the hash-locked verbatim source at report time.
#: Claiming "the document fixes no threshold" and leaving it there is exactly the
#: kind of assertion this project refuses to accept from an implementation, so it
#: does not make it about itself either: the report prints the match count, and a
#: probe that starts matching is a probe that has to be re-read.
SOURCE_PROBES: dict[str, list[tuple[str, str]]] = {
    "REQ-011-T03": [
        ("any date or time offered as the cut-off",
         r"cut-?off[^\n]{0,80}?\d|\d{1,2}\s*(?:am|pm)\b|\d{4}-\d{2}-\d{2}"),
        ("any GitLab URL or project path", r"gitlab[^\n]{0,40}?[/.]"),
    ],
    "REQ-035-T03": [
        ("any obligation to carry a licence file",
         r"licen[cs]e[^\n]{0,60}?(?:file|artifact|copy|include|commit)"),
    ],
    "REQ-045-T04": [
        ("any percentage anywhere in the document", r"\d+\s*%"),
        ("any stated DTI or disposable-income figure",
         r"(?:dti|disposable[^\n]{0,20}income)[^\n]{0,40}?\d"),
    ],
    "REQ-046-T07": [
        ("any monetary amount offered as the high-value boundary",
         r"high[- ]value[^\n]{0,60}?\d|(?:above|over|exceed\w*)\s*[\u00a3$\u20ac]?\s*[\d,]{4,}"),
    ],
}

#: What a reader should do with each gap. Not a threshold, and not a guess at one:
#: a statement of who decides and against what.
RECOMMENDED_INTERPRETATION: dict[str, str] = {
    "REQ-011-T03": (
        "Treat as satisfied when the submitting team pushes to the project they "
        "were assigned, before the cut-off they were given. Both values live in "
        "the engagement brief, not in this document, and neither can be checked "
        "from the repository. docs/FINAL_SUBMISSION.md holds the commands."
    ),
    "REQ-035-T03": (
        "Treat as satisfied by LangGraph being MIT-licensed, which it is. The "
        "source names the licence as a property of the dependency in a stack "
        "table; it places no obligation on this repository to carry a licence "
        "artifact, so there is nothing here to inspect. If the evaluator expects "
        "one, a THIRD_PARTY_LICENCES.md would satisfy it - but inventing that "
        "obligation and then meeting it would be marking our own homework."
    ),
    "REQ-045-T04": (
        "Read AC-02 as requiring the implementation to name the threshold it "
        "applied, not to match a number the source never gives. CredPilot's "
        "thresholds come from its committed policy corpus with an effective date, "
        "and every breach cites the rule it failed - which is auditable in a way "
        "a hard-coded constant would not be."
    ),
    "REQ-046-T07": (
        "Read AC-03 as requiring a high-value boundary that is explicit, "
        "committed and applied consistently - not one that matches an unstated "
        "figure. CredPilot's boundary lives in its committed review-trigger rules."
    ),
}


#: Failures whose cause is a stale or uncommitted artifact rather than missing
#: behaviour. Classified REAL because committing the artifact fixes them, but kept
#: apart in the report so they are not mistaken for missing features.
EVIDENCE_GAP_TESTS = {
    "REQ-051-T02", "REQ-054-T05", "REQ-070-T02", "REQ-071-T02",
    "REQ-073-T04", "REQ-086-T03", "REQ-088-T03", "REQ-106-T02",
}

for _tid in sorted(EVIDENCE_GAP_TESTS):
    CLASSIFICATION.setdefault(
        _tid,
        Verdict(
            REAL,
            "An evidence artifact the check reads is missing, empty, or present in "
            "the working tree but not committed. The Citation-Resolves and "
            "Evidence-in-Repo rules treat an uncommitted artifact as absent.",
            "Regenerate the artifact from committed code and commit it.",
        ),
    )


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def reconcile(payload: dict) -> list[str]:
    """Assert the report's own arithmetic. Returns a list of problems."""
    problems: list[str] = []
    s = payload["summary"]
    total = s["total_requirements"]
    passed = s["requirements_passed"]
    failed = s["requirements_failed"]

    if passed + failed != total:
        problems.append(f"passed({passed}) + failed({failed}) != total({total})")

    listed = s["failed_requirement_ids"]
    counts = Counter(listed)
    duplicated = sorted(rid for rid, n in counts.items() if n > 1)
    if duplicated:
        problems.append(f"failed IDs listed more than once: {duplicated}")
    if len(listed) != failed:
        problems.append(
            f"failed_requirement_ids has {len(listed)} entries but requirements_failed is {failed}"
        )

    graded_failed = {r["requirement_id"] for r in payload["requirements"] if r["status"] != "PASS"}
    if graded_failed != set(listed):
        problems.append(
            f"headline failed set != per-requirement failed set; "
            f"only-in-headline={sorted(set(listed) - graded_failed)}, "
            f"only-in-detail={sorted(graded_failed - set(listed))}"
        )
    return problems


def failing_tests(payload: dict) -> list[dict]:
    return [t for t in payload["tests"] if t["status"] != "PASS"]


def check_coverage(tests: list[dict]) -> list[str]:
    return [t["test_id"] for t in tests if t["test_id"] not in CLASSIFICATION]


def _case_index() -> dict:
    from automated_tests.registry import TEST_CASES

    return {c.test_id: c for c in TEST_CASES}


def _validator_name(case) -> str:
    check = getattr(case, "check", None)
    if check is None:
        return "-"
    return getattr(check, "__name__", type(check).__name__)


def _first_line(text: str, limit: int = 180) -> str:
    line = " ".join(str(text or "").split())
    return (line[: limit - 1] + "…") if len(line) > limit else line


def render(payload: dict, tests: list[dict], cases: dict) -> str:
    s = payload["summary"]
    reqs = {r["requirement_id"]: r for r in payload["requirements"]}
    by_class: dict[str, list[dict]] = {k: [] for k in CLASS_ORDER}
    for t in tests:
        by_class[CLASSIFICATION[t["test_id"]].klass].append(t)

    failed_ids = s["failed_requirement_ids"]
    out: list[str] = [
        "# Current requirement-validation failures\n",
        f"Generated from `reports/latest_test_report.json` ({payload['generated_at']}) by ",
        "`traceability/classify_failures.py`.\n",
        "\nThis document exists because the headline count and the bucket counts had ",
        "disagreed. They are reconciled below, and the script that writes this file ",
        "fails if they stop agreeing or if a new failure appears that nobody has ",
        "classified.\n",
        "\n## Arithmetic\n",
        "```",
        f"Total requirements      : {s['total_requirements']}",
        f"Requirements passed     : {s['requirements_passed']}",
        f"Requirements failed     : {s['requirements_failed']}",
        f"passed + failed == total: {s['requirements_passed'] + s['requirements_failed']} == {s['total_requirements']}",
        "",
        f"Failing tests           : {len(tests)}",
        f"Failing requirements    : {len(failed_ids)}",
        "```\n",
        "\nFailing tests outnumber failing requirements because one requirement can fail ",
        "two different checks. **REQ-011 is the case that matters**: its remote check is ",
        "an external dependency and its cut-off check is unspecified by the source. ",
        "Counting it once per bucket is what produced an apparent 12 from 11 distinct ",
        "requirements. Classification below is therefore keyed by *test*, and the ",
        "requirement totals are derived from it rather than asserted alongside it.\n",
        "\n## Counts by class\n",
        "| Class | Failing tests | Distinct requirements | Fixable in code? |",
        "| --- | --- | --- | --- |",
    ]
    for klass in CLASS_ORDER:
        rows = by_class[klass]
        if not rows:
            continue
        distinct = sorted({t["requirement_id"] for t in rows})
        out.append(
            f"| {klass} | {len(rows)} | {len(distinct)} | "
            f"{'yes' if klass == REAL else 'no'} |"
        )
    out += [
        "",
        f"Distinct failing requirement IDs: **{len(failed_ids)}** — "
        + ", ".join(f"`{r}`" for r in failed_ids)
        + "\n",
    ]

    out += [
        "\n## Every failing test\n",
        "| Test ID | Requirement | Class | Current Failure | Fixable in Code? | Correct Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for t in sorted(tests, key=lambda x: x["test_id"]):
        v = CLASSIFICATION[t["test_id"]]
        out.append(
            f"| `{t['test_id']}` | `{t['requirement_id']}` | {v.klass} | "
            f"{_first_line(t['evidence'], 150)} | {'**yes**' if v.fixable else 'no'} | "
            f"{_first_line(v.action, 150)} |"
        )

    out += ["\n\n## Detail, per failing test\n"]
    for klass in CLASS_ORDER:
        rows = sorted(by_class[klass], key=lambda x: x["test_id"])
        if not rows:
            continue
        out.append(f"\n### {klass} — {len(rows)} test(s)\n")
        for t in rows:
            v = CLASSIFICATION[t["test_id"]]
            req = reqs[t["requirement_id"]]
            case = cases.get(t["test_id"])
            out += [
                f"#### `{t['test_id']}` → `{t['requirement_id']}`\n",
                f"* **Requirement class:** {req['requirement_class']}",
                f"* **Category:** {t['category']}",
                f"* **Source location:** {req['source_location']}",
                f"* **Validator function:** `{_validator_name(case) if case else '-'}`"
                + (f" (`{case.test_type}`)" if case else ""),
                f"* **Pass condition:** {_first_line(case.pass_condition) if case else '-'}",
                "",
                "**Source requirement**\n",
                "~~~text",
                req["exact_requirement"],
                "~~~\n",
                "**Current failure**\n",
                "```",
                str(t["evidence"]).strip(),
                "```\n",
                f"**Why this class:** {v.why}\n",
                f"**Fixable in code:** {'yes' if v.fixable else 'no'}\n",
                f"**Correct action:** {v.action}\n",
            ]

    out += [
        "\n---\n",
        "## The ceiling this implies\n",
        f"Of {len(failed_ids)} failing requirements, "
        f"{len({t['requirement_id'] for t in by_class[REAL]})} fail for reasons this "
        "repository can fix. The rest depend on a human, an external system, or a "
        "value the source document never states.\n",
        "\nNo validator was edited to change any of these outcomes. Where a check "
        "cannot pass, it still reports FAIL and this document says why.\n",
    ]
    return "\n".join(out) + "\n"


VERBATIM_SOURCE = SUITE_ROOT / "source_requirements" / "requirements_verbatim.md"


def _probe_source(patterns: list[tuple[str, str]]) -> list[tuple[str, str, int]]:
    """Run each probe over the verbatim source. Returns (label, pattern, hits)."""
    import re

    try:
        text = VERBATIM_SOURCE.read_text(encoding="utf-8")
    except OSError:
        return [(label, pattern, -1) for label, pattern in patterns]
    out = []
    for label, pattern in patterns:
        try:
            hits = len(re.findall(pattern, text, re.IGNORECASE))
        except re.error:
            hits = -1
        out.append((label, pattern, hits))
    return out


def render_unverifiable(payload: dict, tests: list[dict], cases: dict) -> str:
    """The UNSPECIFIED_BY_REQUIREMENT report."""
    reqs = {r["requirement_id"]: r for r in payload["requirements"]}
    rows = sorted(
        (t for t in tests if CLASSIFICATION[t["test_id"]].klass == UNSPECIFIED),
        key=lambda x: x["test_id"],
    )

    out: list[str] = [
        "# Requirements the source document does not make verifiable\n",
        f"Generated from `reports/latest_test_report.json` ({payload['generated_at']}) by ",
        "`traceability/classify_failures.py`.\n",
        "\nEach entry below is a requirement the source *states* but supplies no value ",
        "for. The implementation cannot be checked against a number the document never ",
        "gives, so these are recorded as specification gaps and left failing.\n",
        "\n**No validator was changed to make any of these pass.** Each still returns ",
        "`Evidence(False, ...)` from `not_verifiable_from_artifact(...)` in ",
        "`validators/evidence_validator.py`, which has no branch that can return True. ",
        "Turning one green would mean claiming the source requirement had been verified ",
        "when nothing verified it.\n",
        f"\nSource of truth: `source_requirements/requirements_verbatim.md`, ",
        f"SHA-256 `{payload['baseline_sha256']}`, "
        f"integrity **{payload['baseline_status']}**.\n",
        "\n## Summary\n",
        "| Requirement | Test | Missing value | Validator |",
        "| --- | --- | --- | --- |",
    ]
    for t in rows:
        case = cases.get(t["test_id"])
        subject = _subject_of(case)
        out.append(
            f"| `{t['requirement_id']}` | `{t['test_id']}` | {subject} | "
            f"`not_verifiable_from_artifact` |"
        )

    for t in rows:
        rid, tid = t["requirement_id"], t["test_id"]
        req = reqs[rid]
        case = cases.get(tid)
        v = CLASSIFICATION[tid]
        out += [
            f"\n\n---\n\n## {rid} — {tid}\n",
            f"**Requirement class:** {req['requirement_class']}  |  "
            f"**Category:** {req['category']}  |  "
            f"**Source location:** {req['source_location']}\n",
            "### Source text, verbatim\n",
            "~~~text",
            req["exact_requirement"],
            "~~~\n",
            f"### Missing verifiable value\n\n{_subject_of(case)}\n",
            "### Why the implementation cannot prove it\n",
            f"{v.why}\n",
        ]
        probes = SOURCE_PROBES.get(tid)
        if probes:
            out += [
                "\n**Searched the source for it:**\n",
                "| Looked for | Pattern | Matches |",
                "| --- | --- | --- |",
            ]
            for label, pattern, hits in _probe_source(probes):
                shown = "error" if hits < 0 else str(hits)
                out.append(f"| {label} | `{pattern}` | **{shown}** |")
            out.append(
                "\nA match count of 0 is the evidence that the value is absent, "
                "rather than that nobody looked."
            )
        out += [
            "\n### Validator function\n",
            "```python",
            "not_verifiable_from_artifact(",
            f"    {_subject_of(case)!r}",
            ")",
            "```",
            f"\nRegistered in `{_case_module(tid)}` as `{tid}`, "
            f"test type `{case.test_type if case else '-'}`, "
            f"weight {case.weight if case else '-'}, "
            f"automatable {case.automatable if case else '-'}.\n",
            f"Pass condition as registered: *{_first_line(case.pass_condition) if case else '-'}*\n",
            "### Recommended human interpretation\n",
            f"{RECOMMENDED_INTERPRETATION.get(tid, v.action)}\n",
        ]

    out += [
        "\n---\n",
        "## What would change these\n",
        "Only the source document. If the engagement issues a threshold, a cut-off, "
        "an assigned project URL or a licence-artifact obligation, each becomes "
        "mechanically checkable and the corresponding test can be rewritten against "
        "the stated value. Until then the honest report is the one above.\n",
    ]
    return "\n".join(out) + "\n"


def _subject_of(case) -> str:
    """The 'what' passed to `not_verifiable_from_artifact`, read off the evidence."""
    if case is None:
        return "-"
    for line in (case.expected_result or "").splitlines():
        if "UNSPECIFIED_BY_REQUIREMENT for" in line:
            return line.split("for", 1)[1].strip().strip("'\"")
    return (case.purpose or "-").strip()


def _case_module(test_id: str) -> str:
    req_num = int(test_id.split("-")[1])
    if req_num <= 44:
        return "automated_tests/registry/cases_core.py"
    if req_num <= 69:
        return "automated_tests/registry/cases_acceptance.py"
    if req_num <= 100:
        return "automated_tests/registry/cases_artifacts.py"
    return "automated_tests/registry/cases_evidence.py"


def main() -> int:
    use_utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", default=str(SUITE_ROOT / "reports" / "latest_test_report.json"))
    ap.add_argument("--out", default=str(SUITE_ROOT / "reports" / "current_failures.md"))
    ap.add_argument("--unverifiable-out",
                    default=str(SUITE_ROOT / "reports" / "unverifiable_requirements.md"))
    args = ap.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: no report at {report_path}. Run runners/run_all_tests.py first.")
        return 2

    payload = load_report(report_path)
    if payload.get("partial_run"):
        print("ERROR: that report is from a partial run (--suite/--requirement).")
        print("       Classification needs a full 112-requirement run.")
        return 2

    problems = reconcile(payload)
    if problems:
        print("ARITHMETIC DOES NOT RECONCILE:")
        for p in problems:
            print(f"  - {p}")
        return 1

    tests = failing_tests(payload)
    unclassified = check_coverage(tests)
    if unclassified:
        print("UNCLASSIFIED FAILING TEST(S):")
        for t in unclassified:
            print(f"  - {t}")
        print("\nAdd each to CLASSIFICATION in this file, with the reasoning, before")
        print("any report is published. An unclassified failure is a failure nobody")
        print("has decided the meaning of.")
        return 1

    cases = _case_index()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(payload, tests, cases), encoding="utf-8")

    unverifiable_path = Path(args.unverifiable_out)
    unverifiable_path.write_text(render_unverifiable(payload, tests, cases), encoding="utf-8")

    s = payload["summary"]
    counts = Counter(CLASSIFICATION[t["test_id"]].klass for t in tests)
    req_counts = {
        k: len({t["requirement_id"] for t in tests if CLASSIFICATION[t["test_id"]].klass == k})
        for k in CLASS_ORDER
    }

    print("Arithmetic reconciles.")
    print(f"  total={s['total_requirements']}  passed={s['requirements_passed']}  "
          f"failed={s['requirements_failed']}")
    print(f"  failing tests={len(tests)}  failing requirements={len(s['failed_requirement_ids'])}")
    print("")
    for k in CLASS_ORDER:
        if counts.get(k):
            print(f"  {k:<32} tests={counts[k]:<3} distinct requirements={req_counts[k]}")
    print("")
    print(f"Written: {out_path}")
    print(f"Written: {unverifiable_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
