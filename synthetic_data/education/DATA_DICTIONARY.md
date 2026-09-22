# Data Dictionary — Education Loan Origination Copilot

**Lender:** Edgemont Education Lending (fictional)
**Dataset size:** 200 synthetic applications
**Format:** One JSON file per application (no CSV)
**All data is entirely fictional.** No real borrowers, schools, or credit records are represented.

---

## 1. Application

Top-level object representing a single loan application.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `application_id` | string | `APP-2026-XXXXX` (zero-padded 5-digit sequence) | No | Unique identifier for the application. |
| `product_code` | string | `UG` \| `GR` \| `SP` \| `INTL` \| `REFI` | No | Loan product type. UG = Undergraduate, GR = Graduate, SP = Specialty/Professional, INTL = International Student, REFI = Refinance. |
| `submitted_at` | string | ISO 8601 datetime (`YYYY-MM-DDTHH:MM:SSZ`) | No | Timestamp when the application was submitted. |
| `channel` | string | `direct` \| `school_referral` \| `partner` | No | Origination channel through which the application was received. |
| `requested_amount` | number | Positive decimal | No | Dollar amount the applicant requested to borrow. |
| `loan_purpose` | string | Free-text description | No | Stated purpose of the loan (e.g., "Tuition and living expenses", "Refinance existing student debt"). |
| `state_of_residence` | string | Two-letter US state/territory code (e.g., `CA`, `NY`) | No | Applicant's state of residence at time of application. |
| `has_cosigner` | boolean | `true` \| `false` | No | Whether the application includes a cosigner. |
| `status` | string | `DECISIONED` | No | All 200 applications in this dataset have reached a final decision; value is always `DECISIONED`. |

---

## 2. Borrower (embedded object)

Nested inside each application. Contains the primary borrower's personal and contact information.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `borrower_id` | string | `BORR-XXXXX` (zero-padded 5-digit sequence) | No | Unique identifier for the borrower. |
| `first_name` | string | Alphabetic | No | Borrower's first name. |
| `last_name` | string | Alphabetic | No | Borrower's last name. |
| `dob` | string | `YYYY-MM-DD` | No | Date of birth. |
| `age` | integer | Positive integer | No | Borrower's age in years at time of application. |
| `ssn_itin_masked` | string | `XXX-XX-####` (last four digits visible) | No | Masked Social Security Number or Individual Taxpayer Identification Number. First five digits are replaced with `X`. |
| `email` | string | Valid email format | No | Borrower's email address. |
| `phone` | string | US phone format | No | Borrower's phone number. |
| `address_line1` | string | Street address | No | Primary street address. |
| `city` | string | City name | No | City of residence. |
| `state` | string | Two-letter US state code | No | State of residence. |
| `zip` | string | 5-digit ZIP code | No | ZIP code. |
| `citizenship_status` | string | `US_CITIZEN` \| `PERM_RESIDENT` \| `F1_VISA` \| `J1_VISA` | No | Borrower's citizenship or immigration status. `F1_VISA` and `J1_VISA` appear only on INTL product applications. |
| `years_at_address` | number | Non-negative number | No | Number of years the borrower has lived at the current address. |
| `references_provided` | integer | `0` \| `1` \| `2` \| `3` | No | Count of personal or professional references supplied with the application. |

---

## 3. Cosigner (embedded object, nullable)

Nested inside each application. Present only when `has_cosigner` is `true`; otherwise `null`.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `cosigner_id` | string | `COSIG-XXXXX` (zero-padded 5-digit sequence) | No | Unique identifier for the cosigner. |
| `borrower_id` | string | `BORR-XXXXX` | No | Foreign key linking to the primary borrower this cosigner supports. |
| `relationship` | string | `parent` \| `spouse` \| `relative` \| `other` | No | Cosigner's relationship to the borrower. |
| `first_name` | string | Alphabetic | No | Cosigner's first name. |
| `last_name` | string | Alphabetic | No | Cosigner's last name. |
| `dob` | string | `YYYY-MM-DD` | No | Cosigner's date of birth. |
| `citizenship_status` | string | `US_CITIZEN` \| `PERM_RESIDENT` | No | Cosigner's citizenship status. Only US citizens and permanent residents may serve as cosigners. |
| `ssn_masked` | string | `XXX-XX-####` | No | Cosigner's masked SSN (last four digits visible). |
| `address` | string | Full mailing address | No | Cosigner's residential address. |
| `cosigner_notice_acknowledged` | boolean | `true` \| `false` | No | Whether the cosigner has acknowledged the regulatory cosigner notice (CFPB model notice or equivalent). |

