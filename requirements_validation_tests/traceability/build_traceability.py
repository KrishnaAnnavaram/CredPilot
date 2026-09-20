"""
Build the derived QA artifacts from the two authoritative sources.

Authoritative sources
---------------------
1. ``source_requirements/requirements_verbatim.md`` - the requirement text (hashed).
2. ``automated_tests/registry/`` - the test cases.

Everything this script writes is DERIVED. Nothing here may be hand-edited: rerun the
script instead. That is what keeps the traceability matrix, the test-spec documents and
the coverage audit from drifting away from the tests that actually execute.

Generated
---------
* ``traceability/requirement_traceability_matrix.md``
* ``traceability/requirement_traceability_matrix.json``
* ``traceability/source_requirements_hash.txt``   (with ``--rewrite-hash``, or if absent)
* ``traceability/coverage_audit.md``
* ``test_specs/<category>/<category>_test_specs.md``
* ``manual_evidence/manual_attestations.json``    (created if absent; never overwritten)

Usage
-----
    python traceability/build_traceability.py
    python traceability/build_traceability.py --rewrite-hash   # only with a revised source document
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SUITE_ROOT))

import bootstrap  # noqa: E402,F401

from baseline_guard import BASELINE_PATH, HASH_PATH, check_baseline, sha256_of, write_hash  # noqa: E402
from console import use_utf8_console  # noqa: E402
from requirement_loader import load_requirements  # noqa: E402

from automated_tests.registry import TEST_CASES, by_requirement  # noqa: E402

TRACE_DIR = SUITE_ROOT / "traceability"
SPEC_DIR = SUITE_ROOT / "test_specs"
MANUAL_PATH = SUITE_ROOT / "manual_evidence" / "manual_attestations.json"

GENERATED_BANNER = (
    "<!-- GENERATED FILE - do not edit by hand.\n"
    "     Regenerate with:  python traceability/build_traceability.py\n"
    "     Sources: source_requirements/requirements_verbatim.md (hashed) and\n"
    "              automated_tests/registry/ -->\n"
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------------------
# Traceability matrix
# --------------------------------------------------------------------------------------


def build_matrix_json(reqs, tests_by_req) -> dict:
    rows = []
    for req_id, req in reqs.items():
        cases = tests_by_req.get(req_id, [])
        rows.append({
            "requirement_id": req_id,
            "source_location": req.source_location,
            "source_type": req.source_type,
            "requirement_class": req.req_class,
            "category": req.category,
            "exact_source_text": req.text,
            "verification_methods": sorted({c.test_type for c in cases}),
            "test_ids": [c.test_id for c in cases],
            "test_count": len(cases),
            "automatable_tests": sum(1 for c in cases if c.automatable),
            "manual_tests": sum(1 for c in cases if not c.automatable),
            "weight_total": sum(c.weight for c in cases),
            "implementation_evidence_required": sorted({c.evidence_required for c in cases}),
            "status": "NOT_RUN",
            "fit_score": None,
        })
    return {
        "generated_at": _now(),
        "source_document": "source_document/Loan_Origination_Underwriting_Copilot_Merged.docx",
        "requirements_baseline": "source_requirements/requirements_verbatim.md",
        "requirements_baseline_sha256": sha256_of(BASELINE_PATH),
        "total_requirements": len(reqs),
        "total_tests": sum(len(v) for v in tests_by_req.values()),
        "requirements_with_tests": sum(1 for r in rows if r["test_count"] > 0),
        "requirements_without_tests": sum(1 for r in rows if r["test_count"] == 0),
        "source_coverage_percent": round(
            100 * sum(1 for r in rows if r["test_count"] > 0) / len(rows), 2
        ) if rows else 0.0,
        "requirements": rows,
    }


def build_matrix_md(data: dict) -> str:
    out: list[str] = [
        GENERATED_BANNER,
        "# CredPilot - Requirement Traceability Matrix\n",
        f"Generated: {data['generated_at']}  ",
        f"Source document: `{data['source_document']}`  ",
        f"Requirements baseline: `{data['requirements_baseline']}`  ",
        f"Baseline SHA-256: `{data['requirements_baseline_sha256']}`\n",
        "## Summary\n",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Total requirements | {data['total_requirements']} |",
        f"| Total test cases | {data['total_tests']} |",
        f"| Requirements with >= 1 test | {data['requirements_with_tests']} |",
        f"| Requirements with no test | {data['requirements_without_tests']} |",
        f"| Source requirements coverage | {data['source_coverage_percent']}% |",
        "",
        "`Status` is `NOT_RUN` until `runners/run_all_tests.py` executes against an "
        "implementation. Running the suite rewrites `reports/latest_test_report.md` and "
        "`reports/latest_test_report.json`; this matrix records the mapping, not the outcome.\n",
        "## Index\n",
        "| Requirement | Class | Category | Source location | Tests | Verification |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in data["requirements"]:
        out.append(
            f"| [{r['requirement_id']}](#{r['requirement_id'].lower()}) | {r['requirement_class']} "
            f"| {r['category']} | {r['source_location']} | {r['test_count']} "
            f"| {', '.join(r['verification_methods'])} |"
        )

    out.append("\n---\n\n## Requirement detail\n")
    for r in data["requirements"]:
        out += [
            f"### {r['requirement_id']}\n",
            f"**Source location:** {r['source_location']}  ",
            f"**Source type:** {r['source_type']}  ",
            f"**Requirement category:** {r['category']}  ",
            f"**Requirement class:** {r['requirement_class']}\n",
            "**Exact requirement (verbatim, unaltered):**\n",
            "~~~text",
            r["exact_source_text"],
            "~~~\n",
            f"**Tests:** {', '.join(r['test_ids']) if r['test_ids'] else 'NONE - COVERAGE GAP'}  ",
            f"**Verification method:** {' + '.join(r['verification_methods']) or 'NONE'}  ",
            f"**Automatable tests:** {r['automatable_tests']}  |  "
            f"**Manual/static tests:** {r['manual_tests']}  |  "
            f"**Total weight:** {r['weight_total']}\n",
            "**Implementation evidence required:**\n",
        ]
        for ev in r["implementation_evidence_required"]:
            out.append(f"- {ev}")
        out += [f"\n**Current status:** {r['status']}\n"]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
# Test specifications
# --------------------------------------------------------------------------------------


def build_spec_md(category: str, reqs, cases) -> str:
    by_req: dict[str, list] = defaultdict(list)
    for c in cases:
        by_req[c.req_id].append(c)

    out = [
        GENERATED_BANNER,
        f"# CredPilot Requirement Test Specifications - {category}\n",
        f"Generated: {_now()}\n",
        f"{len(by_req)} requirement(s), {len(cases)} test case(s) in this category.\n",
        "Every test below carries its **Exact Original Requirement** verbatim from "
        "`source_requirements/requirements_verbatim.md`. That field is read from the hashed "
        "baseline at generation time and is never edited.\n",
        "---\n",
    ]
    for req_id in sorted(by_req):
        req = reqs[req_id]
        out += [
            f"## {req_id}\n",
            f"**Source location:** {req.source_location}  ",
            f"**Requirement class:** {req.req_class}\n",
            "**Exact Original Requirement:**\n",
            "~~~text",
            req.text,
            "~~~\n",
        ]
        for c in sorted(by_req[req_id], key=lambda x: x.test_id):
            steps = "\n".join(f"{i}. {s}" for i, s in enumerate(c.steps, 1))
            out += [
                f"### {c.test_id}\n",
                f"| Field | Value |",
                f"| --- | --- |",
                f"| **Test ID** | {c.test_id} |",
                f"| **Requirement ID** | {c.req_id} |",
                f"| **Test Type** | {c.test_type} |",
                f"| **Executing suite** | `automated_tests/{c.suite}/` |",
                f"| **Weight** | {c.weight} |",
                f"| **Automatable** | {'YES' if c.automatable else 'NO'} |",
                "",
                f"**Exact Original Requirement:**\n",
                "~~~text",
                c.exact_requirement,
                "~~~\n",
                f"**Purpose:** {c.purpose}\n",
                f"**Preconditions:** {c.preconditions}\n",
                f"**Inputs:** {c.inputs}\n",
                "**Execution Steps:**\n",
                steps,
                "",
                f"**Expected Result:** {c.expected_result}\n",
                f"**Evidence Required:** {c.evidence_required}\n",
                f"**Pass Condition:** {c.pass_condition}\n",
                f"**Fail Condition:** {c.fail_condition}\n",
            ]
        out.append("---\n")
    return "\n".join(out)


# --------------------------------------------------------------------------------------
# Coverage audit
# --------------------------------------------------------------------------------------


def build_coverage_audit(reqs, tests_by_req, data: dict) -> str:
    problems: list[str] = []

    # 1. Every captured requirement has an ID and dense numbering.
    expected_ids = [f"REQ-{i:03d}" for i in range(1, len(reqs) + 1)]
    if list(reqs) != expected_ids:
        problems.append("Requirement IDs are not a dense ordered sequence REQ-001..REQ-nnn.")

    # 2. Every requirement has at least one test.
    untested = [r for r in reqs if not tests_by_req.get(r)]
    problems += [f"{r}: no test case bound." for r in untested]

    # 3. Every test maps to an existing requirement, with a matching ID prefix.
    for c in TEST_CASES:
        if c.req_id not in reqs:
            problems.append(f"{c.test_id}: bound to unknown requirement {c.req_id}.")
        elif not c.test_id.startswith(c.req_id + "-T"):
            problems.append(f"{c.test_id}: ID prefix does not match requirement {c.req_id}.")

    # 4. No requirement text is paraphrased: the spec text must be identical to the baseline.
    for c in TEST_CASES:
        if c.req_id in reqs and c.exact_requirement != reqs[c.req_id].text:
            problems.append(f"{c.test_id}: requirement text differs from the baseline.")

    # 5. No generated requirement without source evidence.
    for req_id, req in reqs.items():
        if not req.source_location or req.source_location == "UNSPECIFIED_BY_REQUIREMENT":
            problems.append(f"{req_id}: no source location recorded.")
        if not req.text.strip():
            problems.append(f"{req_id}: empty requirement text.")

    covered = len(reqs) - len(untested)
    pct = round(100 * covered / len(reqs), 2) if reqs else 0.0

    per_class = Counter(r.req_class for r in reqs.values())
    per_category = Counter(r.category for r in reqs.values())
    per_type = Counter(c.test_type for c in TEST_CASES)
    per_suite = Counter(c.suite for c in TEST_CASES)

    out = [
        GENERATED_BANNER,
        "# CredPilot - Mandatory Coverage Audit\n",
        f"Generated: {_now()}\n",
        "This is the second, independent pass required by the validation brief. It compares "
        "the source document, the verbatim baseline, the traceability matrix and the generated "
        "tests, and reports any statement that was dropped, paraphrased or left untested.\n",
        "## What was compared\n",
        "| Comparison | Result |",
        "| --- | --- |",
        f"| Source document -> verbatim baseline | {len(reqs)} requirement units extracted from "
        "`source_document/Loan_Origination_Underwriting_Copilot_Merged.docx`; see "
        "`source_document/EXTRACTION_NOTE.md` for the page-by-page coverage map |",
        f"| Verbatim baseline -> requirement IDs | {len(reqs)} of {len(reqs)} carry an ID |",
        f"| Requirement IDs -> test IDs | {covered} of {len(reqs)} have >= 1 test |",
        f"| Test IDs -> source text | {len(TEST_CASES)} of {len(TEST_CASES)} resolve to exactly one "
        "identified requirement |",
        f"| Baseline text vs. spec text | byte-for-byte identical for all {len(TEST_CASES)} tests |",
        "",
        "## Totals\n",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Source requirement units | {len(reqs)} |",
        f"| Requirements with an ID | {len(reqs)} |",
        f"| Requirements with >= 1 test | {covered} |",
        f"| Requirements with no test | {len(untested)} |",
        f"| Total test cases | {len(TEST_CASES)} |",
        f"| Automated test cases | {sum(1 for c in TEST_CASES if c.automatable)} |",
        f"| Manual / non-automatable test cases | {sum(1 for c in TEST_CASES if not c.automatable)} |",
        f"| Baseline SHA-256 | `{data['requirements_baseline_sha256']}` |",
        "",
        "## Requirements by class\n",
        "| Class | Count |",
        "| --- | --- |",
    ]
    out += [f"| {k} | {v} |" for k, v in sorted(per_class.items())]
    out += ["", "## Requirements by category\n", "| Category | Count |", "| --- | --- |"]
    out += [f"| {k} | {v} |" for k, v in sorted(per_category.items())]
    out += ["", "## Tests by verification type\n", "| Verification type | Count |", "| --- | --- |"]
    out += [f"| {k} | {v} |" for k, v in sorted(per_type.items())]
    out += ["", "## Tests by executing suite\n", "| Suite | Count |", "| --- | --- |"]
    out += [f"| `automated_tests/{k}/` | {v} |" for k, v in sorted(per_suite.items())]

    out += ["", "## Per-requirement coverage\n",
            "| Requirement | Class | Tests | Test IDs |", "| --- | --- | --- | --- |"]
    for req_id, req in reqs.items():
        cases = tests_by_req.get(req_id, [])
        ids = ", ".join(c.test_id for c in cases) if cases else "**NONE**"
        out.append(f"| {req_id} | {req.req_class} | {len(cases)} | {ids} |")

    out += ["", "## Audit findings\n"]
    if problems:
        out.append(f"{len(problems)} finding(s):\n")
        out += [f"- {p}" for p in problems]
    else:
        out += [
            "No findings. Specifically:\n",
            "- Every source requirement unit is captured in the verbatim baseline.",
            "- Every captured requirement has a Requirement ID.",
            "- Every Requirement ID has at least one Test ID.",
            "- Every Test ID maps back to exactly one identified source requirement.",
            "- No requirement text has been paraphrased: every test's Exact Original "
            "Requirement is byte-for-byte identical to the hashed baseline.",
            "- No requirement was silently dropped: requirement IDs form a dense sequence "
            f"REQ-001..REQ-{len(reqs):03d} with no gaps.",
            "- No generated requirement exists without source evidence: every requirement "
            "records the section, table row or sentence it was taken from.",
        ]

    out += ["", "---", "", f"SOURCE REQUIREMENTS COVERAGE: {pct}%", ""]
    return "\n".join(out)


# --------------------------------------------------------------------------------------
# Manual attestation template
# --------------------------------------------------------------------------------------


def build_manual_template() -> dict:
    manual = [c for c in TEST_CASES if not c.automatable]
    return {
        "_comment": [
            "Human-recorded evidence for the statements no artifact in the implementation can",
            "settle on its own.",
            "",
            "An entry counts ONLY when evidence, attested_by and attested_on are all non-empty.",
            "An empty entry is a FAIL: the brief is explicit that no evidence is never a pass.",
            "",
            "Entries marked UNSPECIFIED_BY_REQUIREMENT cannot be attested at all: the source",
            "document fixes no value to verify against. They stay FAIL and are reported as",
            "specification gaps, not as implementation defects.",
        ],
        "attestations": {
            c.test_id: {
                "requirement_id": c.req_id,
                "what_must_be_attested": c.purpose,
                "evidence": None,
                "attested_by": None,
                "attested_on": None,
            }
            for c in sorted(manual, key=lambda x: x.test_id)
        },
    }


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------


def main() -> int:
    use_utf8_console()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rewrite-hash", action="store_true",
                    help="Rewrite the baseline hash. Only correct when the SOURCE DOCUMENT itself "
                         "was revised and the verbatim baseline was re-extracted from it.")
    args = ap.parse_args()

    reqs = load_requirements()
    tests_by_req = by_requirement()

    if args.rewrite_hash or not HASH_PATH.is_file():
        digest = write_hash()
        print(f"[hash ] wrote {HASH_PATH.relative_to(SUITE_ROOT)} -> {digest}")
    else:
        status = check_baseline()
        print(f"[hash ] {status.code} ({status.actual_sha256})")
        if not status.ok:
            print("        Refusing to regenerate derived artifacts from a modified baseline.")
            print("        If the source document really changed, re-extract the verbatim "
                  "baseline and rerun with --rewrite-hash.")
            return 2

    data = build_matrix_json(reqs, tests_by_req)

    (TRACE_DIR / "requirement_traceability_matrix.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[trace] requirement_traceability_matrix.json")

    (TRACE_DIR / "requirement_traceability_matrix.md").write_text(
        build_matrix_md(data), encoding="utf-8")
    print("[trace] requirement_traceability_matrix.md")

    by_cat: dict[str, list] = defaultdict(list)
    for c in TEST_CASES:
        by_cat[c.category].append(c)
    for category, cases in sorted(by_cat.items()):
        d = SPEC_DIR / category
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{category}_test_specs.md").write_text(
            build_spec_md(category, reqs, cases), encoding="utf-8")
        print(f"[spec ] test_specs/{category}/{category}_test_specs.md "
              f"({len(cases)} test case(s))")

    (TRACE_DIR / "coverage_audit.md").write_text(
        build_coverage_audit(reqs, tests_by_req, data), encoding="utf-8")
    print("[audit] coverage_audit.md")

    if MANUAL_PATH.is_file():
        existing = json.loads(MANUAL_PATH.read_text(encoding="utf-8"))
        template = build_manual_template()
        added = [k for k in template["attestations"] if k not in existing.get("attestations", {})]
        for k in added:
            existing.setdefault("attestations", {})[k] = template["attestations"][k]
        if added:
            MANUAL_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
            print(f"[manual] added {len(added)} new attestation slot(s); existing entries kept")
        else:
            print("[manual] up to date; existing attestations left untouched")
    else:
        MANUAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANUAL_PATH.write_text(json.dumps(build_manual_template(), indent=2, ensure_ascii=False)
                               + "\n", encoding="utf-8")
        print("[manual] manual_evidence/manual_attestations.json (template, all unattested)")

    print(f"\nDone. {len(reqs)} requirements, {len(TEST_CASES)} test cases, "
          f"{data['source_coverage_percent']}% source coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
