"""Produce ``reports/golden_signals.json`` — the operational view of one eval run.

REQ-098: *"Golden signals | reports/golden_signals.json | latency, tokens in/out,
cost estimate, accuracy, hallucination rate"*.

The four classic golden signals are latency, traffic, errors and saturation. For
a system like this one they translate as:

* **latency** — wall clock per assessment, split into the deterministic part and
  the one model call, because only the second is variable and only the second is
  billed;
* **traffic** — assessments run, and the retrieval each one issued;
* **errors** — runs that failed outright, plus the quieter failures that matter
  more here: an unfaithful rationale, a citation that does not resolve, a run
  that halted on its budget;
* **saturation** — step budget consumed against the budget available, and token
  spend.

Two additions specific to an AI system, both named in the requirement: accuracy
and hallucination rate.

Everything is derived from committed artifacts — ``reports/eval_report.json``,
``reports/eval_cases.jsonl`` and the action log — so this script re-derives and
never re-measures. Run the evaluation first::

    python -m eval.agent.run_agent_eval
    python scripts/build_golden_signals.py
"""

from __future__ import annotations

import argparse
import json
import sys
import statistics
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
SIGNALS_PATH = REPORTS / "golden_signals.json"
DASHBOARD_DATA = REPORTS / "dashboard_data.csv"

#: Targets the requirements state, so a reader sees the measurement against the
#: bar rather than in isolation. A missed target is reported as missed.
TARGETS = {
    "citation_validity": 1.00,
    "cross_product_contamination_rate": 0.00,
    "hallucination_rate": 0.00,
}


def _percentile(values: Sequence[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(fraction * len(ordered))) - 1))
    return round(ordered[index], 1)


