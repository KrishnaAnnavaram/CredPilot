<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python traceability/build_traceability.py
     Sources: source_requirements/requirements_verbatim.md (hashed) and
              automated_tests/registry/ -->

# CredPilot Requirement Test Specifications - risk

Generated: 2026-09-20T05:48:35Z

2 requirement(s), 7 test case(s) in this category.

Every test below carries its **Exact Original Requirement** verbatim from `source_requirements/requirements_verbatim.md`. That field is read from the hashed baseline at generation time and is never edited.

---

## REQ-086

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Risk register"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

### REQ-086-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-086-T01 |
| **Requirement ID** | REQ-086 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

**Purpose:** The risk register exists at docs/risk-register.md.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/risk-register.md at or near the path shown.

**Expected Result:** docs/risk-register.md exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: docs/risk-register.md exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: docs/risk-register.md exists.

### REQ-086-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-086-T02 |
| **Requirement ID** | REQ-086 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 3 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

**Purpose:** The risk register carries risk, category (OWASP/NIST), likelihood, impact, mitigation, residual risk and owner.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read docs/risk-register.md.
2. Require each of the seven elements the row names.

**Expected Result:** All seven risk-register elements are present.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All seven risk-register elements are present.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All seven risk-register elements are present.

### REQ-086-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-086-T03 |
| **Requirement ID** | REQ-086 |
| **Test Type** | AUDITABILITY_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Risk register | docs/risk-register.md | risk, category (OWASP/NIST), likelihood, impact, mitigation (cite the committed control), residual risk, owner
~~~

**Purpose:** Each mitigation cites the committed control.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Extract the citations from the risk register.
2. Require each to resolve to a committed control.

**Expected Result:** Every mitigation citation resolves to a committed control.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: Every mitigation citation resolves to a committed control.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: Every mitigation citation resolves to a committed control.

---

## REQ-089

**Source location:** Section 7.5 Governance & Compliance (citation-gated) — table row "Output-risk classification"  
**Requirement class:** IMPLEMENTATION

**Exact Original Requirement:**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

### REQ-089-T01

| Field | Value |
| --- | --- |
| **Test ID** | REQ-089-T01 |
| **Requirement ID** | REQ-089 |
| **Test Type** | STATIC_TEST |
| **Executing suite** | `automated_tests/static/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

**Purpose:** The output-risk classification exists at docs/output-risk.md.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Locate docs/output-risk.md at or near the path shown.

**Expected Result:** docs/output-risk.md exists.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: docs/output-risk.md exists.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: docs/output-risk.md exists.

### REQ-089-T02

| Field | Value |
| --- | --- |
| **Test ID** | REQ-089-T02 |
| **Requirement ID** | REQ-089 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

**Purpose:** The classification defines low, medium and high output tiers.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Read docs/output-risk.md.
2. Require the low, medium and high tiers.

**Expected Result:** All three output-risk tiers are defined.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: All three output-risk tiers are defined.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: All three output-risk tiers are defined.

### REQ-089-T03

| Field | Value |
| --- | --- |
| **Test ID** | REQ-089-T03 |
| **Requirement ID** | REQ-089 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 2 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

**Purpose:** The document states how high-risk output is gated by human-in-loop or refusal.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require a statement of how high-risk output is gated.
2. Require the gate to be human-in-loop or refusal.

**Expected Result:** High-risk output is gated by human-in-loop or refusal.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: High-risk output is gated by human-in-loop or refusal.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: High-risk output is gated by human-in-loop or refusal.

### REQ-089-T04

| Field | Value |
| --- | --- |
| **Test ID** | REQ-089-T04 |
| **Requirement ID** | REQ-089 |
| **Test Type** | GOVERNANCE_TEST |
| **Executing suite** | `automated_tests/governance/` |
| **Weight** | 1 |
| **Automatable** | YES |

**Exact Original Requirement:**

~~~text
Output-risk classification | docs/output-risk.md | low/med/high output tiers + how high-risk is gated (human-in-loop / refusal) + a sample
~~~

**Purpose:** A sample is included.

**Preconditions:** The requirements baseline hash verifies, and the CredPilot implementation root is resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target).

**Inputs:** UNSPECIFIED_BY_REQUIREMENT

**Execution Steps:**

1. Require the sample the row asks for.

**Expected Result:** A sample is included in the output-risk classification.

**Evidence Required:** Concrete artifact evidence: resolved path, matched line with line number, record count, or captured process output.

**Pass Condition:** Collected evidence satisfies: A sample is included in the output-risk classification.

**Fail Condition:** Evidence is absent, incomplete, or contradicts: A sample is included in the output-risk classification.

---
