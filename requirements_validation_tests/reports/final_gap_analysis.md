# Final gap analysis

Generated from `reports/latest_test_report.json` (2026-09-22T15:24:26Z) by 
`traceability/build_gap_analysis.py`. Regenerate it after signing an attestation 
or pushing to GitLab — the answers below change as those happen.


Requirements baseline SHA-256 `ed25ccf4473d3cf17daad29d0db50f18276f4ed219aba55d8188e01214adf917`, integrity **REQUIREMENTS_BASELINE_VERIFIED**.


## Where the score stands

```
Requirements passed : 103 / 112
Requirements failed : 9
Overall fit         : 98%
IMPLEMENTATION      : 87/90
ENGAGEMENT          : 12/18
OPTIONAL            : 4/4
```


## The nine, by what would actually close them

| Route | Requirements | Can the team close it? |
| --- | --- | --- |
| **TEAM ARTIFACT CAN SATISFY** | `REQ-008`, `REQ-009` | Yes — a truthful attestation the team signs |
| **NEEDS EXTERNAL EVENT** | `REQ-010`, `REQ-011`, `REQ-012`, `REQ-013` | No — depends on the evaluator or on the submission happening |
| **SOURCE STATES NO VALUE** | `REQ-035`, `REQ-045`, `REQ-046` | No — the source document fixes no value to test against |

`REQ-011` appears once here but fails two tests for two different reasons: `T02` needs the GitLab push, `T03` is a specification gap. It is routed to **NEEDS EXTERNAL EVENT** because that is the part anyone can act on.


---

## REQ-008 — fit 0/100

* **Class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 1
* **Bound tests:** REQ-008-T01 (0 passing, 1 failing)
* **Route:** **TEAM ARTIFACT CAN SATISFY**
* **Needs an external evaluator or event:** no
* **Untestable because the source fixes no value:** no

**Source wording, verbatim**

~~~text
Duration | 20 hours
~~~

**Exact failing condition**

```
Attestation for REQ-008-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**What would close it:** A truthful duration attestation from the two team members, evidenced by `docs/team/WORKLOG.md` and `reports/team_worklog.xlsx`. The repository can show the wall-clock window; only the team can attest to effort inside it.

**Blocked on:** Krishna Annavaram and Mahesh Rajendra confirming the statement.


---

## REQ-009 — fit 0/100

* **Class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 2
* **Bound tests:** REQ-009-T01 (0 passing, 1 failing)
* **Route:** **TEAM ARTIFACT CAN SATISFY**
* **Needs an external evaluator or event:** no
* **Untestable because the source fixes no value:** no

**Source wording, verbatim**

~~~text
Format | Team of 2–4
~~~

**Exact failing condition**

```
Attestation for REQ-009-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**What would close it:** A truthful team-size attestation. Git shows two distinct commit authors, which is corroboration but not proof of team size; `docs/team/TEAM_ATTESTATION.md` is the statement itself.

**Blocked on:** Krishna Annavaram and Mahesh Rajendra confirming the statement.


---

## REQ-010 — fit 50/100

* **Class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 3
* **Bound tests:** REQ-010-T01, REQ-010-T02 (1 passing, 1 failing)
* **Route:** **NEEDS EXTERNAL EVENT**
* **Needs an external evaluator or event:** yes
* **Untestable because the source fixes no value:** no

**Source wording, verbatim**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**What already passes**

* `REQ-010-T01` — E:\Virtusa Projects\CredPilot is a Git repository; git ls-files reports 1881 tracked files

**Exact failing condition**

```
Attestation for REQ-010-T02 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**What would close it:** Confirmation that the **official** automated review against the Hackathon Rubric was carried out. The team's own automated validation is recorded in `docs/team/AUTOMATED_REVIEW_EVIDENCE.md`, but that is the team reviewing itself and is not the evaluation the requirement describes.

**Blocked on:** The official Virtusa evaluator running the rubric review.


---

## REQ-011 — fit 33/100

* **Class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 4
* **Bound tests:** REQ-011-T01, REQ-011-T02, REQ-011-T03 (1 passing, 2 failing)
* **Route:** **NEEDS EXTERNAL EVENT**
* **Needs an external evaluator or event:** yes
* **Untestable because the source fixes no value:** yes

**Source wording, verbatim**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**What already passes**

* `REQ-011-T01` — git remote -v: origin git@github.com:KrishnaAnnavaram/CredPilot.git (fetch) origin git@github.com:KrishnaAnnavaram/CredPilot.git (push)

**Exact failing condition**

```
No configured remote names GitLab, but the submission instruction names a Virtusa GitLab project. Remotes found:
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)
```

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project' could be verified against an implementation.
```

