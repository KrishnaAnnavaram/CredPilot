# Final submission to the assigned Virtusa GitLab project

The source document's submission instruction is one line:

> Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.

This file is the runbook for doing that, and the record of why the corresponding
check currently fails.

---

## Current state

```
$ git remote -v
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)

$ git branch --show-current
chore/unify-synthetic-data
```

There is **no Virtusa GitLab remote configured**, because the assigned project
URL was never supplied to this repository. `REQ-011-T02` therefore fails, and it
should.

### Why no placeholder was added

`REQ-011-T02` is satisfied by `remote_matches_gitlab`, which runs `git remote -v`
and passes if any line matches `/gitlab/i`. That is all it does. So this would
turn the check green in one command:

```bash
git remote add virtusa https://gitlab.example.com/placeholder/credpilot.git   # DO NOT
```

It would also push nowhere, submit nothing, and leave a report saying the
repository had been submitted. A check that can be satisfied by a string is a
check that has to be satisfied by the truth instead — the same rule this project
applies to every other piece of evidence it produces. The remote stays absent
until there is a real one.

This is classified `EXTERNAL_SUBMISSION_DEPENDENCY` in
`requirements_validation_tests/reports/current_failures.md`: not a defect in the
implementation, and not something any amount of code here can close.

---

## What to run at submission time

Replace `<REAL_ASSIGNED_GITLAB_URL>` with the project URL you were actually
assigned. Do not guess it, and do not reuse the example.

### 1. Add the assigned remote

```bash
git remote add virtusa <REAL_ASSIGNED_GITLAB_URL>
git remote -v                      # confirm it is there and spelled correctly
```

### 2. Confirm you can reach it before relying on it

```bash
git ls-remote virtusa              # authenticates and lists refs; fails loudly if not
```

If this fails, the push will fail. Fix access now rather than at the cut-off.

### 3. Decide what branch you are submitting

The work is currently on `chore/unify-synthetic-data`, which is a working-branch
name rather than a submission. Either merge to `main` first, or push explicitly
and tell the reviewer which branch to read:

```bash
git checkout main
git merge --no-ff chore/unify-synthetic-data
```

### 4. Check the tree is clean and the evidence is current

```bash
git status --porcelain             # must be empty
python scripts/regenerate_evidence.py          # non-zero if any step fails
python requirements_validation_tests/runners/run_all_tests.py
```

Committing stale evidence after changing the code that produces it breaks the
Evidence-in-Repo rule, which several requirements are graded on.

### 5. Push

```bash
git push virtusa main              # or the branch you decided on in step 3
git push virtusa --tags            # if you tagged the submission
```

### 6. Verify the push actually landed

```bash
git ls-remote virtusa refs/heads/main
git rev-parse HEAD
```

The two hashes must match. A push that reported success and a remote that does
not have your commit is a failure mode worth thirty seconds to rule out.

### 7. Regenerate the validator evidence

Once a real GitLab remote exists, `REQ-011-T02` will pass on its own:

```bash
python requirements_validation_tests/runners/run_all_tests.py
python requirements_validation_tests/traceability/classify_failures.py
python requirements_validation_tests/traceability/build_source_matrix.py
```

`REQ-011` as a whole will still fail, because `REQ-011-T03` asks for the cut-off
date and the assigned project identity, and the source document states neither.
See `requirements_validation_tests/reports/unverifiable_requirements.md`.

---

## What this does not settle

Pushing to GitLab does not make the engagement attestations true. `REQ-008`,
`REQ-009`, `REQ-010`, `REQ-012` and `REQ-013` are statements about the team, the
review and the grade, and they stay blank until someone who knows signs them —
see `requirements_validation_tests/manual_evidence/ATTESTATION_CHECKLIST.md`.

Two of them (`REQ-012`, the Excel review report, and `REQ-013`, the grade) are
produced by the reviewer. They cannot be signed by the delivery team at all.
