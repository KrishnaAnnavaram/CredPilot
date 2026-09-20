"""
Parses the canonical verbatim requirements baseline.

The ONLY source of requirement text in this suite is
``source_requirements/requirements_verbatim.md``.

Nothing else in the suite is allowed to hold a copy of requirement wording: test
cases reference requirements by ID only, and the verbatim text is looked up from
here at run time. That guarantees the "Exact Original Requirement" field printed in
every spec, matrix and report is literally the baseline text and cannot drift.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

SUITE_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = SUITE_ROOT / "source_requirements" / "requirements_verbatim.md"

_REQ_HEADING = re.compile(r"^##\s+(REQ-\d{3})\s*$", re.MULTILINE)
_META_LINE = re.compile(r"^-\s+\*\*(?P<key>[^:*]+):\*\*\s*(?P<value>.*?)\s*$", re.MULTILINE)
_VERBATIM_BLOCK = re.compile(r"^~~~text\n(?P<body>.*?)\n~~~\s*$", re.MULTILINE | re.DOTALL)

VALID_CLASSES = {"IMPLEMENTATION", "OPTIONAL", "ENGAGEMENT"}


@dataclass(frozen=True)
class Requirement:
    """One requirement unit extracted verbatim from the source document."""

    req_id: str
    source_location: str
    source_type: str
    req_class: str
    category: str
    text: str = field(repr=False)

    @property
    def is_mandatory(self) -> bool:
        """Only IMPLEMENTATION requirements gate the final project status.

        OPTIONAL is used strictly where the SOURCE TEXT ITSELF says optional / bonus /
        good-to-have. ENGAGEMENT is used where the statement describes the engagement or
        the evaluator rather than the CredPilot deliverable. Neither classification
        weakens a test: every requirement is still tested and still receives PASS/FAIL.
        """
        return self.req_class == "IMPLEMENTATION"


class BaselineParseError(RuntimeError):
    pass


def _split_blocks(raw: str) -> List[tuple[str, str]]:
    matches = list(_REQ_HEADING.finditer(raw))
    if not matches:
        raise BaselineParseError(f"No '## REQ-nnn' headings found in {BASELINE_PATH}")
    blocks: List[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        blocks.append((m.group(1), raw[start:end]))
    return blocks


@lru_cache(maxsize=1)
def load_requirements(path: str | None = None) -> Dict[str, Requirement]:
    """Load and validate the verbatim baseline. Returns {req_id: Requirement}."""
    baseline = Path(path) if path else BASELINE_PATH
    if not baseline.is_file():
        raise BaselineParseError(f"Requirements baseline is missing: {baseline}")

    raw = baseline.read_text(encoding="utf-8")
    out: Dict[str, Requirement] = {}

    for req_id, body in _split_blocks(raw):
        meta = {m.group("key").strip(): m.group("value").strip() for m in _META_LINE.finditer(body)}
        vb = _VERBATIM_BLOCK.search(body)
        if not vb:
            raise BaselineParseError(f"{req_id}: no '~~~text' verbatim block found")

        req_class = meta.get("Requirement class", "").strip()
        if req_class not in VALID_CLASSES:
            raise BaselineParseError(
                f"{req_id}: Requirement class {req_class!r} not in {sorted(VALID_CLASSES)}"
            )
        if req_id in out:
            raise BaselineParseError(f"Duplicate requirement id {req_id}")

        out[req_id] = Requirement(
            req_id=req_id,
            source_location=meta.get("Source location", "UNSPECIFIED_BY_REQUIREMENT"),
            source_type=meta.get("Source type", "UNSPECIFIED_BY_REQUIREMENT"),
            req_class=req_class,
            category=meta.get("Category", "uncategorised"),
            text=vb.group("body"),
        )

    # IDs must be dense and ordered: REQ-001 .. REQ-<n>. A gap means a dropped requirement.
    expected = [f"REQ-{i:03d}" for i in range(1, len(out) + 1)]
    if list(out.keys()) != expected:
        missing = sorted(set(expected) - set(out))
        extra = sorted(set(out) - set(expected))
        raise BaselineParseError(
            f"Requirement IDs are not a dense ordered sequence. missing={missing} unexpected={extra}"
        )
    return out


def requirement_text(req_id: str) -> str:
    """The EXACT original requirement. Never transformed, never reformatted."""
    reqs = load_requirements()
    if req_id not in reqs:
        raise KeyError(f"{req_id} is not present in the requirements baseline")
    return reqs[req_id].text


if __name__ == "__main__":  # pragma: no cover - manual inspection helper
    from console import use_utf8_console

    use_utf8_console()
    rs = load_requirements()
    print(f"{len(rs)} requirements loaded from {BASELINE_PATH}")
    for r in rs.values():
        print(f"  {r.req_id}  [{r.req_class:<14}] [{r.category:<14}] {r.text[:72]!r}")
