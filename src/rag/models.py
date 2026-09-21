"""Typed data model for the CredPilot policy-retrieval subsystem.

One normalized shape spans both lending products. Fields a product does not
support are ``None`` — they are never fabricated to make the two products look
symmetrical.
"""

from __future__ import annotations

import hashlib
from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain import LendingProductDomain

# --------------------------------------------------------------------------------------
# Statuses
# --------------------------------------------------------------------------------------


class RetrievalStatus(str, Enum):
    """Outcome of a policy-retrieval call.

    A retriever that cannot find applicable policy says so. It never invents one.
    """

    FOUND = "FOUND"
    NO_APPLICABLE_POLICY = "NO_APPLICABLE_POLICY"
    AMBIGUOUS_POLICY = "AMBIGUOUS_POLICY"
    MISSING_CONTEXT = "MISSING_CONTEXT"
    PRODUCT_CLARIFICATION_REQUIRED = "PRODUCT_CLARIFICATION_REQUIRED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


class ApplicabilityStatus(str, Enum):
    """Why a chunk survived — or would not survive — applicability validation."""

    APPLICABLE = "APPLICABLE"
    NOT_YET_EFFECTIVE = "NOT_YET_EFFECTIVE"
    EXPIRED = "EXPIRED"
    SUPERSEDED = "SUPERSEDED"
    OUT_OF_PRODUCT_SCOPE = "OUT_OF_PRODUCT_SCOPE"
    UNDETERMINED = "UNDETERMINED"


class ChunkKind(str, Enum):
    """What a chunk represents inside its source document."""

    RULE = "RULE"
    SECTION = "SECTION"
    OVERVIEW = "OVERVIEW"


# --------------------------------------------------------------------------------------
# Indexed unit
# --------------------------------------------------------------------------------------


class PolicyChunk(BaseModel):
    """One retrievable unit of policy knowledge.

    The preferred unit is a whole rule together with its thresholds,
    applicability and exceptions. Secondary splitting happens only when a rule is
    genuinely too large, and the parent heading travels with every split part.
    """

    model_config = ConfigDict(extra="forbid")

    # identity
    chunk_id: str
    product_domain: LendingProductDomain
    chunk_kind: ChunkKind
    chunk_index: int = 0
    part_index: int = 0
    part_count: int = 1

    # provenance
    policy_id: str
    policy_title: str
    source_path: str
    source_sha256: str

    # policy-level metadata (present where the corpus supports it)
    policy_version: str | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    source_category: str | None = None
    jurisdiction: str | None = None
    priority: int | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    requires_human_review: bool | None = None
    issuer: str | None = None

    # rule-level metadata
    rule_id: str | None = None
    rule_title: str | None = None
    severity: str | None = None
    outcome_type: str | None = None
    section_number: str | None = None
    section_title: str | None = None

    # product-scope metadata (list-valued in source; stored pipe-joined for Chroma)
    policy_family: str | None = None
    product_scope: list[str] = Field(default_factory=list)
    occupancy_scope: list[str] = Field(default_factory=list)
    purpose_scope: list[str] = Field(default_factory=list)
    cross_refs: list[str] = Field(default_factory=list)

    # content
    heading_path: str = ""
    text: str = ""

    @field_validator("text")
    @classmethod
    def _text_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("chunk text must not be blank")
        return v

    @property
    def citation(self) -> str:
        """Human-resolvable citation in the product's own conventional form.

        Mortgage policy documents are versioned and their golden set cites
        ``POL-DTI-001 v2.0 rule DTI-CONV-001``. The education corpus is
        single-version per document and its golden set cites ``POL-002
        EDU-UW-001``. Each product keeps its own convention rather than being
        forced into the other's.
        """
        return build_citation(
            product_domain=self.product_domain,
            policy_id=self.policy_id,
            policy_version=self.policy_version,
            rule_id=self.rule_id,
            section_number=self.section_number,
        )

    def embedding_text(self) -> str:
        """The text actually embedded and lexically indexed.

        Headings and identifiers are prepended so that both the dense and the
        lexical layer can see the policy id, rule id and titles — a query naming
        ``DTI-CONV-001`` must not depend on the semantics of the rule body alone.
        """
        parts = [
            f"{self.policy_id} {self.policy_title}",
        ]
        if self.policy_version:
            parts[0] += f" (version {self.policy_version})"
        if self.section_number or self.section_title:
            parts.append(f"Section {self.section_number or ''} {self.section_title or ''}".strip())
        if self.rule_id:
            parts.append(f"Rule {self.rule_id} — {self.rule_title or ''}".strip(" —"))
        if self.policy_family:
            parts.append(f"Policy family: {self.policy_family}")
        if self.product_scope:
            parts.append("Products: " + ", ".join(self.product_scope))
        parts.append(self.text)
        return "\n".join(p for p in parts if p)

    def chroma_metadata(self) -> dict[str, Any]:
        """Flatten to Chroma-compatible scalar metadata.

        Chroma stores str/int/float/bool only, so list fields are pipe-joined and
        dates are ISO strings. ``None`` values are dropped rather than coerced.
        """
        meta: dict[str, Any] = {
            "product_domain": self.product_domain.value,
            "chunk_id": self.chunk_id,
            "chunk_kind": self.chunk_kind.value,
            "chunk_index": self.chunk_index,
            "part_index": self.part_index,
            "part_count": self.part_count,
            "policy_id": self.policy_id,
            "policy_title": self.policy_title,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "citation": self.citation,
            "heading_path": self.heading_path,
        }
        optional = {
            "policy_version": self.policy_version,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "effective_ordinal": self.effective_date.toordinal() if self.effective_date else None,
            "expiration_ordinal": (
                self.expiration_date.toordinal() if self.expiration_date else None
            ),
            "source_category": self.source_category,
            "jurisdiction": self.jurisdiction,
            "priority": self.priority,
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "requires_human_review": self.requires_human_review,
            "issuer": self.issuer,
            "rule_id": self.rule_id,
            "rule_title": self.rule_title,
            "severity": self.severity,
            "outcome_type": self.outcome_type,
            "section_number": self.section_number,
            "section_title": self.section_title,
            "policy_family": self.policy_family,
            "product_scope": "|".join(self.product_scope) or None,
            "occupancy_scope": "|".join(self.occupancy_scope) or None,
            "purpose_scope": "|".join(self.purpose_scope) or None,
            "cross_refs": "|".join(self.cross_refs) or None,
        }
        meta.update({k: v for k, v in optional.items() if v is not None})
        return meta


