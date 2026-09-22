"""End-to-end agent evaluation: run every golden case, then score the answer.

REQ-097: *"DeepEval (or equiv) over a golden set: hallucination +
faithfulness/relevance; LLM-as-judge"*.

Two independent families of measurement, kept apart on purpose:

**Deterministic.** Did the recommendation match the golden outcome? Did the
citations resolve, and did they include the rules the golden set names? Did the
narrative quote a figure or a citation that is not in its evidence
(:func:`src.narrative.verify_narrative`)? None of this asks a model anything, so
none of it can drift.

**LLM-as-judge.** DeepEval's faithfulness, hallucination and answer-relevancy,
judged by Gemini (:mod:`eval.agent.judges`). This catches what string matching
cannot — a rationale that cites the right rule and still describes it wrongly.

Where the two disagree, the deterministic result is the one to believe: the judge
shares a model family with the system it is judging.

**Macro-averaging.** Every headline figure is the unweighted mean of the two
products' figures. Mortgage brings 75 cases to education's 20, so a pooled mean
would be a mortgage score with a rounding error attached, and a total failure on
education would barely move it.

Run::

    python -m eval.agent.run_agent_eval --judge-all          # the final run
    python -m eval.agent.run_agent_eval --judge-limit-per-product 10   # cheap, local
    python -m eval.agent.run_agent_eval --no-judge           # deterministic only
    python -m eval.agent.run_agent_eval --limit-per-product 5

``--judge-all`` is the mode for the committed run and **fails** rather than
degrading if the judge is unreachable: a report labelled "every case judged"
that judged none is worse than no report. ``--judge-limit-per-product`` is the
cheap mode for development, and states its denominator in the output.

**The harness enters the graph at its real entry point.** Every case goes
through intake, the input guardrail, the Supervisor, the product specialist,
retrieval, the rules, the recommendation, the narrative, the response validator
and the output guardrail — the path a request actually takes. Supervisor routing
accuracy is scored because of it, and it could not have been from an internal
entry point.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import uuid
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from src.config import REPO_ROOT, get_config
from src.console import use_utf8_stdio
from src.domain import LendingProductDomain
from eval.retrieval.metrics import round_for_serialization
from eval.agent.dataset import (
    AgentCase,
    direction_of,
    load_cases,
    outcome_family,
    rule_coverage,
)

REPORTS = REPO_ROOT / "reports"
REPORT_PATH = REPORTS / "eval_report.json"
CASES_PATH = REPORTS / "eval_cases.jsonl"

#: DeepEval's pass mark. Reported alongside the raw scores so a reader can apply
#: their own; nothing in the system gates on it.
JUDGE_THRESHOLD = 0.7


# ======================================================================== running


@dataclass
class CaseOutcome:
    """What one case produced, before any judging."""

    case: AgentCase
    outcome: str | None = None
    raw_outcome: str | None = None
    eligibility: str | None = None
    risk_level: str | None = None
    requires_human_review: bool | None = None
    citations: list[str] = field(default_factory=list)
    rule_ids: list[str] = field(default_factory=list)
    evidence_texts: list[str] = field(default_factory=list)
    all_citations_resolve: bool | None = None
    narrative: str = ""
    narrative_faithful: bool | None = None
    unsupported_citations: list[str] = field(default_factory=list)
    unsupported_figures: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    steps_taken: int = 0
    halted: bool = False
    latency_ms: float = 0.0
    narrative_latency_ms: float = 0.0
    usage: dict[str, int] = field(default_factory=dict)
    cost_usd: float = 0.0
    error: str | None = None
    judge: dict[str, Any] = field(default_factory=dict)

    # -- the top-level architecture -------------------------------------------
    #: Which route the Supervisor chose. Scored, because the Supervisor is the
    #: component most able to send a file to the wrong body of lending law, and
    #: an evaluation that entered below it would never have tested that.
    route: str | None = None
    routed_to_correct_product: bool | None = None
    response_validated: bool | None = None
    validation_failures: list[str] = field(default_factory=list)
    output_guardrail: dict[str, Any] = field(default_factory=dict)
    degradations: list[dict[str, Any]] = field(default_factory=list)
    required_rules_fetched: list[str] = field(default_factory=list)

    # -- deterministic scoring --------------------------------------------------

    @property
    def outcome_correct(self) -> bool | None:
        if self.case.expected_outcome is None or self.outcome is None:
            return None
        return self.outcome == self.case.expected_outcome

    @property
    def direction_correct(self) -> bool | None:
        expected, actual = self.case.expected_direction, direction_of(self.outcome)
        if expected is None or actual is None:
            return None
        return expected == actual

    @property
    def citation_recall(self) -> float | None:
        """Of the rules the golden set names, how many were cited.

        Measured on rule ids rather than full citation strings: the two sources
        spell a citation differently (``POL-002 EDU-UW-001`` against
        ``POL-DTI-001 v2.0 rule DTI-CONV-001``), and a spelling mismatch is not a
        retrieval failure.
        """
        expected = set(self.case.expected_rule_ids) or _rules_in(self.case.expected_citations)
        if not expected:
            return None
        return len(expected & set(self.rule_ids)) / len(expected)

    def as_dict(self) -> dict[str, Any]:
        return {
            **self.case.as_dict(),
            "actual_outcome": self.outcome,
            "actual_raw_outcome": self.raw_outcome,
            "actual_eligibility": self.eligibility,
            "actual_risk_level": self.risk_level,
            "actual_requires_human_review": self.requires_human_review,
            "outcome_correct": self.outcome_correct,
            "direction_correct": self.direction_correct,
            "citation_recall": self.citation_recall,
            "citations": self.citations,
            "rule_ids": self.rule_ids,
            "all_citations_resolve": self.all_citations_resolve,
            "narrative_faithful": self.narrative_faithful,
            "unsupported_citations": self.unsupported_citations,
            "unsupported_figures": self.unsupported_figures,
            "narrative_chars": len(self.narrative),
            # Committed so the faithfulness figure can be re-derived by a reader
            # without re-running the model. It is built from redacted context and
            # carries no applicant identifiers; tests/rag/test_pii_logging.py
            # scans this file like every other committed artifact.
            "narrative": self.narrative,
            "steps": self.steps,
            "steps_taken": self.steps_taken,
            "halted": self.halted,
            "latency_ms": round(self.latency_ms, 1),
            "narrative_latency_ms": round(self.narrative_latency_ms, 1),
            "usage": self.usage,
            "cost_usd": self.cost_usd,
            "judge": self.judge,
            "error": self.error,
            "route": self.route,
            "routed_to_correct_product": self.routed_to_correct_product,
            "response_validated": self.response_validated,
            "validation_failures": self.validation_failures,
            "output_guardrail": self.output_guardrail,
            "degradations": self.degradations,
            "required_rules_fetched": self.required_rules_fetched,
        }


def _rules_in(citations: Sequence[str]) -> set[str]:
    """Rule ids inside citation strings, for comparing across spellings."""
    import re

    found: set[str] = set()
    for citation in citations:
        for token in re.findall(r"[A-Z]{2,6}-[A-Z]{2,6}-\d+", citation):
            if not token.startswith("POL-"):
                found.add(token)
    return found


def run_case(case: AgentCase, graph: Any, run_id: str) -> CaseOutcome:
    """Run one application all the way through the deployed graph.

    **The whole graph, from its real entry point.** Not
    ``mortgage_policy_retrieval`` with a hand-built state, but ``intake`` — so
    every case exercises intake, the input guardrail, the Supervisor's routing
    decision, the product specialist, retrieval, the rule engine, the
    recommendation, the narrative, the response validator and the output
    guardrail. An evaluation that entered at an internal node would be measuring
    a path no user can take, and the Supervisor's routing — the component most
    likely to send a file to the wrong corpus — would be scored by nothing.

    ``run_id`` scopes the checkpoint thread to this evaluation run. Without it
    the thread id is stable across runs, and LangGraph resumes the thread the
    previous run left at END rather than re-running the case — a case that took
    13 seconds came back in 0.2 with no retrieval performed, replaying a verdict
    reached before the rule engine was fixed. An evaluation that quietly reports
    the last run's answers is worse than one that fails.
    """
    from src.graph import initial_state

    result = CaseOutcome(case=case)
    started = time.perf_counter()
    try:
        state = initial_state(case.packet_path, as_of_date=case.as_of_date)
        final = graph.invoke(
            state, config={"configurable": {"thread_id": f"eval-{run_id}-{case.case_id}"}}
        )
    except Exception as exc:  # noqa: BLE001 - one bad case must not end the run
        result.error = f"{type(exc).__name__}: {exc}"
        result.latency_ms = (time.perf_counter() - started) * 1000
        traceback.print_exc()
        return result
    result.latency_ms = (time.perf_counter() - started) * 1000

    recommendation = final.get("recommendation") or {}
    evidence = final.get("policy_evidence") or []
    narrative = final.get("narrative") or {}

    result.raw_outcome = recommendation.get("outcome")
    result.outcome = outcome_family(result.raw_outcome)
    result.eligibility = (final.get("eligibility") or {}).get("status")
    result.risk_level = (final.get("risk") or {}).get("level")
    result.requires_human_review = bool(final.get("requires_human_review"))
    result.citations = list(recommendation.get("citations") or [])
    result.rule_ids = sorted({e["rule_id"] for e in evidence if e.get("rule_id")})
    result.evidence_texts = [e.get("text", "") for e in evidence if e.get("text")]
    result.all_citations_resolve = recommendation.get("all_citations_resolve")
    result.narrative = narrative.get("text") or ""
    result.narrative_faithful = narrative.get("is_faithful")
    result.unsupported_citations = list(narrative.get("unsupported_citations") or [])
    result.unsupported_figures = list(narrative.get("unsupported_figures") or [])
    result.narrative_latency_ms = float(narrative.get("latency_ms") or 0.0)
    result.usage = dict(narrative.get("usage") or {})
    result.cost_usd = float(narrative.get("cost_usd") or 0.0)
    result.steps = list(final.get("steps") or [])
    result.steps_taken = int(final.get("steps_taken") or 0)
    result.halted = bool(final.get("halted"))

    # -- what the top-level architecture added ---------------------------------
    supervisor = final.get("supervisor") or {}
    response = final.get("final_response") or {}
    result.route = supervisor.get("route")
    result.routed_to_correct_product = (
        None
        if not supervisor.get("route")
        else supervisor.get("route") == (
            "MORTGAGE" if case.product is LendingProductDomain.MORTGAGE
            else "EDUCATION_LOAN"
        )
    )
    result.response_validated = (response.get("validation") or {}).get("passed")
    result.validation_failures = list(
        (response.get("validation") or {}).get("failures") or []
    )
    result.output_guardrail = dict(final.get("output_guardrail") or {})
    result.degradations = list(final.get("degradations") or [])
    result.required_rules_fetched = list(final.get("required_rules_fetched") or [])
    return result


# ======================================================================== judging


def judge_case(result: CaseOutcome, judge: Any) -> dict[str, Any]:
    """Score one rationale with DeepEval, using Gemini as the judge.

    Skipped where there is nothing to judge — a case that errored, or one whose
    narrative fell back to the deterministic summary because the model was
    unreachable. Scoring a fallback summary would measure the fallback, not the
    system.
    """
    from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric
    from deepeval.test_case import LLMTestCase

    if result.error or not result.narrative or not result.evidence_texts:
        return {"judged": False, "reason": result.error or "no narrative or no evidence"}

    case = LLMTestCase(
        input=result.case.question,
        actual_output=result.narrative,
        retrieval_context=result.evidence_texts,
        context=result.evidence_texts,
    )

    scores: dict[str, Any] = {"judged": True}
    for key, metric in (
        ("faithfulness", FaithfulnessMetric(model=judge, async_mode=False, include_reason=True)),
        ("hallucination", HallucinationMetric(model=judge, async_mode=False, include_reason=True)),
        ("answer_relevancy", AnswerRelevancyMetric(model=judge, async_mode=False, include_reason=True)),
    ):
        try:
            metric.measure(case)
            scores[key] = round(float(metric.score), 4)
            scores[f"{key}_reason"] = (metric.reason or "")[:400]
        except Exception as exc:  # noqa: BLE001 - a judge failure is a data point
            scores[key] = None
            scores[f"{key}_reason"] = f"judge failed: {type(exc).__name__}: {str(exc)[:200]}"

    if scores.get("hallucination") is not None:
        scores["hallucination_rate"] = hallucination_rate_from(scores["hallucination"])
    return scores


def hallucination_rate_from(score: float) -> float:
    """Convert DeepEval's hallucination *score* into a *rate*.

    DeepEval 4.x reports hallucination in the same direction as every other
    metric — **1.0 means grounded**, 0.0 means contradicted — where it used to
    report the proportion of violations. Publishing the raw score under the name
    "hallucination rate" would therefore state the exact opposite of the truth: a
    perfectly grounded run would read as fully hallucinated.

    Both numbers are published, under names that say which is which.
    """
    return round(1.0 - float(score), 4)


# ==================================================================== aggregation


def _mean(values: Sequence[float]) -> float | None:
    clean = [v for v in values if v is not None]
    return round(statistics.fmean(clean), 4) if clean else None


def _rate(flags: Sequence[bool | None]) -> float | None:
    clean = [f for f in flags if f is not None]
    return round(sum(1 for f in clean if f) / len(clean), 4) if clean else None


def summarize(results: Sequence[CaseOutcome]) -> dict[str, Any]:
    """Metrics for one group of cases."""
    judged = [r for r in results if r.judge.get("judged")]
    ok = [r for r in results if not r.error]
    expressible = [r for r in ok if r.case.expressible]

    return {
        "cases": len(results),
        "completed": len(ok),
        "errors": len(results) - len(ok),
        "cases_with_inexpressible_expectation": len(ok) - len(expressible),
        # -- decision quality (deterministic) --------------------------------
        "outcome_accuracy": _rate([r.outcome_correct for r in expressible]),
        "outcome_accuracy_all_cases": _rate([r.outcome_correct for r in ok]),
        "directional_agreement": _rate([r.direction_correct for r in ok]),
        "human_review_agreement": _rate(
            [
                r.requires_human_review == r.case.expected_requires_human_review
                for r in ok
                if r.case.expected_requires_human_review is not None
            ]
        ),
        # -- routing (deterministic, and only measurable end to end) ----------
        # The Supervisor sees every case because the harness enters at `intake`.
        # A file routed to the other product's specialist would be assessed
        # against the wrong rulebook and every citation in the answer would
        # still resolve, so this is the one metric that catches it.
        "supervisor_routing_accuracy": _rate(
            [r.routed_to_correct_product for r in ok]
        ),
        "response_validation_pass_rate": _rate([r.response_validated for r in ok]),
        "runs_with_a_degraded_tool_call": sum(1 for r in ok if r.degradations),
        # -- grounding (deterministic) ---------------------------------------
        "citation_validity": _rate([r.all_citations_resolve for r in ok]),
        "citation_recall": _mean([r.citation_recall for r in ok]),
        "narrative_faithfulness_deterministic": _rate([r.narrative_faithful for r in ok]),
        # How many of those narratives a model actually wrote.
        #
        # Without it the faithfulness figure is unreadable. The deterministic
        # summary is *assembled from* the evidence rather than written about
        # it, so it cannot cite or quote anything the evidence does not
        # contain — it scores 1.00 by construction. A run where no model was
        # reachable therefore publishes a perfect grounding score that measures
        # the fallback, not the system. This is the denominator that says which
        # of the two you are looking at.
        "narratives_model_generated": sum(
            1 for r in ok if (r.usage or {}).get("output_tokens")
        ),
        "narratives_deterministic_fallback": sum(
            1 for r in ok if not (r.usage or {}).get("output_tokens")
        ),
        "unsupported_claim_rate": _rate(
            [bool(r.unsupported_citations or r.unsupported_figures) for r in ok]
        ),
        # -- grounding (LLM-as-judge) ----------------------------------------
        "judge_faithfulness": _mean([r.judge.get("faithfulness") for r in judged]),
        "judge_hallucination_score": _mean([r.judge.get("hallucination") for r in judged]),
        "judge_hallucination_rate": _mean([r.judge.get("hallucination_rate") for r in judged]),
        "judge_answer_relevancy": _mean([r.judge.get("answer_relevancy") for r in judged]),
        "judged_cases": len(judged),
        # -- cost and latency -------------------------------------------------
        "latency_ms_mean": _mean([r.latency_ms for r in ok]),
        "latency_ms_p50": round(statistics.median([r.latency_ms for r in ok]), 1) if ok else None,
        "latency_ms_p95": (
            round(sorted(r.latency_ms for r in ok)[max(0, int(len(ok) * 0.95) - 1)], 1)
            if ok else None
        ),
        "steps_taken_mean": _mean([float(r.steps_taken) for r in ok]),
        "halted_runs": sum(1 for r in ok if r.halted),
        "input_tokens_total": sum(r.usage.get("input_tokens", 0) for r in ok),
        "output_tokens_total": sum(r.usage.get("output_tokens", 0) for r in ok),
        "reasoning_tokens_total": sum(r.usage.get("reasoning_tokens", 0) for r in ok),
        "cost_usd_total": round(sum(r.cost_usd for r in ok), 6),
    }


#: Figures that macro-average across products. Counts are summed instead.
_MACRO_KEYS = (
    "supervisor_routing_accuracy",
    "response_validation_pass_rate",
    "outcome_accuracy",
    "outcome_accuracy_all_cases",
    "directional_agreement",
    "human_review_agreement",
    "citation_validity",
    "citation_recall",
    "narrative_faithfulness_deterministic",
    "unsupported_claim_rate",
    "judge_faithfulness",
    "judge_hallucination_score",
    "judge_hallucination_rate",
    "judge_answer_relevancy",
    "latency_ms_mean",
    "steps_taken_mean",
)

_SUM_KEYS = (
    "cases",
    "completed",
    "errors",
    "judged_cases",
    "narratives_model_generated",
    "narratives_deterministic_fallback",
    "halted_runs",
    "runs_with_a_degraded_tool_call",
    "cases_with_inexpressible_expectation",
    "input_tokens_total",
    "output_tokens_total",
    "reasoning_tokens_total",
)


def macro_average(per_product: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The unweighted mean across products, plus the summed counts."""
    groups = list(per_product.values())
    macro: dict[str, Any] = {}
    for key in _MACRO_KEYS:
        macro[key] = _mean([g.get(key) for g in groups])
    for key in _SUM_KEYS:
        macro[key] = sum(int(g.get(key) or 0) for g in groups)
    macro["cost_usd_total"] = round(sum(float(g.get("cost_usd_total") or 0) for g in groups), 6)
    return macro


