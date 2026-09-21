"""Deterministic query normalization and synonym expansion.

Underwriters and policy documents do not always use the same words for the same
thing: a question says "affordability", the rule says "debt-to-income"; a question
says "cost of attendance", the certification field says "COA". A small, committed
synonym table closes that gap without a model in the loop.

Two deliberate constraints:

* **Lexical layer only.** Expansion terms are appended to the BM25 query. The
  dense query keeps the user's own wording, because embeddings already handle
  paraphrase and padding the query with synonyms degrades the vector.
* **No LLM rewriting.** Gemini is not asked to rewrite queries. That option stays
  open, but it has to earn its place against this baseline in the ablation
  (``docs/rag/RETRIEVAL_ABLATION.md``) before it ships.
"""

from __future__ import annotations

import re
from typing import Iterable, Mapping

from src.domain import LendingProductDomain

#: Bidirectional synonym groups. Every member of a group expands to every other
#: member. Terms are matched on word boundaries, case-insensitively.
_SHARED_GROUPS: tuple[tuple[str, ...], ...] = (
    ("dti", "debt-to-income", "debt to income", "affordability"),
    ("income", "earnings"),
    ("fico", "credit score", "bureau score"),
    ("kyc", "know your customer", "identity verification"),
    ("aml", "anti-money laundering"),
    ("ofac", "sanctions screening"),
    ("residual income", "disposable income"),
    ("cosigner", "co-signer", "co signer"),
)

_MORTGAGE_GROUPS: tuple[tuple[str, ...], ...] = (
    ("ltv", "loan-to-value", "loan to value"),
    ("cltv", "combined loan-to-value"),
    ("hcltv", "home equity combined loan-to-value"),
    ("pitia", "housing expense", "principal interest taxes insurance association dues"),
    ("voe", "verification of employment", "employment verification"),
    ("reserves", "post-closing reserves", "months of reserves"),
    ("cash to close", "funds to close"),
    ("source of funds", "sourcing", "seasoning"),
    ("appraisal", "valuation", "appraised value"),
    ("occupancy", "primary residence", "owner occupied"),
    ("self-employed", "self employed", "business income"),
    ("rate-and-term", "rate and term", "rate_term_refinance"),
    ("cash-out", "cash out", "cash_out_refinance"),
    ("mi", "mortgage insurance"),
    ("aus", "automated underwriting system"),
)

_EDUCATION_GROUPS: tuple[tuple[str, ...], ...] = (
    ("coa", "cost of attendance"),
    ("refi", "refinance", "refinancing"),
    ("ug", "undergraduate"),
    ("gr", "graduate"),
    ("sp", "specialty", "professional"),
    ("intl", "international"),
    ("school certification", "certified eligible amount", "certification"),
    ("title iv", "title 4"),
    ("cdr", "cohort default rate"),
    ("opt", "optional practical training"),
    ("sevis", "student and exchange visitor information system"),
    ("adverse action", "reason code", "decline notice"),
    ("reg z", "regulation z", "truth in lending"),
    ("ecoa", "equal credit opportunity act", "reg b", "regulation b"),
    ("risk grade", "grade band", "pricing matrix"),
)


def _build_map(groups: Iterable[tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
    mapping: dict[str, tuple[str, ...]] = {}
    for group in groups:
        for term in group:
            mapping[term.lower()] = tuple(t for t in group if t.lower() != term.lower())
    return mapping


_MAPS: Mapping[LendingProductDomain, dict[str, tuple[str, ...]]] = {
    LendingProductDomain.MORTGAGE: _build_map(_SHARED_GROUPS + _MORTGAGE_GROUPS),
    LendingProductDomain.EDUCATION_LOAN: _build_map(_SHARED_GROUPS + _EDUCATION_GROUPS),
}

_WS = re.compile(r"\s+")

#: Identifier shapes worth surfacing so exact-id lookups can be detected and the
#: lexical layer can be trusted to carry them.
_ID_PATTERNS = (
    re.compile(r"\bPOL-[A-Z]+-\d{3}\b", re.IGNORECASE),  # mortgage policy id
    re.compile(r"\bPOL-\d{3}\b", re.IGNORECASE),  # education policy id
    re.compile(r"\b[A-Z]{2,6}(?:-[A-Z]{2,6})?-\d{3}\b", re.IGNORECASE),  # rule ids
)


def normalize_query(text: str) -> str:
    """Collapse whitespace and strip surrounding punctuation noise."""
    return _WS.sub(" ", str(text)).strip()


def extract_identifiers(text: str) -> list[str]:
    """Pull policy/rule identifiers out of a query, uppercased and deduplicated."""
    found: list[str] = []
    for pattern in _ID_PATTERNS:
        for match in pattern.finditer(text):
            token = match.group(0).upper()
            if token not in found:
                found.append(token)
    return found


def expand_query(
    text: str, domain: LendingProductDomain, *, enabled: bool = True
) -> tuple[str, list[str]]:
    """Return ``(expanded_query, added_terms)`` for the lexical layer.

    The original query always leads the expanded string, so BM25 still weights the
    user's own wording most heavily.
    """
    normalized = normalize_query(text)
    if not enabled:
        return normalized, []

    lowered = normalized.lower()
    mapping = _MAPS.get(domain, {})
    added: list[str] = []
    for term, synonyms in mapping.items():
        if not re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lowered):
            continue
        for synonym in synonyms:
            if synonym.lower() in lowered or synonym in added:
                continue
            added.append(synonym)

    added.sort()  # deterministic ordering
    return (normalized + " " + " ".join(added)).strip() if added else normalized, added
