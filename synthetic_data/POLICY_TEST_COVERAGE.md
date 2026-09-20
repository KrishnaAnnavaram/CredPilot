<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python synthetic_data/generator/generate_synthetic_data.py -->

# Policy to Application Test Coverage

Which applications exercise each rule, and whether that rule has the positive, boundary and negative cases it needs to be testable.

- **Positive case** - an application where the rule evaluates PASS.
- **Boundary case** - the PASS case whose observed value sits closest to the threshold. A rule with no numeric threshold has no boundary case, which is shown as a dash rather than as a gap.
- **Negative case** - an application where the rule evaluates FAIL.
- **Human-review case** - an application where triggering the rule routed the file to a person.

A rule with no negative case is not necessarily a defect: a process rule such as DEC-AUD-001 cannot fail on generated data. Rules that drive an eligibility outcome are listed first and are expected to carry both.

- Rules in the corpus: **174**
- Rules exercised by at least one application: **71**
- Rules with both a positive and a negative case: **10**

| Policy | Rule | Severity | Positive case | Boundary case | Negative case | Human-review case |
| --- | --- | --- | --- | --- | --- | --- |
| POL-AST-002 | `AST-FTC-003` | HARD_FAIL | APP-000001 | APP-000007 (gap 1835.65) | APP-000006 | - |
| POL-AST-003 | `AST-RSV-002` | CONDITIONAL | APP-000001 | APP-000006 (gap 0.00) | APP-000007 | - |
| POL-AST-004 | `AST-SRC-001` | CONDITIONAL | APP-000025 | - | APP-000026 | - |
| POL-AST-004 | `AST-SRC-002` | CONDITIONAL | - | - | APP-000040 (REFER) | APP-000040 |
| POL-CONV-003 | `CONV-COR-001` | HARD_FAIL | APP-000023 | APP-000023 (gap 32) | APP-000024 | - |
| POL-CONV-003 | `CONV-COR-002` | HARD_FAIL | APP-000023 | APP-000023 (gap 0.0600) | - | - |
| POL-CONV-003 | `CONV-COR-003` | HARD_FAIL | APP-000023 | APP-000023 (gap 44) | - | - |
| POL-CONV-003 | `CONV-COR-004` | CONDITIONAL | APP-000023 | APP-000023 (gap 2.00) | - | - |
| POL-CONV-001 | `CONV-PUR-002` | HARD_FAIL | APP-000001 | APP-000005 (gap 0.0000) | - | - |
| POL-CONV-001 | `CONV-PUR-003` | CONDITIONAL | APP-000005 | APP-000025 (gap 0.0500) | - | - |
| POL-CONV-001 | `CONV-PUR-004` | CONDITIONAL | APP-000025 | APP-000041 (gap 0.0000) | - | - |
| POL-CONV-002 | `CONV-RTR-002` | HARD_FAIL | APP-000022 | APP-000022 (gap 0.1700) | - | - |
| POL-CRD-003 | `CRD-DLQ-001` | REFER | APP-000001 | APP-000001 (gap 0) | APP-000030 (REFER) | APP-000030 |
| POL-CRD-003 | `CRD-DLQ-002` | REFER | - | - | APP-000031 (REFER) | APP-000031 |
| POL-CRD-003 | `CRD-DLQ-003` | ADVISORY | APP-000001 | APP-000031 (gap 0.0400) | - | - |
| POL-CRD-002 | `CRD-EVT-001` | HARD_FAIL | APP-000027 | APP-000027 (gap 14) | APP-000028 | - |
| POL-CRD-002 | `CRD-EVT-003` | CONDITIONAL | - | - | APP-000032 | - |
| POL-CRD-001 | `CRD-SCR-003` | HARD_FAIL | APP-000001 | APP-000058 (gap 0) | APP-000003 | - |
| POL-CRD-001 | `CRD-SCR-004` | CONDITIONAL | APP-000001 | APP-000001 (gap 69) | - | - |
| POL-CRD-001 | `CRD-SCR-005` | REFER | - | - | APP-000034 (REFER) | APP-000034 |
| POL-CRD-001 | `CRD-SCR-007` | CONDITIONAL | APP-000001 | APP-000001 (gap 3) | APP-000033 (REFER) | - |
| POL-DEC-001 | `DEC-AUD-001` | HARD_FAIL | APP-000001 | - | - | - |
| POL-DEC-001 | `DEC-REC-001` | HARD_FAIL | APP-000001 | - | - | - |
| POL-DOC-001 | `DOC-REQ-002` | CONDITIONAL | - | - | APP-000046 | - |
| POL-DOC-001 | `DOC-REQ-003` | CONDITIONAL | APP-000001 | APP-000001 (gap 0.0000) | - | - |
| POL-DOC-001 | `DOC-REQ-004` | CONDITIONAL | - | - | APP-000042 (INDETERMINATE) | - |
| POL-DTI-001 | `DTI-BRE-001` | HARD_FAIL | APP-000004 | APP-000007 (gap 0.0100) | - | - |
| POL-DTI-001 | `DTI-CALC-003` | ADVISORY | APP-000001 | - | - | - |
| POL-DTI-001 | `DTI-CONV-001` | HARD_FAIL | APP-000001 | APP-000002 (gap 0.0100) | APP-000004 | - |
| POL-DTI-001 | `DTI-CONV-002` | ADVISORY | APP-000001 | APP-000072 (gap 0.0401) | - | - |
| POL-EMP-002 | `EMP-CNT-001` | CONDITIONAL | APP-000001 | APP-000016 (gap 24) | APP-000008 (REFER) | APP-000008 |
| POL-EMP-002 | `EMP-CNT-002` | CONDITIONAL | - | - | APP-000009 (REFER) | APP-000009 |
| POL-EMP-002 | `EMP-CNT-004` | CONDITIONAL | - | - | APP-000016 (REFER) | APP-000016 |
| POL-EMP-001 | `EMP-VER-003` | REFER | - | - | APP-000037 (REFER) | APP-000037 |
| POL-FHA-001 | `FHA-OVL-002` | HARD_FAIL | APP-000019 | APP-000019 (gap 0.0000) | - | - |
| POL-FHA-001 | `FHA-OVL-004` | HARD_FAIL | APP-000019 | APP-000019 (gap 0.0500) | - | - |
| POL-FRD-001 | `FRD-IND-001` | REFER | APP-000001 | APP-000001 (gap 0) | APP-000043 (REFER) | APP-000043 |
| POL-FRD-001 | `FRD-IND-002` | REFER | - | - | APP-000043 | APP-000043 |
| POL-FRD-001 | `FRD-IND-003` | REFER | - | - | APP-000043 (REFER) | APP-000043 |
| POL-GEN-001 | `GEN-ELG-003` | HARD_FAIL | APP-000001 | APP-000063 (gap 271750.00) | - | - |
| POL-GEN-001 | `GEN-ELG-005` | CONDITIONAL | APP-000001 | APP-000001 (gap 0) | APP-000042 (INDETERMINATE) | - |
| POL-INC-001 | `INC-GEN-006` | REFER | - | - | APP-000036 (REFER) | APP-000036 |
| POL-INC-002 | `INC-SAL-003` | REFER | - | - | APP-000038 (REFER) | APP-000038 |
| POL-INC-005 | `INC-SEB-006` | REFER | - | - | APP-000011 (REFER) | APP-000011 |
| POL-INC-004 | `INC-VAR-001` | HARD_FAIL | APP-000010 | APP-000010 (gap 2) | APP-000012 (REFER) | APP-000012 |
| POL-JUMBO-001 | `JMB-ELG-001` | HARD_FAIL | APP-000017 | APP-000017 (gap 153650.00) | - | - |
| POL-JUMBO-001 | `JMB-ELG-002` | HARD_FAIL | APP-000017 | APP-000017 (gap 0.0300) | - | - |
| POL-JUMBO-001 | `JMB-ELG-003` | CONDITIONAL | APP-000017 | APP-000018 (gap 2.00) | - | - |
| POL-JUMBO-001 | `JMB-ELG-004` | REFER | - | - | APP-000017 (REFER) | APP-000017 |
| POL-KYC-001 | `KYC-IDV-001` | HARD_FAIL | APP-000001 | - | APP-000044 (REFER) | APP-000044 |
| POL-KYC-001 | `KYC-IDV-002` | HARD_FAIL | - | - | APP-000044 | APP-000044 |
| POL-LIA-001 | `LIA-INC-006` | CONDITIONAL | - | - | APP-000035 (REFER) | APP-000035 |
| POL-PRP-001 | `PRP-ELG-001` | HARD_FAIL | APP-000001 | - | - | - |
| POL-PRP-001 | `PRP-ELG-002` | CONDITIONAL | - | - | APP-000051 (REFER) | APP-000051 |
| POL-PRP-001 | `PRP-ELG-004` | CONDITIONAL | APP-000047 | - | APP-000048 (INDETERMINATE) | - |
| POL-PRP-002 | `PRP-OCC-002` | REFER | - | - | APP-000039 (REFER) | APP-000039 |
| POL-SEC-001 | `SEC-AUD-001` | HARD_FAIL | APP-000065 | - | - | - |
| POL-SEC-001 | `SEC-INJ-001` | HARD_FAIL | APP-000001 | - | APP-000065 | APP-000065 |
| POL-SEC-001 | `SEC-INJ-002` | HARD_FAIL | - | - | APP-000068 | APP-000068 |
| POL-SEC-001 | `SEC-INJ-003` | HARD_FAIL | - | - | APP-000067 | APP-000067 |
| POL-SEC-001 | `SEC-INJ-004` | CONDITIONAL | - | - | APP-000070 | APP-000070 |
| POL-TTL-001 | `TTL-LIE-002` | CONDITIONAL | - | - | APP-000049 (REFER) | APP-000049 |
| POL-USDA-001 | `USD-OVL-002` | HARD_FAIL | - | - | APP-000021 | - |
| POL-USDA-001 | `USD-OVL-003` | ADVISORY | APP-000021 | APP-000021 (gap 0.0000) | - | - |
| POL-USDA-001 | `USD-OVL-004` | HARD_FAIL | APP-000021 | APP-000021 (gap 0.0601) | - | - |
| POL-UWR-001 | `UWR-HRV-001` | REFER | - | - | APP-000002 (REFER) | APP-000002 |
| POL-VA-001 | `VA-OVL-002` | ADVISORY | APP-000020 | APP-000020 (gap 0.0000) | - | - |
| POL-VA-001 | `VA-OVL-003` | HARD_FAIL | - | - | APP-000020 | - |
| POL-VAL-001 | `VAL-APR-001` | CONDITIONAL | APP-000001 | - | APP-000053 | - |
| POL-VAL-001 | `VAL-APR-002` | HARD_FAIL | APP-000050 | APP-000050 (gap 30600.00) | - | - |
| POL-VAL-001 | `VAL-APR-003` | CONDITIONAL | APP-000001 | APP-000001 (gap 96) | APP-000054 | - |