---

## 4. Credit Bureau (array of objects)

Array nested inside each application. Contains one entry per credit pull per subject (borrower and, if present, cosigner). A single application may have multiple pulls (e.g., a soft pull followed by a hard pull).

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `subject_id` | string | `BORR-XXXXX` or `COSIG-XXXXX` | No | Identifier of the person whose credit was pulled. |
| `subject_type` | string | `borrower` \| `cosigner` | No | Role of the subject in the application. |
| `pull_date` | string | `YYYY-MM-DD` | No | Date the credit report was pulled. |
| `pull_type` | string | `SOFT` \| `HARD` | No | Type of credit inquiry. `SOFT` does not affect the subject's score; `HARD` does. |
| `fico_score` | integer | 300 -- 850 | Yes | FICO score. `null` when `file_status` is `NO_FILE`. |
| `file_status` | string | `NO_FILE` \| `THIN` \| `ESTABLISHED` | No | Characterization of the credit file. `NO_FILE` = no bureau record found; `THIN` = fewer than 5 tradelines or limited history; `ESTABLISHED` = 5+ tradelines with sufficient history. |
| `oldest_tradeline_months` | integer | Non-negative integer | Yes | Age in months of the oldest tradeline on file. `null` when `file_status` is `NO_FILE`. |
| `open_tradelines` | integer | Non-negative integer | Yes | Number of currently open tradelines. `null` when `file_status` is `NO_FILE`. |
| `total_debt` | number | Non-negative decimal | Yes | Total outstanding debt across all tradelines in dollars. `null` when `file_status` is `NO_FILE`. |
| `revolving_utilization_pct` | number | 0.0 -- 100.0 | Yes | Revolving credit utilization as a percentage. `null` when `file_status` is `NO_FILE` or no revolving accounts exist. |
| `inquiries_6mo` | integer | Non-negative integer | Yes | Number of hard inquiries in the last 6 months. `null` when `file_status` is `NO_FILE`. |
| `delinq_30_24mo` | integer | Non-negative integer | Yes | Count of 30-day delinquencies in the past 24 months. `null` when `file_status` is `NO_FILE`. |
| `delinq_60_24mo` | integer | Non-negative integer | Yes | Count of 60-day delinquencies in the past 24 months. `null` when `file_status` is `NO_FILE`. |
| `delinq_90_24mo` | integer | Non-negative integer | Yes | Count of 90-day delinquencies in the past 24 months. `null` when `file_status` is `NO_FILE`. |
| `collections_count` | integer | Non-negative integer | Yes | Number of accounts currently in collections. `null` when `file_status` is `NO_FILE`. |
| `charge_offs_count` | integer | Non-negative integer | Yes | Number of charged-off accounts. `null` when `file_status` is `NO_FILE`. |
| `bankruptcy_flag` | boolean | `true` \| `false` | Yes | Whether a bankruptcy filing appears on the credit file. `null` when `file_status` is `NO_FILE`. |
| `bankruptcy_discharge_date` | string | `YYYY-MM-DD` | Yes | Date of bankruptcy discharge. `null` if `bankruptcy_flag` is `false` or `file_status` is `NO_FILE`. |
| `student_loan_delinquency_flag` | boolean | `true` \| `false` | Yes | Whether any student loan tradeline shows a current delinquency. `null` when `file_status` is `NO_FILE`. |

---

## 5. Income Verification (array of objects)

