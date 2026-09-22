"""Produce ``reports/golden_signals.json`` — the operational view, from Phoenix.

AC-09: *"A Phoenix-derived golden-signals report (latency incl. thinking/acting/
tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval)
and a cost/latency dashboard."*

**Where each figure comes from, and why it matters that they differ.**

*Operational* figures — latency, its thinking/acting/tool split, tokens and cost
— are computed from **Phoenix spans**, read out of a running Phoenix instance or
the committed export at ``traces/phoenix_spans.jsonl``. They are not re-derived
from the evaluation's own case file. That distinction is the point of the
requirement: an evaluation harness measures itself with a stopwatch around its
own loop and cannot see inside a run, so it can report *that* an assessment took
eighteen seconds but not that fourteen of them were the cross-encoder. Only the
traces can split it, and a split invented from a total would be a fabrication
dressed as telemetry.

*Quality* figures — accuracy, hallucination rate, citation validity — are
imported from ``reports/eval_report.json``, which is where they are measured.
Nothing here recomputes them.

The split is carried in the output: every block states its ``source``, so a
reader can see which numbers came from traces and which from the evaluation.

Run::

    python scripts/export_traces.py          # produce the spans
    python -m eval.agent.run_agent_eval      # produce the quality figures
    python scripts/build_golden_signals.py   # combine them
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.config import REPO_ROOT  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402
from src.observability.tracing import (  # noqa: E402
    SPAN_KIND_ACTING,
    SPAN_KIND_ATTRIBUTE,
    SPAN_KIND_RETRIEVAL,
    SPAN_KIND_THINKING,
    SPAN_KIND_TOOL,
    span_kind_for,
)

REPORTS = REPO_ROOT / "reports"
TRACES = REPO_ROOT / "traces"
EVAL_REPORT = REPORTS / "eval_report.json"
SPANS_PATH = TRACES / "phoenix_spans.jsonl"
SIGNALS_PATH = REPORTS / "golden_signals.json"
DASHBOARD_DATA = REPORTS / "dashboard_data.csv"

#: Targets the requirements state, so a reader sees the measurement against the
#: bar rather than in isolation. A missed target is reported as missed.
TARGETS = {
    "citation_validity": 1.00,
    "cross_product_contamination_rate": 0.00,
    "hallucination_rate": 0.00,
}

#: Published per-million rates for the Gemini flash tier. Recorded alongside
#: every cost figure so a reader can recompute when pricing moves.
PRICE_IN_PER_MILLION = 0.30
PRICE_OUT_PER_MILLION = 2.50


# ======================================================================== spans


def load_spans(path: Path, *, from_phoenix: bool = False) -> tuple[list[dict], str]:
    """Spans, from a running Phoenix instance or the committed export.

    Returns ``(spans, source)``. Phoenix first when asked for: it holds the
    spans the collector actually received, which is the artifact AC-09 names.
    The export is the same spans written by committed code, and is what makes
    the figure reproducible in a fresh clone with no collector running.
    """
    if from_phoenix:
        spans = _from_phoenix()
        if spans:
            return spans, "phoenix_instance"
        print("  could not read spans from Phoenix; falling back to the export")

    if not path.exists():
        return [], "missing"
    spans = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return spans, f"committed_export:{path.relative_to(REPO_ROOT).as_posix()}"


def _from_phoenix() -> list[dict]:
    try:
        import phoenix as px

        client = px.Client()
        frame = client.get_spans_dataframe(project_name="credpilot")
        return json.loads(frame.to_json(orient="records"))
    except Exception as exc:  # noqa: BLE001 - reported, then the export is used
        print(f"  Phoenix unavailable: {type(exc).__name__}: {str(exc)[:160]}")
        return []


def _attributes(span: dict) -> dict[str, Any]:
    """A span's attributes, however the source spelled them.

    The in-process exporter writes a nested ``attributes`` dict; Phoenix's
    dataframe flattens them to ``attributes.x`` columns. Both are read here so
    the same report can be built from either.
    """
    attrs = span.get("attributes")
    if isinstance(attrs, dict):
        return attrs
    flat = {
        key.split("attributes.", 1)[1]: value
        for key, value in span.items()
        if key.startswith("attributes.") and value is not None
    }
    return flat


def _kind(span: dict) -> str:
    """A span's work kind, from its attribute or inferred from its name."""
    attrs = _attributes(span)
    explicit = attrs.get(SPAN_KIND_ATTRIBUTE) or attrs.get("credpilot.span_kind")
    return span_kind_for(str(span.get("name") or ""), explicit)


