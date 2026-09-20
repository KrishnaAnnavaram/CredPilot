<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - governance

Generated: 2026-09-20T05:48:35Z

23 requirement(s), 61 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-001

**Source location:** Document title block — banner line above the title (first line of the document)  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Agentic AI Engineer Pathway — Capstone Hackathon
~~~

### REQ-001-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-001-T01 |
| **Requirement ID** | REQ-001 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agentic AI Engineer Pathway — Capstone Hackathon
~~~

**Purpose:** The delivered repository is identifiable as work on the pathway and capstone hackathon named in the document's banner line.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan every committed Markdown document in the implementation.
2. Require both halves of the banner line: the pathway and the capstone hackathon.

**Expected Result:** The banner line 'Agentic AI Engineer Pathway - Capstone Hackathon' is reflected in the repository documentation.

**Evidence Required:** File paths and line numbers for both matched fragments.

**Pass Condition:** Collected evidence satisfies: The banner line 'Agentic AI Engineer Pathway - Capstone Hackathon' is reflected in the repository documentation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The banner line 'Agentic AI Engineer Pathway - Capstone Hackathon' is reflected in the repository documentation.

---

## REQ-002

**Source location:** Document title block — document title  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Loan Origination & Underwriting Copilot
~~~

### REQ-002-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-002-T01 |
| **Requirement ID** | REQ-002 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Loan Origination & Underwriting Copilot
~~~

**Purpose:** The delivered repository carries the document's title.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan every committed Markdown document in the implementation.
2. Look for the document title exactly as printed.

**Expected Result:** The title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.

**Evidence Required:** File path and line number of the matched title.

**Pass Condition:** Collected evidence satisfies: The title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.

---

## REQ-003

**Source location:** Document title block — subtitle line beneath the title  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

### REQ-003-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T01 |
| **Requirement ID** | REQ-003 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The repository declares the business case ID and domain the subtitle states.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the repository for the business case ID.
2. Scan the repository documentation for the declared domain.

**Expected Result:** Both the business case ID and the domain from the subtitle are declared.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both the business case ID and the domain from the subtitle are declared.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both the business case ID and the domain from the subtitle are declared.

### REQ-003-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T02 |
| **Requirement ID** | REQ-003 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The Agentic Core area of the cross-cutting finale is delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the agent graph that constitutes the agentic core.
2. Confirm the agent framework is a declared dependency.

**Expected Result:** The Agentic Core is delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The Agentic Core is delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The Agentic Core is delivered.

### REQ-003-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T03 |
| **Requirement ID** | REQ-003 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The Context Engineering area of the cross-cutting finale is delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the context-engineering package.

**Expected Result:** Context Engineering is delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Context Engineering is delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Context Engineering is delivered.

### REQ-003-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T04 |
| **Requirement ID** | REQ-003 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The MCP area of the cross-cutting finale is delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the MCP server package.
2. Confirm the MCP SDK is a declared dependency.

**Expected Result:** MCP is delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: MCP is delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: MCP is delivered.

### REQ-003-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T05 |
| **Requirement ID** | REQ-003 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The Observability area of the cross-cutting finale is delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the tracing module.
2. Confirm the observability stack is declared.

**Expected Result:** Observability is delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Observability is delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Observability is delivered.

### REQ-003-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T06 |
| **Requirement ID** | REQ-003 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The Cost Governance area of the cross-cutting finale is delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the golden-signals report and the cost/latency data file.

**Expected Result:** Cost Governance is delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Cost Governance is delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Cost Governance is delivered.

### REQ-003-T07

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T07 |
| **Requirement ID** | REQ-003 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The Security & Governance area of the cross-cutting finale is delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrail package.
2. Locate the risk register and the compliance mapping.

**Expected Result:** Security & Governance is delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Security & Governance is delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Security & Governance is delivered.

### REQ-003-T08

| Field | Value |
| --- | --- |
| **Test ID** | REQ-003-T08 |
| **Requirement ID** | REQ-003 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case BC-AAIE-HACK-02 · Domain: Banking & Finance · Cross-cutting finale: Agentic Core + Context Engineering + MCP + Observability + Cost Governance + Security & Governance + Agent Evaluation
~~~

