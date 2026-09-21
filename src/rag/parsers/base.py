"""Common parsing machinery for both lending-policy corpora.

The two corpora are genuinely different documents. Mortgage policies carry a rich
YAML front matter and a ``### RULE-ID — Title`` heading per rule; education
policies carry a lighter front matter and mark rules with a bold
``**EDU-XXX-000 — Title**`` line beneath a numbered section heading. Each gets
its own parser; both emit the same :class:`~src.rag.models.PolicyChunk`.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

import yaml

from src.config import REPO_ROOT
from src.domain import LendingProductDomain, read_text_tolerant
from src.rag.models import ChunkKind, PolicyChunk, sha256_file

_FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class PolicyParseError(ValueError):
    """Raised when a policy document cannot be parsed into chunks."""


@dataclass
class RawSection:
    """A contiguous span of a policy document, before chunk assembly."""

    kind: ChunkKind
    text: str
    heading_path: str
    rule_id: str | None = None
    rule_title: str | None = None
    section_number: str | None = None
    section_title: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    start_line: int = 0
    end_line: int = 0


@dataclass
class ParsedPolicy:
    """A parsed policy document: its front matter plus its ordered sections."""

    policy_id: str
    policy_title: str
    policy_version: str | None
    source_path: str
    source_sha256: str
    front_matter: dict[str, Any]
    sections: list[RawSection]
    body_line_count: int


def parse_front_matter(text: str, source_path: str) -> tuple[dict[str, Any], str, int]:
    """Split YAML front matter from the document body.

    Returns ``(front_matter, body, body_start_line)``.
    """
    m = _FRONT_MATTER.match(text)
    if not m:
        raise PolicyParseError(f"{source_path}: no YAML front matter")
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - corpus is well-formed
        raise PolicyParseError(f"{source_path}: malformed front matter: {exc}") from exc
    if not isinstance(fm, dict):
        raise PolicyParseError(f"{source_path}: front matter is not a mapping")
    body = text[m.end() :]
    body_start_line = text[: m.end()].count("\n")
    return fm, body, body_start_line


def coerce_date(value: Any) -> date | None:
    """Coerce a front-matter date value to :class:`datetime.date`.

    YAML already gives ``date`` for unquoted ISO dates; quoted ones arrive as
    strings. ``null`` stays ``None`` — an absent expiry is open-ended, not a
    date to invent.
    """
    if value in (None, "", "null"):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    raise PolicyParseError(f"cannot coerce {value!r} to a date")


def coerce_str_list(value: Any) -> list[str]:
    """Normalize a scalar / list / pipe-joined front-matter value to a list of str."""
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [p.strip() for p in value.split("|") if p.strip()]
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value)]


def coerce_version(value: Any) -> str | None:
    """Render a version as it appears in citations: ``2.0``, never ``2``."""
    if value in (None, ""):
        return None
    if isinstance(value, float):
        return f"{value:.1f}"
    s = str(value).strip().lstrip("vV")
    return s or None


def relative_source_path(path: Path) -> str:
    """Repo-relative, forward-slashed path — stable across platforms."""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:  # pragma: no cover - only if corpus moves outside the repo
        return path.as_posix()


class BasePolicyParser(ABC):
    """Parse one product's policy corpus into normalized chunks."""

    product_domain: LendingProductDomain

    def __init__(self, *, max_chars: int = 4200, overlap_chars: int = 200, min_chars: int = 40):
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars
        self.min_chars = min_chars

    # ---- subclass surface -------------------------------------------------------

    @abstractmethod
    def _split_sections(self, body: str, front_matter: dict[str, Any]) -> list[RawSection]:
        """Split a document body into ordered raw sections."""

    @abstractmethod
    def _policy_identity(self, fm: dict[str, Any], path: Path) -> tuple[str, str, str | None]:
        """Return ``(policy_id, policy_title, policy_version)``."""

    @abstractmethod
    def _chunk_metadata(
        self, parsed: ParsedPolicy, section: RawSection
    ) -> dict[str, Any]:
        """Product-specific metadata for one chunk."""

    # ---- shared behaviour -------------------------------------------------------

    def corpus_files(self, corpus_root: Path) -> list[Path]:
        """Every markdown policy document in the corpus, in a stable order."""
        return sorted(p for p in Path(corpus_root).glob("*.md") if p.is_file())

    def parse_document(self, path: Path) -> ParsedPolicy:
        text = read_text_tolerant(path)
        source_path = relative_source_path(path)
        fm, body, _ = parse_front_matter(text, source_path)
        policy_id, policy_title, policy_version = self._policy_identity(fm, path)
        sections = self._split_sections(body, fm)
        if not sections:
            raise PolicyParseError(f"{source_path}: produced no sections")
        return ParsedPolicy(
            policy_id=policy_id,
            policy_title=policy_title,
            policy_version=policy_version,
            source_path=source_path,
            source_sha256=sha256_file(str(path)),
            front_matter=fm,
            sections=sections,
            body_line_count=body.count("\n") + 1,
        )

    def chunk_document(self, parsed: ParsedPolicy) -> list[PolicyChunk]:
        """Turn a parsed document into chunks, splitting only oversized sections."""
        chunks: list[PolicyChunk] = []
        for chunk_index, section in enumerate(parsed.sections):
            body = section.text.strip()
            if len(body) < self.min_chars:
                continue
            parts = self._secondary_split(body, section)
            for part_index, part_text in enumerate(parts):
                meta = self._chunk_metadata(parsed, section)
                chunk_id = self._chunk_id(parsed, section, chunk_index, part_index)
                chunks.append(
                    PolicyChunk(
                        chunk_id=chunk_id,
                        product_domain=self.product_domain,
                        chunk_kind=section.kind,
                        chunk_index=chunk_index,
                        part_index=part_index,
                        part_count=len(parts),
                        policy_id=parsed.policy_id,
                        policy_title=parsed.policy_title,
                        policy_version=parsed.policy_version,
                        source_path=parsed.source_path,
                        source_sha256=parsed.source_sha256,
                        rule_id=section.rule_id,
                        rule_title=section.rule_title,
                        section_number=section.section_number,
                        section_title=section.section_title,
                        heading_path=section.heading_path,
                        text=part_text,
                        **meta,
                    )
                )
        return chunks

    def parse_corpus(self, corpus_root: Path) -> tuple[list[PolicyChunk], list[ParsedPolicy]]:
        """Parse and chunk an entire corpus.

        Raises rather than skipping: a policy that cannot be parsed must not be
        silently absent from the index.
        """
        parsed_docs: list[ParsedPolicy] = []
        chunks: list[PolicyChunk] = []
        for path in self.corpus_files(corpus_root):
            parsed = self.parse_document(path)
            doc_chunks = self.chunk_document(parsed)
            if not doc_chunks:
                raise PolicyParseError(f"{parsed.source_path}: produced no chunks")
            parsed_docs.append(parsed)
            chunks.extend(doc_chunks)
        return chunks, parsed_docs

    # ---- internals --------------------------------------------------------------

    def _chunk_id(
        self, parsed: ParsedPolicy, section: RawSection, chunk_index: int, part_index: int
    ) -> str:
        """Deterministic chunk id.

        Same corpus plus same chunking code yields the same ids, every run. The
        unit key is the rule id where one exists and the section number where one
        does not — never a hash of the text, which would churn on any edit.
        """
        prefix = self.product_domain.chunk_prefix
        version = f"v{parsed.policy_version}" if parsed.policy_version else "vNA"
        if section.rule_id:
            unit = section.rule_id
        elif section.kind is ChunkKind.OVERVIEW:
            unit = "OVERVIEW"
        elif section.section_number:
            unit = "S" + re.sub(r"[^0-9A-Za-z]+", "-", section.section_number).strip("-")
        else:  # pragma: no cover - every section carries one of the above
            unit = f"IDX{chunk_index:03d}"
        return f"{prefix}__{parsed.policy_id}__{version}__{unit}__{part_index:03d}"

    def _secondary_split(self, body: str, section: RawSection) -> list[str]:
        """Split an oversized section at paragraph boundaries, keeping the heading.

        A rule is only split when it genuinely exceeds ``max_chars``; a threshold
        must never be separated from the rule that sets it by an arbitrary window.
        """
        if len(body) <= self.max_chars:
            return [body]

        heading = section.heading_path.strip()
        header_line = f"{heading}\n\n" if heading else ""
        budget = max(self.max_chars - len(header_line), self.min_chars * 4)

        paragraphs = [p for p in re.split(r"\n{2,}", body) if p.strip()]
        parts: list[str] = []
        current: list[str] = []
        current_len = 0
        for para in paragraphs:
            para_len = len(para) + 2
            if current and current_len + para_len > budget:
                parts.append("\n\n".join(current))
                tail = current[-1] if len(current[-1]) <= self.overlap_chars else ""
                current = [tail] if tail else []
                current_len = len(tail) + 2 if tail else 0
            current.append(para)
            current_len += para_len
        if current:
            parts.append("\n\n".join(current))

        return [header_line + p if i else p for i, p in enumerate(parts)] or [body]


def iter_chunks_by_policy(chunks: Iterable[PolicyChunk]) -> dict[str, list[PolicyChunk]]:
    grouped: dict[str, list[PolicyChunk]] = {}
    for c in chunks:
        grouped.setdefault(f"{c.policy_id}|{c.policy_version}", []).append(c)
    return grouped