Array nested inside each application. Contains one entry per subject (borrower and, if applicable, cosigner). Documents employment and income details used for debt-to-income and affordability analysis.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `subject_id` | string | `BORR-XXXXX` or `COSIG-XXXXX` | No | Identifier of the person whose income was verified. |
| `verification_method` | string | `PAYSTUB` \| `W2` \| `TAX_RETURN` \| `BANK_STATEMENT` \| `VOE` | No | Method used to verify income. `VOE` = Verification of Employment (employer-provided). |
| `employer_name` | string | Company or organization name | Yes | Name of the subject's employer. `null` if `employment_type` is `UNEMPLOYED` or `RETIRED`. |
| `employment_type` | string | `W2` \| `SELF_EMPLOYED` \| `CONTRACT` \| `RETIRED` \| `UNEMPLOYED` | No | Classification of the subject's employment situation. |
| `job_title` | string | Free text | Yes | Subject's job title. `null` if `employment_type` is `UNEMPLOYED` or `RETIRED`. |
| `tenure_months` | integer | Non-negative integer | Yes | Number of months the subject has been with the current employer. `null` if `employment_type` is `UNEMPLOYED` or `RETIRED`. |
| `gross_annual_income` | number | Non-negative decimal | No | Subject's gross annual income in dollars from primary employment. May be `0` for unemployed borrowers. |
| `other_income` | number | Non-negative decimal | No | Annual income from secondary sources (e.g., rental income, alimony, investments). `0` if none. |
| `other_income_source` | string | Free text | Yes | Description of the secondary income source. `null` if `other_income` is `0`. |
| `monthly_housing_expense` | number | Non-negative decimal | No | Monthly rent or mortgage payment in dollars. |
| `monthly_debt_service` | number | Non-negative decimal | No | Total monthly minimum debt payments (credit cards, auto loans, existing student loans, etc.), excluding housing. |
| `dti_pct` | number | 0.0 -- 100.0+ | No | Debt-to-income ratio expressed as a percentage. See Derivation Rules (Section 13). |
| `residual_income` | number | Decimal (may be negative) | No | Monthly income remaining after housing and debt service obligations. Used for affordability assessment. |
| `docs_complete` | boolean | `true` \| `false` | No | Whether all required income documentation has been received and validated. |

---

## 6. School (embedded object, nullable)

Nested inside each application. Present for UG, GR, SP, and INTL products. `null` for REFI applications (borrower has already completed their education or is refinancing existing debt).

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `school_id` | string | `SCH-XXX` (zero-padded 3-digit code) | No | Unique identifier for the school in Edgemont's approved school list. |
| `school_name` | string | Institution name | No | Full name of the educational institution. |
| `school_type` | string | `PUBLIC_4YR` \| `PRIVATE_4YR` \| `PROFESSIONAL` \| `COMMUNITY` \| `INTERNATIONAL_ELIGIBLE` | No | Classification of the institution. `INTERNATIONAL_ELIGIBLE` applies to approved non-US institutions for the INTL product. |
| `title_iv_eligible` | boolean | `true` \| `false` | No | Whether the school participates in federal Title IV financial aid programs. Always `false` for `INTERNATIONAL_ELIGIBLE` schools. |
| `accreditation_status` | string | Accrediting body name or status | No | Regional or national accreditation status of the institution. |
| `on_approved_list` | boolean | `true` \| `false` | No | Whether the school is on Edgemont Education Lending's internally maintained approved school list. |
| `cohort_default_rate_pct` | number | 0.0 -- 100.0 | Yes | The school's most recently published federal cohort default rate (percentage). `null` for international schools without a published rate. |
| `completion_rate_pct` | number | 0.0 -- 100.0 | Yes | Percentage of students who complete their program within 150% of normal time. `null` for international schools. |
| `median_earnings_3yr_post` | number | Positive decimal | Yes | Median earnings of graduates three years after completion (from College Scorecard or equivalent). `null` for international schools. |
| `school_risk_tier` | string | `A` \| `B` \| `C` \| `D` | No | Edgemont's internal risk tier for the school. `A` = lowest risk, `D` = highest risk. Derived from default rate, completion rate, and earnings data. |
| `country` | string | ISO 3166-1 alpha-2 country code (e.g., `US`, `GB`, `CA`) | No | Country where the institution is located. |

---

## 7. School Certification (embedded object, nullable)