def _latency(span: dict) -> float | None:
    value = span.get("latency_ms")
    if value is None:
        value = span.get("latency")
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _percentile(values: Sequence[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(fraction * len(ordered))) - 1))
    return round(ordered[index], 1)


def _stats(values: Iterable[float]) -> dict[str, Any]:
    items = [v for v in values if v is not None]
    if not items:
        return {"count": 0, "p50": None, "p95": None, "p99": None,
                "mean": None, "max": None, "total": 0.0}
    return {
        "count": len(items),
        "p50": _percentile(items, 0.50),
        "p95": _percentile(items, 0.95),
        "p99": _percentile(items, 0.99),
        "mean": round(statistics.fmean(items), 1),
        "max": round(max(items), 1),
        "total": round(sum(items), 1),
    }


def _root_spans(spans: Sequence[dict]) -> list[dict]:
    """Spans with no parent inside the export — one per request, at the top.

    A trace's total is its root span's duration, not the sum of its children:
    children nest and overlap, and summing them counts the same wall-clock
    twice.
    """
    by_trace: dict[str, list[dict]] = defaultdict(list)
    for span in spans:
        trace_id = str(span.get("trace_id") or span.get("context.trace_id") or "")
        if trace_id:
            by_trace[trace_id].append(span)

    roots: list[dict] = []
    for trace_spans in by_trace.values():
        ids = {
            str(s.get("span_id") or s.get("context.span_id") or "") for s in trace_spans
        }
        for span in trace_spans:
            parent = str(span.get("parent_span_id") or span.get("parent_id") or "")
            if not parent or parent in ("None", "nan") or parent not in ids:
                roots.append(span)
                break
    return roots


def latency_from_spans(spans: Sequence[dict]) -> dict[str, Any]:
    """Latency split into thinking, acting, tool and retrieval time."""
    by_kind: dict[str, list[float]] = defaultdict(list)
    by_name: dict[str, list[float]] = defaultdict(list)

    for span in spans:
        latency = _latency(span)
        if latency is None:
            continue
        by_kind[_kind(span)].append(latency)
        by_name[str(span.get("name") or "unnamed")].append(latency)

    roots = [_latency(s) for s in _root_spans(spans)]
    root_stats = _stats([r for r in roots if r is not None])

    return {
        "unit": "milliseconds",
        "source": "phoenix spans",
        "request": {
            **root_stats,
            "comment": (
                "One root span per traced request. Children nest and overlap, so "
                "the total is the root's duration rather than the sum of its parts."
            ),
        },
        "thinking": {
            **_stats(by_kind.get(SPAN_KIND_THINKING, [])),
            "comment": "Model calls. The only billed work, and the tail of every run.",
        },
        "acting": {
            **_stats(by_kind.get(SPAN_KIND_ACTING, [])),
            "comment": (
                "Graph nodes doing deterministic work: routing, calculation, rule "
                "evaluation, assembling and validating the response."
            ),
        },
        "tool": {
            **_stats(by_kind.get(SPAN_KIND_TOOL, [])),
            "comment": "Calls crossing a tool boundary: the agentic-RAG tool, MCP.",
        },
        "retrieval": {
            **_stats(by_kind.get(SPAN_KIND_RETRIEVAL, [])),
            "comment": (
                "Stages inside the retrieval pipeline — embedding, BM25, Chroma, "
                "fusion, rerank, temporal and citation validation. Reported "
                "separately from tool time because this is where the latency is."
            ),
        },
        "by_span_name": {
            name: {
                "count": len(values),
                "p50": _percentile(values, 0.50),
                "p95": _percentile(values, 0.95),
                "total": round(sum(values), 1),
            }
            for name, values in sorted(by_name.items())
        },
    }


