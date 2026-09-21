"""Product-specific policy parsers behind one common interface."""

from __future__ import annotations

from src.domain import LendingProductDomain
from src.rag.parsers.base import (
    BasePolicyParser,
    ParsedPolicy,
    PolicyParseError,
    RawSection,
)
from src.rag.parsers.education import EducationPolicyParser
from src.rag.parsers.mortgage import MortgagePolicyParser

_PARSERS: dict[str, type[BasePolicyParser]] = {
    "mortgage": MortgagePolicyParser,
    "education": EducationPolicyParser,
}


def get_parser(
    name_or_domain: "str | LendingProductDomain", **kwargs
) -> BasePolicyParser:
    """Return the parser for a product, by parser name or product domain."""
    key = str(getattr(name_or_domain, "corpus_key", name_or_domain)).lower()
    if key not in _PARSERS:
        try:
            key = LendingProductDomain.from_any(key).corpus_key
        except ValueError as exc:
            raise KeyError(f"no policy parser for {name_or_domain!r}") from exc
    return _PARSERS[key](**kwargs)


__all__ = [
    "BasePolicyParser",
    "EducationPolicyParser",
    "MortgagePolicyParser",
    "ParsedPolicy",
    "PolicyParseError",
    "RawSection",
    "get_parser",
]
