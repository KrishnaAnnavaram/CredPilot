"""Lending product domains and deterministic product resolution.

CredPilot serves two independent lending products. Their AI infrastructure is
shared; their *business knowledge* is not. Every retrieval operation in the
system must therefore know which product domain it is operating in before it
touches a policy corpus, and that decision is made here from structured facts —
never from free text supplied by an applicant.
"""

from __future__ import annotations

import json
import re
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class LendingProductDomain(str, Enum):
    """The lending products CredPilot underwrites.

    The value is the canonical wire form used in metadata, logs and traces.
    """

    MORTGAGE = "MORTGAGE"
    EDUCATION_LOAN = "EDUCATION_LOAN"

    @property
    def corpus_key(self) -> str:
        """Short key used in config, paths and chunk-id prefixes."""
        return "mortgage" if self is LendingProductDomain.MORTGAGE else "education"

    @property
    def chunk_prefix(self) -> str:
        return "MORTGAGE" if self is LendingProductDomain.MORTGAGE else "EDUCATION"

    @classmethod
    def from_any(cls, value: "str | LendingProductDomain") -> "LendingProductDomain":
        """Accept the enum, its value, or the short corpus key."""
        if isinstance(value, cls):
            return value
        key = str(value).strip().upper()
        if key in ("MORTGAGE", "MTG"):
            return cls.MORTGAGE
        if key in ("EDUCATION_LOAN", "EDUCATION", "EDU", "STUDENT_LOAN"):
            return cls.EDUCATION_LOAN
        raise ValueError(f"unknown lending product domain: {value!r}")


class ProductResolutionError(ValueError):
    """Raised when the product domain cannot be established from structured facts."""


#: Sentinel status returned instead of guessing. Callers must escalate, not search both.
PRODUCT_CLARIFICATION_REQUIRED = "PRODUCT_CLARIFICATION_REQUIRED"

# Application-id shapes, verified against the committed corpora:
#   mortgage   APP-000001 .. APP-000075     -> APP-<6 digits>
#   education  APP-2026-00001 .. APP-2026-00200 -> APP-<4-digit year>-<5 digits>
_MORTGAGE_APP_ID = re.compile(r"^APP-\d{6}$")
_EDUCATION_APP_ID = re.compile(r"^APP-\d{4}-\d{5}$")

# Structural discriminators on the application packet itself. A mortgage packet
# carries a `borrowers` array and a `subject_property`; an education packet
# carries a single `borrower` and a `school`.
_MORTGAGE_KEYS = frozenset({"subject_property", "borrowers", "product_family", "loan_purpose"})
_EDUCATION_KEYS = frozenset({"school", "school_certification", "product_code", "borrower"})


def domain_from_application_id(application_id: str) -> LendingProductDomain | None:
    """Resolve the product domain from an application identifier alone.

    Returns ``None`` when the identifier does not match a known shape; the
    caller decides whether another signal is available or clarification is due.
    """
    if not application_id:
        return None
    aid = application_id.strip().upper()
    if _MORTGAGE_APP_ID.match(aid):
        return LendingProductDomain.MORTGAGE
    if _EDUCATION_APP_ID.match(aid):
        return LendingProductDomain.EDUCATION_LOAN
    return None


def domain_from_packet(packet: Mapping[str, Any]) -> LendingProductDomain | None:
    """Resolve the product domain from the shape of an application packet."""
    if not isinstance(packet, Mapping):
        return None
    keys = set(packet.keys())
    mortgage_hits = len(keys & _MORTGAGE_KEYS)
    education_hits = len(keys & _EDUCATION_KEYS)
    if mortgage_hits > education_hits and mortgage_hits >= 2:
        return LendingProductDomain.MORTGAGE
    if education_hits > mortgage_hits and education_hits >= 2:
        return LendingProductDomain.EDUCATION_LOAN
    return None


def resolve_product_domain(
    *,
    explicit_domain: "str | LendingProductDomain | None" = None,
    application_id: str | None = None,
    packet: Mapping[str, Any] | None = None,
    graph_state: Mapping[str, Any] | None = None,
) -> LendingProductDomain:
    """Deterministically resolve the lending product domain.

    Signals are consulted in descending order of authority:

    1. an explicit domain passed by the caller,
    2. the current graph state's ``loan_domain``,
    3. the application identifier's shape,
    4. the structural shape of the application packet.

    Free-text applicant input is never a signal. When no structured fact settles
    the question this raises :class:`ProductResolutionError` rather than guessing
    — searching both corpora and letting the model pick is exactly the failure
    mode product isolation exists to prevent.
    """
    if explicit_domain is not None:
        return LendingProductDomain.from_any(explicit_domain)

    if graph_state:
        state_domain = graph_state.get("loan_domain")
        if state_domain:
            return LendingProductDomain.from_any(state_domain)
        if not application_id:
            application_id = graph_state.get("application_id")
        if packet is None:
            packet = graph_state.get("application_packet")

    if application_id:
        by_id = domain_from_application_id(application_id)
        if by_id is not None:
            return by_id

    if packet is not None:
        by_shape = domain_from_packet(packet)
        if by_shape is not None:
            return by_shape

    raise ProductResolutionError(
        f"{PRODUCT_CLARIFICATION_REQUIRED}: no structured signal identifies the lending "
        f"product (application_id={application_id!r}). Escalate for clarification; do not "
        f"search both policy corpora."
    )


def read_text_tolerant(path: "str | Path") -> str:
    """Read a text file, tolerating the non-UTF-8 files present in the corpus.

    Five committed education application packets are cp1252-encoded rather than
    UTF-8 (see ``docs/rag/DATA_QUALITY_FINDINGS.md``). Runtime code must not fall
    over on them, so decoding falls back to cp1252 and finally to lossy UTF-8.
    """
    raw = Path(path).read_bytes()
    for encoding in ("utf-8", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_application(path: "str | Path") -> dict[str, Any]:
    """Load an application packet from either corpus, tolerating encoding drift."""
    return json.loads(read_text_tolerant(path))
