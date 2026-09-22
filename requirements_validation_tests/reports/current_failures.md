# Current requirement-validation failures

Generated from `reports/latest_test_report.json` (2026-09-22T16:04:01Z) by 
`traceability/classify_failures.py`.


This document exists because the headline count and the bucket counts had 
disagreed. They are reconciled below, and the script that writes this file 
fails if they stop agreeing or if a new failure appears that nobody has 
classified.


## Arithmetic

```
Total requirements      : 112
Requirements passed     : 105
Requirements failed     : 7
passed + failed == total: 112 == 112

Failing tests           : 8
Failing requirements    : 7
```


Failing tests outnumber failing requirements because one requirement can fail 
two different checks. **REQ-011 is the case that matters**: its remote check is 
an external dependency and its cut-off check is unspecified by the source. 
Counting it once per bucket is what produced an apparent 12 from 11 distinct 
requirements. Classification below is therefore keyed by *test*, and the 
requirement totals are derived from it rather than asserted alongside it.


## Counts by class

| Class | Failing tests | Distinct requirements | Fixable in code? |
| --- | --- | --- | --- |
| MANUAL_ATTESTATION_REQUIRED | 3 | 3 | no |
| EXTERNAL_SUBMISSION_DEPENDENCY | 1 | 1 | no |
| UNSPECIFIED_BY_REQUIREMENT | 4 | 4 | no |

Distinct failing requirement IDs: **7** — `REQ-010`, `REQ-011`, `REQ-012`, `REQ-013`, `REQ-035`, `REQ-045`, `REQ-046`


## Every failing test

| Test ID | Requirement | Class | Current Failure | Fixable in Code? | Correct Action |
| --- | --- | --- | --- | --- | --- |
| `REQ-010-T02` | `REQ-010` | MANUAL_ATTESTATION_REQUIRED | Attestation for REQ-010-T02 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL | no | Leave blank. Only the reviewer who ran the rubric can attest to it. |
| `REQ-011-T02` | `REQ-011` | EXTERNAL_SUBMISSION_DEPENDENCY | No configured remote names GitLab, but the submission instruction names a Virtusa GitLab project. Remotes found: origin git@github.com:KrishnaAnnavar… | no | Record as an external dependency. Add the real remote at submission time using docs/FINAL_SUBMISSION.md; do not invent a URL. |
| `REQ-011-T03` | `REQ-011` | UNSPECIFIED_BY_REQUIREMENT | UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the submission cut-off date and time, and the identity of the… | no | Report as a specification gap. A human supplies both values at submission. |
| `REQ-012-T01` | `REQ-012` | MANUAL_ATTESTATION_REQUIRED | Attestation for REQ-012-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL | no | Leave blank until the reviewer produces the report. |
| `REQ-013-T01` | `REQ-013` | MANUAL_ATTESTATION_REQUIRED | Attestation for REQ-013-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL | no | Leave blank until the evaluator issues a grade. |
| `REQ-035-T03` | `REQ-035` | UNSPECIFIED_BY_REQUIREMENT | UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'any licence artifact the implementation must carry to evidenc… | no | Report as a specification gap. LangGraph's MIT licence is a fact about the dependency, not an obligation the source places on this repository. |
| `REQ-045-T04` | `REQ-045` | UNSPECIFIED_BY_REQUIREMENT | UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the numeric DTI or disposable-income threshold that constitut… | no | Report as a specification gap. The implementation's thresholds come from its own committed policy corpus, which is the auditable substitute. |
| `REQ-046-T07` | `REQ-046` | UNSPECIFIED_BY_REQUIREMENT | UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the loan value above which a case counts as a high-value case… | no | Report as a specification gap. The implementation's boundary is set in its committed review-trigger rules. |


## Detail, per failing test


### MANUAL_ATTESTATION_REQUIRED — 3 test(s)

#### `REQ-010-T02` → `REQ-010`

* **Requirement class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 3
* **Validator function:** `check` (`GOVERNANCE_TEST`)
* **Pass condition:** A complete, dated, attributed attestation of 'an automated review against the Hackathon Rubric (7 categories / 100 marks), with no live demo judging' is recorded.

**Source requirement**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**Current failure**

```
Attestation for REQ-010-T02 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**Why this class:** The evaluator runs the 7-category / 100-mark Hackathon Rubric. That rubric is not in this repository, so nothing here can show it was applied or what it scored.

**Fixable in code:** no

**Correct action:** Leave blank. Only the reviewer who ran the rubric can attest to it.

#### `REQ-012-T01` → `REQ-012`

* **Requirement class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 5
* **Validator function:** `check` (`GOVERNANCE_TEST`)
* **Pass condition:** A complete, dated, attributed attestation of 'a per-team Excel report containing the Summary, Categories, Scorecard, Detailed and Improvement sections' is recorded.

**Source requirement**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

**Current failure**

```
Attestation for REQ-012-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**Why this class:** The per-team Excel review report is produced by the reviewer, not by the team. Claiming it exists before the reviewer has produced it would be a fabricated attestation.

