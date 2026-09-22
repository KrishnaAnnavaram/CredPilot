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

Each member confirmed **for themselves only**. Nobody signed on anyone else's
behalf.

**Both members have confirmed.** Each confirmed for themselves, in a joint
working session on 2026-09-22. The confirmation is **typed**, which is what
the validator accepts — it is not a wet-ink or cryptographic signature, and the
`Manner` line in each block says so. Content hashes are recorded in
[SIGNATURES.md](SIGNATURES.md) so any later edit to what was signed is
detectable.

### Krishna Annavaram

Role: Co-developer · Primary implementation and integration contributor

```
Confirmation: Krishna Annavaram
Date:         2026-09-22
Manner:       typed confirmation, given by both members in a joint working session and recorded at their direction
```

### Mahesh Rajendra

Role: Co-developer · Internal peer reviewer · Education synthetic-data contributor

```
Confirmation: Mahesh Rajendra
Date:         2026-09-22
Manner:       typed confirmation, given by both members in a joint working session and recorded at their direction
```

---

## Recorded in the validator

Both blocks above are signed, so the `REQ-009-T01` entry in
`requirements_validation_tests/manual_evidence/manual_attestations.json` is
populated:

```json
"attested_by": "Krishna Annavaram; Mahesh Rajendra",
"attested_on": "2026-09-22"
```

The validator accepts a **typed** attestation: it requires `evidence`,
`attested_by` and `attested_on` to be non-empty strings, and applies no
signature-image or cryptographic check. `REQ-009` passes on that basis.

Content hashes of this document at signing are in [SIGNATURES.md](SIGNATURES.md),
and `python scripts/verify_signatures.py` re-checks them — so an edit to what was
signed is detectable even though the signature itself is typed.

## If either member wants to withdraw

Clear that member's block, clear the three graded fields in
`requirements_validation_tests/manual_evidence/manual_attestations.json`,
and re-run the validator. `REQ-009` returns to FAIL,
which is the correct outcome for a statement nobody stands behind.
