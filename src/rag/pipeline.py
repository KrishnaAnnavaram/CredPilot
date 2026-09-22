"""The CredPilot policy retriever.

One public entry point — :func:`retrieve_policy` — serves both lending products.
The caller names a product domain and asks a question; it never chooses a Chroma
collection, a BM25 index or a filter. Product routing is centralized here, which
is what makes cross-product contamination structurally impossible rather than
merely unlikely.

The pipeline, in order:

    sanitize untrusted text
        -> resolve product domain             (hard: picks the collection)
        -> build product-specific context
        -> applicability / temporal filter     (hard: effective-date window)
        -> BM25 lexical search    (top 15)
        -> dense vector search    (top 15)
        -> reciprocal rank fusion (top 12)
        -> cross-encoder rerank   (top 10)
        -> temporal re-validation
        -> deduplication
        -> citation validation
        -> PolicyEvidence[]       (top 6)

Those widths come from ``config/rag.yaml`` and were chosen by measurement, not
intuition — see ``docs/rag/RETRIEVAL_ABLATION.md``. Each is a *floor of*
``top_k + slack`` rather than a fixed cap, because every stage only removes
candidates: a caller asking for more evidence than a stage is wide would
otherwise receive less, silently.

Every stage opens a span, so a Phoenix trace shows exactly where candidates were
gained and lost. No language model participates in retrieval or ranking.
"""

from __future__ import annotations

import time
from datetime import date
from typing import Any, Mapping, Sequence

from src.config import RagConfig, get_config
from src.domain import (
    LendingProductDomain,
    ProductResolutionError,
    resolve_product_domain,
)
from src.guardrails.sanitize import sanitize_query
from src.observability import tracing as tr
from src.rag import applicability as app_filter
from src.rag.citations import CitationResolver
from src.rag.embedding import PolicyEmbedder
from src.rag.expansion import expand_query, extract_identifiers, normalize_query
from src.rag.fusion import FusedCandidate, fuse
from src.rag.lexical import BM25Index, load_index
from src.rag.models import (
    ApplicabilityStatus,
    PolicyEvidence,
    PolicyRetrievalRequest,
    PolicyRetrievalResult,
    RetrievalStatus,
)
from src.rag.rerank import CrossEncoderReranker
from src.rag.vectorstore import PolicyVectorStore

#: Weight applied to the soft product-scope affinity boost. Small on purpose: it
#: breaks ties between comparable rules without overturning the reranker.
_SCOPE_BOOST_WEIGHT = 0.25

#: How many spare candidates survive deduplication so that citation validation can
#: drop one without shortening the result.
_CITATION_SLACK = 3


