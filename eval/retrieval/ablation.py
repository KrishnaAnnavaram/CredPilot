#!/usr/bin/env python
"""Ablation study: what each retrieval layer is actually worth.

    python eval/retrieval/ablation.py

Six configurations, both products, same cases, same index:

    A. BM25 only
    B. Dense only
    C. Dense + BM25, scores concatenated without fusion
    D. Dense + BM25 + RRF
    E. Dense + BM25 + RRF + cross-encoder reranking
    F. Full pipeline: E plus product isolation, effective-date filtering,
       deterministic query expansion and deduplication

Results go to ``eval/results/retrieval_ablation.json``. A layer that shows no
gain is reported as showing no gain — the point of the study is to find out, and
a component that earns nothing should either be removed or have its reason for
staying written down.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.retrieval.dataset import load_cases  # noqa: E402
from eval.retrieval.runner import HEADLINE_KEYS, evaluate, macro_average  # noqa: E402
from src.config import get_config  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402
from src.domain import LendingProductDomain  # noqa: E402
from src.rag.pipeline import PolicyRetriever  # noqa: E402

RESULTS_PATH = REPO_ROOT / "eval" / "results" / "retrieval_ablation.json"

REPORTED = (
    "macro_rule_recall@5",
    "macro_rule_recall@10",
    "macro_policy_recall@5",
    "macro_rule_mrr@10",
    "macro_rule_ndcg@10",
    "macro_citation_validity",
    "macro_cross_product_contamination",
    "macro_no_result",
)


class AblatedRetriever(PolicyRetriever):
    """A retriever with individual layers switched off.

    Subclassing rather than parameterizing keeps the production path free of
    flags that exist only for the study.
    """

    def __init__(self, *args, use_dense=True, use_lexical=True, use_fusion=True,
                 use_expansion=True, use_temporal=True, use_dedupe=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_dense = use_dense
        self.use_lexical = use_lexical
        self.use_fusion = use_fusion
        self.use_expansion = use_expansion
        self.use_temporal = use_temporal
        self.use_dedupe = use_dedupe

    def _dense_search(self, domain, query_vector, top_k, allowed_ids):
        if not self.use_dense:
            return []
        return super()._dense_search(domain, query_vector, top_k, allowed_ids)

    def lexical(self, domain):
        index = super().lexical(domain)
        if self.use_lexical:
            return index
        return _EmptyLexical(index)

    def _allowed_chunk_ids(self, domain, as_of, temporal_filtering):
        if not self.use_temporal:
            # Still needs the catalogue size, but applies no filter.
            _, _, size = super()._allowed_chunk_ids(domain, None, False)
            return None, {}, size
        return super()._allowed_chunk_ids(domain, as_of, temporal_filtering)

    def _validate_temporal(self, ranked, as_of, governing, temporal_filtering):
        if not self.use_temporal:
            return super()._validate_temporal(ranked, None, {}, False)
        return super()._validate_temporal(ranked, as_of, governing, temporal_filtering)

    def _dedupe(self, ranked, top_k):
        if not self.use_dedupe:
            return list(ranked)[:top_k]
        return super()._dedupe(ranked, top_k)


class _EmptyLexical:
    """A BM25 index that finds nothing, but still reports the catalogue."""

    def __init__(self, inner):
        self.chunk_ids = inner.chunk_ids
        self.metadatas = inner.metadatas
        self.domain = inner.domain

    def search(self, *args, **kwargs):
        return []


def _config_for(base, *, use_expansion=True, use_fusion=True):
    """Config variants the layers read from rather than from flags."""
    retrieval = dataclasses.replace(
        base.retrieval,
        query_expansion=use_expansion,
        # Without fusion, one list is simply concatenated after the other; giving
        # the lexical list a much smaller weight approximates "no rank fusion,
        # dense first" without changing the pipeline's shape.
        lexical_weight=base.retrieval.lexical_weight if use_fusion else 0.001,
    )
    return dataclasses.replace(base, retrieval=retrieval)


CONFIGURATIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "A",
        "name": "BM25 only",
        "description": "Lexical retrieval alone. No embedding is consulted.",
        "flags": dict(use_dense=False, use_lexical=True, use_fusion=False,
                      use_expansion=False, use_temporal=False, use_dedupe=False),
        "reranker": False,
    },
    {
        "id": "B",
        "name": "Dense only",
        "description": "Vector similarity alone. No lexical signal.",
        "flags": dict(use_dense=True, use_lexical=False, use_fusion=False,
                      use_expansion=False, use_temporal=False, use_dedupe=False),
        "reranker": False,
    },
    {
        "id": "C",
        "name": "Dense + BM25, no fusion",
        "description": "Both layers run; the dense ranking dominates the order.",
        "flags": dict(use_dense=True, use_lexical=True, use_fusion=False,
                      use_expansion=False, use_temporal=False, use_dedupe=False),
        "reranker": False,
    },
    {
        "id": "D",
        "name": "Dense + BM25 + RRF",
        "description": "Reciprocal rank fusion combines the two rankings.",
        "flags": dict(use_dense=True, use_lexical=True, use_fusion=True,
                      use_expansion=False, use_temporal=False, use_dedupe=False),
        "reranker": False,
    },
    {
        "id": "E",
        "name": "D + cross-encoder rerank",
        "description": "The cross-encoder reorders the fused candidates.",
        "flags": dict(use_dense=True, use_lexical=True, use_fusion=True,
                      use_expansion=False, use_temporal=False, use_dedupe=False),
        "reranker": True,
    },
    {
        "id": "F",
        "name": "Full pipeline",
        "description": (
            "E plus deterministic query expansion, effective-date filtering and "
            "deduplication. This is what ships."
        ),
        "flags": dict(use_dense=True, use_lexical=True, use_fusion=True,
                      use_expansion=True, use_temporal=True, use_dedupe=True),
        "reranker": True,
    },
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output", default=str(RESULTS_PATH))
    parser.add_argument("--only", nargs="*", default=None, help="run only these ids")
    args = parser.parse_args(argv)

    use_utf8_stdio()
    base = get_config()
    if not base.manifest_path.exists():
        print("indexes not built; run 'python scripts/build_policy_indexes.py' first")
        return 1

    cases = {d: load_cases(d, include_golden=False) for d in LendingProductDomain}
    total = sum(len(v) for v in cases.values())

    print("CredPilot — retrieval ablation")
    print(f"  cases      {total} authored")
    print(f"  embedding  {base.embedding.model}")
    print(f"  reranker   {base.reranker.model}")
    print()

    rows = []
    for spec in CONFIGURATIONS:
        if args.only and spec["id"] not in args.only:
            continue
        print(f"[{spec['id']}] {spec['name']}", flush=True)
        config = _config_for(
            base,
            use_expansion=spec["flags"]["use_expansion"],
            use_fusion=spec["flags"]["use_fusion"],
        )
        retriever = AblatedRetriever(
            config, enable_reranker=spec["reranker"], **spec["flags"]
        )
        per_product = {}
        for domain, domain_cases in cases.items():
            if not domain_cases:
                continue
            metrics, _ = evaluate(retriever, domain_cases)
            per_product[domain.value] = metrics

        macro = macro_average(per_product, HEADLINE_KEYS)
        row = {
            "id": spec["id"],
            "name": spec["name"],
            "description": spec["description"],
            "layers": {**spec["flags"], "reranker": spec["reranker"]},
            "per_product": per_product,
            "macro": macro,
            "latency_p50_ms": max(m["latency_p50_ms"] for m in per_product.values()),
            "latency_p95_ms": max(m["latency_p95_ms"] for m in per_product.values()),
        }
        rows.append(row)
        print(
            f"    rule R@5 {macro.get('macro_rule_recall@5', 0):.4f}  "
            f"policy R@5 {macro.get('macro_policy_recall@5', 0):.4f}  "
            f"rule MRR {macro.get('macro_rule_mrr@10', 0):.4f}  "
            f"nDCG {macro.get('macro_rule_ndcg@10', 0):.4f}  "
            f"p95 {row['latency_p95_ms']:.0f} ms"
        )
        print()

    _print_deltas(rows)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "embedding_model": base.embedding.model,
        "reranker_model": base.reranker.model,
        "case_counts": {d.value: len(v) for d, v in cases.items()},
        "reported_metrics": list(REPORTED),
        "configurations": rows,
        "deltas": _deltas(rows),
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Results → {Path(args.output).relative_to(REPO_ROOT)}")
    return 0


def _deltas(rows: Sequence[dict]) -> list[dict]:
    """What each step added over the one before it."""
    out = []
    for previous, current in zip(rows, rows[1:]):
        out.append(
            {
                "from": previous["id"],
                "to": current["id"],
                "step": current["name"],
                "delta": {
                    key: round(
                        current["macro"].get(key, 0.0) - previous["macro"].get(key, 0.0), 4
                    )
                    for key in REPORTED
                },
                "latency_p95_delta_ms": round(
                    current["latency_p95_ms"] - previous["latency_p95_ms"], 1
                ),
            }
        )
    return out


def _print_deltas(rows: Sequence[dict]) -> None:
    if len(rows) < 2:
        return
    print("Incremental contribution (macro rule Recall@5 / rule MRR@10 / p95 ms)")
    for delta in _deltas(rows):
        print(
            f"  {delta['from']} -> {delta['to']}  {delta['step']:<34} "
            f"{delta['delta']['macro_rule_recall@5']:+.4f}  "
            f"{delta['delta']['macro_rule_mrr@10']:+.4f}  "
            f"{delta['latency_p95_delta_ms']:+.0f}"
        )
    print()


if __name__ == "__main__":
    raise SystemExit(main())