**Fixable in code:** no

**Correct action:** Leave blank until the reviewer produces the report.

#### `REQ-013-T01` → `REQ-013`

* **Requirement class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 6
* **Validator function:** `check` (`GOVERNANCE_TEST`)
* **Pass condition:** A complete, dated, attributed attestation of 'the grade bands Pass >= 60 and Not Yet Passed < 60' is recorded.

**Source requirement**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

**Current failure**

```
Attestation for REQ-013-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**Why this class:** Grade bands (Pass >= 60) are applied by the evaluator against the rubric. The repository holds neither the rubric nor the awarded grade.

**Fixable in code:** no

**Correct action:** Leave blank until the evaluator issues a grade.


### EXTERNAL_SUBMISSION_DEPENDENCY — 1 test(s)

#### `REQ-011-T02` → `REQ-011`

* **Requirement class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 4
* **Validator function:** `remote_matches_gitlab` (`GOVERNANCE_TEST`)
* **Pass condition:** Collected evidence satisfies: A configured Git remote URL identifies a GitLab project.

**Source requirement**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Current failure**

```
No configured remote names GitLab, but the submission instruction names a Virtusa GitLab project. Remotes found:
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)
```

**Why this class:** The check requires a git remote pointing at the assigned Virtusa GitLab project. No such remote is configured, and the assigned URL was never supplied to this repository. Adding a plausible-looking GitLab URL would make the check pass while pushing nowhere real.

**Fixable in code:** no

**Correct action:** Record as an external dependency. Add the real remote at submission time using docs/FINAL_SUBMISSION.md; do not invent a URL.


### UNSPECIFIED_BY_REQUIREMENT — 4 test(s)

#### `REQ-011-T03` → `REQ-011`

* **Requirement class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 4
* **Validator function:** `check` (`GOVERNANCE_TEST`)
* **Pass condition:** Not reachable: the document supplies nothing to verify against.

**Source requirement**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Current failure**

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project' could be verified against an implementation.
```

**Why this class:** The source says to push 'by the cut-off' and names 'your assigned Virtusa GitLab project', but states neither the cut-off date and time nor the project identity anywhere in the document.

**Fixable in code:** no

**Correct action:** Report as a specification gap. A human supplies both values at submission.

#### `REQ-035-T03` → `REQ-035`

* **Requirement class:** IMPLEMENTATION
* **Category:** integration
* **Source location:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"
* **Validator function:** `check` (`GOVERNANCE_TEST`)
* **Pass condition:** Not reachable: the document supplies nothing to verify against.

**Source requirement**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**Current failure**

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence' could be verified against an implementation.
```

**Why this class:** The source names LangGraph's licence as MIT in a stack table. It does not say the implementation must carry any licence artifact, nor name one, so there is no artifact to check for.

**Fixable in code:** no

**Correct action:** Report as a specification gap. LangGraph's MIT licence is a fact about the dependency, not an obligation the source places on this repository.

#### `REQ-045-T04` → `REQ-045`

* **Requirement class:** IMPLEMENTATION
* **Category:** affordability
* **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-02
* **Validator function:** `check` (`BOUNDARY_TEST`)
* **Pass condition:** Not reachable: the document supplies nothing to verify against.

**Source requirement**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Current failure**

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the numeric DTI or disposable-income threshold that constitutes a policy breach' could be verified against an implementation.
```

**Why this class:** AC-02 requires affordability breaches to be flagged 'with the threshold it failed'. The source never states a DTI or disposable-income number, so there is no value against which to verify the one the implementation uses.

**Fixable in code:** no

**Correct action:** Report as a specification gap. The implementation's thresholds come from its own committed policy corpus, which is the auditable substitute.

#### `REQ-046-T07` → `REQ-046`

* **Requirement class:** IMPLEMENTATION
* **Category:** underwriting
* **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-03
* **Validator function:** `check` (`BOUNDARY_TEST`)
* **Pass condition:** Not reachable: the document supplies nothing to verify against.

**Source requirement**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Current failure**

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the loan value above which a case counts as a high-value case' could be verified against an implementation.
```

**Why this class:** AC-03 routes a 'high-value case' for human review. The source never fixes the monetary boundary at which a case becomes high-value.

**Fixable in code:** no

**Correct action:** Report as a specification gap. The implementation's boundary is set in its committed review-trigger rules.


---

## The ceiling this implies

Of 7 failing requirements, 0 fail for reasons this repository can fix. The rest depend on a human, an external system, or a value the source document never states.


No validator was edited to change any of these outcomes. Where a check cannot pass, it still reports FAIL and this document says why.