Nested inside each application. Present for UG, GR, SP, and INTL products. `null` for REFI applications. This object records the school's certification of the student's enrollment and financial need.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `certification_status` | string | `RECEIVED` \| `PENDING` \| `REJECTED` | No | Current status of the school certification request. |
| `certified_at` | string | ISO 8601 datetime (`YYYY-MM-DDTHH:MM:SSZ`) | Yes | Timestamp when certification was received. `null` if `certification_status` is `PENDING` or `REJECTED`. |
| `cost_of_attendance` | number | Positive decimal | No | Total cost of attendance for the enrollment period as certified by the school (tuition, fees, room, board, books, transportation, personal expenses). |
| `other_financial_aid` | number | Non-negative decimal | No | Total grants, scholarships, and other non-loan financial aid the student is receiving. |
| `federal_loans_amount` | number | Non-negative decimal | No | Total federal student loan amount the student is receiving for the enrollment period. |
| `certified_max_eligible` | number | Non-negative decimal | No | Maximum private loan amount the student is eligible for. See Derivation Rules (Section 13). |
| `enrollment_period_start` | string | `YYYY-MM-DD` | No | Start date of the enrollment period covered by the loan. |
| `enrollment_period_end` | string | `YYYY-MM-DD` | No | End date of the enrollment period covered by the loan. |
| `enrollment_intensity` | string | `FULL_TIME` \| `HALF_TIME` \| `LESS_THAN_HALF` | No | Student's enrollment intensity for the period. Affects repayment deferment eligibility. |
| `degree_level` | string | Degree type (e.g., `BS`, `BA`, `MS`, `MBA`, `MD`, `JD`, `PhD`, `AA`) | No | Degree the student is pursuing. |
| `program_name` | string | Free text | No | Name of the academic program (e.g., "Computer Science", "Medicine"). |
| `expected_graduation_date` | string | `YYYY-MM-DD` | No | Anticipated graduation date. |
| `year_in_program` | integer | Positive integer | No | Current academic year within the program (e.g., `1` for first year, `4` for fourth year). |

---

## 8. International Details (embedded object, INTL only)

Nested inside each application. Present only when `product_code` is `INTL`; otherwise `null`. Captures visa, passport, and international-student-specific underwriting data.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `visa_type` | string | `F-1` \| `J-1` | No | Type of US student visa held by the borrower. |
| `i20_ds2019_number` | string | Alphanumeric identifier | No | SEVIS I-20 number (for F-1) or DS-2019 number (for J-1). Used for enrollment and visa status verification. |
| `i94_verified` | boolean | `true` \| `false` | No | Whether the borrower's I-94 arrival/departure record has been electronically verified. |
| `passport_country` | string | ISO 3166-1 alpha-2 country code | No | Country that issued the borrower's passport. |
| `home_country_credit_available` | boolean | `true` \| `false` | No | Whether a credit report from the borrower's home country is available and was obtained. |
| `home_country_reference_provided` | boolean | `true` \| `false` | No | Whether the borrower provided a reference from their home country (e.g., a guarantor or financial sponsor). |
| `sponsor_funds_documented` | boolean | `true` \| `false` | No | Whether the borrower has documented financial sponsorship (family, government, or institutional). |
| `opt_eligible` | boolean | `true` \| `false` | No | Whether the borrower is eligible for Optional Practical Training (OPT) post-graduation. |
| `stem_opt_eligible` | boolean | `true` \| `false` | No | Whether the borrower's program qualifies for the 24-month STEM OPT extension. |
| `post_study_work_months` | integer | Non-negative integer | No | Estimated months of authorized post-study work (OPT + STEM OPT extension if applicable). Typically `12` or `36`. |

---

## 9. Existing Loans (array of objects, REFI only)

Array nested inside each application. Present only when `product_code` is `REFI`; otherwise `null`. Lists each loan the borrower seeks to refinance.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `loan_seq` | integer | Positive integer (1-based) | No | Sequence number of the loan within this application's refinance bundle. |
| `servicer_name` | string | Loan servicer name | No | Name of the current loan servicer (e.g., "Nelnet", "Great Lakes", "SoFi"). |
| `loan_type` | string | `FEDERAL_DIRECT` \| `FEDERAL_PLUS` \| `PRIVATE` | No | Type of the existing loan being refinanced. |
| `current_balance` | number | Positive decimal | No | Outstanding principal balance on the loan in dollars. |
| `current_rate_pct` | number | 0.0 -- 15.0 | No | Current annual interest rate as a percentage. |
| `monthly_payment` | number | Positive decimal | No | Current monthly payment amount in dollars. |
| `status` | string | `CURRENT` \| `30DPD` \| `60DPD` \| `DEFAULT` | No | Payment status of the loan. `30DPD` = 30 days past due; `60DPD` = 60 days past due. |
| `payoff_statement_received` | boolean | `true` \| `false` | No | Whether a payoff statement has been obtained from the servicer. Required before disbursement. |