def build_citation(
    *,
    product_domain: LendingProductDomain,
    policy_id: str,
    policy_version: str | None = None,
    rule_id: str | None = None,
    section_number: str | None = None,
) -> str:
    """Build the product-conventional citation string.

    Never invents a rule id: a chunk with no rule falls back to its section, and
    a chunk with neither cites the policy document alone.
    """
    if product_domain is LendingProductDomain.MORTGAGE:
        head = f"{policy_id} v{policy_version}" if policy_version else policy_id
        if rule_id:
            return f"{head} rule {rule_id}"
        if section_number:
            return f"{head} section {section_number}"
        return head
    # EDUCATION_LOAN
    if rule_id:
        return f"{policy_id} {rule_id}"
    if section_number:
        return f"{policy_id} section {section_number}"
    return policy_id


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


# --------------------------------------------------------------------------------------
# Request / response
# --------------------------------------------------------------------------------------


class PolicyRetrievalRequest(BaseModel):
    """A request for policy evidence, scoped to exactly one lending product."""

    model_config = ConfigDict(extra="forbid")

    product_domain: LendingProductDomain
    query_text: str = Field(min_length=1)

    application_id: str | None = None
    as_of_date: date | None = None

    # Mortgage application context (hard/soft filters where the metadata exists)
    product_family: str | None = None
    loan_purpose: str | None = None
    occupancy_type: str | None = None

    # Education application context
    education_product_code: str | None = None

    # Optional targeting hints
    policy_family_hint: str | None = None
    policy_id_hint: str | None = None
    rule_id_hint: str | None = None

    top_k: int | None = None
    debug: bool = False

    @field_validator("query_text")
    @classmethod
    def _strip_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query_text must not be blank")
        return v


class PolicyEvidence(BaseModel):
    """One retrieved, citation-bearing piece of policy evidence."""

    model_config = ConfigDict(extra="forbid")

    product_domain: LendingProductDomain
    chunk_id: str
    policy_id: str
    policy_title: str
    policy_version: str | None = None
    rule_id: str | None = None
    rule_title: str | None = None
    section_number: str | None = None
    section_title: str | None = None
    source_path: str
    source_sha256: str
    effective_date: date | None = None
    expiration_date: date | None = None
    source_category: str | None = None
    severity: str | None = None
    outcome_type: str | None = None
    requires_human_review: bool | None = None
    text: str

    dense_score: float | None = None
    dense_rank: int | None = None
    bm25_score: float | None = None
    bm25_rank: int | None = None
    fusion_score: float | None = None
    reranker_score: float | None = None
    final_rank: int = 0

    citation: str
    citation_resolves: bool = False
    applicability: ApplicabilityStatus = ApplicabilityStatus.UNDETERMINED


class PolicyRetrievalResult(BaseModel):
    """The full outcome of a retrieval call, including why it came out that way."""

    model_config = ConfigDict(extra="forbid")

    status: RetrievalStatus
    product_domain: LendingProductDomain
    query_text: str
    normalized_query: str
    as_of_date: date | None = None
    evidence: list[PolicyEvidence] = Field(default_factory=list)
    message: str | None = None

    dense_candidates: int = 0
    lexical_candidates: int = 0
    fused_candidates: int = 0
    reranked_candidates: int = 0
    filtered_out: int = 0
    latency_ms: float = 0.0
    stage_latency_ms: dict[str, float] = Field(default_factory=dict)
    debug: dict[str, Any] = Field(default_factory=dict)

    @property
    def citations(self) -> list[str]:
        return [e.citation for e in self.evidence]
