"""Chroma persistence for the two isolated policy collections.

One local persistent Chroma database holds two collections — one per lending
product. There is deliberately no combined collection: a mortgage query can never
reach an education policy because the two bodies of knowledge never share an
index, not because a filter happened to be applied correctly.

Chroma is used as a pure vector store here. Embeddings are computed by
:mod:`src.rag.embedding` and passed in explicitly, so the embedding convention is
owned by CredPilot rather than by whatever default the client ships.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from src.config import RagConfig
from src.domain import LendingProductDomain
from src.rag.models import PolicyChunk

#: Collection names are fixed by config; this guards against a combined index
#: being created by accident.
FORBIDDEN_COLLECTION_NAMES = frozenset({"credpilot_all_policies", "credpilot_policies"})


def _client(path: Path):
    import chromadb
    from chromadb.config import Settings

    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(path),
        settings=Settings(anonymized_telemetry=False, allow_reset=True),
    )


class PolicyVectorStore:
    """Read/write access to one product's Chroma collection."""

    def __init__(self, config: RagConfig, domain: "str | LendingProductDomain"):
        self.config = config
        self.domain = LendingProductDomain.from_any(domain)
        self.product = config.product(self.domain)
        if self.product.collection in FORBIDDEN_COLLECTION_NAMES:
            raise ValueError(
                f"collection {self.product.collection!r} would mix lending products; "
                "each product must have its own collection"
            )
        self._client = _client(config.vectorstore_path)
        self._collection = None

    # -- lifecycle ---------------------------------------------------------------

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=self.product.collection,
                # Cosine distance, matching the normalized embeddings we store.
                metadata={"hnsw:space": "cosine", "product_domain": self.domain.value},
            )
        return self._collection

    def reset(self) -> None:
        """Drop and recreate this product's collection.

        Correctness before cleverness: a rebuild starts from an empty collection
        so a removed or edited policy can never leave stale embeddings behind.
        """
        try:
            self._client.delete_collection(self.product.collection)
        except Exception:  # noqa: BLE001 - absent collection is the normal first-run case
            pass
        self._collection = None
        _ = self.collection

    def count(self) -> int:
        return int(self.collection.count())

    # -- writes ------------------------------------------------------------------

    def add_chunks(
        self, chunks: Sequence[PolicyChunk], embeddings: np.ndarray, batch_size: int = 256
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"chunk/embedding length mismatch: {len(chunks)} vs {len(embeddings)}"
            )
        wrong = [c.chunk_id for c in chunks if c.product_domain is not self.domain]
        if wrong:
            raise ValueError(
                f"refusing to write {len(wrong)} chunk(s) from another product into "
                f"{self.product.collection}: {wrong[:3]}"
            )
        written = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            self.collection.add(
                ids=[c.chunk_id for c in batch],
                documents=[c.embedding_text() for c in batch],
                metadatas=[c.chroma_metadata() for c in batch],
                embeddings=[e.tolist() for e in embeddings[start : start + len(batch)]],
            )
            written += len(batch)
        return written

    # -- reads -------------------------------------------------------------------

    def query(
        self,
        query_embedding: Sequence[float],
        *,
        top_k: int,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Dense similarity search inside this product's collection only."""
        n = max(1, min(top_k, max(self.count(), 1)))
        res = self.collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=n,
            where=where or None,
            include=["metadatas", "documents", "distances"],
        )
        out: list[dict[str, Any]] = []
        ids = res.get("ids") or [[]]
        for rank, chunk_id in enumerate(ids[0]):
            meta = (res.get("metadatas") or [[]])[0][rank] or {}
            distance = (res.get("distances") or [[]])[0][rank]
            out.append(
                {
                    "chunk_id": chunk_id,
                    "metadata": meta,
                    "document": (res.get("documents") or [[]])[0][rank],
                    # Chroma reports cosine *distance*; similarity is 1 - distance.
                    "distance": float(distance),
                    "score": 1.0 - float(distance),
                    "rank": rank + 1,
                }
            )
        return out

    def get_all(self, include_documents: bool = False) -> list[dict[str, Any]]:
        """Every record in the collection — used by the integrity validator."""
        include = ["metadatas"] + (["documents"] if include_documents else [])
        res = self.collection.get(include=include)
        ids = res.get("ids") or []
        metas = res.get("metadatas") or []
        docs = res.get("documents") or [None] * len(ids)
        return [
            {"chunk_id": i, "metadata": metas[n] or {}, "document": docs[n]}
            for n, i in enumerate(ids)
        ]

    def get_by_ids(self, chunk_ids: Sequence[str]) -> dict[str, dict[str, Any]]:
        if not chunk_ids:
            return {}
        res = self.collection.get(ids=list(chunk_ids), include=["metadatas", "documents"])
        ids = res.get("ids") or []
        metas = res.get("metadatas") or []
        docs = res.get("documents") or [None] * len(ids)
        return {
            cid: {"metadata": metas[n] or {}, "document": docs[n]} for n, cid in enumerate(ids)
        }


def open_stores(config: RagConfig) -> dict[LendingProductDomain, PolicyVectorStore]:
    """Open every configured product collection."""
    return {p.domain: PolicyVectorStore(config, p.domain) for p in config.products.values()}


def wipe_vectorstore(config: RagConfig) -> None:
    """Delete the whole persistent directory. Used only by a full rebuild."""
    if config.vectorstore_path.exists():
        shutil.rmtree(config.vectorstore_path)