**What would close it:** `REQ-011-T02` closes when a real assigned Virtusa GitLab remote exists and the final commit is pushed from the Virtusa work laptop. `REQ-011-T03` cannot close: the source names a cut-off but states no date or time, and names the assigned project but no identity.

**Blocked on:** The actual push to the assigned Virtusa GitLab project (T02). T03 is a specification gap and stays open whatever the team does.


---

## REQ-012 — fit 0/100

* **Class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 5
* **Bound tests:** REQ-012-T01 (0 passing, 1 failing)
* **Route:** **NEEDS EXTERNAL EVENT**
* **Needs an external evaluator or event:** yes
* **Untestable because the source fixes no value:** no

**Source wording, verbatim**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

**Exact failing condition**

```
Attestation for REQ-012-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**What would close it:** The **per-team Excel report produced by the reviewer**. `reports/CredPilot_Internal_Peer_Review.xlsx` carries the same five sheets and is internal pre-submission preparation; presenting it as the reviewer's output would be a false claim about who produced it.

**Blocked on:** The official reviewer producing and returning their report.


---

## REQ-013 — fit 0/100

* **Class:** ENGAGEMENT
* **Category:** governance
* **Source location:** Section 2. Engagement Overview — table row 6
* **Bound tests:** REQ-013-T01 (0 passing, 1 failing)
* **Route:** **NEEDS EXTERNAL EVENT**
* **Needs an external evaluator or event:** yes
* **Untestable because the source fixes no value:** no

**Source wording, verbatim**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

**Exact failing condition**

```
Attestation for REQ-013-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

**What would close it:** Confirmation that the stated bands (Pass >= 60, Not Yet Passed < 60) were the ones applied to an awarded grade. The bands are recorded in the internal review workbook; whether they were applied is the evaluator's fact.

**Blocked on:** A grade being issued by the evaluator.


---

## REQ-035 — fit 67/100

* **Class:** IMPLEMENTATION
* **Category:** integration
* **Source location:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"
* **Bound tests:** REQ-035-T01, REQ-035-T02, REQ-035-T03 (2 passing, 1 failing)
* **Route:** **SOURCE STATES NO VALUE**
* **Needs an external evaluator or event:** no
* **Untestable because the source fixes no value:** yes

**Source wording, verbatim**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**What already passes**

* `REQ-035-T01` — Python >= 3.11 declared at pyproject.toml:5: requires-python = ">=3.11"
* `REQ-035-T02` — LangGraph agent framework (ALL: 2/2 satisfied) [OK] langgraph declared (dependency manifests) (ALL: 1/1 satisfied) [OK] requirements.txt:16: langgraph==1.2.11 [OK] langgraph imported (import analysis) (ALL: 1/1 satisfied) [OK] src

