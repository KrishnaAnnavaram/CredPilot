#!/usr/bin/env python
"""Benchmark local embedding models against both lending products.

    python eval/retrieval/benchmark_embeddings.py

For each candidate checkpoint this builds a throwaway index over both corpora,
runs every authored evaluation case through the full pipeline, and records
retrieval quality, build cost and index size. Results go to
``eval/results/embedding_benchmark.json``.

The model committed in ``config/rag.yaml`` has to be justified by this file. The
largest model is not chosen automatically, and neither is the smallest: the
decision rule is macro-averaged rule-level Recall@5 first, then macro MRR, with
latency and index size as tie-breakers.

**Macro, not micro.** Mortgage has 329 chunks and 108 authored cases against
education's 101 and 74. Averaging over cases would let mortgage performance stand
in for the system's; averaging over products does not.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.retrieval.dataset import load_cases  # noqa: E402
from eval.retrieval.harness import (  # noqa: E402
    build_temporary_indexes,
    directory_size_mb,
    temporary_config,
)
from eval.retrieval.runner import HEADLINE_KEYS, evaluate, macro_average  # noqa: E402
from src.config import get_config  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402
from src.domain import LendingProductDomain  # noqa: E402
from src.rag.embedding import PolicyEmbedder, convention_for  # noqa: E402
from src.rag.pipeline import PolicyRetriever  # noqa: E402

RESULTS_PATH = REPO_ROOT / "eval" / "results" / "embedding_benchmark.json"

#: Ranked decision rule. Quality first; cost breaks ties.
DECIDING = ("macro_rule_recall@5", "macro_rule_mrr@10", "macro_policy_recall@5")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--models", nargs="*", default=None, help="override the candidate list")
    parser.add_argument("--no-rerank", action="store_true", help="isolate the embedding")
    parser.add_argument("--output", default=str(RESULTS_PATH))
    parser.add_argument("--keep", action="store_true", help="keep the temporary indexes")
    args = parser.parse_args(argv)

    use_utf8_stdio()
    base = get_config()
    models = args.models or base.benchmark.get("embedding_models") or [base.embedding.model]

    cases = {d: load_cases(d, include_golden=False) for d in LendingProductDomain}
    total_cases = sum(len(v) for v in cases.values())

    print("CredPilot — embedding benchmark")
    print(f"  candidates {len(models)}")
    print(f"  cases      {total_cases} authored "
          f"({', '.join(f'{d.value}={len(v)}' for d, v in cases.items())})")
    print(f"  reranker   {'(disabled)' if args.no_rerank else base.reranker.model}")
    print()

    rows = []
    for model in models:
        print(f"[{model}]", flush=True)
        row = benchmark_model(base, model, cases, use_reranker=not args.no_rerank, keep=args.keep)
        rows.append(row)
        if "error" in row:
            print(f"  FAILED: {row['error']}")
            print()
            continue
        macro = row["macro"]
        print(
            f"  dim {row['dimension']:<4} build {row['build_seconds']:.1f}s  "
            f"index {row['index_size_mb']:.1f} MB  p95 {row['latency_p95_ms']:.0f} ms"
        )
        for domain, metrics in sorted(row["per_product"].items()):
            print(
                f"    {domain:<15} rule R@5 {metrics['rule_recall@5']:.4f}  "
                f"policy R@5 {metrics['policy_recall@5']:.4f}  "
                f"rule MRR {metrics['rule_mrr@10']:.4f}  "
                f"nDCG {metrics['rule_ndcg@10']:.4f}"
            )
        print(
            f"    {'MACRO':<15} rule R@5 {macro.get('macro_rule_recall@5', 0):.4f}  "
            f"policy R@5 {macro.get('macro_policy_recall@5', 0):.4f}  "
            f"rule MRR {macro.get('macro_rule_mrr@10', 0):.4f}"
        )
        print()

    scored = [r for r in rows if "error" not in r]
    if not scored:
        print("no candidate completed")
        return 1

    best = max(scored, key=lambda r: tuple(r["macro"].get(k, 0.0) for k in DECIDING))
    print(f"Selected: {best['model']}")
    print(f"  on {DECIDING[0]} = {best['macro'].get(DECIDING[0], 0):.4f}")
    if best["model"] != base.embedding.model:
        print(f"  NOTE: config/rag.yaml currently specifies {base.embedding.model}")

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "deciding_metrics": list(DECIDING),
        "reranker": None if args.no_rerank else base.reranker.model,
        "case_counts": {d.value: len(v) for d, v in cases.items()},
        "configured_model": base.embedding.model,
        "selected_model": best["model"],
        "candidates": rows,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Results → {Path(args.output).relative_to(REPO_ROOT)}")
    return 0


def benchmark_model(base, model: str, cases, *, use_reranker: bool, keep: bool) -> dict:
    """Build an index with one model and evaluate it over both products."""
    workspace = REPO_ROOT / "data" / "benchmark" / _slug(model)
    if workspace.exists():
        shutil.rmtree(workspace)

    try:
        embedder = PolicyEmbedder(model, batch_size=base.embedding.batch_size)
        dimension = embedder.dimension
        config = temporary_config(base, workspace, embedding_model=model, dimension=dimension)

        started = time.perf_counter()
        build = build_temporary_indexes(config, embedder)
        build_seconds = time.perf_counter() - started

        retriever = PolicyRetriever(config, embedder=embedder, enable_reranker=use_reranker)
        per_product = {}
        for domain, domain_cases in cases.items():
            if not domain_cases:
                continue
            metrics, _ = evaluate(retriever, domain_cases)
            per_product[domain.value] = metrics

        return {
            "model": model,
            "dimension": dimension,
            "encoding_convention": convention_for(model).describe(),
            "normalize": embedder.normalize,
            "build_seconds": round(build_seconds, 2),
            "chunk_count": sum(p.chunk_count for p in build.products.values()),
            "index_size_mb": round(directory_size_mb(workspace), 2),
            "latency_p50_ms": max(m["latency_p50_ms"] for m in per_product.values()),
            "latency_p95_ms": max(m["latency_p95_ms"] for m in per_product.values()),
            "per_product": per_product,
            "macro": macro_average(per_product, HEADLINE_KEYS),
        }
    except Exception as exc:  # noqa: BLE001 - one bad checkpoint must not end the sweep
        return {"model": model, "error": f"{type(exc).__name__}: {exc}"}
    finally:
        if not keep and workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)


def _slug(model: str) -> str:
    return model.replace("/", "__").replace(".", "_")


if __name__ == "__main__":
    raise SystemExit(main())
