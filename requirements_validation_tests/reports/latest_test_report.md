# CredPilot Requirements Validation Report

Generated: 2026-09-20T21:33:37Z  
Implementation under validation: `E:\Virtusa Projects\CredPilot`  
Requirements baseline: `source_requirements/requirements_verbatim.md`  
Baseline SHA-256: `ed25ccf4473d3cf17daad29d0db50f18276f4ed219aba55d8188e01214adf917`  
Baseline integrity: **REQUIREMENTS_BASELINE_VERIFIED**  
Suites executed: api, functional, governance, integration, static, workflow  
Wall time: 24.12s

---

## Headline

```
CredPilot Requirements Validation Report

Total Requirements: 112
Tests Executed: 320
Requirements Passed: 13
Requirements Failed: 99
Requirement Coverage: 100.0%
Overall Requirement Fit: 18%

Final Status:
FAIL
```

## Breakdown by requirement class

| Class | Total | Passed | Failed | Gates final status |
| --- | --- | --- | --- | --- |
| IMPLEMENTATION | 90 | 8 | 82 | yes |
| OPTIONAL | 4 | 1 | 3 | no - the source text marks these optional / bonus / good-to-have |
| ENGAGEMENT | 18 | 4 | 14 | no - these describe the engagement or the evaluator, not the deliverable |

Automated tests executed: 311  |  Manual / non-automatable tests executed: 9

## Failed requirements (IMPLEMENTATION class)

| Requirement | Fit | Category | Reason |
| --- | --- | --- | --- |
| REQ-003 | 0 | governance | 8 of 8 bound test(s) produced no satisfying evidence: REQ-003-T01, REQ-003-T02, REQ-003-T03, REQ-003-T04, REQ-003-T05, REQ-003-T06 (+2 more). |
| REQ-014 | 0 | governance | 10 of 10 bound test(s) produced no satisfying evidence: REQ-014-T01, REQ-014-T02, REQ-014-T03, REQ-014-T04, REQ-014-T05, REQ-014-T06 (+4 more). |
| REQ-015 | 50 | auditability | 1 of 2 bound test(s) produced no satisfying evidence: REQ-015-T02. |
| REQ-020 | 50 | underwriting | 3 of 6 bound test(s) produced no satisfying evidence: REQ-020-T01, REQ-020-T02, REQ-020-T05. |
| REQ-022 | 0 | orchestration | 7 of 7 bound test(s) produced no satisfying evidence: REQ-022-T01, REQ-022-T02, REQ-022-T03, REQ-022-T04, REQ-022-T05, REQ-022-T06 (+1 more). |
| REQ-023 | 50 | non_functional | 1 of 2 bound test(s) produced no satisfying evidence: REQ-023-T02. |
| REQ-024 | 50 | orchestration | 3 of 6 bound test(s) produced no satisfying evidence: REQ-024-T04, REQ-024-T05, REQ-024-T06. |
| REQ-025 | 14 | integration | 6 of 7 bound test(s) produced no satisfying evidence: REQ-025-T01, REQ-025-T02, REQ-025-T03, REQ-025-T04, REQ-025-T06, REQ-025-T07. |
| REQ-026 | 0 | observability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-026-T01, REQ-026-T02, REQ-026-T03. |
| REQ-027 | 0 | governance | 6 of 6 bound test(s) produced no satisfying evidence: REQ-027-T01, REQ-027-T02, REQ-027-T03, REQ-027-T04, REQ-027-T05, REQ-027-T06. |
| REQ-028 | 20 | evaluation | 4 of 5 bound test(s) produced no satisfying evidence: REQ-028-T01, REQ-028-T02, REQ-028-T03, REQ-028-T04. |
| REQ-029 | 0 | auditability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-029-T01, REQ-029-T02. |
| REQ-030 | 0 | auditability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-030-T01, REQ-030-T02. |
| REQ-032 | 50 | integration | 2 of 4 bound test(s) produced no satisfying evidence: REQ-032-T01, REQ-032-T03. |
| REQ-033 | 0 | non_functional | 2 of 2 bound test(s) produced no satisfying evidence: REQ-033-T01, REQ-033-T02. |
| REQ-034 | 33 | integration | 2 of 3 bound test(s) produced no satisfying evidence: REQ-034-T01, REQ-034-T02. |
| REQ-035 | 0 | integration | 3 of 3 bound test(s) produced no satisfying evidence: REQ-035-T01, REQ-035-T02, REQ-035-T03. |
| REQ-036 | 50 | integration | 1 of 2 bound test(s) produced no satisfying evidence: REQ-036-T01. |
| REQ-037 | 0 | integration | 2 of 2 bound test(s) produced no satisfying evidence: REQ-037-T01, REQ-037-T02. |
| REQ-038 | 0 | integration | 2 of 2 bound test(s) produced no satisfying evidence: REQ-038-T01, REQ-038-T02. |
| REQ-039 | 0 | policy | 2 of 2 bound test(s) produced no satisfying evidence: REQ-039-T01, REQ-039-T02. |
| REQ-040 | 0 | observability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-040-T01, REQ-040-T02, REQ-040-T03. |
| REQ-041 | 0 | evaluation | 2 of 2 bound test(s) produced no satisfying evidence: REQ-041-T01, REQ-041-T02. |
| REQ-042 | 0 | security | 3 of 3 bound test(s) produced no satisfying evidence: REQ-042-T01, REQ-042-T02, REQ-042-T03. |
| REQ-044 | 33 | eligibility | 3 of 4 bound test(s) produced no satisfying evidence: REQ-044-T01, REQ-044-T03, REQ-044-T04. |
| REQ-045 | 40 | affordability | 2 of 4 bound test(s) produced no satisfying evidence: REQ-045-T02, REQ-045-T04. |
| REQ-046 | 44 | underwriting | 3 of 7 bound test(s) produced no satisfying evidence: REQ-046-T01, REQ-046-T03, REQ-046-T07. |
| REQ-048 | 0 | functional | 2 of 2 bound test(s) produced no satisfying evidence: REQ-048-T01, REQ-048-T02. |
| REQ-050 | 0 | observability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-050-T01, REQ-050-T02, REQ-050-T03. |
| REQ-051 | 0 | observability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-051-T01, REQ-051-T02. |
| REQ-052 | 0 | observability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-052-T01, REQ-052-T02, REQ-052-T03. |
| REQ-053 | 0 | auditability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-053-T01, REQ-053-T02. |
| REQ-054 | 0 | governance | 5 of 5 bound test(s) produced no satisfying evidence: REQ-054-T01, REQ-054-T02, REQ-054-T03, REQ-054-T04, REQ-054-T05. |
| REQ-055 | 0 | evaluation | 4 of 4 bound test(s) produced no satisfying evidence: REQ-055-T01, REQ-055-T02, REQ-055-T03, REQ-055-T04. |
| REQ-056 | 67 | security | 1 of 3 bound test(s) produced no satisfying evidence: REQ-056-T02. |
| REQ-057 | 20 | non_functional | 2 of 3 bound test(s) produced no satisfying evidence: REQ-057-T01, REQ-057-T03. |
| REQ-059 | 0 | non_functional | 2 of 2 bound test(s) produced no satisfying evidence: REQ-059-T01, REQ-059-T02. |
| REQ-061 | 0 | auditability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-061-T01, REQ-061-T02. |
| REQ-062 | 0 | orchestration | 1 of 1 bound test(s) produced no satisfying evidence: REQ-062-T01. |
| REQ-063 | 0 | observability | 5 of 5 bound test(s) produced no satisfying evidence: REQ-063-T01, REQ-063-T02, REQ-063-T03, REQ-063-T04, REQ-063-T05. |
| REQ-064 | 67 | functional | 1 of 3 bound test(s) produced no satisfying evidence: REQ-064-T03. |
| REQ-066 | 0 | integration | 2 of 2 bound test(s) produced no satisfying evidence: REQ-066-T01, REQ-066-T02. |
| REQ-068 | 50 | security | 1 of 2 bound test(s) produced no satisfying evidence: REQ-068-T02. |
| REQ-070 | 40 | auditability | 1 of 2 bound test(s) produced no satisfying evidence: REQ-070-T01. |
| REQ-071 | 0 | auditability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-071-T01, REQ-071-T02. |
| REQ-072 | 10 | orchestration | 5 of 6 bound test(s) produced no satisfying evidence: REQ-072-T01, REQ-072-T03, REQ-072-T04, REQ-072-T05, REQ-072-T06. |
| REQ-073 | 0 | integration | 4 of 4 bound test(s) produced no satisfying evidence: REQ-073-T01, REQ-073-T02, REQ-073-T03, REQ-073-T04. |
| REQ-074 | 33 | functional | 3 of 4 bound test(s) produced no satisfying evidence: REQ-074-T01, REQ-074-T02, REQ-074-T03. |
| REQ-075 | 0 | functional | 5 of 5 bound test(s) produced no satisfying evidence: REQ-075-T01, REQ-075-T02, REQ-075-T03, REQ-075-T04, REQ-075-T05. |
| REQ-076 | 40 | policy | 2 of 4 bound test(s) produced no satisfying evidence: REQ-076-T01, REQ-076-T03. |
| REQ-077 | 33 | observability | 2 of 3 bound test(s) produced no satisfying evidence: REQ-077-T01, REQ-077-T02. |
| REQ-078 | 0 | observability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-078-T01, REQ-078-T02. |
| REQ-079 | 0 | observability | 4 of 4 bound test(s) produced no satisfying evidence: REQ-079-T01, REQ-079-T02, REQ-079-T03, REQ-079-T04. |
| REQ-080 | 0 | observability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-080-T01, REQ-080-T02. |
| REQ-081 | 0 | observability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-081-T01, REQ-081-T02, REQ-081-T03. |
| REQ-082 | 0 | observability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-082-T01, REQ-082-T02. |
| REQ-083 | 0 | security | 2 of 2 bound test(s) produced no satisfying evidence: REQ-083-T01, REQ-083-T02. |
| REQ-084 | 20 | auditability | 2 of 3 bound test(s) produced no satisfying evidence: REQ-084-T01, REQ-084-T02. |
| REQ-085 | 60 | security | 1 of 2 bound test(s) produced no satisfying evidence: REQ-085-T01. |
| REQ-086 | 0 | risk | 3 of 3 bound test(s) produced no satisfying evidence: REQ-086-T01, REQ-086-T02, REQ-086-T03. |
| REQ-087 | 0 | governance | 3 of 3 bound test(s) produced no satisfying evidence: REQ-087-T01, REQ-087-T02, REQ-087-T03. |
| REQ-088 | 0 | governance | 3 of 3 bound test(s) produced no satisfying evidence: REQ-088-T01, REQ-088-T02, REQ-088-T03. |
| REQ-089 | 0 | risk | 4 of 4 bound test(s) produced no satisfying evidence: REQ-089-T01, REQ-089-T02, REQ-089-T03, REQ-089-T04. |
| REQ-090 | 0 | evaluation | 2 of 2 bound test(s) produced no satisfying evidence: REQ-090-T01, REQ-090-T02. |
| REQ-091 | 0 | orchestration | 2 of 2 bound test(s) produced no satisfying evidence: REQ-091-T01, REQ-091-T02. |
| REQ-092 | 0 | orchestration | 3 of 3 bound test(s) produced no satisfying evidence: REQ-092-T01, REQ-092-T02, REQ-092-T03. |
| REQ-093 | 0 | integration | 2 of 2 bound test(s) produced no satisfying evidence: REQ-093-T01, REQ-093-T02. |
| REQ-094 | 33 | non_functional | 2 of 4 bound test(s) produced no satisfying evidence: REQ-094-T02, REQ-094-T03. |
| REQ-096 | 0 | auditability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-096-T01, REQ-096-T02, REQ-096-T03. |
| REQ-097 | 20 | auditability | 2 of 3 bound test(s) produced no satisfying evidence: REQ-097-T01, REQ-097-T02. |
| REQ-098 | 0 | observability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-098-T01, REQ-098-T02, REQ-098-T03. |
| REQ-099 | 0 | observability | 4 of 4 bound test(s) produced no satisfying evidence: REQ-099-T01, REQ-099-T02, REQ-099-T03, REQ-099-T04. |
| REQ-100 | 0 | observability | 3 of 3 bound test(s) produced no satisfying evidence: REQ-100-T01, REQ-100-T02, REQ-100-T03. |
| REQ-101 | 0 | observability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-101-T01, REQ-101-T02. |
| REQ-102 | 0 | observability | 4 of 4 bound test(s) produced no satisfying evidence: REQ-102-T01, REQ-102-T02, REQ-102-T03, REQ-102-T04. |
| REQ-103 | 0 | observability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-103-T01, REQ-103-T02. |
| REQ-104 | 0 | security | 3 of 3 bound test(s) produced no satisfying evidence: REQ-104-T01, REQ-104-T02, REQ-104-T03. |
| REQ-105 | 0 | auditability | 2 of 2 bound test(s) produced no satisfying evidence: REQ-105-T01, REQ-105-T02. |
| REQ-106 | 0 | governance | 2 of 2 bound test(s) produced no satisfying evidence: REQ-106-T01, REQ-106-T02. |
| REQ-107 | 0 | evaluation | 2 of 2 bound test(s) produced no satisfying evidence: REQ-107-T01, REQ-107-T02. |
| REQ-108 | 0 | evaluation | 4 of 4 bound test(s) produced no satisfying evidence: REQ-108-T01, REQ-108-T02, REQ-108-T03, REQ-108-T04. |
| REQ-112 | 0 | governance | 6 of 6 bound test(s) produced no satisfying evidence: REQ-112-T01, REQ-112-T02, REQ-112-T03, REQ-112-T04, REQ-112-T05, REQ-112-T06. |

## Failed requirements (OPTIONAL / ENGAGEMENT - not gating)

| Requirement | Class | Fit | Reason |
| --- | --- | --- | --- |
| REQ-001 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-001-T01. |
| REQ-002 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-002-T01. |
| REQ-004 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-004-T01. |
| REQ-005 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-005-T01. |
| REQ-006 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-006-T01. |
| REQ-007 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-007-T01. |
| REQ-008 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-008-T01. |
| REQ-009 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-009-T01. |
| REQ-010 | ENGAGEMENT | 50 | 1 of 2 bound test(s) produced no satisfying evidence: REQ-010-T02. |
| REQ-011 | ENGAGEMENT | 33 | 2 of 3 bound test(s) produced no satisfying evidence: REQ-011-T02, REQ-011-T03. |
| REQ-012 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-012-T01. |
| REQ-013 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-013-T01. |
| REQ-019 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-019-T01. |
| REQ-021 | ENGAGEMENT | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-021-T01. |
| REQ-109 | OPTIONAL | 0 | 2 of 2 bound test(s) produced no satisfying evidence: REQ-109-T01, REQ-109-T02. |
| REQ-110 | OPTIONAL | 67 | 1 of 3 bound test(s) produced no satisfying evidence: REQ-110-T01. |
| REQ-111 | OPTIONAL | 0 | 1 of 1 bound test(s) produced no satisfying evidence: REQ-111-T01. |

## Fit score by category

| Category | Requirements | Passed | Mean fit |
| --- | --- | --- | --- |
| affordability | 1 | 0 | 40 |
| auditability | 11 | 0 | 12 |
| eligibility | 1 | 0 | 33 |
| evaluation | 6 | 0 | 3 |
| functional | 7 | 2 | 43 |
| governance | 23 | 2 | 12 |
| integration | 10 | 0 | 15 |
| non_functional | 8 | 3 | 50 |
| observability | 19 | 0 | 2 |
| orchestration | 6 | 0 | 10 |
| policy | 3 | 0 | 13 |
| risk | 2 | 0 | 0 |
| security | 11 | 4 | 59 |
| underwriting | 3 | 1 | 65 |
| workflow | 1 | 1 | 100 |

---

## Per-requirement result

Each entry carries the exact original requirement, its status, its fit score, the actual evidence collected, and a factual reason.

### REQ-001 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Document title block — banner line above the title (first line of the document)

**Requirement:**

~~~text
Agentic AI Engineer Pathway — Capstone Hackathon
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-001-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-001-T01.

**Evidence:**

```
[FAIL] REQ-001-T01: the pathway and capstone hackathon named in the banner line across implementation tree (51 files) (ALL: 0/2 satisfied)
[NOT FOUND] no match for /Agentic\s+AI\s+Engineer\s+Pathway/ in 51 files under implementation tree
[NOT FOUND] no match for /Capstone\s+Hackathon/ in 51 files under implementation tree
```

### REQ-002 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Document title block — document title

**Requirement:**

~~~text
Loan Origination & Underwriting Copilot
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-002-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-002-T01.

