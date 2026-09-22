"""Render the human-facing attestation checklist from the attestation record.

``manual_attestations.json`` is the machine-readable record the validator grades
against. This turns it into something a person can actually work from: for each
unsigned statement, what would have to be true, who is in a position to say so,
and when they could truthfully say it.

Generated rather than hand-written for one reason: the status column has to be
live. Somebody signs an entry, re-runs this, and the checklist says SIGNED. A
hand-maintained list would keep saying UNSIGNED until someone remembered to edit
it, and a stale checklist is worse than none — it is the thing people trust.

Nothing here fills anything in. The script refuses to treat a partly-completed
entry as signed, and says which field is missing.

Usage
-----
    python manual_evidence/build_checklist.py
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

ATTESTATIONS = SUITE_ROOT / "manual_evidence" / "manual_attestations.json"
DEFAULT_OUT = SUITE_ROOT / "manual_evidence" / "ATTESTATION_CHECKLIST.md"

SIGNED = "SIGNED"
UNSIGNED = "UNSIGNED"
PARTIAL = "PARTIALLY FILLED - counts as UNSIGNED"
UNSIGNABLE = "CANNOT BE SIGNED (source fixes no value)"

#: Who is in a position to know, and the earliest moment the statement could be
#: made truthfully. Neither is in the JSON, because neither is a fact about the
#: repository — they are facts about the engagement.
WHO_AND_WHEN: dict[str, tuple[str, str]] = {
    "REQ-008-T01": (
        "A member of the delivery team.",
        "Any time after the work has stopped. The elapsed window is knowable now; "
        "the effort inside it is only knowable by the people who did it.",
    ),
    "REQ-009-T01": (
        "A member of the delivery team.",
        "Now. The team size is already known — it simply is not written anywhere a "
        "validator can read, and the git history shows committers rather than "
        "members.",
    ),
    "REQ-010-T02": (
        "The reviewer who ran the evaluation, or the submitter if they were told "
        "how it would be run.",
        "After the review has been conducted. Not before: how a review was carried "
        "out is not something the submitting team can assert on the reviewer's "
        "behalf.",
    ),
    "REQ-012-T01": (
        "The reviewer who produces the report.",
        "After the per-team Excel report exists and has been seen. Claiming it "
        "before then would be attesting to an event that has not happened.",
    ),
    "REQ-013-T01": (
        "The evaluator who awards the grade.",
        "After a grade has been issued. The bands are stated in the source; whether "
        "they were the ones applied is only knowable from the returned scorecard.",
    ),
}


def load() -> dict:
    return json.loads(ATTESTATIONS.read_text(encoding="utf-8"))


def status_of(entry: dict) -> tuple[str, list[str]]:
    """The entry's status, and which fields are still missing."""
    if entry.get("unspecified_by_requirement"):
        return UNSIGNABLE, []
    missing = [f for f in ("evidence", "attested_by", "attested_on")
               if not str(entry.get(f) or "").strip()]
    if not missing:
        return SIGNED, []
    if len(missing) == 3:
        return UNSIGNED, missing
    return PARTIAL, missing


