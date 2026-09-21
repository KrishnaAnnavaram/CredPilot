#!/usr/bin/env python
"""Sweep the retrieval funnel widths against the authored evaluation sets.

    python eval/retrieval/sweep_pipeline.py

The funnel has four widths — dense candidates, lexical candidates, how many
survive fusion, how many the cross-encoder scores — and each one trades recall
for latency. This sweeps them over both products and writes the measurements to
``eval/results/pipeline_sweep.json`` so the values committed in ``config/rag.yaml``
are a result rather than a guess.
"""

from __future__ import annotations

import argparse
import dataclasses
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

RESULTS_PATH = REPO_ROOT / "eval" / "results" / "pipeline_sweep.json"

#: (dense_top_k, lexical_top_k, fusion_top_k, rerank_top_k)
FUNNELS: tuple[tuple[int, int, int, int], ...] = (
    (15, 15, 12, 10),
    (25, 25, 20, 15),
    (30, 30, 30, 20),
    (40, 40, 40, 25),
    (50, 50, 50, 35),
    (60, 60, 60, 50),
)

#: Metrics that decide the winner, in priority order.
DECIDING = ("macro_rule_recall@5", "macro_policy_recall@5", "macro_rule_mrr@10")


def with_funnel(config, dense: int, lexical: int, fusion: int, rerank: int):
    retrieval = dataclasses.replace(
        config.retrieval,
        dense_top_k=dense,
        lexical_top_k=lexical,
        fusion_top_k=fusion,
        rerank_top_k=rerank,
    )
    return dataclasses.replace(config, retrieval=retrieval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output", default=str(RESULTS_PATH))
    args = parser.parse_args(argv)

    use_utf8_stdio()
    base = get_config()

    cases = {
        domain: load_cases(domain, include_golden=False) for domain in LendingProductDomain
    }
    total = sum(len(v) for v in cases.values())
    print(f"CredPilot — retrieval funnel sweep ({total} authored cases, "
          f"{len(FUNNELS)} configurations)")
    print()

    rows = []
    for dense, lexical, fusion, rerank in FUNNELS:
        config = with_funnel(base, dense, lexical, fusion, rerank)
        retriever = PolicyRetriever(config)
        per_domain = {}
        started = time.perf_counter()
        for domain, domain_cases in cases.items():
            if not domain_cases:
                continue
            metrics, _ = evaluate(retriever, domain_cases)
            per_domain[domain.value] = metrics
        elapsed = time.perf_counter() - started
        macro = macro_average(per_domain, HEADLINE_KEYS)
        latency_p95 = max(m["latency_p95_ms"] for m in per_domain.values())
        row = {
            "dense_top_k": dense,
            "lexical_top_k": lexical,
            "fusion_top_k": fusion,
            "rerank_top_k": rerank,
            "macro": macro,
            "latency_p95_ms": round(latency_p95, 1),
            "wall_seconds": round(elapsed, 1),
            "per_product": per_domain,
        }
        rows.append(row)
        print(
            f"  dense {dense:>2} · lex {lexical:>2} · fuse {fusion:>2} · rerank {rerank:>2}"
            f"  →  rule R@5 {macro.get('macro_rule_recall@5', 0):.4f}"
            f"  policy R@5 {macro.get('macro_policy_recall@5', 0):.4f}"
            f"  rule MRR {macro.get('macro_rule_mrr@10', 0):.4f}"
            f"  p95 {latency_p95:.0f} ms",
            flush=True,
        )

    best = max(rows, key=lambda r: tuple(r["macro"].get(k, 0.0) for k in DECIDING))
    print()
    print(
        f"Best on {DECIDING[0]}: dense {best['dense_top_k']} · lexical {best['lexical_top_k']} "
        f"· fusion {best['fusion_top_k']} · rerank {best['rerank_top_k']} "
        f"(p95 {best['latency_p95_ms']:.0f} ms)"
    )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "embedding_model": base.embedding.model,
        "reranker_model": base.reranker.model,
        "case_count": total,
        "deciding_metrics": list(DECIDING),
        "configurations": rows,
        "best": {k: best[k] for k in ("dense_top_k", "lexical_top_k", "fusion_top_k", "rerank_top_k")},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Results → {Path(args.output).relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