**Evidence:**

```
[FAIL] REQ-002-T01: the document title declared in repository documentation across implementation tree (51 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /Loan\s+Origination\s*&\s*Underwriting\s+Copilot/ in 51 files under implementation tree
```

### REQ-003 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Document title block — subtitle line beneath the title

**Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-003-T01, REQ-003-T02, REQ-003-T03, REQ-003-T04, REQ-003-T05, REQ-003-T06, REQ-003-T07, REQ-003-T08  
**Reason:** 8 of 8 bound test(s) produced no satisfying evidence: REQ-003-T01, REQ-003-T02, REQ-003-T03, REQ-003-T04, REQ-003-T05, REQ-003-T06 (+2 more).

**Evidence:**

```
[FAIL] REQ-003-T01: business case ID and domain from the subtitle (ALL: 0/2 satisfied)
[NOT FOUND] business case ID across implementation tree (1191 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /BC-AAIE-HACK-02/ in 1191 files under implementation tree
[NOT FOUND] domain across implementation tree (51 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /Banking\s*&\s*Finance|Banking and Finance/ in 51 files under implementation tree
[FAIL] REQ-003-T02: Agentic Core (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'src/graph.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'LangGraph declared as a dependency': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[FAIL] REQ-003-T03: No directory at or near 'src/context' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-003-T04: MCP (ALL: 0/2 satisfied)
[NOT FOUND] No directory at or near 'mcp_server' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'the MCP Python SDK declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[FAIL] REQ-003-T05: Observability (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'src/observability/tracing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'arize-phoenix declared as a dependency': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[FAIL] REQ-003-T06: Cost Governance (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'reports/dashboard_data.csv' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-003-T07: Security & Governance (ALL: 0/3 satisfied)
[NOT FOUND] No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-003-T08: Agent Evaluation (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
```

### REQ-004 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 1

**Requirement:**

~~~text
Business Case Title | Loan Origination & Underwriting Copilot
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-004-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-004-T01.

**Evidence:**

```
[FAIL] REQ-004-T01: business case title declared in repository documentation across implementation tree (51 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /Loan\s+Origination\s*&\s*Underwriting\s+Copilot/ in 51 files under implementation tree
```

### REQ-005 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 2

**Requirement:**

~~~text
Business Case ID | BC-AAIE-HACK-02
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-005-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-005-T01.

**Evidence:**

```
[FAIL] REQ-005-T01: business case ID declared in the repository across implementation tree (1191 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /BC-AAIE-HACK-02/ in 1191 files under implementation tree
```

### REQ-006 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 3

**Requirement:**

~~~text
Domain | Banking & Finance
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-006-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-006-T01.

**Evidence:**

```
[FAIL] REQ-006-T01: domain declared in repository documentation across implementation tree (51 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /Banking\s*&\s*Finance|Banking and Finance/ in 51 files under implementation tree
```

### REQ-007 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 1. Project Identity — table row 4

**Requirement:**

~~~text
Project Type | Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-007-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-007-T01.

**Evidence:**

```
[FAIL] REQ-007-T01: project type declared in repository documentation across implementation tree (51 files) (ALL: 0/2 satisfied)
[NOT FOUND] no match for /Agentic\s+AI\s+Engineer\s+Pathway/ in 51 files under implementation tree
[NOT FOUND] no match for /Capstone\s+Hackathon/ in 51 files under implementation tree
```

### REQ-008 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 1

**Requirement:**

~~~text
Duration | 20 hours
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-008-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-008-T01.

**Evidence:**

```
[FAIL] REQ-008-T01: Attestation for REQ-008-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-009 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 2

**Requirement:**

~~~text
Format | Team of 2–4
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-009-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-009-T01.

**Evidence:**

```
[FAIL] REQ-009-T01: Attestation for REQ-009-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-010 - FAIL (50/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 3

**Requirement:**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-010-T01, REQ-010-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-010-T02.

**Evidence:**

```
[PASS] REQ-010-T01: E:\Virtusa Projects\CredPilot is a Git repository; git ls-files reports 71 tracked files
[FAIL] REQ-010-T02: Attestation for REQ-010-T02 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-011 - FAIL (33/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 4

**Requirement:**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-011-T01, REQ-011-T02, REQ-011-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-011-T02, REQ-011-T03.

**Evidence:**

```
[PASS] REQ-011-T01: git remote -v:
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)
[FAIL] REQ-011-T02: No configured remote names GitLab, but the submission instruction names a Virtusa GitLab project. Remotes found:
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (fetch)
origin	git@github.com:KrishnaAnnavaram/CredPilot.git (push)
[FAIL] REQ-011-T03: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project' could be verified against an implementation.
```

### REQ-012 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 5

**Requirement:**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-012-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-012-T01.

**Evidence:**

```
[FAIL] REQ-012-T01: Attestation for REQ-012-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-013 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — table row 6

**Requirement:**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-013-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-013-T01.

**Evidence:**

```
[FAIL] REQ-013-T01: Attestation for REQ-013-T01 is incomplete (evidence='', attested_by='', attested_on='') -> FAIL
```

### REQ-014 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 1

**Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-014-T01, REQ-014-T02, REQ-014-T03, REQ-014-T04, REQ-014-T05, REQ-014-T06, REQ-014-T07, REQ-014-T08, REQ-014-T09, REQ-014-T10  
**Reason:** 10 of 10 bound test(s) produced no satisfying evidence: REQ-014-T01, REQ-014-T02, REQ-014-T03, REQ-014-T04, REQ-014-T05, REQ-014-T06 (+4 more).

**Evidence:**

```
[FAIL] REQ-014-T01: LangGraph multi-agent system (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'src/graph.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'LangGraph declared as a dependency': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[FAIL] REQ-014-T02: No directory at or near 'src/context' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-014-T03: No directory at or near 'src/memory' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-014-T04: No directory at or near 'mcp_server' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-014-T05: No file at or near 'src/tools/rag_tool.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-014-T06: Arize Phoenix observability (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'src/observability/tracing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'arize-phoenix declared as a dependency': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[FAIL] REQ-014-T07: cost and latency governance artifacts (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] cost/latency dashboard (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/dashboard.png' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'reports/dashboard_data.csv' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-014-T08: guardrails and audit (ALL: 0/2 satisfied)
[NOT FOUND] No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'logs/agent_actions.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-014-T09: governance and compliance documentation (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/model-card.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/output-risk.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-014-T10: agent-level evaluation and tests (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_loops.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_tool_contracts.py' under E:\Virtusa Projects\CredPilot
```

### REQ-015 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 2

**Requirement:**

~~~text
Every claim is scored from committed evidence.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-015-T01, REQ-015-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-015-T02.

**Evidence:**

```
[PASS] REQ-015-T01: E:\Virtusa Projects\CredPilot is a Git repository; git ls-files reports 71 tracked files
[FAIL] REQ-015-T02: 2 artifact(s) exist on disk but are not listed by 'git ls-files': synthetic_data/.gitignore, synthetic_data/README.md. Committed: 0.
```

### REQ-016 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 1

**Requirement:**

~~~text
What is not evaluated: the visual polish of any interface, generic unit-test volume, or which optional deployment path you use.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-016-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-016-T01: Scanned 307 of 320 registered test cases (excluding the 2 exclusion-stating requirements and the absence-asserting NEGATIVE_TESTs, which must name a topic in order to exclude it): none would score interface visual polish, generic unit-test volume, or a particular optional deployment path.
```

### REQ-017 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 2

**Requirement:**

~~~text
Containerized/cloud deployment is out of scope for this cut.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-017-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-017-T01: synthetic_data/README.md (293 lines) documents no docker / docker-compose / kubectl / helm command, so the run path does not depend on containerized or cloud deployment.
```

### REQ-018 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** underwriting  |  **Source:** Section 3.1 Problem — sentence 1

**Requirement:**

