"""Citation construction and resolution.

Every piece of evidence CredPilot hands to an agent carries a citation, and every
citation must resolve to a committed source document. A citation that cannot be
resolved is a hallucination with a reference number on it, so resolution is
checked against the corpus itself — the policy file is opened and the rule id is
found in it — rather than against the index that produced the citation.

Two citation conventions, one per product, because the two corpora and their
golden sets use different ones:

* mortgage — ``POL-DTI-001 v2.0 rule DTI-CONV-001``
* education — ``POL-002 EDU-UW-001``
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from src.config import REPO_ROOT, RagConfig, repo_path
from src.domain import LendingProductDomain, read_text_tolerant
from src.rag.models import build_citation  # re-exported for callers

_MORTGAGE_CITATION = re.compile(
    r"^(?P<policy_id>POL-[A-Z]+-\d{3})"
    r"(?:\s+v(?P<version>[\d.]+))?"
    r"(?:\s+rule\s+(?P<rule_id>[A-Z0-9-]+)|\s+section\s+(?P<section>[\w.]+))?$"
)
_EDUCATION_CITATION = re.compile(
    r"^(?P<policy_id>POL-\d{3})"
    r"(?:\s+v(?P<version>[\d.]+))?"
    r"(?:\s+(?P<rule_id>EDU-[A-Z]+-\d+)|\s+section\s+(?P<section>[\w.]+))?$"
)


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:  # pragma: no cover - only if a corpus moves outside the repo
        return path.as_posix()


@dataclass(frozen=True)
class ParsedCitation:
    product_domain: LendingProductDomain
    policy_id: str
    policy_version: str | None
    rule_id: str | None
    section: str | None
    raw: str


def parse_citation(citation: str) -> ParsedCitation | None:
    """Parse a citation string in either product's convention."""
    text = " ".join(str(citation).split())
    m = _EDUCATION_CITATION.match(text)
    if m:
        return ParsedCitation(
            LendingProductDomain.EDUCATION_LOAN,
            m.group("policy_id"),
            m.group("version"),
            m.group("rule_id"),
            m.group("section"),
            text,
        )
    m = _MORTGAGE_CITATION.match(text)
    if m:
        return ParsedCitation(
            LendingProductDomain.MORTGAGE,
            m.group("policy_id"),
            m.group("version"),
            m.group("rule_id"),
            m.group("section"),
            text,
        )
    return None


@lru_cache(maxsize=4)
def _corpus_map(corpus_root: str) -> dict[tuple[str, str | None], Path]:
    """Map ``(policy_id, version)`` to its source file, scanning front matter."""
    out: dict[tuple[str, str | None], Path] = {}
    for path in sorted(Path(corpus_root).glob("*.md")):
        text = read_text_tolerant(path)
        pid = re.search(r"^policy_id:\s*\"?([A-Za-z0-9-]+)\"?\s*$", text, re.M)
        ver = re.search(r"^version:\s*\"?([\d.]+)\"?\s*$", text, re.M)
        if not pid:
            continue
        version = ver.group(1) if ver else None
        if version and "." not in version:
            version = f"{float(version):.1f}"
        out[(pid.group(1), version)] = path
        out.setdefault((pid.group(1), None), path)
    return out


class CitationResolver:
    """Resolve citations against the committed policy corpora."""

    def __init__(self, config: RagConfig):
        self.config = config

    def source_path_for(self, parsed: ParsedCitation) -> Path | None:
        product = self.config.product(parsed.product_domain)
        mapping = _corpus_map(str(product.corpus_root))
        return mapping.get((parsed.policy_id, parsed.policy_version)) or (
            mapping.get((parsed.policy_id, None)) if parsed.policy_version is None else None
        )

    def resolve(self, citation: str) -> tuple[bool, str]:
        """Return ``(resolves, reason)`` for one citation string."""
        parsed = parse_citation(citation)
        if parsed is None:
            return False, "citation does not match either product's citation grammar"

        path = self.source_path_for(parsed)
        if path is None or not path.exists():
            return False, (
                f"no committed source document for {parsed.policy_id}"
                + (f" v{parsed.policy_version}" if parsed.policy_version else "")
            )

        if parsed.rule_id:
            text = read_text_tolerant(path)
            if not re.search(rf"(?<![A-Z0-9-]){re.escape(parsed.rule_id)}(?![A-Z0-9-])", text):
                return False, f"{parsed.rule_id} does not appear in {path.name}"

        # Repo-relative, so a resolution recorded in a log or a report means the
        # same thing on every checkout.
        return True, f"resolves to {_repo_relative(path)}"

    def citation_exists(self, citation: str) -> bool:
        """Boolean form of :meth:`resolve`."""
        return self.resolve(citation)[0]

    def validate_all(self, citations: Iterable[str]) -> dict[str, tuple[bool, str]]:
        return {c: self.resolve(c) for c in citations}


def citation_exists(citation: str, config: RagConfig | None = None) -> bool:
    """Module-level convenience: does this citation resolve to a committed artifact?"""
    from src.config import get_config

    return CitationResolver(config or get_config()).citation_exists(citation)


__all__ = [
    "CitationResolver",
    "ParsedCitation",
    "build_citation",
    "citation_exists",
    "parse_citation",
    "repo_path",
]
