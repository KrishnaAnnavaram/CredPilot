"""Parser for the U.S. residential mortgage policy corpus.

Every document in ``synthetic_data/mortgage/policy_corpus/`` has the same shape:
YAML front matter, then numbered ``## N. Title`` sections, with the rules living
under ``## 4. Rules`` as ``### RULE-ID — Title`` blocks. A rule block carries its
source category, severity, outcome, applicability, body, parameter table,
evidence, exceptions and cross references — which is exactly the unit
underwriting needs, so a rule block becomes one chunk.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.domain import LendingProductDomain
from src.rag.models import ChunkKind
from src.rag.parsers.base import (
    BasePolicyParser,
    ParsedPolicy,
    PolicyParseError,
    RawSection,
    coerce_date,
    coerce_str_list,
    coerce_version,
)

# "## 4. Rules" / "## 3. Definitions" ...
_H2 = re.compile(r"^##\s+(?:(\d+)\.\s*)?(.+?)\s*$", re.MULTILINE)
# "### DTI-CONV-001 — Maximum back-end debt-to-income"  (em dash or hyphen)
_H3_RULE = re.compile(r"^###\s+([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)\s*[—–-]{1,2}\s*(.+?)\s*$")
_ATTR_LINE = re.compile(
    r"\*\*Source category:\*\*\s*`?([A-Z_]+)`?"
    r"(?:.*?\*\*Severity:\*\*\s*`?([A-Z_]+)`?)?"
    r"(?:.*?\*\*Outcome:\*\*\s*`?([A-Z_]+)`?)?",
    re.DOTALL,
)
_CROSS_REF = re.compile(r"\bPOL-[A-Z]+-\d{3}\b")

#: Sections whose prose is worth retrieving in its own right. "Version history"
#: and "Related policies" are navigation, not underwriting knowledge, and folding
#: them into the overview chunk keeps them retrievable without competing with
#: rules for a slot.
_OVERVIEW_SECTIONS = ("Purpose", "Scope", "Definitions")
_TRAILER_SECTIONS = ("Documentation requirements", "Exceptions and escalation")


class MortgagePolicyParser(BasePolicyParser):
    """Rule-aware parser for the mortgage corpus."""

    product_domain = LendingProductDomain.MORTGAGE

    def _policy_identity(self, fm: dict[str, Any], path: Path) -> tuple[str, str, str | None]:
        policy_id = str(fm.get("policy_id") or "").strip()
        if not policy_id:
            raise PolicyParseError(f"{path.name}: front matter has no policy_id")
        title = str(fm.get("title") or policy_id).strip()
        version = coerce_version(fm.get("version"))
        if not version:
            raise PolicyParseError(f"{path.name}: front matter has no version")
        return policy_id, title, version

    def _split_sections(self, body: str, front_matter: dict[str, Any]) -> list[RawSection]:
        spans = self._h2_spans(body)
        if not spans:
            raise PolicyParseError("no '## N. Title' sections found")

        sections: list[RawSection] = []
        overview_parts: list[str] = []
        declared_rules = set(coerce_str_list(front_matter.get("rule_ids")))
        seen_rules: set[str] = set()

        # The preamble between the H1 and the first H2 carries the document's
        # identity line ("POL-DTI-001 · version 2.0 · effective 2026-07-01") and
        # its synthetic-data disclaimer. Both belong to the overview chunk.
        first_h2 = _H2.search(body)
        preamble = body[: first_h2.start()] if first_h2 else ""
        preamble = re.sub(r"^#\s+.*$", "", preamble, count=1, flags=re.MULTILINE).strip()
        if preamble:
            overview_parts.append(preamble)

        for number, title, text in spans:
            if title in _OVERVIEW_SECTIONS:
                overview_parts.append(f"## {number}. {title}\n\n{text.strip()}")
                continue
            if title == "Rules":
                rule_sections = self._split_rules(text, number)
                seen_rules.update(r.rule_id for r in rule_sections if r.rule_id)
                sections.extend(rule_sections)
                continue
            if title in _TRAILER_SECTIONS:
                sections.append(
                    RawSection(
                        kind=ChunkKind.SECTION,
                        text=text.strip(),
                        heading_path=f"## {number}. {title}",
                        section_number=number,
                        section_title=title,
                    )
                )
                continue
            # Version history / Related policies: keep with the overview so the
            # supersession narrative stays retrievable alongside the scope.
            overview_parts.append(f"## {number}. {title}\n\n{text.strip()}")

        missing = declared_rules - seen_rules
        if missing:
            raise PolicyParseError(
                f"front matter declares rules absent from the body: {sorted(missing)}"
            )
        extra = seen_rules - declared_rules
        if extra:
            raise PolicyParseError(
                f"body contains rules not declared in front matter: {sorted(extra)}"
            )

        overview = RawSection(
            kind=ChunkKind.OVERVIEW,
            text="\n\n".join(overview_parts).strip(),
            heading_path="Purpose and scope",
            section_title="Purpose and scope",
        )
        return [overview] + sections

    @staticmethod
    def _h2_spans(body: str) -> list[tuple[str, str, str]]:
        matches = list(_H2.finditer(body))
        spans: list[tuple[str, str, str]] = []
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            number = m.group(1) or ""
            spans.append((number, m.group(2).strip(), body[m.end() : end]))
        return spans

    def _split_rules(self, rules_body: str, section_number: str) -> list[RawSection]:
        """Split the Rules section into one span per ``### RULE-ID — Title``."""
        lines = rules_body.splitlines()
        starts: list[tuple[int, str, str]] = []
        for idx, line in enumerate(lines):
            m = _H3_RULE.match(line)
            if m:
                starts.append((idx, m.group(1), m.group(2).strip()))
        if not starts:
            raise PolicyParseError("Rules section contains no '### RULE-ID — Title' headings")

        out: list[RawSection] = []
        for i, (start, rule_id, rule_title) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
            block = "\n".join(lines[start:end]).strip()
            attrs = _ATTR_LINE.search(block)
            out.append(
                RawSection(
                    kind=ChunkKind.RULE,
                    text=block,
                    heading_path=f"## {section_number}. Rules > ### {rule_id} — {rule_title}",
                    rule_id=rule_id,
                    rule_title=rule_title,
                    section_number=section_number,
                    section_title="Rules",
                    extra={
                        "source_category": attrs.group(1) if attrs else None,
                        "severity": attrs.group(2) if attrs else None,
                        "outcome_type": attrs.group(3) if attrs else None,
                        "cross_refs": sorted(set(_CROSS_REF.findall(block))),
                    },
                )
            )
        return out

    def _chunk_metadata(self, parsed: ParsedPolicy, section: RawSection) -> dict[str, Any]:
        fm = parsed.front_matter
        extra = section.extra
        return {
            "effective_date": coerce_date(fm.get("effective_date")),
            "expiration_date": coerce_date(fm.get("expiration_date")),
            # A rule declares its own source category; the document's is the fallback.
            "source_category": extra.get("source_category") or fm.get("source_category"),
            "jurisdiction": fm.get("jurisdiction"),
            "priority": int(fm["priority"]) if fm.get("priority") is not None else None,
            "supersedes": fm.get("supersedes"),
            "superseded_by": fm.get("superseded_by"),
            "requires_human_review": (
                bool(fm["requires_human_review"])
                if fm.get("requires_human_review") is not None
                else None
            ),
            "issuer": fm.get("issuer"),
            "severity": extra.get("severity"),
            "outcome_type": extra.get("outcome_type"),
            "policy_family": fm.get("family"),
            "product_scope": coerce_str_list(fm.get("product_scope")),
            "occupancy_scope": coerce_str_list(fm.get("occupancy_scope")),
            "purpose_scope": coerce_str_list(fm.get("purpose_scope")),
            "cross_refs": extra.get("cross_refs") or [],
        }
