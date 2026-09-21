"""Re-derive the deterministic faithfulness figure after a fix to the checker.

The committed evaluation run measured `narrative_faithfulness_deterministic` with
a version of :func:`src.narrative.verify_narrative` whose supported-set had a
hole: `months_of_reserves` sits at the top level of the calculations dict rather
than inside `ratios` or `amounts`, and the representative score and every policy
floor arrive only via the rule evaluations. The check flagged the model for
quoting figures the system had computed and handed it, and reported 0.648 against
the judge's 0.984.

Re-running the evaluation is the obvious remedy and was not available — the model
quota was exhausted partway through the attempt. This script gets the answer
without one.

**Why it is sound.** The run records every figure it flagged, and the fix only
ever *widens* the supported set: a figure that is now covered was wrongly flagged,
and no figure can become newly flagged. The widened sources — the computed
figures, the rule evaluations, the review reasons — all come from retrieval, the
calculators and the rule engine, none of which involve a model, so each flagged
figure can be re-tested exactly.

**Where it is a lower bound rather than an exact answer.** The same round of fixes
also tightened the figure *pattern*, so that `mortgage-affordability-2.1` no
longer reads as a quoted `2.1`. That reasoning does not carry over: the record
keeps the flagged string but not the sentence around it, so a figure the new
pattern would no longer match cannot be identified from the record alone. Such a
case stays counted as unfaithful. The figure this script reports is therefore the
**conservative** one — the true figure is at least this high, never lower.

Runs from now on commit the narrative text with each case record, so the question
does not arise again: a future recheck can re-read the prose directly.

The result is written to ``reports/faithfulness_recheck.json`` as its own
artifact, and the report's figure is updated in place with a note recording that
it was re-derived and by what. The original measurement is kept beside it under
``narrative_faithfulness_deterministic_as_measured``, because overwriting a number
without leaving the old one visible is how a report stops being evidence.

    python scripts/recheck_faithfulness.py
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.config import REPO_ROOT  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402

REPORTS = REPO_ROOT / "reports"
EVAL_REPORT = REPORTS / "eval_report.json"
EVAL_CASES = REPORTS / "eval_cases.jsonl"
RECHECK_PATH = REPORTS / "faithfulness_recheck.json"


def _load_cases(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def recheck(cases: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Decide, per case, whether its flagged figures are still unsupported."""
    from src.application_context import build_underwriting_input
    from src.calculations import compute_affordability
    from src.domain import LendingProductDomain
    from src.narrative import _as_number, _is_percentage, _is_supported, _supported_numbers
    from src.graph import build_graph, initial_state

    flagged = [
        case for case in cases
        if case.get("narrative_faithful") is False and not case.get("error")
    ]
    print(f"{len(flagged)} case(s) were flagged unfaithful; rechecking each")

    cleared: list[dict[str, Any]] = []
    still_unfaithful: list[dict[str, Any]] = []

    graph, context = build_graph()
    try:
        for index, case in enumerate(flagged, start=1):
            product = LendingProductDomain.from_any(case["product"])
            folder = "mortgage" if product is LendingProductDomain.MORTGAGE else "education"
            packet_path = (
                REPO_ROOT / "synthetic_data" / folder / "applications"
                / f"{case['application_id']}.json"
            )

            # Deterministic only: retrieval, calculators, rule engine. No model.
            state = initial_state(packet_path, as_of_date=case.get("as_of_date"))
            final = graph.invoke(
                state,
                config={"configurable": {"thread_id": f"recheck-{case['case_id']}"}},
            )
            evidence = final.get("policy_evidence") or []
            calculations = final.get("calculations") or {}
            evaluations = (final.get("eligibility") or {}).get("evaluations") or []

            supported = _supported_numbers(
                evidence,
                calculations,
                evaluations,
                supplied_text=list(final.get("human_review_reasons") or []),
            )

            remaining: list[str] = []
            for figure in case.get("unsupported_figures") or []:
                value = _as_number(figure)
                if value is None:
                    continue
                candidates = [value]
                if _is_percentage(figure):
                    candidates.append(round(value / 100, 6))
                if not any(_is_supported(c, supported) for c in candidates):
                    remaining.append(figure)

            record = {
                "case_id": case["case_id"],
                "product": case["product"],
                "flagged_originally": case.get("unsupported_figures") or [],
                "unsupported_citations": case.get("unsupported_citations") or [],
                "still_unsupported": remaining,
            }
            # A citation that pointed nowhere is untouched by this fix.
            if remaining or record["unsupported_citations"]:
                still_unfaithful.append(record)
            else:
                cleared.append(record)

            print(
                f"  [{index:>3}/{len(flagged)}] {case['case_id']:<18} "
                f"{len(record['flagged_originally'])} flagged -> "
                f"{len(remaining)} remaining"
            )
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    return {"cleared": cleared, "still_unfaithful": still_unfaithful, "flagged": len(flagged)}


