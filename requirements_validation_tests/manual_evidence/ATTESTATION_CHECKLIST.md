# Attestation checklist

Generated from `manual_attestations.json` by `manual_evidence/build_checklist.py`. 
Re-run it after signing anything.


## Where this stands

```
Statements needing a human signature : 5
  signed                             : 2
  still unsigned                     : 3
Statements that cannot be signed     : 4
```


Every unsigned statement below is a **FAIL** in the validation report, and 
that is the correct outcome. The brief is explicit that no evidence is never 
a pass, and an attestation is worth exactly as much as the care taken before 
signing it.


> **Do not sign an event that has not happened.** Two of these — the Excel 
> review report and the grade — are produced by the reviewer, not by the 
> delivery team. They cannot be truthfully signed by us at all, whatever the 
> effect on the score.


## Summary

| Requirement | Test | Statement | Who signs | Status |
| --- | --- | --- | --- | --- |
| `REQ-008` | `REQ-008-T01` | The engagement ran for the stated duration. | A member of the delivery team. | **SIGNED** |
| `REQ-009` | `REQ-009-T01` | The delivery team matched the stated team size. | A member of the delivery team. | **SIGNED** |
| `REQ-010` | `REQ-010-T02` | The review was performed automatically against the Hackathon Rubric with no live demo judging. | The reviewer who ran the evaluation, or the submitter if they were told how it would be run. | **UNSIGNED** |
| `REQ-012` | `REQ-012-T01` | The per-team Excel review report with its five stated sections was produced. | The reviewer who produces the report. | **UNSIGNED** |
| `REQ-013` | `REQ-013-T01` | The stated grade bands were applied. | The evaluator who awards the grade. | **UNSIGNED** |


## Each statement in full


### `REQ-008` — `REQ-008-T01`

**Status: SIGNED**

* **Source location:** Section 2. Engagement Overview - table row 1

**Exact statement that must be true**

> The engagement ran for the stated duration.

**Source text it comes from**

~~~text
Duration | 20 hours
~~~

**What evidence would support it**

The actual elapsed engagement time against the stated 20 hours. Git shows a 55.6-hour wall-clock window over 13 commits, but that is the window work happened inside, not effort - and the majority of this team's research is not represented in commits at all. Exact task-level hours are team-attested rather than mechanically derivable from Git history.

**Where to look**

```
docs/team/WORKLOG.md and reports/team_worklog.xlsx - generated from git history and the self-recorded timestamps inside the committed evidence artifacts by scripts/build_team_worklog.py. Both members sign the confirmation blocks in WORKLOG.md.
```

**Who should attest:** A member of the delivery team.

**When it can truthfully be attested:** Any time after the work has stopped. The elapsed window is knowable now; the effort inside it is only knowable by the people who did it.

**Attested**

* by: Krishna Annavaram; Mahesh Rajendra
* on: 2026-09-22
* evidence: docs/team/WORKLOG.md and reports/team_worklog.xlsx, signed by both members. Combined project development, testing, evaluation, review, research and documentation activity met or exceeded the stated 20 hours. Repository evidence bounds but does not measure this: git shows a 55.6-hour wall-clock window over 13 commits (2026-09-20 06:08 UTC to 2026-09-22 13:44 UTC), of which only 3.72 hours is observable as commit-to-commit span across 2 of 8 sessions. Exact task-level hours are team-attested rather than mechanically derivable from Git history, and the majority of this team's research - done by Mahesh Rajendra - produces no commits at all. Typed confirmation by both members in a joint working session on 2026-09-22, recorded at their direction. Not a wet-ink or cryptographic signature - see docs/team/SIGNATURES.md, which records the SHA-256 of each signed document so a later edit is detectable (python scripts/verify_signatures.py).


### `REQ-009` — `REQ-009-T01`

**Status: SIGNED**

* **Source location:** Section 2. Engagement Overview - table row 2

**Exact statement that must be true**

> The delivery team matched the stated team size.

**Source text it comes from**

~~~text
Format | Team of 2-4
~~~

**What evidence would support it**

The number of people on the delivery team, and whether that is within 2-4. The team is two: Krishna Annavaram and Mahesh Rajendra. Git records two distinct commit authors, which corroborates but does not prove team size.

**Where to look**

```
docs/team/TEAM_ATTESTATION.md for the statement and both signature blocks; docs/team/TEAM_AND_ROLES.md for roles and the repository-verified vs team-attested contribution split. Corroborating: git shortlog -sne --all shows two distinct contributors.
```

**Who should attest:** A member of the delivery team.

**When it can truthfully be attested:** Now. The team size is already known — it simply is not written anywhere a validator can read, and the git history shows committers rather than members.

**Attested**

