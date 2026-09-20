# Source Document Extraction Note

## The two files in this folder

| File | Role |
| --- | --- |
| `Loan_Origination_Underwriting_Copilot_Merged.docx` | **The supplied requirements document.** Authoritative. Five page images, no extractable text. |
| `Loan_Origination_Underwriting_Copilot_Extracted_Text.docx` | **A machine-readable rendering of the same document**, supplied afterwards. Used as an independent cross-check, not as the authority. |

Both were moved (not copied) into this folder, per the strict-folder rule for this task.

## Why the original needed visual transcription

`Loan_Origination_Underwriting_Copilot_Merged.docx` contains **no machine-readable body text**. Its
`word/document.xml` holds five paragraphs, each containing only an embedded picture; the entire
requirements text is delivered as **five page images**:

| Image part in the .docx | Original embedded name | Copied to |
|---|---|---|
| `word/media/image1.png`  | `Screenshot 2026-09-18 at 9.48.55 PM.png` | `pages/page_1.png` |
| `word/media/image2.jpeg` | `BB46D9AF-894F-48AA-8D0C-5CC061B30CA1.jpeg` | `pages/page_2.jpeg` |
| `word/media/image3.jpeg` | `D8595772-8953-4396-AEBF-5DEA93E8E826.jpeg` | `pages/page_3.jpeg` |
| `word/media/image4.jpeg` | `4AD441D1-7EFE-43CB-A6C2-3FB314955859.jpeg` | `pages/page_4.jpeg` |
| `word/media/image5.jpeg` | `CAF4C26F-12F5-4E72-A682-A3AF88C06960.jpeg` | `pages/page_5.jpeg` |

The page images are retained so any reviewer can independently re-verify every verbatim quotation in
`../source_requirements/requirements_verbatim.md` against the original source.

The text was transcribed by direct visual reading of the five images at magnification. The images
overlap, and the whole document body is covered end-to-end with no gaps:

| Page image | Coverage |
|---|---|
| page_1 | Title block → Section 1 → Section 2 → Section 3.1 → 3.2 → 3.3 → heading "3.4 Applicable Rules" |
| page_2 | end of 3.2 → 3.3 (complete) → 3.4 (complete) → Section 4 (complete) → heading "5. Acceptance Criteria & Non-Functional Requirements" → 5.1 → start of 5.2 |
| page_3 | Section 5 (complete: 5.1, 5.2) → Section 6.1 → 6.2 → Section 7 lead-in → 7.1 → start of 7.2 |
| page_4 | Section 6.2 → Section 7 (complete: 7.1 – 7.7) → Section 8 lead-in → start of Section 8 table |
| page_5 | Section 7.7 → Section 8 (complete, incl. continuation table) → 8.1 → closing paragraph (end of document) |

### The overlay hazard, and how it was handled

Pages 1, 3, 4 and 5 carry a floating Google-Docs overlay chip reading **"Summarize this document"**
plus a pencil button, which covers part of the text beneath it.

**No text was guessed.** Every span hidden by the overlay on one page is fully visible, unobscured,
on the overlapping neighbouring page:

* Section 3.3 bullets 3 and 4 — obscured on page_1, read in full from **page_2**.
* Section 5.2 NFR rows — obscured on page_2, read in full from **page_3**.
* Section 7.2 rows — obscured on page_3, read in full from **page_4**.
* Section 8 table rows — obscured on page_4, read in full from **page_5**.

There is therefore no `UNREADABLE_IN_SOURCE` span anywhere in the extraction.

---

## Cross-check against the machine-readable rendering

After the baseline was built, `Loan_Origination_Underwriting_Copilot_Extracted_Text.docx` was
supplied — the same document with real text. Every one of the **112** requirements was compared
against it character by character by `../traceability/verify_against_source.py`, which is
re-runnable at any time:

```bash
python traceability/verify_against_source.py
```

It makes two comparisons:

1. **Direct** — 97 requirements map to one whole paragraph or one whole table row and must match
   exactly.
2. **Reconstruction** — the 6 paragraphs that were split across several requirements must be
   reproducible by joining those requirements back together with single spaces. This catches a
   dropped clause at a split boundary, which a per-requirement comparison alone would miss.

### What the cross-check found

**One transcription error, now corrected.** In the Section 2 `Evaluation Mode` row (now `REQ-010`)
the visual transcription had dropped the words **"in the repository"**. Re-reading `page_1.png` at
4× magnification confirmed the document reads *"…scored entirely from committed evidence **in the
repository**. No live demo judging."* The baseline was corrected to match the source.

