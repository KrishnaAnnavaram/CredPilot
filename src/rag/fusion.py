"""Reciprocal Rank Fusion of the lexical and dense candidate lists.

RRF combines rankings, not scores, which is what makes it safe here: a BM25 score
and a cosine similarity are not on the same scale and normalizing them into one
would bake an arbitrary calibration into every retrieval.

For a document *d* appearing at rank ``r_i(d)`` in each input ranking *i*:

.. math::

    \\mathrm{RRF}(d) = \\sum_i \\frac{w_i}{k + r_i(d)}

with ``k`` (default 60) damping the influence of the very top of any single list
and ``w_i`` a per-list weight (both lists weighted 1.0 by default). Ranks are
1-based. A document absent from a list contributes nothing from that list.

The fusion is deterministic: ties break on chunk id, so the same inputs always
produce the same order. No language model participates in ranking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


@dataclass
class FusedCandidate:
    """One candidate after fusion, carrying where it came from."""

    chunk_id: str
    fusion_score: float
    dense_rank: int | None = None
    dense_score: float | None = None
    bm25_rank: int | None = None
    bm25_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    document: str | None = None
    rank: int = 0

    @property
    def sources(self) -> list[str]:
        out = []
        if self.dense_rank is not None:
            out.append("dense")
        if self.bm25_rank is not None:
            out.append("bm25")
        return out


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[str]],
    *,
    k: int = 60,
    weights: Sequence[float] | None = None,
) -> dict[str, float]:
    """Fuse ranked id lists into ``{id: rrf_score}``.

    ``ranked_lists`` are ordered best-first; ``weights`` defaults to 1.0 each.
    """
    if k <= 0:
        raise ValueError("rrf_k must be positive")
    if weights is None:
        weights = [1.0] * len(ranked_lists)
    if len(weights) != len(ranked_lists):
        raise ValueError("weights must be the same length as ranked_lists")

    scores: dict[str, float] = {}
    for ranking, weight in zip(ranked_lists, weights):
        for position, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + weight / (k + position)
    return scores


def fuse(
    dense_hits: Iterable[Mapping[str, Any]],
    lexical_hits: Iterable[Any],
    *,
    k: int = 60,
    dense_weight: float = 1.0,
    lexical_weight: float = 1.0,
    top_k: int | None = None,
) -> list[FusedCandidate]:
    """Fuse dense and lexical hits into one ranked candidate list.

    ``dense_hits`` are the mappings returned by
    :meth:`~src.rag.vectorstore.PolicyVectorStore.query`; ``lexical_hits`` are
    :class:`~src.rag.lexical.LexicalHit` objects.
    """
    dense = list(dense_hits)
    lexical = list(lexical_hits)

    dense_ids = [h["chunk_id"] for h in dense]
    lexical_ids = [h.chunk_id for h in lexical]

    scores = reciprocal_rank_fusion(
        [dense_ids, lexical_ids], k=k, weights=[dense_weight, lexical_weight]
    )

    dense_by_id = {h["chunk_id"]: h for h in dense}
    lexical_by_id = {h.chunk_id: h for h in lexical}

    candidates: list[FusedCandidate] = []
    for chunk_id, score in scores.items():
        d = dense_by_id.get(chunk_id)
        lx = lexical_by_id.get(chunk_id)
        candidates.append(
            FusedCandidate(
                chunk_id=chunk_id,
                fusion_score=score,
                dense_rank=d["rank"] if d else None,
                dense_score=d["score"] if d else None,
                bm25_rank=lx.rank if lx else None,
                bm25_score=lx.score if lx else None,
                metadata=dict(d["metadata"]) if d else dict(lx.metadata) if lx else {},
                document=d.get("document") if d else None,
            )
        )

    # Deterministic: score descending, then chunk id ascending.
    candidates.sort(key=lambda c: (-c.fusion_score, c.chunk_id))
    for position, cand in enumerate(candidates, start=1):
        cand.rank = position
    return candidates[:top_k] if top_k else candidates
