"""Local cross-encoder reranking.

Fusion produces a good candidate set from two cheap signals; a cross-encoder then
reads each (query, chunk) pair jointly and reorders them. This runs locally
through ``sentence-transformers``' ``CrossEncoder`` — no hosted reranking service
is contacted.

Which checkpoint is used is a benchmark result, not an assumption; see
``docs/rag/RERANKER_BENCHMARK.md``.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

_MODEL_LOCK = threading.Lock()


@lru_cache(maxsize=4)
def _load_cross_encoder(model_name: str, max_length: int, device: str | None):
    from sentence_transformers import CrossEncoder

    with _MODEL_LOCK:
        return CrossEncoder(model_name, max_length=max_length, device=device)


@dataclass
class RerankedItem:
    index: int
    score: float
    rank: int


class CrossEncoderReranker:
    """Score (query, passage) pairs with a local cross-encoder."""

    def __init__(
        self,
        model_name: str,
        *,
        batch_size: int = 32,
        max_length: int = 512,
        device: str | None = None,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_length = max_length
        self.device = device
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = _load_cross_encoder(self.model_name, self.max_length, self.device)
        return self._model

    def score(self, query: str, passages: Sequence[str]) -> list[float]:
        if not passages:
            return []
        raw = self.model.predict(
            [(query, p) for p in passages],
            batch_size=self.batch_size,
            show_progress_bar=False,
        )
        return [float(s) for s in raw]

    def rerank(
        self, query: str, passages: Sequence[str], *, top_k: int | None = None
    ) -> list[RerankedItem]:
        """Return passage indices reordered best-first.

        Ties break on the original index, so a reranker that cannot separate two
        candidates leaves the fusion order between them intact.
        """
        scores = self.score(query, passages)
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
        items = [
            RerankedItem(index=i, score=scores[i], rank=position)
            for position, i in enumerate(order, start=1)
        ]
        return items[:top_k] if top_k else items

    def fingerprint(self) -> dict[str, object]:
        return {
            "model": self.model_name,
            "max_length": self.max_length,
            "batch_size": self.batch_size,
        }
