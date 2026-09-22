#!/usr/bin/env python
"""Evaluate policy retrieval across both lending products.

    python eval/retrieval/run_retrieval_eval.py

Runs every evaluation case for both products through the live retrieval
pipeline, reports per-product and macro-averaged metrics, and writes machine
readable results to ``eval/results/retrieval_eval.json`` plus a per-case record
to ``eval/results/retrieval_eval_cases.jsonl``.

Both products are always evaluated. A run that only exercised mortgage would say
nothing about whether education retrieval works.

Two case families are scored separately, because they ask different questions:

* **authored** — targeted policy questions with rule-level ground truth, one to
  two relevant policies each. Recall@5 is well posed here, and this is the family
  the engineering targets are stated against.
* **golden-application** — one broad "which policy governs this file?" question
  per golden application, with every governing policy as ground truth. A mortgage
  file is governed by ~16 policies, so Recall@5 on this family is bounded above
  by ``5/16`` no matter how good the ranking is. It is reported with coverage
  (recall normalized by the achievable maximum) and at a larger ``top_k``, and is
  never used to claim a Recall@5 target was met.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.retrieval.dataset import load_cases  # noqa: E402
from eval.retrieval.metrics import round_for_serialization  # noqa: E402
from eval.retrieval.runner import (  # noqa: E402
    GOLDEN_KEYS,
    HEADLINE_KEYS,
    evaluate,
    macro_average,
)
from src.config import get_config  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402
from src.domain import LendingProductDomain  # noqa: E402
from src.observability.tracing import configure_tracing, flush_traces  # noqa: E402
from src.rag.pipeline import PolicyRetriever  # noqa: E402

RESULTS_DIR = REPO_ROOT / "eval" / "results"
RESULTS_PATH = RESULTS_DIR / "retrieval_eval.json"
CASES_PATH = RESULTS_DIR / "retrieval_eval_cases.jsonl"

#: Whole-file golden questions get more slots, because they legitimately have
#: more than six governing policies to surface.
GOLDEN_TOP_K = 15

#: Engineering targets for the authored family. These are goals this team set for
#: the retrieval subsystem, not requirements of the source document. They are
#: reported honestly whether met or missed.
TARGETS = {
    "policy_recall@5": 0.95,
    "rule_recall@5": 0.90,
    "citation_validity": 1.00,
    "cross_product_contamination": 0.00,
    "version_accuracy": 1.00,
}

_LOWER_IS_BETTER = {"cross_product_contamination", "wrong_version_rate", "no_result"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--top-k", type=int, default=None, help="override final_top_k")
    parser.add_argument("--golden-top-k", type=int, default=GOLDEN_TOP_K)
    parser.add_argument("--no-golden", action="store_true", help="authored cases only")
    parser.add_argument("--no-authored", action="store_true", help="golden cases only")
    parser.add_argument("--no-rerank", action="store_true", help="disable the cross-encoder")
    parser.add_argument("--trace", action="store_true", help="emit Phoenix spans for the run")
    parser.add_argument("--quiet", action="store_true", help="suppress per-case progress")
    parser.add_argument("--output", default=str(RESULTS_PATH))
    args = parser.parse_args(argv)

    use_utf8_stdio()
    config = get_config()
    if args.trace:
        configure_tracing()

    retriever = PolicyRetriever(config, enable_reranker=not args.no_rerank)

    print("CredPilot — retrieval evaluation")
    print(f"  embedding  {config.embedding.model}")
    print(f"  reranker   {config.reranker.model if not args.no_rerank else '(disabled)'}")
    print()

    authored_metrics: dict[str, dict] = {}
    golden_metrics: dict[str, dict] = {}
    all_outcomes = []

    for domain in LendingProductDomain:
        cases = load_cases(
            domain,
            include_authored=not args.no_authored,
            include_golden=not args.no_golden,
        )
        if not cases:
            print(f"{domain.value}: no cases found — skipping")
            continue

        authored = [c for c in cases if c.source == "authored"]
        golden = [c for c in cases if c.source == "golden"]

        if authored:
            metrics, outcomes = evaluate(
                retriever,
                authored,
                top_k=args.top_k,
                progress=_progress(args.quiet, domain, "authored"),
            )
            authored_metrics[domain.value] = metrics
            all_outcomes.extend(outcomes)
            _print_block(f"{domain.value} · authored", len(authored), metrics, HEADLINE_KEYS)

        if golden:
            metrics, outcomes = evaluate(
                retriever,
                golden,
                top_k=args.golden_top_k,
                progress=_progress(args.quiet, domain, "golden"),
            )
            golden_metrics[domain.value] = metrics
            all_outcomes.extend(outcomes)
            _print_block(
                f"{domain.value} · golden-application (top_k={args.golden_top_k})",
                len(golden),
                metrics,
                GOLDEN_KEYS,
            )

    macro_authored = macro_average(authored_metrics, HEADLINE_KEYS)
    macro_golden = macro_average(golden_metrics, GOLDEN_KEYS)

    if macro_authored:
        print("MACRO · authored (unweighted mean across products)")
        for key in sorted(macro_authored):
            print(f"  {key:<40} {macro_authored[key]:.4f}")
        print()
    if macro_golden:
        print("MACRO · golden-application (unweighted mean across products)")
        for key in sorted(macro_golden):
            print(f"  {key:<40} {macro_golden[key]:.4f}")
        print()

    met_all = _print_targets(macro_authored)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config": {
            "embedding_model": config.embedding.model,
            "reranker_model": config.reranker.model if not args.no_rerank else None,
            "reranker_enabled": not args.no_rerank,
            "retrieval": {
                "dense_top_k": config.retrieval.dense_top_k,
                "lexical_top_k": config.retrieval.lexical_top_k,
                "fusion_top_k": config.retrieval.fusion_top_k,
                "rerank_top_k": config.retrieval.rerank_top_k,
                "final_top_k": args.top_k or config.retrieval.final_top_k,
                "golden_top_k": args.golden_top_k,
                "rrf_k": config.retrieval.rrf_k,
                "query_expansion": config.retrieval.query_expansion,
            },
        },
        "targets": TARGETS,
        "targets_all_met": met_all,
        "authored": {"per_product": authored_metrics, "macro": macro_authored},
        "golden_application": {"per_product": golden_metrics, "macro": macro_golden},
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with CASES_PATH.open("w", encoding="utf-8") as fh:
        for outcome in all_outcomes:
            # Rounded on write only: the aggregates above were computed from
            # full precision. See `round_for_serialization`.
            record = round_for_serialization(outcome.as_dict())
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    if args.trace:
        flush_traces()

    print(f"Results  → {Path(args.output).relative_to(REPO_ROOT)}")
    print(f"Per-case → {CASES_PATH.relative_to(REPO_ROOT)}")
    return 0


def _progress(quiet: bool, domain: LendingProductDomain, family: str):
    def progress(index: int, total: int, case) -> None:
        if not quiet and (index % 25 == 0 or index == total):
            print(f"  {domain.value} {family}: {index}/{total}", flush=True)

    return progress


def _print_block(title: str, case_count: int, metrics: dict, keys) -> None:
    print(f"{title}  ({case_count} cases)")
    for key in keys:
        if key in metrics:
            print(f"  {key:<32} {metrics[key]:.4f}")
    print(f"  {'latency p50 / p95 (ms)':<32} "
          f"{metrics['latency_p50_ms']:.0f} / {metrics['latency_p95_ms']:.0f}")
    print(f"  {'statuses':<32} {metrics['status_counts']}")
    print()


def _print_targets(macro: dict) -> bool:
    print("Targets (authored family)")
    all_met = True
    for key, target in TARGETS.items():
        value = macro.get(f"macro_{key}")
        if value is None:
            print(f"  {key:<32} target {target:.2f}   not measured")
            continue
        met = value <= target if key in _LOWER_IS_BETTER else value >= target
        all_met = all_met and met
        print(
            f"  {key:<32} target {target:.2f}   measured {value:.4f}   "
            f"{'MET' if met else 'MISSED'}"
        )
    print()
    return all_met


if __name__ == "__main__":
    raise SystemExit(main())