def _load_cases(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(report: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    macro = report.get("macro") or {}
    per_product = report.get("per_product") or {}
    ok = [c for c in cases if not c.get("error")]

    latencies = [float(c["latency_ms"]) for c in ok if c.get("latency_ms")]
    narrative_latencies = [
        float(c["narrative_latency_ms"]) for c in ok if c.get("narrative_latency_ms")
    ]

    input_tokens = sum(int((c.get("usage") or {}).get("input_tokens", 0)) for c in ok)
    output_tokens = sum(int((c.get("usage") or {}).get("output_tokens", 0)) for c in ok)
    reasoning_tokens = sum(int((c.get("usage") or {}).get("reasoning_tokens", 0)) for c in ok)
    system_cost = round(sum(float(c.get("cost_usd") or 0.0) for c in ok), 6)
    judge = report.get("judge") or {}
    judge_cost = float(judge.get("judge_cost_usd") or 0.0)

    hallucination_rate = macro.get("judge_hallucination_rate")
    citation_validity = macro.get("citation_validity")

    signals = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "derived_from": {
            "eval_report": str(EVAL_REPORT.relative_to(REPO_ROOT)).replace("\\", "/"),
            "eval_cases": str(EVAL_CASES.relative_to(REPO_ROOT)).replace("\\", "/"),
            "eval_generated_at_utc": report.get("generated_at_utc"),
        },
        "note": (
            "Re-derived from a committed evaluation run, not re-measured. Figures are "
            "macro-averaged across products where the underlying metric is a rate."
        ),

        # ---------------------------------------------------------------- latency
        "latency": {
            "unit": "milliseconds",
            "assessment_p50": _percentile(latencies, 0.50),
            "assessment_p95": _percentile(latencies, 0.95),
            "assessment_p99": _percentile(latencies, 0.99),
            "assessment_mean": round(statistics.fmean(latencies), 1) if latencies else None,
            "narrative_call_p50": _percentile(narrative_latencies, 0.50),
            "narrative_call_p95": _percentile(narrative_latencies, 0.95),
            "narrative_call_mean": (
                round(statistics.fmean(narrative_latencies), 1) if narrative_latencies else None
            ),
            "deterministic_share_of_mean": (
                round(
                    1 - statistics.fmean(narrative_latencies) / statistics.fmean(latencies), 4
                )
                if latencies and narrative_latencies else None
            ),
            "comment": (
                "The deterministic pipeline — retrieval, calculation, rules — is the "
                "faster half and does not vary with a provider. The single model call "
                "dominates the tail."
            ),
        },

        # ---------------------------------------------------------------- traffic
        "traffic": {
            "assessments": len(cases),
            "assessments_completed": len(ok),
            "products": sorted(per_product),
            "cases_per_product": {k: v.get("cases") for k, v in per_product.items()},
            "model_calls_per_assessment": 1,
            "judge_calls_total": int(judge.get("judge_calls") or 0),
        },

        # ----------------------------------------------------------------- errors
        "errors": {
            "failed_runs": len(cases) - len(ok),
            "failure_rate": (
                round((len(cases) - len(ok)) / len(cases), 4) if cases else None
            ),
            "halted_on_budget": sum(1 for c in ok if c.get("halted")),
            "unfaithful_rationales": sum(
                1 for c in ok if c.get("narrative_faithful") is False
            ),
            "runs_with_unresolvable_citation": sum(
                1 for c in ok if c.get("all_citations_resolve") is False
            ),
            "comment": (
                "A failed run is loud and rare. The three rows beneath it are the quiet "
                "failures that matter more: a rationale that asserted something its "
                "evidence does not support, a citation that does not resolve, and a run "
                "that spent its budget without reaching a decision."
            ),
        },

        # ------------------------------------------------------------- saturation
        "saturation": {
            "step_budget": 24,
            "steps_taken_mean": macro.get("steps_taken_mean"),
            "steps_taken_max": max((int(c.get("steps_taken") or 0) for c in ok), default=None),
            "budget_headroom_mean": (
                round(1 - (macro.get("steps_taken_mean") or 0) / 24, 4)
                if macro.get("steps_taken_mean") else None
            ),
            "recursion_limit": 40,
        },

        # ----------------------------------------------------------------- tokens
        "tokens": {
            "system_input_total": input_tokens,
            "system_output_total": output_tokens,
            "system_reasoning_total": reasoning_tokens,
            "system_input_per_assessment": round(input_tokens / len(ok), 1) if ok else None,
            "system_output_per_assessment": round(output_tokens / len(ok), 1) if ok else None,
            "reasoning_share_of_output": (
                round(reasoning_tokens / output_tokens, 4) if output_tokens else None
            ),
            "judge_input_total": int(judge.get("judge_input_tokens") or 0),
            "judge_output_total": int(judge.get("judge_output_tokens") or 0),
            "comment": (
                "Reasoning tokens are billed as output and never appear in the text. "
                "Gemini allocates them by how hard it judges the task, so the figure "
                "belongs to the prompt rather than the model: a short under-specified "
                "prompt drew 388 of 419 output tokens, while the narrative prompt — "
                "long, fully specified, decision already made — draws none. Reported "
                "separately so a prompt change that starts drawing them is visible."
            ),
        },

        # ------------------------------------------------------------------- cost
        "cost": {
            "currency": "USD",
            "basis": "estimate from published per-million rates, not a billing record",
            "rate_input_per_million": 0.30,
            "rate_output_per_million": 2.50,
            "system_total": system_cost,
            "system_per_assessment": round(system_cost / len(ok), 6) if ok else None,
            "judge_total": round(judge_cost, 6),
            "judge_note": "evaluation overhead, not a running cost of the system",
            "run_total": round(system_cost + judge_cost, 6),
        },

        # --------------------------------------------------------------- accuracy
        "accuracy": {
            "outcome_accuracy_macro": macro.get("outcome_accuracy"),
            "outcome_accuracy_all_cases_macro": macro.get("outcome_accuracy_all_cases"),
            "directional_agreement_macro": macro.get("directional_agreement"),
            "human_review_agreement_macro": macro.get("human_review_agreement"),
            "per_product": {
                key: {
                    "outcome_accuracy": value.get("outcome_accuracy"),
                    "directional_agreement": value.get("directional_agreement"),
                }
                for key, value in per_product.items()
            },
            "comment": (
                "Agreement with a synthetic generator, which is not the same as "
                "correctness. See R-01 in docs/risk-register.md."
            ),
        },

        # ---------------------------------------------------------------- grounding
        "grounding": {
            "hallucination_rate_macro": hallucination_rate,
            "hallucination_rate_target": TARGETS["hallucination_rate"],
            "hallucination_rate_meets_target": (
                hallucination_rate is not None and hallucination_rate <= TARGETS["hallucination_rate"]
            ),
            "judge_faithfulness_macro": macro.get("judge_faithfulness"),
            "judge_answer_relevancy_macro": macro.get("judge_answer_relevancy"),
            "deterministic_faithfulness_macro": macro.get("narrative_faithfulness_deterministic"),
            "citation_validity_macro": citation_validity,
            "citation_validity_target": TARGETS["citation_validity"],
            "citation_validity_meets_target": (
                citation_validity is not None and citation_validity >= TARGETS["citation_validity"]
            ),
            "citation_recall_macro": macro.get("citation_recall"),
            "comment": (
                "hallucination_rate is derived as 1 - DeepEval's hallucination score, "
                "which in 4.x runs 1 = grounded. The deterministic figure beside it asks "
                "no model anything; on disagreement it is the one to believe."
            ),
        },
    }
    return signals


def write_dashboard_data(signals: dict[str, Any], report: dict[str, Any], path: Path) -> None:
    """The flat table behind ``reports/dashboard.png``.

    A CSV because a reader should be able to check the chart against numbers
    without running anything.
    """
    import csv

    rows: list[dict[str, Any]] = []

    def add(group: str, metric: str, value: Any, target: Any = None, unit: str = "") -> None:
        if value is None:
            return
        rows.append({
            "group": group, "metric": metric, "value": value,
            "target": "" if target is None else target, "unit": unit,
        })

    grounding = signals["grounding"]
    accuracy = signals["accuracy"]
    latency = signals["latency"]

    add("accuracy", "outcome_accuracy_macro", accuracy["outcome_accuracy_macro"], unit="rate")
    add("accuracy", "directional_agreement_macro", accuracy["directional_agreement_macro"], unit="rate")
    add("accuracy", "human_review_agreement_macro", accuracy["human_review_agreement_macro"], unit="rate")
    for product, values in (report.get("per_product") or {}).items():
        add("accuracy_by_product", f"{product}_outcome_accuracy", values.get("outcome_accuracy"), unit="rate")

    add("grounding", "citation_validity", grounding["citation_validity_macro"],
        grounding["citation_validity_target"], "rate")
    add("grounding", "citation_recall", grounding["citation_recall_macro"], unit="rate")
    add("grounding", "faithfulness_deterministic", grounding["deterministic_faithfulness_macro"], unit="rate")
    add("grounding", "faithfulness_judge", grounding["judge_faithfulness_macro"], unit="rate")
    add("grounding", "answer_relevancy_judge", grounding["judge_answer_relevancy_macro"], unit="rate")
    add("grounding", "hallucination_rate", grounding["hallucination_rate_macro"],
        grounding["hallucination_rate_target"], "rate")

    add("latency", "assessment_p50", latency["assessment_p50"], unit="ms")
    add("latency", "assessment_p95", latency["assessment_p95"], unit="ms")
    add("latency", "narrative_call_p50", latency["narrative_call_p50"], unit="ms")
    add("latency", "narrative_call_p95", latency["narrative_call_p95"], unit="ms")

    tokens = signals["tokens"]
    add("tokens", "input_per_assessment", tokens["system_input_per_assessment"], unit="tokens")
    add("tokens", "output_per_assessment", tokens["system_output_per_assessment"], unit="tokens")
    add("tokens", "reasoning_share_of_output", tokens["reasoning_share_of_output"], unit="rate")

    cost = signals["cost"]
    add("cost", "usd_per_assessment", cost["system_per_assessment"], unit="usd")

    errors = signals["errors"]
    add("reliability", "failure_rate", errors["failure_rate"], 0.0, "rate")
    add("reliability", "unfaithful_rationales", errors["unfaithful_rationales"], 0, "count")
    add("reliability", "halted_on_budget", errors["halted_on_budget"], 0, "count")
    add("reliability", "steps_taken_mean", signals["saturation"]["steps_taken_mean"], 24, "steps")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["group", "metric", "value", "target", "unit"])
        writer.writeheader()
        writer.writerows(rows)