**Purpose:** The Agent Evaluation area of the cross-cutting finale is delivered.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the evaluation report.
2. Locate at least one committed agent test.

**Expected Result:** Agent Evaluation is delivered.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Agent Evaluation is delivered.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Agent Evaluation is delivered.

---

## REQ-004

**Source location:** Section 1. Project Identity — table row 1  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Business Case Title | Loan Origination & Underwriting Copilot
~~~

### REQ-004-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-004-T01 |
| **Requirement ID** | REQ-004 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case Title | Loan Origination & Underwriting Copilot
~~~

**Purpose:** The delivered repository identifies itself as the business case titled in the source document.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan every committed Markdown document in the implementation.
2. Look for the business case title exactly as the source document states it.

**Expected Result:** The business case title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.

**Evidence Required:** File path and line number of the matched title.

**Pass Condition:** Collected evidence satisfies: The business case title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The business case title 'Loan Origination & Underwriting Copilot' appears in the repository documentation.

---

## REQ-005

**Source location:** Section 1. Project Identity — table row 2  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Business Case ID | BC-AAIE-HACK-02
~~~

### REQ-005-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-005-T01 |
| **Requirement ID** | REQ-005 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Business Case ID | BC-AAIE-HACK-02
~~~

**Purpose:** The delivered repository is identifiable as business case BC-AAIE-HACK-02.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the repository's documentation and project metadata files.
2. Look for the literal business case ID.

**Expected Result:** The business case ID 'BC-AAIE-HACK-02' appears in the repository.

**Evidence Required:** File path and line number of the matched ID.

**Pass Condition:** Collected evidence satisfies: The business case ID 'BC-AAIE-HACK-02' appears in the repository.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The business case ID 'BC-AAIE-HACK-02' appears in the repository.

---

## REQ-006

**Source location:** Section 1. Project Identity — table row 3  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Domain | Banking & Finance
~~~

### REQ-006-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-006-T01 |
| **Requirement ID** | REQ-006 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Domain | Banking & Finance
~~~

**Purpose:** The delivered repository declares its domain as Banking & Finance.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan committed Markdown documentation for the declared domain.

**Expected Result:** The domain 'Banking & Finance' appears in the repository documentation.

**Evidence Required:** File path and line number of the matched domain statement.

**Pass Condition:** Collected evidence satisfies: The domain 'Banking & Finance' appears in the repository documentation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The domain 'Banking & Finance' appears in the repository documentation.

---

## REQ-007

**Source location:** Section 1. Project Identity — table row 4  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Project Type | Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon
~~~

### REQ-007-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-007-T01 |
| **Requirement ID** | REQ-007 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Project Type | Agentic AI Engineer Pathway — Cross-Cutting Capstone Hackathon
~~~

**Purpose:** The delivered repository declares the project type stated in the source document.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan committed Markdown documentation.
2. Require both halves of the project type: the pathway and the capstone hackathon.

**Expected Result:** The project type 'Agentic AI Engineer Pathway - Cross-Cutting Capstone Hackathon' is declared.

**Evidence Required:** File paths and line numbers for both matched fragments.

**Pass Condition:** Collected evidence satisfies: The project type 'Agentic AI Engineer Pathway - Cross-Cutting Capstone Hackathon' is declared.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The project type 'Agentic AI Engineer Pathway - Cross-Cutting Capstone Hackathon' is declared.

---

## REQ-008

**Source location:** Section 2. Engagement Overview — table row 1  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Duration | 20 hours
~~~

### REQ-008-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-008-T01 |
| **Requirement ID** | REQ-008 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
Duration | 20 hours
~~~

**Purpose:** The engagement ran for the stated duration.

**Preconditions:** A reviewer has had the opportunity to record out-of-band evidence.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read manual_evidence/manual_attestations.json for entry 'REQ-008-T01'.
2. Require a non-empty evidence string, an attester and an attestation date.

