# GOLD-18: Enrollment Fraud Flag Triggers Decline

## Decision

**DECLINE** | Risk Grade: **B3** | Adverse Action Required: **Yes**

## Reasoning Chain

1. **Borrower eligibility**: Yuki Yamamoto, 28-year-old US citizen, applying for GR loan at Cedar Falls University (Tier B).

2. **Credit evaluation**: Borrower FICO 687 with established file. One 30-day delinquency in 24 months but otherwise clean. Cosigner Jaya Duval (US citizen) has FICO 735. Credit profiles are marginally acceptable.

3. **Income and DTI**: Borrower DTI 15.5% with income of $85,273. Cosigner DTI 30.3% with income of $133,390. Financial capacity is adequate.

4. **FRAUD FLAG -- HARD STOP**: The fraud screening module has flagged enrollment_fraud_flag=true. Per POL-012 EDU-FRAUD-001, any application with a confirmed enrollment fraud flag is subject to immediate automatic decline. RC-016 (enrollment fraud detected) applies per POL-009.

5. **Enrollment fraud implications**: Enrollment fraud indicates that the borrower's enrollment at Cedar Falls University may be fabricated, misrepresented, or part of a scheme to obtain loan proceeds without genuine educational intent. This is a zero-tolerance violation.

6. **No override available**: Unlike credit-based declines where cosigner strength can compensate, enrollment fraud is a hard stop that cannot be overridden by any credit factor. The decision must be DECLINE regardless of the otherwise acceptable credit profile.

7. **School factors**: Cedar Falls University is Tier B with 8% CDR. The school itself is eligible, but the specific enrollment claim is flagged as fraudulent.

## Policy Citations

- POL-012 EDU-FRAUD-001 (fraud screening -- enrollment fraud)
- POL-009 RC-016 (enrollment fraud detected)

## Documents Requested

None. Application is declined on fraud grounds.

## Conditions

None. Hard decline with no path to reconsideration. Suspicious activity report may be required per POL-012 EDU-FRAUD-001.