---

## 10. Fraud Screening (embedded object)

Nested inside each application. Contains the results of identity verification, anti-money-laundering checks, and fraud detection signals.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `kyc_status` | string | `PASS` \| `FAIL` \| `REVIEW` | No | Result of Know Your Customer identity verification. `REVIEW` indicates manual review is needed. |
| `cip_documents_verified` | boolean | `true` \| `false` | No | Whether Customer Identification Program document requirements have been satisfied (valid government-issued ID, etc.). |
| `ofac_hit` | boolean | `true` \| `false` | No | Whether the applicant's name matched against the OFAC Specially Designated Nationals (SDN) list. |
| `device_risk_score` | integer | 0 -- 100 | No | Risk score for the device used to submit the application. `0` = lowest risk, `100` = highest risk. |
| `velocity_flag` | boolean | `true` \| `false` | No | Whether an unusual number of applications have been submitted from the same device, IP address, or identity cluster in a short time window. |
| `synthetic_identity_score` | integer | 0 -- 100 | No | Model score estimating the probability that the identity is synthetic (fabricated). `0` = very likely real, `100` = very likely synthetic. |
| `enrollment_fraud_flag` | boolean | `true` \| `false` | No | Whether signals suggest the borrower may not be genuinely enrolled (phantom student risk). |
| `address_mismatch_flag` | boolean | `true` \| `false` | No | Whether the applicant's stated address does not match addresses on file with credit bureaus, USPS, or other verification sources. |

---

## 11. Aggregate Exposure (embedded object)

Nested inside each application. Provides a holistic view of the borrower's total education debt burden, including existing obligations with Edgemont and other lenders, as well as projected post-graduation affordability metrics.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `prior_loans_with_us` | integer | Non-negative integer | No | Number of prior or concurrent education loans the borrower holds with Edgemont Education Lending. |
| `prior_balance_with_us` | number | Non-negative decimal | No | Total outstanding balance on prior Edgemont loans in dollars. `0` for first-time borrowers. |
| `federal_loan_balance` | number | Non-negative decimal | No | Borrower's total outstanding federal student loan balance from NSLDS or self-reported data. |
| `other_private_balance` | number | Non-negative decimal | No | Total outstanding private education loan balance with other lenders. |
| `total_education_debt` | number | Non-negative decimal | No | Sum of all education-related debt: `prior_balance_with_us + federal_loan_balance + other_private_balance + requested_amount`. |
| `projected_debt_at_graduation` | number | Non-negative decimal | No | Estimated total education debt at the time of graduation, accounting for additional borrowing in remaining enrollment periods and accrued interest. |
| `projected_starting_salary` | number | Positive decimal | Yes | Estimated starting salary after graduation, based on school/program earnings data. `null` if no reliable estimate is available. |
| `debt_to_projected_income_ratio` | number | Non-negative decimal | Yes | Ratio of projected debt at graduation to projected starting salary. See Derivation Rules (Section 13). `null` if `projected_starting_salary` is `null`. |

---

## 12. Decision (embedded object)

Nested inside each application. Contains the final underwriting decision, pricing, and any conditions or adverse-action information.

