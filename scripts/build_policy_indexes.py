#!/usr/bin/env python
"""Build both lending-policy indexes from the committed corpora.

    python scripts/build_policy_indexes.py

Runs from the repository root and, for each lending product in turn:

1. validates the corpus is present and parseable,
2. parses every policy document into rule-aware chunks,
3. encodes the chunks with the configured local Sentence-Transformers model,
4. rebuilds that product's Chroma collection from scratch,
5. rebuilds that product's BM25 lexical index,

then runs the cross-product integrity checks, writes the manifests and prints a
summary. Counts are measured from the corpus on disk, never hard-coded.

Exits non-zero if any integrity check fails, so a broken index cannot be
committed unnoticed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import get_config  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402
from src.rag.corpus_registry import write_registry  # noqa: E402
from src.rag.indexer import build_all_indexes  # noqa: E402
from src.rag.integrity import validate_indexes  # noqa: E402

INTEGRITY_REPORT_PATH = REPO_ROOT / "data" / "vectorstore" / "index_integrity.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--config", default=None, help="path to config/rag.yaml")
    parser.add_argument(
        "--progress", action="store_true", help="show the embedding progress bar"
    )
    parser.add_argument(
        "--skip-integrity", action="store_true", help="build without validating (not for CI)"
    )
    args = parser.parse_args(argv)

    use_utf8_stdio()
    config = get_config(args.config)

    print("CredPilot — building policy indexes")
    print(f"  embedding model : {config.embedding.model}")
    print(f"  vector store    : {config.vectorstore_path.relative_to(REPO_ROOT)}")
    print()

    report = build_all_indexes(config, show_progress=args.progress)

    for key in sorted(report.products):
        p = report.products[key]
        print(f"{p.product_domain.value}:")
        print(f"  corpus root       {p.corpus_root}")
        print(f"  source docs       {p.source_document_count}")
        print(f"  chunks            {p.chunk_count}"
              f"  (rule {p.rule_chunk_count} / section {p.section_chunk_count}"
              f" / overview {p.overview_chunk_count})")
        print(f"  policies / rules  {p.distinct_policy_ids} / {p.distinct_rule_ids}")
        print(f"  collection        {p.collection}")
        print(f"  embedding model   {config.embedding.model} "
              f"(dim {report.embedding['dimension']}, {report.embedding['encoding_convention']})")
        print(f"  timings (s)       parse {p.parse_seconds:.2f} · "
              f"embed {p.embed_seconds:.2f} · write {p.write_seconds:.2f}")
        print()

    registry_path = write_registry(config, report)
    print("Manifests:")
    print(f"  {report.manifest_path.relative_to(REPO_ROOT)}")
    print(f"  {registry_path.relative_to(REPO_ROOT)}")
    print()

    if args.skip_integrity:
        print("Integrity: SKIPPED (--skip-integrity)")
        return 0

    integrity = validate_indexes(config)
    integrity.write(INTEGRITY_REPORT_PATH)

    print("Integrity:")
    for key, metrics in sorted(integrity.metrics["products"].items()):
        print(
            f"  {key:<10} docs {metrics['indexed_source_count']}/{metrics['source_document_count']}"
            f" · rules {metrics['indexed_rule_count']}/{metrics['declared_rule_count']}"
            f" · chunks {metrics['chunk_count']}"
            f" · contamination {metrics['cross_product_contamination_rate']:.2f}"
            f" · citations resolvable {metrics['citation_validity']:.2f}"
        )
    print(
        f"  overall    cross_product_contamination_rate "
        f"{integrity.metrics['cross_product_contamination_rate']:.2f}"
        f" · citation_validity {integrity.metrics['citation_validity']:.2f}"
    )
    print(f"  {len(integrity.checks) - len(integrity.failures)}/{len(integrity.checks)} checks passed")
    print(f"  report → {INTEGRITY_REPORT_PATH.relative_to(REPO_ROOT)}")

    if integrity.failures:
        print()
        print("FAILED CHECKS:")
        for check in integrity.failures:
            print(f"  [FAIL] {check.name}: {check.detail}")
        return 1

    print()
    print("Build complete. Both product indexes are in place and isolated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
