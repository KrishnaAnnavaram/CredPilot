"""Building throwaway indexes for benchmarking.

The benchmarks need to build an index with a model that is not the configured one
without disturbing the committed index. This builds into a temporary directory
with a config cloned from the real one, so everything else about the pipeline —
chunking, metadata, fusion, filtering — is identical to production.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from src.config import RagConfig
from src.rag.embedding import PolicyEmbedder
from src.rag.indexer import BuildReport, ProductBuildReport, build_product_index


def temporary_config(
    base: RagConfig,
    workspace: Path,
    *,
    embedding_model: str | None = None,
    dimension: int | None = None,
    reranker_model: str | None = None,
) -> RagConfig:
    """Clone the config, pointing storage at ``workspace``."""
    workspace.mkdir(parents=True, exist_ok=True)
    embedding = base.embedding
    if embedding_model:
        embedding = dataclasses.replace(
            embedding, model=embedding_model, dimension=dimension or embedding.dimension
        )
    reranker = base.reranker
    if reranker_model:
        reranker = dataclasses.replace(reranker, model=reranker_model)

    return dataclasses.replace(
        base,
        vectorstore_path=workspace / "chroma",
        lexical_path=workspace / "lexical",
        manifest_path=workspace / "index_manifest.json",
        embedding=embedding,
        reranker=reranker,
    )


def build_temporary_indexes(config: RagConfig, embedder: PolicyEmbedder) -> BuildReport:
    """Build every product index into the config's workspace."""
    products: dict[str, ProductBuildReport] = {}
    for key in config.products:
        products[key] = build_product_index(config, key, embedder=embedder)
    return BuildReport(
        products=products,
        embedding=embedder.fingerprint(),
        reranker={"model": config.reranker.model, "enabled": config.reranker.enabled},
        config_snapshot={},
        total_seconds=0.0,
    )


def directory_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    total = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    return total / (1024 * 1024)


def peak_memory_mb() -> float | None:
    """Process peak working set, when the platform reports one."""
    try:
        import psutil

        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:  # noqa: BLE001 - optional dependency
        try:
            import resource

            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        except Exception:  # noqa: BLE001 - not available on Windows
            return None