**One coverage gap, now closed.** The document's **title block** — the banner line, the title and
the subtitle — had been recorded only as header metadata in the verbatim file rather than as
requirements with IDs. The subtitle uniquely names the seven areas the capstone integrates
("Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance +
Security & Governance + Agent Evaluation"), which appears nowhere else. Those three paragraphs are
now `REQ-001`, `REQ-002` and `REQ-003`, and every requirement after them was renumbered `+3` so that
requirement IDs still run in document order. The count went from 109 to **112**.

**One adjudicated difference, baseline retained.** In the Section 8 `Guardrail code` row
(`REQ-104`), the baseline uses the typographic apostrophe `’` (U+2019) in *"the agent’s input"* and
*"the graph’s I/O nodes"*, while the extracted text normalises both to the straight `'` (U+0027).
`page_5.jpeg` at 8× magnification shows a clearly curly apostrophe with a descending tail in this
row — visibly different from the straight vertical ticks in *"bank's"* (page_1, §3.1) and *"agent's
I/O path"* (page_4, §7.4), which the baseline records as straight. **The source document genuinely
mixes both glyphs, and the baseline preserves that mix.** The original page images decide such
cases, because the extracted-text file is itself a derived rendering of them.

Every other requirement is byte-for-byte identical across the two sources.

---

## Rendering conventions used in `requirements_verbatim.md`

These affect *layout only*. No word, number, symbol or punctuation mark of the source was changed.

1. **Table rows** are written as their cells joined by ` | ` in left-to-right column order.
   * A 2-column row becomes `<cell 1> | <cell 2>` — e.g. `Domain | Banking & Finance`.
   * A 3-column row becomes `<Area> | <Artifact (path)> | <Must contain>`.
   * The **cell contents themselves are character-for-character verbatim**. The ` | ` separator is
     the table's own column boundary made visible in plain text; it is not added wording.
2. **A cell that wraps onto a second line** (e.g. `mcp_server/ +` / `logs/mcp_transcript.jsonl`) is
   written on one line with the wrap rendered as a single space. Whether such a break is a hard
   paragraph break or a soft wrap cannot be determined from a page image, and the cross-check
   collapses intra-cell whitespace on both sides so the comparison is unaffected.
3. **ID-bearing rows** (AC-01 … AC-12, NFR-01 … NFR-06) keep their ID cell as the first cell,
   exactly as printed.
4. **Typography is preserved as printed**: `—` (em dash), `–` (en dash, in "Team of 2–4"), `≥`,
   `·` (middle dot), `→` (arrow), `×` (multiplication sign), `“ ”` (curly double quotes, Section 8),
   `’` (curly apostrophe, Section 8 Guardrail-code row), `'` (straight apostrophe, Sections 3.1, 5.1,
   7.4, 7.6), and the backticks inside Section 8's lead-in paragraph.
5. **Section headings** are recorded in each requirement's `Source location` field as external
   metadata. Headings are not restated as requirement text.
6. **Sentence splitting**: where one source paragraph contains several complete sentences, each
   sentence gets its own requirement ID, quoted in full and unaltered. Where one *sentence* contains
   several independently verifiable obligations, the sentence is kept whole in a single requirement
   record and is covered by **multiple test cases**, as the task's coverage rule requires.

## What is deliberately NOT in the verbatim file

* The iOS status bar (`9:48`, `9:49`, `9:50`, signal/wifi/battery glyphs) at the top of the
  screenshots.
* The Google-Docs chrome: the `◀ Drive` back control, the share / comment / Gemini / overflow icons,
  the page scroll thumb, the "Summarize this document" overlay chip and the pencil edit button.
* The 24 section headings, which are recorded as `Source location` metadata instead.
* The 11 repeated table header rows (`ID | Criterion`, `Area | Artifact (path) | Must contain`,
  `Layer | Approved tool (open source unless noted)`, `Artifact | Format | How to produce it / where
  to get it`) — these are column labels, not requirements.
* A stray full stop that stands alone as its own paragraph between the two Section 2 paragraphs
  (paragraph 9 of the extracted rendering).
* Content repeated because the page images overlap.

None of these are document content; all are viewer UI, headings recorded elsewhere, column labels,
or repetition. Everything that is document content is present in `requirements_verbatim.md`, and
`../traceability/coverage_audit.md` re-verifies that independently.

## Integrity

`requirements_verbatim.md` is hashed. The hash lives in
`../traceability/source_requirements_hash.txt` and is verified before every validation run. See
`../BASELINE_REQUIREMENTS.md`.