def tokens_from_spans(spans: Sequence[dict]) -> dict[str, Any]:
    """Token counts, read off the model-call spans that carry them.

    The narrative node and the policy-answer path both set ``input_tokens`` and
    ``output_tokens`` on their span. A span that carries no token attribute is
    not a model call and contributes nothing.
    """
    input_tokens = output_tokens = total_tokens = reasoning = 0
    calls = 0
    cost = 0.0

    for span in spans:
        if _kind(span) != SPAN_KIND_THINKING:
            continue
        attrs = _attributes(span)
        if not any(k in attrs for k in ("input_tokens", "output_tokens")):
            continue
        calls += 1
        input_tokens += int(attrs.get("input_tokens", 0) or 0)
        output_tokens += int(attrs.get("output_tokens", 0) or 0)
        total_tokens += int(attrs.get("total_tokens", 0) or 0)
        reasoning += int(attrs.get("reasoning_tokens", 0) or 0)
        cost += float(attrs.get("cost_usd", 0.0) or 0.0)

    # A model call that recorded no tokens is not a measurement gap, it is a
    # call that did not reach the provider — and the two look identical in a
    # report that shows only a zero. Said plainly here so nobody reads "$0.00
    # per assessment" as an efficiency result.
    unbilled = calls > 0 and input_tokens == 0 and output_tokens == 0

    return {
        "source": "phoenix spans (THINKING spans carrying token attributes)",
        "model_calls": calls,
        "model_calls_recorded_no_tokens": unbilled,
        **(
            {
                "zero_token_note": (
                    f"{calls} model-call span(s) were opened and every one recorded "
                    f"zero tokens. That means the calls did not reach the provider "
                    f"— an unreachable or unfunded API key — not that generation was "
                    f"free. Every cost figure below is therefore 0.00 by absence of "
                    f"measurement, and the narratives in this run are the "
                    f"deterministic fallback rather than generated prose."
                )
            }
            if unbilled
            else {}
        ),
        "input_total": input_tokens,
        "output_total": output_tokens,
        "total": total_tokens or (input_tokens + output_tokens),
        "reasoning_total": reasoning,
        "reasoning_share_of_output": (
            round(reasoning / output_tokens, 4) if output_tokens else None
        ),
        "cost_usd_from_spans": round(cost, 6),
        "comment": (
            "Reasoning tokens are billed as output and never appear in the text. "
            "Gemini allocates them by how hard it judges the task, so the figure "
            "belongs to the prompt rather than the model. Reported separately so a "
            "prompt change that starts drawing them is visible."
        ),
    }


def traffic_from_spans(spans: Sequence[dict]) -> dict[str, Any]:
    traces = {
        str(s.get("trace_id") or s.get("context.trace_id") or "")
        for s in spans
    } - {""}
    by_kind: dict[str, int] = defaultdict(int)
    for span in spans:
        by_kind[_kind(span)] += 1
    return {
        "source": "phoenix spans",
        "spans": len(spans),
        "traces": len(traces),
        "spans_by_kind": dict(sorted(by_kind.items())),
        "distinct_span_names": len({str(s.get("name") or "") for s in spans}),
    }


def errors_from_spans(spans: Sequence[dict]) -> dict[str, Any]:
    statuses: dict[str, int] = defaultdict(int)
    for span in spans:
        statuses[str(span.get("status") or "UNSET")] += 1
    failing = sum(count for name, count in statuses.items() if name.upper() == "ERROR")
    return {
        "source": "phoenix spans",
        "spans_by_status": dict(sorted(statuses.items())),
        "error_spans": failing,
        "error_span_rate": round(failing / len(spans), 4) if spans else None,
    }


