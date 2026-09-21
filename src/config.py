"""Configuration loading for CredPilot.

Configuration is a committed YAML file plus environment overrides for paths only.
No secret ever lives in config; API keys come from the environment via
python-dotenv (see ``.env.example``).
"""

from __future__ import annotations

import copy
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import yaml

from src.domain import LendingProductDomain

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "rag.yaml"


def repo_path(relative: str | Path) -> Path:
    """Resolve a repo-relative path to an absolute one."""
    p = Path(relative)
    return p if p.is_absolute() else REPO_ROOT / p


@dataclass(frozen=True)
class EmbeddingConfig:
    provider: str
    model: str
    dimension: int
    normalize: bool
    distance: str
    batch_size: int


@dataclass(frozen=True)
class RerankerConfig:
    enabled: bool
    model: str
    batch_size: int


@dataclass(frozen=True)
class ChunkingConfig:
    max_chars: int
    split_overlap_chars: int
    min_chars: int


@dataclass(frozen=True)
class RetrievalConfig:
    dense_top_k: int
    lexical_top_k: int
    fusion_top_k: int
    rerank_top_k: int
    final_top_k: int
    rrf_k: int
    dense_weight: float
    lexical_weight: float
    query_expansion: bool
    min_reranker_score: float


@dataclass(frozen=True)
class DedupeConfig:
    max_per_rule: int
    max_per_policy: int
    max_overview: int


@dataclass(frozen=True)
class ProductConfig:
    key: str
    domain: LendingProductDomain
    corpus_root: Path
    collection: str
    parser: str
    temporal_filtering: bool
    final_top_k: int


@dataclass(frozen=True)
class RagConfig:
    vectorstore_path: Path
    lexical_path: Path
    manifest_path: Path
    embedding: EmbeddingConfig
    reranker: RerankerConfig
    chunking: ChunkingConfig
    retrieval: RetrievalConfig
    dedupe: DedupeConfig
    products: dict[str, ProductConfig]
    benchmark: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def product(self, domain: "str | LendingProductDomain") -> ProductConfig:
        d = LendingProductDomain.from_any(domain)
        return self.products[d.corpus_key]

    def final_top_k_for(self, domain: "str | LendingProductDomain") -> int:
        return self.product(domain).final_top_k or self.retrieval.final_top_k


def _build(raw: Mapping[str, Any]) -> RagConfig:
    rag = raw["rag"]
    vs = rag["vectorstore"]
    emb = rag["embedding"]
    rr = rag["reranker"]
    ch = rag["chunking"]
    rt = rag["retrieval"]
    dd = rag.get("dedupe", {})

    products: dict[str, ProductConfig] = {}
    for key, spec in rag["products"].items():
        products[key] = ProductConfig(
            key=key,
            domain=LendingProductDomain.from_any(spec["domain"]),
            corpus_root=repo_path(spec["corpus_root"]),
            collection=spec["collection"],
            parser=spec["parser"],
            temporal_filtering=bool(spec.get("temporal_filtering", True)),
            final_top_k=int(spec.get("final_top_k", rt["final_top_k"])),
        )

    return RagConfig(
        vectorstore_path=repo_path(os.environ.get("CREDPILOT_VECTORSTORE_PATH", vs["path"])),
        lexical_path=repo_path(os.environ.get("CREDPILOT_LEXICAL_PATH", vs["lexical_path"])),
        manifest_path=repo_path(vs["manifest_path"]),
        embedding=EmbeddingConfig(
            provider=emb["provider"],
            model=os.environ.get("CREDPILOT_EMBEDDING_MODEL", emb["model"]),
            dimension=int(emb["dimension"]),
            normalize=bool(emb["normalize"]),
            distance=emb["distance"],
            batch_size=int(emb.get("batch_size", 32)),
        ),
        reranker=RerankerConfig(
            enabled=bool(rr.get("enabled", True)),
            model=os.environ.get("CREDPILOT_RERANKER_MODEL", rr["model"]),
            batch_size=int(rr.get("batch_size", 32)),
        ),
        chunking=ChunkingConfig(
            max_chars=int(ch["max_chars"]),
            split_overlap_chars=int(ch["split_overlap_chars"]),
            min_chars=int(ch.get("min_chars", 40)),
        ),
        retrieval=RetrievalConfig(
            dense_top_k=int(rt["dense_top_k"]),
            lexical_top_k=int(rt["lexical_top_k"]),
            fusion_top_k=int(rt["fusion_top_k"]),
            rerank_top_k=int(rt["rerank_top_k"]),
            final_top_k=int(rt["final_top_k"]),
            rrf_k=int(rt["rrf_k"]),
            dense_weight=float(rt.get("dense_weight", 1.0)),
            lexical_weight=float(rt.get("lexical_weight", 1.0)),
            query_expansion=bool(rt.get("query_expansion", True)),
            min_reranker_score=float(rt.get("min_reranker_score", -1e9)),
        ),
        dedupe=DedupeConfig(
            max_per_rule=int(dd.get("max_per_rule", 1)),
            max_per_policy=int(dd.get("max_per_policy", 3)),
            max_overview=int(dd.get("max_overview", 2)),
        ),
        products=products,
        benchmark=dict(raw.get("benchmark", {})),
        raw=copy.deepcopy(dict(raw)),
    )


def load_config(path: "str | Path | None" = None) -> RagConfig:
    """Load the retrieval config from YAML (uncached)."""
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    with open(cfg_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return _build(raw)


@lru_cache(maxsize=4)
def get_config(path: "str | Path | None" = None) -> RagConfig:
    """Load and cache the retrieval config."""
    return load_config(path)