**Expected Result:** A reviewer records that the engagement duration was 20 hours.

**Evidence Required:** A completed attestation record for REQ-008-T01 naming 'the 20-hour engagement duration', its attester and date.

**Pass Condition:** A complete, dated, attributed attestation of 'the 20-hour engagement duration' is recorded.

**Fail Condition:** No attestation, or an incomplete attestation, for 'the 20-hour engagement duration'.

---

## REQ-009

**Source location:** Section 2. Engagement Overview — table row 2  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Format | Team of 2–4
~~~

### REQ-009-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-009-T01 |
| **Requirement ID** | REQ-009 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
Format | Team of 2–4
~~~

**Purpose:** The delivery team matched the stated team size.

**Preconditions:** A reviewer has had the opportunity to record out-of-band evidence.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read manual_evidence/manual_attestations.json for entry 'REQ-009-T01'.
2. Require a non-empty evidence string, an attester and an attestation date.

**Expected Result:** A reviewer records that the team size was within 2-4.

**Evidence Required:** A completed attestation record for REQ-009-T01 naming 'a team of 2-4 people', its attester and date.

**Pass Condition:** A complete, dated, attributed attestation of 'a team of 2-4 people' is recorded.

**Fail Condition:** No attestation, or an incomplete attestation, for 'a team of 2-4 people'.

---

## REQ-010

**Source location:** Section 2. Engagement Overview — table row 3  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

### REQ-010-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-010-T01 |
| **Requirement ID** | REQ-010 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**Purpose:** The submission is a Git repository, which is what the stated evaluation mode reviews.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm a .git directory exists at the implementation root.
2. Run 'git ls-files' and count the tracked files.

**Expected Result:** The implementation root is a Git repository with tracked files.

**Evidence Required:** git ls-files output count.

**Pass Condition:** Collected evidence satisfies: The implementation root is a Git repository with tracked files.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The implementation root is a Git repository with tracked files.

### REQ-010-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-010-T02 |
| **Requirement ID** | REQ-010 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
Evaluation Mode | Automated review of the submitted Git repository against the Hackathon Rubric (7 categories / 100 marks), scored entirely from committed evidence in the repository. No live demo judging.
~~~

**Purpose:** The review was performed automatically against the Hackathon Rubric with no live demo judging.

**Preconditions:** A reviewer has had the opportunity to record out-of-band evidence.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read manual_evidence/manual_attestations.json for entry 'REQ-010-T02'.
2. Require a non-empty evidence string, an attester and an attestation date.

**Expected Result:** A reviewer records that scoring was automated, rubric-based, and included no live demo judging.

**Evidence Required:** A completed attestation record for REQ-010-T02 naming 'an automated review against the Hackathon Rubric (7 categories / 100 marks), with no live demo judging', its attester and date.

**Pass Condition:** A complete, dated, attributed attestation of 'an automated review against the Hackathon Rubric (7 categories / 100 marks), with no live demo judging' is recorded.

**Fail Condition:** No attestation, or an incomplete attestation, for 'an automated review against the Hackathon Rubric (7 categories / 100 marks), with no live demo judging'.

---

## REQ-011

**Source location:** Section 2. Engagement Overview — table row 4  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

### REQ-011-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-011-T01 |
| **Requirement ID** | REQ-011 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Purpose:** The repository has been pushed to a remote, as the submission instruction requires.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Run 'git remote -v' in the implementation root.

**Expected Result:** At least one Git remote is configured.

**Evidence Required:** The 'git remote -v' output.

**Pass Condition:** Collected evidence satisfies: At least one Git remote is configured.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: At least one Git remote is configured.

### REQ-011-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-011-T02 |
| **Requirement ID** | REQ-011 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Purpose:** The configured remote is a GitLab project, as the submission instruction names.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Run 'git remote -v'.
2. Require at least one remote URL naming GitLab.

**Expected Result:** A configured Git remote URL identifies a GitLab project.

**Evidence Required:** The matching remote URL.

