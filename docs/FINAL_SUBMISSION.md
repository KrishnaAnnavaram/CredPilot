# Final submission to the assigned Virtusa GitLab project

The source document's submission instruction is one line:

> Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.

This is the runbook for doing that, and the record of why `REQ-011` is still open.

Team: **Krishna Annavaram**, **Mahesh Rajendra**.

---

## Two different repositories

This is the part most likely to be misread, so it is stated first:

| | Repository | Purpose |
|---|---|---|
| **Development / sharing** | `git@github.com:KrishnaAnnavaram/CredPilot.git` (personal GitHub) | Where the two of us build and share work. **Not the submission.** |
| **Final submission** | The **assigned Virtusa GitLab project** | Where the graded repository must land. **Not yet pushed.** |

The personal GitHub is a working repository. It is not the hackathon submission
and must not be presented as one.

### Current state

```
$ git remote -v
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)

$ git branch --show-current
chore/unify-synthetic-data
```

There is **no Virtusa GitLab remote configured**. The assigned project URL has
not been supplied to this repository. `REQ-011-T02` therefore fails, and it
should.

---

## Submission record — blank until the push happens

These are filled in **after** the real push, from the real output. They are blank
now because the push has not occurred.

```
VIRTUSA_GITLAB_URL=
FINAL_COMMIT_SHA=
FINAL_PUSH_TIMESTAMP=
FINAL_BRANCH=
PUSHED_BY=
REMOTE_COMMIT_VERIFIED=
```

Filling any of these in before the push would be recording an event that has not
happened.

### Why no placeholder remote was added

`REQ-011-T02` is satisfied by `remote_matches_gitlab`, which runs `git remote -v`
and passes if **any line matches `/gitlab/i`**. That is all it does. So this would
turn the check green in one command:

```bash
git remote add virtusa https://gitlab.example.com/placeholder/credpilot.git   # DO NOT
```

It would also push nowhere, submit nothing, and leave a report saying the
repository had been submitted. A check that can be satisfied by a string has to
be satisfied by the truth instead — the same rule this project applies to every
other piece of evidence it produces. The remote stays absent until there is a
real one.

This is classified `EXTERNAL_SUBMISSION_DEPENDENCY` in
[`requirements_validation_tests/reports/current_failures.md`](../requirements_validation_tests/reports/current_failures.md):
not a defect in the implementation, and not something any amount of code here can
close.

---

## Planned sequence

Steps 1–5 happen on the development machine. Steps 6–11 happen on Krishna's
**Virtusa work laptop**, which is where the assigned GitLab project is reachable.

### 1. Complete the project

Code freeze. No further functional change after this point.

### 2. Run the complete tests

```bash
python -m pytest -q
```

Expect **970 passed, 0 failed**. Do not proceed on a red suite.

### 3. Run evidence generation

```bash
python scripts/regenerate_evidence.py
python scripts/verify_evidence_citations.py
python scripts/verify_doc_tables.py
python scripts/check_published_figures.py
python requirements_validation_tests/runners/run_all_tests.py
python requirements_validation_tests/traceability/build_gap_analysis.py
```

`regenerate_evidence.py` returns non-zero and names the stage on any failure.
Committing stale evidence after changing the code that produced it breaks the
Evidence-in-Repo rule, which several requirements are graded on.

### 4. Verify a clean git status

```bash
git status --porcelain     # must be empty
```

Anything uncommitted is, by the Citation-Resolves rule, **missing** — a document
citing a file present only in the working tree fails the check.

### 5. Verify no secrets

```bash
git ls-files | grep -E "^\.env$"                     # must return nothing
git ls-files -z | xargs -0 grep -lE "AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|BEGIN [A-Z ]*PRIVATE KEY"
git ls-files '*.py' '*.md' | xargs grep -lE "\b(4[0-9]{12}([0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"
```

All three must return nothing. `data/memory/` is gitignored and must stay that
way — it holds applicant memory stores.