# ================================================================ the eval report


def quality_from_eval(report: dict[str, Any]) -> dict[str, Any]:
    """Accuracy and grounding, imported from the evaluation. Not recomputed."""
    macro = report.get("macro") or {}
    per_product = report.get("per_product") or {}
    judge = report.get("judge") or {}
    hallucination = macro.get("judge_hallucination_rate")
    citation_validity = macro.get("citation_validity")

    return {
        "accuracy": {
            "source": "reports/eval_report.json",
            "outcome_accuracy_macro": macro.get("outcome_accuracy"),
            "outcome_accuracy_all_cases_macro": macro.get("outcome_accuracy_all_cases"),
            "directional_agreement_macro": macro.get("directional_agreement"),
            "human_review_agreement_macro": macro.get("human_review_agreement"),
            "supervisor_routing_accuracy_macro": macro.get("supervisor_routing_accuracy"),
            "response_validation_pass_rate_macro": macro.get(
                "response_validation_pass_rate"
            ),
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
        "grounding": {
            "source": "reports/eval_report.json",
            "judge_available": bool(judge.get("available", judge.get("model"))),
            "judge_unavailable_reason": judge.get("unavailable_reason"),
            "judged_cases": macro.get("judged_cases"),
            "hallucination_rate_macro": hallucination,
            "hallucination_rate_target": TARGETS["hallucination_rate"],
            "hallucination_rate_meets_target": (
                None
                if hallucination is None
                else hallucination <= TARGETS["hallucination_rate"]
            ),
            "judge_faithfulness_macro": macro.get("judge_faithfulness"),
            "judge_answer_relevancy_macro": macro.get("judge_answer_relevancy"),
            "deterministic_faithfulness_macro": macro.get(
                "narrative_faithfulness_deterministic"
            ),
            "citation_validity_macro": citation_validity,
            "citation_validity_target": TARGETS["citation_validity"],
            "citation_validity_meets_target": (
                None
                if citation_validity is None
                else citation_validity >= TARGETS["citation_validity"]
            ),
            "citation_recall_macro": macro.get("citation_recall"),
            "unsupported_claim_rate_macro": macro.get("unsupported_claim_rate"),
            "comment": (
                "hallucination_rate is 1 - DeepEval's hallucination score, which in "
                "4.x runs 1 = grounded. A null here means the judge did not run, "
                "not that the rate was zero — read judge_available beside it. The "
                "deterministic figure asks no model anything; on disagreement it is "
                "the one to believe."
            ),
        },
        "reliability": {
            "source": "reports/eval_report.json",
            "cases": macro.get("cases"),
            "completed": macro.get("completed"),
            "errors": macro.get("errors"),
            "failure_rate": (
                round((macro.get("errors") or 0) / macro["cases"], 4)
                if macro.get("cases") else None
            ),
            "halted_on_budget": macro.get("halted_runs"),
            "runs_with_a_degraded_tool_call": macro.get("runs_with_a_degraded_tool_call"),
            "steps_taken_mean": macro.get("steps_taken_mean"),
            "comment": (
                "A failed run is loud and rare. The quieter failures matter more: a "
                "rationale that asserted something its evidence does not support, a "
                "citation that does not resolve, a run that spent its budget without "
                "reaching a decision, and a tool call that had to be retried."
            ),
        },
    }


def cost_from(tokens: dict[str, Any], report: dict[str, Any], traces: int) -> dict[str, Any]:
    """Cost, estimated from the token counts the spans carry."""
    span_cost = float(tokens.get("cost_usd_from_spans") or 0.0)
    recomputed = round(
        tokens["input_total"] / 1_000_000 * PRICE_IN_PER_MILLION
        + tokens["output_total"] / 1_000_000 * PRICE_OUT_PER_MILLION,
        6,
    )
    judge = report.get("judge") or {}
    judge_cost = float(judge.get("judge_cost_usd") or 0.0)

    return {
        "currency": "USD",
        "source": "phoenix spans (tokens) x published per-million rates",
        "basis": "estimate from published rates, not a billing record",
        "rate_input_per_million": PRICE_IN_PER_MILLION,
        "rate_output_per_million": PRICE_OUT_PER_MILLION,
        "system_total_from_span_attribute": span_cost,
        "system_total_recomputed_from_tokens": recomputed,
        "system_per_traced_request": (
            round(recomputed / traces, 6) if traces else None
        ),
        "judge_total": round(judge_cost, 6),
        "judge_note": "evaluation overhead, not a running cost of the system",
        "comment": (
            "Two figures for the same thing: what the spans recorded, and what the "
            "token counts recompute to at the published rates. They should agree, "
            "and a divergence means a cost attribute was written with a stale rate."
        ),
    }


# ========================================================================= output


def build(
    report: dict[str, Any], spans: Sequence[dict], span_source: str
) -> dict[str, Any]:
    latency = latency_from_spans(spans)
    tokens = tokens_from_spans(spans)
    traffic = traffic_from_spans(spans)
    quality = quality_from_eval(report)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        # The Evidence-in-Repo Rule: an artifact names the code that wrote it.
        "generated_by": "scripts/build_golden_signals.py",
        "sources": {
            "operational": span_source,
            "quality": str(EVAL_REPORT.relative_to(REPO_ROOT)).replace("\\", "/"),
            "eval_generated_at_utc": report.get("generated_at_utc"),
            "eval_run_id": report.get("run_id"),
            "note": (
                "Latency, its thinking/acting/tool split, tokens and cost are "
                "computed from Phoenix spans. Accuracy, hallucination rate and "
                "citation validity are imported from the evaluation report, which "
                "is where they are measured. Nothing here is derived from the "
                "other: a latency split invented from an evaluation total would be "
                "a fabrication, and an accuracy figure recomputed here would be a "
                "second opinion nobody asked for."
            ),
        },
        "latency": latency,
        "traffic": traffic,
        "errors": {
            **errors_from_spans(spans),
            **{
                f"eval_{k}": v
                for k, v in quality["reliability"].items()
                if k not in ("source", "comment")
            },
        },
        "saturation": {
            "source": "reports/eval_report.json",
            "step_budget": 32,
            "recursion_limit": 60,
            "steps_taken_mean": (report.get("macro") or {}).get("steps_taken_mean"),
            "halted_on_budget": (report.get("macro") or {}).get("halted_runs"),
        },
        "tokens": tokens,
        "cost": cost_from(tokens, report, traffic["traces"]),
        "accuracy": quality["accuracy"],
        "grounding": quality["grounding"],
    }