**Pass Condition:** Collected evidence satisfies: A configured Git remote URL identifies a GitLab project.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A configured Git remote URL identifies a GitLab project.

### REQ-011-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-011-T03 |
| **Requirement ID** | REQ-011 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
Submission | Push the final repository to your assigned Virtusa GitLab project by the cut-off.
~~~

**Purpose:** The push happened by the cut-off.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Re-read the exact source text of REQ-011.
2. Confirm the document specifies no verifiable value or artifact for 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project'.
3. Record UNSPECIFIED_BY_REQUIREMENT rather than inventing a threshold or path.

**Expected Result:** UNSPECIFIED_BY_REQUIREMENT for 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project'

**Evidence Required:** The exact source text of REQ-011, showing it fixes no testable value for 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project'.

**Pass Condition:** Not reachable: the document supplies nothing to verify against.

**Fail Condition:** Recorded as UNSPECIFIED_BY_REQUIREMENT because the document fixes no value for 'the submission cut-off date and time, and the identity of the assigned Virtusa GitLab project'.

---

## REQ-012

**Source location:** Section 2. Engagement Overview — table row 5  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

### REQ-012-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-012-T01 |
| **Requirement ID** | REQ-012 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
Review Output | Per-team Excel report (Summary, Categories, Scorecard, Detailed, Improvement).
~~~

**Purpose:** The per-team Excel review report with its five stated sections was produced.

**Preconditions:** A reviewer has had the opportunity to record out-of-band evidence.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read manual_evidence/manual_attestations.json for entry 'REQ-012-T01'.
2. Require a non-empty evidence string, an attester and an attestation date.

**Expected Result:** A reviewer records that the Excel report exists with all five named sections.

**Evidence Required:** A completed attestation record for REQ-012-T01 naming 'a per-team Excel report containing the Summary, Categories, Scorecard, Detailed and Improvement sections', its attester and date.

**Pass Condition:** A complete, dated, attributed attestation of 'a per-team Excel report containing the Summary, Categories, Scorecard, Detailed and Improvement sections' is recorded.

**Fail Condition:** No attestation, or an incomplete attestation, for 'a per-team Excel report containing the Summary, Categories, Scorecard, Detailed and Improvement sections'.

---

## REQ-013

**Source location:** Section 2. Engagement Overview — table row 6  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

### REQ-013-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-013-T01 |
| **Requirement ID** | REQ-013 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | NO |

**Exact Original Requirement:**

~~~text
Grade Bands | Pass ≥ 60 · Not Yet Passed < 60
~~~

**Purpose:** The stated grade bands were applied.

**Preconditions:** A reviewer has had the opportunity to record out-of-band evidence.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read manual_evidence/manual_attestations.json for entry 'REQ-013-T01'.
2. Require a non-empty evidence string, an attester and an attestation date.

**Expected Result:** A reviewer records that the Pass >= 60 / Not Yet Passed < 60 bands were applied to the score.

**Evidence Required:** A completed attestation record for REQ-013-T01 naming 'the grade bands Pass >= 60 and Not Yet Passed < 60', its attester and date.

**Pass Condition:** A complete, dated, attributed attestation of 'the grade bands Pass >= 60 and Not Yet Passed < 60' is recorded.

**Fail Condition:** No attestation, or an incomplete attestation, for 'the grade bands Pass >= 60 and Not Yet Passed < 60'.

---

## REQ-014

**Source location:** Section 2. Engagement Overview — paragraph "What is evaluated", sentence 1  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

### REQ-014-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T01 |
| **Requirement ID** | REQ-014 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** A working LangGraph multi-agent system exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the graph module.
2. Confirm LangGraph is a declared dependency.

**Expected Result:** A LangGraph graph module is present and LangGraph is a declared dependency.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A LangGraph graph module is present and LangGraph is a declared dependency.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A LangGraph graph module is present and LangGraph is a declared dependency.

### REQ-014-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T02 |
| **Requirement ID** | REQ-014 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** Context engineering is present as part of the foundation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the context-engineering package.