class PolicyRetriever:
    """Hybrid, product-isolated, citation-validated policy retrieval."""

    def __init__(
        self,
        config: RagConfig | None = None,
        *,
        embedder: PolicyEmbedder | None = None,
        reranker: CrossEncoderReranker | None = None,
        enable_reranker: bool | None = None,
    ):
        self.config = config or get_config()
        self._embedder = embedder
        self._reranker = reranker
        self._enable_reranker = (
            self.config.reranker.enabled if enable_reranker is None else bool(enable_reranker)
        )
        self._stores: dict[LendingProductDomain, PolicyVectorStore] = {}
        self._lexical: dict[LendingProductDomain, BM25Index] = {}
        self._citations = CitationResolver(self.config)

    # -- lazily constructed components -------------------------------------------

    @property
    def embedder(self) -> PolicyEmbedder:
        if self._embedder is None:
            emb = self.config.embedding
            self._embedder = PolicyEmbedder(
                emb.model, normalize=emb.normalize, batch_size=emb.batch_size
            )
        return self._embedder

    @property
    def reranker(self) -> CrossEncoderReranker | None:
        if not self._enable_reranker:
            return None
        if self._reranker is None:
            rr = self.config.reranker
            self._reranker = CrossEncoderReranker(rr.model, batch_size=rr.batch_size)
        return self._reranker

    def store(self, domain: LendingProductDomain) -> PolicyVectorStore:
        if domain not in self._stores:
            self._stores[domain] = PolicyVectorStore(self.config, domain)
        return self._stores[domain]

    def lexical(self, domain: LendingProductDomain) -> BM25Index:
        if domain not in self._lexical:
            self._lexical[domain] = load_index(self.config, domain)
        return self._lexical[domain]

    # -- public API ---------------------------------------------------------------

    def retrieve(self, request: PolicyRetrievalRequest) -> PolicyRetrievalResult:
        """Retrieve policy evidence for one request."""
        started = time.perf_counter()
        stage_ms: dict[str, float] = {}
        domain = request.product_domain
        retrieval_cfg = self.config.retrieval
        product_cfg = self.config.product(domain)
        top_k = request.top_k or self.config.final_top_k_for(domain)

        # The configured funnel is tuned for the default top_k. Every stage below
        # only ever *removes* candidates, so a caller asking for more evidence
        # than a stage's width would silently receive less — a request for 15 was
        # capped at 12 by fusion_top_k, with nothing to say so. Each width
        # therefore has a floor of top_k plus enough slack for deduplication and
        # citation validation to discard from. The configured values still govern
        # at the default top_k, where they are wider than the floor.
        width_floor = top_k + _CITATION_SLACK
        dense_k = max(retrieval_cfg.dense_top_k, width_floor)
        lexical_k = max(retrieval_cfg.lexical_top_k, width_floor)
        fusion_k = max(retrieval_cfg.fusion_top_k, width_floor)
        rerank_depth = max(retrieval_cfg.rerank_top_k, width_floor)

        with tr.span(
            tr.SPAN_RAG_RETRIEVE,
            product_domain=domain.value,
            application_id=request.application_id,
            as_of_date=request.as_of_date.isoformat() if request.as_of_date else None,
            top_k=top_k,
        ) as root_span:
            # 1. Untrusted text never reaches the machinery ------------------------
            sanitized = sanitize_query(request.query_text)
            if sanitized.blocked:
                return self._empty(
                    request,
                    RetrievalStatus.MISSING_CONTEXT,
                    "the query contained no answerable policy question after sanitization",
                    started,
                    stage_ms,
                    normalized="",
                )
            normalized = normalize_query(sanitized.text)
            root_span.set(
                injection_findings=sanitized.findings or None,
                requires_human_review=sanitized.requires_human_review,
            )

            # 2. Applicability / metadata filtering (hard: domain + effective date)
            t0 = time.perf_counter()
            with tr.span(
                tr.SPAN_METADATA_FILTER, product_domain=domain.value
            ) as filter_span:
                allowed_ids, governing, catalogue_size = self._allowed_chunk_ids(
                    domain, request.as_of_date, product_cfg.temporal_filtering
                )
                filter_span.set(
                    catalogue_size=catalogue_size,
                    allowed=len(allowed_ids) if allowed_ids is not None else catalogue_size,
                    governing_policies=len(governing),
                )
            stage_ms["metadata_filter"] = (time.perf_counter() - t0) * 1000

            if allowed_ids is not None and not allowed_ids:
                return self._empty(
                    request,
                    RetrievalStatus.NO_APPLICABLE_POLICY,
                    f"no {domain.value} policy is in force as of "
                    f"{request.as_of_date.isoformat() if request.as_of_date else 'the requested date'}",
                    started,
                    stage_ms,
                    normalized=normalized,
                )

            # 3. Lexical retrieval ------------------------------------------------
            t0 = time.perf_counter()
            expanded, added_terms = expand_query(
                normalized, domain, enabled=retrieval_cfg.query_expansion
            )
            identifiers = extract_identifiers(normalized)
            with tr.span(
                tr.SPAN_BM25_SEARCH,
                product_domain=domain.value,
                top_k=lexical_k,
                expansion_terms=len(added_terms),
                identifiers=identifiers or None,
            ) as bm_span:
                lexical_hits = self.lexical(domain).search(
                    expanded, top_k=lexical_k, allowed_ids=allowed_ids
                )
                bm_span.set(hits=len(lexical_hits))
            stage_ms["bm25"] = (time.perf_counter() - t0) * 1000

            # 4. Dense retrieval --------------------------------------------------
            t0 = time.perf_counter()
            with tr.span(tr.SPAN_EMBEDDING_QUERY, model=self.config.embedding.model):
                query_vector = self.embedder.encode_query(normalized)
            stage_ms["embedding"] = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            with tr.span(
                tr.SPAN_CHROMA_SEARCH,
                product_domain=domain.value,
                collection=product_cfg.collection,
                top_k=dense_k,
            ) as chroma_span:
                dense_hits = self._dense_search(domain, query_vector, dense_k, allowed_ids)
                chroma_span.set(hits=len(dense_hits))
            stage_ms["dense"] = (time.perf_counter() - t0) * 1000

            if not dense_hits and not lexical_hits:
                return self._empty(
                    request,
                    RetrievalStatus.NO_APPLICABLE_POLICY,
                    "no policy chunk matched the query in either the lexical or the dense index",
                    started,
                    stage_ms,
                    normalized=normalized,
                )

            # 5. Rank fusion ------------------------------------------------------
            t0 = time.perf_counter()
            with tr.span(
                tr.SPAN_RRF_FUSION,
                rrf_k=retrieval_cfg.rrf_k,
                dense_candidates=len(dense_hits),
                lexical_candidates=len(lexical_hits),
            ) as fusion_span:
                fused = fuse(
                    dense_hits,
                    lexical_hits,
                    k=retrieval_cfg.rrf_k,
                    dense_weight=retrieval_cfg.dense_weight,
                    lexical_weight=retrieval_cfg.lexical_weight,
                    top_k=fusion_k,
                )
                fusion_span.set(fused_candidates=len(fused))
            stage_ms["fusion"] = (time.perf_counter() - t0) * 1000

            self._hydrate(domain, fused)

            # 6. Cross-encoder reranking -------------------------------------------
            t0 = time.perf_counter()
            ranked = self._rerank(normalized, fused, rerank_depth, domain)
            stage_ms["rerank"] = (time.perf_counter() - t0) * 1000

            # 7. Temporal re-validation, on the survivors ---------------------------
            t0 = time.perf_counter()
            with tr.span(
                tr.SPAN_TEMPORAL_VALIDATE,
                as_of_date=request.as_of_date.isoformat() if request.as_of_date else None,
                temporal_filtering=product_cfg.temporal_filtering,
            ) as temporal_span:
                validated, dropped = self._validate_temporal(
                    ranked, request.as_of_date, governing, product_cfg.temporal_filtering
                )
                temporal_span.set(kept=len(validated), dropped=dropped)
            stage_ms["temporal"] = (time.perf_counter() - t0) * 1000

            # 8. Context affinity + deduplication -----------------------------------
            # Deduplicate to slightly more than the caller asked for. Step 9 drops
            # anything whose citation does not resolve, and without the slack a
            # single unresolvable citation would silently shorten the result
            # instead of being replaced by the next good candidate.
            context = self._context(request)
            validated = self._apply_scope_affinity(validated, context)
            deduped = self._dedupe(validated, top_k + _CITATION_SLACK)

            # 9. Citation validation -------------------------------------------------
            t0 = time.perf_counter()
            with tr.span(tr.SPAN_CITATION_VALIDATE, candidates=len(deduped)) as cite_span:
                candidates = self._to_evidence(deduped, domain)
                unresolved = [e.citation for e in candidates if not e.citation_resolves]
                cite_span.set(unresolved=len(unresolved), unresolved_citations=unresolved or None)
            stage_ms["citation"] = (time.perf_counter() - t0) * 1000

            # A citation that does not resolve is not evidence.
            evidence = [e for e in candidates if e.citation_resolves][:top_k]
            for position, item in enumerate(evidence, start=1):
                item.final_rank = position

            status, message = self._status(evidence, sanitized.requires_human_review)
            latency_ms = (time.perf_counter() - started) * 1000

            with tr.span(
                tr.SPAN_RAG_RESULT,
                product_domain=domain.value,
                status=status.value,
                evidence_count=len(evidence),
                policy_ids=[e.policy_id for e in evidence],
                policy_versions=[e.policy_version or "" for e in evidence],
                rule_ids=[e.rule_id or "" for e in evidence],
                citations=[e.citation for e in evidence],
                latency_ms=round(latency_ms, 2),
            ):
                pass

            root_span.set(status=status.value, evidence_count=len(evidence))

            return PolicyRetrievalResult(
                status=status,
                product_domain=domain,
                query_text=request.query_text,
                normalized_query=normalized,
                as_of_date=request.as_of_date,
                evidence=evidence,
                message=message,
                dense_candidates=len(dense_hits),
                lexical_candidates=len(lexical_hits),
                fused_candidates=len(fused),
                reranked_candidates=len(ranked),
                filtered_out=dropped,
                latency_ms=latency_ms,
                stage_latency_ms={k: round(v, 3) for k, v in stage_ms.items()},
                debug=(
                    {
                        "expanded_query": expanded,
                        "expansion_terms": added_terms,
                        "identifiers": identifiers,
                        "sanitization": sanitized.summary(),
                        "governing_versions": {
                            pid: ver for pid, (ver, _) in sorted(governing.items())
                        },
                    }
                    if request.debug
                    else {}
                ),
            )

    # -- stages -------------------------------------------------------------------

    def fetch_rules(
        self,
        domain: LendingProductDomain,
        rule_ids: Sequence[str],
        *,
        as_of: date | None = None,
    ) -> list[PolicyEvidence]:
        """Fetch specific rules by id, without the ranking funnel.

        Asking "which rule answers this question?" is a ranking problem.
        Asking "give me DTI-CONV-003" is not — the rule id is indexed metadata
        and there is exactly one chunk per rule per version. Running the full
        funnel for it costs an embedding, a BM25 pass, fusion and a cross-encoder
        rerank to rediscover a fact the index already holds, and measured at
        about 1.4 seconds against roughly 40 milliseconds here.

        Temporal selection still applies, and that is the part that must not be
        skipped: ``DTI-CONV-001`` exists in both v1.0 and v2.0 with different
        ceilings, so a lookup by id alone would be ambiguous in exactly the way
        the whole effective-date mechanism exists to prevent. The same
        ``_allowed_chunk_ids`` filter the ranked path uses decides which version
        this returns.
        """
        wanted = {str(r).strip().upper() for r in rule_ids if str(r).strip()}
        if not wanted:
            return []

        catalogue = self.lexical(domain)
        product_cfg = self.config.product(domain)
        allowed, _, _ = self._allowed_chunk_ids(
            domain, as_of, product_cfg.temporal_filtering
        )

        with tr.span(
            tr.SPAN_RAG_RETRIEVE,
            product_domain=domain.value,
            lookup="by_rule_id",
            requested=len(wanted),
            as_of_date=as_of.isoformat() if as_of else None,
        ) as root_span:
            matches: list[tuple[str, dict[str, Any]]] = []
            for chunk_id, meta in zip(catalogue.chunk_ids, catalogue.metadatas):
                rule_id = str(meta.get("rule_id") or "").upper()
                if rule_id not in wanted:
                    continue
                if allowed is not None and chunk_id not in allowed:
                    continue
                matches.append((chunk_id, dict(meta)))

            if not matches:
                root_span.set(found=0)
                return []

            store = self.store(domain)
            documents = store.get_by_ids([cid for cid, _ in matches])
            candidates = [
                FusedCandidate(
                    chunk_id=chunk_id,
                    # No fusion happened, so there is no fusion score to report.
                    # Zero says "this did not come from ranking" rather than
                    # implying it ranked last.
                    fusion_score=0.0,
                    metadata=meta,
                    document=(documents.get(chunk_id) or {}).get("document", ""),
                )
                for chunk_id, meta in matches
            ]
            evidence = self._to_evidence(
                [(c, None, ApplicabilityStatus.APPLICABLE) for c in candidates], domain
            )
            root_span.set(found=len(evidence))
            return evidence

    def _allowed_chunk_ids(
        self, domain: LendingProductDomain, as_of: date | None, temporal_filtering: bool
    ) -> tuple[set[str] | None, dict[str, tuple[str | None, date | None]], int]:
        """Chunk ids that survive the hard applicability filter.

        Returns ``(allowed_ids | None, governing_versions, catalogue_size)``.
        ``None`` means "no filtering applies" and lets the search layers run
        unconstrained, which is faster than passing an allow-list of everything.
        """
        catalogue = self.lexical(domain)
        catalogue_size = len(catalogue.chunk_ids)
        if not temporal_filtering or as_of is None:
            return None, {}, catalogue_size

        governing = app_filter.select_effective_versions(catalogue.metadatas, as_of)
        allowed: set[str] = set()
        for chunk_id, meta in zip(catalogue.chunk_ids, catalogue.metadatas):
            decision = app_filter.classify(
                meta, as_of=as_of, governing_versions=governing, temporal_filtering=True
            )
            if decision.status in (
                ApplicabilityStatus.APPLICABLE,
                ApplicabilityStatus.UNDETERMINED,
            ):
                allowed.add(chunk_id)
        return allowed, governing, catalogue_size

    def _dense_search(
        self,
        domain: LendingProductDomain,
        query_vector: Sequence[float],
        top_k: int,
        allowed_ids: set[str] | None,
    ) -> list[dict[str, Any]]:
        """Dense search, over-fetching when an allow-list will thin the results."""
        store = self.store(domain)
        fetch = top_k if allowed_ids is None else min(top_k * 3, max(store.count(), top_k))
        hits = store.query(query_vector, top_k=fetch)
        if allowed_ids is not None:
            hits = [h for h in hits if h["chunk_id"] in allowed_ids]
        hits = hits[:top_k]
        for position, hit in enumerate(hits, start=1):
            hit["rank"] = position
        return hits

    def _hydrate(self, domain: LendingProductDomain, candidates: Sequence[FusedCandidate]) -> None:
        """Fill in documents for candidates that only the lexical layer found."""
        missing = [c.chunk_id for c in candidates if not c.document]
        if not missing:
            return
        fetched = self.store(domain).get_by_ids(missing)
        for cand in candidates:
            if cand.document:
                continue
            record = fetched.get(cand.chunk_id)
            if record:
                cand.document = record["document"]
                if not cand.metadata:
                    cand.metadata = dict(record["metadata"])

    def _rerank(
        self,
        query: str,
        candidates: Sequence[FusedCandidate],
        top_k: int,
        domain: LendingProductDomain,
    ) -> list[tuple[FusedCandidate, float | None]]:
        """Reorder candidates with the cross-encoder, or pass fusion order through."""
        reranker = self.reranker
        if reranker is None or not candidates:
            return [(c, None) for c in list(candidates)[:top_k]]

        with tr.span(
            tr.SPAN_RERANKER_RUN,
            model=self.config.reranker.model,
            candidates=len(candidates),
            product_domain=domain.value,
        ) as span:
            passages = [c.document or "" for c in candidates]
            items = reranker.rerank(query, passages, top_k=top_k)
            span.set(kept=len(items))
        return [(candidates[i.index], i.score) for i in items]

    def _validate_temporal(
        self,
        ranked: Sequence[tuple[FusedCandidate, float | None]],
        as_of: date | None,
        governing: Mapping[str, tuple[str | None, date | None]],
        temporal_filtering: bool,
    ) -> tuple[list[tuple[FusedCandidate, float | None, ApplicabilityStatus]], int]:
        out: list[tuple[FusedCandidate, float | None, ApplicabilityStatus]] = []
        dropped = 0
        for cand, score in ranked:
            decision = app_filter.classify(
                cand.metadata,
                as_of=as_of,
                governing_versions=governing or None,
                temporal_filtering=temporal_filtering,
            )
            if decision.status in (
                ApplicabilityStatus.APPLICABLE,
                ApplicabilityStatus.UNDETERMINED,
            ):
                out.append((cand, score, decision.status))
            else:
                dropped += 1
        return out, dropped

    @staticmethod
    def _context(request: PolicyRetrievalRequest) -> dict[str, Any]:
        return {
            "product_family": request.product_family,
            "loan_purpose": request.loan_purpose,
            "occupancy_type": request.occupancy_type,
            "education_product_code": request.education_product_code,
        }

    def _apply_scope_affinity(
        self,
        ranked: Sequence[tuple[FusedCandidate, float | None, ApplicabilityStatus]],
        context: Mapping[str, Any],
    ) -> list[tuple[FusedCandidate, float | None, ApplicabilityStatus]]:
        """Nudge in-scope evidence upward without overturning the reranker."""
        if not any(context.values()):
            return list(ranked)
        scored = []
        for position, (cand, score, status) in enumerate(ranked):
            affinity = app_filter.scope_affinity(cand.metadata, context)
            base = score if score is not None else -float(position)
            scored.append(((base + _SCOPE_BOOST_WEIGHT * affinity), position, cand, score, status))
        scored.sort(key=lambda t: (-t[0], t[1]))
        return [(cand, score, status) for _, _, cand, score, status in scored]

    def _dedupe(
        self,
        ranked: Sequence[tuple[FusedCandidate, float | None, ApplicabilityStatus]],
        top_k: int,
    ) -> list[tuple[FusedCandidate, float | None, ApplicabilityStatus]]:
        """Keep the best chunk per rule, and cap how much one policy can occupy.

        Several chunks of one rule add no evidence a single one does not already
        carry; several rules of one policy crowding out every other policy hides
        the evidence an underwriter needs.

        A document's OVERVIEW chunk is budgeted separately from its rules. It is
        navigation — purpose, scope, version history — and when it counted against
        the same per-policy budget it starved the rules underneath it: a question
        about which obligations count would return POL-LIA-001's overview plus two
        incidental rules, using up the policy's three slots before the rule that
        actually answers it was reached. Overviews now have their own small budget
        and keep their rank, so they can still answer "summarise this policy"
        without displacing the rule that answers everything else.
        """
        limits = self.config.dedupe
        # The overview budget scales with the request. A broad question — "which
        # policies govern this application?" — matches document overviews more
        # closely than any individual rule, so a fixed cap of 2 became the binding
        # constraint and returned 4 results where 15 were asked for. Half the
        # requested size, floored at the configured value, keeps the cap tight at
        # the default top_k (where it stops overviews starving rules) without
        # strangling a larger request.
        overview_budget = max(limits.max_overview, top_k // 2)
        per_rule: dict[tuple, int] = {}
        per_policy: dict[tuple, int] = {}
        overviews = 0
        out = []
        for cand, score, status in ranked:
            meta = cand.metadata
            is_overview = meta.get("chunk_kind") == "OVERVIEW"
            rule_key = (
                meta.get("policy_id"),
                meta.get("policy_version"),
                meta.get("rule_id") or meta.get("section_number") or meta.get("chunk_kind"),
            )
            policy_key = (meta.get("policy_id"), meta.get("policy_version"))
            if per_rule.get(rule_key, 0) >= limits.max_per_rule:
                continue
            if is_overview:
                if overviews >= overview_budget:
                    continue
                overviews += 1
            elif per_policy.get(policy_key, 0) >= limits.max_per_policy:
                continue
            else:
                per_policy[policy_key] = per_policy.get(policy_key, 0) + 1
            per_rule[rule_key] = per_rule.get(rule_key, 0) + 1
            out.append((cand, score, status))
            if len(out) >= top_k:
                break
        return out

    def _to_evidence(
        self,
        ranked: Sequence[tuple[FusedCandidate, float | None, ApplicabilityStatus]],
        domain: LendingProductDomain,
    ) -> list[PolicyEvidence]:
        evidence: list[PolicyEvidence] = []
        for position, (cand, score, status) in enumerate(ranked, start=1):
            meta = cand.metadata
            citation = meta.get("citation") or ""
            resolves, _ = self._citations.resolve(citation) if citation else (False, "no citation")
            evidence.append(
                PolicyEvidence(
                    product_domain=domain,
                    chunk_id=cand.chunk_id,
                    policy_id=meta.get("policy_id", ""),
                    policy_title=meta.get("policy_title", ""),
                    policy_version=meta.get("policy_version"),
                    rule_id=meta.get("rule_id"),
                    rule_title=meta.get("rule_title"),
                    section_number=meta.get("section_number"),
                    section_title=meta.get("section_title"),
                    source_path=meta.get("source_path", ""),
                    source_sha256=meta.get("source_sha256", ""),
                    effective_date=_parse_date(meta.get("effective_date")),
                    expiration_date=_parse_date(meta.get("expiration_date")),
                    source_category=meta.get("source_category"),
                    severity=meta.get("severity"),
                    outcome_type=meta.get("outcome_type"),
                    requires_human_review=meta.get("requires_human_review"),
                    text=cand.document or "",
                    dense_score=cand.dense_score,
                    dense_rank=cand.dense_rank,
                    bm25_score=cand.bm25_score,
                    bm25_rank=cand.bm25_rank,
                    fusion_score=cand.fusion_score,
                    reranker_score=score,
                    final_rank=position,
                    citation=citation,
                    citation_resolves=resolves,
                    applicability=status,
                )
            )
        return evidence

    @staticmethod
    def _status(
        evidence: Sequence[PolicyEvidence], requires_human_review: bool
    ) -> tuple[RetrievalStatus, str | None]:
        if requires_human_review:
            return (
                RetrievalStatus.HUMAN_REVIEW_REQUIRED,
                "the request carried an instruction-override or data-access attempt; "
                "evidence is returned for review but must not be auto-actioned "
                "(POL-SEC-001 SEC-INJ-001)",
            )
        if not evidence:
            return (
                RetrievalStatus.NO_APPLICABLE_POLICY,
                "no applicable policy with a resolvable citation was found",
            )
        return RetrievalStatus.FOUND, None

    def _empty(
        self,
        request: PolicyRetrievalRequest,
        status: RetrievalStatus,
        message: str,
        started: float,
        stage_ms: dict[str, float],
        *,
        normalized: str,
    ) -> PolicyRetrievalResult:
        return PolicyRetrievalResult(
            status=status,
            product_domain=request.product_domain,
            query_text=request.query_text,
            normalized_query=normalized,
            as_of_date=request.as_of_date,
            evidence=[],
            message=message,
            latency_ms=(time.perf_counter() - started) * 1000,
            stage_latency_ms={k: round(v, 3) for k, v in stage_ms.items()},
        )


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


_DEFAULT_RETRIEVER: PolicyRetriever | None = None


def get_retriever(config: RagConfig | None = None) -> PolicyRetriever:
    """Process-wide retriever, so models and indexes load once."""
    global _DEFAULT_RETRIEVER
    if _DEFAULT_RETRIEVER is None or config is not None:
        _DEFAULT_RETRIEVER = PolicyRetriever(config)
    return _DEFAULT_RETRIEVER


def retrieve_policy(
    *,
    query: str,
    product_domain: "str | LendingProductDomain | None" = None,
    application_id: str | None = None,
    as_of_date: "str | date | None" = None,
    application_context: Mapping[str, Any] | None = None,
    graph_state: Mapping[str, Any] | None = None,
    top_k: int | None = None,
    debug: bool = False,
    retriever: PolicyRetriever | None = None,
) -> PolicyRetrievalResult:
    """Retrieve policy evidence for one lending product.

    This is the only retrieval entry point callers should use. It resolves the
    product domain from structured facts, refusing to search when the product is
    genuinely ambiguous rather than searching both corpora and hoping the model
    picks correctly.
    """
    ctx = dict(application_context or {})
    with tr.span(tr.SPAN_DOMAIN_RESOLVE, application_id=application_id) as span:
        try:
            domain = resolve_product_domain(
                explicit_domain=product_domain,
                application_id=application_id,
                packet=ctx.get("packet"),
                graph_state=graph_state,
            )
        except ProductResolutionError as exc:
            span.set(resolved=False)
            return PolicyRetrievalResult(
                status=RetrievalStatus.PRODUCT_CLARIFICATION_REQUIRED,
                # The request could not be scoped, so no corpus was touched.
                product_domain=LendingProductDomain.MORTGAGE,
                query_text=query,
                normalized_query=normalize_query(query),
                evidence=[],
                message=str(exc),
            )
        span.set(resolved=True, product_domain=domain.value)

    if isinstance(as_of_date, str) and as_of_date:
        as_of_date = date.fromisoformat(as_of_date)

    request = PolicyRetrievalRequest(
        product_domain=domain,
        query_text=query,
        application_id=application_id,
        as_of_date=as_of_date,
        product_family=ctx.get("product_family"),
        loan_purpose=ctx.get("loan_purpose"),
        occupancy_type=ctx.get("occupancy_type"),
        education_product_code=ctx.get("product_code") or ctx.get("education_product_code"),
        policy_family_hint=ctx.get("policy_family_hint"),
        policy_id_hint=ctx.get("policy_id_hint"),
        rule_id_hint=ctx.get("rule_id_hint"),
        top_k=top_k,
        debug=debug,
    )
    return (retriever or get_retriever()).retrieve(request)