# =========================================================================== main


def main(argv: Sequence[str] | None = None) -> int:
    use_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-per-product", type=int, default=None,
                        help="run only the first N cases of each product")
    parser.add_argument("--product", choices=["mortgage", "education"], default=None,
                        help="restrict to one product (macro averaging then has one group)")
    parser.add_argument("--no-judge", action="store_true",
                        help="deterministic metrics only; skip the LLM-as-judge pass")
    parser.add_argument("--judge-all", action="store_true",
                        help="judge every case — the mode for the final committed "
                             "run. Fails rather than silently sampling if the judge "
                             "is unreachable")
    parser.add_argument("--judge-limit-per-product", type=int, default=None,
                        help="judge only the first N cases of each product; the "
                             "deterministic metrics still cover every case. The "
                             "cheap mode, for local development")
    parser.add_argument("--output", default=str(REPORT_PATH))
    parser.add_argument("--cases-output", default=str(CASES_PATH))
    args = parser.parse_args(argv)

    products = None
    if args.product:
        products = [
            LendingProductDomain.MORTGAGE if args.product == "mortgage"
            else LendingProductDomain.EDUCATION_LOAN
        ]
    cases = load_cases(products, limit_per_product=args.limit_per_product)
    print(f"loaded {len(cases)} case(s)")

    from src import llm
    from src.graph import build_graph

    status = llm.probe()
    print(f"gemini: {status.as_dict()}")

    if args.judge_all and args.judge_limit_per_product is not None:
        parser.error("--judge-all and --judge-limit-per-product are contradictory")
    if args.judge_all and args.no_judge:
        parser.error("--judge-all and --no-judge are contradictory")

    judge = None
    judge_unavailable_reason: str | None = None
    if not args.no_judge:
        if not status.available:
            judge_unavailable_reason = status.reason
            if args.judge_all:
                # --judge-all is the mode for the final committed run, and a
                # final run that quietly produced deterministic-only figures
                # under a name promising judged ones is how a report comes to
                # claim more than it measured. Fail instead.
                print(
                    f"\n!! --judge-all was requested and the judge is unreachable: "
                    f"{status.reason}\n"
                    f"   Refusing to publish a run labelled 'every case judged' "
                    f"that judged none.\n"
                    f"   Set a working GOOGLE_API_KEY, or re-run with --no-judge "
                    f"for deterministic metrics only."
                )
                return 2
            print("!! the judge needs Gemini and it is unreachable; "
                  "running deterministic metrics only")
        else:
            from eval.agent.judges import GeminiJudge

            judge = GeminiJudge()
            print(f"judge:  {judge.get_model_name()}"
                  + (" (every case)" if args.judge_all else ""))

    run_id = uuid.uuid4().hex[:8]
    print(f"run id: {run_id}  (checkpoint threads are scoped to it, so nothing is replayed)")

    started = time.perf_counter()
    results: list[CaseOutcome] = []
    graph, context = build_graph()
    try:
        judged_per_product: dict[str, int] = {}
        for index, case in enumerate(cases, start=1):
            result = run_case(case, graph, run_id)

            product = case.product.value
            within_sample = (
                args.judge_limit_per_product is None
                or judged_per_product.get(product, 0) < args.judge_limit_per_product
            )
            if judge is not None and within_sample:
                result.judge = judge_case(result, judge)
                if result.judge.get("judged"):
                    judged_per_product[product] = judged_per_product.get(product, 0) + 1
            results.append(result)
            mark = "!" if result.error else ("x" if result.outcome_correct is False else ".")
            print(
                f"  [{index:>3}/{len(cases)}] {mark} {case.case_id:<18} "
                f"{case.product.value:<14} expected={case.expected_outcome or '-':<24} "
                f"got={result.outcome or '-':<10} "
                f"{result.latency_ms / 1000:.1f}s"
                + (f"  ERROR {result.error[:80]}" if result.error else "")
            )
    finally:
        if context is not None:
            context.__exit__(None, None, None)
    elapsed = time.perf_counter() - started

    per_product: dict[str, dict[str, Any]] = {}
    for product in sorted({r.case.product for r in results}, key=lambda p: p.value):
        group = [r for r in results if r.case.product is product]
        per_product[product.value] = summarize(group)

    config = get_config()
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id": run_id,
        "wall_clock_seconds": round(elapsed, 1),
        "harness": "deepeval",
        "deepeval_version": _deepeval_version(),
        "judge": {
            "provider": "google-gemini",
            "model": judge.get_model_name() if judge else None,
            "threshold": JUDGE_THRESHOLD,
            "mode": (
                "judge_all" if args.judge_all
                else "no_judge" if args.no_judge
                else "sampled" if args.judge_limit_per_product is not None
                else "all_reachable"
            ),
            "sampled": args.judge_limit_per_product is not None,
            "judge_limit_per_product": args.judge_limit_per_product,
            "available": judge is not None,
            "unavailable_reason": judge_unavailable_reason,
            "sampling_note": (
                "The deterministic metrics cover every case. The judged metrics cover "
                "a balanced sample, taken per product so neither dominates; "
                "judged_cases states the denominator for each."
                if args.judge_limit_per_product is not None
                else "Every case was judged."
                if judge is not None
                else (
                    "NO CASE WAS JUDGED. The judge was unreachable for this run "
                    f"({judge_unavailable_reason}), so every judge_* metric below is "
                    "null. They are not zero and they are not carried over from an "
                    "earlier run — they were not measured."
                )
            ),
            "caveat": (
                "The judge and the system under test are the same model family, so a "
                "shared blind spot would not show up here. Every judged figure has a "
                "deterministic counterpart in this report; where they disagree, trust "
                "the deterministic one."
            ),
            **(judge.usage if judge else {}),
            "judge_cost_usd": round(judge.cost_usd, 6) if judge else 0.0,
        },
        "system_under_test": {
            "llm_provider": "google-gemini",
            "llm_model": status.model,
            "llm_role": "narrative rationale only; no retrieval, arithmetic, "
                        "threshold or verdict is produced by a model",
            "embedding_model": config.embedding.model,
            "reranker_model": config.reranker.model if config.reranker.enabled else None,
            "final_top_k": config.retrieval.final_top_k,
        },
        "averaging": (
            "macro across products: mortgage contributes 75 cases to education's 20, "
            "so a pooled mean would be a mortgage score"
        ),
        "metric_notes": {
            "outcome_accuracy": (
                "exact outcome-family match, over cases whose expected outcome the "
                "system can express at all. Read it against rule_coverage: 40% of "
                "mortgage cases turn on a rule family the engine does not implement, "
                "which is the ceiling on this figure rather than an excuse for it"
            ),
            "outcome_accuracy_all_cases": (
                "the same match over every case, including the 6 expecting "
                "APPROVE_WITH_CONDITIONS, which the recommendation node cannot emit "
                "and therefore always misses"
            ),
            "directional_agreement": "positive / neutral / negative agreement, a softer test",
            "judge_hallucination_score": "DeepEval 4.x direction: 1.0 is grounded, 0.0 contradicted",
            "judge_hallucination_rate": "1 - score, so 0.0 is the good end",
            "narrative_faithfulness_deterministic": (
                "src.narrative.verify_narrative: no citation or figure in the prose "
                "that is absent from its evidence; asks no model anything. "
                "READ IT AGAINST narratives_model_generated. The deterministic "
                "fallback is assembled from the evidence rather than written about "
                "it, so it scores 1.00 by construction — a run with no model "
                "reachable publishes a perfect grounding figure that measures the "
                "fallback and not the system."
            ),
            "supervisor_routing_accuracy": (
                "did the Supervisor send each case to its own product's specialist. "
                "Measurable only because the harness enters the graph at intake; an "
                "evaluation starting at an internal node would not exercise routing "
                "at all"
            ),
            "response_validation_pass_rate": (
                "did the assembled response pass its own checks — citations resolve, "
                "figures supported, prose consistent with the recommendation — "
                "measured on the exact text that was published"
            ),
        },
        "rule_coverage": rule_coverage(),
        "macro": macro_average(per_product),
        "per_product": per_product,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cases_output = Path(args.cases_output)
    with cases_output.open("w", encoding="utf-8") as fh:
        for result in results:
            # Rounded on write only; `payload` above was aggregated from full
            # precision. A 17-significant-digit float in [0,1) is repr noise,
            # and about half of them contain a payment-card-shaped 16-digit
            # run, which buries any real leak in a PII scan.
            record = round_for_serialization(result.as_dict())
            fh.write(json.dumps(record, sort_keys=True, default=str) + "\n")

    macro = payload["macro"]
    print(f"\n{'=' * 72}")
    print(f"macro outcome accuracy (expressible) : {macro['outcome_accuracy']}")
    print(f"macro directional agreement          : {macro['directional_agreement']}")
    print(f"macro citation validity              : {macro['citation_validity']}")
    print(f"macro citation recall                : {macro['citation_recall']}")
    print(f"macro faithfulness (deterministic)   : {macro['narrative_faithfulness_deterministic']}")
    print(f"macro faithfulness (judge)           : {macro['judge_faithfulness']}")
    print(f"macro hallucination rate (judge)     : {macro['judge_hallucination_rate']}")
    print(f"macro answer relevancy (judge)       : {macro['judge_answer_relevancy']}")
    print(f"macro supervisor routing accuracy    : {macro['supervisor_routing_accuracy']}")
    print(f"macro response validation pass rate  : {macro['response_validation_pass_rate']}")
    print(f"errors                               : {macro['errors']}")
    if judge is None:
        print()
        print("!! no case was judged this run. Every judge_* figure is null, "
              "not zero.")
        if judge_unavailable_reason:
            print(f"   reason: {judge_unavailable_reason[:160]}")
    for product, coverage in payload["rule_coverage"].items():
        if not isinstance(coverage, dict):
            continue
        print(
            f"{product:<20} cases needing an unimplemented rule family : "
            f"{coverage['cases_needing_an_unimplemented_family']} of {coverage['cases']}"
        )
    print(f"wall clock                           : {elapsed:.0f}s")
    print(f"\nwrote {output}")
    print(f"wrote {cases_output}")
    return 0


def _deepeval_version() -> str | None:
    try:
        import deepeval

        return deepeval.__version__
    except Exception:  # noqa: BLE001
        return None


if __name__ == "__main__":
    raise SystemExit(main())
