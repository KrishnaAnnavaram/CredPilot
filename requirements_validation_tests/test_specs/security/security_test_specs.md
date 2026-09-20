<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - security

Generated: 2026-09-20T05:48:35Z

11 requirement(s), 29 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-031

**Source location:** Section 3.4 Applicable Rules — bullet 3 (Synthetic-Data Rule)  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

### REQ-031-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-031-T01 |
| **Requirement ID** | REQ-031 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

**Purpose:** Loan applications and lending policies are synthetic.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the repository for the declaration that the application and policy data is synthetic.

**Expected Result:** The loan application and lending policy data is declared synthetic.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The loan application and lending policy data is declared synthetic.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The loan application and lending policy data is declared synthetic.

### REQ-031-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-031-T02 |
| **Requirement ID** | REQ-031 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

**Purpose:** No real-format account or card numbers are written in plaintext anywhere in the repository.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan every committed text artifact for card numbers matching the major issuer patterns.

**Expected Result:** No unmasked card number appears anywhere in the repository.

**Evidence Required:** The scanned file count, and any matching file and line.

**Pass Condition:** Collected evidence satisfies: No unmasked card number appears anywhere in the repository.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No unmasked card number appears anywhere in the repository.

### REQ-031-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-031-T03 |
| **Requirement ID** | REQ-031 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Synthetic-Data Rule. Use only synthetic loan applications and lending policies you generate. Applicant PII and account/card numbers must be synthetic and masked where shown; never write them to logs in plaintext.
~~~

**Purpose:** Applicant PII is masked where shown and never written to logs in plaintext.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm masking/redaction code exists in the implementation.
2. Scan the committed logs for unmasked account, card and credit identifiers.

**Expected Result:** Masking is implemented and no committed log contains plaintext sensitive identifiers.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Masking is implemented and no committed log contains plaintext sensitive identifiers.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Masking is implemented and no committed log contains plaintext sensitive identifiers.

---

## REQ-042

**Source location:** Section 4. Technology & Framework Stack — table row "Security"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

### REQ-042-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-042-T01 |
| **Requirement ID** | REQ-042 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

**Purpose:** Guardrails-AI or LLM Guard provides the guardrail layer.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Check for guardrails-ai.
2. Otherwise check for llm-guard - the document permits either.

**Expected Result:** Either Guardrails-AI or LLM Guard is declared.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Either Guardrails-AI or LLM Guard is declared.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Either Guardrails-AI or LLM Guard is declared.

### REQ-042-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-042-T02 |
| **Requirement ID** | REQ-042 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

**Purpose:** Presidio provides PII handling.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm Presidio is declared.
2. Confirm it is used in code.

**Expected Result:** Presidio is declared and used for PII.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Presidio is declared and used for PII.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Presidio is declared and used for PII.

### REQ-042-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-042-T03 |
| **Requirement ID** | REQ-042 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Security | Guardrails-AI / LLM Guard · Presidio (PII) · python-dotenv
~~~

**Purpose:** python-dotenv provides environment configuration.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm python-dotenv is declared.
2. Confirm it is used.

**Expected Result:** python-dotenv is declared and used.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: python-dotenv is declared and used.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: python-dotenv is declared and used.

---

## REQ-049

**Source location:** Section 5.1 Functional Acceptance Criteria — table row AC-06  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

### REQ-049-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-049-T01 |
| **Requirement ID** | REQ-049 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

**Purpose:** Attempts to inject instructions are refused.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for injection detection.
2. Require the detected attempt to be refused, blocked or rejected.

**Expected Result:** Instruction-injection attempts are refused.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Instruction-injection attempts are refused.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Instruction-injection attempts are refused.

### REQ-049-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-049-T02 |
| **Requirement ID** | REQ-049 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

**Purpose:** Attempts to access another applicant's data are refused.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search for the control that scopes data access to the requesting applicant.

**Expected Result:** Cross-applicant data access is refused.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Cross-applicant data access is refused.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Cross-applicant data access is refused.

### REQ-049-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-049-T03 |
| **Requirement ID** | REQ-049 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

