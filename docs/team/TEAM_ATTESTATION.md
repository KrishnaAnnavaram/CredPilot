# Team attestation — CredPilot

**Project:** CredPilot — Loan Origination & Underwriting Copilot
**Team size:** 2

**Members:**

- Krishna Annavaram
- Mahesh Rajendra

Satisfies `REQ-009` (*"Format | Team of 2–4"*), Section 2 of the requirements
document.

---

## Statement

> We attest that CredPilot was developed for this hackathon by a two-person team:
> Krishna Annavaram and Mahesh Rajendra.

---

## Supporting repository evidence

This is **corroboration, not proof**. Git records who committed, not who was on
the team, and a two-author history is consistent with several team sizes. The
statement above is what the requirement rests on; the evidence below is what a
reader can check for themselves.

```bash
git shortlog -sne --all
```

```
    12  Krishna Annavaram <annavaramkrishna02@gmail.com>
     2  KrishnaAnnavaram <162373752+KrishnaAnnavaram@users.noreply.github.com>
     1  Mahesh Rajendra <rajendramahesh25@gmail.com>
```

Two distinct people. The third identity is Krishna's GitHub web account, used for
merging pull requests through the browser.

| Member | Repository evidence |
|---|---|
| Krishna Annavaram | 12 authored commits + 2 merge commits, 2026-09-20 → 2026-09-22 |
| Mahesh Rajendra | Commit `f28a1fd` — education synthetic dataset, 260 files, 39,470 insertions, merged via PR #2 |

Roles and the full contribution split, including the research work that leaves no
commits behind, are in [TEAM_AND_ROLES.md](TEAM_AND_ROLES.md).

---

## Confirmations

Each member confirms **for themselves only**. Nobody signs on anyone else's
behalf, and this file is committed unsigned until each person fills in their own
block.

To confirm, replace the blank line with your name typed in full, and the date in
`YYYY-MM-DD` form.

### Krishna Annavaram

Role: Co-developer · Primary implementation and integration contributor

```
Confirmation: __________________________
Date:         __________________________
```

### Mahesh Rajendra

Role: Co-developer · Internal peer reviewer · Education synthetic-data contributor

```
Confirmation: __________________________
Date:         __________________________
```

---

## After both blocks are signed

The validator accepts a **typed** attestation. It reads
`requirements_validation_tests/manual_evidence/manual_attestations.json` and
requires all three of `evidence`, `attested_by` and `attested_on` to be non-empty
strings — there is no signature-image or cryptographic check, and no required
wording beyond being concrete.

Once **both** blocks above are genuinely filled in, replace the `REQ-009-T01`
entry in that file with:

```json
"REQ-009-T01": {
  "requirement_id": "REQ-009",
  "what_must_be_attested": "The delivery team matched the stated team size.",
  "source_location": "Section 2. Engagement Overview - table row 2",
  "source_text": "Format | Team of 2-4",
  "what_would_count_as_evidence": "The number of people on the delivery team, and whether that is within 2-4.",
  "where_to_look": "git shortlog -sne --all lists every committer.",
  "evidence": "docs/team/TEAM_ATTESTATION.md - CredPilot was built by a two-person team, Krishna Annavaram and Mahesh Rajendra, which is within the stated 2-4. Corroborated by two distinct commit authors in git shortlog -sne --all. Both members have signed the confirmation blocks in that file.",
  "attested_by": "Krishna Annavaram; Mahesh Rajendra",
  "attested_on": "YYYY-MM-DD"
}
```

Set `attested_on` to the date the **second** signature was added, then re-run:

```bash
python requirements_validation_tests/runners/run_all_tests.py
python requirements_validation_tests/traceability/build_gap_analysis.py
```

`REQ-009` moves to PASS at that point and not before. Leaving it unsigned is a
truthful FAIL, which this project treats as worth more than a pass nobody can
stand behind.