def render(payload: dict) -> str:
    entries = payload["attestations"]
    rows = [(tid, e, *status_of(e)) for tid, e in sorted(entries.items())]

    signable = [r for r in rows if r[2] != UNSIGNABLE]
    unsignable = [r for r in rows if r[2] == UNSIGNABLE]
    signed = [r for r in signable if r[2] == SIGNED]

    out: list[str] = [
        "# Attestation checklist\n",
        "Generated from `manual_attestations.json` by `manual_evidence/build_checklist.py`. ",
        "Re-run it after signing anything.\n",
        "\n## Where this stands\n",
        "```",
        f"Statements needing a human signature : {len(signable)}",
        f"  signed                             : {len(signed)}",
        f"  still unsigned                     : {len(signable) - len(signed)}",
        f"Statements that cannot be signed     : {len(unsignable)}",
        "```\n",
        "\nEvery unsigned statement below is a **FAIL** in the validation report, and ",
        "that is the correct outcome. The brief is explicit that no evidence is never ",
        "a pass, and an attestation is worth exactly as much as the care taken before ",
        "signing it.\n",
        "\n> **Do not sign an event that has not happened.** Two of these — the Excel ",
        "> review report and the grade — are produced by the reviewer, not by the ",
        "> delivery team. They cannot be truthfully signed by us at all, whatever the ",
        "> effect on the score.\n",
        "\n## Summary\n",
        "| Requirement | Test | Statement | Who signs | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for tid, entry, state, _missing in signable:
        who = WHO_AND_WHEN.get(tid, ("—", "—"))[0]
        out.append(
            f"| `{entry['requirement_id']}` | `{tid}` | "
            f"{entry.get('what_must_be_attested', '—')} | {who} | **{state}** |"
        )

    out += ["\n\n## Each statement in full\n"]
    for tid, entry, state, missing in signable:
        who, when = WHO_AND_WHEN.get(tid, ("—", "—"))
        out += [
            f"\n### `{entry['requirement_id']}` — `{tid}`\n",
            f"**Status: {state}**\n",
            f"* **Source location:** {entry.get('source_location', '—')}",
            "",
            "**Exact statement that must be true**\n",
            f"> {entry.get('what_must_be_attested', '—')}\n",
            "**Source text it comes from**\n",
            "~~~text",
            str(entry.get("source_text", "—")),
            "~~~\n",
            "**What evidence would support it**\n",
            f"{entry.get('what_would_count_as_evidence', '—')}\n",
        ]
        if entry.get("where_to_look"):
            out += ["**Where to look**\n", "```", str(entry["where_to_look"]), "```\n"]
        out += [
            f"**Who should attest:** {who}\n",
            f"**When it can truthfully be attested:** {when}\n",
        ]
        if state == SIGNED:
            out += [
                "**Attested**\n",
                f"* by: {entry.get('attested_by')}",
                f"* on: {entry.get('attested_on')}",
                f"* evidence: {entry.get('evidence')}\n",
            ]
        else:
            out += [
                f"**Still missing:** {', '.join(f'`{m}`' for m in missing)}\n",
                "To sign, fill all three fields in `manual_attestations.json` and re-run "
                "this script. An entry with one field left blank does not count.\n",
            ]

    out += [
        "\n\n## Statements that cannot be signed at all\n",
        "These are not waiting on anybody. The source document fixes no value to "
        "verify against, so there is nothing a signature could be about. They are "
        "reported as specification gaps in "
        "`reports/unverifiable_requirements.md`, and the checks are written never to "
        "pass.\n",
        "| Requirement | Test | Statement |",
        "| --- | --- | --- |",
    ]
    for tid, entry, _state, _missing in unsignable:
        out.append(
            f"| `{entry['requirement_id']}` | `{tid}` | "
            f"{entry.get('what_must_be_attested', '—')} |"
        )

    out += [
        "\n\n---\n",
        "## How to sign\n",
        "Open `manual_attestations.json` and fill in, for the entry concerned:\n",
        "```",
        '  "evidence":    "what you are relying on, concretely — not \\"yes\\"",',
        '  "attested_by": "your name",',
        '  "attested_on": "2026-09-22"',
        "```\n",
        "Then re-run this script and the validator. Attest only to what you know: a "
        "truthful FAIL is worth more than a pass nobody can stand behind.\n",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    use_utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    if not ATTESTATIONS.exists():
        print(f"ERROR: no attestation record at {ATTESTATIONS}")
        return 2

    payload = load()
    out_path = Path(args.out)
    out_path.write_text(render(payload), encoding="utf-8")

    rows = [(tid, *status_of(e)) for tid, e in sorted(payload["attestations"].items())]
    for tid, state, missing in rows:
        note = f" (missing: {', '.join(missing)})" if missing and state != UNSIGNED else ""
        print(f"  {tid:<14} {state}{note}")
    print(f"\nWritten: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