| Field | Type | Format / Allowed Values | Nullable | Description |
|---|---|---|---|---|
| `risk_grade` | string | `A1` through `E3` (letter `A`--`E` + digit `1`--`3`) | No | Internal risk grade assigned by the underwriting model. `A1` = best risk; `E3` = worst risk. |
| `decision` | string | `APPROVE` \| `APPROVE_WITH_CONDITIONS` \| `REFER_MANUAL` \| `DECLINE` | No | Final underwriting decision. |
| `approved_amount` | number | Positive decimal | Yes | Dollar amount approved for disbursement. `null` when `decision` is `DECLINE`. |
| `offered_rate_pct` | number | Positive decimal | Yes | Annual interest rate offered to the borrower as a percentage. `null` when `decision` is `DECLINE`. |
| `rate_type` | string | `FIXED` \| `VARIABLE` | Yes | Whether the offered rate is fixed for the life of the loan or variable (indexed to SOFR or equivalent). `null` when `decision` is `DECLINE`. |
| `term_months` | integer | Positive integer (typically 60, 84, 120, 180, or 240) | Yes | Loan term in months. `null` when `decision` is `DECLINE`. |
| `repayment_option` | string | `IMMEDIATE` \| `INTEREST_ONLY` \| `FLAT_25` \| `DEFERRED` | Yes | In-school and grace-period repayment option. `IMMEDIATE` = full P&I payments begin immediately; `INTEREST_ONLY` = interest-only payments while enrolled; `FLAT_25` = fixed $25/month while enrolled; `DEFERRED` = no payments until after graduation/separation. `null` when `decision` is `DECLINE`. |
| `cosigner_release_eligible` | boolean | `true` \| `false` | Yes | Whether the borrower may apply for cosigner release after meeting on-time payment and credit criteria. `null` when `decision` is `DECLINE` or no cosigner is present. |
| `conditions` | array of strings | Free-text condition descriptions | No | List of conditions that must be met before disbursement. Empty array `[]` for `APPROVE` and `DECLINE`. Populated for `APPROVE_WITH_CONDITIONS` and may be populated for `REFER_MANUAL`. |
| `decline_reason_codes` | array of strings | Standardized reason codes (e.g., `CREDIT_SCORE_LOW`, `DTI_HIGH`, `SCHOOL_NOT_APPROVED`, `FRAUD_FLAG`) | No | Reason codes explaining a decline. Empty array `[]` for `APPROVE` and `APPROVE_WITH_CONDITIONS`. Must contain at least one code for `DECLINE`. |
| `adverse_action_required` | boolean | `true` \| `false` | No | Whether an adverse action notice must be sent to the applicant under ECOA/Regulation B. `true` for `DECLINE` and `APPROVE_WITH_CONDITIONS`. |
| `decisioned_at` | string | ISO 8601 datetime (`YYYY-MM-DDTHH:MM:SSZ`) | No | Timestamp when the decision was rendered. |
| `decisioned_by` | string | `AUTO` \| `ANALYST-NNN` (3-digit analyst ID) | No | Whether the decision was made by the automated engine (`AUTO`) or a human analyst (`ANALYST-NNN`). |

---

## 13. Derivation Rules

The following formulas and business rules govern computed fields in the dataset.

### 13.1 Debt-to-Income Ratio (DTI)

```
dti_pct = (monthly_debt_service / ((gross_annual_income + other_income) / 12)) * 100
```

- `monthly_debt_service` includes all recurring debt obligations **excluding** housing (housing is captured separately in `monthly_housing_expense`).
- If `gross_annual_income + other_income` equals zero, `dti_pct` is set to `999.0` as a sentinel value indicating incalculable DTI.

### 13.2 Certified Maximum Eligible Amount

```
certified_max_eligible = max(0, cost_of_attendance - other_financial_aid - federal_loans_amount)
```

- The result is floored at zero; a negative gap means the student's other funding fully covers (or exceeds) the cost of attendance.
- Applies to UG, GR, SP, and INTL products only.

### 13.3 Approved Amount Constraint (non-REFI)

```
approved_amount <= certified_max_eligible
```

- For UG, GR, SP, and INTL products, the approved loan amount must not exceed the school-certified maximum eligible amount.
- For REFI products, the approved amount is constrained by the sum of `current_balance` values in the existing loans array.

### 13.4 Debt-to-Projected-Income Ratio

```
debt_to_projected_income_ratio = projected_debt_at_graduation / projected_starting_salary
```

- Expressed as a decimal ratio (e.g., `1.5` means debt is 150% of projected first-year salary).
- `null` if `projected_starting_salary` is `null`.

### 13.5 Decision-Outcome Integrity Rules

| Decision | `decline_reason_codes` | `conditions` | `adverse_action_required` |
|---|---|---|---|
| `APPROVE` | Must be empty `[]` | Must be empty `[]` | `false` |
| `APPROVE_WITH_CONDITIONS` | Must be empty `[]` | Must contain >= 1 entry | `true` |
| `REFER_MANUAL` | May be empty or populated | May be empty or populated | `false` or `true` (depends on outcome) |
| `DECLINE` | Must contain >= 1 code | Must be empty `[]` | `true` |

---

## 14. FICO Score Distributions

Synthetic FICO scores are generated according to the following product-specific distributions.

### 14.1 Cosigners (all products)