**Exact failing condition**

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence' could be verified against an implementation.
```

**What would close it:** Nothing the repository can add. `docs/THIRD_PARTY_LICENSES.md` and `reports/dependency_licenses.json` now evidence LangGraph's MIT licence from installed package metadata, which is the substantive claim — but the check asks for a licence *artifact the source requires*, and the source requires none.

**Blocked on:** Nothing. The source places no licence-artifact obligation.


---

## REQ-045 — fit 80/100

* **Class:** IMPLEMENTATION
* **Category:** affordability
* **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-02
* **Bound tests:** REQ-045-T01, REQ-045-T02, REQ-045-T03, REQ-045-T04 (3 passing, 1 failing)
* **Route:** **SOURCE STATES NO VALUE**
* **Needs an external evaluator or event:** no
* **Untestable because the source fixes no value:** yes

**Source wording, verbatim**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**What already passes**

* `REQ-045-T01` — DTI / disposable-income computation across implementation tree (156 files) (ALL: 1/1 satisfied) [OK] eval/agent/dataset.py:320: "DTI-CONV": "src/rules.py — affordability ceiling, with the compensating-factor extension",
* `REQ-045-T02` — affordability figure in observable output (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json') (ALL: 1/1 satisfied) [OK] /afford|\bDTI\b|disposable/ matched observable output: 'afford' --- observa
* `REQ-045-T03` — threshold-bearing policy breach flag across implementation tree (156 files) (ALL: 2/2 satisfied) [OK] eval/agent/dataset.py:316: #: reader, but no code compares them against a threshold. [OK] eval/agent/dataset.py:158: asked, and 

**Exact failing condition**

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the numeric DTI or disposable-income threshold that constitutes a policy breach' could be verified against an implementation.
```

**What would close it:** Nothing, without inventing a number. Three of four bound tests pass: the copilot computes DTI, reports it in observable output, and names the threshold it failed. The fourth asks for the numeric threshold *the source document* fixes, and it fixes none.

**Blocked on:** Nothing. Hard-coding 43% or 45% would fabricate a source value.


---

## REQ-046 — fit 89/100

* **Class:** IMPLEMENTATION
* **Category:** underwriting
* **Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-03
* **Bound tests:** REQ-046-T01, REQ-046-T02, REQ-046-T03, REQ-046-T04, REQ-046-T05, REQ-046-T06, REQ-046-T07 (6 passing, 1 failing)
* **Route:** **SOURCE STATES NO VALUE**
* **Needs an external evaluator or event:** no
* **Untestable because the source fixes no value:** yes

**Source wording, verbatim**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**What already passes**

* `REQ-046-T01` — Decision vocabulary present in observable output: ['decline'] (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json')
* `REQ-046-T02` — the approve / refer / decline outcomes across implementation tree (156 files) (ALL: 3/3 satisfied) [OK] eval/agent/dataset.py:41: #: ``APPROVE_WITH_CONDITIONS`` is listed because the golden sets use it — six [OK] eval/agent/datase
* `REQ-046-T03` — written rationale in observable output (from 'python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json') (ALL: 1/1 satisfied) [OK] /rationale|reason|justification|because|explanation/ matched observable output
* `REQ-046-T04` — decline handling across implementation tree (156 files) (ALL: 1/1 satisfied) [OK] eval/agent/dataset.py:43: #: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
* `REQ-046-T05` — high-value case routing across implementation tree (156 files) (ALL: 1/1 satisfied) [OK] scripts/build_peer_review_workbook.py:128: "High-value routing keys off the policy corpus. The source states no "
* `REQ-046-T06` — human-review route across implementation tree (156 files) (ALL: 1/1 satisfied) [OK] eval/agent/dataset.py:63: "PENDING_HUMAN_REVIEW": REFER,

**Exact failing condition**

```
UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the loan value above which a case counts as a high-value case' could be verified against an implementation.
```

**What would close it:** Nothing, without inventing a boundary. Six of seven bound tests pass, including high-value routing (`src/review_triggers.py`). The seventh asks for the monetary boundary *the source document* fixes, and it fixes none.

**Blocked on:** Nothing. Inventing a dollar figure would fabricate a source value.


---

## What was deliberately not done

* No attestation was signed on anyone's behalf. `attested_by` stays empty until the named person confirms.
* No GitLab remote was invented. `REQ-011-T02` passes on any remote URL matching `/gitlab/i`, which is exactly why it has to be satisfied by a real one.
* The internal peer-review workbook is titled as internal pre-submission preparation. It is not presented as the reviewer's report, and `REQ-012` stays open.
* No DTI percentage and no high-value monetary boundary were hard-coded. Both come from the retrieved, versioned policy corpus at runtime; the source document states neither.
* No validator was edited. Where a check cannot pass, it still reports FAIL.


## Not the official rubric

Every figure here comes from this repository's own 112-requirement validator. The engagement is graded on a 7-category / 100-mark Hackathon Rubric that is **not in this repository and has not been run**. Nothing above is a mark against it.