### 6. Move the final project to the Virtusa work laptop

Transfer the complete repository **including its Git history** to Krishna's
Virtusa work laptop. Clone or copy the whole working tree; do not export a
snapshot of files, or the commit history — which is itself evidence for `REQ-008`
and `REQ-009` — is lost.

```bash
# On the Virtusa laptop
git clone git@github.com:KrishnaAnnavaram/CredPilot.git
cd CredPilot
git log --oneline -5          # confirm the history came with it
git shortlog -sne --all       # confirm both contributors are present
```

### 7. Configure the real assigned Virtusa GitLab remote

Replace `<REAL_ASSIGNED_GITLAB_URL>` with the project URL actually assigned to
the team. Do not guess it, and do not reuse any example.

```bash
git remote add virtusa <REAL_ASSIGNED_GITLAB_URL>
git remote -v
git ls-remote virtusa          # authenticates; fails loudly if access is wrong
```

Fix access now rather than at the cut-off.

### 8. Decide the submission branch

The work is currently on `chore/unify-synthetic-data`, which is a working-branch
name rather than a submission. Either merge to `main` or tell the reviewer which
branch to read.

```bash
git checkout main
git merge --no-ff chore/unify-synthetic-data
```

### 9. Push the exact final commit

```bash
git push virtusa main
git push virtusa --tags        # if a submission tag was created
```

### 10. Record the submission facts

Fill in the block at the top of this file from the real output:

```bash
git remote get-url virtusa                       # -> VIRTUSA_GITLAB_URL
git rev-parse HEAD                               # -> FINAL_COMMIT_SHA
git branch --show-current                        # -> FINAL_BRANCH
date -u +"%Y-%m-%dT%H:%M:%SZ"                    # -> FINAL_PUSH_TIMESTAMP
```

### 11. Verify the commit exists on the remote

```bash
git ls-remote virtusa refs/heads/main
git rev-parse HEAD
```

**The two hashes must match.** A push that reported success against a remote that
does not have the commit is a failure mode worth thirty seconds to rule out. Set
`REMOTE_COMMIT_VERIFIED=yes` only after seeing them match.

### 12. Regenerate the validator evidence

Once a real GitLab remote exists, `REQ-011-T02` passes on its own:

```bash
python requirements_validation_tests/runners/run_all_tests.py
python requirements_validation_tests/traceability/build_gap_analysis.py
```

Commit and push the refreshed reports.

---

## What still will not pass

`REQ-011` as a whole stays open even after a successful push, because it fails two
tests for two different reasons:

| Test | Closes on push? | Why |
|---|---|---|
| `REQ-011-T02` | **Yes** | A real GitLab remote will exist. |
| `REQ-011-T03` | **No** | It asks for the submission cut-off date and time, and the identity of the assigned project. The source document states **neither**. |

`REQ-011-T03` is a specification gap, recorded in
[`requirements_validation_tests/reports/unverifiable_requirements.md`](../requirements_validation_tests/reports/unverifiable_requirements.md).
Nothing the team does closes it.

---

## What this does not settle

Pushing to GitLab does not make the engagement facts true:

| Requirement | Blocked on |
|---|---|
| `REQ-008` — 20 hours | Both members signing [`docs/team/WORKLOG.md`](team/WORKLOG.md) |
| `REQ-009` — team of 2–4 | Both members signing [`docs/team/TEAM_ATTESTATION.md`](team/TEAM_ATTESTATION.md) |
| `REQ-010` — official rubric review | The evaluator running it |
| `REQ-012` — per-team Excel report | The **reviewer** producing it. [`reports/CredPilot_Internal_Peer_Review.xlsx`](../reports/CredPilot_Internal_Peer_Review.xlsx) is internal preparation, not that report. |
| `REQ-013` — grade bands applied | A grade being issued |

Full picture:
[`requirements_validation_tests/reports/final_gap_analysis.md`](../requirements_validation_tests/reports/final_gap_analysis.md).
