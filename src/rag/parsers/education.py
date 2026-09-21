"""Parser for the private education-loan policy corpus.

The twelve documents in ``synthetic_data/education/policy_corpus/`` are laid out
differently from the mortgage corpus. Front matter is lighter (no occupancy or
purpose scope, no supersession chain, and two different key spellings for the
product list), and rules are marked by a bold ``**EDU-XXX-000 — Title**`` line
inside a numbered ``## N. Title`` section rather than by their own heading.

The corpus does carry stable rule identifiers, so rule-level chunking applies
here too. Sections that contain no rule marker — purpose statements, reason-code
dictionaries, review cycles — become section-level chunks rather than being
dropped, so every line of every document is represented somewhere in the index.
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

_H2 = re.compile(r"^##\s+(?:(\d+)\.\s*)?(.+?)\s*$", re.MULTILINE)
# "**EDU-UW-001 -- Undergraduate Underwriting Criteria.**" (POL-001..006 use "--",
# POL-007..012 use an em dash; some end the title with a period, some do not).
# The marker opens a line but need not end it — in POL-001 the rule body runs on
# from the closing "**" on the same line.
_RULE_MARKER = re.compile(
    r"^\*\*(EDU-[A-Z]+-\d+)\s*[—–-]{1,2}\s*([^*]+?)\.?\*\*", re.MULTILINE
)
_CROSS_REF = re.compile(r"\bPOL-\d{3}\b")

_PURPOSE_SECTIONS = ("Purpose", "Overview", "Purpose and Scope", "Scope")


class EducationPolicyParser(BasePolicyParser):
    """Rule-aware parser for the education-loan corpus."""

    product_domain = LendingProductDomain.EDUCATION_LOAN

    def _policy_identity(self, fm: dict[str, Any], path: Path) -> tuple[str, str, str | None]:
        policy_id = str(fm.get("policy_id") or "").strip()
        if not policy_id:
            raise PolicyParseError(f"{path.name}: front matter has no policy_id")
        title = str(fm.get("title") or policy_id).strip()
        # Every education document declares a version; unlike mortgage there is
        # only ever one published version per policy_id in this corpus.
        version = coerce_version(fm.get("version"))
        return policy_id, title, version

    def _split_sections(self, body: str, front_matter: dict[str, Any]) -> list[RawSection]:
        matches = list(_H2.finditer(body))
        if not matches:
            raise PolicyParseError("no '## N. Title' sections found")

        declared_rules = set(coerce_str_list(front_matter.get("rule_ids")))
        seen_rules: set[str] = set()

        sections: list[RawSection] = []
        overview_parts: list[str] = []

        # Any preamble between the H1 and the first H2 belongs to the overview.
        preamble = body[: matches[0].start()]
        preamble = re.sub(r"^#\s+.*$", "", preamble, count=1, flags=re.MULTILINE).strip()
        if preamble:
            overview_parts.append(preamble)

        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            number = m.group(1) or ""
            title = m.group(2).strip()
            text = body[m.end() : end].strip()
            if not text:
                continue

            heading = f"## {number}. {title}" if number else f"## {title}"
            rule_spans = self._split_rules(text, heading, number, title)
            if rule_spans:
                seen_rules.update(r.rule_id for r in rule_spans if r.rule_id)
                sections.extend(rule_spans)
            elif title in _PURPOSE_SECTIONS:
                overview_parts.append(f"{heading}\n\n{text}")
            else:
                sections.append(
                    RawSection(
                        kind=ChunkKind.SECTION,
                        text=f"{heading}\n\n{text}",
                        heading_path=heading,
                        section_number=number or None,
                        section_title=title,
                        extra={"cross_refs": sorted(set(_CROSS_REF.findall(text)))},
                    )
                )

        missing = declared_rules - seen_rules
        if missing:
            raise PolicyParseError(
                f"front matter declares rules absent from the body: {sorted(missing)}"
            )
        extra_rules = seen_rules - declared_rules
        if extra_rules:
            raise PolicyParseError(
                f"body contains rules not declared in front matter: {sorted(extra_rules)}"
            )

        overview = RawSection(
            kind=ChunkKind.OVERVIEW,
            text="\n\n".join(p for p in overview_parts if p).strip(),
            heading_path="Purpose and scope",
            section_title="Purpose and scope",
        )
        return ([overview] if overview.text else []) + sections

    def _split_rules(
        self, section_text: str, heading: str, number: str, title: str
    ) -> list[RawSection]:
        """Split a section at its bold rule markers.

        Prose ahead of the first marker is prepended to that first rule rather
        than dropped — in this corpus it is the lead-in that scopes the rule.
        """
        markers = list(_RULE_MARKER.finditer(section_text))
        if not markers:
            return []

        lead_in = section_text[: markers[0].start()].strip()
        out: list[RawSection] = []
        for i, m in enumerate(markers):
            end = markers[i + 1].start() if i + 1 < len(markers) else len(section_text)
            block = section_text[m.start() : end].strip()
            rule_id, rule_title = m.group(1), m.group(2).strip()
            body = f"{heading}\n\n{lead_in}\n\n{block}" if (i == 0 and lead_in) else f"{heading}\n\n{block}"
            out.append(
                RawSection(
                    kind=ChunkKind.RULE,
                    text=body.strip(),
                    heading_path=f"{heading} > {rule_id} — {rule_title}",
                    rule_id=rule_id,
                    rule_title=rule_title,
                    section_number=number or None,
                    section_title=title,
                    extra={"cross_refs": sorted(set(_CROSS_REF.findall(block)))},
                )
            )
        return out

    def _chunk_metadata(self, parsed: ParsedPolicy, section: RawSection) -> dict[str, Any]:
        fm = parsed.front_matter
        # POL-001..006 spell the product list `product_scope`; POL-007..012 spell
        # it `products`. Both mean the five education loan programmes.
        product_scope = coerce_str_list(fm.get("product_scope") or fm.get("products"))
        return {
            "effective_date": coerce_date(fm.get("effective_date")),
            # No education policy in this corpus declares an expiration date or a
            # supersession chain. Those stay None rather than being invented.
            "expiration_date": coerce_date(fm.get("expiration_date")),
            "source_category": fm.get("source_category") or fm.get("classification"),
            "jurisdiction": fm.get("jurisdiction"),
            "priority": int(fm["priority"]) if fm.get("priority") is not None else None,
            "supersedes": fm.get("supersedes"),
            "superseded_by": fm.get("superseded_by"),
            "requires_human_review": (
                bool(fm["requires_human_review"])
                if fm.get("requires_human_review") is not None
                else None
            ),
            "issuer": fm.get("issuer") or fm.get("lender"),
            "severity": None,
            "outcome_type": None,
            "policy_family": None,
            "product_scope": product_scope,
            "occupancy_scope": [],
            "purpose_scope": [],
            "cross_refs": section.extra.get("cross_refs") or [],
        }