def write_dashboard_data(signals: dict[str, Any], path: Path) -> int:
    """The flat table behind ``reports/dashboard.png``.

    A CSV because a reader should be able to check the chart against numbers
    without running anything. Every row carries the source of its value, so a
    reader can tell a Phoenix-derived latency from an eval-derived accuracy at a
    glance.

    Written with ``DataFrame.to_csv``, the method REQ-103 names. What it writes
    is the **aggregated** table the dashboard draws — p50/p95 by span kind,
    token totals, the quality figures — rather than a raw dump of every span.
    A dump of 980 spans is not a dashboard data file: it cannot be read against
    the picture, which is the whole reason the requirement asks for the CSV.
    The raw frame is already committed at ``traces/phoenix_spans.jsonl`` for
    anyone who wants to re-derive these rows, and
    ``--raw-spans-csv`` writes it as CSV too.
    """
    import pandas as pd

    rows: list[dict[str, Any]] = []

    def add(group: str, metric: str, value: Any, source: str,
            target: Any = None, unit: str = "") -> None:
        if value is None:
            return
        rows.append({
            "group": group, "metric": metric, "value": value,
            "target": "" if target is None else target,
            "unit": unit, "source": source,
        })

    latency = signals["latency"]
    for kind in ("request", "thinking", "acting", "tool", "retrieval"):
        block = latency.get(kind) or {}
        add("latency", f"{kind}_p50", block.get("p50"), "phoenix", unit="ms")
        add("latency", f"{kind}_p95", block.get("p95"), "phoenix", unit="ms")

    tokens = signals["tokens"]
    add("tokens", "input_total", tokens["input_total"], "phoenix", unit="tokens")
    add("tokens", "output_total", tokens["output_total"], "phoenix", unit="tokens")
    add("tokens", "reasoning_total", tokens["reasoning_total"], "phoenix", unit="tokens")
    add("tokens", "model_calls", tokens["model_calls"], "phoenix", unit="count")

    cost = signals["cost"]
    add("cost", "usd_per_traced_request", cost["system_per_traced_request"],
        "phoenix", unit="usd")
    add("cost", "usd_total", cost["system_total_recomputed_from_tokens"],
        "phoenix", unit="usd")

    traffic = signals["traffic"]
    add("traffic", "traces", traffic["traces"], "phoenix", unit="count")
    add("traffic", "spans", traffic["spans"], "phoenix", unit="count")
    for kind, count in (traffic.get("spans_by_kind") or {}).items():
        add("traffic", f"spans_{kind.lower()}", count, "phoenix", unit="count")

    accuracy = signals["accuracy"]
    add("accuracy", "outcome_accuracy_macro", accuracy["outcome_accuracy_macro"],
        "eval", unit="rate")
    add("accuracy", "directional_agreement_macro",
        accuracy["directional_agreement_macro"], "eval", unit="rate")
    add("accuracy", "human_review_agreement_macro",
        accuracy["human_review_agreement_macro"], "eval", unit="rate")
    add("accuracy", "supervisor_routing_accuracy_macro",
        accuracy["supervisor_routing_accuracy_macro"], "eval", 1.0, "rate")
    for product, values in (accuracy.get("per_product") or {}).items():
        add("accuracy_by_product", f"{product}_outcome_accuracy",
            values.get("outcome_accuracy"), "eval", unit="rate")

    grounding = signals["grounding"]
    add("grounding", "citation_validity", grounding["citation_validity_macro"],
        "eval", grounding["citation_validity_target"], "rate")
    add("grounding", "citation_recall", grounding["citation_recall_macro"],
        "eval", unit="rate")
    add("grounding", "faithfulness_deterministic",
        grounding["deterministic_faithfulness_macro"], "eval", unit="rate")
    add("grounding", "faithfulness_judge", grounding["judge_faithfulness_macro"],
        "eval", unit="rate")
    add("grounding", "answer_relevancy_judge",
        grounding["judge_answer_relevancy_macro"], "eval", unit="rate")
    add("grounding", "hallucination_rate", grounding["hallucination_rate_macro"],
        "eval", grounding["hallucination_rate_target"], "rate")

    errors = signals["errors"]
    add("reliability", "eval_failure_rate", errors.get("eval_failure_rate"),
        "eval", 0.0, "rate")
    add("reliability", "eval_halted_on_budget", errors.get("eval_halted_on_budget"),
        "eval", 0, "count")
    add("reliability", "error_spans", errors.get("error_spans"), "phoenix", 0, "count")
    add("reliability", "steps_taken_mean", signals["saturation"]["steps_taken_mean"],
        "eval", signals["saturation"]["step_budget"], "steps")

    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=["group", "metric", "value", "target",
                                        "unit", "source"])
    frame.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    return len(rows)