**Purpose:** Sensitive data is never exposed in logs.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm masking exists.
2. Scan every committed log and data artifact for plaintext income, account numbers and credit identifiers.

**Expected Result:** No committed log exposes income, account numbers or credit identifiers.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No committed log exposes income, account numbers or credit identifiers.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No committed log exposes income, account numbers or credit identifiers.

### REQ-049-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-049-T04 |
| **Requirement ID** | REQ-049 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
AC-06 | The copilot handles untrusted applicant-supplied input safely: attempts to inject instructions or access another applicant's data are refused, and sensitive data (income, account numbers, credit identifiers) is never exposed in answers or logs.
~~~

**Purpose:** Sensitive data is never exposed in answers.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the output path for masking applied before an answer is emitted.

**Expected Result:** Answers are masked so sensitive data is not exposed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Answers are masked so sensitive data is not exposed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Answers are masked so sensitive data is not exposed.

---

## REQ-056

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-01  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

### REQ-056-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-056-T01 |
| **Requirement ID** | REQ-056 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

**Purpose:** No secrets or keys are committed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan every committed text artifact against a set of credential patterns.
2. Ignore documented placeholders in the committed template.

**Expected Result:** No secret or key is committed anywhere in the repository.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No secret or key is committed anywhere in the repository.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No secret or key is committed anywhere in the repository.

### REQ-056-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-056-T02 |
| **Requirement ID** | REQ-056 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

**Purpose:** Configuration is by environment variable with a committed .env.example, and .gitignore covers .env.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate .gitignore and require a rule covering .env.
2. Locate the committed .env.example template.
3. Confirm no real .env is committed.

**Expected Result:** Env-var config with a committed .env.example and a .gitignore covering .env.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Env-var config with a committed .env.example and a .gitignore covering .env.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Env-var config with a committed .env.example and a .gitignore covering .env.

### REQ-056-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-056-T03 |
| **Requirement ID** | REQ-056 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-01 | No secrets/keys committed; env-var config with a committed .env.example and a .gitignore covering .env.
~~~

**Purpose:** Configuration is read from environment variables.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for environment-variable configuration.

**Expected Result:** Configuration is read from environment variables.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Configuration is read from environment variables.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Configuration is read from environment variables.

---

## REQ-058

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-03  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
NFR-03 | Untrusted free-text applicant-supplied content is quarantined and never treated as instructions.
~~~

### REQ-058-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-058-T01 |
| **Requirement ID** | REQ-058 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-03 | Untrusted free-text applicant-supplied content is quarantined and never treated as instructions.
~~~

**Purpose:** Untrusted free-text applicant-supplied content is quarantined.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the implementation for the quarantine mechanism.

**Expected Result:** Untrusted free-text applicant-supplied content is quarantined.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Untrusted free-text applicant-supplied content is quarantined.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Untrusted free-text applicant-supplied content is quarantined.

### REQ-058-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-058-T02 |
| **Requirement ID** | REQ-058 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-03 | Untrusted free-text applicant-supplied content is quarantined and never treated as instructions.
~~~

**Purpose:** Quarantined content is never treated as instructions.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate where quarantined content enters the model context.
2. Require it to be handled as data rather than as instructions.

**Expected Result:** Quarantined content is passed as data and never interpreted as instructions.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Quarantined content is passed as data and never interpreted as instructions.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Quarantined content is passed as data and never interpreted as instructions.

---

## REQ-060

**Source location:** Section 5.2 Non-Functional Requirements — table row NFR-05  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
NFR-05 | All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext.
~~~

### REQ-060-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-060-T01 |
| **Requirement ID** | REQ-060 |
| **Test Type** | DATA_VALIDATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-05 | All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext.
~~~

**Purpose:** All data is synthetic.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the repository for the declaration that all data is synthetic.

**Expected Result:** All data is declared synthetic.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All data is declared synthetic.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All data is declared synthetic.

### REQ-060-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-060-T02 |
| **Requirement ID** | REQ-060 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
NFR-05 | All data synthetic; income, account numbers, credit identifiers masked and never logged in plaintext.
~~~