def main(argv: Sequence[str] | None = None) -> int:
    use_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-report", default=str(EVAL_REPORT))
    parser.add_argument("--eval-cases", default=str(EVAL_CASES))
    parser.add_argument("--output", default=str(SIGNALS_PATH))
    parser.add_argument("--dashboard-data", default=str(DASHBOARD_DATA))
    args = parser.parse_args(argv)

    report_path = Path(args.eval_report)
    if not report_path.exists():
        print(f"!! {report_path} not found — run `python -m eval.agent.run_agent_eval` first")
        return 1

    report = json.loads(report_path.read_text(encoding="utf-8"))
    cases = _load_cases(Path(args.eval_cases))
    signals = build(report, cases)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(signals, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    dashboard_data = Path(args.dashboard_data)
    write_dashboard_data(signals, report, dashboard_data)

    print(f"assessments        : {signals['traffic']['assessments_completed']}")
    print(f"latency p50 / p95  : {signals['latency']['assessment_p50']} / "
          f"{signals['latency']['assessment_p95']} ms")
    print(f"tokens in / out    : {signals['tokens']['system_input_total']} / "
          f"{signals['tokens']['system_output_total']} "
          f"({signals['tokens']['system_reasoning_total']} reasoning)")
    print(f"cost per assessment: ${signals['cost']['system_per_assessment']}")
    print(f"outcome accuracy   : {signals['accuracy']['outcome_accuracy_macro']}")
    print(f"hallucination rate : {signals['grounding']['hallucination_rate_macro']} "
          f"(target {TARGETS['hallucination_rate']})")
    print(f"citation validity  : {signals['grounding']['citation_validity_macro']} "
          f"(target {TARGETS['citation_validity']})")
    print(f"\nwrote {output}")
    print(f"wrote {dashboard_data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
