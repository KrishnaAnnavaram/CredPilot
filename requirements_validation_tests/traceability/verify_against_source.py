"""
Cross-check the verbatim baseline against the machine-readable source document.

The original supplied document is five page images with no extractable text, so the
baseline was transcribed by reading them. A second, machine-readable rendering of the
same document was subsequently supplied:

    source_document/Loan_Origination_Underwriting_Copilot_Extracted_Text.docx

This script compares every requirement in the hashed baseline against that document,
character by character, so the transcription is never taken on trust.

Two comparisons are made:

1. **Direct** - for requirements that map to one whole paragraph or one whole table row,
   the baseline text must equal the document text exactly.
2. **Reconstruction** - for the six paragraphs that were split across several
   requirements, joining those requirements back together with single spaces must
   reproduce the paragraph exactly. This catches a dropped clause at a split boundary,
   which a per-requirement comparison alone would miss.

Adjudicated differences
-----------------------
Where the two sources genuinely disagree, the ORIGINAL PAGE IMAGES decide, because they
are the supplied document; the extracted-text .docx is itself a derived rendering of
them. Each such case is listed in ``ADJUDICATED`` below with the evidence, and is
reported as adjudicated rather than as a failure. Anything not listed there is reported
as an UNEXPECTED difference and makes this script exit non-zero.

Usage
-----
    python traceability/verify_against_source.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SUITE_ROOT))

import bootstrap  # noqa: E402,F401

from console import use_utf8_console  # noqa: E402
from requirement_loader import load_requirements  # noqa: E402

EXTRACTED = (SUITE_ROOT / "source_document"
             / "Loan_Origination_Underwriting_Copilot_Extracted_Text.docx")

#: Differences where the page images were re-read at magnification and found to support
#: the baseline over the extracted-text rendering.
ADJUDICATED: dict[str, str] = {
    "REQ-104": (
        "Apostrophe glyph in \"the agent's input\" / \"the graph's I/O nodes\". The baseline "
        "uses U+2019 (typographic); the extracted text normalises to U+0027 (straight). "
        "page_5.jpeg at 8x magnification shows a curly apostrophe with a descending tail in "
        "this row, distinct from the straight ticks visible in \"bank's\" (page_1, S3.1) and "
        "\"agent's I/O path\" (page_4, S7.4). The source document genuinely mixes both glyphs; "
        "the baseline preserves that."
    ),
}


def load_document() -> tuple[dict[int, str], list[list[list[str]]]]:
    """Return {paragraph_number: text} (1-based) and a list of tables as cell grids."""
    try:
        from docx import Document
        from docx.oxml.ns import qn
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError:  # pragma: no cover
        raise SystemExit(
            "python-docx is required for this cross-check:  pip install python-docx"
        )

    if not EXTRACTED.is_file():
        raise SystemExit(f"Cross-check source not found: {EXTRACTED}")

    doc = Document(str(EXTRACTED))

    def blocks(parent):
        from docx.document import Document as _D
        elm = parent.element.body if isinstance(parent, _D) else parent._tc
        for child in elm.iterchildren():
            if child.tag == qn("w:p"):
                yield Paragraph(child, parent)
            elif child.tag == qn("w:tbl"):
                yield Table(child, parent)

    paragraphs: dict[int, str] = {}
    tables: list[list[list[str]]] = []
    n = 0
    for b in blocks(doc):
        if isinstance(b, Paragraph):
            n += 1
            paragraphs[n] = b.text
        else:
            # A cell that wraps onto a second line carries a newline; the baseline renders
            # a table row on one line, so intra-cell whitespace is collapsed on both sides.
            tables.append([[re.sub(r"\s+", " ", c.text).strip() for c in r.cells] for r in b.rows])
    return paragraphs, tables


def build_expectations(P: dict[int, str], T: list[list[list[str]]]) -> dict[str, str]:
    """Map every requirement ID to the document text it was taken from."""
    def row(table_no: int, row_no: int) -> str:
        return " | ".join(T[table_no - 1][row_no])

    exp: dict[str, str] = {}
    exp["REQ-001"], exp["REQ-002"], exp["REQ-003"] = P[1], P[2], P[3]      # title block
    for i, r in enumerate(range(0, 4)):    exp[f"REQ-{i + 4:03d}"] = row(1, r)    # S1
    for i, r in enumerate(range(0, 6)):    exp[f"REQ-{i + 8:03d}"] = row(2, r)    # S2
    exp["REQ-023"] = P[17]                                                        # S3.3 lead-in
    for i, p in enumerate(range(18, 23)):  exp[f"REQ-{i + 24:03d}"] = P[p]        # S3.3 bullets
    for i, p in enumerate(range(24, 29)):  exp[f"REQ-{i + 29:03d}"] = P[p]        # S3.4 rules
    exp["REQ-034"] = P[30]                                                        # S4 lead-in
    for i, r in enumerate(range(1, 10)):   exp[f"REQ-{i + 35:03d}"] = row(3, r)   # S4 stack
    for i, r in enumerate(range(1, 13)):   exp[f"REQ-{i + 44:03d}"] = row(4, r)   # AC-01..12
    for i, r in enumerate(range(1, 7)):    exp[f"REQ-{i + 56:03d}"] = row(5, r)   # NFR-01..06
    for i, p in enumerate(range(39, 42)):  exp[f"REQ-{i + 62:03d}"] = P[p]        # S6.1
    for i, p in enumerate(range(43, 47)):  exp[f"REQ-{i + 65:03d}"] = P[p]        # S6.2
    for i, r in enumerate(range(1, 6)):    exp[f"REQ-{i + 72:03d}"] = row(6, r)   # S7.1
    for i, r in enumerate(range(1, 5)):    exp[f"REQ-{i + 77:03d}"] = row(7, r)   # S7.2
    for i, r in enumerate(range(1, 3)):    exp[f"REQ-{i + 81:03d}"] = row(8, r)   # S7.3
    for i, r in enumerate(range(1, 4)):    exp[f"REQ-{i + 83:03d}"] = row(9, r)   # S7.4
    for i, r in enumerate(range(1, 5)):    exp[f"REQ-{i + 86:03d}"] = row(10, r)  # S7.5
    for i, r in enumerate(range(1, 5)):    exp[f"REQ-{i + 90:03d}"] = row(11, r)  # S7.6
    for i, r in enumerate(range(1, 3)):    exp[f"REQ-{i + 94:03d}"] = row(12, r)  # S7.7
    for i, r in enumerate(range(1, 11)):   exp[f"REQ-{i + 99:03d}"] = row(13, r)  # S8 table
    for i, p in enumerate(range(67, 70)):  exp[f"REQ-{i + 109:03d}"] = P[p]       # S8.1
    exp["REQ-112"] = P[70]                                                        # closing
    return exp


#: Paragraphs split across several requirements: joining them must rebuild the paragraph.
SPLITS: dict[int, list[str]] = {
    8:  ["REQ-014", "REQ-015"],                 # "What is evaluated: ..."
    10: ["REQ-016", "REQ-017"],                 # "What is not evaluated: ..."
    13: ["REQ-018", "REQ-019", "REQ-020"],      # 3.1 Problem
    15: ["REQ-021", "REQ-022"],                 # 3.2 Your Role
    48: ["REQ-069", "REQ-070", "REQ-071"],      # 7 lead-in
    64: ["REQ-096", "REQ-097", "REQ-098"],      # 8 lead-in
}


def main() -> int:
    use_utf8_console()
    P, T = load_document()
    reqs = load_requirements()
    exp = build_expectations(P, T)

    print("=" * 78)
    print("Verbatim baseline  vs  machine-readable source document")
    print("=" * 78)
    print(f"baseline : source_requirements/requirements_verbatim.md ({len(reqs)} requirements)")
    print(f"document : {EXTRACTED.name} ({len(P)} paragraphs, {len(T)} tables)\n")

    unexpected: list[str] = []
    adjudicated: list[str] = []

    print("1. DIRECT COMPARISON")
    for rid in sorted(exp):
        mine, theirs = reqs[rid].text, exp[rid]
        if mine == theirs:
            continue
        pos = next((i for i, (a, b) in enumerate(zip(mine, theirs)) if a != b), None)
        if rid in ADJUDICATED:
            adjudicated.append(rid)
            print(f"   {rid}  ADJUDICATED -> baseline retained")
            print(f"      {ADJUDICATED[rid]}")
        else:
            unexpected.append(rid)
            print(f"   {rid}  *** UNEXPECTED DIFFERENCE ***")
            print(f"      baseline: {mine}")
            print(f"      document: {theirs}")
            if pos is not None:
                print(f"      first difference at character {pos}: "
                      f"{mine[pos]!r} (U+{ord(mine[pos]):04X}) vs "
                      f"{theirs[pos]!r} (U+{ord(theirs[pos]):04X})")
            else:
                longer, shorter = ((mine, theirs) if len(mine) > len(theirs) else (theirs, mine))
                print(f"      one is a prefix of the other; extra text: {longer[len(shorter):]!r}")
    print(f"   {len(exp) - len(unexpected) - len(adjudicated)} of {len(exp)} identical, "
          f"{len(adjudicated)} adjudicated, {len(unexpected)} unexpected")

    print("\n2. RECONSTRUCTION OF SPLIT PARAGRAPHS")
    recon_bad: list[int] = []
    for pn, rids in SPLITS.items():
        joined = " ".join(reqs[r].text for r in rids)
        ok = joined == P[pn]
        print(f"   P{pn:03d} -> {', '.join(rids)}: {'EXACT' if ok else '*** MISMATCH ***'}")
        if not ok:
            recon_bad.append(pn)
            print(f"      joined  : {joined}")
            print(f"      document: {P[pn]}")

    covered = set(exp) | {r for v in SPLITS.values() for r in v}
    missing = sorted(set(reqs) - covered)
    print("\n3. COVERAGE OF THE CROSS-CHECK")
    print(f"   {len(covered)} of {len(reqs)} requirements compared against the document")
    if missing:
        print(f"   NOT COMPARED: {missing}")

    ok = not unexpected and not recon_bad and not missing
    print("\n" + "=" * 78)
    print("RESULT: " + ("VERBATIM BASELINE VERIFIED AGAINST SOURCE DOCUMENT"
                        if ok else "DISCREPANCIES FOUND - INVESTIGATE BEFORE VALIDATING"))
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