| Parameter | Value |
|---|---|
| Distribution | Normal |
| Center (mean) | ~720 |
| Standard deviation | 50 |
| Floor (minimum) | 650 |

All cosigners have `file_status` = `ESTABLISHED`.

### 14.2 UG (Undergraduate) Borrowers

| Segment | Proportion | FICO Range | File Status |
|---|---|---|---|
| No credit file | 55% | `null` | `NO_FILE` |
| Thin file | 20% | 640 -- 710 | `THIN` |
| Established file | 25% | 620 -- 780 | `ESTABLISHED` |

### 14.3 GR (Graduate) Borrowers

| Parameter | Value |
|---|---|
| Distribution | Bimodal normal mixture |
| Mode 1 center | ~695 |
| Mode 2 center | ~740 |
| File status | Primarily `ESTABLISHED`; small proportion `THIN` |

### 14.4 SP (Specialty/Professional) Borrowers

| Segment | Proportion | FICO Range | File Status |
|---|---|---|---|
| No/thin file | 8% | `null` or 640 -- 700 | `NO_FILE` or `THIN` |
| Thin file | 17% | 640 -- 750 | `THIN` |
| Established file | 75% | 650 -- 810 | `ESTABLISHED` |

### 14.5 INTL (International) Borrowers

| Parameter | Value |
|---|---|
| FICO score | Always `null` |
| File status | Always `NO_FILE` |

International borrowers on F-1 or J-1 visas are assumed to have no US credit history. Underwriting relies on cosigner credit, income verification, and program/school characteristics.

### 14.6 REFI (Refinance) Borrowers

| Parameter | Value |
|---|---|
| Distribution | Normal |
| Center (mean) | ~705 |
| Standard deviation | 45 |
| Range | 600 -- 820 |
| File status | Always `ESTABLISHED` |

---

## 15. Product Mix & Outcome Mix

### 15.1 Product Distribution

| Product Code | Description | Count | Percentage |
|---|---|---|---|
| `UG` | Undergraduate | 80 | 40% |
| `GR` | Graduate | 50 | 25% |
| `SP` | Specialty / Professional | 30 | 15% |
| `INTL` | International Student | 25 | 12.5% |
| `REFI` | Refinance | 15 | 7.5% |
| **Total** | | **200** | **100%** |

### 15.2 Decision Outcome Targets

| Decision | Target Percentage | Approximate Count |
|---|---|---|
| `APPROVE` | ~55% | ~110 |
| `APPROVE_WITH_CONDITIONS` | ~15% | ~30 |
| `REFER_MANUAL` | ~15% | ~30 |
| `DECLINE` | ~15% | ~30 |
| **Total** | **100%** | **200** |

These are target proportions; actual counts may vary slightly due to the stochastic nature of synthetic data generation.

---

## Appendix: JSON Structure Overview

Each application is stored as a single JSON file named for its application id, for example `synthetic_data/education/applications/APP-2026-00001.json`. The top-level structure is:

```json
{
  "application_id": "APP-2026-00001",
  "product_code": "UG",
  "submitted_at": "2026-01-15T10:30:00Z",
  "channel": "direct",
  "requested_amount": 25000.00,
  "loan_purpose": "Tuition and living expenses for junior year",
  "state_of_residence": "CA",
  "has_cosigner": true,
  "status": "DECISIONED",
  "borrower": { ... },
  "cosigner": { ... },
  "credit_bureau": [ { ... }, { ... } ],
  "income_verification": [ { ... } ],
  "school": { ... },
  "school_certification": { ... },
  "international_details": null,
  "existing_loans": null,
  "fraud_screening": { ... },
  "aggregate_exposure": { ... },
  "decision": { ... }
}
```

**Key nullability rules by product:**

| Section | UG | GR | SP | INTL | REFI |
|---|---|---|---|---|---|
| `cosigner` | If `has_cosigner` | If `has_cosigner` | If `has_cosigner` | If `has_cosigner` | If `has_cosigner` |
| `school` | Present | Present | Present | Present | `null` |
| `school_certification` | Present | Present | Present | Present | `null` |
| `international_details` | `null` | `null` | `null` | Present | `null` |
| `existing_loans` | `null` | `null` | `null` | `null` | Present |

---

*This data dictionary describes synthetic data generated for the Edgemont Education Lending Education Loan Origination Copilot. It is intended for development, testing, and demonstration purposes only.*