~~~text
A retail bank's loan officers spend most of an application on manual work: gathering the applicant's documents, checking eligibility against product policy, computing affordability, screening for risk flags, and drafting a decision rationale.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-018-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-018-T01: the five manual activities named in the problem statement across implementation tree (51 files) (ALL: 5/5 satisfied)
[OK] synthetic_data/DATA_DICTIONARY.md:6: Every committed table, its grain, what it is for, and every column with its inferred type. Row counts and types are read from the generated files, so this document describes what actually exists rather than what was intended.
[OK] synthetic_data/DATA_DICTIONARY.md:102: Verified balance plus two independent eligibility amounts: what can be brought to closing and what counts as a reserve. They are frequently different, which is why one 'balance' column would not do.
[OK] synthetic_data/DATA_LINEAGE.md:15: ### 1. Income → affordability → decision
[OK] synthetic_data/DATA_DICTIONARY.md:82: Deposits and withdrawals that bear on source of funds, including the unsourced large deposits the risk rules act on.
[OK] synthetic_data/DATA_DICTIONARY.md:126: The ordered trail from authorisation through policy selection, extraction, calculation, rule evaluation, risk screening and recommendation.
```

### REQ-019 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** policy  |  **Source:** Section 3.1 Problem — sentence 2

**Requirement:**

~~~text
Rules are scattered across policy PDFs and change often, so decisions are inconsistent and slow.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-019-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-019-T01.

**Evidence:**

```
[FAIL] REQ-019-T01: policy retrieved from a corpus (ALL: 1/2 satisfied)
[OK] Directory present: synthetic_data/policy_corpus (near match for 'data/policy_corpus'); 42 entries: POL-AST-001_assets-eligibility_v1.0.md, POL-AST-002_funds-to-close_v1.0.md, POL-AST-003_reserves_v1.0.md, POL-AST-003_reserves_v2.0.md, POL-AST-004_source-of-funds_v1.0.md, POL-CONV-001_conventional-purchase_v1.0.md, POL-CONV-002_conventional-rate-term-refinance_v1.0.md, POL-CONV-003_cash-out-refinance_v1.0.md, POL-CRD-001_credit-assessment_v1.0.md, POL-CRD-001_credit-assessment_v2.0.md, POL-CRD-002_credit-events_v1.0.md, POL-CRD-003_delinquency-treatment_v1.0.md...
[NOT FOUND] No file at or near 'src/tools/rag_tool.py' under E:\Virtusa Projects\CredPilot
```

### REQ-020 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** underwriting  |  **Source:** Section 3.1 Problem — sentence 3

**Requirement:**

~~~text
The bank wants an agentic copilot that ingests a loan application, retrieves the current lending policy, computes eligibility and affordability, screens risk, and drafts an auditable decision recommendation — with a human making the final call.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-020-T01, REQ-020-T02, REQ-020-T03, REQ-020-T04, REQ-020-T05, REQ-020-T06  
**Reason:** 3 of 6 bound test(s) produced no satisfying evidence: REQ-020-T01, REQ-020-T02, REQ-020-T05.

**Evidence:**

```
[FAIL] REQ-020-T01: loan application ingestion (ALL: 1/2 satisfied)
[NOT FOUND] committed loan application inputs: no sample input files found under any of data, samples, sample_inputs, inputs, fixtures, examples, data/samples, data/applications, tests/data
[OK] application handling in source across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:18: synthetic_data/applications/         the input packets the copilot reads
[FAIL] REQ-020-T02: current lending policy retrieval (ALL: 1/2 satisfied)
[NOT FOUND] No file at or near 'src/tools/rag_tool.py' under E:\Virtusa Projects\CredPilot
[OK] Directory present: synthetic_data/policy_corpus (near match for 'data/policy_corpus'); 42 entries: POL-AST-001_assets-eligibility_v1.0.md, POL-AST-002_funds-to-close_v1.0.md, POL-AST-003_reserves_v1.0.md, POL-AST-003_reserves_v2.0.md, POL-AST-004_source-of-funds_v1.0.md, POL-CONV-001_conventional-purchase_v1.0.md, POL-CONV-002_conventional-rate-term-refinance_v1.0.md, POL-CONV-003_cash-out-refinance_v1.0.md, POL-CRD-001_credit-assessment_v1.0.md, POL-CRD-001_credit-assessment_v2.0.md, POL-CRD-002_credit-events_v1.0.md, POL-CRD-003_delinquency-treatment_v1.0.md...
[PASS] REQ-020-T03: eligibility and affordability computation across implementation tree (16 files) (ALL: 2/2 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:54: eligibility_result,
[OK] synthetic_data/generator/generate_synthetic_data.py:216: "MONITORING_ONLY - must never reach an eligibility, affordability, "
[PASS] REQ-020-T04: risk screening in source across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:57: risk_level,
[FAIL] REQ-020-T05: auditable decision recommendation (ALL: 1/2 satisfied)
[OK] decision vocabulary in source across implementation tree (16 files) (ALL: 3/3 satisfied)
[OK] synthetic_data/generator/synth/documents.py:1333: "received and accepted, or to WAIVED only under an approved exception.",
[OK] synthetic_data/generator/generate_synthetic_data.py:87: refers = {e.rule_id for e in result.refers}
[OK] synthetic_data/generator/generate_synthetic_data.py:573: if rec == "DECLINE_RECOMMENDATION":
[NOT FOUND] No file at or near 'logs/agent_actions.jsonl' under E:\Virtusa Projects\CredPilot
[PASS] REQ-020-T06: human-in-the-loop final decision across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:56: requires_human_review,
```

### REQ-021 - FAIL (0/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 3.2 Your Role — sentence 1

**Requirement:**

~~~text
Agentic AI Engineer.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-021-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-021-T01.

**Evidence:**

```
[FAIL] REQ-021-T01: the stated role named in documentation across implementation tree (51 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /Agentic\s+AI\s+Engineer/ in 51 files under implementation tree
```

### REQ-022 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 3.2 Your Role — sentence 2

**Requirement:**

~~~text
You build a LangGraph multi-agent copilot, then instrument it with Arize Phoenix, govern its cost and latency, harden it with guardrails and an audit trail, document its risk and compliance posture, and prove its behaviour with agent-level evaluation and tests — delivering every artifact as committed evidence.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-022-T01, REQ-022-T02, REQ-022-T03, REQ-022-T04, REQ-022-T05, REQ-022-T06, REQ-022-T07  
**Reason:** 7 of 7 bound test(s) produced no satisfying evidence: REQ-022-T01, REQ-022-T02, REQ-022-T03, REQ-022-T04, REQ-022-T05, REQ-022-T06 (+1 more).

**Evidence:**

```
[FAIL] REQ-022-T01: LangGraph multi-agent copilot (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'src/graph.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] LangGraph imported by the implementation (import analysis) (ALL: 0/1 satisfied)
[NOT FOUND] module 'langgraph' is never imported
[FAIL] REQ-022-T02: Arize Phoenix instrumentation (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'src/observability/tracing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Phoenix/openinference imported (import analysis) (ANY: 0/2 satisfied)
[NOT FOUND] module 'phoenix' is never imported
[NOT FOUND] module 'openinference' is never imported
[FAIL] REQ-022-T03: No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-022-T04: guardrails and audit trail (ALL: 0/2 satisfied)
[NOT FOUND] No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'logs/agent_actions.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-022-T05: risk and compliance documentation (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-022-T06: agent-level evaluation and tests (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_loops.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_tool_contracts.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-022-T07: 2 artifact(s) exist on disk but are not listed by 'git ls-files': synthetic_data/.gitignore, synthetic_data/README.md. Committed: 0.
```

### REQ-023 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 3.3 Expected Solution — lead-in sentence

**Requirement:**

~~~text
A working, instrumented multi-agent application delivered as a Git repository that demonstrates:
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-023-T01, REQ-023-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-023-T02.

**Evidence:**

```
[PASS] REQ-023-T01: E:\Virtusa Projects\CredPilot is a Git repository; git ls-files reports 71 tracked files
[FAIL] REQ-023-T02: working instrumented multi-agent application (ALL: 0/3 satisfied)
[NOT FOUND] No file at or near 'src/graph.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'src/observability/tracing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] a committed trace export proving it ran (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'traces/phoenix_spans.jsonl' under E:\Virtusa Projects\CredPilot
```

### REQ-024 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 3.3 Expected Solution — bullet 1

**Requirement:**

~~~text
A LangGraph graph: typed state, a supervisor routing loan applications to specialized worker agents (an eligibility-and-affordability agent, a policy-retrieval agent, a risk-screening agent), conditional routing, checkpointing and structured output.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-024-T01, REQ-024-T02, REQ-024-T03, REQ-024-T04, REQ-024-T05, REQ-024-T06  
**Reason:** 3 of 6 bound test(s) produced no satisfying evidence: REQ-024-T04, REQ-024-T05, REQ-024-T06.

**Evidence:**

```
[PASS] REQ-024-T01: typed state definition across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/build.py:73: @dataclass
[PASS] REQ-024-T02: supervisor routing node across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/people.py:107: "logistics": ("Operations Supervisor", "Warehouse Planner", "Fleet Coordinator"),
[PASS] REQ-024-T03: the three named worker agents across implementation tree (16 files) (ALL: 3/3 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:216: "MONITORING_ONLY - must never reach an eligibility, affordability, "
[OK] synthetic_data/generator/generate_synthetic_data.py:633: ("AUTOMATED_COMPONENT", "select_policy_versions", "policy_retrieval",
[OK] synthetic_data/generator/generate_synthetic_data.py:641: ("AUTOMATED_COMPONENT", "screen_risk", "risk_screening",
[FAIL] REQ-024-T04: conditional routing wired into the graph (AST call analysis) (ALL: 0/1 satisfied)
[NOT FOUND] no call to 'add_conditional_edges' in 16 Python file(s)
[FAIL] REQ-024-T05: checkpointing (ALL: 1/2 satisfied)
[NOT FOUND] checkpointer configured across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /checkpoint/ in 16 files under implementation tree
[OK] graph compiled, which is where a checkpointer is attached (AST call analysis) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/validate_synthetic_data.py contains a call to 'compile'
[FAIL] REQ-024-T06: structured output at the graph boundary across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /with_structured_output|response_format|BaseModel|TypedDict|model_json_schema/ in 16 files under implementation tree
```

### REQ-025 - FAIL (14/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 3.3 Expected Solution — bullet 2

**Requirement:**

~~~text
A custom MCP server (≥ 2 tools + 1 resource) consumed via langchain-mcp-adapters, engineered context (write/select/compress/isolate + summarization + quarantine of untrusted applicant-supplied text), tiered memory with verified cross-session persistence, and an agentic-RAG tool over a synthetic lending-policy corpus.
~~~

**Status:** FAIL  
**Fit Score:** 14  
**Tests:** REQ-025-T01, REQ-025-T02, REQ-025-T03, REQ-025-T04, REQ-025-T05, REQ-025-T06, REQ-025-T07  
**Reason:** 6 of 7 bound test(s) produced no satisfying evidence: REQ-025-T01, REQ-025-T02, REQ-025-T03, REQ-025-T04, REQ-025-T06, REQ-025-T07.

**Evidence:**

```
[FAIL] REQ-025-T01: No MCP server package at or near 'mcp_server/'.
[FAIL] REQ-025-T02: langchain-mcp-adapters consumption (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'langchain-mcp-adapters declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] langchain_mcp_adapters imported (import analysis) (ALL: 0/1 satisfied)
[NOT FOUND] module 'langchain_mcp_adapters' is never imported
[FAIL] REQ-025-T03: Cannot check 'the four context operations': no directory at or near 'src/context'
[FAIL] REQ-025-T04: Cannot check 'summarization in the context layer': no directory at or near 'src/context'
[PASS] REQ-025-T05: quarantine of untrusted applicant-supplied text across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:449: "action_taken": "QUARANTINED_AND_ESCALATED",
[FAIL] REQ-025-T06: verified cross-session persistence (ALL: 0/3 satisfied)
[NOT FOUND] No directory at or near 'src/memory' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_memory_persistence.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'logs/memory_test.log' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-025-T07: agentic-RAG over a synthetic lending-policy corpus (ALL: 1/2 satisfied)
[NOT FOUND] No file at or near 'src/tools/rag_tool.py' under E:\Virtusa Projects\CredPilot
[OK] Directory present: synthetic_data/policy_corpus (near match for 'data/policy_corpus'); 42 entries: POL-AST-001_assets-eligibility_v1.0.md, POL-AST-002_funds-to-close_v1.0.md, POL-AST-003_reserves_v1.0.md, POL-AST-003_reserves_v2.0.md, POL-AST-004_source-of-funds_v1.0.md, POL-CONV-001_conventional-purchase_v1.0.md, POL-CONV-002_conventional-rate-term-refinance_v1.0.md, POL-CONV-003_cash-out-refinance_v1.0.md, POL-CRD-001_credit-assessment_v1.0.md, POL-CRD-001_credit-assessment_v2.0.md, POL-CRD-002_credit-events_v1.0.md, POL-CRD-003_delinquency-treatment_v1.0.md...
```

### REQ-026 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 3.3 Expected Solution — bullet 3

**Requirement:**

~~~text
Arize Phoenix instrumentation with a committed trace export, a machine-generated tool-invocation log, and an evidence-linked failure-mode analysis.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-026-T01, REQ-026-T02, REQ-026-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-026-T01, REQ-026-T02, REQ-026-T03.

**Evidence:**

```
[FAIL] REQ-026-T01: committed Phoenix trace export (ALL: 0/2 satisfied)
[NOT FOUND] trace export artifact (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'traces/phoenix_spans.jsonl' under E:\Virtusa Projects\CredPilot
[NOT FOUND] the export is committed (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' to check for commitment
[NOT FOUND] No file at or near 'traces/phoenix_spans.jsonl' to check for commitment
[FAIL] REQ-026-T02: machine-generated tool-invocation log (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'logs/tool_calls.jsonl'
[NOT FOUND] no committed Python source matches any producer pattern ['tool_calls\\.jsonl', 'tool[_\\- ]?call.*(?:append|write|dump)'] - the artifact cannot be shown to be machine-generated
[FAIL] REQ-026-T03: evidence-linked failure-mode analysis (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'docs/failure-analysis.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'Phoenix evidence links': no file at or near 'docs/failure-analysis.md'
```

### REQ-027 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 3.3 Expected Solution — bullet 4

**Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-027-T01, REQ-027-T02, REQ-027-T03, REQ-027-T04, REQ-027-T05, REQ-027-T06  
**Reason:** 6 of 6 bound test(s) produced no satisfying evidence: REQ-027-T01, REQ-027-T02, REQ-027-T03, REQ-027-T04, REQ-027-T05, REQ-027-T06.

**Evidence:**

```
[FAIL] REQ-027-T01: No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-027-T02: cost/latency dashboard (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/dashboard.png' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'reports/dashboard_data.csv' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-027-T03: No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-027-T04: No file at or near 'logs/agent_actions.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-027-T05: secrets hygiene (ALL: 1/2 satisfied)
[NOT FOUND] No file at or near '.env.example' under E:\Virtusa Projects\CredPilot
[OK] File present: synthetic_data/.gitignore (near match for '.gitignore'); size=86 bytes
[FAIL] REQ-027-T06: governance pack (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/model-card.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/output-risk.md' under E:\Virtusa Projects\CredPilot
```

### REQ-028 - FAIL (20/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 3.3 Expected Solution — bullet 5

**Requirement:**

~~~text
Agent-level evaluation (LLM-as-judge + hallucination) and agent tests (routing-logic, loop/cascade guard, tool-contract), with a reproducible local-run runbook.
~~~

**Status:** FAIL  
**Fit Score:** 20  
**Tests:** REQ-028-T01, REQ-028-T02, REQ-028-T03, REQ-028-T04, REQ-028-T05  
**Reason:** 4 of 5 bound test(s) produced no satisfying evidence: REQ-028-T01, REQ-028-T02, REQ-028-T03, REQ-028-T04.

**Evidence:**

```
[FAIL] REQ-028-T01: LLM-as-judge and hallucination evaluation (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No JSON artifact at or near 'reports/eval_report.json'
[FAIL] REQ-028-T02: No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-028-T03: No file at or near 'tests/test_loops.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-028-T04: No file at or near 'tests/test_tool_contracts.py' under E:\Virtusa Projects\CredPilot
[PASS] REQ-028-T05: local-run runbook (ALL: 2/2 satisfied)
[OK] File present: synthetic_data/README.md (near match for 'README.md'); size=14865 bytes
[OK] a documented runnable command block in synthetic_data/README.md (near match for 'README.md') (ANY: 1/1 satisfied)
[OK] synthetic_data/README.md:11: ```bash
```

### REQ-029 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 3.4 Applicable Rules — bullet 1 (Evidence-in-Repo Rule)

**Requirement:**

~~~text
Evidence-in-Repo Rule. Only committed artifacts are scored. A claim with no committed evidence scores zero; an evidence artifact with no producing code (a metric, trace or log a team could hand-write) is heavily discounted.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-029-T01, REQ-029-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-029-T01, REQ-029-T02.

**Evidence:**

```
[FAIL] REQ-029-T01: 2 artifact(s) exist on disk but are not listed by 'git ls-files': synthetic_data/.gitignore, synthetic_data/README.md. Committed: 0.
[FAIL] REQ-029-T02: None of the machine-generated evidence artifacts named by the document exist, so no producing code can be evidenced.
```

### REQ-030 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 3.4 Applicable Rules — bullet 2 (Citation-Resolves Rule)

**Requirement:**

~~~text
Citation-Resolves Rule. Wherever a document cites evidence (a Phoenix run/span id, a log record, a control file), the citation must resolve to a committed artifact. Unresolvable citations are treated as missing.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-030-T01, REQ-030-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-030-T01, REQ-030-T02.

**Evidence:**

```
[FAIL] REQ-030-T01: Cannot check citations: no document at or near 'docs/failure-analysis.md'
[FAIL] REQ-030-T02: governance pack citations resolve (ALL: 0/4 satisfied)
[NOT FOUND] Cannot check citations: no document at or near 'docs/risk-register.md'
[NOT FOUND] Cannot check citations: no document at or near 'docs/model-card.md'
[NOT FOUND] Cannot check citations: no document at or near 'docs/compliance.md'
[NOT FOUND] Cannot check citations: no document at or near 'docs/output-risk.md'
```

### REQ-031 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 3.4 Applicable Rules — bullet 3 (Synthetic-Data Rule)

**Requirement:**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-031-T01, REQ-031-T02, REQ-031-T03  
**Reason:** All 3 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-031-T01: synthetic data declared for applications and policies across implementation tree (149 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/applications/APP-000001.json:133: "relative_path": "synthetic_data/applicant_documents/APP-000001/01_loan_application_summary.txt"
[PASS] REQ-031-T02: unmasked payment-card numbers: no prohibited pattern matched across 1327 scanned files
[PASS] REQ-031-T03: PII masking and leak-free logs (ALL: 2/2 satisfied)
[OK] masking implemented at synthetic_data/generator/synth/people.py:238: mask_ssn(
[OK] no plaintext sensitive identifier in 1178 scanned log/data artifact(s)
```

### REQ-032 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 3.4 Applicable Rules — bullet 4 (Open-Source & Gemini-Only Rule)

**Requirement:**

~~~text
Open-Source & Gemini-Only Rule. Use the approved open-source stack with Google Gemini as the only model provider (not Claude). Build, run and evaluate with pip + Python — no Docker or external database service required for this cut.
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-032-T01, REQ-032-T02, REQ-032-T03, REQ-032-T04  
**Reason:** 2 of 4 bound test(s) produced no satisfying evidence: REQ-032-T01, REQ-032-T03.

**Evidence:**

```
[FAIL] REQ-032-T01: Google Gemini as model provider (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'a Google Gemini SDK declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Gemini referenced in the implementation across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /gemini/ in 16 files under implementation tree
[PASS] REQ-032-T02: no Claude provider (ALL: 2/2 satisfied)
[OK] Claude/Anthropic provider usage: no prohibited pattern matched across 16 scanned files
[OK] Claude/Anthropic dependency declaration: no prohibited pattern matched across 1140 scanned files
[FAIL] REQ-032-T03: pip + Python toolchain (ALL: 0/2 satisfied)
[NOT FOUND] a pip-installable dependency manifest (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'requirements.txt' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'pyproject.toml' under E:\Virtusa Projects\CredPilot
[NOT FOUND] documented pip install step in synthetic_data/README.md (near match for 'README.md') (ANY: 0/1 satisfied)
[NOT FOUND] no match for /pip\s+install/ in synthetic_data/README.md
[PASS] REQ-032-T04: no Docker or external DB service required (ALL: 2/2 satisfied)
[OK] container build/orchestration files: no file matches ['Dockerfile', 'docker-compose*.yml', 'docker-compose*.yaml', '*.dockerfile', 'compose.yaml', 'compose.yml'] across 1328 files
[OK] external database service connection strings: no prohibited pattern matched across 1207 scanned files
```

### REQ-033 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 3.4 Applicable Rules — bullet 5 (Reproducibility Rule)

**Requirement:**

~~~text
Reproducibility Rule. The system, its traces and its evaluation must be regenerable from a single documented command with committed sample inputs.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-033-T01, REQ-033-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-033-T01, REQ-033-T02.

**Evidence:**

```
[FAIL] REQ-033-T01: documented regeneration commands (ALL: 1/3 satisfied)
[OK] documented command to run the copilot: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[NOT FOUND] no documented command to regenerate the Phoenix traces: synthetic_data/README.md documents no command mentioning ('trace', 'phoenix', 'span', 'observability')
[NOT FOUND] no documented command to regenerate the evaluation: synthetic_data/README.md documents no command mentioning ('eval', 'deepeval', 'golden', 'judge')
[FAIL] REQ-033-T02: committed sample inputs: no sample input files found under any of data, samples, sample_inputs, inputs, fixtures, examples, data/samples, data/applications, tests/data
```

### REQ-034 - FAIL (33/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — lead-in paragraph

**Requirement:**

~~~text
Fixed open-source toolchain with Google Gemini as the only model provider. Everything installs with pip; no Docker or external DB service required.
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-034-T01, REQ-034-T02, REQ-034-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-034-T01, REQ-034-T02.

**Evidence:**

```
[FAIL] REQ-034-T01: Gemini is the only model provider (ALL: 1/2 satisfied)
[NOT FOUND] Cannot check 'a Google Gemini SDK declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[OK] a competing model-provider dependency: no prohibited pattern matched across 1140 scanned files
[FAIL] REQ-034-T02: pip-installable manifest (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'requirements.txt' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'pyproject.toml' under E:\Virtusa Projects\CredPilot
[PASS] REQ-034-T03: no Docker or external DB service (ALL: 2/2 satisfied)
[OK] container build/orchestration files: no file matches ['Dockerfile', 'docker-compose*.yml', 'docker-compose*.yaml', 'compose.yaml', 'compose.yml'] across 1328 files
[OK] external database service connection strings: no prohibited pattern matched across 1207 scanned files
```

### REQ-035 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "Language / Agent Framework"

**Requirement:**

~~~text
Language / Agent Framework | Python 3.11+ · LangGraph (MIT)
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-035-T01, REQ-035-T02, REQ-035-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-035-T01, REQ-035-T02, REQ-035-T03.

**Evidence:**

```
[FAIL] REQ-035-T01: No declaration of Python 3.11+ found in any of: pyproject.toml, setup.cfg, setup.py, .python-version, runtime.txt, README.md, requirements.txt
[FAIL] REQ-035-T02: LangGraph agent framework (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'langgraph declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] langgraph imported (import analysis) (ALL: 0/1 satisfied)
[NOT FOUND] module 'langgraph' is never imported
[FAIL] REQ-035-T03: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'any licence artifact the implementation must carry to evidence LangGraph's MIT licence' could be verified against an implementation.
```

### REQ-036 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "LLM Provider"

**Requirement:**

~~~text
LLM Provider | Google Gemini (API) — the only approved provider; not Claude
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-036-T01, REQ-036-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-036-T01.

**Evidence:**

```
[FAIL] REQ-036-T01: Gemini API usage (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'a Google Gemini SDK declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Gemini model referenced across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /gemini/ in 16 files under implementation tree
[PASS] REQ-036-T02: Claude/Anthropic usage: no prohibited pattern matched across 1156 scanned files
```

### REQ-037 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "Interoperability"

**Requirement:**

~~~text
Interoperability | MCP Python SDK (stdio) + langchain-mcp-adapters
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-037-T01, REQ-037-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-037-T01, REQ-037-T02.

**Evidence:**

```
[FAIL] REQ-037-T01: MCP Python SDK over stdio (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'the MCP Python SDK declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] stdio transport configured across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /stdio/ in 16 files under implementation tree
[FAIL] REQ-037-T02: langchain-mcp-adapters (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'langchain-mcp-adapters declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] langchain_mcp_adapters imported (import analysis) (ALL: 0/1 satisfied)
[NOT FOUND] module 'langchain_mcp_adapters' is never imported
```

### REQ-038 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 4. Technology & Framework Stack — table row "Memory"

**Requirement:**

~~~text
Memory | langgraph-checkpoint-sqlite (SQLite file) + LangMem
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-038-T01, REQ-038-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-038-T01, REQ-038-T02.

**Evidence:**

```
[FAIL] REQ-038-T01: langgraph-checkpoint-sqlite (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'langgraph-checkpoint-sqlite declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] SQLite checkpointer used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /SqliteSaver|langgraph\.checkpoint\.sqlite|AsyncSqliteSaver/ in 16 files under implementation tree
[FAIL] REQ-038-T02: LangMem (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'langmem declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] LangMem used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /langmem/ in 16 files under implementation tree
```

### REQ-039 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** policy  |  **Source:** Section 4. Technology & Framework Stack — table row "Retrieval"

**Requirement:**

~~~text
Retrieval | Chroma or FAISS + Sentence-Transformers (local)
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-039-T01, REQ-039-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-039-T01, REQ-039-T02.

**Evidence:**

```
[FAIL] REQ-039-T01: Chroma or FAISS (ANY: 0/2 satisfied)
[NOT FOUND] Chroma (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'chromadb declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Chroma used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /chroma/ in 16 files under implementation tree
[NOT FOUND] FAISS (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'faiss declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] FAISS used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /faiss/ in 16 files under implementation tree
[FAIL] REQ-039-T02: Sentence-Transformers (local) (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'sentence-transformers declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Sentence-Transformers used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /sentence_transformers|SentenceTransformer/ in 16 files under implementation tree
```

### REQ-040 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 4. Technology & Framework Stack — table row "Observability (mandated)"

**Requirement:**

~~~text
Observability (mandated) | Arize Phoenix + OpenTelemetry / openinference (local, in-process)
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-040-T01, REQ-040-T02, REQ-040-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-040-T01, REQ-040-T02, REQ-040-T03.

**Evidence:**

```
[FAIL] REQ-040-T01: Arize Phoenix (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'arize-phoenix declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] phoenix imported (import analysis) (ALL: 0/1 satisfied)
[NOT FOUND] module 'phoenix' is never imported
[FAIL] REQ-040-T02: OpenTelemetry / openinference (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'openinference/OpenTelemetry declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] openinference/OpenTelemetry imported (import analysis) (ANY: 0/2 satisfied)
[NOT FOUND] module 'openinference' is never imported
[NOT FOUND] module 'opentelemetry' is never imported
[FAIL] REQ-040-T03: local in-process Phoenix session across implementation tree (67 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /px\.launch_app|phoenix\.launch_app|localhost:6006|127\.0\.0\.1:6006|register\(/ in 67 files under implementation tree
```

### REQ-041 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 4. Technology & Framework Stack — table row "Evaluation"

**Requirement:**

~~~text
Evaluation | DeepEval (LLM-as-judge = Gemini) · pytest for agent tests
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-041-T01, REQ-041-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-041-T01, REQ-041-T02.

**Evidence:**

```
[FAIL] REQ-041-T01: DeepEval with a Gemini judge (ALL: 0/3 satisfied)
[NOT FOUND] Cannot check 'deepeval declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] DeepEval used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /deepeval/ in 16 files under implementation tree
[NOT FOUND] Gemini configured as the judge model across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /gemini/ in 16 files under implementation tree
[FAIL] REQ-041-T02: pytest for agent tests (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'pytest declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
```

### REQ-042 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 4. Technology & Framework Stack — table row "Security"

**Requirement:**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-042-T01, REQ-042-T02, REQ-042-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-042-T01, REQ-042-T02, REQ-042-T03.

**Evidence:**

```
[FAIL] REQ-042-T01: Guardrails-AI or LLM Guard (ANY: 0/2 satisfied)
[NOT FOUND] Cannot check 'guardrails-ai declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Cannot check 'llm-guard declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[FAIL] REQ-042-T02: Presidio for PII (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'presidio declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Presidio used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /presidio/ in 16 files under implementation tree
[FAIL] REQ-042-T03: python-dotenv (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'python-dotenv declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] dotenv used across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /dotenv/ in 16 files under implementation tree
```

### REQ-043 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 4. Technology & Framework Stack — table row "Interface" (continuation table)

**Requirement:**

~~~text
Interface | CLI (required) · FastAPI streaming (optional / bonus)
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-043-T01, REQ-043-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-043-T01: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in synthetic_data/generator/generate_synthetic_data.py
[OK] CLI invocation documented: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[PASS] REQ-043-T02: FastAPI streaming (optional / bonus): not present at or near 'src/api'. The source text marks this surface optional / bonus and explicitly not required, so its absence satisfies the interface requirement.
```

### REQ-044 - FAIL (33/100)

**Class:** IMPLEMENTATION  |  **Category:** eligibility  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-01

**Requirement:**

~~~text
AC-01 | Given a synthetic loan application, the copilot retrieves the applicable current lending policy and returns an eligibility determination that cites the policy rule it applied.
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-044-T01, REQ-044-T02, REQ-044-T03, REQ-044-T04  
**Reason:** 3 of 4 bound test(s) produced no satisfying evidence: REQ-044-T01, REQ-044-T03, REQ-044-T04.

**Evidence:**

```
[FAIL] REQ-044-T01: eligibility determination in observable output (from 'python synthetic_data/generator/generate_synthetic_data.py') (ALL: 0/1 satisfied)
[NOT FOUND] /eligib/ not present in the output of 'python synthetic_data/generator/generate_synthetic_data.py'
--- observable output (last lines) ---
CredPilot synthetic data generator - seed 20260920
----------------------------------------------------------------------
1/8  policy corpus
     42 documents, 203 rule versions
2/8  building applications (asserting each scenario)
     75 applications, 90 people
3/8  structured tables and documents
     12091 rows across 32 tables
4/8  profiles
5/8  application input packets
6/8  scenarios and golden set
7/8  schemas
8/8  generated documentation
----------------------------------------------------------------------
Generation complete.
  policy documents      42
  policy rule versions  203
  applications          75
  borrowers             90
  applicant documents   1140
  rule evaluations      1827
  golden cases          75

Next: python synthetic_data/generator/validate_synthetic_data.py
[PASS] REQ-044-T02: policy rule citation in observable output (from 'python synthetic_data/generator/generate_synthetic_data.py') (ALL: 2/2 satisfied)
[OK] /polic(y|ies)/ matched observable output: 'policy'
[OK] /rule|clause|section|citation|cite/ matched observable output: 'rule'
--- observable output (last lines) ---
CredPilot synthetic data generator - seed 20260920
----------------------------------------------------------------------
1/8  policy corpus
     42 documents, 203 rule versions
2/8  building applications (asserting each scenario)
     75 applications, 90 people
3/8  structured tables and documents
     12091 rows across 32 tables
4/8  profiles
5/8  application input packets
6/8  scenarios and golden set
7/8  schemas
8/8  generated documentation
----------------------------------------------------------------------
Generation complete.
  policy documents      42
  policy rule versions  203
  applications          75
  borrowers             90
  applicant documents   1140
  rule evaluations      1827
  golden cases          75

Next: python synthetic_data/generator/validate_synthetic_data.py
[FAIL] REQ-044-T03: current lending policy retrieval (ALL: 1/2 satisfied)
[NOT FOUND] No file at or near 'src/tools/rag_tool.py' under E:\Virtusa Projects\CredPilot
[OK] Directory present: synthetic_data/policy_corpus (near match for 'data/policy_corpus'); 42 entries: POL-AST-001_assets-eligibility_v1.0.md, POL-AST-002_funds-to-close_v1.0.md, POL-AST-003_reserves_v1.0.md, POL-AST-003_reserves_v2.0.md, POL-AST-004_source-of-funds_v1.0.md, POL-CONV-001_conventional-purchase_v1.0.md, POL-CONV-002_conventional-rate-term-refinance_v1.0.md, POL-CONV-003_cash-out-refinance_v1.0.md, POL-CRD-001_credit-assessment_v1.0.md, POL-CRD-001_credit-assessment_v2.0.md, POL-CRD-002_credit-events_v1.0.md, POL-CRD-003_delinquency-treatment_v1.0.md...
[FAIL] REQ-044-T04: committed synthetic loan applications: no sample input files found under any of data, samples, sample_inputs, inputs, fixtures, examples, data/samples, data/applications, tests/data
```

### REQ-045 - FAIL (40/100)

**Class:** IMPLEMENTATION  |  **Category:** affordability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-02

**Requirement:**

~~~text
AC-02 | The copilot computes affordability (DTI / disposable income) from the application data and flags any policy breach with the threshold it failed.
~~~

**Status:** FAIL  
**Fit Score:** 40  
**Tests:** REQ-045-T01, REQ-045-T02, REQ-045-T03, REQ-045-T04  
**Reason:** 2 of 4 bound test(s) produced no satisfying evidence: REQ-045-T02, REQ-045-T04.

**Evidence:**

```
[PASS] REQ-045-T01: DTI / disposable-income computation across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/build.py:10: debt-to-income ratio lands on its target to the cent, the assets are solved so the
[FAIL] REQ-045-T02: affordability figure in observable output (from 'python synthetic_data/generator/generate_synthetic_data.py') (ALL: 0/1 satisfied)
[NOT FOUND] /afford|\bDTI\b|disposable/ not present in the output of 'python synthetic_data/generator/generate_synthetic_data.py'
--- observable output (last lines) ---
CredPilot synthetic data generator - seed 20260920
----------------------------------------------------------------------
1/8  policy corpus
     42 documents, 203 rule versions
2/8  building applications (asserting each scenario)
     75 applications, 90 people
3/8  structured tables and documents
     12091 rows across 32 tables
4/8  profiles
5/8  application input packets
6/8  scenarios and golden set
7/8  schemas
8/8  generated documentation
----------------------------------------------------------------------
Generation complete.
  policy documents      42
  policy rule versions  203
  applications          75
  borrowers             90
  applicant documents   1140
  rule evaluations      1827
  golden cases          75

Next: python synthetic_data/generator/validate_synthetic_data.py
[PASS] REQ-045-T03: threshold-bearing policy breach flag across implementation tree (16 files) (ALL: 2/2 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:292: "threshold_value": ev.threshold_value,
[OK] synthetic_data/generator/generate_synthetic_data.py:13: scenario stops producing the outcome it declares, generation fails loudly rather
[FAIL] REQ-045-T04: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the numeric DTI or disposable-income threshold that constitutes a policy breach' could be verified against an implementation.
```

### REQ-046 - FAIL (44/100)

**Class:** IMPLEMENTATION  |  **Category:** underwriting  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-03

**Requirement:**

~~~text
AC-03 | The copilot produces a decision recommendation (approve / refer / decline) with a written rationale; a decline or high-value case is routed for human review rather than auto-decided.
~~~

**Status:** FAIL  
**Fit Score:** 44  
**Tests:** REQ-046-T01, REQ-046-T02, REQ-046-T03, REQ-046-T04, REQ-046-T05, REQ-046-T06, REQ-046-T07  
**Reason:** 3 of 7 bound test(s) produced no satisfying evidence: REQ-046-T01, REQ-046-T03, REQ-046-T07.

**Evidence:**

```
[FAIL] REQ-046-T01: No decision recommendation term ['approve', 'refer', 'decline'] in the output of 'python synthetic_data/generator/generate_synthetic_data.py'
[PASS] REQ-046-T02: the approve / refer / decline outcomes across implementation tree (16 files) (ALL: 3/3 satisfied)
[OK] synthetic_data/generator/synth/documents.py:1333: "received and accepted, or to WAIVED only under an approved exception.",
[OK] synthetic_data/generator/generate_synthetic_data.py:87: refers = {e.rule_id for e in result.refers}
[OK] synthetic_data/generator/generate_synthetic_data.py:573: if rec == "DECLINE_RECOMMENDATION":
[FAIL] REQ-046-T03: written rationale in observable output (from 'python synthetic_data/generator/generate_synthetic_data.py') (ALL: 0/1 satisfied)
[NOT FOUND] /rationale|reason|justification|because|explanation/ not present in the output of 'python synthetic_data/generator/generate_synthetic_data.py'
--- observable output (last lines) ---
CredPilot synthetic data generator - seed 20260920
----------------------------------------------------------------------
1/8  policy corpus
     42 documents, 203 rule versions
2/8  building applications (asserting each scenario)
     75 applications, 90 people
3/8  structured tables and documents
     12091 rows across 32 tables
4/8  profiles
5/8  application input packets
6/8  scenarios and golden set
7/8  schemas
8/8  generated documentation
----------------------------------------------------------------------
Generation complete.
  policy documents      42
  policy rule versions  203
  applications          75
  borrowers             90
  applicant documents   1140
  rule evaluations      1827
  golden cases          75

Next: python synthetic_data/generator/validate_synthetic_data.py
[PASS] REQ-046-T04: decline handling across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:573: if rec == "DECLINE_RECOMMENDATION":
[PASS] REQ-046-T05: high-value case routing across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:572: return "HIGH_VALUE_UNDERWRITING"
[PASS] REQ-046-T06: human-review route across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:56: requires_human_review,
[FAIL] REQ-046-T07: UNSPECIFIED_BY_REQUIREMENT: the source document states no value or artifact from which 'the loan value above which a case counts as a high-value case' could be verified against an implementation.
```

### REQ-047 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** workflow  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-04

**Requirement:**

~~~text
AC-04 | The copilot identifies each application's intent and handles it with the right capability; ambiguous or out-of-scope requests are clarified or escalated to a human, not mishandled.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-047-T01, REQ-047-T02, REQ-047-T03, REQ-047-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-047-T01: intent identification across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:631: ("AUTOMATED_COMPONENT", "classify_request", "intent_classifier",
[PASS] REQ-047-T02: intent-to-capability dispatch across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/people.py:114: "transport": ("Route Manager", "Dispatch Lead", "Logistics Planner"),
[PASS] REQ-047-T03: clarification of ambiguous requests across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/emit.py:588: "OUT_OF_SCOPE_REQUEST": "CLARIFY_OR_ESCALATE",
[PASS] REQ-047-T04: out-of-scope escalation across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:449: "action_taken": "QUARANTINED_AND_ESCALATED",
```

### REQ-048 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-05

**Requirement:**

~~~text
AC-05 | The copilot maintains context — it uses facts stated earlier in the interaction and recalls prior-session context on a return visit.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-048-T01, REQ-048-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-048-T01, REQ-048-T02.

**Evidence:**

```
[FAIL] REQ-048-T01: within-interaction context (ALL: 1/2 satisfied)
[NOT FOUND] No directory at or near 'src/memory' under E:\Virtusa Projects\CredPilot
[OK] short-term conversational context across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/build.py:86: income_history: list[dict[str, Any]] = field(default_factory=list)
[FAIL] REQ-048-T02: cross-session recall (ALL: 1/3 satisfied)
[NOT FOUND] No file at or near 'tests/test_memory_persistence.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'logs/memory_test.log' under E:\Virtusa Projects\CredPilot
[OK] session-keyed persistence across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/scenarios.py:1392: "property. Prior-session context must be recalled without carrying stale "
```

### REQ-049 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-06

**Requirement:**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-049-T01, REQ-049-T02, REQ-049-T03, REQ-049-T04  
**Reason:** All 4 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-049-T01: prompt-injection refusal across implementation tree (16 files) (ALL: 2/2 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:606: "PROMPT_INJECTION": "SEC-INJ-001",
[OK] synthetic_data/generator/synth/build.py:970: title_exception_blocking=spec.title_exception_blocking,
[PASS] REQ-049-T02: per-applicant data access control across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/build.py:933: ownership_months=spec.ownership_months,
[PASS] REQ-049-T03: PII masking and leak-free logs (ALL: 2/2 satisfied)
[OK] masking implemented at synthetic_data/generator/synth/people.py:238: mask_ssn(
[OK] no plaintext sensitive identifier in 1178 scanned log/data artifact(s)
[PASS] REQ-049-T04: output-side masking before answers are emitted across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:184: "ssn_masked": person.ssn_masked,
```

### REQ-050 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-07

**Requirement:**

~~~text
AC-07 | A machine-generated tool-invocation log (logs/tool_calls.jsonl) written by committed logging middleware; tool names reconcile with the agent/MCP code.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-050-T01, REQ-050-T02, REQ-050-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-050-T01, REQ-050-T02, REQ-050-T03.

**Evidence:**

```
[FAIL] REQ-050-T01: No tool-invocation log at or near 'logs/tool_calls.jsonl'.
[FAIL] REQ-050-T02: committed logging middleware that writes the tool-invocation log (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'logs/tool_calls.jsonl'
[NOT FOUND] no committed Python source matches any producer pattern ['tool_calls\\.jsonl'] - the artifact cannot be shown to be machine-generated
[FAIL] REQ-050-T03: Cannot reconcile tool names: no log at or near 'logs/tool_calls.jsonl'
```

### REQ-051 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-08

**Requirement:**

~~~text
AC-08 | docs/failure-analysis.md documents ≥ 3 real failures from your own runs, each citing the Phoenix run_id + span_id (or a tool-log record) that shows it, plus root cause and fix.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-051-T01, REQ-051-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-051-T01, REQ-051-T02.

**Evidence:**

```
[FAIL] REQ-051-T01: No failure-mode analysis at or near 'docs/failure-analysis.md'.
[FAIL] REQ-051-T02: 153 unresolvable citation(s) across 51 document(s) (treated as missing per the Citation-Resolves Rule):
synthetic_data/DATA_DICTIONARY.md cites 'synthetic_data/generator/generate_synthetic_data.py' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'application_borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'applications.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'appraisals.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'asset_transactions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'assets.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'audit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrower_demographics.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'conditions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_accounts.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_profiles.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decision_reasons.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decisions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'document_extractions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'documents.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'eligibility_results.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'employment.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'fraud_checks.csv' -> present but uncommitted
```

### REQ-052 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-09

**Requirement:**

~~~text
AC-09 | A Phoenix-derived golden-signals report (latency incl. thinking/acting/tool, tokens, cost estimate, plus accuracy + hallucination rate from the eval) and a cost/latency dashboard (Phoenix screenshot + underlying data file).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-052-T01, REQ-052-T02, REQ-052-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-052-T01, REQ-052-T02, REQ-052-T03.

**Evidence:**

```
[FAIL] REQ-052-T01: No golden-signals report at or near 'reports/golden_signals.json'.
[FAIL] REQ-052-T02: Phoenix-derived golden-signals report (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'reports/golden_signals.json'
[NOT FOUND] no committed Python source matches any producer pattern ['get_spans_dataframe', 'golden_signals\\.json'] - the artifact cannot be shown to be machine-generated
[FAIL] REQ-052-T03: cost/latency dashboard screenshot AND its underlying data file (ALL: 0/2 satisfied)
[NOT FOUND] no dashboard screenshot at or near 'reports/dashboard.png'
[NOT FOUND] no underlying data file at or near 'reports/dashboard_data.csv'
```

### REQ-053 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-10

**Requirement:**

~~~text
AC-10 | Input/output guardrails wired into the agent's I/O path, and a machine-generated audit trail of agent actions (logs/agent_actions.jsonl).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-053-T01, REQ-053-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-053-T01, REQ-053-T02.

**Evidence:**

```
[FAIL] REQ-053-T01: input/output guardrails wired into the I/O path (ALL: 1/5 satisfied)
[NOT FOUND] no guardrail package at or near 'src/guardrails/'
[NOT FOUND] input guardrail: no match for /input[_\- ]?guard|validate_input|check_input|on_input/ in the guardrail package
[NOT FOUND] output guardrail: no match for /output[_\- ]?guard|validate_output|check_output|on_output/ in the guardrail package
[NOT FOUND] blocks or sanitizes: no match for /\bblock|\brefus|saniti[sz]e|redact|\braise\b/ in the guardrail package
[OK] wired into the I/O path: synthetic_data/generator/generate_synthetic_data.py references the guardrail layer
[FAIL] REQ-053-T02: No audit trail at or near 'logs/agent_actions.jsonl'.
```

### REQ-054 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-11

**Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-054-T01, REQ-054-T02, REQ-054-T03, REQ-054-T04, REQ-054-T05  
**Reason:** 5 of 5 bound test(s) produced no satisfying evidence: REQ-054-T01, REQ-054-T02, REQ-054-T03, REQ-054-T04, REQ-054-T05.

**Evidence:**

```
[FAIL] REQ-054-T01: No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-054-T02: No file at or near 'docs/model-card.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-054-T03: compliance mapping: no document at or near 'docs/compliance.md'.
[FAIL] REQ-054-T04: No file at or near 'docs/output-risk.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-054-T05: 153 unresolvable citation(s) across 51 document(s) (treated as missing per the Citation-Resolves Rule):
synthetic_data/DATA_DICTIONARY.md cites 'synthetic_data/generator/generate_synthetic_data.py' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'application_borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'applications.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'appraisals.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'asset_transactions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'assets.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'audit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrower_demographics.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'conditions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_accounts.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_profiles.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decision_reasons.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decisions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'document_extractions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'documents.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'eligibility_results.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'employment.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'fraud_checks.csv' -> present but uncommitted
```

### REQ-055 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 5.1 Functional Acceptance Criteria — table row AC-12

**Requirement:**

~~~text
AC-12 | Agent evaluation: a DeepEval (or equivalent) report over a golden set (hallucination + faithfulness/relevance), and agent tests — routing-logic, loop/cascade guard, and tool-contract.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-055-T01, REQ-055-T02, REQ-055-T03, REQ-055-T04  
**Reason:** 4 of 4 bound test(s) produced no satisfying evidence: REQ-055-T01, REQ-055-T02, REQ-055-T03, REQ-055-T04.

**Evidence:**

```
[FAIL] REQ-055-T01: No evaluation report at or near 'reports/eval_report.json'.
[FAIL] REQ-055-T02: routing-logic test: no test module at or near 'tests/test_routing.py'.
[FAIL] REQ-055-T03: loop/cascade guard test: no test module at or near 'tests/test_loops.py'.
[FAIL] REQ-055-T04: tool-contract test: no test module at or near 'tests/test_tool_contracts.py'.
```

### REQ-056 - FAIL (67/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-01

**Requirement:**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-056-T01, REQ-056-T02, REQ-056-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-056-T02.

**Evidence:**

```
[PASS] REQ-056-T01: No committed secret matched 6 credential patterns across 1293 scanned files.
[FAIL] REQ-056-T02: secrets hygiene (ALL: 1/3 satisfied)
[NOT FOUND] synthetic_data/.gitignore has no rule covering .env
[NOT FOUND] no .env.example committed as the env-var config template
[OK] no .env file is committed
[PASS] REQ-056-T03: environment-variable configuration across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synthetic_data_utils.py:71: raw = os.environ.get("SYNTHETIC_SEED", "").strip()
```

### REQ-057 - FAIL (20/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-02

**Requirement:**

~~~text
NFR-02 | Single documented command runs the copilot and a second regenerates the Phoenix traces and the evaluation; committed sample inputs.
~~~

**Status:** FAIL  
**Fit Score:** 20  
**Tests:** REQ-057-T01, REQ-057-T02, REQ-057-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-057-T01, REQ-057-T03.

**Evidence:**

```
[FAIL] REQ-057-T01: single documented command plus a regeneration command (ALL: 1/3 satisfied)
[OK] single documented run command: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[NOT FOUND] no documented trace-regeneration command: synthetic_data/README.md documents no command mentioning ('trace', 'phoenix', 'span', 'observability')
[NOT FOUND] no documented evaluation command: synthetic_data/README.md documents no command mentioning ('eval', 'deepeval', 'golden', 'judge')
[PASS] REQ-057-T02: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in synthetic_data/generator/generate_synthetic_data.py
[OK] CLI invocation documented: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[FAIL] REQ-057-T03: committed sample inputs: no sample input files found under any of data, samples, sample_inputs, inputs, fixtures, examples, data/samples, data/applications, tests/data
```

### REQ-058 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-03

**Requirement:**

~~~text
NFR-03 | Untrusted free-text applicant-supplied content is quarantined and never treated as instructions.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-058-T01, REQ-058-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-058-T01: quarantine of untrusted applicant-supplied content across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:449: "action_taken": "QUARANTINED_AND_ESCALATED",
[PASS] REQ-058-T02: untrusted content marked as data, not instructions across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:448: "masked_excerpt": _mask_excerpt(spec.untrusted_text),
```

### REQ-059 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-04

**Requirement:**

~~~text
NFR-04 | Agent pipeline uses async where it calls tools/models; graceful degradation on tool/model failure (timeouts, retries, exit conditions).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-059-T01, REQ-059-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-059-T01, REQ-059-T02.

**Evidence:**

```
[FAIL] REQ-059-T01: async tool/model invocation (ALL: 0/2 satisfied)
[NOT FOUND] no 'async def' anywhere in the agent pipeline
[NOT FOUND] no 'await' expression: async is declared but never used
[FAIL] REQ-059-T02: graceful degradation on tool/model failure (ALL: 2/4 satisfied)
[NOT FOUND] timeouts: no match for /\btimeout\b/ in 16 Python file(s)
[NOT FOUND] retries: no match for /\bretry|retries|tenacity|max_attempts|backoff\b/ in 16 Python file(s)
[OK] exit conditions: synthetic_data/generator/synthetic_data_utils.py:491: break
[OK] failure handling around tool/model calls: synthetic_data/generator/synth/build.py:996: except KeyError:
```

### REQ-060 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-05

**Requirement:**

~~~text
NFR-05 | All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-060-T01, REQ-060-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-060-T01: synthetic data declaration across implementation tree (149 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/applications/APP-000001.json:133: "relative_path": "synthetic_data/applicant_documents/APP-000001/01_loan_application_summary.txt"
[PASS] REQ-060-T02: PII masking and leak-free logs (ALL: 2/2 satisfied)
[OK] masking implemented at synthetic_data/generator/synth/people.py:238: mask_ssn(
[OK] no plaintext sensitive identifier in 1178 scanned log/data artifact(s)
```

### REQ-061 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 5.2 Non-Functional Requirements — table row NFR-06

**Requirement:**

~~~text
NFR-06 | Evidence artifacts (traces, logs, reports) are machine-generated by committed code; the code that produced each is committed alongside it.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-061-T01, REQ-061-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-061-T01, REQ-061-T02.

**Evidence:**

```
[FAIL] REQ-061-T01: None of the machine-generated evidence artifacts named by the document exist, so no producing code can be evidenced.
[FAIL] REQ-061-T02: artifact and its producer both committed (ALL: 0/2 satisfied)
[NOT FOUND] None of the machine-generated evidence artifacts named by the document exist, so no producing code can be evidenced.
[NOT FOUND] 2 artifact(s) exist on disk but are not listed by 'git ls-files': synthetic_data/.gitignore, synthetic_data/README.md. Committed: 0.
```

### REQ-062 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 6.1 In Scope — bullet 1

**Requirement:**

~~~text
The LangGraph multi-agent copilot (foundation) plus its full observability, cost-governance, security, governance and evaluation surface.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-062-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-062-T01.

**Evidence:**

```
[FAIL] REQ-062-T01: the full in-scope surface (ALL: 0/6 satisfied)
[NOT FOUND] No file at or near 'src/graph.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'src/observability/tracing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
```

### REQ-063 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 6.1 In Scope — bullet 2

**Requirement:**

~~~text
Arize Phoenix tracing, golden-signals + cost/latency governance, guardrails + audit + secrets hygiene, governance/compliance docs, and agent-level evaluation & tests.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-063-T01, REQ-063-T02, REQ-063-T03, REQ-063-T04, REQ-063-T05  
**Reason:** 5 of 5 bound test(s) produced no satisfying evidence: REQ-063-T01, REQ-063-T02, REQ-063-T03, REQ-063-T04, REQ-063-T05.

**Evidence:**

```
[FAIL] REQ-063-T01: Phoenix tracing (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'src/observability/tracing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] a trace export (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'traces/phoenix_spans.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-063-T02: golden signals and cost/latency governance (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'reports/dashboard_data.csv' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-063-T03: guardrails, audit and secrets hygiene (ALL: 0/3 satisfied)
[NOT FOUND] No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'logs/agent_actions.jsonl' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near '.env.example' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-063-T04: governance and compliance docs (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/model-card.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/output-risk.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-063-T05: agent-level evaluation and tests (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_loops.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_tool_contracts.py' under E:\Virtusa Projects\CredPilot
```

### REQ-064 - FAIL (67/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 6.1 In Scope — bullet 3

**Requirement:**

~~~text
A CLI to drive applications through the graph and to regenerate traces and the evaluation.
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-064-T01, REQ-064-T02, REQ-064-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-064-T03.

**Evidence:**

```
[PASS] REQ-064-T01: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in synthetic_data/generator/generate_synthetic_data.py
[OK] CLI invocation documented: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[PASS] REQ-064-T02: the CLI invoking the graph across implementation tree (16 files) (ALL: 2/2 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:51: from synth.people import make_demographics, make_person
[OK] synthetic_data/generator/generate_synthetic_data.py:8: random draw is derived from a hash of that seed plus a stable label, so running
[FAIL] REQ-064-T03: single documented command plus a regeneration command (ALL: 1/3 satisfied)
[OK] single documented run command: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[NOT FOUND] no documented trace-regeneration command: synthetic_data/README.md documents no command mentioning ('trace', 'phoenix', 'span', 'observability')
[NOT FOUND] no documented evaluation command: synthetic_data/README.md documents no command mentioning ('eval', 'deepeval', 'golden', 'judge')
```

### REQ-065 - PASS (100/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 1

**Requirement:**

~~~text
Containerized / cloud deployment (Docker, Rancher, k8s) — deferred; do not spend hackathon time on it.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-065-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-065-T01: Docker / Rancher / k8s deployment artifacts: no file matches ['Dockerfile', '*.dockerfile', 'docker-compose*.yml', 'docker-compose*.yaml', 'compose.yaml', 'compose.yml', '*.k8s.yaml', 'Chart.yaml', 'rancher*.yml'] across 1328 files
```

### REQ-066 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 2

**Requirement:**

~~~text
Real credit-bureau or core-banking integrations — use synthetic application and policy data.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-066-T01, REQ-066-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-066-T01, REQ-066-T02.

**Evidence:**

```
[FAIL] REQ-066-T01: real credit-bureau or core-banking integrations: prohibited content found (1 hit(s))
/experian|equifax|transunion|cibil|creditbureau|credit[_\- ]bureau[_\- ]api/ matched synthetic_data/generator/synth/people.py:6: with no network access and no extra dependency - which is what the Reproducibility
[FAIL] REQ-066-T02: synthetic application and policy data (ALL: 1/2 satisfied)
[OK] Directory present: synthetic_data/policy_corpus (near match for 'data/policy_corpus'); 42 entries: POL-AST-001_assets-eligibility_v1.0.md, POL-AST-002_funds-to-close_v1.0.md, POL-AST-003_reserves_v1.0.md, POL-AST-003_reserves_v2.0.md, POL-AST-004_source-of-funds_v1.0.md, POL-CONV-001_conventional-purchase_v1.0.md, POL-CONV-002_conventional-rate-term-refinance_v1.0.md, POL-CONV-003_cash-out-refinance_v1.0.md, POL-CRD-001_credit-assessment_v1.0.md, POL-CRD-001_credit-assessment_v2.0.md, POL-CRD-002_credit-events_v1.0.md, POL-CRD-003_delinquency-treatment_v1.0.md...
[NOT FOUND] committed synthetic application data: no sample input files found under any of data, samples, sample_inputs, inputs, fixtures, examples, data/samples, data/applications, tests/data
```

### REQ-067 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** non_functional  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 3

**Requirement:**

~~~text
Front-end visual polish; generic unit-test volume for its own sake.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-067-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-067-T01: front-end build tooling: no file matches ['package.json', 'webpack.config.js', 'vite.config.*', 'tailwind.config.*', 'next.config.*', 'angular.json'] across 1328 files
```

### REQ-068 - FAIL (50/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 6.2 Out of Scope (this cut) — bullet 4

**Requirement:**

~~~text
Advanced OAuth flows and live secrets-rotation infrastructure (document the approach instead).
~~~

**Status:** FAIL  
**Fit Score:** 50  
**Tests:** REQ-068-T01, REQ-068-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-068-T02.

**Evidence:**

```
[PASS] REQ-068-T01: advanced OAuth flows and live secrets-rotation infrastructure: no prohibited pattern matched across 16 scanned files
[FAIL] REQ-068-T02: the documented approach to OAuth and secrets rotation across implementation tree (51 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /oauth|secret[_\- ]?rotation|rotate|key rotation/ in 51 files under implementation tree
```

### REQ-069 - PASS (100/100)

**Class:** ENGAGEMENT  |  **Category:** governance  |  **Source:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 1

**Requirement:**

~~~text
This is the checklist your submission is scored against.
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-069-T01  
**Reason:** All 1 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-069-T01: All 25 checklist artifacts are referenced by the 320 registered test cases, so this suite scores the stated checklist.
```

### REQ-070 - FAIL (40/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 2

**Requirement:**

~~~text
Each artifact must be present at (or near) the path shown and contain what is listed.
~~~

**Status:** FAIL  
**Fit Score:** 40  
**Tests:** REQ-070-T01, REQ-070-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-070-T01.

**Evidence:**

```
[FAIL] REQ-070-T01: every artifact named by the checklist is present at (or near) its path (ALL: 2/24 satisfied)
[NOT FOUND] src/graph.py -> absent
[NOT FOUND] logs/mcp_transcript.jsonl -> absent
[NOT FOUND] tests/test_memory_persistence.py -> absent
[NOT FOUND] logs/memory_test.log -> absent
[NOT FOUND] src/tools/rag_tool.py -> absent
[NOT FOUND] src/observability/tracing.py -> absent
[NOT FOUND] logs/tool_calls.jsonl -> absent
[NOT FOUND] docs/failure-analysis.md -> absent
[NOT FOUND] reports/golden_signals.json -> absent
[NOT FOUND] reports/dashboard.png -> absent
[NOT FOUND] reports/dashboard_data.csv -> absent
[NOT FOUND] logs/agent_actions.jsonl -> absent
[NOT FOUND] .env.example -> absent
[OK] .gitignore -> synthetic_data/.gitignore (near match)
[NOT FOUND] docs/risk-register.md -> absent
[NOT FOUND] docs/model-card.md -> absent
[NOT FOUND] docs/compliance.md -> absent
[NOT FOUND] docs/output-risk.md -> absent
[NOT FOUND] reports/eval_report.json -> absent
[NOT FOUND] tests/test_routing.py -> absent
[NOT FOUND] tests/test_loops.py -> absent
[NOT FOUND] tests/test_tool_contracts.py -> absent
[OK] README.md -> synthetic_data/README.md (near match)
[NOT FOUND] traces/phoenix_spans.parquet or traces/phoenix_spans.jsonl -> absent
[PASS] REQ-070-T02: content of 2 present checklist artifact(s) (ALL: 2/2 satisfied)
[OK] synthetic_data/.gitignore: 86 bytes of content
[OK] synthetic_data/README.md: 14865 bytes of content
```

### REQ-071 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 3

**Requirement:**

~~~text
Remember the Evidence-in-Repo and Citation-Resolves rules: outputs must be produced by committed code, and every citation must resolve to a committed artifact.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-071-T01, REQ-071-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-071-T01, REQ-071-T02.

**Evidence:**

```
[FAIL] REQ-071-T01: None of the machine-generated evidence artifacts named by the document exist, so no producing code can be evidenced.
[FAIL] REQ-071-T02: 153 unresolvable citation(s) across 51 document(s) (treated as missing per the Citation-Resolves Rule):
synthetic_data/DATA_DICTIONARY.md cites 'synthetic_data/generator/generate_synthetic_data.py' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'application_borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'applications.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'appraisals.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'asset_transactions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'assets.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'audit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrower_demographics.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'conditions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_accounts.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_profiles.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decision_reasons.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decisions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'document_extractions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'documents.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'eligibility_results.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'employment.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'fraud_checks.csv' -> present but uncommitted
```

### REQ-072 - FAIL (10/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 7.1 Agentic System — Foundation — table row "LangGraph graph"

**Requirement:**

~~~text
LangGraph graph | src/graph.py | Typed state; supervisor + ≥3 worker agents; conditional edges; checkpointer; structured output at node boundaries
~~~

**Status:** FAIL  
**Fit Score:** 10  
**Tests:** REQ-072-T01, REQ-072-T02, REQ-072-T03, REQ-072-T04, REQ-072-T05, REQ-072-T06  
**Reason:** 5 of 6 bound test(s) produced no satisfying evidence: REQ-072-T01, REQ-072-T03, REQ-072-T04, REQ-072-T05, REQ-072-T06.

**Evidence:**

```
[FAIL] REQ-072-T01: No file at or near 'src/graph.py' under E:\Virtusa Projects\CredPilot
[PASS] REQ-072-T02: typed graph state across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/build.py:73: @dataclass
[FAIL] REQ-072-T03: No graph module at or near 'src/graph.py' in which to count agents.
[FAIL] REQ-072-T04: conditional edges added to the graph (AST call analysis) (ALL: 0/1 satisfied)
[NOT FOUND] no call to 'add_conditional_edges' in 16 Python file(s)
[FAIL] REQ-072-T05: checkpointer (ALL: 0/2 satisfied)
[NOT FOUND] checkpointer referenced across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /checkpoint/ in 16 files under implementation tree
[NOT FOUND] a checkpointer implementation (ANY: 0/2 satisfied)
[NOT FOUND] SQLite checkpointer across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /SqliteSaver|AsyncSqliteSaver/ in 16 files under implementation tree
[NOT FOUND] checkpointer class across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /MemorySaver|BaseCheckpointSaver/ in 16 files under implementation tree
[FAIL] REQ-072-T06: structured output at node boundaries across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /with_structured_output|response_format|model_json_schema|return\s+\w*State/ in 16 files under implementation tree
```

### REQ-073 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 7.1 Agentic System — Foundation — table row "MCP server"

**Requirement:**

~~~text
MCP server | mcp_server/ + logs/mcp_transcript.jsonl | ≥2 tools + 1 resource; consumed via langchain-mcp-adapters; committed tool-call transcript
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-073-T01, REQ-073-T02, REQ-073-T03, REQ-073-T04  
**Reason:** 4 of 4 bound test(s) produced no satisfying evidence: REQ-073-T01, REQ-073-T02, REQ-073-T03, REQ-073-T04.

**Evidence:**

```
[FAIL] REQ-073-T01: No directory at or near 'mcp_server' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-073-T02: No MCP server package at or near 'mcp_server/'.
[FAIL] REQ-073-T03: consumed via langchain-mcp-adapters (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'langchain-mcp-adapters declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] langchain_mcp_adapters imported (import analysis) (ALL: 0/1 satisfied)
[NOT FOUND] module 'langchain_mcp_adapters' is never imported
[FAIL] REQ-073-T04: No MCP tool-call transcript at or near 'logs/mcp_transcript.jsonl'.
```

### REQ-074 - FAIL (33/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 7.1 Agentic System — Foundation — table row "Context engineering"

**Requirement:**

~~~text
Context engineering | src/context/ | write/select/compress/isolate; summarization middleware; quarantine of untrusted text
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-074-T01, REQ-074-T02, REQ-074-T03, REQ-074-T04  
**Reason:** 3 of 4 bound test(s) produced no satisfying evidence: REQ-074-T01, REQ-074-T02, REQ-074-T03.

**Evidence:**

```
[FAIL] REQ-074-T01: No directory at or near 'src/context' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-074-T02: Cannot check 'the four named context operations': no directory at or near 'src/context'
[FAIL] REQ-074-T03: Cannot check 'summarization middleware': no directory at or near 'src/context'
[PASS] REQ-074-T04: quarantine of untrusted text across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:449: "action_taken": "QUARANTINED_AND_ESCALATED",
```

### REQ-075 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** functional  |  **Source:** Section 7.1 Agentic System — Foundation — table row "Tiered memory"

**Requirement:**

~~~text
Tiered memory | src/memory/ + tests/test_memory_persistence.py + logs/memory_test.log | short + long/semantic memory; cross-session recall test with committed output log
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-075-T01, REQ-075-T02, REQ-075-T03, REQ-075-T04, REQ-075-T05  
**Reason:** 5 of 5 bound test(s) produced no satisfying evidence: REQ-075-T01, REQ-075-T02, REQ-075-T03, REQ-075-T04, REQ-075-T05.

**Evidence:**

```
[FAIL] REQ-075-T01: No directory at or near 'src/memory' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-075-T02: No file at or near 'tests/test_memory_persistence.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-075-T03: committed memory test output log (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'logs/memory_test.log' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'logs/memory_test.log' to check for commitment
[FAIL] REQ-075-T04: short + long/semantic memory (ALL: 0/2 satisfied)
[NOT FOUND] short-term memory tier across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /short[_\- ]?term|short_memory|working[_\- ]?memory/ in 16 files under implementation tree
[NOT FOUND] long/semantic memory tier across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /long[_\- ]?term|semantic[_\- ]?memory|episodic|vector/ in 16 files under implementation tree
[FAIL] REQ-075-T05: cross-session recall test: no test module at or near 'tests/test_memory_persistence.py'.
```

### REQ-076 - FAIL (40/100)

**Class:** IMPLEMENTATION  |  **Category:** policy  |  **Source:** Section 7.1 Agentic System — Foundation — table row "Agentic-RAG tool"

**Requirement:**

~~~text
Agentic-RAG tool | src/tools/rag_tool.py + data/policy_corpus/ | retrieval-in-the-loop over a synthetic lending-policy corpus
~~~

**Status:** FAIL  
**Fit Score:** 40  
**Tests:** REQ-076-T01, REQ-076-T02, REQ-076-T03, REQ-076-T04  
**Reason:** 2 of 4 bound test(s) produced no satisfying evidence: REQ-076-T01, REQ-076-T03.

**Evidence:**

```
[FAIL] REQ-076-T01: No file at or near 'src/tools/rag_tool.py' under E:\Virtusa Projects\CredPilot
[PASS] REQ-076-T02: Directory present: synthetic_data/policy_corpus (near match for 'data/policy_corpus'); 42 entries: POL-AST-001_assets-eligibility_v1.0.md, POL-AST-002_funds-to-close_v1.0.md, POL-AST-003_reserves_v1.0.md, POL-AST-003_reserves_v2.0.md, POL-AST-004_source-of-funds_v1.0.md, POL-CONV-001_conventional-purchase_v1.0.md, POL-CONV-002_conventional-rate-term-refinance_v1.0.md, POL-CONV-003_cash-out-refinance_v1.0.md, POL-CRD-001_credit-assessment_v1.0.md, POL-CRD-001_credit-assessment_v2.0.md, POL-CRD-002_credit-events_v1.0.md, POL-CRD-003_delinquency-treatment_v1.0.md...
[FAIL] REQ-076-T03: retrieval-in-the-loop (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'the RAG capability exposed as an agent tool': no directory at or near 'src/tools'
[NOT FOUND] Cannot check 'retrieval invoked by the tool': no directory at or near 'src/tools'
[PASS] REQ-076-T04: the corpus declared synthetic across implementation tree (1289 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/applicant_documents/APP-000001/01_loan_application_summary.txt:3: SYNTHETIC DOCUMENT - generated for CredPilot testing. Not a real record.
```

### REQ-077 - FAIL (33/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Phoenix instrumentation"

**Requirement:**

~~~text
Phoenix instrumentation | src/observability/tracing.py | Phoenix/openinference tracer wired into the run path (called, not just imported)
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-077-T01, REQ-077-T02, REQ-077-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-077-T01, REQ-077-T02.

**Evidence:**

```
[FAIL] REQ-077-T01: No file at or near 'src/observability/tracing.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-077-T02: the tracer actually invoked (AST call analysis) (ANY: 0/5 satisfied)
[NOT FOUND] no call to 'register' in 16 Python file(s)
[NOT FOUND] no call to 'instrument' in 16 Python file(s)
[NOT FOUND] no call to 'LangChainInstrumentor' in 16 Python file(s)
[NOT FOUND] no call to 'launch_app' in 16 Python file(s)
[NOT FOUND] no call to 'tracer_provider' in 16 Python file(s)
[PASS] REQ-077-T03: the run path referencing the tracing module across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/synth/policy_defs_c.py:1180: "The security instrument must hold first-lien position, with an "
```

### REQ-078 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Trace export"

**Requirement:**

~~~text
Trace export | traces/phoenix_spans.parquet (or .jsonl) | ≥1 full run; spans across multiple agents + every tool call; latencies present
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-078-T01, REQ-078-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-078-T01, REQ-078-T02.

**Evidence:**

```
[FAIL] REQ-078-T01: trace export artifact (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'traces/phoenix_spans.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-078-T02: No trace export at or near 'traces/phoenix_spans.parquet' or '.jsonl'.
```

### REQ-079 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Tool-invocation log"

**Requirement:**

~~~text
Tool-invocation log | logs/tool_calls.jsonl | machine-generated; per call: timestamp, agent/node, tool_name, args, result, latency_ms, status; names reconcile with code
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-079-T01, REQ-079-T02, REQ-079-T03, REQ-079-T04  
**Reason:** 4 of 4 bound test(s) produced no satisfying evidence: REQ-079-T01, REQ-079-T02, REQ-079-T03, REQ-079-T04.

**Evidence:**

```
[FAIL] REQ-079-T01: No file at or near 'logs/tool_calls.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-079-T02: No tool-invocation log at or near 'logs/tool_calls.jsonl'.
[FAIL] REQ-079-T03: machine-generated tool-invocation log (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'logs/tool_calls.jsonl'
[NOT FOUND] no committed Python source matches any producer pattern ['tool_calls\\.jsonl'] - the artifact cannot be shown to be machine-generated
[FAIL] REQ-079-T04: Cannot reconcile tool names: no log at or near 'logs/tool_calls.jsonl'
```

### REQ-080 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.2 Observability & Tracing (Arize Phoenix — mandated) — table row "Failure-mode analysis"

**Requirement:**

~~~text
Failure-mode analysis | docs/failure-analysis.md | ≥3 real failures, EACH citing Phoenix run_id + span_id (or tool-log record) + root cause + fix
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-080-T01, REQ-080-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-080-T01, REQ-080-T02.

**Evidence:**

```
[FAIL] REQ-080-T01: No file at or near 'docs/failure-analysis.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-080-T02: No failure-mode analysis at or near 'docs/failure-analysis.md'.
```

### REQ-081 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.3 Performance & Cost Governance — table row "Golden-signals report"

**Requirement:**

~~~text
Golden-signals report | reports/golden_signals.json + producing script | Phoenix-derived latency (thinking/acting/tool), tokens in/out, cost estimate; accuracy + hallucination rate from the eval
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-081-T01, REQ-081-T02, REQ-081-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-081-T01, REQ-081-T02, REQ-081-T03.

**Evidence:**

```
[FAIL] REQ-081-T01: No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-081-T02: the report's producing script (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'reports/golden_signals.json'
[NOT FOUND] no committed Python source matches any producer pattern ['golden_signals\\.json'] - the artifact cannot be shown to be machine-generated
[FAIL] REQ-081-T03: No golden-signals report at or near 'reports/golden_signals.json'.
```

### REQ-082 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 7.3 Performance & Cost Governance — table row "Cost/latency dashboard"

**Requirement:**

~~~text
Cost/latency dashboard | reports/dashboard.png + reports/dashboard_data.csv | Phoenix latency/cost/token dashboard screenshot AND the underlying data file it was drawn from
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-082-T01, REQ-082-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-082-T01, REQ-082-T02.

**Evidence:**

```
[FAIL] REQ-082-T01: cost/latency dashboard screenshot AND its underlying data file (ALL: 0/2 satisfied)
[NOT FOUND] no dashboard screenshot at or near 'reports/dashboard.png'
[NOT FOUND] no underlying data file at or near 'reports/dashboard_data.csv'
[FAIL] REQ-082-T02: the dashboard data export (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'reports/dashboard_data.csv'
[NOT FOUND] no committed Python source matches any producer pattern ['dashboard_data\\.csv', 'to_csv\\('] - the artifact cannot be shown to be machine-generated
```

### REQ-083 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 7.4 Security & Guardrails — table row "Guardrail code"

**Requirement:**

~~~text
Guardrail code | src/guardrails/ | input/output guardrails wired into the agent's I/O path (blocks/sanitizes)
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-083-T01, REQ-083-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-083-T01, REQ-083-T02.

**Evidence:**

```
[FAIL] REQ-083-T01: No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-083-T02: input/output guardrails wired into the I/O path (ALL: 1/5 satisfied)
[NOT FOUND] no guardrail package at or near 'src/guardrails/'
[NOT FOUND] input guardrail: no match for /input[_\- ]?guard|validate_input|check_input|on_input/ in the guardrail package
[NOT FOUND] output guardrail: no match for /output[_\- ]?guard|validate_output|check_output|on_output/ in the guardrail package
[NOT FOUND] blocks or sanitizes: no match for /\bblock|\brefus|saniti[sz]e|redact|\braise\b/ in the guardrail package
[OK] wired into the I/O path: synthetic_data/generator/generate_synthetic_data.py references the guardrail layer
```

### REQ-084 - FAIL (20/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 7.4 Security & Guardrails — table row "Audit trail"

**Requirement:**

~~~text
Audit trail | logs/agent_actions.jsonl + audit middleware | machine-generated: actor, action, tool, decision, timestamp for consequential actions
~~~

**Status:** FAIL  
**Fit Score:** 20  
**Tests:** REQ-084-T01, REQ-084-T02, REQ-084-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-084-T01, REQ-084-T02.

**Evidence:**

```
[FAIL] REQ-084-T01: No file at or near 'logs/agent_actions.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-084-T02: No audit trail at or near 'logs/agent_actions.jsonl'.
[PASS] REQ-084-T03: audit middleware invoked on agent actions across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:169: "audit_events", "scenario_assignments",
```

### REQ-085 - FAIL (60/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 7.4 Security & Guardrails — table row "Secrets hygiene"

**Requirement:**

~~~text
Secrets hygiene | .env.example, .gitignore | env-var config; .gitignore covers .env; no secrets committed anywhere
~~~

**Status:** FAIL  
**Fit Score:** 60  
**Tests:** REQ-085-T01, REQ-085-T02  
**Reason:** 1 of 2 bound test(s) produced no satisfying evidence: REQ-085-T01.

**Evidence:**

```
[FAIL] REQ-085-T01: secrets hygiene (ALL: 1/3 satisfied)
[NOT FOUND] synthetic_data/.gitignore has no rule covering .env
[NOT FOUND] no .env.example committed as the env-var config template
[OK] no .env file is committed
[PASS] REQ-085-T02: No committed secret matched 6 credential patterns across 1293 scanned files.
```

### REQ-086 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** risk  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Risk register"

**Requirement:**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-086-T01, REQ-086-T02, REQ-086-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-086-T01, REQ-086-T02, REQ-086-T03.

**Evidence:**

```
[FAIL] REQ-086-T01: No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-086-T02: risk register columns: no document at or near 'docs/risk-register.md'.
[FAIL] REQ-086-T03: 153 unresolvable citation(s) across 51 document(s) (treated as missing per the Citation-Resolves Rule):
synthetic_data/DATA_DICTIONARY.md cites 'synthetic_data/generator/generate_synthetic_data.py' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'application_borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'applications.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'appraisals.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'asset_transactions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'assets.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'audit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrower_demographics.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'conditions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_accounts.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_profiles.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decision_reasons.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decisions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'document_extractions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'documents.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'eligibility_results.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'employment.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'fraud_checks.csv' -> present but uncommitted
```

### REQ-087 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Model / system card"

**Requirement:**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-087-T01, REQ-087-T02, REQ-087-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-087-T01, REQ-087-T02, REQ-087-T03.

**Evidence:**

```
[FAIL] REQ-087-T01: No file at or near 'docs/model-card.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-087-T02: model card contents: no document at or near 'docs/model-card.md'.
[FAIL] REQ-087-T03: Cannot check 'citation of failure-analysis.md': no file at or near 'docs/model-card.md'
```

### REQ-088 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Compliance mapping"

**Requirement:**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-088-T01, REQ-088-T02, REQ-088-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-088-T01, REQ-088-T02, REQ-088-T03.

**Evidence:**

```
[FAIL] REQ-088-T01: No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-088-T02: compliance frameworks: no document at or near 'docs/compliance.md'.
[FAIL] REQ-088-T03: obligation -> how addressed -> evidence artifact (ALL: 0/2 satisfied)
[NOT FOUND] compliance mapping columns: no document at or near 'docs/compliance.md'.
[NOT FOUND] 153 unresolvable citation(s) across 51 document(s) (treated as missing per the Citation-Resolves Rule):
synthetic_data/DATA_DICTIONARY.md cites 'synthetic_data/generator/generate_synthetic_data.py' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'application_borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'applications.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'appraisals.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'asset_transactions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'assets.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'audit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrower_demographics.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'conditions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_accounts.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_profiles.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decision_reasons.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decisions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'document_extractions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'documents.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'eligibility_results.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'employment.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'fraud_checks.csv' -> present but uncommitted
```

### REQ-089 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** risk  |  **Source:** Section 7.5 Governance & Compliance (citation-gated) — table row "Output-risk classification"

**Requirement:**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-089-T01, REQ-089-T02, REQ-089-T03, REQ-089-T04  
**Reason:** 4 of 4 bound test(s) produced no satisfying evidence: REQ-089-T01, REQ-089-T02, REQ-089-T03, REQ-089-T04.

**Evidence:**

```
[FAIL] REQ-089-T01: No file at or near 'docs/output-risk.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-089-T02: output-risk tiers: no document at or near 'docs/output-risk.md'.
[FAIL] REQ-089-T03: high-risk gating: no document at or near 'docs/output-risk.md'.
[FAIL] REQ-089-T04: output-risk sample: no document at or near 'docs/output-risk.md'.
```

### REQ-090 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Evaluation report"

**Requirement:**

~~~text
Evaluation report | reports/eval_report.json + harness | DeepEval (or equiv) over a golden set: hallucination + faithfulness/relevance; LLM-as-judge
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-090-T01, REQ-090-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-090-T01, REQ-090-T02.

**Evidence:**

```
[FAIL] REQ-090-T01: No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-090-T02: No evaluation report at or near 'reports/eval_report.json'.
```

### REQ-091 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Routing-logic test"

**Requirement:**

~~~text
Routing-logic test | tests/test_routing.py | asserts conditional edges route the right worker for given states
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-091-T01, REQ-091-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-091-T01, REQ-091-T02.

**Evidence:**

```
[FAIL] REQ-091-T01: No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-091-T02: routing-logic assertions: no test module at or near 'tests/test_routing.py'.
```

### REQ-092 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** orchestration  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Loop/cascade guard"

**Requirement:**

~~~text
Loop/cascade guard | tests/test_loops.py | asserts a max-steps / recursion-limit stops runaway loops
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-092-T01, REQ-092-T02, REQ-092-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-092-T01, REQ-092-T02, REQ-092-T03.

**Evidence:**

```
[FAIL] REQ-092-T01: No file at or near 'tests/test_loops.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-092-T02: loop/cascade guard assertions: no test module at or near 'tests/test_loops.py'.
[FAIL] REQ-092-T03: a configured step or recursion limit across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /recursion_limit|max_steps|max_iterations/ in 16 files under implementation tree
```

### REQ-093 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** integration  |  **Source:** Section 7.6 Agent Evaluation & Testing (lean, agent-specific) — table row "Tool-contract test"

**Requirement:**

~~~text
Tool-contract test | tests/test_tool_contracts.py | asserts each tool's input/output schema + one error path
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-093-T01, REQ-093-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-093-T01, REQ-093-T02.

**Evidence:**

```
[FAIL] REQ-093-T01: No file at or near 'tests/test_tool_contracts.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-093-T02: tool-contract assertions: no test module at or near 'tests/test_tool_contracts.py'.
```

### REQ-094 - FAIL (33/100)

**Class:** IMPLEMENTATION  |  **Category:** non_functional  |  **Source:** Section 7.7 Engineering & Delivery — table row "Local-run runbook"

**Requirement:**

~~~text
Local-run runbook | README.md | single-command run; how to regenerate traces (Phoenix) and the eval; committed sample inputs
~~~

**Status:** FAIL  
**Fit Score:** 33  
**Tests:** REQ-094-T01, REQ-094-T02, REQ-094-T03, REQ-094-T04  
**Reason:** 2 of 4 bound test(s) produced no satisfying evidence: REQ-094-T02, REQ-094-T03.

**Evidence:**

```
[PASS] REQ-094-T01: File present: synthetic_data/README.md (near match for 'README.md'); size=14865 bytes
[FAIL] REQ-094-T02: single documented command plus a regeneration command (ALL: 1/3 satisfied)
[OK] single documented run command: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[NOT FOUND] no documented trace-regeneration command: synthetic_data/README.md documents no command mentioning ('trace', 'phoenix', 'span', 'observability')
[NOT FOUND] no documented evaluation command: synthetic_data/README.md documents no command mentioning ('eval', 'deepeval', 'golden', 'judge')
[FAIL] REQ-094-T03: runbook sample inputs: no sample input files found under any of data, samples, sample_inputs, inputs, fixtures, examples, data/samples, data/applications, tests/data
[PASS] REQ-094-T04: required CLI interface (ALL: 2/2 satisfied)
[OK] CLI parser defined in synthetic_data/generator/generate_synthetic_data.py
[OK] CLI invocation documented: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
```

### REQ-095 - PASS (100/100)

**Class:** OPTIONAL  |  **Category:** functional  |  **Source:** Section 7.7 Engineering & Delivery — table row "Bonus"

**Requirement:**

~~~text
Bonus | src/api/ (FastAPI streaming) | OPTIONAL: async FastAPI streaming endpoint — extra credit, not required
~~~

**Status:** PASS  
**Fit Score:** 100  
**Tests:** REQ-095-T01, REQ-095-T02  
**Reason:** All 2 bound test(s) passed with committed evidence.

**Evidence:**

```
[PASS] REQ-095-T01: FastAPI streaming endpoint (OPTIONAL, not required): not present at or near 'src/api'. The source text marks this surface optional / bonus and explicitly not required, so its absence satisfies the interface requirement.
[PASS] REQ-095-T02: async FastAPI streaming endpoint, or the surface is absent (ANY: 1/2 satisfied)
[NOT FOUND] async FastAPI streaming endpoint (ALL: 0/3 satisfied)
[NOT FOUND] No directory at or near 'src/api' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'fastapi declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Cannot check 'async streaming endpoint': no directory at or near 'src/api'
[OK] FastAPI streaming endpoint (OPTIONAL, not required): not present at or near 'src/api'. The source text marks this surface optional / bonus and explicitly not required, so its absence satisfies the interface requirement.
```

### REQ-096 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 1

**Requirement:**

~~~text
Every evidence artifact must be produced by committed code and committed in the format shown below.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-096-T01, REQ-096-T02, REQ-096-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-096-T01, REQ-096-T02, REQ-096-T03.

**Evidence:**

```
[FAIL] REQ-096-T01: None of the machine-generated evidence artifacts named by the document exist, so no producing code can be evidenced.
[FAIL] REQ-096-T02: 2 artifact(s) exist on disk but are not listed by 'git ls-files': synthetic_data/.gitignore, synthetic_data/README.md. Committed: 0.
[FAIL] REQ-096-T03: artifacts in their stated formats (ALL: 0/8 satisfied)
[NOT FOUND] Phoenix trace export as Parquet or JSONL of OTel spans (ANY: 0/2 satisfied)
[NOT FOUND] No artifact at or near 'traces/phoenix_spans.parquet'
[NOT FOUND] No JSONL artifact at or near 'traces/phoenix_spans.jsonl'
[NOT FOUND] No JSONL artifact at or near 'logs/tool_calls.jsonl'
[NOT FOUND] No file at or near 'docs/failure-analysis.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'golden-signals report as JSON': no file at or near 'reports/golden_signals.json'
[NOT FOUND] No artifact at or near 'reports/dashboard.png'
[NOT FOUND] No CSV artifact at or near 'reports/dashboard_data.csv'
[NOT FOUND] No JSONL artifact at or near 'logs/agent_actions.jsonl'
[NOT FOUND] Cannot check 'evaluation report as JSON': no file at or near 'reports/eval_report.json'
```

### REQ-097 - FAIL (20/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 2

**Requirement:**

~~~text
This tells you the exact format and the tool / method to generate each one, so “observability” or “cost governance” becomes a concrete file you generate — not a slide.
~~~

**Status:** FAIL  
**Fit Score:** 20  
**Tests:** REQ-097-T01, REQ-097-T02, REQ-097-T03  
**Reason:** 2 of 3 bound test(s) produced no satisfying evidence: REQ-097-T01, REQ-097-T02.

**Evidence:**

```
[FAIL] REQ-097-T01: observability as generated files (ALL: 0/2 satisfied)
[NOT FOUND] a trace export (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'traces/phoenix_spans.jsonl' under E:\Virtusa Projects\CredPilot
[NOT FOUND] generated tool-invocation log (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'logs/tool_calls.jsonl'
[NOT FOUND] no committed Python source matches any producer pattern ['tool_calls\\.jsonl'] - the artifact cannot be shown to be machine-generated
[FAIL] REQ-097-T02: cost governance as generated files (ALL: 0/2 satisfied)
[NOT FOUND] generated golden-signals report (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'reports/golden_signals.json'
[NOT FOUND] no committed Python source matches any producer pattern ['golden_signals\\.json'] - the artifact cannot be shown to be machine-generated
[NOT FOUND] generated dashboard data (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'reports/dashboard_data.csv'
[NOT FOUND] no committed Python source matches any producer pattern ['dashboard_data\\.csv', 'to_csv\\('] - the artifact cannot be shown to be machine-generated
[PASS] REQ-097-T03: slide decks substituted for generated evidence: no file matches ['*.pptx', '*.ppt', '*.key', '*.odp'] across 1328 files
```

### REQ-098 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — Format & Where to Obtain — lead-in paragraph, sentence 3

**Requirement:**

~~~text
Enable Arize Phoenix locally (`pip install arize-phoenix openinference-instrumentation-langchain`; the UI runs at localhost:6006) — it is the single source your traces, latency, token and cost evidence come from.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-098-T01, REQ-098-T02, REQ-098-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-098-T01, REQ-098-T02, REQ-098-T03.

**Evidence:**

```
[FAIL] REQ-098-T01: arize-phoenix and openinference-instrumentation-langchain (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'arize-phoenix declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Cannot check 'openinference-instrumentation-langchain declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[FAIL] REQ-098-T02: the local Phoenix UI endpoint across implementation tree (67 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /localhost:6006|127\.0\.0\.1:6006|:6006/ in 67 files under implementation tree
[FAIL] REQ-098-T03: Phoenix as the single evidence source (ALL: 0/2 satisfied)
[NOT FOUND] golden signals derived from Phoenix spans (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'reports/golden_signals.json'
[NOT FOUND] no committed Python source matches any producer pattern ['get_spans_dataframe'] - the artifact cannot be shown to be machine-generated
[NOT FOUND] dashboard data derived from Phoenix spans (ALL: 0/2 satisfied)
[NOT FOUND] artifact absent: no file at or near 'reports/dashboard_data.csv'
[NOT FOUND] no committed Python source matches any producer pattern ['get_spans_dataframe'] - the artifact cannot be shown to be machine-generated
```

### REQ-099 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Phoenix trace export"

**Requirement:**

~~~text
Phoenix trace export | Parquet or JSONL of OTel spans | Turn on Phoenix tracing (openinference-instrumentation-langchain), run one full conversation, then export: px.Client().get_spans_dataframe().to_parquet('traces/phoenix_spans.parquet').
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-099-T01, REQ-099-T02, REQ-099-T03, REQ-099-T04  
**Reason:** 4 of 4 bound test(s) produced no satisfying evidence: REQ-099-T01, REQ-099-T02, REQ-099-T03, REQ-099-T04.

**Evidence:**

```
[FAIL] REQ-099-T01: Parquet or JSONL of OTel spans (ANY: 0/2 satisfied)
[NOT FOUND] No artifact at or near 'traces/phoenix_spans.parquet'
[NOT FOUND] No JSONL artifact at or near 'traces/phoenix_spans.jsonl'
[FAIL] REQ-099-T02: openinference-instrumentation-langchain tracing (ALL: 0/2 satisfied)
[NOT FOUND] Cannot check 'openinference-instrumentation-langchain declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] openinference instrumentation activated across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /openinference/ in 16 files under implementation tree
[FAIL] REQ-099-T03: the stated export method (ALL: 0/2 satisfied)
[NOT FOUND] px.Client().get_spans_dataframe() across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /get_spans_dataframe/ in 16 files under implementation tree
[NOT FOUND] the span dataframe exported to file across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /to_parquet|to_json/ in 16 files under implementation tree
[FAIL] REQ-099-T04: No trace export at or near 'traces/phoenix_spans.parquet' or '.jsonl'.
```

### REQ-100 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Tool-invocation log"

**Requirement:**

~~~text
Tool-invocation log | JSONL — one object per tool call | A logging wrapper/decorator on every tool that appends {timestamp, agent, tool_name, args, result, latency_ms, status} to logs/tool_calls.jsonl.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-100-T01, REQ-100-T02, REQ-100-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-100-T01, REQ-100-T02, REQ-100-T03.

**Evidence:**

```
[FAIL] REQ-100-T01: No JSONL artifact at or near 'logs/tool_calls.jsonl'
[FAIL] REQ-100-T02: No tool-invocation log at or near 'logs/tool_calls.jsonl'.
[FAIL] REQ-100-T03: a logging wrapper/decorator (ALL: 1/2 satisfied)
[OK] a logging wrapper or decorator across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:678: def scenario_catalog(state: dict[str, Any]) -> list[dict[str, Any]]:
[NOT FOUND] appending to logs/tool_calls.jsonl across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /tool_calls\.jsonl/ in 16 files under implementation tree
```

### REQ-101 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Failure-mode analysis"

**Requirement:**

~~~text
Failure-mode analysis | Markdown | Open your Phoenix traces, pick ≥ 3 real failures, write each up citing its run_id + span_id, with root cause and the fix.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-101-T01, REQ-101-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-101-T01, REQ-101-T02.

**Evidence:**

```
[FAIL] REQ-101-T01: Markdown failure-mode analysis (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'docs/failure-analysis.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/failure-analysis.md' to check for commitment
[FAIL] REQ-101-T02: No failure-mode analysis at or near 'docs/failure-analysis.md'.
```

### REQ-102 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Golden-signals report"

**Requirement:**

~~~text
Golden-signals report | JSON | A script reads the Phoenix spans (get_spans_dataframe()): p50/p95 latency by span type (thinking / acting / tool), token totals from LLM spans, cost = tokens × price; import accuracy + hallucination from the eval report; write reports/golden_signals.json.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-102-T01, REQ-102-T02, REQ-102-T03, REQ-102-T04  
**Reason:** 4 of 4 bound test(s) produced no satisfying evidence: REQ-102-T01, REQ-102-T02, REQ-102-T03, REQ-102-T04.

**Evidence:**

```
[FAIL] REQ-102-T01: Cannot check 'valid JSON report': no file at or near 'reports/golden_signals.json'
[FAIL] REQ-102-T02: No golden-signals report at or near 'reports/golden_signals.json'.
[FAIL] REQ-102-T03: No golden-signals report at or near 'reports/golden_signals.json'.
[FAIL] REQ-102-T04: accuracy and hallucination imported from the eval report (ALL: 0/2 satisfied)
[NOT FOUND] No golden-signals report at or near 'reports/golden_signals.json'.
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
```

### REQ-103 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** observability  |  **Source:** Section 8. Producing the Evidence — table row "Cost/latency dashboard"

**Requirement:**

~~~text
Cost/latency dashboard | PNG + CSV | Phoenix UI (localhost:6006) shows latency / cost / token dashboards — screenshot one; export the data with get_spans_dataframe().to_csv('reports/dashboard_data.csv').
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-103-T01, REQ-103-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-103-T01, REQ-103-T02.

**Evidence:**

```
[FAIL] REQ-103-T01: cost/latency dashboard screenshot AND its underlying data file (ALL: 0/2 satisfied)
[NOT FOUND] no dashboard screenshot at or near 'reports/dashboard.png'
[NOT FOUND] no underlying data file at or near 'reports/dashboard_data.csv'
[FAIL] REQ-103-T02: the stated CSV export method (ALL: 0/3 satisfied)
[NOT FOUND] the Phoenix spans dataframe across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /get_spans_dataframe/ in 16 files under implementation tree
[NOT FOUND] the to_csv export across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /to_csv\(/ in 16 files under implementation tree
[NOT FOUND] the dashboard data target path across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /dashboard_data\.csv/ in 16 files under implementation tree
```

### REQ-104 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** security  |  **Source:** Section 8. Producing the Evidence — table row "Guardrail code"

**Requirement:**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-104-T01, REQ-104-T02, REQ-104-T03  
**Reason:** 3 of 3 bound test(s) produced no satisfying evidence: REQ-104-T01, REQ-104-T02, REQ-104-T03.

**Evidence:**

```
[FAIL] REQ-104-T01: guardrail Python module (ALL: 0/2 satisfied)
[NOT FOUND] No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'Python definitions in the guardrail module': no directory at or near 'src/guardrails'
[FAIL] REQ-104-T02: validators or policy functions wrapping input and output (ALL: 0/2 satisfied)
[NOT FOUND] Guardrails-AI, LLM Guard, or policy functions (ANY: 0/3 satisfied)
[NOT FOUND] Cannot check 'guardrails-ai declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Cannot check 'llm-guard declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Cannot check 'policy/validator functions': no directory at or near 'src/guardrails'
[NOT FOUND] input/output guardrails wired into the I/O path (ALL: 1/5 satisfied)
[NOT FOUND] no guardrail package at or near 'src/guardrails/'
[NOT FOUND] input guardrail: no match for /input[_\- ]?guard|validate_input|check_input|on_input/ in the guardrail package
[NOT FOUND] output guardrail: no match for /output[_\- ]?guard|validate_output|check_output|on_output/ in the guardrail package
[NOT FOUND] blocks or sanitizes: no match for /\bblock|\brefus|saniti[sz]e|redact|\braise\b/ in the guardrail package
[OK] wired into the I/O path: synthetic_data/generator/generate_synthetic_data.py references the guardrail layer
[FAIL] REQ-104-T03: wired into the graph's I/O nodes (ALL: 1/2 satisfied)
[NOT FOUND] input/output guardrails wired into the I/O path (ALL: 1/5 satisfied)
[NOT FOUND] no guardrail package at or near 'src/guardrails/'
[NOT FOUND] input guardrail: no match for /input[_\- ]?guard|validate_input|check_input|on_input/ in the guardrail package
[NOT FOUND] output guardrail: no match for /output[_\- ]?guard|validate_output|check_output|on_output/ in the guardrail package
[NOT FOUND] blocks or sanitizes: no match for /\bblock|\brefus|saniti[sz]e|redact|\braise\b/ in the guardrail package
[OK] wired into the I/O path: synthetic_data/generator/generate_synthetic_data.py references the guardrail layer
[OK] the graph referencing the guardrail layer across implementation tree (16 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/generator/generate_synthetic_data.py:649: ("AUTOMATED_COMPONENT", "quarantine_untrusted_text", "guardrail",
```

### REQ-105 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** auditability  |  **Source:** Section 8. Producing the Evidence — table row "Audit trail"

**Requirement:**

~~~text
Audit trail | JSONL | Audit middleware that appends {actor, action, tool, decision, timestamp} for each consequential action to logs/agent_actions.jsonl.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-105-T01, REQ-105-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-105-T01, REQ-105-T02.

**Evidence:**

```
[FAIL] REQ-105-T01: No JSONL artifact at or near 'logs/agent_actions.jsonl'
[FAIL] REQ-105-T02: No audit trail at or near 'logs/agent_actions.jsonl'.
```

### REQ-106 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 8. Producing the Evidence — table row "Governance pack" (continuation table)

**Requirement:**

~~~text
Governance pack | Markdown | risk-register.md, model-card.md, compliance.md, output-risk.md — each entry cites the committed control/artifact it refers to.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-106-T01, REQ-106-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-106-T01, REQ-106-T02.

**Evidence:**

```
[FAIL] REQ-106-T01: the four governance Markdown documents (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/model-card.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/output-risk.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-106-T02: 153 unresolvable citation(s) across 51 document(s) (treated as missing per the Citation-Resolves Rule):
synthetic_data/DATA_DICTIONARY.md cites 'synthetic_data/generator/generate_synthetic_data.py' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'application_borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'applications.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'appraisals.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'asset_transactions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'assets.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'audit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrower_demographics.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'borrowers.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'conditions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_accounts.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_events.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'credit_profiles.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decision_reasons.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'decisions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'document_extractions.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'documents.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'eligibility_results.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'employment.csv' -> present but uncommitted
synthetic_data/DATA_DICTIONARY.md cites 'fraud_checks.csv' -> present but uncommitted
```

### REQ-107 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 8. Producing the Evidence — table row "Evaluation report" (continuation table)

**Requirement:**

~~~text
Evaluation report | JSON | A DeepEval run over your golden set (hallucination, faithfulness, answer-relevance) that writes reports/eval_report.json, plus the harness.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-107-T01, REQ-107-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-107-T01, REQ-107-T02.

**Evidence:**

```
[FAIL] REQ-107-T01: Cannot check 'valid JSON evaluation report': no file at or near 'reports/eval_report.json'
[FAIL] REQ-107-T02: No evaluation report at or near 'reports/eval_report.json'.
```

### REQ-108 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** evaluation  |  **Source:** Section 8. Producing the Evidence — table row "Agent tests" (continuation table)

**Requirement:**

~~~text
Agent tests | pytest files | tests/test_routing.py (routing), tests/test_loops.py (recursion/step limit), tests/test_tool_contracts.py (I/O schema + error path).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-108-T01, REQ-108-T02, REQ-108-T03, REQ-108-T04  
**Reason:** 4 of 4 bound test(s) produced no satisfying evidence: REQ-108-T01, REQ-108-T02, REQ-108-T03, REQ-108-T04.

**Evidence:**

```
[FAIL] REQ-108-T01: the three pytest files (ALL: 0/3 satisfied)
[NOT FOUND] No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_loops.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_tool_contracts.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-108-T02: routing test: no test module at or near 'tests/test_routing.py'.
[FAIL] REQ-108-T03: loops test: no test module at or near 'tests/test_loops.py'.
[FAIL] REQ-108-T04: tool-contract test: no test module at or near 'tests/test_tool_contracts.py'.
```

### REQ-109 - FAIL (0/100)

**Class:** OPTIONAL  |  **Category:** functional  |  **Source:** Section 8.1 Good-to-Have — bullet 1

**Requirement:**

~~~text
FastAPI streaming endpoint; a demonstrated local run (screenshot/log).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-109-T01, REQ-109-T02  
**Reason:** 2 of 2 bound test(s) produced no satisfying evidence: REQ-109-T01, REQ-109-T02.

**Evidence:**

```
[FAIL] REQ-109-T01: FastAPI streaming endpoint (ALL: 0/3 satisfied)
[NOT FOUND] No directory at or near 'src/api' under E:\Virtusa Projects\CredPilot
[NOT FOUND] Cannot check 'fastapi declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Cannot check 'an async streaming endpoint': no directory at or near 'src/api'
[FAIL] REQ-109-T02: a demonstrated local run (ANY: 0/2 satisfied)
[NOT FOUND] a committed run log of the streaming endpoint across implementation tree (1191 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /uvicorn|fastapi|/stream|127\.0\.0\.1:8000|localhost:8000/ in 1191 files under implementation tree
[NOT FOUND] No file at or near 'docs/api-run.png' under E:\Virtusa Projects\CredPilot
```

### REQ-110 - FAIL (67/100)

**Class:** OPTIONAL  |  **Category:** security  |  **Source:** Section 8.1 Good-to-Have — bullet 2

**Requirement:**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

**Status:** FAIL  
**Fit Score:** 67  
**Tests:** REQ-110-T01, REQ-110-T02, REQ-110-T03  
**Reason:** 1 of 3 bound test(s) produced no satisfying evidence: REQ-110-T01.

**Evidence:**

```
[FAIL] REQ-110-T01: Presidio PII-redaction middleware (ALL: 1/3 satisfied)
[NOT FOUND] Cannot check 'presidio declared': no dependency manifest found (looked for requirements.txt, requirements-dev.txt, pyproject.toml, setup.cfg, setup.py, Pipfile, environment.yml, constraints.txt)
[NOT FOUND] Presidio used in the redaction path across implementation tree (16 files) (ALL: 0/1 satisfied)
[NOT FOUND] no match for /presidio/ in 16 files under implementation tree
[OK] PII masking and leak-free logs (ALL: 2/2 satisfied)
[OK] masking implemented at synthetic_data/generator/synth/people.py:238: mask_ssn(
[OK] no plaintext sensitive identifier in 1178 scanned log/data artifact(s)
[PASS] REQ-110-T02: a before/after redaction sample across implementation tree (1273 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/policy_corpus/POL-SEC-001_privacy-and-ai-security_v1.0.md:133: | `check_timing` | before retrieval, not after |
[PASS] REQ-110-T03: red-team attack set and results (ALL: 2/2 satisfied)
[OK] a red-team attack set across implementation tree (187 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/DESIGN_ASSUMPTIONS.md:190: ## 6. Adversarial content
[OK] the attack results across implementation tree (171 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/DATA_DICTIONARY.md:139: | `outcome` | string | PASS | FAIL | REFER | NOT_APPLICABLE | INDETERMINATE. |
```

### REQ-111 - FAIL (0/100)

**Class:** OPTIONAL  |  **Category:** observability  |  **Source:** Section 8.1 Good-to-Have — bullet 3

**Requirement:**

~~~text
An optimization note showing a measured before/after latency or cost improvement (two Phoenix-derived reports).
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-111-T01  
**Reason:** 1 of 1 bound test(s) produced no satisfying evidence: REQ-111-T01.

**Evidence:**

```
[FAIL] REQ-111-T01: optimization note backed by two Phoenix-derived reports (ALL: 2/3 satisfied)
[OK] the optimization note across implementation tree (51 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/policy_corpus/POL-CRD-003_delinquency-treatment_v1.0.md:113: Where a file shows deteriorating recent behaviour against a clean older history, the recent behaviour governs the referral decision. Where it shows improving behaviour against an adverse older history, the improvement is recorded as a compensating factor available to POL-DTI-001. Neither direction i
[OK] the measured dimension across implementation tree (51 files) (ALL: 1/1 satisfied)
[OK] synthetic_data/DATA_DICTIONARY.md:117: | `liquidity_haircut` | decimal | Reduction applied for conversion cost or uncertainty. |
[NOT FOUND] only 0 Phoenix-derived report(s) found ([]); a measured before/after improvement needs two
```

### REQ-112 - FAIL (0/100)

**Class:** IMPLEMENTATION  |  **Category:** governance  |  **Source:** Section 8.1 Good-to-Have — closing italic paragraph (final paragraph of the document)

**Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Status:** FAIL  
**Fit Score:** 0  
**Tests:** REQ-112-T01, REQ-112-T02, REQ-112-T03, REQ-112-T04, REQ-112-T05, REQ-112-T06  
**Reason:** 6 of 6 bound test(s) produced no satisfying evidence: REQ-112-T01, REQ-112-T02, REQ-112-T03, REQ-112-T04, REQ-112-T05, REQ-112-T06.

**Evidence:**

```
[FAIL] REQ-112-T01: observable lending decision (ALL: 0/2 satisfied)
[NOT FOUND] a trace export (ANY: 0/2 satisfied)
[NOT FOUND] No file at or near 'traces/phoenix_spans.parquet' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'traces/phoenix_spans.jsonl' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'logs/tool_calls.jsonl' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-112-T02: cost governance (ALL: 0/2 satisfied)
[NOT FOUND] No file at or near 'reports/golden_signals.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'reports/dashboard_data.csv' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-112-T03: security (ALL: 1/3 satisfied)
[NOT FOUND] No directory at or near 'src/guardrails' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near '.env.example' under E:\Virtusa Projects\CredPilot
[OK] PII masking and leak-free logs (ALL: 2/2 satisfied)
[OK] masking implemented at synthetic_data/generator/synth/people.py:238: mask_ssn(
[OK] no plaintext sensitive identifier in 1178 scanned log/data artifact(s)
[FAIL] REQ-112-T04: compliance (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'docs/compliance.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/risk-register.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/model-card.md' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'docs/output-risk.md' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-112-T05: continuous evaluation (ALL: 0/4 satisfied)
[NOT FOUND] No file at or near 'reports/eval_report.json' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_routing.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_loops.py' under E:\Virtusa Projects\CredPilot
[NOT FOUND] No file at or near 'tests/test_tool_contracts.py' under E:\Virtusa Projects\CredPilot
[FAIL] REQ-112-T06: committed, regenerable evidence (ALL: 0/3 satisfied)
[NOT FOUND] 2 artifact(s) exist on disk but are not listed by 'git ls-files': synthetic_data/.gitignore, synthetic_data/README.md. Committed: 0.
[NOT FOUND] None of the machine-generated evidence artifacts named by the document exist, so no producing code can be evidenced.
[NOT FOUND] single documented command plus a regeneration command (ALL: 1/3 satisfied)
[OK] single documented run command: 'python synthetic_data/generator/generate_synthetic_data.py' (from synthetic_data/README.md (first documented command))
[NOT FOUND] no documented trace-regeneration command: synthetic_data/README.md documents no command mentioning ('trace', 'phoenix', 'span', 'observability')
[NOT FOUND] no documented evaluation command: synthetic_data/README.md documents no command mentioning ('eval', 'deepeval', 'golden', 'judge')
```

---

## How to read this report

* **PASS** means the implementation provided sufficient verifiable evidence that the original requirement is satisfied.
* **FAIL** means it did not. Partial implementation stays FAIL even where the fit score is high.
* **Fit Score** is the weighted percentage of that requirement's tests that passed: 100 = fully satisfied with evidence; 75-99 = substantial but one or more explicit parts incomplete; 50-74 = partially implemented; 1-49 = minimal; 0 = absent.
* `UNSPECIFIED_BY_REQUIREMENT` in an evidence line means the source document fixes no value to test against. That is a specification gap recorded honestly, not an implementation defect, and no threshold was invented to fill it.

Do not edit the expectations in this suite to turn a FAIL into a PASS. The requirements define the expected behaviour; the implementation does not.