## Reference-only rules

These rules are part of the corpus but are not evaluated against an application. They are definitional, procedural or govern a workflow stage beyond underwriting, so a retrieval agent should still be able to find and cite them.

- `AST-ELG-001` - Asset categories and their haircuts (POL-AST-001, HARD_FAIL)
- `AST-ELG-002` - Ownership and access (POL-AST-001, CONDITIONAL)
- `AST-ELG-003` - Verified balance governs over declared balance (POL-AST-001, HARD_FAIL)
- `AST-ELG-004` - Asset verification freshness (POL-AST-001, CONDITIONAL)
- `AST-FTC-001` - The funds-to-close calculation (POL-AST-002, HARD_FAIL)
- `AST-FTC-002` - Synthetic closing-cost and prepaid basis (POL-AST-002, ADVISORY)
- `AST-FTC-004` - Draw order and its effect on reserves (POL-AST-002, HARD_FAIL)
- `AST-FTC-005` - Earnest money must be sourced like any other funds (POL-AST-002, CONDITIONAL)
- `AST-RSV-001` - Reserve definition and measurement (POL-AST-003, HARD_FAIL)
- `AST-RSV-003` - Additional financed properties (POL-AST-003, CONDITIONAL)
- `AST-RSV-004` - Reserves in excess of the requirement are a compensating factor (POL-AST-003, ADVISORY)
- `AST-RSV-005` - Reserve shortfall is curable, not a decline (POL-AST-003, CONDITIONAL)
- `AST-SRC-003` - Borrowed funds (POL-AST-004, CONDITIONAL)
- `AST-SRC-004` - Grants and employer assistance (POL-AST-004, CONDITIONAL)
- `CONV-COR-005` - Stated use of proceeds (POL-CONV-003, ADVISORY)
- `CONV-PUR-001` - Eligible transaction characteristics (POL-CONV-001, HARD_FAIL)
- `CONV-PUR-005` - Interested-party contributions are limited (POL-CONV-001, CONDITIONAL)
- `CONV-RTR-001` - Cash returned to the borrower is capped (POL-CONV-002, HARD_FAIL)
- `CONV-RTR-003` - Existing mortgage payment history (POL-CONV-002, REFER)
- `CONV-RTR-004` - Payoff figure must be evidenced (POL-CONV-002, CONDITIONAL)
- `CRD-DLQ-004` - Recent payment behaviour outweighs distant behaviour (POL-CRD-003, ADVISORY)
- `CRD-EVT-002` - Reduced seasoning with documented extenuating circumstances (POL-CRD-002, REFER)
- `CRD-EVT-004` - Disputed tradelines (POL-CRD-002, CONDITIONAL)
- `CRD-SCR-001` - A credit report must be obtained for a permissible purpose (POL-CRD-001, HARD_FAIL)
- `CRD-SCR-002` - Representative score methodology (POL-CRD-001, HARD_FAIL)
- `CRD-SCR-006` - Prohibited-basis characteristics are never credit factors (POL-CRD-001, HARD_FAIL)
- `DEC-ADV-001` - Adverse-action reasons must be specific and accurate (POL-DEC-001, HARD_FAIL)
- `DEC-ADV-002` - Reasons based on a consumer report carry additional notice duties (POL-DEC-001, HARD_FAIL)
- `DEC-ADV-003` - Prohibited bases may never appear in a reason (POL-DEC-001, HARD_FAIL)
- `DEC-REC-002` - A decline recommendation is always routed to a human (POL-DEC-001, REFER)
- `DOC-REQ-001` - Baseline document set (POL-DOC-001, CONDITIONAL)
- `DOC-REQ-005` - Letters of explanation are not self-validating (POL-DOC-001, CONDITIONAL)
- `DOC-REQ-006` - Every extracted field keeps its provenance (POL-DOC-001, HARD_FAIL)
- `DTI-BRE-002` - Payment shock is recorded where a prior housing payment exists (POL-DTI-001, ADVISORY)
- `DTI-CALC-001` - Definition and components of the affordability measures (POL-DTI-001, HARD_FAIL)
- `DTI-CALC-002` - Affordability is computed deterministically, never estimated (POL-DTI-001, HARD_FAIL)
- `DTI-CONV-003` - Recognised compensating factors (POL-DTI-001, CONDITIONAL)
- `EMP-CNT-003` - Employment gaps (POL-EMP-002, CONDITIONAL)
- `EMP-CNT-005` - Tenure is computed deterministically (POL-EMP-002, HARD_FAIL)
- `EMP-VER-001` - Independent verification is required (POL-EMP-001, CONDITIONAL)
- `EMP-VER-002` - Re-verification before closing (POL-EMP-001, CONDITIONAL)
- `EMP-VER-004` - Verification freshness (POL-EMP-001, CONDITIONAL)
- `FHA-OVL-001` - Authority and what this document is not (POL-FHA-001, ADVISORY)
- `FHA-OVL-003` - Insurance premiums enter the housing expense (POL-FHA-001, CONDITIONAL)
- `FRD-IND-004` - An indicator is not by itself an adverse-action reason (POL-FRD-001, HARD_FAIL)
- `GEN-ELG-001` - Order of evaluation (POL-GEN-001, ADVISORY)
- `GEN-ELG-002` - Applicable policy version is selected by as-of date (POL-GEN-001, HARD_FAIL)
- `GEN-ELG-004` - Eligibility, risk, recommendation and credit decision are distinct (POL-GEN-001, HARD_FAIL)
- `GEN-ELG-006` - Ability to repay must be established from verified information (POL-GEN-001, HARD_FAIL)
- `INC-GEN-001` - Declared, verified and qualifying amounts are stored separately (POL-INC-001, HARD_FAIL)
- `INC-GEN-002` - Qualifying income must not exceed verified income (POL-INC-001, HARD_FAIL)
- `INC-GEN-003` - Continuance period (POL-INC-001, HARD_FAIL)
- `INC-GEN-004` - Income source is never a basis for discounting (POL-INC-001, HARD_FAIL)
- `INC-GEN-005` - Non-taxable income may be grossed up (POL-INC-001, CONDITIONAL)
- `INC-HRL-001` - Guaranteed hours are qualified as fixed income (POL-INC-003, HARD_FAIL)
- `INC-HRL-002` - Variable hours are averaged over history (POL-INC-003, HARD_FAIL)
- `INC-HRL-003` - Declining hours reduce the qualifying amount (POL-INC-003, REFER)
- `INC-HRL-004` - Seasonal employment (POL-INC-003, CONDITIONAL)
- `INC-OTH-001` - Retirement, pension and benefit income (POL-INC-007, CONDITIONAL)
- `INC-OTH-002` - Benefit income is never discounted for its source (POL-INC-007, HARD_FAIL)
- `INC-OTH-003` - Interest and dividend income (POL-INC-007, CONDITIONAL)
- `INC-OTH-004` - Support payments the borrower chooses to disclose (POL-INC-007, CONDITIONAL)
- `INC-OTH-005` - Military pay and allowances (POL-INC-007, CONDITIONAL)
- `INC-RNT-001` - Vacancy factor (POL-INC-006, HARD_FAIL)
- `INC-RNT-002` - Net rental income and negative rent (POL-INC-006, HARD_FAIL)
- `INC-RNT-003` - Evidence hierarchy (POL-INC-006, CONDITIONAL)
- `INC-RNT-004` - Related-party leases (POL-INC-006, REFER)
- `INC-SAL-001` - Conversion to monthly qualifying income (POL-INC-002, HARD_FAIL)
- `INC-SAL-002` - Required documentation (POL-INC-002, CONDITIONAL)
- `INC-SAL-004` - A documented raise may be used before it appears on a paystub (POL-INC-002, CONDITIONAL)
- `INC-SEB-001` - Ownership test determines the analysis method (POL-INC-005, HARD_FAIL)
- `INC-SEB-002` - Required history and returns (POL-INC-005, CONDITIONAL)
- `INC-SEB-003` - Cash-flow analysis, not revenue (POL-INC-005, HARD_FAIL)
- `INC-SEB-004` - Declining business income (POL-INC-005, REFER)
- `INC-SEB-005` - Current-period evidence (POL-INC-005, CONDITIONAL)
- `INC-VAR-002` - Averaging method (POL-INC-004, HARD_FAIL)
- `INC-VAR-003` - Declining variable income (POL-INC-004, REFER)
- `INC-VAR-004` - Commission income with significant unreimbursed expenses (POL-INC-004, CONDITIONAL)
- `INC-VAR-005` - Positive factors supporting a shorter history (POL-INC-004, CONDITIONAL)
- `JMB-ELG-005` - Second valuation above a loan amount threshold (POL-JUMBO-001, CONDITIONAL)
- `KYC-IDV-003` - Identifiers are tokenised in every downstream system (POL-KYC-001, HARD_FAIL)
- `LIA-INC-001` - Every obligation is recorded individually with its inclusion decision (POL-LIA-001, HARD_FAIL)
- `LIA-INC-002` - Obligations ending within ten months may be excluded (POL-LIA-001, CONDITIONAL)
- `LIA-INC-003` - Revolving accounts use the stated minimum payment (POL-LIA-001, HARD_FAIL)
- `LIA-INC-004` - Deferred and income-driven obligations (POL-LIA-001, CONDITIONAL)
- `LIA-INC-005` - Obligations paid by another party (POL-LIA-001, CONDITIONAL)
- `PRP-ELG-003` - Condominium project eligibility (POL-PRP-001, CONDITIONAL)
- `PRP-OCC-001` - Occupancy classes (POL-PRP-002, HARD_FAIL)
- `PRP-OCC-003` - Occupancy misrepresentation is a fraud finding, not a pricing question (POL-PRP-002, REFER)
- `SEC-PII-001` - Minimum necessary data reaches any component (POL-SEC-001, HARD_FAIL)
- `SEC-PII-002` - Demographic monitoring data is segregated from decisioning (POL-SEC-001, HARD_FAIL)
- `TTL-INS-001` - Hazard insurance (POL-TTL-001, CONDITIONAL)
- `TTL-INS-002` - Vesting must match the borrowers (POL-TTL-001, CONDITIONAL)
- `TTL-LIE-001` - Required lien position (POL-TTL-001, HARD_FAIL)
- `USD-OVL-001` - Property and occupancy eligibility (POL-USDA-001, HARD_FAIL)
- `UWR-CND-001` - Condition lifecycle (POL-UWR-001, CONDITIONAL)
- `UWR-CND-002` - Prior-to-close conditions gate the clear-to-close (POL-UWR-001, HARD_FAIL)
- `UWR-EXC-001` - Exception authority (POL-UWR-001, REFER)
- `UWR-EXC-002` - An automated component may never grant an exception (POL-UWR-001, HARD_FAIL)
- `VA-OVL-001` - Programme eligibility rests on an entitlement certificate (POL-VA-001, HARD_FAIL)
- `VA-OVL-004` - Occupancy certification (POL-VA-001, HARD_FAIL)
- `VAL-APR-004` - Appraiser independence (POL-VAL-001, HARD_FAIL)
- `VAL-APR-005` - Valuation data standard and metadata (POL-VAL-001, ADVISORY)
