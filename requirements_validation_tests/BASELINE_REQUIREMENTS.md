# CredPilot — Requirements Baseline Declaration

## Origin of this baseline

The requirement baseline held in
[`source_requirements/requirements_verbatim.md`](source_requirements/requirements_verbatim.md)
**originated solely from the supplied source document**:

    source_document/Loan_Origination_Underwriting_Copilot_Merged.docx

That document was supplied as the requirements specification for CredPilot and has been moved into
this folder so the baseline and its source travel together. It is titled *Agentic AI Engineer
Pathway — Capstone Hackathon / Loan Origination & Underwriting Copilot*, Business Case
BC-AAIE-HACK-02.

The `.docx` carries no machine-readable body text: the entire specification is five page images
embedded in it. Those images were extracted to `source_document/pages/` and transcribed by direct
visual reading. [`source_document/EXTRACTION_NOTE.md`](source_document/EXTRACTION_NOTE.md) records
the page-by-page coverage map, the rendering conventions used for table rows, and how the one
transcription hazard (a floating UI overlay on four pages) was resolved without guessing — every
span it covered is legible in full on an overlapping neighbouring page.

**112 requirement units** were extracted.

## Cross-check against a machine-readable rendering

A second file was subsequently supplied and also moved into `source_document/`:

    source_document/Loan_Origination_Underwriting_Copilot_Extracted_Text.docx

It is the same document with real, extractable text. It is **not** the authority — it is itself a
rendering of the page images — but it makes an independent character-by-character verification of
the transcription possible. That verification is automated and re-runnable:

```bash
python traceability/verify_against_source.py
```

It compares all 112 requirements two ways: directly for the 97 that map to one whole paragraph or
table row, and by **reconstruction** for the 6 paragraphs split across several requirements, where
rejoining those requirements must reproduce the paragraph exactly. The reconstruction check is what
catches a clause dropped at a split boundary.

### Corrections this cross-check produced

| Finding | Action |
| --- | --- |
| The Section 2 `Evaluation Mode` row was missing the words **"in the repository"**. | Corrected. Re-reading `pages/page_1.png` at 4× confirmed the document reads *"…scored entirely from committed evidence **in the repository**. No live demo judging."* Now `REQ-010`. |
| The document's **title block** (banner, title, subtitle) had been recorded only as header metadata, not as requirements. The subtitle uniquely names the seven cross-cutting areas. | Closed. Added as `REQ-001`, `REQ-002`, `REQ-003`; all later requirements renumbered `+3` so IDs still run in document order. 109 → **112**. |
| `REQ-104` uses `’` (U+2019) where the extracted text has `'` (U+0027). | **Baseline retained.** `pages/page_5.jpeg` at 8× shows a curly apostrophe with a descending tail in that row, visibly different from the straight ticks in *"bank's"* (page_1) and *"agent's I/O path"* (page_4). The document genuinely mixes both glyphs. Recorded as an adjudicated difference in `verify_against_source.py`. |

Every other requirement is byte-for-byte identical across the two sources. Where the two disagree,
**the original page images decide**, because they are the supplied document.

## What this baseline guarantees

1. **Verbatim.** Every `~~~text` block in `requirements_verbatim.md` is a character-for-character
   quotation of the source document. Nothing was paraphrased, summarised, reworded, corrected,
   simplified, reordered or dropped.
2. **IDs are external metadata.** `REQ-001` … `REQ-112` do not appear in the source document. They
   are QA-layer labels. They do not alter the requirement text in any way.
3. **No invented requirements.** Every requirement record names the section, table row or sentence
   it came from. There is no requirement in this baseline that is not in the source document.
4. **Nothing silently skipped.** Requirement IDs form a dense sequence `REQ-001..REQ-112` with no
   gaps, and `traceability/coverage_audit.md` re-verifies that independently.
5. **Single source of requirement text.** No other file in this suite stores requirement wording.
   Test cases reference requirements by ID only; the exact text printed in every specification,
   matrix row and report line is read back from this baseline at run time. It cannot drift.
6. **Gaps are recorded, not filled.** Where the document states an obligation but fixes no value to
   test against — a DTI threshold, a "high-value" boundary, the submission cut-off, LangGraph's
   licence artifact — the test records `UNSPECIFIED_BY_REQUIREMENT`. No threshold, path or limit was
   invented to make a test executable.

## Baseline protection

The baseline is hashed. The digest lives in
[`traceability/source_requirements_hash.txt`](traceability/source_requirements_hash.txt):

```
sha256(source_requirements/requirements_verbatim.md)
```

**Before every validation run the hash is verified.** Both entry points do this:

* `runners/run_all_tests.py` — checks first, and exits with code `3` on a mismatch.
* `pytest` — `conftest.py` aborts the session via `pytest_sessionstart`.

If the baseline no longer matches its recorded hash, validation **STOPS** and reports:

```
REQUIREMENTS_BASELINE_MODIFIED
```

This exists for one reason: so that a failing implementation can never be made to pass by quietly
editing the requirements.

### Legitimately changing the baseline

Only when the **source document itself** is revised. The procedure is:

1. Replace the document in `source_document/` and re-extract the affected requirement text verbatim.
2. Update `source_document/EXTRACTION_NOTE.md` to describe the new source.
3. Run `python traceability/build_traceability.py --rewrite-hash`.
4. Say so explicitly in the commit message.

Editing `source_requirements_hash.txt` on its own, to silence a mismatch, defeats the entire control.

## Rules this suite operates under

These are fixed and are not to be relaxed to accommodate an implementation:

* **The requirements define expected behaviour. The implementation does not.** Test expectations are
  never rewritten to match how CredPilot currently behaves.
* **No evidence is a FAIL.** A PASS must carry concrete evidence: a resolved path, a matched line
  with its line number, a record count, a `git ls-files` entry, captured process output. "Appears
  implemented", "probably supported" and "seems fine" are not evidence and cannot be produced by
  this suite — every check returns a factual string or fails.
* **Partial implementation is a FAIL.** A requirement passes only when *every* test bound to it
  passes. A partial fit score does not earn a PASS.
* **The suite is external.** Nothing here is imported by, depended on by, or copied into the
  CredPilot implementation, and nothing under `requirements_validation_tests/` is ever scanned as
  implementation evidence. The QA layer cannot satisfy the requirements it grades.
* **Do not weaken a test to turn a FAIL into a PASS.** If CredPilot fails a requirement, the report
  says FAIL and the implementation is what changes.

## A note on requirement classes

Each requirement carries an external `Requirement class` used **only for report grouping**. It never
changes whether a test runs or how strictly it is judged — every requirement is tested and every
requirement gets a PASS/FAIL and a fit score.

| Class | Meaning | Gates the final status |
| --- | --- | --- |
| `IMPLEMENTATION` | The statement constrains the CredPilot deliverable. | **Yes** |
| `OPTIONAL` | The **source text itself** says optional / bonus / good-to-have — e.g. `OPTIONAL: async FastAPI streaming endpoint — extra credit, not required`. | No |
| `ENGAGEMENT` | The statement describes the engagement or the evaluator, not the software — e.g. `Duration \| 20 hours`, `Review Output \| Per-team Excel report ...`. | No |

The distinction is drawn from the source wording, not from convenience. Failing the build over a
feature the document calls "not required" would misreport the document just as surely as passing a
requirement without evidence would.

For the `ENGAGEMENT` statements that no artifact in a repository can settle — the engagement
duration, the team size, the evaluator's own Excel report — the suite provides a recorded human
attestation channel in `manual_evidence/manual_attestations.json`. An unattested entry is a **FAIL**.
Silence is never a pass.