def summarize(cases: Sequence[dict[str, Any]], result: dict[str, Any]) -> dict[str, Any]:
    """Per-product and macro faithfulness after the recheck."""
    still_bad = {record["case_id"] for record in result["still_unfaithful"]}
    by_product: dict[str, list[bool]] = {}

    for case in cases:
        if case.get("error") or case.get("narrative_faithful") is None:
            continue
        faithful = case["case_id"] not in still_bad
        by_product.setdefault(case["product"], []).append(faithful)

    per_product = {
        product: round(sum(flags) / len(flags), 4)
        for product, flags in sorted(by_product.items())
        if flags
    }
    macro = round(statistics.fmean(per_product.values()), 4) if per_product else None
    return {"per_product": per_product, "macro": macro}


def _apply_to_cases(
    cases: Sequence[dict[str, Any]],
    result: dict[str, Any],
    path: Path,
) -> None:
    """Write the corrected verdict onto each case, keeping the original beside it.

    Every downstream artifact — the golden signals, the dashboard's reliability
    count — reads these records. Leaving them at the run's own flags produced a
    dashboard whose grounding panel and reliability panel disagreed about the same
    quantity.
    """
    still_bad = {record["case_id"] for record in result["still_unfaithful"]}
    rechecked = {record["case_id"] for record in result["cleared"]} | still_bad

    with path.open("w", encoding="utf-8") as handle:
        for case in cases:
            if case["case_id"] in rechecked:
                case["narrative_faithful_as_measured"] = case.get("narrative_faithful")
                case["narrative_faithful"] = case["case_id"] not in still_bad
                if case["case_id"] not in still_bad:
                    case["unsupported_figures_as_measured"] = case.get("unsupported_figures")
                    case["unsupported_figures"] = []
                    case["unsupported_citations_as_measured"] = case.get("unsupported_citations")
                    case["unsupported_citations"] = []
            handle.write(json.dumps(case, sort_keys=True, default=str) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    use_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--eval-report", default=str(EVAL_REPORT))
    parser.add_argument("--eval-cases", default=str(EVAL_CASES))
    parser.add_argument("--output", default=str(RECHECK_PATH))
    parser.add_argument("--dry-run", action="store_true",
                        help="report the corrected figure without touching eval_report.json")
    parser.add_argument("--apply-only", action="store_true",
                        help="apply an existing faithfulness_recheck.json to the case "
                             "records without re-running the graph")
    args = parser.parse_args(argv)

    report_path, cases_path = Path(args.eval_report), Path(args.eval_cases)
    if not (report_path.exists() and cases_path.exists()):
        print("!! run `python -m eval.agent.run_agent_eval` first")
        return 1

    report = json.loads(report_path.read_text(encoding="utf-8"))
    cases = _load_cases(cases_path)

    if args.apply_only:
        existing = json.loads(Path(args.output).read_text(encoding="utf-8"))
        still = existing.get("still_unfaithful", [])
        still_ids = {record["case_id"] for record in still}
        # Derived rather than read: a case the run flagged and the recheck did not
        # leave flagged was cleared, whether or not the artifact lists it.
        cleared = [
            {"case_id": case["case_id"]}
            for case in cases
            if case.get("narrative_faithful_as_measured", case.get("narrative_faithful")) is False
            and case["case_id"] not in still_ids
        ]
        result = {
            "cleared": cleared,
            "still_unfaithful": still,
            "flagged": len(cleared) + len(still),
        }
        corrected = existing["corrected"]
        _apply_to_cases(cases, result, cases_path)
        print(f"applied to {cases_path}")
        return 0

    result = recheck(cases)
    corrected = summarize(cases, result)
    _apply_to_cases(cases, result, cases_path)

    as_measured = (report.get("macro") or {}).get("narrative_faithfulness_deterministic")
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rechecked_run_id": report.get("run_id"),
        "why": (
            "The run measured deterministic faithfulness with a supported-set that "
            "omitted two sources the narrative prompt actually supplies: figures "
            "published at the top level of the calculations (months_of_reserves) and "
            "the rule evaluations (the representative score and every policy floor). "
            "The check flagged the model for quoting what it had been handed."
        ),
        "why_this_is_sound": (
            "The run records every figure it flagged, and the fix only widens the "
            "supported set, so it can clear a flag and never raise a new one. Each "
            "flagged figure was re-tested against a supported set rebuilt from "
            "retrieval, the calculators and the rule engine — none of which involve a "
            "model."
        ),
        "why_this_is_a_lower_bound": (
            "The same round of fixes also tightened the figure pattern, so that a "
            "formula version no longer reads as a quoted number. The record keeps the "
            "flagged string but not the sentence around it, so a figure the new "
            "pattern would no longer match cannot be identified from the record alone "
            "and stays counted as unfaithful. The true figure is at least this high, "
            "never lower. Runs from now on commit the narrative text with each case, "
            "so a future recheck can re-read the prose directly."
        ),
        "as_measured": as_measured,
        "corrected": corrected,
        "cases_flagged_originally": result["flagged"],
        "cases_cleared": len(result["cleared"]),
        "cleared": result["cleared"],
        "cases_still_unfaithful": len(result["still_unfaithful"]),
        "still_unfaithful": result["still_unfaithful"],
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print()
    print(f"as measured : {as_measured}")
    print(f"corrected   : {corrected['macro']}  {corrected['per_product']}")
    print(f"cleared     : {len(result['cleared'])} of {result['flagged']}")
    print(f"still unfaithful: {len(result['still_unfaithful'])}")
    print(f"\nwrote {output}")

    if args.dry_run:
        print("(dry run — eval_report.json untouched)")
        return 0

    # Update the report in place, keeping the original figure visible beside it.
    macro = report.setdefault("macro", {})
    macro["narrative_faithfulness_deterministic_as_measured"] = as_measured
    macro["narrative_faithfulness_deterministic"] = corrected["macro"]
    for product, value in corrected["per_product"].items():
        entry = (report.get("per_product") or {}).get(product)
        if entry is not None:
            entry["narrative_faithfulness_deterministic_as_measured"] = entry.get(
                "narrative_faithfulness_deterministic"
            )
            entry["narrative_faithfulness_deterministic"] = value
    report.setdefault("metric_notes", {})["narrative_faithfulness_deterministic"] = (
        "Re-derived by scripts/recheck_faithfulness.py after a fix to the checker's "
        "supported-set, which had been flagging the model for quoting figures the "
        "system computed and supplied. The figure the run itself produced is kept "
        "beside it as narrative_faithfulness_deterministic_as_measured. It is a "
        "conservative lower bound; see reports/faithfulness_recheck.json."
    )
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"updated {report_path} (original figure kept as *_as_measured)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
