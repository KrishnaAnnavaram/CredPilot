"""Deterministic index construction for both policy corpora.

A build is a full, safe rebuild: each product's Chroma collection is dropped and
recreated from the committed corpus. Incremental indexing is not worth its risk
here — the corpora are 54 documents totalling a few hundred chunks, a rebuild
takes seconds, and a stale embedding left behind by a partial update would be a
silent correctness failure in an underwriting decision.

Every build writes a manifest recording what was indexed, from which files, at
which content hashes, with which model — so a later run can prove the index still
matches the corpus.
"""

from __future__ import annotations

import json
import platform
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from src.config import REPO_ROOT, RagConfig, get_config
from src.domain import LendingProductDomain
from src.rag.embedding import PolicyEmbedder
from src.rag.lexical import BM25Index
from src.rag.models import PolicyChunk
from src.rag.parsers import ParsedPolicy, get_parser
from src.rag.vectorstore import PolicyVectorStore

MANIFEST_SCHEMA_VERSION = 2


def _rel_to_repo(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:  # pragma: no cover
        return path.as_posix()


@dataclass
class ProductBuildReport:
    """What one product's build produced."""

    product_domain: LendingProductDomain
    collection: str
    corpus_root: str
    source_document_count: int
    chunk_count: int
    rule_chunk_count: int
    section_chunk_count: int
    overview_chunk_count: int
    distinct_policy_ids: int
    distinct_rule_ids: int
    parse_seconds: float
    embed_seconds: float
    write_seconds: float
    documents: list[dict[str, Any]] = field(default_factory=list)
    chunks: list[PolicyChunk] = field(default_factory=list)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "product_domain": self.product_domain.value,
            "collection_name": self.collection,
            "corpus_root": self.corpus_root,
            "source_document_count": self.source_document_count,
            "chunk_count": self.chunk_count,
            "chunk_kinds": {
                "RULE": self.rule_chunk_count,
                "SECTION": self.section_chunk_count,
                "OVERVIEW": self.overview_chunk_count,
            },
            "distinct_policy_ids": self.distinct_policy_ids,
            "distinct_rule_ids": self.distinct_rule_ids,
            "documents": self.documents,
        }


@dataclass
class BuildReport:
    """The outcome of a whole build, across every product."""

    products: dict[str, ProductBuildReport]
    embedding: dict[str, Any]
    reranker: dict[str, Any]
    config_snapshot: dict[str, Any]
    total_seconds: float
    manifest_path: Path | None = None

    def manifest(self) -> dict[str, Any]:
        return {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "index_version": datetime.now(timezone.utc).strftime("%Y%m%d"),
            "embedding": self.embedding,
            "reranker": self.reranker,
            "build": {
                "python": sys.version.split()[0],
                "platform": platform.system(),
                "total_seconds": round(self.total_seconds, 3),
            },
            "config": self.config_snapshot,
            "products": {k: v.to_manifest() for k, v in sorted(self.products.items())},
        }


def _document_record(parsed: ParsedPolicy, chunks: Sequence[PolicyChunk]) -> dict[str, Any]:
    mine = [c for c in chunks if c.source_path == parsed.source_path]
    return {
        "policy_id": parsed.policy_id,
        "policy_version": parsed.policy_version,
        "policy_title": parsed.policy_title,
        "source_path": parsed.source_path,
        "source_sha256": parsed.source_sha256,
        "chunk_count": len(mine),
        "rule_ids": sorted({c.rule_id for c in mine if c.rule_id}),
        "chunk_ids": sorted(c.chunk_id for c in mine),
    }


def build_product_index(
    config: RagConfig,
    product_key: str,
    *,
    embedder: PolicyEmbedder,
    show_progress: bool = False,
) -> ProductBuildReport:
    """Parse, chunk, embed and index one product's policy corpus."""
    product = config.products[product_key]

    t0 = time.perf_counter()
    parser = get_parser(
        product.parser,
        max_chars=config.chunking.max_chars,
        overlap_chars=config.chunking.split_overlap_chars,
        min_chars=config.chunking.min_chars,
    )
    chunks, parsed_docs = parser.parse_corpus(product.corpus_root)
    parse_seconds = time.perf_counter() - t0

    ids = [c.chunk_id for c in chunks]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise ValueError(f"{product_key}: duplicate chunk ids {sorted(duplicates)[:5]}")

    t0 = time.perf_counter()
    embeddings = embedder.encode_passages(
        [c.embedding_text() for c in chunks], show_progress=show_progress
    )
    embed_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    store = PolicyVectorStore(config, product.domain)
    store.reset()
    store.add_chunks(chunks, embeddings)

    lexical = BM25Index.build(product.domain, chunks)
    lexical.save(BM25Index.path_for(config, product.domain))
    write_seconds = time.perf_counter() - t0

    return ProductBuildReport(
        product_domain=product.domain,
        collection=product.collection,
        corpus_root=_rel_to_repo(product.corpus_root),
        source_document_count=len(parsed_docs),
        chunk_count=len(chunks),
        rule_chunk_count=sum(1 for c in chunks if c.chunk_kind.value == "RULE"),
        section_chunk_count=sum(1 for c in chunks if c.chunk_kind.value == "SECTION"),
        overview_chunk_count=sum(1 for c in chunks if c.chunk_kind.value == "OVERVIEW"),
        distinct_policy_ids=len({c.policy_id for c in chunks}),
        distinct_rule_ids=len({c.rule_id for c in chunks if c.rule_id}),
        parse_seconds=parse_seconds,
        embed_seconds=embed_seconds,
        write_seconds=write_seconds,
        documents=[_document_record(p, chunks) for p in parsed_docs],
        chunks=chunks,
    )


def build_all_indexes(
    config: RagConfig | None = None,
    *,
    show_progress: bool = False,
    write_manifest: bool = True,
) -> BuildReport:
    """Build every configured product index and write the manifest."""
    config = config or get_config()
    started = time.perf_counter()

    emb = config.embedding
    embedder = PolicyEmbedder(emb.model, normalize=emb.normalize, batch_size=emb.batch_size)

    reports: dict[str, ProductBuildReport] = {}
    for key in config.products:
        reports[key] = build_product_index(
            config, key, embedder=embedder, show_progress=show_progress
        )

    report = BuildReport(
        products=reports,
        embedding=embedder.fingerprint(),
        reranker={"model": config.reranker.model, "enabled": config.reranker.enabled},
        config_snapshot={
            "chunking": {
                "max_chars": config.chunking.max_chars,
                "split_overlap_chars": config.chunking.split_overlap_chars,
                "min_chars": config.chunking.min_chars,
            },
            "retrieval": {
                "dense_top_k": config.retrieval.dense_top_k,
                "lexical_top_k": config.retrieval.lexical_top_k,
                "fusion_top_k": config.retrieval.fusion_top_k,
                "rerank_top_k": config.retrieval.rerank_top_k,
                "final_top_k": config.retrieval.final_top_k,
                "rrf_k": config.retrieval.rrf_k,
                "query_expansion": config.retrieval.query_expansion,
            },
        },
        total_seconds=time.perf_counter() - started,
    )

    if write_manifest:
        path = config.manifest_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(report.manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        report.manifest_path = path

    return report


def load_manifest(config: RagConfig | None = None) -> dict[str, Any]:
    config = config or get_config()
    if not config.manifest_path.exists():
        raise FileNotFoundError(
            f"no index manifest at {config.manifest_path}; run "
            "'python scripts/build_policy_indexes.py'"
        )
    return json.loads(config.manifest_path.read_text(encoding="utf-8"))