**Expected Result:** A context-engineering module/package exists and is non-empty.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A context-engineering module/package exists and is non-empty.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A context-engineering module/package exists and is non-empty.

### REQ-014-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T03 |
| **Requirement ID** | REQ-014 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** Tiered memory is present as part of the foundation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the memory package.

**Expected Result:** A memory module/package exists and is non-empty.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A memory module/package exists and is non-empty.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A memory module/package exists and is non-empty.

### REQ-014-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T04 |
| **Requirement ID** | REQ-014 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** A custom MCP server is present as part of the foundation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the MCP server package.

**Expected Result:** A custom MCP server package exists and is non-empty.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A custom MCP server package exists and is non-empty.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A custom MCP server package exists and is non-empty.

### REQ-014-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T05 |
| **Requirement ID** | REQ-014 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** An agentic-RAG tool is present as part of the foundation.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the agentic-RAG tool module.

**Expected Result:** An agentic-RAG tool module exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An agentic-RAG tool module exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An agentic-RAG tool module exists.

### REQ-014-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T06 |
| **Requirement ID** | REQ-014 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** Arize Phoenix observability instruments the system.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the tracing module.
2. Confirm arize-phoenix is a declared dependency.

**Expected Result:** A Phoenix tracing module exists and arize-phoenix is a declared dependency.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A Phoenix tracing module exists and arize-phoenix is a declared dependency.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A Phoenix tracing module exists and arize-phoenix is a declared dependency.

### REQ-014-T07

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T07 |
| **Requirement ID** | REQ-014 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** Cost & latency governance is present.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the golden-signals report.
2. Locate the cost/latency dashboard artifacts.

**Expected Result:** Golden-signals and cost/latency dashboard artifacts exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Golden-signals and cost/latency dashboard artifacts exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Golden-signals and cost/latency dashboard artifacts exist.

### REQ-014-T08

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T08 |
| **Requirement ID** | REQ-014 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** Guardrails & audit are present.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrails package.
2. Locate the audit trail artifact.

**Expected Result:** A guardrails package and an audit-trail artifact both exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A guardrails package and an audit-trail artifact both exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A guardrails package and an audit-trail artifact both exist.

### REQ-014-T09

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T09 |
| **Requirement ID** | REQ-014 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** Governance/compliance documentation is present.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate each of the four governance documents named by the document.

**Expected Result:** The risk register, model card, compliance mapping and output-risk classification all exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The risk register, model card, compliance mapping and output-risk classification all exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The risk register, model card, compliance mapping and output-risk classification all exist.

### REQ-014-T10

| Field | Value |
| --- | --- |
| **Test ID** | REQ-014-T10 |
| **Requirement ID** | REQ-014 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is evaluated: a working LangGraph multi-agent system (foundation: context engineering, tiered memory, a custom MCP server, an agentic-RAG tool) that is then instrumented and governed — Arize Phoenix observability, cost & latency governance, guardrails & audit, governance/compliance documentation, and agent-level evaluation & testing.
~~~

**Purpose:** Agent-level evaluation & testing are present.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the evaluation report.
2. Locate the three named agent test modules.

**Expected Result:** An evaluation report and the three named agent test modules exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An evaluation report and the three named agent test modules exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An evaluation report and the three named agent test modules exist.

---

## REQ-016

**Source location:** Section 2. Engagement Overview — paragraph "What is not evaluated", sentence 1  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
What is not evaluated: the visual polish of any interface, generic unit-test volume, or which optional deployment path you use.
~~~

### REQ-016-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-016-T01 |
| **Requirement ID** | REQ-016 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
What is not evaluated: the visual polish of any interface, generic unit-test volume, or which optional deployment path you use.
~~~

**Purpose:** This validation suite does not score what the source document excludes from evaluation.

**Preconditions:** The test registry is importable.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Inspect every test case in this registry.
2. Confirm none of them scores interface visual polish, raw unit-test volume, or a particular optional deployment path.

**Expected Result:** No registered test scores visual polish, generic unit-test volume, or a chosen deployment path.

**Evidence Required:** The registry scan result, listing any offending test IDs.

