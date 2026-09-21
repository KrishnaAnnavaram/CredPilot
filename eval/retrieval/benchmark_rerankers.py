#!/usr/bin/env python
"""Benchmark local cross-encoder rerankers against both lending products.

    python eval/retrieval/benchmark_rerankers.py

The embedding model and the index are held fixed; only the reranker changes, so
the difference measured is the reranker's. A no-reranker baseline runs first, so
the question "does reranking earn its latency at all?" gets an answer rather than
an assumption.

Results go to ``eval/results/reranker_benchmark.json``. No hosted reranking
service is contacted; every candidate runs locally through
``sentence-transformers``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.retrieval.dataset import load_cases  # noqa: E402
from eval.retrieval.runner import HEADLINE_KEYS, evaluate, macro_average  # noqa: E402
from src.config import get_config  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402
from src.domain import LendingProductDomain  # noqa: E402
from src.rag.pipeline import PolicyRetriever  # noqa: E402
from src.rag.rerank import CrossEncoderReranker  # noqa: E402

RESULTS_PATH = REPO_ROOT / "eval" / "results" / "reranker_benchmark.json"

DECIDING = ("macro_rule_recall@5", "macro_rule_mrr@10", "macro_rule_ndcg@10")

#: A heavier reranker has to beat the lightweight one by more than this on the
#: deciding metric to be worth its extra latency.
MATERIAL_GAIN = 0.01


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--output", default=str(RESULTS_PATH))
    args = parser.parse_args(argv)

    use_utf8_stdio()
    config = get_config()
    if not config.manifest_path.exists():
        print("indexes not built; run 'python scripts/build_policy_indexes.py' first")
        return 1

    models = args.models or config.benchmark.get("reranker_models") or [config.reranker.model]
    cases = {d: load_cases(d, include_golden=False) for d in LendingProductDomain}

    print("CredPilot — reranker benchmark")
    print(f"  embedding  {config.embedding.model} (held fixed)")
    print(f"  candidates {len(models)} plus a no-reranker baseline")
    print()

    rows = [_run(config, None, cases)]
    _print_row(rows[0])
    for model in models:
        rows.append(_run(config, model, cases))
        _print_row(rows[-1])

    scored = [r for r in rows if "error" not in r]
    baseline = next(r for r in scored if r["model"] is None)
    ranked = [r for r in scored if r["model"] is not None]
    if not ranked:
        print("no reranker completed")
        return 1

    best = max(ranked, key=lambda r: tuple(r["macro"].get(k, 0.0) for k in DECIDING))
    lightest = min(ranked, key=lambda r: r["latency_p95_ms"])

    baseline_score = baseline["macro"].get(DECIDING[0], 0.0)
    best_score = best["macro"].get(DECIDING[0], 0.0)
    lightest_score = lightest["macro"].get(DECIDING[0], 0.0)

    print("Decision")
    print(f"  no reranker         {DECIDING[0]} = {baseline_score:.4f}")
    print(f"  best   {best['model']:<38} = {best_score:.4f} "
          f"(p95 {best['latency_p95_ms']:.0f} ms)")
    print(f"  fastest {lightest['model']:<37} = {lightest_score:.4f} "
          f"(p95 {lightest['latency_p95_ms']:.0f} ms)")

    if best_score - baseline_score < MATERIAL_GAIN:
        selected = None
        rationale = (
            f"no reranker improves {DECIDING[0]} by the {MATERIAL_GAIN:.2f} needed to "
            f"justify its latency; reranking is not carrying its weight here"
        )
    elif best is lightest:
        selected = best["model"]
        rationale = (
            f"{best['model']} is both the most accurate and the fastest candidate — "
            f"{DECIDING[0]} {best_score:.4f} against {baseline_score:.4f} with no "
            f"reranker (+{best_score - baseline_score:.4f}), at "
            f"{best['latency_p95_ms']:.0f} ms p95. No trade-off to make"
        )
    elif (best_score - lightest_score) < MATERIAL_GAIN:
        selected = lightest["model"]
        rationale = (
            f"{best['model']} leads by only {best_score - lightest_score:.4f}, under the "
            f"{MATERIAL_GAIN:.2f} materiality bar, so the lighter model is preferred "
            f"({lightest['latency_p95_ms']:.0f} ms vs {best['latency_p95_ms']:.0f} ms p95)"
        )
    else:
        selected = best["model"]
        rationale = (
            f"{best['model']} leads by {best_score - lightest_score:.4f} on {DECIDING[0]}, "
            f"a material gain over the lightest candidate "
            f"({best['latency_p95_ms']:.0f} ms vs {lightest['latency_p95_ms']:.0f} ms p95)"
        )

    print()
    print(f"Selected: {selected or '(none — disable reranking)'}")
    print(f"  {rationale}")
    if selected and selected != config.reranker.model:
        print(f"  NOTE: config/rag.yaml currently specifies {config.reranker.model}")

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "embedding_model": config.embedding.model,
        "deciding_metrics": list(DECIDING),
        "materiality_threshold": MATERIAL_GAIN,
        "configured_model": config.reranker.model,
        "selected_model": selected,
        "rationale": rationale,
        "case_counts": {d.value: len(v) for d, v in cases.items()},
        "candidates": rows,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Results → {Path(args.output).relative_to(REPO_ROOT)}")
    return 0


def _run(config, model: str | None, cases) -> dict:
    label = model or "(no reranker)"
    print(f"[{label}]", flush=True)
    try:
        started = time.perf_counter()
        reranker = CrossEncoderReranker(model, batch_size=config.reranker.batch_size) if model else None
        if reranker is not None:
            reranker.score("warm up", ["a passage to warm the model"])
        load_seconds = time.perf_counter() - started

        retriever = PolicyRetriever(
            config, reranker=reranker, enable_reranker=reranker is not None
        )
        per_product = {}
        for domain, domain_cases in cases.items():
            if not domain_cases:
                continue
            metrics, _ = evaluate(retriever, domain_cases)
            per_product[domain.value] = metrics

        return {
            "model": model,
            "load_seconds": round(load_seconds, 2),
            "latency_p50_ms": max(m["latency_p50_ms"] for m in per_product.values()),
            "latency_p95_ms": max(m["latency_p95_ms"] for m in per_product.values()),
            "per_product": per_product,
            "macro": macro_average(per_product, HEADLINE_KEYS),
        }
    except Exception as exc:  # noqa: BLE001
        return {"model": model, "error": f"{type(exc).__name__}: {exc}"}


def _print_row(row: dict) -> None:
    if "error" in row:
        print(f"  FAILED: {row['error']}")
        print()
        return
    for domain, metrics in sorted(row["per_product"].items()):
        print(
            f"    {domain:<15} rule R@5 {metrics['rule_recall@5']:.4f}  "
            f"rule MRR {metrics['rule_mrr@10']:.4f}  "
            f"nDCG {metrics['rule_ndcg@10']:.4f}  "
            f"policy R@5 {metrics['policy_recall@5']:.4f}"
        )
    macro = row["macro"]
    print(
        f"    {'MACRO':<15} rule R@5 {macro.get('macro_rule_recall@5', 0):.4f}  "
        f"rule MRR {macro.get('macro_rule_mrr@10', 0):.4f}  "
        f"p95 {row['latency_p95_ms']:.0f} ms"
    )
    print()


if __name__ == "__main__":
    raise SystemExit(main())