**Purpose:** Income, account numbers and credit identifiers are masked and never logged in plaintext.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm masking is implemented.
2. Scan every committed log and data artifact for plaintext sensitive identifiers.

**Expected Result:** Sensitive identifiers are masked and absent from the committed logs in plaintext.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Sensitive identifiers are masked and absent from the committed logs in plaintext.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Sensitive identifiers are masked and absent from the committed logs in plaintext.

---

## REQ-068

**Source location:** Section 6.2 Out of Scope (this cut) — bullet 4  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Advanced OAuth flows and live secrets-rotation infrastructure (document the approach instead).
~~~

### REQ-068-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-068-T01 |
| **Requirement ID** | REQ-068 |
| **Test Type** | NEGATIVE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Advanced OAuth flows and live secrets-rotation infrastructure (document the approach instead).
~~~

**Purpose:** No advanced OAuth flow or live secrets-rotation infrastructure is implemented.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan the implementation for OAuth flows and live secrets-rotation infrastructure.

**Expected Result:** Neither is implemented, matching the stated out-of-scope decision.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Neither is implemented, matching the stated out-of-scope decision.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Neither is implemented, matching the stated out-of-scope decision.

### REQ-068-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-068-T02 |
| **Requirement ID** | REQ-068 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Advanced OAuth flows and live secrets-rotation infrastructure (document the approach instead).
~~~

**Purpose:** The approach to OAuth and secrets rotation is documented instead.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. S
2. e
3. a
4. r
5. c
6. h
7.  
8. t
9. h
10. e
11.  
12. c
13. o
14. m
15. m
16. i
17. t
18. t
19. e
20. d
21.  
22. d
23. o
24. c
25. u
26. m
27. e
28. n
29. t
30. a
31. t
32. i
33. o
34. n
35.  
36. f
37. o
38. r
39.  
40. t
41. h
42. e
43.  
44. s
45. t
46. a
47. t
48. e
49. d
50.  
51. a
52. p
53. p
54. r
55. o
56. a
57. c
58. h
59.  
60. t
61. o
62.  
63. O
64. A
65. u
66. t
67. h
68.  
69. a
70. n
71. d
72.  
73. s
74. e
75. c
76. r
77. e
78. t
79. s
80.  
81. r
82. o
83. t
84. a
85. t
86. i
87. o
88. n
89. .

**Expected Result:** The approach is documented, as the source text instructs in place of implementing it.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The approach is documented, as the source text instructs in place of implementing it.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The approach is documented, as the source text instructs in place of implementing it.

---

## REQ-083

**Source location:** Section 7.4 Security & Guardrails — table row "Guardrail code"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Guardrail code | src/guardrails/ | input/output guardrails wired into the agent's I/O path (blocks/sanitizes)
~~~

### REQ-083-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-083-T01 |
| **Requirement ID** | REQ-083 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Guardrail code | src/guardrails/ | input/output guardrails wired into the agent's I/O path (blocks/sanitizes)
~~~

**Purpose:** The guardrail code exists at src/guardrails/.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate src/guardrails/ at or near the path shown.

**Expected Result:** src/guardrails/ exists and is non-empty.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: src/guardrails/ exists and is non-empty.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: src/guardrails/ exists and is non-empty.

### REQ-083-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-083-T02 |
| **Requirement ID** | REQ-083 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Guardrail code | src/guardrails/ | input/output guardrails wired into the agent's I/O path (blocks/sanitizes)
~~~

**Purpose:** Input/output guardrails are wired into the agent's I/O path and block or sanitize.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require an input guardrail and an output guardrail.
2. Require blocking or sanitizing behaviour.
3. Require a module outside the guardrail package to call into it.

**Expected Result:** Guardrails are wired into the I/O path and block or sanitize.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Guardrails are wired into the I/O path and block or sanitize.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Guardrails are wired into the I/O path and block or sanitize.

---

## REQ-085

**Source location:** Section 7.4 Security & Guardrails — table row "Secrets hygiene"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Secrets hygiene | .env.example, .gitignore | env-var config; .gitignore covers .env; no secrets committed anywhere
~~~