**Pass Condition:** Collected evidence satisfies: No registered test scores visual polish, generic unit-test volume, or a chosen deployment path.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No registered test scores visual polish, generic unit-test volume, or a chosen deployment path.

---

## REQ-021

**Source location:** Section 3.2 Your Role — sentence 1  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
Agentic AI Engineer.
~~~

### REQ-021-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-021-T01 |
| **Requirement ID** | REQ-021 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Agentic AI Engineer.
~~~

**Purpose:** The delivered work is presented as the work of the stated role.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan committed Markdown documentation for the role statement.

**Expected Result:** The role 'Agentic AI Engineer' is named in the repository documentation.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The role 'Agentic AI Engineer' is named in the repository documentation.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The role 'Agentic AI Engineer' is named in the repository documentation.

---

## REQ-027

**Source location:** Section 3.3 Expected Solution — bullet 4  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

### REQ-027-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-027-T01 |
| **Requirement ID** | REQ-027 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Purpose:** A Phoenix-derived golden-signals report exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the golden-signals report.

**Expected Result:** reports/golden_signals.json exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: reports/golden_signals.json exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: reports/golden_signals.json exists.

### REQ-027-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-027-T02 |
| **Requirement ID** | REQ-027 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Purpose:** A cost/latency dashboard exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the dashboard screenshot and its underlying data file.

**Expected Result:** Both the dashboard image and its underlying data file exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both the dashboard image and its underlying data file exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both the dashboard image and its underlying data file exist.

### REQ-027-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-027-T03 |
| **Requirement ID** | REQ-027 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Purpose:** Input/output guardrails exist.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrails package.

**Expected Result:** A guardrails package exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A guardrails package exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A guardrails package exists.

### REQ-027-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-027-T04 |
| **Requirement ID** | REQ-027 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Purpose:** An audit trail exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the audit trail artifact.

**Expected Result:** logs/agent_actions.jsonl exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: logs/agent_actions.jsonl exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: logs/agent_actions.jsonl exists.

### REQ-027-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-027-T05 |
| **Requirement ID** | REQ-027 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Purpose:** Secrets hygiene is in place.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate .env.example and .gitignore.

**Expected Result:** Both .env.example and .gitignore exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Both .env.example and .gitignore exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Both .env.example and .gitignore exist.

### REQ-027-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-027-T06 |
| **Requirement ID** | REQ-027 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
A Phoenix-derived golden-signals report and a cost/latency dashboard; input/output guardrails, an audit trail and secrets hygiene; a governance pack (risk register, model card, compliance mapping, output-risk classification).
~~~

**Purpose:** The governance pack contains all four named documents.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the risk register, model card, compliance mapping and output-risk classification.

**Expected Result:** All four governance pack documents exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All four governance pack documents exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All four governance pack documents exist.

---

## REQ-054

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-11  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

### REQ-054-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-054-T01 |
| **Requirement ID** | REQ-054 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Purpose:** The governance pack contains a risk register.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/risk-register.md.

**Expected Result:** A risk register exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A risk register exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A risk register exists.

### REQ-054-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-054-T02 |
| **Requirement ID** | REQ-054 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Purpose:** The governance pack contains a model/system card.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/model-card.md.

**Expected Result:** A model/system card exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A model/system card exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A model/system card exists.

### REQ-054-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-054-T03 |
| **Requirement ID** | REQ-054 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Purpose:** The compliance mapping covers EU AI Act, NIST AI RMF and DPDP.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/compliance.md.
2. Require each of the three frameworks the criterion names.

**Expected Result:** The compliance mapping covers EU AI Act, NIST AI RMF and DPDP.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The compliance mapping covers EU AI Act, NIST AI RMF and DPDP.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The compliance mapping covers EU AI Act, NIST AI RMF and DPDP.

### REQ-054-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-054-T04 |
| **Requirement ID** | REQ-054 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Purpose:** The governance pack contains an output-risk classification.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/output-risk.md.

