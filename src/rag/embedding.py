"""Local Sentence-Transformers embedding, used according to each model's own convention.

No hosted embedding API is called. Models run on the local machine through
``sentence-transformers``; the only network access is the initial model download
from the Hugging Face hub, after which the local cache serves every run.

Each family is used the way its authors published it:

* **BGE v1.5** — normalized embeddings, no passage prefix, and a short retrieval
  instruction on the query side only.
* **E5** — the mandatory ``query: `` / ``passage: `` prefixes.
* **MiniLM (all-*)** — symmetric, no prefixes.

Getting this wrong silently costs recall, so the convention travels with the
model name rather than being a caller's responsibility.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class EncodingConvention:
    """How one model family wants its queries and passages presented."""

    query_prefix: str = ""
    passage_prefix: str = ""
    normalize: bool = True

    def describe(self) -> str:
        if not self.query_prefix and not self.passage_prefix:
            return "symmetric (no prefixes)"
        return f"query={self.query_prefix!r} passage={self.passage_prefix!r}"


_BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

_CONVENTIONS: tuple[tuple[str, EncodingConvention], ...] = (
    # order matters: first substring match wins
    ("bge-m3", EncodingConvention(normalize=True)),
    ("bge-", EncodingConvention(query_prefix=_BGE_QUERY_INSTRUCTION, normalize=True)),
    ("e5-", EncodingConvention(query_prefix="query: ", passage_prefix="passage: ", normalize=True)),
    ("gte-", EncodingConvention(normalize=True)),
    ("all-minilm", EncodingConvention(normalize=True)),
    ("all-mpnet", EncodingConvention(normalize=True)),
)


def convention_for(model_name: str) -> EncodingConvention:
    """Return the published encoding convention for a model name."""
    key = model_name.lower()
    for marker, conv in _CONVENTIONS:
        if marker in key:
            return conv
    # Unknown checkpoint: normalized, symmetric. Recorded in the manifest so the
    # choice is visible rather than assumed.
    return EncodingConvention(normalize=True)


_MODEL_LOCK = threading.Lock()


@lru_cache(maxsize=8)
def _load_model(model_name: str, device: str | None):
    from sentence_transformers import SentenceTransformer

    with _MODEL_LOCK:
        return SentenceTransformer(model_name, device=device)


class PolicyEmbedder:
    """Encode policy chunks and queries with one local Sentence-Transformers model."""

    def __init__(
        self,
        model_name: str,
        *,
        normalize: bool | None = None,
        batch_size: int = 32,
        device: str | None = None,
    ):
        self.model_name = model_name
        self.convention = convention_for(model_name)
        self.normalize = self.convention.normalize if normalize is None else bool(normalize)
        self.batch_size = batch_size
        self.device = device
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = _load_model(self.model_name, self.device)
        return self._model

    @property
    def dimension(self) -> int:
        # sentence-transformers 6 renamed this; support both without a warning.
        getter = getattr(self.model, "get_embedding_dimension", None) or getattr(
            self.model, "get_sentence_embedding_dimension"
        )
        return int(getter())

    @property
    def revision(self) -> str | None:
        """The model revision, when the loaded checkpoint reports one."""
        for module in getattr(self.model, "_modules", {}).values():
            cfg = getattr(getattr(module, "auto_model", None), "config", None)
            rev = getattr(cfg, "_commit_hash", None)
            if rev:
                return str(rev)
        return None

    def encode_passages(self, texts: Sequence[str], show_progress: bool = False) -> np.ndarray:
        prepared = [self.convention.passage_prefix + t for t in texts]
        return self._encode(prepared, show_progress)

    def encode_queries(self, texts: Sequence[str], show_progress: bool = False) -> np.ndarray:
        prepared = [self.convention.query_prefix + t for t in texts]
        return self._encode(prepared, show_progress)

    def encode_query(self, text: str) -> list[float]:
        return self.encode_queries([text])[0].tolist()

    def _encode(self, texts: Sequence[str], show_progress: bool) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        vectors = self.model.encode(
            list(texts),
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize,
            show_progress_bar=show_progress,
        )
        return np.asarray(vectors, dtype=np.float32)

    def fingerprint(self) -> dict[str, object]:
        """Everything a manifest needs to reproduce this embedding configuration."""
        return {
            "model": self.model_name,
            "revision": self.revision,
            "dimension": self.dimension,
            "normalize": self.normalize,
            "encoding_convention": self.convention.describe(),
            "query_prefix": self.convention.query_prefix,
            "passage_prefix": self.convention.passage_prefix,
            "distance_metric": "cosine",
        }


def batched(items: Sequence, size: int) -> Iterable[Sequence]:
    for start in range(0, len(items), size):
        yield items[start : start + size]