* by: Krishna Annavaram; Mahesh Rajendra
* on: 2026-09-22
* evidence: docs/team/TEAM_ATTESTATION.md, signed by both members. CredPilot was developed by a two-person team - Krishna Annavaram and Mahesh Rajendra - which is within the stated 2-4. Corroborated in the repository by two distinct commit authors (git shortlog -sne --all): Krishna Annavaram (12 commits plus 2 merge commits) and Mahesh Rajendra (commit f28a1fd, the education synthetic dataset, 260 files / 39,470 insertions, merged via PR #2). Roles and the repository-verified vs team-attested split are in docs/team/TEAM_AND_ROLES.md. Typed confirmation by both members in a joint working session on 2026-09-22, recorded at their direction. Not a wet-ink or cryptographic signature - see docs/team/SIGNATURES.md, which records the SHA-256 of each signed document so a later edit is detectable (python scripts/verify_signatures.py).


### `REQ-010` — `REQ-010-T02`

**Status: UNSIGNED**

* **Source location:** Section 2. Engagement Overview - table row 3

**Exact statement that must be true**

> The review was performed automatically against the Hackathon Rubric with no live demo judging.

**Source text it comes from**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**What evidence would support it**

Confirmation that the review was run this way - automated, from committed evidence, with no live demo judged. Only the reviewer or the submitter can say how the review was actually conducted.

**Where to look**

```
The reviewer's instructions or the returned scorecard. NOTE: docs/team/AUTOMATED_REVIEW_EVIDENCE.md records the TEAM's own automated validation (validator, pytest, DeepEval, evidence regeneration). That is not the official evaluation this requirement describes and does not satisfy it.
```

**Who should attest:** The reviewer who ran the evaluation, or the submitter if they were told how it would be run.

**When it can truthfully be attested:** After the review has been conducted. Not before: how a review was carried out is not something the submitting team can assert on the reviewer's behalf.

**Still missing:** `evidence`, `attested_by`, `attested_on`

To sign, fill all three fields in `manual_attestations.json` and re-run this script. An entry with one field left blank does not count.


### `REQ-012` — `REQ-012-T01`

**Status: UNSIGNED**

* **Source location:** Section 2. Engagement Overview - table row 5

**Exact statement that must be true**

> The per-team Excel review report with its five stated sections was produced.

**Source text it comes from**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

**What evidence would support it**

That the per-team Excel report was produced with those five sheets. Cite the file - name, date received, and that the five sections are present.

**Where to look**

```
The review report itself, if it has been returned. NOTE: reports/CredPilot_Internal_Peer_Review.xlsx carries the same five sheets but is INTERNAL pre-submission preparation by the delivery team, reviewed by Mahesh Rajendra as an internal peer reviewer - NOT a Virtusa evaluator. It is not the per-team report this requirement describes.
```

**Who should attest:** The reviewer who produces the report.

**When it can truthfully be attested:** After the per-team Excel report exists and has been seen. Claiming it before then would be attesting to an event that has not happened.

**Still missing:** `evidence`, `attested_by`, `attested_on`

To sign, fill all three fields in `manual_attestations.json` and re-run this script. An entry with one field left blank does not count.


### `REQ-013` — `REQ-013-T01`

**Status: UNSIGNED**

* **Source location:** Section 2. Engagement Overview - table row 6

**Exact statement that must be true**

> The stated grade bands were applied.

**Source text it comes from**

~~~text
Grade Bands | Pass >= 60 - Not Yet Passed < 60
~~~

**What evidence would support it**

That the stated bands were the ones applied - a score at or above 60 recorded as Pass, below 60 as Not Yet Passed. Cite the returned grade.

**Where to look**

```
The returned scorecard. The bands (Pass >= 60, Not Yet Passed < 60) are recorded in reports/CredPilot_Internal_Peer_Review.xlsx, but whether they were applied to an awarded grade is the evaluator's fact.
```

**Who should attest:** The evaluator who awards the grade.

**When it can truthfully be attested:** After a grade has been issued. The bands are stated in the source; whether they were the ones applied is only knowable from the returned scorecard.

**Still missing:** `evidence`, `attested_by`, `attested_on`

To sign, fill all three fields in `manual_attestations.json` and re-run this script. An entry with one field left blank does not count.



## Statements that cannot be signed at all

These are not waiting on anybody. The source document fixes no value to verify against, so there is nothing a signature could be about. They are reported as specification gaps in `reports/unverifiable_requirements.md`, and the checks are written never to pass.

| Requirement | Test | Statement |
| --- | --- | --- |
| `REQ-011` | `REQ-011-T03` | The push happened by the cut-off. |
| `REQ-035` | `REQ-035-T03` | LangGraph is used under the MIT licence. |
| `REQ-045` | `REQ-045-T04` | The DTI / disposable-income threshold values themselves. |
| `REQ-046` | `REQ-046-T07` | The monetary boundary at which a case becomes high-value. |


---

## How to sign

Open `manual_attestations.json` and fill in, for the entry concerned:

```
  "evidence":    "what you are relying on, concretely — not \"yes\"",
  "attested_by": "your name",
  "attested_on": "2026-09-22"
```

Then re-run this script and the validator. Attest only to what you know: a truthful FAIL is worth more than a pass nobody can stand behind.