**Expected Result:** An output-risk classification exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: An output-risk classification exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: An output-risk classification exists.

### REQ-054-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-054-T05 |
| **Requirement ID** | REQ-054 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-11 | A governance pack: risk register, model/system card, compliance mapping (EU AI Act / NIST AI RMF / DPDP) and output-risk classification — each mitigation/claim citing a committed control.
~~~

**Purpose:** Each mitigation/claim in the governance pack cites a committed control.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Extract every file-path citation from the governance documents.
2. Require each to resolve to a committed control or artifact.

**Expected Result:** Every mitigation/claim citation resolves to a committed control.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every mitigation/claim citation resolves to a committed control.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every mitigation/claim citation resolves to a committed control.

---

## REQ-069

**Source location:** Section 7. Required Artifacts — What to Commit — lead-in paragraph, sentence 1  
**Requirement class:** ENGAGEMENT

**Exact Original Requirement:**

~~~text
This is the checklist your submission is scored against.
~~~

### REQ-069-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-069-T01 |
| **Requirement ID** | REQ-069 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
This is the checklist your submission is scored against.
~~~

**Purpose:** The checklist the submission is scored against is exactly what this suite scores.

**Preconditions:** The test registry is importable.

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Enumerate every artifact the Section 7 checklist names.
2. Confirm each is referenced by at least one registered test case.

**Expected Result:** Every checklist artifact is covered by at least one test in this suite.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every checklist artifact is covered by at least one test in this suite.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every checklist artifact is covered by at least one test in this suite.

---

## REQ-087

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Model / system card"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

### REQ-087-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-087-T01 |
| **Requirement ID** | REQ-087 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

**Purpose:** The model / system card exists at docs/model-card.md.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/model-card.md at or near the path shown.

**Expected Result:** docs/model-card.md exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: docs/model-card.md exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: docs/model-card.md exists.

### REQ-087-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-087-T02 |
| **Requirement ID** | REQ-087 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

**Purpose:** The model card states model (Gemini), data (synthetic), intended use, limitations, known failure modes and out-of-scope.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read docs/model-card.md.
2. Require each of the six elements the row names.

**Expected Result:** All six model-card elements are present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All six model-card elements are present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All six model-card elements are present.

### REQ-087-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-087-T03 |
| **Requirement ID** | REQ-087 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Model / system card | docs/model-card.md | model (Gemini), data (synthetic), intended use, limitations, known failure modes (cite failure-analysis.md), out-of-scope
~~~

**Purpose:** The known failure modes cite failure-analysis.md.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the model card for the citation of failure-analysis.md the row requires.

**Expected Result:** The model card cites failure-analysis.md for its known failure modes.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The model card cites failure-analysis.md for its known failure modes.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The model card cites failure-analysis.md for its known failure modes.

---

## REQ-088

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Compliance mapping"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

### REQ-088-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-088-T01 |
| **Requirement ID** | REQ-088 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

**Purpose:** The compliance mapping exists at docs/compliance.md.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/compliance.md at or near the path shown.

**Expected Result:** docs/compliance.md exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: docs/compliance.md exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: docs/compliance.md exists.

### REQ-088-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-088-T02 |
| **Requirement ID** | REQ-088 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

**Purpose:** The mapping names the applicable EU AI Act, NIST AI RMF and DPDP obligations.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read docs/compliance.md.
2. Require all three named frameworks.

**Expected Result:** All three frameworks are mapped.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All three frameworks are mapped.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All three frameworks are mapped.

### REQ-088-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-088-T03 |
| **Requirement ID** | REQ-088 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Compliance mapping | docs/compliance.md | applicable EU AI Act / NIST AI RMF / DPDP obligations → how addressed → evidence artifact
~~~

**Purpose:** Each obligation maps to how it is addressed and to an evidence artifact.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require a 'how addressed' element and an 'evidence artifact' element.
2. Require every cited evidence artifact to resolve to a committed file.

**Expected Result:** Each obligation maps through to a resolvable committed evidence artifact.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Each obligation maps through to a resolvable committed evidence artifact.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Each obligation maps through to a resolvable committed evidence artifact.

