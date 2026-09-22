# Requirements the source document does not make verifiable

Generated from `reports/latest_test_report.json` (2026-09-22T15:24:26Z) by 
`traceability/classify_failures.py`.


Each entry below is a requirement the source *states* but supplies no value 
for. The implementation cannot be checked against a number the document never 
gives, so these are recorded as specification gaps and left failing.


**No validator was changed to make any of these pass.** Each still returns 
`Evidence(False, ...)` from `not_verifiable_from_artifact(...)` in 
`validators/evidence_validator.py`, which has no branch that can return True. 
Turning one green would mean claiming the source requirement had been verified 
when nothing verified it.


Source of truth: `source_requirements/requirements_verbatim.md`, 
SHA-256 `ed25ccf4473d3cf17daad29d0db50f18276f4ed219aba55d8188e01214adf917`, integrity **REQUIREMENTS_BASELINE_VERIFIED**.


## Summary

| Requirement | Test | Missing value | Validator |
| --- | --- | --- | --- |
| `REQ-011` | `REQ-011-T03` | the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project | `not_verifiable_from_artifact` |
| `REQ-035` | `REQ-035-T03` | any licence artifact the implementation must carry to evidence LangGraph's MIT licence | `not_verifiable_from_artifact` |
| `REQ-045` | `REQ-045-T04` | the numeric DTI or disposable-income threshold that constitutes a policy breach | `not_verifiable_from_artifact` |
| `REQ-046` | `REQ-046-T07` | the loan value above which a case counts as a high-value case | `not_verifiable_from_artifact` |


---

## REQ-011 — REQ-011-T03

**Requirement class:** ENGAGEMENT  |  **Category:** governance  |  **Source location:** Section 2. Engagement Overview — table row 4

### Source text, verbatim

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

### Missing verifiable value

the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project

### Why the implementation cannot prove it

The source says to push 'by the cut-off' and names 'your assigned Virtusa GitLab project', but states neither the cut-off date and time nor the project identity anywhere in the document.


**Searched the source for it:**

| Looked for | Pattern | Matches |
| --- | --- | --- |
| any date or time offered as the cut-off | `cut-?off[^\n]{0,80}?\d|\d{1,2}\s*(?:am|pm)\b|\d{4}-\d{2}-\d{2}` | **0** |
| any GitLab URL or project path | `gitlab[^\n]{0,40}?[/.]` | **1** |

A match count of 0 is the evidence that the value is absent, rather than that nobody looked.

### Validator function

```python
not_verifiable_from_artifact(
    'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project'
)
```

Registered in `automated_tests/registry/cases_core.py` as `REQ-011-T03`, test type `GOVERNANCE_TEST`, weight 1, automatable False.

Pass condition as registered: *Not reachable: the document supplies nothing to verify against.*

### Recommended human interpretation

Treat as satisfied when the submitting team pushes to the project they were assigned, before the cut-off they were given. Both values live in the engagement brief, not in this document, and neither can be checked from the repository. docs/FINAL_SUBMISSION.md holds the commands.



---

## REQ-035 — REQ-035-T03

**Requirement class:** IMPLEMENTATION  |  **Category:** integration  |  **Source location:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"

### Source text, verbatim

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

### Missing verifiable value

any licence artifact the implementation must carry to evidence LangGraph's MIT licence

### Why the implementation cannot prove it

The source names LangGraph's licence as MIT in a stack table. It does not say the implementation must carry any licence artifact, nor name one, so there is no artifact to check for.


**Searched the source for it:**

| Looked for | Pattern | Matches |
| --- | --- | --- |
| any obligation to carry a licence file | `licen[cs]e[^\n]{0,60}?(?:file|artifact|copy|include|commit)` | **0** |

A match count of 0 is the evidence that the value is absent, rather than that nobody looked.

### Validator function

```python
not_verifiable_from_artifact(
    "any licence artifact the implementation must carry to evidence LangGraph's MIT licence"
)
```

Registered in `automated_tests/registry/cases_core.py` as `REQ-035-T03`, test type `GOVERNANCE_TEST`, weight 1, automatable False.

Pass condition as registered: *Not reachable: the document supplies nothing to verify against.*

### Recommended human interpretation

Treat as satisfied by LangGraph being MIT-licensed, which it is. The source names the licence as a property of the dependency in a stack table; it places no obligation on this repository to carry a licence artifact, so there is nothing here to inspect. If the evaluator expects one, a THIRD_PARTY_LICENCES.md would satisfy it - but inventing that obligation and then meeting it would be marking our own homework.



---

## REQ-045 — REQ-045-T04

**Requirement class:** IMPLEMENTATION  |  **Category:** affordability  |  **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-02

### Source text, verbatim

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

### Missing verifiable value

the numeric DTI or disposable-income threshold that constitutes a policy breach

### Why the implementation cannot prove it

AC-02 requires affordability breaches to be flagged 'with the threshold it failed'. The source never states a DTI or disposable-income number, so there is no value against which to verify the one the implementation uses.


**Searched the source for it:**

| Looked for | Pattern | Matches |
| --- | --- | --- |
| any percentage anywhere in the document | `\d+\s*%` | **0** |
| any stated DTI or disposable-income figure | `(?:dti|disposable[^\n]{0,20}income)[^\n]{0,40}?\d` | **0** |

A match count of 0 is the evidence that the value is absent, rather than that nobody looked.

### Validator function

```python
not_verifiable_from_artifact(
    'the numeric DTI or disposable-income threshold that constitutes a policy breach'
)
```

Registered in `automated_tests/registry/cases_acceptance.py` as `REQ-045-T04`, test type `BOUNDARY_TEST`, weight 1, automatable False.

Pass condition as registered: *Not reachable: the document supplies nothing to verify against.*

### Recommended human interpretation

Read AC-02 as requiring the implementation to name the threshold it applied, not to match a number the source never gives. CredPilot's thresholds come from its committed policy corpus with an effective date, and every breach cites the rule it failed - which is auditable in a way a hard-coded constant would not be.



---

## REQ-046 — REQ-046-T07

**Requirement class:** IMPLEMENTATION  |  **Category:** underwriting  |  **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-03

### Source text, verbatim

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

### Missing verifiable value

the loan value above which a case counts as a high-value case

### Why the implementation cannot prove it

AC-03 routes a 'high-value case' for human review. The source never fixes the monetary boundary at which a case becomes high-value.


**Searched the source for it:**

| Looked for | Pattern | Matches |
| --- | --- | --- |
| any monetary amount offered as the high-value boundary | `high[- ]value[^\n]{0,60}?\d|(?:above|over|exceed\w*)\s*[\u00a3$\u20ac]?\s*[\d,]{4,}` | **0** |

A match count of 0 is the evidence that the value is absent, rather than that nobody looked.

### Validator function

```python
not_verifiable_from_artifact(
    'the loan value above which a case counts as a high-value case'
)
```

Registered in `automated_tests/registry/cases_acceptance.py` as `REQ-046-T07`, test type `BOUNDARY_TEST`, weight 1, automatable False.

Pass condition as registered: *Not reachable: the document supplies nothing to verify against.*

### Recommended human interpretation

Read AC-03 as requiring a high-value boundary that is explicit, committed and applied consistently - not one that matches an unstated figure. CredPilot's boundary lives in its committed review-trigger rules.


---

## What would change these

Only the source document. If the engagement issues a threshold, a cut-off, an assigned project URL or a licence-artifact obligation, each becomes mechanically checkable and the corresponding test can be rewritten against the stated value. Until then the honest report is the one above.

