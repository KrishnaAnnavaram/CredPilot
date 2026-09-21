"""BM25 lexical retrieval over the policy corpora.

Lending policy is full of tokens that carry meaning no embedding reliably
recovers: ``POL-DTI-001``, ``DTI-CONV-001``, ``HCLTV``, ``PITIA``, ``COA``,
``I-94``, ``Tier A``. A question naming a rule id must not depend on the
semantics of that rule's prose, so a lexical index runs alongside the dense one
and the two are fused.

Implementation is ``rank-bm25`` (pure Python, pip-installable, no service). The
index persists as JSON — readable, diffable, and deterministic to rebuild.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from src.config import RagConfig
from src.domain import LendingProductDomain
from src.rag.models import PolicyChunk

#: Keep identifier shapes intact: ``POL-DTI-001``, ``I-94``, ``ms-marco``. Splitting
#: on the hyphen would scatter the exact token a user typed across three terms.
_TOKEN = re.compile(r"[a-z0-9]+(?:[-/][a-z0-9]+)*")

#: Very common English words carry no discrimination across a single-domain
#: policy corpus. Kept deliberately short — policy vocabulary such as "income",
#: "credit" or "value" must survive.
_STOPWORDS = frozenset(
    """a an and are as at be been being by for from has have how in into is it its
    of on or that the their then there these this to was were what when where which
    who will with would you your""".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase, identifier-preserving tokenization.

    Hyphenated identifiers are emitted whole *and* as their parts, so
    ``DTI-CONV-001`` matches a query spelling it either way.
    """
    out: list[str] = []
    for match in _TOKEN.finditer(text.lower()):
        token = match.group(0)
        if token in _STOPWORDS:
            continue
        out.append(token)
        if "-" in token or "/" in token:
            out.extend(p for p in re.split(r"[-/]", token) if p and p not in _STOPWORDS)
    return out


@dataclass
class LexicalHit:
    chunk_id: str
    score: float
    rank: int
    metadata: dict[str, Any]


class BM25Index:
    """A persisted BM25 index over one product's policy chunks."""

    SCHEMA_VERSION = 1

    def __init__(
        self,
        domain: LendingProductDomain,
        chunk_ids: Sequence[str],
        corpus_tokens: Sequence[Sequence[str]],
        metadatas: Sequence[dict[str, Any]],
    ):
        if not (len(chunk_ids) == len(corpus_tokens) == len(metadatas)):
            raise ValueError("chunk_ids, corpus_tokens and metadatas must be the same length")
        self.domain = domain
        self.chunk_ids = list(chunk_ids)
        self.corpus_tokens = [list(t) for t in corpus_tokens]
        self.metadatas = [dict(m) for m in metadatas]
        self._bm25 = None

    # -- build / persist ---------------------------------------------------------

    @classmethod
    def build(cls, domain: LendingProductDomain, chunks: Sequence[PolicyChunk]) -> "BM25Index":
        return cls(
            domain=domain,
            chunk_ids=[c.chunk_id for c in chunks],
            corpus_tokens=[tokenize(c.embedding_text()) for c in chunks],
            metadatas=[c.chroma_metadata() for c in chunks],
        )

    @staticmethod
    def path_for(config: RagConfig, domain: "str | LendingProductDomain") -> Path:
        d = LendingProductDomain.from_any(domain)
        return config.lexical_path / f"bm25_{d.corpus_key}.json"

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "product_domain": self.domain.value,
            "document_count": len(self.chunk_ids),
            "records": [
                {"chunk_id": cid, "tokens": toks, "metadata": meta}
                for cid, toks, meta in zip(self.chunk_ids, self.corpus_tokens, self.metadatas)
            ],
        }
        # sort_keys keeps the artifact byte-stable across runs.
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
        )
        return path

    @classmethod
    def load(cls, path: Path) -> "BM25Index":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != cls.SCHEMA_VERSION:
            raise ValueError(
                f"{path}: lexical index schema {payload.get('schema_version')} is not "
                f"{cls.SCHEMA_VERSION}; rebuild the indexes"
            )
        records = payload["records"]
        return cls(
            domain=LendingProductDomain.from_any(payload["product_domain"]),
            chunk_ids=[r["chunk_id"] for r in records],
            corpus_tokens=[r["tokens"] for r in records],
            metadatas=[r["metadata"] for r in records],
        )

    # -- search ------------------------------------------------------------------

    @property
    def bm25(self):
        if self._bm25 is None:
            from rank_bm25 import BM25Okapi

            self._bm25 = BM25Okapi(self.corpus_tokens)
        return self._bm25

    def search(
        self,
        query: str,
        *,
        top_k: int,
        allowed_ids: set[str] | None = None,
    ) -> list[LexicalHit]:
        """Score every chunk, then return the best ``top_k`` still allowed.

        Filtering happens on the scored list rather than by rebuilding the index,
        so document frequencies stay those of the whole product corpus and scores
        remain comparable between filtered and unfiltered calls.
        """
        tokens = tokenize(query)
        if not tokens or not self.chunk_ids:
            return []
        scores = self.bm25.get_scores(tokens)
        order = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), self.chunk_ids[i]))
        hits: list[LexicalHit] = []
        for idx in order:
            cid = self.chunk_ids[idx]
            if allowed_ids is not None and cid not in allowed_ids:
                continue
            score = float(scores[idx])
            if score <= 0.0:
                break
            hits.append(
                LexicalHit(
                    chunk_id=cid,
                    score=score,
                    rank=len(hits) + 1,
                    metadata=self.metadatas[idx],
                )
            )
            if len(hits) >= top_k:
                break
        return hits


def load_index(config: RagConfig, domain: "str | LendingProductDomain") -> BM25Index:
    path = BM25Index.path_for(config, domain)
    if not path.exists():
        raise FileNotFoundError(
            f"lexical index missing at {path}; run 'python scripts/build_policy_indexes.py'"
        )
    return BM25Index.load(path)