### REQ-085-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-085-T01 |
| **Requirement ID** | REQ-085 |
| **Test Type** | CONFIGURATION_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Secrets hygiene | .env.example, .gitignore | env-var config; .gitignore covers .env; no secrets committed anywhere
~~~

**Purpose:** Env-var config with a committed .env.example, and .gitignore covering .env.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate .gitignore and require a rule covering .env.
2. Locate the committed .env.example.
3. Confirm no real .env is committed.

**Expected Result:** Secrets hygiene per the row: env-var config, .gitignore covers .env.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Secrets hygiene per the row: env-var config, .gitignore covers .env.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Secrets hygiene per the row: env-var config, .gitignore covers .env.

### REQ-085-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-085-T02 |
| **Requirement ID** | REQ-085 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Secrets hygiene | .env.example, .gitignore | env-var config; .gitignore covers .env; no secrets committed anywhere
~~~

**Purpose:** No secrets are committed anywhere.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Scan every committed text artifact against a set of credential patterns.

**Expected Result:** No secret is committed anywhere in the repository.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: No secret is committed anywhere in the repository.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: No secret is committed anywhere in the repository.

---

## REQ-104

**Source location:** Section 8. Producing the Evidence — table row "Guardrail code"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

### REQ-104-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-104-T01 |
| **Requirement ID** | REQ-104 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

**Purpose:** The guardrail code is a Python module.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the guardrail package.
2. Confirm it contains Python definitions.

**Expected Result:** The guardrail code is a real Python module.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: The guardrail code is a real Python module.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: The guardrail code is a real Python module.

### REQ-104-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-104-T02 |
| **Requirement ID** | REQ-104 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

**Purpose:** Guardrails-AI / LLM Guard validators, or policy functions, wrap the agent's input and output.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require Guardrails-AI, LLM Guard, or policy functions - the document permits any.
2. Require them to wrap both the input and the output.

**Expected Result:** Validators or policy functions wrap the agent's input and output.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Validators or policy functions wrap the agent's input and output.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Validators or policy functions wrap the agent's input and output.

### REQ-104-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-104-T03 |
| **Requirement ID** | REQ-104 |
| **Test Type** | ARCHITECTURE_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Guardrail code | Python module | Guardrails-AI / LLM Guard validators (or policy functions) wrapped around the agent’s input and output, wired into the graph’s I/O nodes.
~~~

**Purpose:** The guardrails are wired into the graph's I/O nodes.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm the graph references the guardrail layer at its I/O nodes.

**Expected Result:** Guardrails are wired into the graph's I/O nodes.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Guardrails are wired into the graph's I/O nodes.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Guardrails are wired into the graph's I/O nodes.

---

## REQ-110

**Source location:** Section 8.1 Good-to-Have — bullet 2  
**Requirement class:** OPTIONAL

**Exact Original Requirement:**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

### REQ-110-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-110-T01 |
| **Requirement ID** | REQ-110 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

**Purpose:** PII-redaction middleware using Presidio exists.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Confirm Presidio is declared and used.
2. Confirm redaction is applied.

**Expected Result:** Presidio-based PII-redaction middleware exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Presidio-based PII-redaction middleware exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Presidio-based PII-redaction middleware exists.

### REQ-110-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-110-T02 |
| **Requirement ID** | REQ-110 |
| **Test Type** | DOCUMENTATION_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

**Purpose:** A before/after redaction sample is committed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Search the committed documentation and data for a before/after redaction sample.

**Expected Result:** A before/after redaction sample is committed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A before/after redaction sample is committed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A before/after redaction sample is committed.

### REQ-110-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-110-T03 |
| **Requirement ID** | REQ-110 |
| **Test Type** | SECURITY_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
PII-redaction middleware (Presidio) with a before/after sample; a small red-team attack set + results.
~~~

**Purpose:** A small red-team attack set and its results are committed.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate the committed red-team attack set.
2. Locate its committed results.

**Expected Result:** A red-team attack set and its results are both committed.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A red-team attack set and its results are both committed.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A red-team attack set and its results are both committed.

---