def write_raw_span_csv(spans: Sequence[dict], path: Path) -> int:
    """The Phoenix span frame itself, as CSV.

    ``get_spans_dataframe().to_csv(...)`` in the literal sense REQ-103 names,
    for a reader who wants to re-derive the aggregated table rather than trust
    it. Off by default because it is a second copy of
    ``traces/phoenix_spans.jsonl`` in a lossier format — the attributes of a
    span are a nested object, and flattening them to columns loses the ones
    that vary by span kind.
    """
    import pandas as pd

    flat: list[dict[str, Any]] = []
    for span in spans:
        row = {k: v for k, v in span.items() if k != "attributes"}
        for key, value in (_attributes(span) or {}).items():
            row[f"attributes.{key}"] = value
        flat.append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(flat).to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    return len(flat)


def main(argv: Sequence[str] | None = None) -> int:
    use_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-report", default=str(EVAL_REPORT))
    parser.add_argument("--spans", default=str(SPANS_PATH))
    parser.add_argument("--phoenix", action="store_true",
                        help="read spans from a running Phoenix instance first")
    parser.add_argument("--output", default=str(SIGNALS_PATH))
    parser.add_argument("--dashboard-data", default=str(DASHBOARD_DATA))
    parser.add_argument("--raw-spans-csv", default=None,
                        help="also write the raw Phoenix span frame to this path")
    args = parser.parse_args(argv)

    report_path = Path(args.eval_report)
    if not report_path.exists():
        print(f"!! {report_path} not found — run `python -m eval.agent.run_agent_eval` first")
        return 1
    report = json.loads(report_path.read_text(encoding="utf-8"))

    spans, span_source = load_spans(Path(args.spans), from_phoenix=args.phoenix)
    if not spans:
        print(
            f"!! no spans at {args.spans} and none in Phoenix.\n"
            f"   Latency, tokens and cost are Phoenix-derived by requirement, so "
            f"this report cannot be built without them.\n"
            f"   Run `python scripts/export_traces.py` first."
        )
        return 1

    signals = build(report, spans, span_source)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(signals, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = write_dashboard_data(signals, Path(args.dashboard_data))
    raw_rows = (
        write_raw_span_csv(spans, Path(args.raw_spans_csv)) if args.raw_spans_csv else 0
    )

    latency = signals["latency"]
    print(f"span source        : {span_source}")
    print(f"spans / traces     : {signals['traffic']['spans']} / "
          f"{signals['traffic']['traces']}")
    print(f"request p50 / p95  : {latency['request']['p50']} / "
          f"{latency['request']['p95']} ms")
    print(f"  thinking p50/p95 : {latency['thinking']['p50']} / "
          f"{latency['thinking']['p95']} ms  ({latency['thinking']['count']} spans)")
    print(f"  acting   p50/p95 : {latency['acting']['p50']} / "
          f"{latency['acting']['p95']} ms  ({latency['acting']['count']} spans)")
    print(f"  tool     p50/p95 : {latency['tool']['p50']} / "
          f"{latency['tool']['p95']} ms  ({latency['tool']['count']} spans)")
    print(f"  retrieval p50/p95: {latency['retrieval']['p50']} / "
          f"{latency['retrieval']['p95']} ms  ({latency['retrieval']['count']} spans)")
    print(f"tokens in / out    : {signals['tokens']['input_total']} / "
          f"{signals['tokens']['output_total']} "
          f"({signals['tokens']['model_calls']} model call(s))")
    if signals["tokens"].get("model_calls_recorded_no_tokens"):
        print("  !! every model call recorded zero tokens — the calls did not "
              "reach the provider.")
        print("     Cost below is 0.00 by absence of measurement, not by "
              "efficiency.")
    print(f"cost per request   : ${signals['cost']['system_per_traced_request']}")
    print(f"outcome accuracy   : {signals['accuracy']['outcome_accuracy_macro']}  (eval)")
    print(f"hallucination rate : {signals['grounding']['hallucination_rate_macro']}  "
          f"(eval; judge available: {signals['grounding']['judge_available']})")
    print(f"citation validity  : {signals['grounding']['citation_validity_macro']}  (eval)")
    print(f"\nwrote {output}")
    print(f"wrote {args.dashboard_data}  ({rows} rows)")
    if raw_rows:
        print(f"wrote {args.raw_spans_csv}  ({raw_rows} span rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