---

## REQ-106

**Source location:** Section 8. Producing the Evidence — table row "Governance pack" (continuation table)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Governance pack | Markdown | risk-register.md, model-card.md, compliance.md, output-risk.md — each entry cites the committed control/artifact it refers to.
~~~

### REQ-106-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-106-T01 |
| **Requirement ID** | REQ-106 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Governance pack | Markdown | risk-register.md, model-card.md, compliance.md, output-risk.md — each entry cites the committed control/artifact it refers to.
~~~

**Purpose:** The governance pack is four committed Markdown documents.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate risk-register.md, model-card.md, compliance.md and output-risk.md.

**Expected Result:** All four governance documents exist as Markdown.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All four governance documents exist as Markdown.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All four governance documents exist as Markdown.

### REQ-106-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-106-T02 |
| **Requirement ID** | REQ-106 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Governance pack | Markdown | risk-register.md, model-card.md, compliance.md, output-risk.md — each entry cites the committed control/artifact it refers to.
~~~

**Purpose:** Each entry cites the committed control/artifact it refers to.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Extract every citation from the governance documents.
2. Require each to resolve to a committed control or artifact.

**Expected Result:** Every governance entry's citation resolves to a committed artifact.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every governance entry's citation resolves to a committed artifact.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every governance entry's citation resolves to a committed artifact.

---

## REQ-112

**Source location:** Section 8.1 Good-to-Have — closing italic paragraph (final paragraph of the document)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

### REQ-112-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-112-T01 |
| **Requirement ID** | REQ-112 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Purpose:** The lending decision is observable.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the trace export and the tool-invocation log that make the decision observable.

**Expected Result:** The lending decision is observable through committed traces and logs.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The lending decision is observable through committed traces and logs.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The lending decision is observable through committed traces and logs.

### REQ-112-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-112-T02 |
| **Requirement ID** | REQ-112 |
| **Test Type** | OBSERVABILITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Purpose:** The lending decision is cost-governed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the golden-signals report and the cost/latency data.

**Expected Result:** Cost governance artifacts exist.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Cost governance artifacts exist.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Cost governance artifacts exist.

### REQ-112-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-112-T03 |
| **Requirement ID** | REQ-112 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Purpose:** The lending decision is secure.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrails, the secrets hygiene template and the masking implementation.

**Expected Result:** The security surface is in place.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The security surface is in place.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The security surface is in place.

### REQ-112-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-112-T04 |
| **Requirement ID** | REQ-112 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Purpose:** The lending decision is compliant.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the four governance and compliance documents.

**Expected Result:** The compliance surface is in place.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The compliance surface is in place.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The compliance surface is in place.

### REQ-112-T05

| Field | Value |
| --- | --- |
| **Test ID** | REQ-112-T05 |
| **Requirement ID** | REQ-112 |
| **Test Type** | INTEGRATION_TEST |
| **Executing suite** | `automated_tests/integration/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Purpose:** The lending decision is continuously evaluated.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the evaluation report and the three agent tests.

**Expected Result:** The evaluation surface is in place.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The evaluation surface is in place.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The evaluation surface is in place.

### REQ-112-T06

| Field | Value |
| --- | --- |
| **Test ID** | REQ-112-T06 |
| **Requirement ID** | REQ-112 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
On completion you will have demonstrated the skill the industry actually screens for: not just building a LangGraph agent, but making a lending decision observable, cost-governed, secure, compliant and continuously evaluated — the full production surface of an agentic system, proven with committed evidence rather than a demo that worked once.
~~~

**Purpose:** The result is proven with committed evidence rather than a demo that worked once.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm every named artifact present is committed.
2. Confirm each evidence artifact has committed producing code.
3. Confirm the documented commands can regenerate it, so it is not a one-off demo.

**Expected Result:** The evidence is committed, machine-generated and regenerable on demand.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The evidence is committed, machine-generated and regenerable on demand.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The evidence is committed, machine-generated and regenerable on demand.

---
